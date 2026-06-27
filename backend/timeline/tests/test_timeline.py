import pytest
from world.models.entities import Worker
from world_state.snapshot.models import WorldState
from timeline.engine.core import TimelineEngine
from timeline.timeline.entry import TimelineEntry

@pytest.fixture
def engine():
    return TimelineEngine()

def test_timeline_insertion_and_compression(engine: TimelineEngine):
    # Insert 150 dummy snapshots
    for i in range(150):
        w = Worker(id=f"w{i}", name=f"Test{i}", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE")
        state = WorldState(version=i, workers=[w])
        entry = TimelineEntry(version=i, simulation_tick=i)
        entry.set_state(state)
        engine.store.insert(entry)
        
    assert len(engine.store.get_all()) == 150
    assert engine.queries.latest().version == 149
    
    # Test worker index lookup
    w_hist = engine.queries.worker_history("w10")
    assert len(w_hist) == 1
    assert w_hist[0].version == 10
    
    # Trigger compression (keep uncompressed=100)
    engine.compression.keep_uncompressed = 100
    targets = engine.store.get_uncompressed_entries(keep_last=100)
    assert len(targets) == 50
    
    for t in targets:
        t.compress()
        
    # Verify the oldest entry is compressed
    oldest = engine.queries.oldest()
    assert oldest.is_compressed is True
    assert oldest._raw_state is None
    
    # Verify it automatically decompresses on get_state()
    state = oldest.get_state()
    assert state.version == 0
    assert state.workers[0].id == "w0"
    
def test_analytics(engine: TimelineEngine):
    w1 = Worker(id="w1", name="A", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="Z1")
    state1 = WorldState(version=1, workers=[w1])
    entry1 = TimelineEntry(version=1, simulation_tick=1)
    entry1.set_state(state1)
    engine.store.insert(entry1)
    
    w1_moved = Worker(id="w1", name="A", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="Z2")
    state2 = WorldState(version=2, workers=[w1_moved])
    entry2 = TimelineEntry(version=2, simulation_tick=2)
    entry2.set_state(state2)
    engine.store.insert(entry2)
    
    movements = engine.analytics.worker_movement_history("w1")
    assert len(movements) == 2
    assert movements[0]["to_zone"] == "Z1"
    assert movements[1]["to_zone"] == "Z2"
    assert movements[1]["from_zone"] == "Z1"
