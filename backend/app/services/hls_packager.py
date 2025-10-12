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
        """Build and start a simple ffmpeg HLS pipeline for MJPEG/HTTP streams."""
        paths = self._paths(session)
        paths["seg_dir"].mkdir(parents=True, exist_ok=True)

        # Simple command for MJPEG camera streams
        cmd = [
            'ffmpeg',
            '-re',  # Read input at native frame rate
            '-i', session.camera_url,  # Input URL
            '-c:v', 'libx264',  # Video codec
            '-preset', 'veryfast',  # Encoding speed
            '-tune', 'zerolatency',  # Low latency
            '-g', '60',  # GOP size (keyframe every 2 seconds at 30fps)
            '-sc_threshold', '0',  # Disable scene change detection
            '-b:v', '2000k',  # Video bitrate
            '-maxrate', '2000k',
            '-bufsize', '4000k',
            '-f', 'hls',  # HLS format
            '-hls_time', str(session.segment_duration),  # Segment duration
            '-hls_list_size', str(session.window_size),  # Playlist size
            '-hls_flags', 'delete_segments+independent_segments',  # HLS flags
            '-hls_segment_filename', str(paths["seg_pattern"]),  # Segment pattern
            '-hls_segment_type', 'mpegts',  # Segment type
            str(paths["master"])  # Output playlist
        ]

        self.logger.info(f"Starting ffmpeg for stream={session.stream_id}")
        self.logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment to see if ffmpeg starts successfully
            await asyncio.sleep(0.5)
            
            if process.returncode is not None:
                # Process already exited - read error
                stderr = await process.stderr.read()
                error_msg = stderr.decode('utf-8', errors='ignore')
                self.logger.error(f"ffmpeg failed immediately: {error_msg}")
                raise Exception(f"ffmpeg failed to start: {error_msg[:200]}")
            
            session.active = True
            
            # Start a task to monitor ffmpeg output
            asyncio.create_task(self._monitor_ffmpeg(session, process))
            
            self.logger.info(f"✅ ffmpeg started successfully for stream={session.stream_id}")
            return process
        except Exception as e:
            self.logger.error(f"ffmpeg spawn failed for {session.stream_id}: {e}")
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

    async def _monitor_ffmpeg(self, session: StreamSession, process: asyncio.subprocess.Process):
        """Monitor ffmpeg stderr output for errors and info."""
        try:
            while session.active and process.returncode is None:
                line = await process.stderr.readline()
                if not line:
                    break
                line_str = line.decode('utf-8', errors='ignore').strip()
                if line_str:
                    if 'error' in line_str.lower() or 'failed' in line_str.lower():
                        self.logger.error(f"FFmpeg [{session.stream_id}]: {line_str}")
                        session.error_count += 1
                    else:
                        self.logger.debug(f"FFmpeg [{session.stream_id}]: {line_str}")
        except Exception as e:
            self.logger.error(f"Error monitoring ffmpeg for {session.stream_id}: {e}")
    
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
