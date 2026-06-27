from typing import Any, List
import structlog
from vision.detectors.base import BaseDetector, BaseTracker
from vision.detectors.implementations import MockYOLODetector, MockByteTracker
from vision.ppe.analyzer import PPEAnalyzer
from vision.activities.analyzer import ActivityAnalyzer
from vision.models.schemas import VisionEvent, Detection

logger = structlog.get_logger(__name__)

class VisionEngine:
    def __init__(self, detector: BaseDetector = None, tracker: BaseTracker = None):
        self.detector = detector or MockYOLODetector()
        self.tracker = tracker or MockByteTracker()
        self.ppe_analyzer = PPEAnalyzer()
        self.activity_analyzer = ActivityAnalyzer()
        
        self.events_history: List[VisionEvent] = []
        
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
