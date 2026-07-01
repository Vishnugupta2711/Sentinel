package world

import "reflect"

type DiffType string

const (
	DiffAdded   DiffType = "ADDED"
	DiffRemoved DiffType = "REMOVED"
	DiffUpdated DiffType = "UPDATED"
)

type EntityDiff[T any] struct {
	Type      DiffType `json:"type"`
	EntityID  string   `json:"entity_id"`
	OldEntity *T       `json:"old_entity,omitempty"`
	NewEntity *T       `json:"new_entity,omitempty"`
}

type WorldDiff struct {
	Version    int                    `json:"version"`
	Buildings  []EntityDiff[Building]   `json:"buildings,omitempty"`
	Zones      []EntityDiff[Zone]       `json:"zones,omitempty"`
	Sensors    []EntityDiff[Sensor]     `json:"sensors,omitempty"`
	Workers    []EntityDiff[Worker]     `json:"workers,omitempty"`
	Vehicles   []EntityDiff[Vehicle]    `json:"vehicles,omitempty"`
	Cameras    []EntityDiff[Camera]     `json:"cameras,omitempty"`
	Equipment  []EntityDiff[Equipment]  `json:"equipment,omitempty"`
	Pipelines  []EntityDiff[Pipeline]   `json:"pipelines,omitempty"`
	Valves     []EntityDiff[Valve]      `json:"valves,omitempty"`
	Permits    []EntityDiff[Permit]     `json:"permits,omitempty"`
	Hazards    []EntityDiff[Hazard]     `json:"hazards,omitempty"`
	Exits      []EntityDiff[EmergencyExit] `json:"exits,omitempty"`
	Weather    *WeatherState           `json:"weather,omitempty"`
	HasChanges bool                    `json:"has_changes"`
}

type DiffEngine struct{}

func NewDiffEngine() *DiffEngine {
	return &DiffEngine{}
}

func (e *DiffEngine) Diff(old, new PlantState) WorldDiff {
	d := WorldDiff{Version: new.Version}

	d.Buildings = diffSlice(old.Buildings, new.Buildings, func(b Building) string { return b.ID })
	d.Zones = diffSlice(old.Zones, new.Zones, func(z Zone) string { return z.ID })
	d.Sensors = diffSlice(old.Sensors, new.Sensors, func(s Sensor) string { return s.ID })
	d.Workers = diffSlice(old.Workers, new.Workers, func(w Worker) string { return w.ID })
	d.Vehicles = diffSlice(old.Vehicles, new.Vehicles, func(v Vehicle) string { return v.ID })
	d.Cameras = diffSlice(old.Cameras, new.Cameras, func(c Camera) string { return c.ID })
	d.Equipment = diffSlice(old.Equipment, new.Equipment, func(eq Equipment) string { return eq.ID })
	d.Pipelines = diffSlice(old.Pipelines, new.Pipelines, func(p Pipeline) string { return p.ID })
	d.Valves = diffSlice(old.Valves, new.Valves, func(v Valve) string { return v.ID })
	d.Permits = diffSlice(old.Permits, new.Permits, func(p Permit) string { return p.ID })
	d.Hazards = diffSlice(old.Hazards, new.Hazards, func(h Hazard) string { return h.ID })
	d.Exits = diffSlice(old.Exits, new.Exits, func(e EmergencyExit) string { return e.ID })

	if !reflect.DeepEqual(old.Weather, new.Weather) {
		w := new.Weather
		d.Weather = &w
	}

	d.HasChanges = len(d.Buildings) > 0 || len(d.Zones) > 0 || len(d.Sensors) > 0 ||
		len(d.Workers) > 0 || len(d.Vehicles) > 0 || len(d.Cameras) > 0 ||
		len(d.Equipment) > 0 || len(d.Pipelines) > 0 || len(d.Valves) > 0 ||
		len(d.Permits) > 0 || len(d.Hazards) > 0 || len(d.Exits) > 0 || d.Weather != nil

	return d
}

func diffSlice[T any](old, new []T, getID func(T) string) []EntityDiff[T] {
	oldMap := make(map[string]T, len(old))
	for _, item := range old {
		oldMap[getID(item)] = item
	}

	newMap := make(map[string]T, len(new))
	for _, item := range new {
		newMap[getID(item)] = item
	}

	var diffs []EntityDiff[T]

	for _, item := range new {
		id := getID(item)
		if _, exists := oldMap[id]; !exists {
			e := item
			diffs = append(diffs, EntityDiff[T]{Type: DiffAdded, EntityID: id, NewEntity: &e})
		}
	}

	for _, item := range old {
		id := getID(item)
		if _, exists := newMap[id]; !exists {
			e := item
			diffs = append(diffs, EntityDiff[T]{Type: DiffRemoved, EntityID: id, OldEntity: &e})
		}
	}

	for _, newItem := range new {
		id := getID(newItem)
		if oldItem, exists := oldMap[id]; exists {
			if !reflect.DeepEqual(newItem, oldItem) {
				o := oldItem
				n := newItem
				diffs = append(diffs, EntityDiff[T]{Type: DiffUpdated, EntityID: id, OldEntity: &o, NewEntity: &n})
			}
		}
	}

	return diffs
}
