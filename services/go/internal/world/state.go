package world

import "time"

type PlantState struct {
	Version   int          `json:"version"`
	Timestamp time.Time    `json:"timestamp"`
	Plant     Plant        `json:"plant"`
	Buildings []Building   `json:"buildings"`
	Zones     []Zone       `json:"zones"`
	Sensors   []Sensor     `json:"sensors"`
	Workers   []Worker     `json:"workers"`
	Vehicles  []Vehicle    `json:"vehicles"`
	Cameras   []Camera     `json:"cameras"`
	Equipment []Equipment  `json:"equipment"`
	Pipelines []Pipeline   `json:"pipelines"`
	Valves    []Valve      `json:"valves"`
	Permits   []Permit     `json:"permits"`
	Hazards   []Hazard     `json:"hazards"`
	Exits     []EmergencyExit `json:"exits"`
	Weather   WeatherState `json:"weather"`
}
