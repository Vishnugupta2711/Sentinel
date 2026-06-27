from world.builder.builder import WorldBuilder
from world.models.entities import Building, Zone
from world.sample_data.factory import generate_sample_world

def test_world_builder():
    builder = WorldBuilder()
    builder.create_plant(name="Test Plant", description="Desc", address="123")
    b = Building(name="Test Building")
    builder.add_building(b)
    z = Zone(name="Test Zone", building_id=b.id)
    builder.add_zone(z)
    
    state = builder.build()
    
    assert state.plant.name == "Test Plant"
    assert len(state.buildings) == 1
    assert len(state.zones) == 1

def test_sample_factory():
    state = generate_sample_world()
    
    assert state.plant is not None
    assert len(state.buildings) == 2
    assert len(state.zones) == 8
    assert len(state.sensors) == 40
    assert len(state.workers) == 30
    assert len(state.cameras) == 25
    assert len(state.equipment) == 50
    assert len(state.pipelines) == 15
    assert len(state.valves) == 20
    assert len(state.emergency_exits) == 5
