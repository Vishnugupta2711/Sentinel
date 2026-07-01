package worker

import (
	"context"
	"testing"
	"time"

	"github.com/sentinel/services/go/internal/world"
	pb "github.com/sentinel/services/go/pkg/proto/worker"
)

func TestInMemoryStore(t *testing.T) {
	store := NewInMemoryStore()

	w := world.Worker{
		PhysicalObject: world.PhysicalObject{
			BaseObject: world.BaseObject{
				Name:      "Test Worker",
				CreatedAt: time.Now().UTC(),
				UpdatedAt: time.Now().UTC(),
			},
			X: 10, Y: 20, Z: 0,
			ZoneID: "zone-1",
		},
		Role:        world.WorkerRoleOperator,
		Department:  "Test",
		Shift:       "DAY",
		CurrentPPE:  []string{"HELMET", "VEST"},
		WorkerStatus: world.WorkerStatusActive,
	}

	created, err := store.Create(w)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if created.ID == "" {
		t.Error("expected non-empty ID")
	}
	if created.Name != "Test Worker" {
		t.Errorf("expected 'Test Worker', got '%s'", created.Name)
	}

	got, err := store.Get(created.ID)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Name != "Test Worker" {
		t.Errorf("expected 'Test Worker', got '%s'", got.Name)
	}

	got.Role = world.WorkerRoleSupervisor
	updated, err := store.Update(*got)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if string(updated.Role) != "SUPERVISOR" {
		t.Errorf("expected SUPERVISOR, got '%s'", updated.Role)
	}

	if err := store.Delete(created.ID); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	_, err = store.Get(created.ID)
	if err == nil {
		t.Error("expected error after delete")
	}
}

func TestListWorkers(t *testing.T) {
	store := NewInMemoryStore()

	for i := 0; i < 5; i++ {
		w := world.Worker{
			PhysicalObject: world.PhysicalObject{
				BaseObject: world.BaseObject{
					Name:      "Worker " + string(rune('A'+i)),
					CreatedAt: time.Now().UTC(),
					UpdatedAt: time.Now().UTC(),
				},
			},
			Role:        world.WorkerRoleOperator,
			Department:  "Test",
			Shift:       "DAY",
			WorkerStatus: world.WorkerStatusActive,
		}
		store.Create(w)
	}

	workers, err := store.List()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(workers) != 5 {
		t.Errorf("expected 5 workers, got %d", len(workers))
	}
}

func TestWorkerService(t *testing.T) {
	store := NewInMemoryStore()
	svc := NewService(store)

	created, err := svc.CreateWorker(context.Background(), &pb.CreateWorkerRequest{
		Name:       "Alice",
		Role:       "OPERATOR",
		Department: "Operations",
		Shift:      "DAY",
		CurrentPpe: []string{"HELMET"},
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if created.Worker.Name != "Alice" {
		t.Errorf("expected 'Alice', got '%s'", created.Worker.Name)
	}
	if created.Worker.Status != "ACTIVE" {
		t.Errorf("expected ACTIVE status, got '%s'", created.Worker.Status)
	}

	got, err := svc.GetWorker(context.Background(), &pb.GetWorkerRequest{Id: created.Worker.Id})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Worker.Name != "Alice" {
		t.Errorf("expected 'Alice', got '%s'", got.Worker.Name)
	}

	updated, err := svc.UpdateWorker(context.Background(), &pb.UpdateWorkerRequest{
		Id:     created.Worker.Id,
		Name:   "Alice B.",
		Status: "ON_BREAK",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if updated.Worker.Name != "Alice B." {
		t.Errorf("expected 'Alice B.', got '%s'", updated.Worker.Name)
	}
	if updated.Worker.Status != "ON_BREAK" {
		t.Errorf("expected ON_BREAK, got '%s'", updated.Worker.Status)
	}

	listResp, err := svc.ListWorkers(context.Background(), &pb.ListWorkersRequest{})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(listResp.Workers) != 1 {
		t.Errorf("expected 1 worker, got %d", len(listResp.Workers))
	}

	_, err = svc.DeleteWorker(context.Background(), &pb.DeleteWorkerRequest{Id: created.Worker.Id})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	_, err = svc.GetWorker(context.Background(), &pb.GetWorkerRequest{Id: created.Worker.Id})
	if err == nil {
		t.Error("expected error after delete")
	}
}
