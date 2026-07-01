package main

import (
	"log"
	"net"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	port := os.Getenv("CORE_PORT")
	if port == "" {
		port = "9000"
	}

	lis, err := net.Listen("tcp", ":"+port)
	if err != nil {
		log.Fatalf("core: failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	reflection.Register(srv)

	log.Printf("core gRPC server listening on :%s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("core: %v", err)
	}
}
