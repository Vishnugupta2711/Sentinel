import pytest
from vision.engine.core import VisionEngine
from vision.models.schemas import Detection, BoundingBox, ObjectClass, VisionEventType

@pytest.fixture
def engine():
    return VisionEngine()

def test_missing_helmet_detection(engine: VisionEngine):
    # Setup mock detections: Worker with NO helmet
    worker_bbox = BoundingBox(x_min=0.1, y_min=0.1, x_max=0.5, y_max=0.8, confidence=0.95)
    
    mock_frame = [] # doesn't matter, mock detector ignores it
    engine.inject_mock_detections([
        Detection(object_class=ObjectClass.WORKER, bbox=worker_bbox)
    ])
    
    events = engine.process_frame(mock_frame, camera_id="cam_01")
    
    assert len(events) == 1
    assert events[0].event_type == VisionEventType.MISSING_HELMET

def test_forklift_near_worker(engine: VisionEngine):
    # Setup mock detections: Worker and Forklift overlapping/near
    worker_bbox = BoundingBox(x_min=0.4, y_min=0.4, x_max=0.5, y_max=0.6, confidence=0.9)
    forklift_bbox = BoundingBox(x_min=0.45, y_min=0.45, x_max=0.8, y_max=0.8, confidence=0.9)
    
    mock_frame = []
    engine.inject_mock_detections([
        Detection(object_class=ObjectClass.WORKER, bbox=worker_bbox),
        Detection(object_class=ObjectClass.FORKLIFT, bbox=forklift_bbox)
    ])
    
    events = engine.process_frame(mock_frame, camera_id="cam_02")
    
    # Expecting 2 events: Missing helmet AND Forklift near worker
    assert len(events) == 2
    event_types = [e.event_type for e in events]
    assert VisionEventType.FORKLIFT_NEAR_WORKER in event_types
    assert VisionEventType.MISSING_HELMET in event_types
