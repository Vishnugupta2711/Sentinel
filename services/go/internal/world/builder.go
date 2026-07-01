package world

import "time"

type PlantStateBuilder struct {
	state PlantState
}

func NewPlantStateBuilder() *PlantStateBuilder {
	return &PlantStateBuilder{
		state: PlantState{
			Timestamp: time.Now().UTC(),
		},
	}
}

func (b *PlantStateBuilder) WithVersion(v int) *PlantStateBuilder {
	b.state.Version = v
	return b
}

func (b *PlantStateBuilder) WithPlant(p Plant) *PlantStateBuilder {
	b.state.Plant = p
	return b
}

func (b *PlantStateBuilder) WithBuildings(buildings []Building) *PlantStateBuilder {
	b.state.Buildings = buildings
	return b
}

func (b *PlantStateBuilder) WithZones(zones []Zone) *PlantStateBuilder {
	b.state.Zones = zones
	return b
}

func (b *PlantStateBuilder) WithSensors(sensors []Sensor) *PlantStateBuilder {
	b.state.Sensors = sensors
	return b
}

func (b *PlantStateBuilder) WithWorkers(workers []Worker) *PlantStateBuilder {
	b.state.Workers = workers
	return b
}

func (b *PlantStateBuilder) WithVehicles(vehicles []Vehicle) *PlantStateBuilder {
	b.state.Vehicles = vehicles
	return b
}

func (b *PlantStateBuilder) WithCameras(cameras []Camera) *PlantStateBuilder {
	b.state.Cameras = cameras
	return b
}

func (b *PlantStateBuilder) WithEquipment(equipment []Equipment) *PlantStateBuilder {
	b.state.Equipment = equipment
	return b
}

func (b *PlantStateBuilder) WithPipelines(pipelines []Pipeline) *PlantStateBuilder {
	b.state.Pipelines = pipelines
	return b
}

func (b *PlantStateBuilder) WithValves(valves []Valve) *PlantStateBuilder {
	b.state.Valves = valves
	return b
}

func (b *PlantStateBuilder) WithPermits(permits []Permit) *PlantStateBuilder {
	b.state.Permits = permits
	return b
}

func (b *PlantStateBuilder) WithHazards(hazards []Hazard) *PlantStateBuilder {
	b.state.Hazards = hazards
	return b
}

func (b *PlantStateBuilder) WithExits(exits []EmergencyExit) *PlantStateBuilder {
	b.state.Exits = exits
	return b
}

func (b *PlantStateBuilder) WithWeather(w WeatherState) *PlantStateBuilder {
	b.state.Weather = w
	return b
}

func (b *PlantStateBuilder) Build() PlantState {
	return b.state
}
