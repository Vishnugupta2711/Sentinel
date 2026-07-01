package world

import (
	"sync"
)

type Event struct {
	Topic   string
	Payload any
}

type Subscription struct {
	ch     chan Event
	once   sync.Once
}

func (s *Subscription) C() <-chan Event {
	return s.ch
}

func (s *Subscription) Close() {
	s.once.Do(func() {
		close(s.ch)
	})
}

type EventBus struct {
	mu   sync.RWMutex
	subs map[string][]*Subscription
}

func NewEventBus() *EventBus {
	return &EventBus{
		subs: make(map[string][]*Subscription),
	}
}

func (b *EventBus) Publish(topic string, payload any) {
	b.mu.RLock()
	subs := b.subs[topic]
	b.mu.RUnlock()

	evt := Event{Topic: topic, Payload: payload}
	for _, sub := range subs {
		select {
		case sub.ch <- evt:
		default:
		}
	}
}

func (b *EventBus) Subscribe(topic string, buffer int) *Subscription {
	sub := &Subscription{
		ch: make(chan Event, buffer),
	}

	b.mu.Lock()
	b.subs[topic] = append(b.subs[topic], sub)
	b.mu.Unlock()

	return sub
}

func (b *EventBus) Unsubscribe(topic string, sub *Subscription) {
	b.mu.Lock()
	defer b.mu.Unlock()

	subs := b.subs[topic]
	for i, s := range subs {
		if s == sub {
			b.subs[topic] = append(subs[:i], subs[i+1:]...)
			break
		}
	}
	sub.Close()
}
