from abc import ABC, abstractmethod
from typing import List, Any
from vision.models.schemas import Detection

class BaseDetector(ABC):
    @abstractmethod
    def detect(self, frame: Any) -> List[Detection]:
        """
        Takes an image frame (numpy array, tensor) and returns object detections.
        """
        pass

class BaseTracker(ABC):
    @abstractmethod
    def update(self, detections: List[Detection]) -> List[Any]:
        """
        Takes frame detections and returns tracked objects (with persistent IDs).
        """
        pass
