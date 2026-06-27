from typing import List
from vision.models.schemas import TrackedObject, ObjectClass, VisionEvent, VisionEventType

class ActivityAnalyzer:
    """
    Analyzes trajectories and interactions.
    """
    def analyze(self, tracked_objects: List[TrackedObject], camera_id: str) -> List[VisionEvent]:
        events = []
        
        # Check Forklift proximity
        workers = [t for t in tracked_objects if t.object_class == ObjectClass.WORKER]
        forklifts = [t for t in tracked_objects if t.object_class == ObjectClass.FORKLIFT]
        
        for w in workers:
            for f in forklifts:
                # Simple distance proxy: distance between bbox centers
                wx = (w.bbox.x_min + w.bbox.x_max) / 2
                wy = (w.bbox.y_min + w.bbox.y_max) / 2
                fx = (f.bbox.x_min + f.bbox.x_max) / 2
                fy = (f.bbox.y_min + f.bbox.y_max) / 2
                
                # Assuming normalized coordinates (0-1)
                dist_sq = (wx - fx)**2 + (wy - fy)**2
                
                if dist_sq < 0.05: # threshold
                    events.append(
                        VisionEvent(
                            event_type=VisionEventType.FORKLIFT_NEAR_WORKER,
                            camera_id=camera_id,
                            description=f"Forklift {f.track_id} dangerously close to worker {w.track_id}.",
                            severity="CRITICAL",
                            tracked_object_ids=[w.track_id, f.track_id]
                        )
                    )
                    
        return events
