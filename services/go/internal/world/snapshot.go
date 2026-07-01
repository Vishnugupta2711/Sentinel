package world

import (
	"fmt"
	"sync"
	"time"
)

type SnapshotStore interface {
	Store(state PlantState) (int64, error)
	Get(version int64) (*PlantState, error)
	Latest() (*PlantState, error)
	List(limit int) ([]PlantState, error)
	Len() int
}

type InMemorySnapshotStore struct {
	mu       sync.RWMutex
	version  int64
	snapshots map[int64]PlantState
	ordered  []int64
	maxSnap  int
}

func NewInMemorySnapshotStore(maxSnapshots int) *InMemorySnapshotStore {
	return &InMemorySnapshotStore{
		snapshots: make(map[int64]PlantState),
		ordered:   make([]int64, 0, maxSnapshots),
		maxSnap:   maxSnapshots,
	}
}

func (s *InMemorySnapshotStore) Store(state PlantState) (int64, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.version++
	v := s.version
	state.Version = int(v)
	state.Timestamp = time.Now().UTC()

	s.snapshots[v] = state
	s.ordered = append(s.ordered, v)

	if len(s.ordered) > s.maxSnap {
		old := s.ordered[0]
		s.ordered = s.ordered[1:]
		delete(s.snapshots, old)
	}

	return v, nil
}

func (s *InMemorySnapshotStore) Get(version int64) (*PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	state, ok := s.snapshots[version]
	if !ok {
		return nil, fmt.Errorf("snapshot %d not found", version)
	}
	return &state, nil
}

func (s *InMemorySnapshotStore) Latest() (*PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if len(s.ordered) == 0 {
		return nil, fmt.Errorf("no snapshots available")
	}
	v := s.ordered[len(s.ordered)-1]
	state := s.snapshots[v]
	return &state, nil
}

func (s *InMemorySnapshotStore) List(limit int) ([]PlantState, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	if limit <= 0 || limit > len(s.ordered) {
		limit = len(s.ordered)
	}

	start := len(s.ordered) - limit
	result := make([]PlantState, limit)
	for i, v := range s.ordered[start:] {
		result[i] = s.snapshots[v]
	}
	return result, nil
}

func (s *InMemorySnapshotStore) Len() int {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return len(s.snapshots)
}
