from world.manager.manager import world_manager
from world.models.state import PlantState
from world_state.snapshot.models import WorldState
from world_state.manager.manager import snapshot_manager
import structlog

logger = structlog.get_logger(__name__)

class WorldStateBuilder:
    """Builds immutable WorldState snapshots from the active PlantState."""
    
    def build_snapshot(self) -> WorldState:
        """
        Pulls the live PlantState, computes any necessary metrics, 
        creates a deep copy, and returns an immutable WorldState.
        """
        state: PlantState = world_manager.get_state()
        if not state:
            raise ValueError("Cannot build WorldState: PlantState is empty.")
            
        # Get atomic version
        version = snapshot_manager.get_next_version()
        
        # Calculate zone occupancies dynamically
        zone_occupancy = {}
        for zone in state.zones:
            zone_occupancy[zone.id] = 0
            
        for worker in state.workers:
            if worker.zone_id in zone_occupancy:
                zone_occupancy[worker.zone_id] += 1
                
        # Calculate plant status (e.g., if there's an active hazard)
        plant_status = "CRITICAL" if len(state.hazards) > 0 else "NORMAL"
        
        # Deepcopy the entities via model_copy(deep=True) so the snapshot is truly isolated
        snapshot = WorldState(
            version=version,
            plant=state.plant.model_copy(deep=True) if state.plant else None,
            buildings=[b.model_copy(deep=True) for b in state.buildings],
            zones=[z.model_copy(deep=True) for z in state.zones],
            workers=[w.model_copy(deep=True) for w in state.workers],
            sensors=[s.model_copy(deep=True) for s in state.sensors],
            equipment=[e.model_copy(deep=True) for e in state.equipment],
            pipelines=[p.model_copy(deep=True) for p in state.pipelines],
            valves=[v.model_copy(deep=True) for v in state.valves],
            cameras=[c.model_copy(deep=True) for c in state.cameras],
            vehicles=[v.model_copy(deep=True) for v in state.vehicles],
            emergency_exits=[e.model_copy(deep=True) for e in state.emergency_exits],
            weather=state.weather.model_copy(deep=True) if state.weather else None,
            permits=[p.model_copy(deep=True) for p in state.permits],
            hazards=[h.model_copy(deep=True) for h in state.hazards],
            zone_occupancy=zone_occupancy,
            plant_status=plant_status
        )
        
        # Push to manager
        snapshot_manager.push_snapshot(snapshot)
        
        # Pre-serialize once — the WS broadcaster reuses this string
        # instead of serializing once per connected client.
        snapshot._cached_json = snapshot.model_dump_json()
        logger.debug(f"Snapshot v{version} built, {len(snapshot._cached_json)} bytes")
        return snapshot

world_state_builder = WorldStateBuilder()
