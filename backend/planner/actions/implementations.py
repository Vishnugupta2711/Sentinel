from planner.actions.base import BaseAction
from planner.models.schemas import InterventionActionSchema, ActionType
from world_state.snapshot.models import WorldState
from world.models.enums import Status

class CancelPermitAction(BaseAction):
    def get_schema(self) -> InterventionActionSchema:
        return InterventionActionSchema(
            name="Cancel Permit",
            description=f"Immediately cancels permit {self.target_id}.",
            action_type=ActionType.CANCEL_PERMIT,
            target_id=self.target_id,
            estimated_duration_minutes=1,
            estimated_cost_usd=500.0, # Cost of delay
            expected_risk_reduction_percentage=0.8,
            production_impact_percentage=0.05,
            confidence=0.95
        )

    def apply(self, state: WorldState) -> WorldState:
        # State is already cloned by the sandbox, but we can return it directly
        for p in state.permits:
            if p.id == self.target_id:
                p.status = Status.OFFLINE # Canceled
        return state

class EvacuateZoneAction(BaseAction):
    def get_schema(self) -> InterventionActionSchema:
        return InterventionActionSchema(
            name="Evacuate Zone",
            description=f"Evacuates all workers from zone {self.target_id}.",
            action_type=ActionType.EVACUATE_ZONE,
            target_id=self.target_id,
            estimated_duration_minutes=5,
            estimated_cost_usd=5000.0, # Cost of downtime
            expected_risk_reduction_percentage=0.95,
            production_impact_percentage=0.20,
            confidence=0.90
        )

    def apply(self, state: WorldState) -> WorldState:
        # Move all workers in target zone to a safe zone (None or SAFE)
        for w in state.workers:
            if w.zone_id == self.target_id:
                w.zone_id = None # Evacuated
        return state
