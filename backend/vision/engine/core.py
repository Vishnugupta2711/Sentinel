from typing import Any, List
import structlog
from vision.detectors.base import BaseDetector, BaseTracker
from vision.detectors.implementations import MockYOLODetector, MockByteTracker
from vision.ppe.analyzer import PPEAnalyzer
from vision.activities.analyzer import ActivityAnalyzer
from vision.models.schemas import VisionEvent, Detection
from vision.camera.ingest import CameraStream
from vision.websocket.live import ws_vision_queues
from vision.edge_manager import edge_manager

logger = structlog.get_logger(__name__)

class VisionEngine:
    def __init__(self, detector: BaseDetector = None, tracker: BaseTracker = None):
        self.detector = detector or MockYOLODetector()
        self.tracker = tracker or MockByteTracker()
        self.ppe_analyzer = PPEAnalyzer()
        self.activity_analyzer = ActivityAnalyzer()
        
        self.events_history: List[VisionEvent] = []
        self.streams = {}
        
        # Start streams for registered edge devices
        for device in edge_manager.list_devices():
            self._start_stream(device)
            
    def _start_stream(self, device):
        stream = CameraStream(
            camera_id=device.camera_id,
            rtsp_url=device.rtsp_url,
            frame_callback=self._handle_frame
        )
        stream.start()
        self.streams[device.camera_id] = stream
        
    def _handle_frame(self, frame: Any, camera_id: str):
        events = self.process_frame(frame, camera_id)
        if events:
            # Broadcast to WS
            import asyncio
            from vision.websocket import live
            if getattr(live, "main_loop", None):
                for q in ws_vision_queues:
                    for event in events:
                        asyncio.run_coroutine_threadsafe(q.put(event.model_dump()), live.main_loop)
        
    def process_frame(self, frame: Any, camera_id: str) -> List[VisionEvent]:
        # 1. Detection
        detections = self.detector.detect(frame)
        
        # 2. Tracking
        tracked_objects = self.tracker.update(detections)
        
        events = []
        
        # 3. PPE Analysis
        ppe_events = self.ppe_analyzer.analyze(tracked_objects, camera_id)
        events.extend(ppe_events)
        
        # 4. Activity Analysis
        activity_events = self.activity_analyzer.analyze(tracked_objects, camera_id)
        events.extend(activity_events)
        
        # Log to history
        self.events_history.extend(events)
        
        if events:
            logger.info(f"VisionEngine generated {len(events)} events for camera {camera_id}")
            
        return events
        
    def inject_mock_detections(self, detections: List[Detection]):
        """Helper for testing without real frames"""
        if isinstance(self.detector, MockYOLODetector):
            self.detector.mock_queue.append(detections)
            
    def get_events(self) -> List[VisionEvent]:
        return self.events_history

vision_engine = VisionEngine()
