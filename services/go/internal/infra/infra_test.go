package infra_test

import (
	"testing"

	"github.com/sentinel/services/go/internal/infra"
	"github.com/sentinel/services/go/internal/world"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

func TestRedisSnapshotStoreInMemoryFallback(t *testing.T) {
	store := infra.NewRedisSnapshotStore("", 100)

	state := world.SamplePlantState()
	v, err := store.Store(state)
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
		t.Errorf("expected version 1, got %d", latest.Version)
	}

	if store.Len() != 1 {
		t.Errorf("expected 1 entry, got %d", store.Len())
	}

	store.Close()
}

func TestRedisSnapshotStoreGet(t *testing.T) {
	store := infra.NewRedisSnapshotStore("", 100)

	s1 := world.SamplePlantState()
	s1.Plant.Name = "Test Plant"
	v1, _ := store.Store(s1)

	got, err := store.Get(v1)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Plant.Name != "Test Plant" {
		t.Errorf("expected 'Test Plant', got '%s'", got.Plant.Name)
	}
}

func TestRedisSnapshotStoreList(t *testing.T) {
	store := infra.NewRedisSnapshotStore("", 100)

	for i := 0; i < 5; i++ {
		store.Store(world.SamplePlantState())
	}

	snapshots, err := store.List(3)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(snapshots) != 3 {
		t.Errorf("expected 3 snapshots, got %d", len(snapshots))
	}
}

func TestClickHouseTimelineStoreInMemoryFallback(t *testing.T) {
	pbtl := &pb.TimelineEntry{}
	pbtl.Version = 1
	pbtl.EntityId = "test"
	pbtl.EventType = "TEST"

	store := infra.NewClickHouseTimelineStore("", 100)
	err := store.Record(pbtl)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if store.Len() != 1 {
		t.Errorf("expected 1 entry, got %d", store.Len())
	}
}
