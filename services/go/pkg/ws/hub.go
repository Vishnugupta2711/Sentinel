package ws

import (
	"log"
	"net/http"
	"sync"

	"golang.org/x/net/websocket"
)

type Client struct {
	conn *websocket.Conn
	send chan []byte
}

type Hub struct {
	mu      sync.RWMutex
	clients map[*Client]bool
}

func NewHub() *Hub {
	return &Hub{
		clients: make(map[*Client]bool),
	}
}

func (h *Hub) Register(conn *websocket.Conn) *Client {
	c := &Client{conn: conn, send: make(chan []byte, 256)}
	h.mu.Lock()
	h.clients[c] = true
	h.mu.Unlock()
	return c
}

func (h *Hub) Unregister(c *Client) {
	h.mu.Lock()
	delete(h.clients, c)
	h.mu.Unlock()
	close(c.send)
}

func (h *Hub) Broadcast(msg []byte) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	for c := range h.clients {
		select {
		case c.send <- msg:
		default:
			log.Printf("ws: client send buffer full, dropping message")
		}
	}
}

func (h *Hub) ServeWS(w http.ResponseWriter, r *http.Request) {
	websocket.Server{
		Handler: func(conn *websocket.Conn) {
			c := h.Register(conn)
			defer h.Unregister(c)
			go h.writePump(c)
			h.readPump(c)
		},
	}.ServeHTTP(w, r)
}

func (h *Hub) writePump(c *Client) {
	for msg := range c.send {
		if err := websocket.Message.Send(c.conn, string(msg)); err != nil {
			log.Printf("ws: write error: %v", err)
			return
		}
	}
}

func (h *Hub) readPump(c *Client) {
	for {
		var msg string
		if err := websocket.Message.Receive(c.conn, &msg); err != nil {
			break
		}
	}
}
