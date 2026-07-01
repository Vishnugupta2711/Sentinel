package timeline_test

import (
	"testing"

	"github.com/sentinel/services/go/internal/timeline"
	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

func TestInMemoryStoreRecord(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	entry := &pb.TimelineEntry{
		Version:    1,
		EntityId:   "sensor-1",
		EntityType: "SENSOR",
		EventType:  "SENSOR_UPDATED",
		Snapshot:   []byte(`{"value": 42.0}`),
	}

	if err := store.Record(entry); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if store.Len() != 1 {
		t.Errorf("expected 1 entry, got %d", store.Len())
	}
}

func TestInMemoryStoreQuery(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	for i := 1; i <= 10; i++ {
		store.Record(&pb.TimelineEntry{
			Version:    int64(i),
			EntityId:   "sensor-temp",
			EntityType: "SENSOR",
			EventType:  "SENSOR_UPDATED",
			Timestamp: &common.Timestamp{Seconds: int64(i * 100)},
		})
	}

	entries, total, err := store.Query(&pb.TimelineQuery{
		Start: &common.Timestamp{Seconds: 200},
		End:   &common.Timestamp{Seconds: 800},
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if total != 7 {
		t.Errorf("expected 7 total, got %d", total)
	}
	if len(entries) != 7 {
		t.Errorf("expected 7 entries, got %d", len(entries))
	}

	entries, total, err = store.Query(&pb.TimelineQuery{
		EntityIds: []string{"sensor-temp"},
		Limit:     3,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(entries) != 3 {
		t.Errorf("expected 3 entries, got %d", len(entries))
	}
	_ = total
}

func TestInMemoryStoreQueryOffset(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	for i := 1; i <= 5; i++ {
		store.Record(&pb.TimelineEntry{
			Version:    int64(i),
			EntityId:   "sensor-1",
			EntityType: "SENSOR",
			EventType:  "SENSOR_UPDATED",
			Timestamp:  &common.Timestamp{Seconds: int64(i * 10)},
		})
	}

	entries, total, err := store.Query(&pb.TimelineQuery{
		Offset: 3,
		Limit:  10,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if total != 5 {
		t.Errorf("expected total 5, got %d", total)
	}
	if len(entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(entries))
	}
}

func TestInMemoryStoreQueryEntityFilter(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	store.Record(&pb.TimelineEntry{Version: 1, EntityId: "sensor-a", EntityType: "SENSOR", EventType: "UPDATED"})
	store.Record(&pb.TimelineEntry{Version: 2, EntityId: "sensor-b", EntityType: "SENSOR", EventType: "UPDATED"})

	entries, total, err := store.Query(&pb.TimelineQuery{
		EntityIds: []string{"sensor-a"},
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if total != 1 {
		t.Errorf("expected 1 total, got %d", total)
	}
	if len(entries) != 1 || entries[0].EntityId != "sensor-a" {
		t.Error("expected only sensor-a entries")
	}
}

func TestInMemoryStoreReplay(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	for i := 1; i <= 5; i++ {
		store.Record(&pb.TimelineEntry{Version: int64(i)})
	}

	entries, err := store.Replay(2, 4)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(entries) != 3 {
		t.Errorf("expected 3 entries, got %d", len(entries))
	}
	if entries[0].Version != 2 {
		t.Errorf("expected version 2, got %d", entries[0].Version)
	}
	if entries[2].Version != 4 {
		t.Errorf("expected version 4, got %d", entries[2].Version)
	}
}

func TestInMemoryStoreMaxRetention(t *testing.T) {
	store := timeline.NewInMemoryStore(3)

	for i := 1; i <= 10; i++ {
		store.Record(&pb.TimelineEntry{Version: int64(i)})
	}

	if store.Len() != 3 {
		t.Errorf("expected 3 retained entries, got %d", store.Len())
	}

	entries, err := store.Replay(8, 10)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(entries) != 3 {
		t.Errorf("expected 3 entries after retention, got %d", len(entries))
	}
}

func TestTimelineServiceRecord(t *testing.T) {
	store := timeline.NewInMemoryStore(100)
	svc := timeline.NewService(store)

	resp, err := svc.Record(t.Context(), &pb.RecordRequest{
		Entry: &pb.TimelineEntry{
			Version:   1,
			EntityId:  "hazard-1",
			EventType: "HAZARD_DETECTED",
		},
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Recorded {
		t.Error("expected recorded=true")
	}
	if store.Len() != 1 {
		t.Errorf("expected 1 entry, got %d", store.Len())
	}

	_, err = svc.Record(t.Context(), &pb.RecordRequest{})
	if err == nil {
		t.Error("expected error for nil entry")
	}
}

func TestTimelineServiceQuery(t *testing.T) {
	store := timeline.NewInMemoryStore(100)
	svc := timeline.NewService(store)

	for i := 1; i <= 3; i++ {
		svc.Record(t.Context(), &pb.RecordRequest{
			Entry: &pb.TimelineEntry{Version: int64(i), EventType: "TEST_EVENT"},
		})
	}

	result, err := svc.Query(t.Context(), &pb.TimelineQuery{Limit: 2})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(result.Entries))
	}
	if result.Total != 3 {
		t.Errorf("expected total 3, got %d", result.Total)
	}
}
