package world

import (
	"context"
	"time"

	"github.com/sentinel/services/go/pkg/proto/common"
	pb "github.com/sentinel/services/go/pkg/proto/world"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type WorldService struct {
	pb.UnimplementedWorldServiceServer
	store       SnapshotStore
	diffEngine  *DiffEngine
}

func NewWorldService(store SnapshotStore, diffEngine *DiffEngine) *WorldService {
	return &WorldService{
		store:      store,
		diffEngine: diffEngine,
	}
}

func (s *WorldService) GetSnapshot(ctx context.Context, req *pb.GetSnapshotRequest) (*pb.GetSnapshotResponse, error) {
	var state *PlantState
	var err error

	if req.Version == 0 {
		state, err = s.store.Latest()
	} else {
		state, err = s.store.Get(req.Version)
	}

	if err != nil {
		return nil, status.Errorf(codes.NotFound, "snapshot not found: %v", err)
	}

	return &pb.GetSnapshotResponse{
		Snapshot: toProtoSnapshot(state),
	}, nil
}

func (s *WorldService) StreamSnapshots(req *pb.StreamSnapshotsRequest, stream pb.WorldService_StreamSnapshotsServer) error {
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
			state, err := s.store.Latest()
			if err != nil {
				continue
			}
			if err := stream.Send(&pb.StreamSnapshotsResponse{
				Snapshot: toProtoSnapshot(state),
			}); err != nil {
				return err
			}
		}
	}
}

func (s *WorldService) ListSnapshots(ctx context.Context, req *pb.ListSnapshotsRequest) (*pb.ListSnapshotsResponse, error) {
	limit := int(req.Limit)
	if limit <= 0 {
		limit = 10
	}
	if limit > 100 {
		limit = 100
	}

	snapshots, err := s.store.List(limit)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to list snapshots: %v", err)
	}

	protoSnapshots := make([]*pb.WorldSnapshot, len(snapshots))
	for i, snap := range snapshots {
		protoSnapshots[i] = toProtoSnapshot(&snap)
	}

	return &pb.ListSnapshotsResponse{
		Snapshots: protoSnapshots,
		Total:     int32(s.store.Len()),
	}, nil
}

func toProtoSnapshot(state *PlantState) *pb.WorldSnapshot {
	return &pb.WorldSnapshot{
		Version:   int64(state.Version),
		Timestamp: toProtoTimestamp(state.Timestamp),
		Plant:     toProtoPlant(&state.Plant),
		Weather:   toProtoWeather(&state.Weather),
	}
}

func toProtoTimestamp(t time.Time) *common.Timestamp {
	return &common.Timestamp{
		Seconds: t.Unix(),
		Nanos:   int32(t.Nanosecond()),
	}
}

func toProtoPlant(p *Plant) *pb.Plant {
	return &pb.Plant{
		Id:        p.ID,
		Name:      p.Name,
		Status:    string(p.Status),
		UpdatedAt: toProtoTimestamp(p.UpdatedAt),
	}
}

func toProtoWeather(w *WeatherState) *pb.WeatherState {
	return &pb.WeatherState{
		Temperature: w.Temperature,
		WindSpeed:   w.WindSpeed,
		Humidity:    w.Humidity,
	}
}
