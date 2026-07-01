package infra_test

import (
	"testing"

	"github.com/sentinel/services/go/internal/infra"
	"github.com/sentinel/services/go/internal/world"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

func TestRedisStoreFallback(t *testing.T) {
	store := infra.NewRedisSnapshotStore("", 100)
	defer store.Close()

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
}

func TestRedisStoreList(t *testing.T) {
	store := infra.NewRedisSnapshotStore("", 100)
	defer store.Close()

	for i := 0; i < 5; i++ {
		store.Store(world.SamplePlantState())
	}

	list, err := store.List(2)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(list) != 2 {
		t.Errorf("expected 2 snapshots, got %d", len(list))
	}
}

func TestClickHouseStoreFallback(t *testing.T) {
	store := infra.NewClickHouseTimelineStore("", 100)

	entry := &pb.TimelineEntry{
		Version:   1,
		EntityId:  "sensor-1",
		EventType: "TEST",
	}

	err := store.Record(entry)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if store.Len() != 1 {
		t.Errorf("expected 1 entry, got %d", store.Len())
	}
}

func TestClickHouseStoreQuery(t *testing.T) {
	store := infra.NewClickHouseTimelineStore("", 100)

	store.Record(&pb.TimelineEntry{Version: 1, EntityId: "a"})
	store.Record(&pb.TimelineEntry{Version: 2, EntityId: "b"})
	store.Record(&pb.TimelineEntry{Version: 3, EntityId: "a"})

	entries, total, err := store.Query(&pb.TimelineQuery{
		EntityIds: []string{"a"},
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if total != 2 {
		t.Errorf("expected 2, got %d", total)
	}
	if len(entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(entries))
	}
}
