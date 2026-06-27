import pytest
from pydantic import ValidationError
from world.models.entities import Worker
from world_state.snapshot.models import WorldState
from world_state.manager.manager import SnapshotManager
from world_state.diff.engine import StateDiffEngine
from world_state.builder.builder import WorldStateBuilder
from world.manager.manager import world_manager
from world.sample_data.factory import generate_sample_world

@pytest.fixture
def clean_manager():
    manager = SnapshotManager()
    # Clear out anything from other tests
    manager._history.clear()
    manager._current_snapshot = None
    manager._previous_snapshot = None
    manager._version_counter = 0
    return manager

def test_snapshot_immutability():
    w = Worker(id="w1", name="Test", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE")
    state = WorldState(version=1, workers=[w])
    
    # Trying to mutate the frozen WorldState should raise ValidationError
    with pytest.raises(ValidationError):
        state.version = 2

def test_manager_history_and_rollback(clean_manager):
    # Push 3 states
    s1 = WorldState(version=clean_manager.get_next_version())
    clean_manager.push_snapshot(s1)
    
    s2 = WorldState(version=clean_manager.get_next_version())
    clean_manager.push_snapshot(s2)
    
    s3 = WorldState(version=clean_manager.get_next_version())
    clean_manager.push_snapshot(s3)
    
    assert clean_manager.latest().version == 3
    assert len(clean_manager.history()) == 3
    
    # Rollback to 2
    rolled_back = clean_manager.rollback(2)
    assert rolled_back.version == 2
    assert clean_manager.latest().version == 2
    
    # History should now only contain v1 and v2
    hist = clean_manager.history()
    assert len(hist) == 2
    assert hist[0].version == 2 # latest first
    assert hist[1].version == 1

def test_diff_engine():
    w_a = Worker(id="w1", name="Test", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="z1")
    w_b = Worker(id="w1", name="Test", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="z2")
    
    state_a = WorldState(version=1, workers=[w_a])
    state_b = WorldState(version=2, workers=[w_b])
    
    delta = StateDiffEngine.compare(state_a, state_b)
    
    assert delta.version_a == 1
    assert delta.version_b == 2
    assert len(delta.worker_movement) == 1
    assert delta.worker_movement[0]["worker_id"] == "w1"
    assert delta.worker_movement[0]["from_zone"] == "z1"
    assert delta.worker_movement[0]["to_zone"] == "z2"

def test_builder_deep_copy():
    # Make sure we have a plant state loaded
    if not world_manager.get_state():
        world_manager.load(generate_sample_world())
        
    builder = WorldStateBuilder()
    snapshot = builder.build_snapshot()
    
    # Modify the original plant state
    orig_worker = world_manager.get_state().workers[0]
    orig_worker.name = "MutatedName"
    
    # Snapshot should be unaffected
    assert snapshot.workers[0].name != "MutatedName"
