from typing import List, Any
from vision.detectors.base import BaseDetector, BaseTracker
from vision.models.schemas import Detection, TrackedObject

class MockYOLODetector(BaseDetector):
    """
    Mock detector that returns predefined detections for testing.
    In production, this wraps ultralytics YOLOv8.
    """
    def __init__(self):
        self.mock_queue: List[List[Detection]] = []
        
    def detect(self, frame: Any) -> List[Detection]:
        if self.mock_queue:
            return self.mock_queue.pop(0)
        return []

class MockByteTracker(BaseTracker):
    """
    Mock tracker. Assigns sequential IDs to detections.
    """
    def __init__(self):
        self.next_id = 1
        
    def update(self, detections: List[Detection]) -> List[TrackedObject]:
        tracked = []
        for d in detections:
            obj = TrackedObject(
                track_id=f"trk_{self.next_id}",
                object_class=d.object_class,
                bbox=d.bbox
            )
            self.next_id += 1
            tracked.append(obj)
        return tracked
