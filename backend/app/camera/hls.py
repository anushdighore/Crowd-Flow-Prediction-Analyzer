from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.services.hls_packager import hls_packager
from app.services.stream_manager import stream_manager
from pathlib import Path
import os
import time
from pydantic import BaseModel

router = APIRouter()

class StreamRequest(BaseModel):
    camera_url: str

@router.post("/start")
async def start_hls_stream(request: StreamRequest):
    stream_id = stream_manager.create_stream(request.camera_url)
    success = await hls_packager.start_stream(stream_id, request.camera_url)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start HLS stream")
    return {"stream_id": stream_id}

@router.post("/hls/start")
async def start_hls_stream(request: StreamRequest):
    try:
        camera_url = request.camera_url
        stream_id = stream_manager.create_stream(camera_url)
        success = await hls_packager.start_stream(stream_id, camera_url)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start HLS stream")
        return {"stream_id": stream_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hls/stop/{stream_id}")
async def stop_hls_stream(stream_id: str):
    success = await hls_packager.stop_stream(stream_id)
    if not success: 
        raise HTTPException(status_code=404, detail="Stream not found")
    return {"status": "stopped"}

@router.get("/hls/status/{stream_id}")
async def get_hls_status(stream_id: str):
    status = hls_packager.get_stream_status(stream_id)
    if status['status'] == 'not_found':
        raise HTTPException(status_code=404, detail="Stream not found")
    return status

@router.get("/hls/playlist/{stream_id}/playlist.m3u8")
async def get_playlist(stream_id: str):
    playlist_path = hls_packager.base_dir / stream_id / "playlist.m3u8"
    if not playlist_path.exists():
        raise HTTPException(status_code=404, detail="Playlist not found")
    return FileResponse(playlist_path, media_type="application/vnd.apple.mpegurl")

@router.get("/hls/health")
async def health_check():
    return {
        "status": "ok",
        "active_streams": len([s for s in hls_packager.sessions.values() if s.active])
    }