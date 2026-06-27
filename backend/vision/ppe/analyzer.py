from typing import List
from vision.models.schemas import TrackedObject, ObjectClass, VisionEvent, VisionEventType

def calculate_iou(boxA, boxB) -> float:
    # Intersection over Union
    xA = max(boxA.x_min, boxB.x_min)
    yA = max(boxA.y_min, boxB.y_min)
    xB = min(boxA.x_max, boxB.x_max)
    yB = min(boxA.y_max, boxB.y_max)
    
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA.x_max - boxA.x_min) * (boxA.y_max - boxA.y_min)
    boxBArea = (boxB.x_max - boxB.x_min) * (boxB.y_max - boxB.y_min)
    
    if float(boxAArea + boxBArea - interArea) == 0.0:
        return 0.0
    return interArea / float(boxAArea + boxBArea - interArea)

class PPEAnalyzer:
    """
    Associates PPE detections with Worker tracks and generates events if missing.
    """
    def analyze(self, tracked_objects: List[TrackedObject], camera_id: str) -> List[VisionEvent]:
        events = []
        workers = [t for t in tracked_objects if t.object_class == ObjectClass.WORKER]
        helmets = [t for t in tracked_objects if t.object_class == ObjectClass.HELMET]
        
        for worker in workers:
            has_helmet = False
            for helmet in helmets:
                iou = calculate_iou(worker.bbox, helmet.bbox)
                # If the helmet is inside the worker's bounding box
                if iou > 0.0:
                    has_helmet = True
                    worker.associated_detections.append(helmet)
                    break
                    
            if not has_helmet:
                events.append(
                    VisionEvent(
                        event_type=VisionEventType.MISSING_HELMET,
                        camera_id=camera_id,
                        description=f"Worker {worker.track_id} is missing a helmet.",
                        severity="WARNING",
                        tracked_object_ids=[worker.track_id]
                    )
                )
                
        return events
