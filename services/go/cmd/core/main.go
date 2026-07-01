package main

import (
	"log"
	"net"
	"os"

	"github.com/sentinel/services/go/internal/world"
	pb "github.com/sentinel/services/go/pkg/proto/world"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	port := os.Getenv("CORE_PORT")
	if port == "" {
		port = "9000"
	}

	snapStore := world.NewInMemorySnapshotStore(100)
	diffEngine := world.NewDiffEngine()
	worldSvc := world.NewWorldService(snapStore, diffEngine)

	_, err := snapStore.Store(world.SamplePlantState())
	if err != nil {
		log.Fatalf("core: failed to seed initial state: %v", err)
	}
	log.Printf("core: seeded initial world state (v1)")

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("core: failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	pb.RegisterWorldServiceServer(srv, worldSvc)
	reflection.Register(srv)

	log.Printf("core gRPC server listening on :%s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("core: %v", err)
	}
}
