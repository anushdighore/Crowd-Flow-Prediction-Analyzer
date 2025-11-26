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
        # Try multiple URL variations if the base URL fails
        urls_to_try = [camera_url]
        
        # Add common camera URL patterns
        if not any(x in camera_url for x in ['/video', '/shot', '/photo', '/image']):
            urls_to_try.extend([
                f"{camera_url}/video",
                f"{camera_url}/shot.jpg",
                f"{camera_url}/photo.jpg",
            ])
        
        last_error = None
        
        for url in urls_to_try:
            session = None
            try:
                session = await self.get_session()
                async with session.get(
                    url,
                    headers=self.headers,
                    ssl=self.ssl,
                    timeout=self.timeout
                ) as resp:
                    if resp.status != 200:
                        logger.debug(f"Camera returned status {resp.status} for {url}")
                        continue
                        
                    content_type = resp.headers.get('Content-Type', '')
                    
                    # Handle MJPEG streams - read first frame
                    if 'multipart' in content_type.lower():
                        logger.info(f"Detected MJPEG stream at {url}")
                        # Read until we find JPEG data
                        chunk_size = 4096
                        buffer = b''
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            buffer += chunk
                            # Look for JPEG markers
                            start = buffer.find(b'\xff\xd8')  # JPEG start
                            end = buffer.find(b'\xff\xd9')    # JPEG end
                            
                            if start != -1 and end != -1 and end > start:
                                img_data = buffer[start:end+2]
                                frame = cv2.imdecode(
                                    np.frombuffer(img_data, dtype=np.uint8),
                                    cv2.IMREAD_COLOR
                                )
                                if frame is not None and frame.size > 0:
                                    logger.info(f"✅ Successfully got frame from {url}")
                                    return frame
                                buffer = buffer[end+2:]
                            
                            if len(buffer) > 1024 * 1024:  # 1MB limit
                                break
                    
                    # Handle regular image
                    elif 'image' in content_type:
                        img_data = await resp.read()
                        if not img_data:
                            logger.debug(f"Received empty image data from {url}")
                            continue
                            
                        frame = cv2.imdecode(
                            np.frombuffer(img_data, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )
                        
                        if frame is not None and frame.size > 0:
                            logger.info(f"✅ Successfully got frame from {url}")
                            return frame
                    else:
                        logger.debug(f"Unexpected content type: {content_type} from {url}")
                        continue
                    
            except asyncio.TimeoutError:
                last_error = f"Timeout while connecting to {url}"
                logger.debug(last_error)
            except aiohttp.ClientError as e:
                last_error = f"Error connecting to {url}: {str(e)}"
                logger.debug(last_error)
            except Exception as e:
                last_error = f"Unexpected error processing frame from {url}: {str(e)}"
                logger.debug(last_error)
            finally:
                # Explicitly close session to prevent memory leaks
                if session and not session.closed:
                    await session.close()
        
        # If we get here, all attempts failed
        logger.error(f"❌ Failed to get frame from camera. Last error: {last_error}")
        logger.error(f"   Tried URLs: {urls_to_try}")
        return None

# Create a single instance of the camera client
camera_client = CameraClient()
