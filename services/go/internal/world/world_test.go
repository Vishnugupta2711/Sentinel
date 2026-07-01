package world

import (
	"testing"

	pb "github.com/sentinel/services/go/pkg/proto/world"
)

func TestPlantStateBuilder(t *testing.T) {
	b := NewPlantStateBuilder()
	state := b.WithVersion(1).Build()

	if state.Version != 1 {
		t.Errorf("expected version 1, got %d", state.Version)
	}
	if state.Timestamp.IsZero() {
		t.Error("expected non-zero timestamp")
	}
}

func TestSamplePlantState(t *testing.T) {
	state := SamplePlantState()

	if state.Plant.Name != "Sentinel Refinery" {
		t.Errorf("expected 'Sentinel Refinery', got '%s'", state.Plant.Name)
	}
	if state.Version != 1 {
		t.Errorf("expected version 1, got %d", state.Version)
	}
	if len(state.Sensors) == 0 {
		t.Error("expected at least one sensor")
	}
	if len(state.Workers) == 0 {
		t.Error("expected at least one worker")
	}
	if len(state.Zones) == 0 {
		t.Error("expected at least one zone")
	}
}

func TestInMemorySnapshotStore(t *testing.T) {
	store := NewInMemorySnapshotStore(10)

	v, err := store.Store(SamplePlantState())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if v != 1 {
		t.Errorf("expected version 1, got %d", v)
	}

	v2, err := store.Store(SamplePlantState())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if v2 != 2 {
		t.Errorf("expected version 2, got %d", v2)
	}

	latest, err := store.Latest()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if latest.Version != 2 {
		t.Errorf("expected latest version 2, got %d", latest.Version)
	}

	snap, err := store.Get(1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if snap.Version != 1 {
		t.Errorf("expected version 1, got %d", snap.Version)
	}

	_, err = store.Get(999)
	if err == nil {
		t.Error("expected error for non-existent snapshot")
	}

	snapshots, err := store.List(1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(snapshots) != 1 {
		t.Errorf("expected 1 snapshot, got %d", len(snapshots))
	}
	if snapshots[0].Version != 2 {
		t.Errorf("expected latest snapshot version 2, got %d", snapshots[0].Version)
	}

	emptyStore := NewInMemorySnapshotStore(10)
	_, err = emptyStore.Latest()
	if err == nil {
		t.Error("expected error on empty store")
	}
}

func TestInMemorySnapshotStoreMaxRetention(t *testing.T) {
	store := NewInMemorySnapshotStore(3)

	for i := 0; i < 5; i++ {
		store.Store(SamplePlantState())
	}

	if store.Len() != 3 {
		t.Errorf("expected 3 retained snapshots, got %d", store.Len())
	}

	list, _ := store.List(10)
	if len(list) != 3 {
		t.Errorf("expected 3 from list, got %d", len(list))
	}
}

func TestDiffEngine(t *testing.T) {
	engine := NewDiffEngine()
	old := SamplePlantState()

	new := SamplePlantState()
	new.Version = 2
	new.Weather.Temperature = 35.0
	if len(new.Sensors) > 0 {
		new.Sensors[0].CurrentValue = 99.9
	}

	diff := engine.Diff(old, new)

	if !diff.HasChanges {
		t.Error("expected changes")
	}

	if diff.Weather == nil || diff.Weather.Temperature != 35.0 {
		t.Error("expected weather temperature change")
	}
}

func TestDiffEngineNoChanges(t *testing.T) {
	engine := NewDiffEngine()
	state := SamplePlantState()

	diff := engine.Diff(state, state)
	if diff.HasChanges {
		t.Error("expected no changes when comparing identical states")
	}
}

func TestDiffEngineAddedRemoved(t *testing.T) {
	engine := NewDiffEngine()
	old := newPlantStateForTest([]string{"w1", "w2", "w3"}, []string{"s1"})
	new := newPlantStateForTest([]string{"w2", "w3", "w4"}, []string{"s1"})

	diff := engine.Diff(old, new)

	foundRemoved := false
	foundAdded := false
	for _, w := range diff.Workers {
		if w.Type == DiffRemoved && w.EntityID == "w1" {
			foundRemoved = true
		}
		if w.Type == DiffAdded && w.EntityID == "w4" {
			foundAdded = true
		}
	}
	if !foundRemoved {
		t.Error("expected removed diff for w1")
	}
	if !foundAdded {
		t.Error("expected added diff for w4")
	}
	if len(diff.Sensors) != 0 {
		t.Error("expected no sensor diffs")
	}
}

func newPlantStateForTest(workerIDs, sensorIDs []string) PlantState {
	state := SamplePlantState()
	state.Workers = make([]Worker, len(workerIDs))
	for i, id := range workerIDs {
		state.Workers[i] = Worker{
			PhysicalObject: PhysicalObject{
				BaseObject: BaseObject{ID: id, Name: "worker-" + id},
			},
			Role: WorkerRoleOperator,
		}
	}
	state.Sensors = make([]Sensor, len(sensorIDs))
	for i, id := range sensorIDs {
		state.Sensors[i] = Sensor{
			PhysicalObject: PhysicalObject{
				BaseObject: BaseObject{ID: id, Name: "sensor-" + id},
			},
			SensorType: SensorTypeTemperature,
		}
	}
	return state
}

func TestWorldServiceGetSnapshot(t *testing.T) {
	store := NewInMemorySnapshotStore(10)
	engine := NewDiffEngine()
	svc := NewWorldService(store, engine)

	state := SamplePlantState()
	store.Store(state)

	resp, err := svc.GetSnapshot(t.Context(), &pb.GetSnapshotRequest{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp == nil || resp.Snapshot == nil {
		t.Fatal("expected non-nil response")
	}
	if resp.Snapshot.Plant.Name != state.Plant.Name {
		t.Errorf("expected plant name %s, got %s", state.Plant.Name, resp.Snapshot.Plant.Name)
	}
}

func TestWorldServiceListSnapshots(t *testing.T) {
	store := NewInMemorySnapshotStore(100)
	engine := NewDiffEngine()
	svc := NewWorldService(store, engine)

	for i := 0; i < 5; i++ {
		store.Store(SamplePlantState())
	}

	listResp, err := svc.ListSnapshots(t.Context(), &pb.ListSnapshotsRequest{Limit: 3})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(listResp.Snapshots) != 3 {
		t.Errorf("expected 3 snapshots, got %d", len(listResp.Snapshots))
	}
	if listResp.Total != 5 {
		t.Errorf("expected total 5, got %d", listResp.Total)
	}
}

func TestWorldServiceGetSnapshotByVersion(t *testing.T) {
	store := NewInMemorySnapshotStore(10)
	engine := NewDiffEngine()
	svc := NewWorldService(store, engine)

	s1 := SamplePlantState()
	s1.Plant.Name = "Plant Alpha"
	store.Store(s1)

	s2 := SamplePlantState()
	s2.Plant.Name = "Plant Beta"
	v2, _ := store.Store(s2)

	resp, err := svc.GetSnapshot(t.Context(), &pb.GetSnapshotRequest{Version: v2})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Snapshot.Plant.Name != "Plant Beta" {
		t.Errorf("expected 'Plant Beta', got '%s'", resp.Snapshot.Plant.Name)
	}
}

func TestGenerateID(t *testing.T) {
	id1 := GenerateID()
	id2 := GenerateID()

	if id1 == id2 {
		t.Error("expected unique IDs")
	}
	if len(id1) != 36 {
		t.Errorf("expected UUID length 36, got %d", len(id1))
	}
}
