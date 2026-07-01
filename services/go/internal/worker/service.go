package worker

import (
	"context"
	"time"

	"github.com/sentinel/services/go/internal/world"
	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/worker"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Service struct {
	pb.UnimplementedWorkerServiceServer
	store Store
}

func NewService(store Store) *Service {
	return &Service{store: store}
}

func (s *Service) CreateWorker(ctx context.Context, req *pb.CreateWorkerRequest) (*pb.CreateWorkerResponse, error) {
	now := time.Now().UTC()
	worker := world.Worker{
		PhysicalObject: world.PhysicalObject{
			BaseObject: world.BaseObject{
				Name:      req.Name,
				CreatedAt: now,
				UpdatedAt: now,
			},
			X:      req.X,
			Y:      req.Y,
			Z:      req.Z,
			ZoneID: req.ZoneId,
		},
		Role:        world.WorkerRole(req.Role),
		Department:  req.Department,
		Shift:       req.Shift,
		CurrentPPE:  req.CurrentPpe,
		WorkerStatus: world.WorkerStatusActive,
	}

	created, err := s.store.Create(worker)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to create worker: %v", err)
	}

	return &pb.CreateWorkerResponse{
		Worker: toProtoWorker(created),
	}, nil
}

func (s *Service) GetWorker(ctx context.Context, req *pb.GetWorkerRequest) (*pb.GetWorkerResponse, error) {
	worker, err := s.store.Get(req.Id)
	if err != nil {
		return nil, status.Errorf(codes.NotFound, "worker not found: %v", err)
	}
	return &pb.GetWorkerResponse{
		Worker: toProtoWorker(worker),
	}, nil
}

func (s *Service) UpdateWorker(ctx context.Context, req *pb.UpdateWorkerRequest) (*pb.UpdateWorkerResponse, error) {
	existing, err := s.store.Get(req.Id)
	if err != nil {
		return nil, status.Errorf(codes.NotFound, "worker not found: %v", err)
	}

	updated := *existing
	updated.UpdatedAt = time.Now().UTC()

	if req.Name != "" {
		updated.Name = req.Name
	}
	if req.Role != "" {
		updated.Role = world.WorkerRole(req.Role)
	}
	if req.Status != "" {
		updated.WorkerStatus = world.WorkerStatus(req.Status)
	}
	if req.Department != "" {
		updated.Department = req.Department
	}
	if req.Shift != "" {
		updated.Shift = req.Shift
	}
	if req.ZoneId != "" {
		updated.ZoneID = req.ZoneId
	}
	if req.X != 0 || req.Y != 0 || req.Z != 0 {
		updated.X = req.X
		updated.Y = req.Y
		updated.Z = req.Z
	}
	if req.CurrentPpe != nil {
		updated.CurrentPPE = req.CurrentPpe
	}

	result, err := s.store.Update(updated)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update worker: %v", err)
	}

	return &pb.UpdateWorkerResponse{
		Worker: toProtoWorker(result),
	}, nil
}

func (s *Service) DeleteWorker(ctx context.Context, req *pb.DeleteWorkerRequest) (*pb.DeleteWorkerResponse, error) {
	if err := s.store.Delete(req.Id); err != nil {
		return nil, status.Errorf(codes.NotFound, "worker not found: %v", err)
	}
	return &pb.DeleteWorkerResponse{}, nil
}

func (s *Service) ListWorkers(ctx context.Context, req *pb.ListWorkersRequest) (*pb.ListWorkersResponse, error) {
	all, err := s.store.List()
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to list workers: %v", err)
	}

	var filtered []world.Worker
	for _, w := range all {
		if req.Role != "" && string(w.Role) != req.Role {
			continue
		}
		if req.Status != "" && string(w.WorkerStatus) != req.Status {
			continue
		}
		if req.ZoneId != "" && w.ZoneID != req.ZoneId {
			continue
		}
		filtered = append(filtered, w)
	}

	page := int(req.Page)
	pageSize := int(req.PageSize)
	if page <= 0 {
		page = 1
	}
	if pageSize <= 0 {
		pageSize = 20
	}

	start := (page - 1) * pageSize
	if start >= len(filtered) {
		return &pb.ListWorkersResponse{
			Workers: nil,
			Total:   int32(len(filtered)),
			Page:    int32(page),
		}, nil
	}

	end := start + pageSize
	if end > len(filtered) {
		end = len(filtered)
	}

	protoWorkers := make([]*pb.Worker, end-start)
	for i, w := range filtered[start:end] {
		protoWorkers[i] = toProtoWorker(&w)
	}

	return &pb.ListWorkersResponse{
		Workers: protoWorkers,
		Total:   int32(len(filtered)),
		Page:    int32(page),
	}, nil
}

func (s *Service) StreamWorkerUpdates(req *pb.StreamWorkerUpdatesRequest, stream pb.WorkerService_StreamWorkerUpdatesServer) error {
	interval := time.Duration(req.IntervalMs) * time.Millisecond
	if interval <= 0 {
		interval = 1000 * time.Millisecond
	}

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-stream.Context().Done():
			return stream.Context().Err()
		case <-ticker.C:
			workers, err := s.store.List()
			if err != nil {
				continue
			}
			for _, w := range workers {
				if err := stream.Send(&pb.WorkerUpdate{
					Worker:     toProtoWorker(&w),
					UpdateType: "tick",
				}); err != nil {
					return err
				}
			}
		}
	}
}

func toProtoWorker(w *world.Worker) *pb.Worker {
	return &pb.Worker{
		Id:         w.ID,
		Name:       w.Name,
		Role:       string(w.Role),
		Status:     string(w.WorkerStatus),
		Department: w.Department,
		ZoneId:     w.ZoneID,
		Shift:      w.Shift,
		X:          w.X,
		Y:          w.Y,
		Z:          w.Z,
		CurrentPpe: w.CurrentPPE,
		CreatedAt: &common.Timestamp{
			Seconds: w.CreatedAt.Unix(),
			Nanos:   int32(w.CreatedAt.Nanosecond()),
		},
		UpdatedAt: &common.Timestamp{
			Seconds: w.UpdatedAt.Unix(),
			Nanos:   int32(w.UpdatedAt.Nanosecond()),
		},
	}
}
