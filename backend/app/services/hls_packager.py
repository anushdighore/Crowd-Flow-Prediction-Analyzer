import asyncio
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import ffmpeg  # ffmpeg-python

# Import configuration (expected to define output_dir, segment_duration, window_size, variants)
from app.camera.config import hls_config

logger = logging.getLogger(__name__)


@dataclass
class StreamSession:
    """Represents an active HLS streaming session."""
    stream_id: str
    camera_url: str
    output_dir: Path
    variants: List[Dict[str, object]] = field(default_factory=list)
    segment_duration: int = field(default_factory=lambda: hls_config.segment_duration)
    window_size: int = field(default_factory=lambda: hls_config.window_size)
    process: Optional[asyncio.subprocess.Process] = None
    last_segment_time: float = field(default_factory=time.time)
    error_count: int = 0
    active: bool = False


class HLSPackager:
    """Manages HLS streaming sessions via ffmpeg."""

    def __init__(self, base_output_dir: str, public_base="/streams"):
        self.base_dir = Path(base_output_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, StreamSession] = {}
        self.public_base = public_base.rstrip("/")
        self.logger = logging.getLogger(f"{__name__}.HLSPackager")

    def _paths(self, session: StreamSession) -> Dict[str, Path]:
        base = self.base_dir / session.stream_id
        seg_dir = base / "segments"
        return {
            "base": base,
            "master": base / "playlist.m3u8",
            "seg_dir": seg_dir,
            "seg_pattern": seg_dir / "segment_%05d.ts",
        }

    def _public_urls(self, stream_id: str) -> Dict[str, str]:
        base = f"{self.public_base}/{stream_id}"
        return {
            "manifest_url": f"{base}/playlist.m3u8",
            "segments_base": f"{base}/segments/",
        }

    async def _run_ffmpeg(self, session: StreamSession) -> asyncio.subprocess.Process:
        """Build and start the ffmpeg HLS pipeline."""
        paths = self._paths(session)
        paths["seg_dir"].mkdir(parents=True, exist_ok=True)

        # Input tuning: robust probing and RTSP-over-TCP if applicable
        input_kwargs = {
            "rtsp_transport": "tcp",
            "fflags": "nobuffer",
            "flags": "low_delay",
            "stimeout": "5000000",      # 5s in microseconds (for some inputs like RTSP)
            "analyzeduration": "10M",
            "probesize": "32M",
        }

        # HLS output tuning: TS segments for compatibility; rolling window; independent keyframes
        # master_pl_name triggers master playlist generation in newer ffmpeg when used with var_stream_map
        # See: https://ffmpeg.org/ffmpeg-formats.html#hls-2
        output_kwargs = {
            "f": "hls",
            "hls_time": max(1, int(session.segment_duration)),
            "hls_list_size": max(1, int(session.window_size)),
            "hls_flags": "delete_segments+independent_segments+append_list+temp_file",
            "hls_segment_filename": str(paths["seg_pattern"]),
            "hls_playlist_type": "event",
            "hls_allow_cache": 0,
            "master_pl_name": "playlist.m3u8",
            "hls_base_url": f"{self._public_urls(session.stream_id)['segments_base']}",
        }

        # Variants: ensure we have at least one
        variants = session.variants or hls_config.variants
        if not variants:
            # Fallback single variant ~720p at 2000k bitrate
            variants = [{"name": "v0", "width": 1280, "height": 720, "bitrate": "2000k"}]

        # We will use filter_complex and var_stream_map to produce a master playlist with variants
        # Build scale filters per variant and map them
        in_stream = ffmpeg.input(session.camera_url, **input_kwargs)

        # Build variant streams
        streams = []
        var_map_parts = []
        for i, v in enumerate(variants):
            scale = ffmpeg.filter(in_stream.video, "scale", v["width"], v["height"])
            # You can tune encoders here (e.g., libx264 settings), but keep minimal for now
            out = ffmpeg.output(
                scale,
                str(paths["master"]),  # ffmpeg will build variants into the master via var_stream_map
                **{
                    **output_kwargs,
                    f"b:v:{i}": v["bitrate"],
                    # We rely on var_stream_map instead of explicit -map; set below as global args
                },
            )
            streams.append(out)
            var_map_parts.append(f"v:{i},name:{v.get('name', f'v{i}')},bw={_bitrate_to_bw(v['bitrate'])}")

        # Build the var_stream_map
        var_stream_map = " ".join(var_map_parts)

        # Assemble global args
        graph = ffmpeg.merge_outputs(*streams).global_args(
            "-loglevel", "warning",
            "-preset", "veryfast",
            "-g", str(int(2 * output_kwargs["hls_time"]) * 30),  # approximate GOP if 30fps
            "-sc_threshold", "0",
            "-var_stream_map", var_stream_map,
        )

        self.logger.info(f"Starting ffmpeg for stream={session.stream_id} -> {paths['master']}")
        try:
            process = graph.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            session.active = True
            return process
        except Exception as e:
            msg = getattr(e, "stderr", None)
            msg = msg.decode() if isinstance(msg, (bytes, bytearray)) else str(e)
            self.logger.error(f"ffmpeg spawn failed for {session.stream_id}: {msg}")
            raise

    async def start_stream(self, stream_id: str, camera_url: str) -> Dict[str, str]:
        """Start a new HLS stream and return manifest_url and stream_id."""
        if stream_id in self.sessions and self.sessions[stream_id].active:
            self.logger.warning(f"Stream {stream_id} already active")
            return self._public_urls(stream_id)

        session = StreamSession(
            stream_id=stream_id,
            camera_url=camera_url,
            output_dir=self.base_dir / stream_id,
        )
        session.output_dir.mkdir(parents=True, exist_ok=True)
        paths = self._paths(session)
        paths["seg_dir"].mkdir(parents=True, exist_ok=True)

        # Start ffmpeg
        proc = await self._run_ffmpeg(session)
        session.process = proc
        self.sessions[stream_id] = session

        # Optionally: spawn a background watcher to update last_segment_time by inspecting seg_dir mtimes
        asyncio.create_task(self._watch_segments(session))

        return self._public_urls(stream_id)

    async def stop_stream(self, stream_id: str) -> bool:
        """Stop an active HLS stream gracefully."""
        session = self.sessions.get(stream_id)
        if not session or not session.process:
            self.logger.warning(f"Stream {stream_id} not found or not active")
            return False

        self.logger.info(f"Stopping ffmpeg for stream={stream_id}")
        ok = True
        try:
            # Try graceful terminate
            session.process.terminate()
            try:
                await asyncio.wait_for(session.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning(f"ffmpeg did not exit in time; killing process for {stream_id}")
                session.process.kill()
                await session.process.wait()
        except Exception as e:
            self.logger.error(f"Error stopping stream {stream_id}: {e}")
            ok = False

        session.active = False
        return ok

    async def _watch_segments(self, session: StreamSession):
        """Monitor segment directory to keep last_segment_time fresh and detect stalls."""
        paths = self._paths(session)
        seg_dir = paths["seg_dir"]
        while session.active:
            try:
                if seg_dir.exists():
                    latest = max(seg_dir.glob("*.ts"), default=None, key=lambda p: p.stat().st_mtime)
                    if latest:
                        session.last_segment_time = latest.stat().st_mtime
            except Exception as e:
                session.error_count += 1
                self.logger.debug(f"Segment watch error for {session.stream_id}: {e}")
            await asyncio.sleep(1.0)

    def get_stream_status(self, stream_id: str) -> Dict[str, object]:
        """Return basic session status."""
        session = self.sessions.get(stream_id)
        if not session:
            return {"status": "not_found"}

        return {
            "status": "active" if session.active else "inactive",
            "last_segment_time": session.last_segment_time,
            "error_count": session.error_count,
            "camera_url": session.camera_url,
            "manifest_url": self._public_urls(stream_id)["manifest_url"],
            "variants": session.variants or hls_config.variants,
        }

    def cleanup_old_segments(self):
        """Trim old segments beyond the rolling window for all active streams."""
        for session in list(self.sessions.values()):
            if not session.active:
                continue
            try:
                seg_dir = self._paths(session)["seg_dir"]
                if not seg_dir.exists():
                    continue
                segments = sorted(seg_dir.glob("*.ts"))
                keep = session.window_size + 2  # cushion to avoid race with reader
                for seg in segments[:-keep]:
                    try:
                        seg.unlink()
                    except Exception as e:
                        self.logger.warning(f"Failed to remove {seg}: {e}")
            except Exception as e:
                self.logger.error(f"Cleanup error for {session.stream_id}: {e}")


def _bitrate_to_bw(br: str) -> int:
    """
    Convert a bitrate string like '2000k' or '2M' to an approximate bandwidth in bits/sec
    for EXT-X-STREAM-INF:BANDWIDTH, used by var_stream_map.
    """
    s = str(br).strip().lower()
    if s.endswith("k"):
        return int(float(s[:-1]) * 1000)
    if s.endswith("m"):
        return int(float(s[:-1]) * 1_000_000)
    # assume raw bps
    return int(float(s))


# Singleton instance (ensure hls_config.output_dir points to a public mount like ./streams)
hls_packager = HLSPackager(
    str(Path(__file__).resolve().parent.parent / hls_config.output_dir),
    public_base="/streams",
)
