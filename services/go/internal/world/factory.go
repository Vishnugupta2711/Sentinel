package world

import (
	"crypto/rand"
	"fmt"
	"time"
)

func generateID() string {
	b := make([]byte, 16)
	rand.Read(b)
	return fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:])
}

func now() time.Time {
	return time.Now().UTC()
}

func SamplePlantState() PlantState {
	plant := Plant{
		BaseObject: BaseObject{
			ID:        generateID(),
			Name:      "Sentinel Refinery",
			Status:    StatusOnline,
			CreatedAt: now(),
			UpdatedAt: now(),
		},
		Address: "123 Industrial Highway, Sector 7",
		Manager: "John Control",
	}
	capacity := 100000.0
	plant.Capacity = &capacity

	building1 := Building{
		PhysicalObject: PhysicalObject{
			BaseObject: BaseObject{ID: generateID(), Name: "Processing Unit A", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()},
			X: 0, Y: 0, Z: 0,
		},
		Floors: 3, MaxOccupancy: intPtr(50),
	}

	building2 := Building{
		PhysicalObject: PhysicalObject{
			BaseObject: BaseObject{ID: generateID(), Name: "Storage Facility B", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()},
			X: 200, Y: 50, Z: 0,
		},
		Floors: 1, MaxOccupancy: intPtr(10),
	}

	zones := []Zone{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Reactor Core", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 10, Y: 10, Z: 0, BuildingID: building1.ID}, HazardLevel: "HIGH", CurrentOccupancy: 2},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Control Room", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 50, Y: 10, Z: 0, BuildingID: building1.ID}, HazardLevel: "LOW", CurrentOccupancy: 5},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Tank Farm Alpha", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 210, Y: 60, Z: 0, BuildingID: building2.ID}, HazardLevel: "HIGH", CurrentOccupancy: 1},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Loading Dock", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 220, Y: 40, Z: 0, BuildingID: building2.ID}, HazardLevel: "MEDIUM", CurrentOccupancy: 3},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Workshop", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 100, Y: 80, Z: 0, BuildingID: building1.ID}, HazardLevel: "MEDIUM", CurrentOccupancy: 4},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Chemical Storage", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 300, Y: 100, Z: 0}, HazardLevel: "HIGH", CurrentOccupancy: 0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Admin Office", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 0, Y: 150, Z: 0}, HazardLevel: "LOW", CurrentOccupancy: 8},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Maintenance Bay", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 150, Y: 120, Z: 0, BuildingID: building1.ID}, HazardLevel: "MEDIUM", CurrentOccupancy: 2},
	}

	n := func(v float64) *float64 { return &v }
	sensors := []Sensor{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Gas Sensor G-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 15, Y: 15, Z: 2, ZoneID: zones[0].ID}, SensorType: SensorTypeGas, CurrentValue: 0.5, Unit: "ppm", Threshold: 10.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Temp Sensor T-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 20, Y: 15, Z: 3, ZoneID: zones[0].ID}, SensorType: SensorTypeTemperature, CurrentValue: 85.0, Unit: "°C", Threshold: 120.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Pressure P-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 15, Y: 20, Z: 1, ZoneID: zones[0].ID}, SensorType: SensorTypePressure, CurrentValue: 4.5, Unit: "bar", Threshold: 10.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Gas Sensor G-02", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 215, Y: 65, Z: 2, ZoneID: zones[2].ID}, SensorType: SensorTypeGas, CurrentValue: 2.1, Unit: "ppm", Threshold: 15.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Smoke Detector S-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 55, Y: 15, Z: 4, ZoneID: zones[1].ID}, SensorType: SensorTypeSmoke, CurrentValue: 0.0, Unit: "mg/m³", Threshold: 5.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Flow Meter F-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 10, Y: 10, Z: 0, ZoneID: zones[0].ID}, SensorType: SensorTypeFlow, CurrentValue: 120.0, Unit: "L/min", Threshold: 200.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Vibration V-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 25, Y: 15, Z: 0, ZoneID: zones[0].ID}, SensorType: SensorTypeVibration, CurrentValue: 0.3, Unit: "mm/s", Threshold: 5.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Humidity H-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 5, Y: 155, Z: 2, ZoneID: zones[6].ID}, SensorType: SensorTypeHumidity, CurrentValue: 45.0, Unit: "%", Threshold: 80.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Gas Sensor G-03", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 305, Y: 105, Z: 1, ZoneID: zones[5].ID}, SensorType: SensorTypeGas, CurrentValue: 0.0, Unit: "ppm", Threshold: 10.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Temp Sensor T-02", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 100, Y: 80, Z: 2, ZoneID: zones[4].ID}, SensorType: SensorTypeTemperature, CurrentValue: 32.0, Unit: "°C", Threshold: 45.0},
	}

	workers := []Worker{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Alex Rivera", CreatedAt: now(), UpdatedAt: now()}, X: 15, Y: 15, Z: 0, ZoneID: zones[0].ID}, Role: WorkerRoleOperator, Department: "Operations", CurrentPPE: []string{"HELMET", "VEST", "GLOVES", "GOGGLES"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Sam Chen", CreatedAt: now(), UpdatedAt: now()}, X: 55, Y: 12, Z: 0, ZoneID: zones[1].ID}, Role: WorkerRoleSupervisor, Department: "Operations", CurrentPPE: []string{"HELMET", "VEST"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Priya Sharma", CreatedAt: now(), UpdatedAt: now()}, X: 215, Y: 62, Z: 0, ZoneID: zones[2].ID}, Role: WorkerRoleOperator, Department: "Storage", CurrentPPE: []string{"HELMET", "VEST", "GLOVES"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Mike O'Brien", CreatedAt: now(), UpdatedAt: now()}, X: 105, Y: 82, Z: 0, ZoneID: zones[4].ID}, Role: WorkerRoleMaintenance, Department: "Maintenance", CurrentPPE: []string{"HELMET", "VEST", "GLOVES", "GOGGLES", "EARPLUGS"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Elena Torres", CreatedAt: now(), UpdatedAt: now()}, X: 5, Y: 152, Z: 0, ZoneID: zones[6].ID}, Role: WorkerRoleSafetyOfficer, Department: "Safety", CurrentPPE: []string{"HELMET", "VEST"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "James Wilson", CreatedAt: now(), UpdatedAt: now()}, X: 155, Y: 122, Z: 0, ZoneID: zones[7].ID}, Role: WorkerRoleMaintenance, Department: "Maintenance", CurrentPPE: []string{"HELMET", "VEST", "GLOVES"}, Shift: "NIGHT", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Fatima Al-Rashid", CreatedAt: now(), UpdatedAt: now()}, X: 225, Y: 42, Z: 0, ZoneID: zones[3].ID}, Role: WorkerRoleOperator, Department: "Logistics", CurrentPPE: []string{"HELMET", "VEST"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Bob Harper", CreatedAt: now(), UpdatedAt: now()}, X: 20, Y: 15, Z: 0, ZoneID: zones[0].ID}, Role: WorkerRoleContractor, Department: "External", CurrentPPE: []string{"HELMET"}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Diana Prince", CreatedAt: now(), UpdatedAt: now()}, X: 10, Y: 155, Z: 0, ZoneID: zones[6].ID}, Role: WorkerRoleSupervisor, Department: "Administration", CurrentPPE: []string{}, Shift: "DAY", WorkerStatus: WorkerStatusActive},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Carlos Mendez", CreatedAt: now(), UpdatedAt: now()}, X: 160, Y: 118, Z: 0, ZoneID: zones[7].ID}, Role: WorkerRoleOperator, Department: "Operations", CurrentPPE: []string{"HELMET", "VEST", "GLOVES"}, Shift: "NIGHT", WorkerStatus: WorkerStatusOnBreak},
	}

	vehicles := []Vehicle{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Forklift-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 100, Y: 85, Z: 0, ZoneID: zones[4].ID}, VehicleType: "FORKLIFT", Capacity: n(5.0)},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Truck-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 225, Y: 45, Z: 0, ZoneID: zones[3].ID}, VehicleType: "TRUCK", Capacity: n(20.0)},
	}

	cameras := []Camera{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "CAM-Reactor-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 10, Y: 10, Z: 10, ZoneID: zones[0].ID}, Direction: 180, CoverageRadius: 15},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "CAM-TankFarm-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 210, Y: 60, Z: 8, ZoneID: zones[2].ID}, Direction: 270, CoverageRadius: 20},
	}

	equipment := []Equipment{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Reactor Vessel R-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 15, Y: 15, Z: 0, ZoneID: zones[0].ID}, EquipmentType: "REACTOR", Manufacturer: "IndustrialCorp", Criticality: "CRITICAL"},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Pump P-100", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 20, Y: 20, Z: 0, ZoneID: zones[0].ID}, EquipmentType: "PUMP", Manufacturer: "FluidTech", Criticality: "HIGH"},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Compressor C-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 100, Y: 85, Z: 0, ZoneID: zones[4].ID}, EquipmentType: "COMPRESSOR", Manufacturer: "AirComp", Criticality: "MEDIUM"},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Generator G-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 5, Y: 155, Z: 0, ZoneID: zones[6].ID}, EquipmentType: "GENERATOR", Manufacturer: "PowerGen", Criticality: "HIGH"},
	}

	pipelines := []Pipeline{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Pipe-Crude-Main", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 10, Y: 10, Z: -1, ZoneID: zones[0].ID}, SourceID: zones[0].ID, DestinationID: zones[2].ID, Material: "CRUDE_OIL", PressureRating: 50.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Pipe-Gas-Feed", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 15, Y: 15, Z: -1, ZoneID: zones[0].ID}, SourceID: zones[0].ID, DestinationID: zones[5].ID, Material: "NATURAL_GAS", PressureRating: 30.0},
	}

	valves := []Valve{
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Valve-VC-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 12, Y: 12, Z: 0, ZoneID: zones[0].ID}, PipelineID: pipelines[0].ID, CurrentState: ValveStateOpen, Health: 95.0},
		{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Valve-VG-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, X: 17, Y: 17, Z: 0, ZoneID: zones[0].ID}, PipelineID: pipelines[1].ID, CurrentState: ValveStateOpen, Health: 88.0},
	}

	permits := []Permit{
		{BaseObject: BaseObject{ID: generateID(), Name: "Hot Work Permit #2024-01", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, PermitType: "HOT_WORK", AssignedTo: workers[3].ID, ValidFrom: "2026-07-01T08:00:00Z", ValidUntil: "2026-07-01T17:00:00Z", ApprovedBy: workers[1].ID},
		{BaseObject: BaseObject{ID: generateID(), Name: "Confined Space Entry #2024-02", Status: StatusOnline, CreatedAt: now(), UpdatedAt: now()}, PermitType: "CONFINED_SPACE", AssignedTo: workers[5].ID, ValidFrom: "2026-07-01T09:00:00Z", ValidUntil: "2026-07-01T15:00:00Z", ApprovedBy: workers[1].ID},
	}

	weather := WeatherState{
		Temperature: 28.5, Humidity: 62.0, WindSpeed: 12.0, WindDirection: 180.0,
		Condition: "PARTLY_CLOUDY", LastUpdated: now().UTC().Format(time.RFC3339),
	}

	return NewPlantStateBuilder().
		WithVersion(1).
		WithPlant(plant).
		WithBuildings([]Building{building1, building2}).
		WithZones(zones).
		WithSensors(sensors).
		WithWorkers(workers).
		WithVehicles(vehicles).
		WithCameras(cameras).
		WithEquipment(equipment).
		WithPipelines(pipelines).
		WithValves(valves).
		WithPermits(permits).
		WithExits([]EmergencyExit{
			{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Exit-North", CreatedAt: now(), UpdatedAt: now()}, X: 50, Y: 0, Z: 0}, IsBlocked: false},
			{PhysicalObject: PhysicalObject{BaseObject: BaseObject{ID: generateID(), Name: "Exit-South", CreatedAt: now(), UpdatedAt: now()}, X: 50, Y: 200, Z: 0}, IsBlocked: false},
		}).
		WithWeather(weather).
		Build()
}

func intPtr(i int) *int { return &i }
