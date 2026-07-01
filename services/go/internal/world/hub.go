package world

import (
	"encoding/json"
	"log"
	"sync"
)

type Client struct {
	ID     string
	SendCh chan []byte
}

type Hub struct {
	mu       sync.RWMutex
	clients  map[string]*Client
	bus      *EventBus
	sub      *Subscription
}

func NewHub(bus *EventBus) *Hub {
	h := &Hub{
		clients: make(map[string]*Client),
		bus:     bus,
	}
	h.sub = bus.Subscribe("world.diff", 64)
	return h
}

func (h *Hub) Register(client *Client) {
	h.mu.Lock()
	h.clients[client.ID] = client
	h.mu.Unlock()
	log.Printf("hub: client %s connected (%d total)", client.ID, len(h.clients))
}

func (h *Hub) Unregister(clientID string) {
	h.mu.Lock()
	delete(h.clients, clientID)
	h.mu.Unlock()
	log.Printf("hub: client %s disconnected (%d remaining)", clientID, len(h.clients))
}

func (h *Hub) Broadcast(data []byte) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	for _, client := range h.clients {
		select {
		case client.SendCh <- data:
		default:
		}
	}
}

func (h *Hub) Run() {
	for event := range h.sub.C() {
		data, err := json.Marshal(event.Payload)
		if err != nil {
			log.Printf("hub: marshal error: %v", err)
			continue
		}
		h.Broadcast(data)
	}
}

func (h *Hub) ClientCount() int {
	h.mu.RLock()
	defer h.mu.RUnlock()
	return len(h.clients)
}
