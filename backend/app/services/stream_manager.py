# app/services/stream_manager.py

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List

# Import configuration
from app.camera.config import hls_config

logger = logging.getLogger(__name__)

@dataclass
class Stream:
    """Represents a single stream session"""
    
    stream_id: str
    camera_url: str
    created_at: float
    last_active: float
    active: bool = True
    metadata: Dict = None

    def __post_init__(self):
        self.metadata = self.metadata or {}

class StreamManager:
    """Manages stream sessions and their lifecycle"""
    
    def __init__(self):
        self.streams: Dict[str, Stream] = {}
        self.cleanup_interval = hls_config.stream_timeout // 6  # Clean up 6 times before timeout
        self.logger = logging.getLogger(f"{__name__}.StreamManager")
        self._cleanup_task = None

    def create_stream(self, camera_url: str, metadata: Optional[Dict] = None) -> str:
        """Create a new stream session
        
        Args:
            camera_url: URL of the camera feed
            metadata: Optional metadata for the stream
            
        Returns:
            str: Generated stream ID
        """
        stream_id = str(uuid.uuid4())
        now = time.time()
        
        self.streams[stream_id] = Stream(
            stream_id=stream_id,
            camera_url=camera_url,
            created_at=now,
            last_active=now,
            metadata=metadata or {}
        )
        
        self.logger.info(f"Created stream {stream_id} for {camera_url}")
        return stream_id

    def get_stream(self, stream_id: str) -> Optional[Stream]:
        """Get a stream by ID
        
        Args:
            stream_id: ID of the stream to retrieve
            
        Returns:
            Optional[Stream]: The stream if found, None otherwise
        """
        return self.streams.get(stream_id)

    def update_stream_activity(self, stream_id: str) -> bool:
        """Update the last active time for a stream
        
        Args:
            stream_id: ID of the stream to update
            
        Returns:
            bool: True if stream was found and updated, False otherwise
        """
        if stream_id in self.streams:
            self.streams[stream_id].last_active = time.time()
            return True
        return False

    def update_stream_metadata(self, stream_id: str, metadata: Dict) -> bool:
        """Update metadata for a stream
        
        Args:
            stream_id: ID of the stream to update
            metadata: Dictionary of metadata to update
            
        Returns:
            bool: True if stream was found and updated, False otherwise
        """
        if stream_id in self.streams:
            self.streams[stream_id].metadata.update(metadata)
            return True
        return False

    async def remove_stream(self, stream_id: str) -> bool:
        """Remove a stream session
        
        Args:
            stream_id: ID of the stream to remove
            
        Returns:
            bool: True if stream was found and removed, False otherwise
        """
        if stream_id in self.streams:
            stream = self.streams.pop(stream_id)
            self.logger.info(f"Removed stream {stream_id} (active: {stream.active})")
            return True
        return False

    def list_active_streams(self) -> List[Stream]:
        """Get a list of all active streams
        
        Returns:
            List[Stream]: List of active streams
        """
        now = time.time()
        return [
            stream for stream in self.streams.values()
            if stream.active and (now - stream.last_active) < hls_config.stream_timeout
        ]

    async def cleanup_inactive_streams(self, timeout: Optional[int] = None):
        """Periodically remove inactive streams
        
        Args:
            timeout: Optional timeout in seconds (defaults to hls_config.stream_timeout)
        """
        if timeout is None:
            timeout = hls_config.stream_timeout
            
        self.logger.info(f"Starting stream cleanup task (timeout: {timeout}s, interval: {self.cleanup_interval}s)")
        
        while True:
            try:
                now = time.time()
                inactive = [
                    stream_id for stream_id, stream in list(self.streams.items())
                    if not stream.active or (now - stream.last_active) > timeout
                ]
                
                for stream_id in inactive:
                    await self.remove_stream(stream_id)
                    
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                self.logger.info("Stream cleanup task cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(min(60, self.cleanup_interval))  # Backoff on error

    async def start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self.cleanup_inactive_streams())

    async def stop_cleanup_task(self):
        """Stop the background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

# Singleton instance
stream_manager = StreamManager()