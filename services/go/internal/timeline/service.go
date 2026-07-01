package timeline

import (
	"context"
	"time"

	pb "github.com/sentinel/services/go/pkg/proto/timeline"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type Service struct {
	pb.UnimplementedTimelineServiceServer
	store Store
}

func NewService(store Store) *Service {
	return &Service{store: store}
}

func (s *Service) Record(ctx context.Context, req *pb.RecordRequest) (*pb.RecordResponse, error) {
	if req.Entry == nil {
		return nil, status.Error(codes.InvalidArgument, "entry is required")
	}

	if err := s.store.Record(req.Entry); err != nil {
		return nil, status.Errorf(codes.Internal, "failed to record: %v", err)
	}

	return &pb.RecordResponse{Recorded: true}, nil
}

func (s *Service) Query(ctx context.Context, req *pb.TimelineQuery) (*pb.TimelineResult, error) {
	entries, total, err := s.store.Query(req)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "query failed: %v", err)
	}

	return &pb.TimelineResult{
		Entries: entries,
		Total:   total,
	}, nil
}

func (s *Service) Replay(req *pb.ReplayRequest, stream pb.TimelineService_ReplayServer) error {
	entries, err := s.store.Replay(req.FromVersion, req.ToVersion)
	if err != nil {
		return status.Errorf(codes.Internal, "replay failed: %v", err)
	}

	interval := time.Duration(req.IntervalMs) * time.Millisecond
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for _, entry := range entries {
		select {
		case <-stream.Context().Done():
			return stream.Context().Err()
		case <-ticker.C:
			if err := stream.Send(&pb.ReplayResponse{Entry: entry}); err != nil {
				return err
			}
		}
	}

	return nil
}
