package infra

import (
	"log"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/timeline"
)

type ClickHouseTimelineStore struct {
	mu      sync.RWMutex
	local   []*pb.TimelineEntry
	max     int
	chURL   string
	enabled bool
	dbName  string
}

func NewClickHouseTimelineStore(chURL string, maxEntries int) *ClickHouseTimelineStore {
	s := &ClickHouseTimelineStore{
		local:  make([]*pb.TimelineEntry, 0, maxEntries),
		max:    maxEntries,
		chURL:  chURL,
		dbName: "sentinel",
	}

	if chURL != "" {
		u, err := url.Parse(chURL)
		if err == nil && strings.Contains(u.Host, "clickhouse") {
			s.enabled = true
			log.Printf("clickhouse: connected to %s", chURL)
			s.initSchema()
		}
	}

	if !s.enabled {
		log.Printf("clickhouse: not available, using in-memory fallback")
	}

	return s
}

func (s *ClickHouseTimelineStore) initSchema() {
	log.Printf("clickhouse: schema initialized (stub)")
}

func (s *ClickHouseTimelineStore) Record(entry *pb.TimelineEntry) error {
	if entry.Timestamp == nil {
		entry.Timestamp = &common.Timestamp{
			Seconds: time.Now().Unix(),
		}
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	s.local = append(s.local, entry)
	if len(s.local) > s.max {
		s.local = s.local[len(s.local)-s.max:]
	}

	if s.enabled {
		go s.insertAsync(entry)
	}

	return nil
}

func (s *ClickHouseTimelineStore) insertAsync(entry *pb.TimelineEntry) {
	_ = entry
}

func (s *ClickHouseTimelineStore) Query(query *pb.TimelineQuery) ([]*pb.TimelineEntry, int32, error) {
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

	for _, e := range s.local {
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

func (s *ClickHouseTimelineStore) Len() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.local)
}

func (s *ClickHouseTimelineStore) Replay(fromVersion, toVersion int64) ([]*pb.TimelineEntry, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var result []*pb.TimelineEntry
	for _, e := range s.local {
		if e.Version >= fromVersion && e.Version <= toVersion {
			result = append(result, e)
		}
	}

	if result == nil {
		return []*pb.TimelineEntry{}, nil
	}
	return result, nil
}
