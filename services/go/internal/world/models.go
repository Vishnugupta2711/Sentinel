package world

import "time"

type BaseObject struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Description string            `json:"description,omitempty"`
	Status      Status            `json:"status"`
	CreatedAt   time.Time         `json:"created_at"`
	UpdatedAt   time.Time         `json:"updated_at"`
	Metadata    map[string]any   `json:"metadata,omitempty"`
}

type PhysicalObject struct {
	BaseObject
	X          float64  `json:"x"`
	Y          float64  `json:"y"`
	Z          float64  `json:"z"`
	ZoneID     string   `json:"zone_id,omitempty"`
	BuildingID string   `json:"building_id,omitempty"`
	Latitude   *float64 `json:"latitude,omitempty"`
	Longitude  *float64 `json:"longitude,omitempty"`
}

type Plant struct {
	BaseObject
	Address  string `json:"address,omitempty"`
	Manager  string `json:"manager,omitempty"`
	Capacity *float64 `json:"capacity,omitempty"`
}

type Building struct {
	PhysicalObject
	Floors       int  `json:"floors"`
	MaxOccupancy *int `json:"max_occupancy,omitempty"`
}

type Zone struct {
	PhysicalObject
	HazardLevel     string `json:"hazard_level"`
	MaxCapacity     *int   `json:"max_capacity,omitempty"`
	CurrentOccupancy int   `json:"current_occupancy"`
}

type Sensor struct {
	PhysicalObject
	SensorType  SensorType `json:"sensor_type"`
	CurrentValue float64   `json:"current_value"`
	Unit        string     `json:"unit"`
	Threshold   float64    `json:"threshold"`
	LastUpdated string     `json:"last_updated"`
}

type Worker struct {
	PhysicalObject
	Role        WorkerRole   `json:"role"`
	Department  string       `json:"department"`
	CurrentPPE  []string     `json:"current_ppe"`
	Shift       string       `json:"shift"`
	WorkerStatus WorkerStatus `json:"worker_status"`
}

type Vehicle struct {
	PhysicalObject
	VehicleType string `json:"vehicle_type"`
	DriverID    string `json:"driver_id,omitempty"`
	Capacity    *float64 `json:"capacity,omitempty"`
}

type Camera struct {
	PhysicalObject
	Direction      float64 `json:"direction"`
	CoverageRadius float64 `json:"coverage_radius"`
}

type Equipment struct {
	PhysicalObject
	EquipmentType     string `json:"equipment_type"`
	Manufacturer      string `json:"manufacturer"`
	Criticality       string `json:"criticality"`
	MaintenanceStatus Status `json:"maintenance_status"`
}

type Pipeline struct {
	PhysicalObject
	SourceID      string  `json:"source_id"`
	DestinationID string  `json:"destination_id"`
	Material      string  `json:"material"`
	PressureRating float64 `json:"pressure_rating"`
}

type Valve struct {
	PhysicalObject
	PipelineID   string     `json:"pipeline_id"`
	CurrentState ValveState `json:"current_state"`
	Health       float64    `json:"health"`
}

type Permit struct {
	BaseObject
	PermitType  string `json:"permit_type"`
	AssignedTo  string `json:"assigned_to"`
	ValidFrom   string `json:"valid_from"`
	ValidUntil  string `json:"valid_until"`
	ApprovedBy  string `json:"approved_by,omitempty"`
}

type Hazard struct {
	PhysicalObject
	HazardType HazardType     `json:"hazard_type"`
	Severity   HazardSeverity `json:"severity"`
	Radius     float64        `json:"radius"`
	IsActive   bool           `json:"is_active"`
}

type EmergencyExit struct {
	PhysicalObject
	IsBlocked bool  `json:"is_blocked"`
	Capacity  *int  `json:"capacity,omitempty"`
}

type WeatherState struct {
	Temperature  float64 `json:"temperature"`
	Humidity     float64 `json:"humidity"`
	WindSpeed    float64 `json:"wind_speed"`
	WindDirection float64 `json:"wind_direction"`
	Condition    string  `json:"condition"`
	LastUpdated  string  `json:"last_updated"`
}
