package world

import (
	"log"
	"math/rand"
	"time"
)

type Simulator struct {
	store       SnapshotStore
	diffEngine  *DiffEngine
	bus         *EventBus
	tickInterval time.Duration
	stopCh      chan struct{}
}

func NewSimulator(store SnapshotStore, diffEngine *DiffEngine, bus *EventBus, tickInterval time.Duration) *Simulator {
	return &Simulator{
		store:        store,
		diffEngine:   diffEngine,
		bus:          bus,
		tickInterval: tickInterval,
		stopCh:       make(chan struct{}),
	}
}

func (s *Simulator) Start() {
	go s.run()
}

func (s *Simulator) Stop() {
	close(s.stopCh)
}

func (s *Simulator) run() {
	ticker := time.NewTicker(s.tickInterval)
	defer ticker.Stop()

	for {
		select {
		case <-s.stopCh:
			return
		case <-ticker.C:
			s.tick()
		}
	}
}

func (s *Simulator) tick() {
	latest, err := s.store.Latest()
	if err != nil {
		log.Printf("simulator: no state to mutate: %v", err)
		return
	}

	next := s.mutate(*latest)
	next.Version = latest.Version + 1
	next.Timestamp = time.Now().UTC()

	v, err := s.store.Store(next)
	if err != nil {
		log.Printf("simulator: failed to store: %v", err)
		return
	}

	diff := s.diffEngine.Diff(*latest, next)
	diff.Version = int(v)

	s.bus.Publish("world.diff", diff)
}

func (s *Simulator) mutate(state PlantState) PlantState {
	for i := range state.Sensors {
		state.Sensors[i].CurrentValue += (rand.Float64()*2 - 1) * state.Sensors[i].CurrentValue * 0.02
	}

	for i := range state.Workers {
		move := rand.Float64()*4 - 2
		state.Workers[i].X += move
		move = rand.Float64()*4 - 2
		state.Workers[i].Y += move
	}

	state.Weather.Temperature += (rand.Float64()*2 - 1) * 0.5
	state.Weather.Humidity += (rand.Float64()*2 - 1) * 1.0
	state.Weather.WindSpeed += (rand.Float64()*2 - 1) * 2.0
	if state.Weather.WindSpeed < 0 {
		state.Weather.WindSpeed = 0
	}

	return state
}
