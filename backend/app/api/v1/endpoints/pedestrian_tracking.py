"""
Pedestrian Tracking API Endpoint
REST API for video upload and pedestrian tracking processing
"""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import logging
from pathlib import Path
import json
from typing import Optional
import shutil

logger = logging.getLogger(__name__)

# Import tracking service
try:
    from app.services.pedestrian_tracker import PedestrianTrackingPipeline
    logger.info("✅ Imported PedestrianTrackingPipeline")
except ImportError as e:
    logger.warning(f"⚠️ Could not import pedestrian tracker service: {e}")
    PedestrianTrackingPipeline = None

router = APIRouter(prefix="/pedestrian-tracking", tags=["pedestrian-tracking"])

# Store active jobs
active_jobs = {}


@router.post("/process-video")
async def process_video_upload(
    file: UploadFile = File(...),
    homography: Optional[str] = Form(None),
    frame_skip: Optional[int] = Form(1),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload video and process with pedestrian tracking
    
    Args:
        file: Video file (MP4, AVI, etc.)
        homography: Optional JSON string with image_points and world_points
        frame_skip: Process every Nth frame (default: 1)
    
    Returns:
        Job ID for tracking progress
    """
    if PedestrianTrackingPipeline is None:
        raise HTTPException(status_code=500, detail="Pedestrian tracker not available")
    
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(status_code=400, detail="Invalid video format")
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="ped_track_")
        video_input = os.path.join(temp_dir, file.filename)
        video_output = os.path.join(temp_dir, "processed.mp4")
        trajectory_output = os.path.join(temp_dir, "trajectories.csv")
        
        # Save uploaded file
        with open(video_input, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"✅ Saved video to {video_input}")
        
        # Parse homography if provided
        homography_data = None
        if homography:
            try:
                homography_data = json.loads(homography)
            except json.JSONDecodeError:
                logger.warning("Invalid homography JSON, processing without world coordinates")
        
        # Create job ID
        job_id = os.path.basename(temp_dir)
        
        # Initialize pipeline
        pipeline = PedestrianTrackingPipeline()
        
        # Store job info
        active_jobs[job_id] = {
            'status': 'processing',
            'temp_dir': temp_dir,
            'input_file': video_input,
            'output_file': video_output,
            'trajectory_file': trajectory_output,
            'progress': 0,
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_video_background,
            job_id,
            pipeline,
            video_input,
            video_output,
            homography_data,
            frame_skip,
            trajectory_output
        )
        
        return {
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video processing started'
        }
    
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_video_background(
    job_id: str,
    pipeline,
    input_path: str,
    output_path: str,
    homography_data: Optional[dict],
    frame_skip: int,
    trajectory_output: str
):
    """Background task for video processing"""
    try:
        logger.info(f"🎬 Starting video processing for job {job_id}")
        
        def _update_progress(percent: int):
            job = active_jobs.get(job_id)
            if job and job.get('status') == 'processing':
                job['progress'] = percent
        
        result = pipeline.process_video(
            input_path,
            output_path,
            homography_data=homography_data,
            frame_skip=frame_skip,
            progress_callback=_update_progress,
            trajectory_output_path=trajectory_output
        )
        
        # Get trajectories
        trajectories_csv = pipeline.get_trajectories_csv()
        
        # Store result
        active_jobs[job_id].update({
            'status': 'completed',
            'progress': 100,
            'result': result,
            'trajectories': trajectories_csv
        })
        
        logger.info(f"✅ Completed processing for job {job_id}")
    
    except Exception as e:
        logger.error(f"❌ Error processing video: {e}")
        active_jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'progress': 0
        })


@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    return {
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'error': job['error'],
        'result': job.get('result')
    }


@router.get("/download-video/{job_id}")
async def download_processed_video(job_id: str):
    """Download processed video"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Job status: {job['status']}")
    
    output_file = job['output_file']
    
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Processed video not found")
    
    return FileResponse(
        output_file,
        media_type="video/mp4",
        filename="processed_video.mp4"
    )


@router.get("/download-trajectories/{job_id}")
async def download_trajectories(job_id: str):
    """Download trajectory data as CSV"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Job status: {job['status']}")
    
    trajectories_csv = job.get('trajectories')
    
    if not trajectories_csv:
        raise HTTPException(status_code=404, detail="No trajectory data")
    
    # Create temp file with CSV data
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.csv',
        delete=False
    )
    temp_file.write(trajectories_csv)
    temp_file.close()
    
    return FileResponse(
        temp_file.name,
        media_type="text/csv",
        filename="trajectories.csv"
    )


@router.post("/cleanup/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job temporary files"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    temp_dir = job.get('temp_dir')
    
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up: {e}")
    
    del active_jobs[job_id]
    
    return {'status': 'cleaned', 'job_id': job_id}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'pedestrian-tracking',
        'available': PedestrianTrackingPipeline is not None
    }
