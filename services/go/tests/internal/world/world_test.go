package world_test

import (
	"testing"
	"time"

	"github.com/sentinel/services/go/internal/world"
	pb "github.com/sentinel/services/go/pkg/proto/world"
)

func TestSamplePlantStateHasContent(t *testing.T) {
	state := world.SamplePlantState()

	if state.Plant.Name == "" {
		t.Error("expected plant name to be non-empty")
	}
	if len(state.Sensors) < 3 {
		t.Errorf("expected at least 3 sensors, got %d", len(state.Sensors))
	}
	if len(state.Workers) < 3 {
		t.Errorf("expected at least 3 workers, got %d", len(state.Workers))
	}
	if len(state.Zones) < 3 {
		t.Errorf("expected at least 3 zones, got %d", len(state.Zones))
	}
	if len(state.Buildings) == 0 {
		t.Error("expected at least one building")
	}
	if len(state.Valves) == 0 {
		t.Error("expected at least one valve")
	}
}

func TestSnapshotStoreBasic(t *testing.T) {
	store := world.NewInMemorySnapshotStore(10)

	v, err := store.Store(world.SamplePlantState())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if v != 1 {
		t.Errorf("expected version 1, got %d", v)
	}

	latest, err := store.Latest()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if latest.Version != 1 {
		t.Errorf("expected latest version 1, got %d", latest.Version)
	}

	got, err := store.Get(1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Plant.Name != "Sentinel Refinery" {
		t.Errorf("expected 'Sentinel Refinery', got '%s'", got.Plant.Name)
	}
}

func TestDiffEngineDetectsChanges(t *testing.T) {
	engine := world.NewDiffEngine()
	old := world.SamplePlantState()

	new := world.SamplePlantState()
	new.Version = 2
	new.Weather.Temperature = 99.9

	diff := engine.Diff(old, new)
	if !diff.HasChanges {
		t.Error("expected changes when weather differs")
	}
}

func TestDiffEngineNoChanges(t *testing.T) {
	engine := world.NewDiffEngine()
	state := world.SamplePlantState()

	diff := engine.Diff(state, state)
	if diff.HasChanges {
		t.Error("expected no changes for identical states")
	}
}

func TestWorldServiceGetLatest(t *testing.T) {
	store := world.NewInMemorySnapshotStore(10)
	engine := world.NewDiffEngine()
	svc := world.NewWorldService(store, engine)

	store.Store(world.SamplePlantState())

	resp, err := svc.GetSnapshot(t.Context(), &pb.GetSnapshotRequest{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Snapshot.Version != 1 {
		t.Errorf("expected version 1, got %d", resp.Snapshot.Version)
	}
	if resp.Snapshot.Plant.Name != "Sentinel Refinery" {
		t.Errorf("expected 'Sentinel Refinery', got '%s'", resp.Snapshot.Plant.Name)
	}
}

func TestWorldServiceGetByVersion(t *testing.T) {
	store := world.NewInMemorySnapshotStore(10)
	engine := world.NewDiffEngine()
	svc := world.NewWorldService(store, engine)

	s1 := world.SamplePlantState()
	s1.Plant.Name = "Plant Alpha"
	v1, _ := store.Store(s1)

	s2 := world.SamplePlantState()
	s2.Plant.Name = "Plant Beta"
	store.Store(s2)

	resp, err := svc.GetSnapshot(t.Context(), &pb.GetSnapshotRequest{Version: v1})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Snapshot.Plant.Name != "Plant Alpha" {
		t.Errorf("expected 'Plant Alpha', got '%s'", resp.Snapshot.Plant.Name)
	}
}

func TestWorldServiceList(t *testing.T) {
	store := world.NewInMemorySnapshotStore(100)
	engine := world.NewDiffEngine()
	svc := world.NewWorldService(store, engine)

	for i := 0; i < 5; i++ {
		store.Store(world.SamplePlantState())
	}

	resp, err := svc.ListSnapshots(t.Context(), &pb.ListSnapshotsRequest{Limit: 3})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Snapshots) != 3 {
		t.Errorf("expected 3 snapshots, got %d", len(resp.Snapshots))
	}
}

func TestEventBusPublishSubscribe(t *testing.T) {
	bus := world.NewEventBus()
	sub := bus.Subscribe("test", 10)

	bus.Publish("test", "hello")

	select {
	case evt := <-sub.C():
		if evt.Payload != "hello" {
			t.Errorf("expected 'hello', got '%v'", evt.Payload)
		}
	default:
		t.Fatal("expected event")
	}

	sub.Close()
}

func TestSimulatorProducesSnapshots(t *testing.T) {
	bus := world.NewEventBus()
	store := world.NewInMemorySnapshotStore(100)
	engine := world.NewDiffEngine()

	store.Store(world.SamplePlantState())

	sim := world.NewSimulator(store, engine, bus, 10*time.Millisecond)
	sim.Start()
	defer sim.Stop()

	for i := 0; i < 100; i++ {
		latest, _ := store.Latest()
		if latest.Version > 1 {
			return
		}
		time.Sleep(5 * time.Millisecond)
	}

	t.Error("expected simulator to produce at least one tick")
}

func TestBuilderPattern(t *testing.T) {
	b := world.NewPlantStateBuilder()
	state := b.WithVersion(42).Build()

	if state.Version != 42 {
		t.Errorf("expected version 42, got %d", state.Version)
	}
}
