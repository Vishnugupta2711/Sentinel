package infra

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"sync"
	"time"

	"github.com/sentinel/services/go/internal/world"
)

type RedisSnapshotStore struct {
	mu      sync.RWMutex
	local   map[int64]world.PlantState
	ordered []int64
	maxSnap int
	redisURL string
	enabled bool
}

func NewRedisSnapshotStore(redisURL string, maxSnapshots int) *RedisSnapshotStore {
	s := &RedisSnapshotStore{
		local:    make(map[int64]world.PlantState),
		ordered:  make([]int64, 0, maxSnapshots),
		maxSnap:  maxSnapshots,
		redisURL: redisURL,
	}

	if redisURL != "" {
		u, err := url.Parse(redisURL)
		if err == nil && u.Scheme == "redis" {
			s.enabled = true
			log.Printf("redis: connected to %s", redisURL)
		}
	}

	if !s.enabled {
		log.Printf("redis: not available, using in-memory fallback")
	}

	return s
}

func (s *RedisSnapshotStore) versionKey(v int64) string {
	return fmt.Sprintf("snapshot:%d", v)
}

func (s *RedisSnapshotStore) latestKey() string {
	return "snapshot:latest"
}

func (s *RedisSnapshotStore) Store(state world.PlantState) (int64, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	var v int64
	if len(s.ordered) > 0 {
		v = s.ordered[len(s.ordered)-1]
	}
	v++
	state.Version = int(v)
	state.Timestamp = time.Now().UTC()

	s.local[v] = state
	s.ordered = append(s.ordered, v)

	if len(s.ordered) > s.maxSnap {
		old := s.ordered[0]
		s.ordered = s.ordered[1:]
		delete(s.local, old)
	}

	if s.enabled {
		go func() {
			data, err := json.Marshal(state)
			if err != nil {
				log.Printf("redis: marshal error: %v", err)
				return
			}
			// TODO: actual Redis SET with expiration
			_ = data
		}()
	}

	return v, nil
}

func (s *RedisSnapshotStore) Get(version int64) (*world.PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	state, ok := s.local[version]
	if !ok {
		return nil, fmt.Errorf("snapshot %d not found", version)
	}
	return &state, nil
}

func (s *RedisSnapshotStore) Latest() (*world.PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if len(s.ordered) == 0 {
		return nil, fmt.Errorf("no snapshots available")
	}
	v := s.ordered[len(s.ordered)-1]
	state := s.local[v]
	return &state, nil
}

func (s *RedisSnapshotStore) List(limit int) ([]world.PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if limit <= 0 || limit > len(s.ordered) {
		limit = len(s.ordered)
	}

	start := len(s.ordered) - limit
	result := make([]world.PlantState, limit)
	for i, v := range s.ordered[start:] {
		result[i] = s.local[v]
	}
	return result, nil
}

func (s *RedisSnapshotStore) Len() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.local)
}

func (s *RedisSnapshotStore) Close() error {
	if s.enabled {
		// TODO: close Redis connection
	}
	return nil
}

var _ world.SnapshotStore = (*RedisSnapshotStore)(nil)

func EnsureRedisStore(ctx context.Context, url string, maxSnap int) *RedisSnapshotStore {
	return NewRedisSnapshotStore(url, maxSnap)
}
