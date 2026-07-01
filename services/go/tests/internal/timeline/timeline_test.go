package timeline_test

import (
	"testing"

	"github.com/sentinel/services/go/internal/timeline"
	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

func TestTimelineRecordAndQuery(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	for i := 1; i <= 10; i++ {
		err := store.Record(&pb.TimelineEntry{
			Version:    int64(i),
			EntityId:   "sensor-temp",
			EntityType: "SENSOR",
			EventType:  "SENSOR_UPDATED",
			Timestamp:  &common.Timestamp{Seconds: int64(i * 100)},
		})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
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
}

func TestTimelineQueryLimit(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	for i := 1; i <= 5; i++ {
		store.Record(&pb.TimelineEntry{Version: int64(i)})
	}

	entries, total, err := store.Query(&pb.TimelineQuery{Limit: 2})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(entries))
	}
	if total != 5 {
		t.Errorf("expected total 5, got %d", total)
	}
}

func TestTimelineReplay(t *testing.T) {
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
}

func TestTimelineServiceRecordAndQuery(t *testing.T) {
	store := timeline.NewInMemoryStore(100)
	svc := timeline.NewService(store)

	for i := 1; i <= 3; i++ {
		_, err := svc.Record(t.Context(), &pb.RecordRequest{
			Entry: &pb.TimelineEntry{Version: int64(i)},
		})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
	}

	result, err := svc.Query(t.Context(), &pb.TimelineQuery{Limit: 2})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(result.Entries) != 2 {
		t.Errorf("expected 2 entries, got %d", len(result.Entries))
	}
}

func TestTimelineEntityFilter(t *testing.T) {
	store := timeline.NewInMemoryStore(100)

	store.Record(&pb.TimelineEntry{Version: 1, EntityId: "sensor-a"})
	store.Record(&pb.TimelineEntry{Version: 2, EntityId: "sensor-b"})
	store.Record(&pb.TimelineEntry{Version: 3, EntityId: "sensor-a"})

	entries, total, err := store.Query(&pb.TimelineQuery{
		EntityIds: []string{"sensor-a"},
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
