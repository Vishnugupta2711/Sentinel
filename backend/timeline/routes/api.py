from fastapi import APIRouter, Depends, HTTPException, Query
from timeline.engine.core import TimelineEngine, get_timeline_engine
from timeline.schemas.api import GenericResponse, TimelineEntryResponse, TimelineHistoryResponse, ReplayStatusResponse

router = APIRouter(prefix="/timeline", tags=["Historical Timeline"])

def _to_response(entry) -> TimelineEntryResponse:
    return TimelineEntryResponse(
        entry_id=entry.entry_id,
        timestamp=entry.timestamp,
        version=entry.version,
        simulation_tick=entry.simulation_tick,
        metadata=entry.metadata,
        state=entry.get_state()
    )

@router.get("/latest", response_model=TimelineEntryResponse)
async def get_latest(engine: TimelineEngine = Depends(get_timeline_engine)):
    latest = engine.queries.latest()
    if not latest:
        raise HTTPException(status_code=404, detail="No timeline entries available.")
    return _to_response(latest)

@router.get("/history", response_model=TimelineHistoryResponse)
async def get_history(
    minutes: int = Query(5, description="Fetch last N minutes of history"),
    engine: TimelineEngine = Depends(get_timeline_engine)
):
    entries = engine.queries.last_minutes(minutes)
    return TimelineHistoryResponse(entries=[_to_response(e) for e in entries])

@router.get("/worker/{worker_id}", response_model=TimelineHistoryResponse)
async def get_worker_history(worker_id: str, engine: TimelineEngine = Depends(get_timeline_engine)):
    entries = engine.queries.worker_history(worker_id)
    return TimelineHistoryResponse(entries=[_to_response(e) for e in entries])

@router.get("/sensor/{sensor_id}", response_model=TimelineHistoryResponse)
async def get_sensor_history(sensor_id: str, engine: TimelineEngine = Depends(get_timeline_engine)):
    entries = engine.queries.sensor_history(sensor_id)
    return TimelineHistoryResponse(entries=[_to_response(e) for e in entries])

@router.get("/zone/{zone_id}", response_model=TimelineHistoryResponse)
async def get_zone_history(zone_id: str, engine: TimelineEngine = Depends(get_timeline_engine)):
    entries = engine.queries.zone_history(zone_id)
    return TimelineHistoryResponse(entries=[_to_response(e) for e in entries])

@router.get("/statistics")
async def get_statistics(engine: TimelineEngine = Depends(get_timeline_engine)):
    return engine.analytics.plant_statistics()

# Replay Controls
@router.get("/replay/status", response_model=ReplayStatusResponse)
async def get_replay_status(engine: TimelineEngine = Depends(get_timeline_engine)):
    return engine.replay.get_status()

@router.post("/replay/pause", response_model=GenericResponse)
async def pause_replay(engine: TimelineEngine = Depends(get_timeline_engine)):
    engine.replay.pause()
    return GenericResponse(success=True, message="Replay paused.")

@router.post("/replay/resume", response_model=GenericResponse)
async def resume_replay(engine: TimelineEngine = Depends(get_timeline_engine)):
    engine.replay.resume()
    return GenericResponse(success=True, message="Replay resumed.")

@router.post("/replay/step/forward", response_model=GenericResponse)
async def step_forward(engine: TimelineEngine = Depends(get_timeline_engine)):
    engine.replay.step_forward()
    return GenericResponse(success=True, message="Stepped forward.")

@router.post("/replay/step/backward", response_model=GenericResponse)
async def step_backward(engine: TimelineEngine = Depends(get_timeline_engine)):
    engine.replay.step_backward()
    return GenericResponse(success=True, message="Stepped backward.")
