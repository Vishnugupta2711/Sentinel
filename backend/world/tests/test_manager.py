from world.manager.manager import WorldManager, world_manager
from world.models.entities import Worker
from world.sample_data.factory import generate_sample_world

def test_world_manager_singleton():
    manager1 = WorldManager()
    manager2 = WorldManager()
    assert manager1 is manager2
    assert manager1 is world_manager

def test_world_manager_state_and_registry():
    state = generate_sample_world()
    world_manager.load(state)
    
    retrieved_state = world_manager.get_state()
    assert retrieved_state is not None
    assert len(retrieved_state.workers) == 30
    
    # Test registry lookup
    worker = retrieved_state.workers[0]
    lookup_worker = world_manager.registry.get_by_id(worker.id)
    
    assert lookup_worker is not None
    assert lookup_worker.id == worker.id
    assert isinstance(lookup_worker, Worker)

def test_world_manager_reset():
    world_manager.reset()
    state = world_manager.get_state()
    assert state is None
    # Reset loads an empty state into registry with no plant/weather
    # But essentially state is None.
