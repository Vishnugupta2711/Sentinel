import cv2
import threading
import time
import numpy as np
import structlog
from typing import Callable, Any

logger = structlog.get_logger(__name__)

class CameraStream:
    def __init__(self, camera_id: str, rtsp_url: str, frame_callback: Callable[[Any, str], None]):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.frame_callback = frame_callback
        self.running = False
        self.thread = None
        self._mock_counter = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._ingest_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started camera stream ingest for {self.camera_id}")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info(f"Stopped camera stream ingest for {self.camera_id}")

    def _generate_synthetic_frame(self):
        # Create a blank black frame (480p)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Simulate a moving worker
        self._mock_counter += 1
        x_pos = (self._mock_counter * 10) % 640
        y_pos = 240 + int(np.sin(self._mock_counter * 0.1) * 50)
        
        # Draw a "worker" body (green rectangle)
        cv2.rectangle(frame, (x_pos, y_pos), (x_pos+40, y_pos+100), (0, 255, 0), -1)
        # Draw a "head" (gray circle)
        cv2.circle(frame, (x_pos+20, y_pos-20), 15, (200, 200, 200), -1)
        
        # Simulate missing PPE (red box missing) vs PPE (yellow hat)
        # 80% of the time, the worker has a helmet. 20% of the time, missing.
        if (self._mock_counter % 100) > 20: 
            # Yellow helmet
            cv2.ellipse(frame, (x_pos+20, y_pos-25), (18, 12), 0, 180, 360, (0, 255, 255), -1)
            
        return frame

    def _ingest_loop(self):
        is_synthetic = self.rtsp_url.startswith("mock://")
        cap = None
        
        if not is_synthetic:
            cap = cv2.VideoCapture(self.rtsp_url)
            if not cap.isOpened():
                logger.error(f"Failed to open RTSP stream for {self.camera_id}, falling back to synthetic.")
                is_synthetic = True

        fps = 10 # process at 10 fps
        frame_time = 1.0 / fps

        while self.running:
            start_t = time.time()
            
            if is_synthetic:
                frame = self._generate_synthetic_frame()
            else:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from {self.camera_id}, reconnecting...")
                    time.sleep(1)
                    continue
            
            # Send frame to callback
            try:
                self.frame_callback(frame, self.camera_id)
            except Exception as e:
                logger.error(f"Error in frame callback for {self.camera_id}: {e}")

            # Pace the stream
            elapsed = time.time() - start_t
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
                
        if cap:
            cap.release()
