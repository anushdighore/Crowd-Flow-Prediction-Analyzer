"""Camera client module for handling camera connections and frame fetching."""
import asyncio
import logging
from typing import Optional

import aiohttp
import cv2
import numpy as np

from .config import camera_config

logger = logging.getLogger(__name__)

class CameraClient:
    """Handles camera connections and image processing with async support"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CameraClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.timeout = aiohttp.ClientTimeout(total=10.0, connect=5.0)
            self.connector = None
            self.headers = {
                "User-Agent": camera_config.user_agent,
                "Connection": "keep-alive"
            }
            self.ssl = None if camera_config.verify_ssl else False
            self._initialized = True
    
    async def get_session(self):
        """Get or create an aiohttp session with the connector"""
        if self.connector is None or self.connector.closed:
            self.connector = aiohttp.TCPConnector(
                limit=10,
                force_close=True,
                enable_cleanup_closed=True
            )
        return aiohttp.ClientSession(connector=self.connector, timeout=self.timeout)

    async def get_frame(self, camera_url: str) -> Optional[np.ndarray]:
        """
        Asynchronously fetch and decode a single frame from camera URL
        
        Args:
            camera_url: URL of the camera stream or image
            
        Returns:
            Optional[np.ndarray]: Decoded image frame or None if failed
        """
        try:
            session = await self.get_session()
            async with session.get(
                camera_url,
                headers=self.headers,
                ssl=self.ssl,
                timeout=self.timeout
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Camera returned status {resp.status}")
                    return None
                    
                content_type = resp.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    logger.error(f"Unexpected content type: {content_type}")
                    return None
                
                img_data = await resp.read()
                if not img_data:
                    logger.error("Received empty image data")
                    return None
                    
                frame = cv2.imdecode(
                    np.frombuffer(img_data, dtype=np.uint8),
                    cv2.IMREAD_COLOR
                )
                
                if frame is None or frame.size == 0:
                    logger.error("Failed to decode image data")
                    return None
                    
                return frame
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout while connecting to camera: {camera_url}")
        except aiohttp.ClientError as e:
            logger.error(f"Error connecting to camera {camera_url}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error processing frame from {camera_url}: {str(e)}", exc_info=True)
            
        return None

# Create a single instance of the camera client
camera_client = CameraClient()
