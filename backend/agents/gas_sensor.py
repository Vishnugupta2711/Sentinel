from typing import List, Optional
import structlog
from agents.base import BaseAgent, AgentSignal
from world.models.enums import SensorType, HazardType
from world_state.snapshot.models import WorldState
from intelligence.contracts.context import IntelligenceContext

logger = structlog.get_logger(__name__)

GAS_THRESHOLDS = {
    "CH4":  {"low": 10.0, "medium": 30.0, "high": 50.0, "critical": 70.0, "unit": "% LEL"},
    "H2S":  {"low": 5.0,  "medium": 10.0, "high": 20.0, "critical": 50.0, "unit": "ppm"},
    "CO":   {"low": 25.0, "medium": 50.0, "high": 100.0, "critical": 200.0, "unit": "ppm"},
    "O2":   {"low": 19.5, "medium": 18.0, "high": 16.0, "critical": 14.0, "unit": "%"},
    "NH3":  {"low": 25.0, "medium": 50.0, "high": 100.0, "critical": 300.0, "unit": "ppm"},
    "CL2":  {"low": 0.5,  "medium": 1.0,  "high": 3.0,  "critical": 10.0,  "unit": "ppm"},
}


def _classify_gas_level(gas_type: str, value: float) -> tuple[str, float, str]:
    thresholds = GAS_THRESHOLDS.get(gas_type, {"low": 50, "medium": 100, "high": 200, "critical": 500})
    if value >= thresholds["critical"]:
        return "CRITICAL", 90.0 + min((value - thresholds["critical"]) / thresholds["critical"] * 10, 10.0)
    if value >= thresholds["high"]:
        ratio = (value - thresholds["high"]) / (thresholds["critical"] - thresholds["high"]) if thresholds["critical"] != thresholds["high"] else 1
        return "HIGH", 70.0 + ratio * 20.0
    if value >= thresholds["medium"]:
        ratio = (value - thresholds["medium"]) / (thresholds["high"] - thresholds["medium"]) if thresholds["high"] != thresholds["medium"] else 1
        return "MEDIUM", 40.0 + ratio * 30.0
    if value >= thresholds["low"]:
        ratio = (value - thresholds["low"]) / (thresholds["medium"] - thresholds["low"]) if thresholds["medium"] != thresholds["low"] else 1
        return "LOW", 10.0 + ratio * 30.0
    return "LOW", 0.0


class GasSensorAgent(BaseAgent):
    def name(self) -> str:
        return "gas_sensor"

    def priority(self) -> int:
        return 5

    async def analyze(self, world_state: Optional[WorldState], context: IntelligenceContext) -> List[AgentSignal]:
        signals: List[AgentSignal] = []
        if not world_state:
            return signals

        for sensor in world_state.sensors:
            if sensor.sensor_type != SensorType.GAS:
                continue

            gas_type = sensor.unit.upper() if sensor.unit else "CH4"
            severity, score = _classify_gas_level(gas_type, sensor.current_value)

            if score > 0:
                signals.append(AgentSignal(
                    agent_name="gas_sensor",
                    signal_type=f"GAS_{gas_type}",
                    severity=severity,
                    zone_id=sensor.zone_id,
                    description=f"Gas sensor {sensor.name} in {sensor.zone_id or 'unknown zone'}: {gas_type}={sensor.current_value} {GAS_THRESHOLDS.get(gas_type, {}).get('unit', '')} ({severity})",
                    score=score,
                    metadata={
                        "sensor_id": sensor.id if hasattr(sensor, 'id') else str(id(sensor)),
                        "sensor_name": sensor.name if hasattr(sensor, 'name') else str(sensor),
                        "gas_type": gas_type,
                        "current_value": sensor.current_value,
                        "unit": GAS_THRESHOLDS.get(gas_type, {}).get("unit", ""),
                        "thresholds": GAS_THRESHOLDS.get(gas_type, {}),
                    }
                ))
                logger.info(f"GasSensorAgent: {severity} - {gas_type}={sensor.current_value} in {sensor.zone_id}")

        return signals


gas_sensor_agent = GasSensorAgent()
