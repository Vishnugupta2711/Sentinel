package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	pb "github.com/sentinel/services/go/pkg/proto/world"
	pbwk "github.com/sentinel/services/go/pkg/proto/worker"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"nhooyr.io/websocket"
)

var coreClient pb.WorldServiceClient
var workerClient pbwk.WorkerServiceClient

func initCoreClient(coreAddr string) {
	if coreAddr == "" {
		coreAddr = "core:9000"
	}

	conn, err := grpc.NewClient(coreAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Printf("gateway: gRPC to core not available (%v), WS world-state will be degraded", err)
		return
	}

	coreClient = pb.NewWorldServiceClient(conn)
	workerClient = pbwk.NewWorkerServiceClient(conn)
	log.Printf("gateway: connected to core gRPC at %s", coreAddr)
}

func worldStateHandler(w http.ResponseWriter, r *http.Request) {
	c, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		InsecureSkipVerify: true,
	})
	if err != nil {
		log.Printf("gateway: WS accept error: %v", err)
		return
	}
	defer c.Close(websocket.StatusNormalClosure, "done")

	log.Printf("gateway: WS world-state client connected from %s", r.RemoteAddr)

	ctx := c.CloseRead(r.Context())

	if coreClient == nil {
		sendJSON(ctx, c, map[string]string{"error": "core not available"})
		return
	}

	stream, err := coreClient.StreamSnapshots(ctx, &pb.StreamSnapshotsRequest{
		IntervalMs: 1000,
	})
	if err != nil {
		log.Printf("gateway: gRPC stream error: %v", err)
		sendJSON(ctx, c, map[string]string{"error": "stream unavailable"})
		return
	}

	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			if err := c.Ping(ctx); err != nil {
				log.Printf("gateway: WS ping error: %v", err)
				return
			}
		default:
			snap, err := stream.Recv()
			if err != nil {
				log.Printf("gateway: gRPC recv error: %v", err)
				return
			}

			data, err := json.Marshal(snap.Snapshot)
			if err != nil {
				log.Printf("gateway: marshal error: %v", err)
				continue
			}

			if err := c.Write(ctx, websocket.MessageText, data); err != nil {
				log.Printf("gateway: WS write error: %v", err)
				return
			}
		}
	}
}

func sendJSON(ctx context.Context, c *websocket.Conn, v any) {
	data, err := json.Marshal(v)
	if err != nil {
		return
	}
	c.Write(ctx, websocket.MessageText, data)
}
