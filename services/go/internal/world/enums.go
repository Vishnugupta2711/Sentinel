package world

type Status string

const (
	StatusOnline      Status = "ONLINE"
	StatusOffline     Status = "OFFLINE"
	StatusWarning     Status = "WARNING"
	StatusCritical    Status = "CRITICAL"
	StatusMaintenance Status = "MAINTENANCE"
)

type SensorType string

const (
	SensorTypeGas         SensorType = "GAS"
	SensorTypeTemperature SensorType = "TEMPERATURE"
	SensorTypePressure    SensorType = "PRESSURE"
	SensorTypeHumidity    SensorType = "HUMIDITY"
	SensorTypeFlow        SensorType = "FLOW"
	SensorTypeVibration   SensorType = "VIBRATION"
	SensorTypeSmoke       SensorType = "SMOKE"
)

type WorkerRole string

const (
	WorkerRoleOperator     WorkerRole = "OPERATOR"
	WorkerRoleSupervisor   WorkerRole = "SUPERVISOR"
	WorkerRoleMaintenance  WorkerRole = "MAINTENANCE"
	WorkerRoleSafetyOfficer WorkerRole = "SAFETY_OFFICER"
	WorkerRoleContractor   WorkerRole = "CONTRACTOR"
)

type WorkerStatus string

const (
	WorkerStatusActive    WorkerStatus = "ACTIVE"
	WorkerStatusOnBreak   WorkerStatus = "ON_BREAK"
	WorkerStatusOffShift  WorkerStatus = "OFF_SHIFT"
	WorkerStatusEmergency WorkerStatus = "EMERGENCY"
)

type HazardType string

const (
	HazardTypeGasLeak    HazardType = "GAS_LEAK"
	HazardTypeFire       HazardType = "FIRE"
	HazardTypeSpill      HazardType = "SPILL"
	HazardTypeStructural HazardType = "STRUCTURAL"
	HazardTypeElectrical HazardType = "ELECTRICAL"
)

type HazardSeverity string

const (
	HazardSeverityLow      HazardSeverity = "LOW"
	HazardSeverityMedium   HazardSeverity = "MEDIUM"
	HazardSeverityHigh     HazardSeverity = "HIGH"
	HazardSeverityCritical HazardSeverity = "CRITICAL"
)

type ValveState string

const (
	ValveStateOpen    ValveState = "OPEN"
	ValveStateClosed  ValveState = "CLOSED"
	ValveStatePartial ValveState = "PARTIAL"
	ValveStateFault   ValveState = "FAULT"
)
