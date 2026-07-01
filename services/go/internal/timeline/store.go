package timeline

import (
	"sync"
	"time"

	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

type Store interface {
	Record(entry *pb.TimelineEntry) error
	Query(query *pb.TimelineQuery) ([]*pb.TimelineEntry, int32, error)
	Replay(fromVersion, toVersion int64) ([]*pb.TimelineEntry, error)
}

type InMemoryStore struct {
	mu      sync.RWMutex
	entries []*pb.TimelineEntry
	max     int
}

func NewInMemoryStore(maxEntries int) *InMemoryStore {
	return &InMemoryStore{
		entries: make([]*pb.TimelineEntry, 0, maxEntries),
		max:     maxEntries,
	}
}

func (s *InMemoryStore) Record(entry *pb.TimelineEntry) error {
	if entry.Timestamp == nil {
		entry.Timestamp = &common.Timestamp{
			Seconds: time.Now().Unix(),
		}
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	s.entries = append(s.entries, entry)
	if len(s.entries) > s.max {
		s.entries = s.entries[len(s.entries)-s.max:]
	}
	return nil
}

func (s *InMemoryStore) Query(query *pb.TimelineQuery) ([]*pb.TimelineEntry, int32, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var matched []*pb.TimelineEntry

	startSec := int64(0)
	endSec := int64(1<<63 - 1)
	if query.Start != nil {
		startSec = query.Start.Seconds
	}
	if query.End != nil {
		endSec = query.End.Seconds
	}

	entityFilter := make(map[string]bool, len(query.EntityIds))
	for _, id := range query.EntityIds {
		entityFilter[id] = true
	}
	typeFilter := make(map[string]bool, len(query.EventTypes))
	for _, et := range query.EventTypes {
		typeFilter[et] = true
	}

	for _, e := range s.entries {
		ts := e.Timestamp.GetSeconds()
		if ts < startSec || ts > endSec {
			continue
		}
		if len(entityFilter) > 0 && !entityFilter[e.EntityId] {
			continue
		}
		if len(typeFilter) > 0 && !typeFilter[e.EventType] {
			continue
		}
		matched = append(matched, e)
	}

	total := int32(len(matched))
	limit := int(query.Limit)
	offset := int(query.Offset)

	if offset > len(matched) {
		return []*pb.TimelineEntry{}, total, nil
	}
	matched = matched[offset:]

	if limit > 0 && limit < len(matched) {
		matched = matched[:limit]
	}

	return matched, total, nil
}

func (s *InMemoryStore) Replay(fromVersion, toVersion int64) ([]*pb.TimelineEntry, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var result []*pb.TimelineEntry
	for _, e := range s.entries {
		if e.Version >= fromVersion && e.Version <= toVersion {
			result = append(result, e)
		}
	}

	if result == nil {
		return []*pb.TimelineEntry{}, nil
	}
	return result, nil
}

func (s *InMemoryStore) Len() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.entries)
}
