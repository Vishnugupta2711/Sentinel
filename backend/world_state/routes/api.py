from fastapi import APIRouter, HTTPException, Query
from world_state.manager.manager import snapshot_manager
from world_state.snapshot.models import WorldState
from world_state.diff.engine import StateDiffEngine, StateDelta
from world_state.schemas.api import WorldStateHistoryResponse

router = APIRouter(prefix="/world-state", tags=["World State"])

@router.get("/current", response_model=WorldState)
async def get_current_state():
    """Returns the most recent immutable snapshot."""
    snap = snapshot_manager.latest()
    if not snap:
        raise HTTPException(status_code=404, detail="No world state available yet.")
    return snap

@router.get("/history", response_model=WorldStateHistoryResponse)
async def get_history(limit: int = Query(10, le=1000)):
    """Returns the most recent N snapshots."""
    return WorldStateHistoryResponse(snapshots=snapshot_manager.history(limit))

@router.get("/diff", response_model=StateDelta)
async def get_diff(v1: int, v2: int):
    """Returns the exact differences between two versions of the WorldState."""
    s1 = snapshot_manager.get_by_version(v1)
    s2 = snapshot_manager.get_by_version(v2)
    
    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="One or both versions not found in history.")
        
    return StateDiffEngine.compare(s1, s2)

@router.post("/rollback", response_model=WorldState)
async def rollback_state(version: int):
    """Rolls back the current world state manager pointer to a previous version."""
    snap = snapshot_manager.rollback(version)
    if not snap:
        raise HTTPException(status_code=404, detail="Version not found.")
    return snap
