package world

import (
	"context"
	"encoding/json"
	"log"

	"github.com/sentinel/services/go/pkg/kafka"
)

type KafkaPublisher struct {
	producer *kafka.Producer
	bus      *EventBus
	sub      *Subscription
}

func NewKafkaPublisher(producer *kafka.Producer, bus *EventBus) *KafkaPublisher {
	return &KafkaPublisher{
		producer: producer,
		bus:      bus,
		sub:      bus.Subscribe("world.diff", 64),
	}
}

func (p *KafkaPublisher) Run(ctx context.Context) {
	for event := range p.sub.C() {
		diff, ok := event.Payload.(WorldDiff)
		if !ok {
			log.Printf("kafka: unexpected payload type %T", event.Payload)
			continue
		}

		data, err := json.Marshal(diff)
		if err != nil {
			log.Printf("kafka: marshal error: %v", err)
			continue
		}

		if err := p.producer.Publish(ctx, kafka.Message{
			Key:   []byte("world.diff"),
			Value: data,
		}); err != nil {
			log.Printf("kafka: publish error: %v", err)
		}
	}
}

func (p *KafkaPublisher) Close() {
	p.sub.Close()
	p.producer.Close()
}
