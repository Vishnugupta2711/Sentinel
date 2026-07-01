package main

import (
	"log"
	"net"
	"os"
	"time"

	"github.com/sentinel/services/go/internal/infra"
	"github.com/sentinel/services/go/internal/timeline"
	"github.com/sentinel/services/go/internal/world"
	pbtl "github.com/sentinel/services/go/pkg/proto/timeline"
	pbw "github.com/sentinel/services/go/pkg/proto/world"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	port := os.Getenv("CORE_PORT")
	if port == "" {
		port = "9000"
	}

	redisURL := os.Getenv("REDIS_URL")
	chURL := os.Getenv("CLICKHOUSE_URL")

	bus := world.NewEventBus()
	diffEngine := world.NewDiffEngine()

	snapStore := infra.NewRedisSnapshotStore(redisURL, 100)
	tlStore := infra.NewClickHouseTimelineStore(chURL, 1000)

	worldSvc := world.NewWorldService(snapStore, diffEngine)
	tlSvc := timeline.NewService(tlStore)
	hub := world.NewHub(bus)
	sim := world.NewSimulator(snapStore, diffEngine, bus, 1*time.Second)

	_, err := snapStore.Store(world.SamplePlantState())
	if err != nil {
		log.Fatalf("core: failed to seed initial state: %v", err)
	}
	log.Printf("core: seeded initial world state (v1)")

	go hub.Run()
	sim.Start()

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("core: failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	pbw.RegisterWorldServiceServer(srv, worldSvc)
	pbtl.RegisterTimelineServiceServer(srv, tlSvc)
	reflection.Register(srv)

	log.Printf("core gRPC server listening on :%s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("core: %v", err)
	}
}
