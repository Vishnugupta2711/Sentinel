package worker

import (
	"fmt"
	"sync"

	"github.com/sentinel/services/go/internal/world"
)

type Store interface {
	List() ([]world.Worker, error)
	Get(id string) (*world.Worker, error)
	Create(worker world.Worker) (*world.Worker, error)
	Update(worker world.Worker) (*world.Worker, error)
	Delete(id string) error
}

type InMemoryStore struct {
	mu      sync.RWMutex
	workers map[string]world.Worker
	ids     []string
}

func NewInMemoryStore() *InMemoryStore {
	return &InMemoryStore{
		workers: make(map[string]world.Worker),
	}
}

func (s *InMemoryStore) LoadFromSnapshot(snapStore world.SnapshotStore) error {
	state, err := snapStore.Latest()
	if err != nil {
		return fmt.Errorf("worker store: failed to load from snapshot: %w", err)
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, w := range state.Workers {
		s.workers[w.ID] = w
		s.ids = append(s.ids, w.ID)
	}
	return nil
}

func (s *InMemoryStore) List() ([]world.Worker, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	result := make([]world.Worker, 0, len(s.ids))
	for _, id := range s.ids {
		result = append(result, s.workers[id])
	}
	return result, nil
}

func (s *InMemoryStore) Get(id string) (*world.Worker, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	w, ok := s.workers[id]
	if !ok {
		return nil, fmt.Errorf("worker %q not found", id)
	}
	return &w, nil
}

func (s *InMemoryStore) Create(worker world.Worker) (*world.Worker, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	worker.ID = world.GenerateID()
	s.workers[worker.ID] = worker
	s.ids = append(s.ids, worker.ID)
	copy := worker
	return &copy, nil
}

func (s *InMemoryStore) Update(worker world.Worker) (*world.Worker, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	id := worker.ID
	if _, ok := s.workers[id]; !ok {
		return nil, fmt.Errorf("worker %q not found", id)
	}
	s.workers[id] = worker
	copy := worker
	return &copy, nil
}

func (s *InMemoryStore) Delete(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.workers[id]; !ok {
		return fmt.Errorf("worker %q not found", id)
	}
	delete(s.workers, id)
	for i, wid := range s.ids {
		if wid == id {
			s.ids = append(s.ids[:i], s.ids[i+1:]...)
			break
		}
	}
	return nil
}
