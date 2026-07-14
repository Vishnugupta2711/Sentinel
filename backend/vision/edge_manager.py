from pydantic import BaseModel
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

class EdgeDevice(BaseModel):
    camera_id: str
    zone: str
    rtsp_url: str
    status: str = "OFFLINE"
    fps: int = 30
    resolution: str = "1080p"

class EdgeDeviceManager:
    def __init__(self):
        self.devices: Dict[str, EdgeDevice] = {}
        
    def register_device(self, device: EdgeDevice) -> EdgeDevice:
        self.devices[device.camera_id] = device
        logger.info(f"Registered edge device: {device.camera_id} in {device.zone}")
        return device
        
    def get_device(self, camera_id: str) -> Optional[EdgeDevice]:
        return self.devices.get(camera_id)
        
    def list_devices(self) -> List[EdgeDevice]:
        return list(self.devices.values())
        
    def update_status(self, camera_id: str, status: str):
        if camera_id in self.devices:
            self.devices[camera_id].status = status
            logger.info(f"Device {camera_id} status updated to {status}")

edge_manager = EdgeDeviceManager()

# Default mock camera for edge testing
edge_manager.register_device(EdgeDevice(
    camera_id="cam_01",
    zone="zone_alpha",
    rtsp_url="mock://synthetic-stream",
    status="ONLINE"
))
