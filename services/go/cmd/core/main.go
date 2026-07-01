package main

import (
	"context"
	"log"
	"net"
	"os"
	"time"

	"github.com/sentinel/services/go/internal/infra"
	"github.com/sentinel/services/go/internal/timeline"
	"github.com/sentinel/services/go/internal/worker"
	"github.com/sentinel/services/go/internal/world"
	"github.com/sentinel/services/go/pkg/kafka"
	pbtl "github.com/sentinel/services/go/pkg/proto/timeline"
	pbw "github.com/sentinel/services/go/pkg/proto/world"
	pbwk "github.com/sentinel/services/go/pkg/proto/worker"
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

	workerStore := worker.NewInMemoryStore()
	workerSvc := worker.NewService(workerStore)

	_, err := snapStore.Store(world.SamplePlantState())
	if err != nil {
		log.Fatalf("core: failed to seed initial state: %v", err)
	}
	log.Printf("core: seeded initial world state (v1)")

	if err := workerStore.LoadFromSnapshot(snapStore); err != nil {
		log.Printf("core: warning: failed to load workers from snapshot: %v", err)
	} else {
		log.Printf("core: loaded workers into worker service")
	}

	go hub.Run()
	sim.Start()

	kafkaBroker := os.Getenv("KAFKA_BROKER")
	if kafkaBroker == "" {
		kafkaBroker = "localhost:9092"
	}
	kafkaProd := kafka.NewProducer([]string{kafkaBroker}, "raw-events")
	kafkaPub := world.NewKafkaPublisher(kafkaProd, bus)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go kafkaPub.Run(ctx)

	log.Printf("core: kafka publisher started (broker: %s, topic: raw-events)", kafkaBroker)

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("core: failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	pbw.RegisterWorldServiceServer(srv, worldSvc)
	pbtl.RegisterTimelineServiceServer(srv, tlSvc)
	pbwk.RegisterWorkerServiceServer(srv, workerSvc)
	reflection.Register(srv)

	log.Printf("core gRPC server listening on :%s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("core: %v", err)
	}
}
