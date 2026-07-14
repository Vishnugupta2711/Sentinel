from typing import List, Any
import cv2
import numpy as np
from vision.detectors.base import BaseDetector, BaseTracker
from vision.models.schemas import Detection, TrackedObject, BoundingBox, ObjectClass

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
            
        if frame is None:
            return []
            
        # Synthetic OpenCV color detection for demo purposes
        detections = []
        
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 1. Detect workers (Green body: H=60 approx)
            lower_green = np.array([40, 100, 100])
            upper_green = np.array([80, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"Debug green mask: found {len(contours)} contours")
            
            for c in contours:
                area = cv2.contourArea(c)
                print(f"Debug green area: {area}")
                if area > 500:
                    x, y, w, h = cv2.boundingRect(c)
                    detections.append(Detection(
                        object_class=ObjectClass.WORKER,
                        bbox=BoundingBox(x_min=x, y_min=y-40, x_max=x+w, y_max=y+h, confidence=0.95)
                    ))
                    
            # 2. Detect helmets (Yellow: H=30 approx)
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([40, 255, 255])
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
            contours_y, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"Debug yellow mask: found {len(contours_y)} contours")
            
            for c in contours_y:
                area = cv2.contourArea(c)
                print(f"Debug yellow area: {area}")
                if area > 50:
                    x, y, w, h = cv2.boundingRect(c)
                    detections.append(Detection(
                        object_class=ObjectClass.HELMET,
                        bbox=BoundingBox(x_min=x, y_min=y, x_max=x+w, y_max=y+h, confidence=0.90)
                    ))
        except Exception as e:
            print("Detector exception:", e)
            pass
            
        return detections

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
