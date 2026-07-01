package world

import (
	"testing"
	"time"
)

func TestEventBusPublishSubscribe(t *testing.T) {
	bus := NewEventBus()
	sub := bus.Subscribe("test.topic", 10)

	bus.Publish("test.topic", "hello")

	select {
	case event := <-sub.C():
		if event.Topic != "test.topic" {
			t.Errorf("expected topic 'test.topic', got '%s'", event.Topic)
		}
		if event.Payload != "hello" {
			t.Errorf("expected payload 'hello', got '%v'", event.Payload)
		}
	case <-time.After(time.Second):
		t.Fatal("timeout waiting for event")
	}

	sub.Close()
}

func TestEventBusMultipleSubscribers(t *testing.T) {
	bus := NewEventBus()
	sub1 := bus.Subscribe("test.topic", 10)
	sub2 := bus.Subscribe("test.topic", 10)

	bus.Publish("test.topic", "msg")

	select {
	case <-sub1.C():
	case <-time.After(time.Second):
		t.Fatal("sub1 timeout")
	}

	select {
	case <-sub2.C():
	case <-time.After(time.Second):
		t.Fatal("sub2 timeout")
	}

	sub1.Close()
	sub2.Close()
}

func TestEventBusUnsubscribe(t *testing.T) {
	bus := NewEventBus()
	sub := bus.Subscribe("test.topic", 10)
	bus.Unsubscribe("test.topic", sub)

	bus.Publish("test.topic", "should-not-receive")

	select {
	case _, ok := <-sub.C():
		if ok {
			t.Error("should not receive after close")
		}
	case <-time.After(100 * time.Millisecond):
	}
}

func TestEventBusDifferentTopics(t *testing.T) {
	bus := NewEventBus()
	sub := bus.Subscribe("topic.a", 10)

	bus.Publish("topic.b", "data")

	select {
	case <-sub.C():
		t.Error("should not receive on different topic")
	case <-time.After(100 * time.Millisecond):
	}

	sub.Close()
}

func TestSimulatorTick(t *testing.T) {
	bus := NewEventBus()
	store := NewInMemorySnapshotStore(100)
	engine := NewDiffEngine()

	state := SamplePlantState()
	store.Store(state)

	initialTemp := state.Weather.Temperature
	initialSensor := state.Sensors[0].CurrentValue
	initialWorkerX := state.Workers[0].X

	sim := NewSimulator(store, engine, bus, 50*time.Millisecond)
	sim.Start()
	defer sim.Stop()

	time.Sleep(120 * time.Millisecond)

	latest, err := store.Latest()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if latest.Version <= 1 {
		t.Error("expected simulator to produce new snapshots")
	}

	if latest.Weather.Temperature == initialTemp &&
		latest.Sensors[0].CurrentValue == initialSensor &&
		latest.Workers[0].X == initialWorkerX {
		t.Error("expected simulator to mutate state")
	}
}

func TestHubBroadcastsDiff(t *testing.T) {
	bus := NewEventBus()
	hub := NewHub(bus)
	go hub.Run()

	client := &Client{
		ID:     "test-client",
		SendCh: make(chan []byte, 10),
	}
	hub.Register(client)
	defer hub.Unregister("test-client")

	diff := WorldDiff{Version: 1, HasChanges: true}
	bus.Publish("world.diff", diff)

	select {
	case msg := <-client.SendCh:
		if len(msg) == 0 {
			t.Error("expected non-empty message")
		}
	case <-time.After(time.Second):
		t.Fatal("timeout waiting for broadcast")
	}

	if hub.ClientCount() != 1 {
		t.Errorf("expected 1 client, got %d", hub.ClientCount())
	}
}

func TestHubClientCount(t *testing.T) {
	bus := NewEventBus()
	hub := NewHub(bus)

	c1 := &Client{ID: "c1", SendCh: make(chan []byte, 10)}
	c2 := &Client{ID: "c2", SendCh: make(chan []byte, 10)}

	hub.Register(c1)
	hub.Register(c2)

	if hub.ClientCount() != 2 {
		t.Errorf("expected 2 clients, got %d", hub.ClientCount())
	}

	hub.Unregister("c1")

	if hub.ClientCount() != 1 {
		t.Errorf("expected 1 client, got %d", hub.ClientCount())
	}
}
