package kafka

import (
	"context"
	"log"
	"time"

	"github.com/segmentio/kafka-go"
)

type Producer struct {
	writer *kafka.Writer
}

type Message struct {
	Key   []byte
	Value []byte
}

func NewProducer(brokers []string, topic string) *Producer {
	w := &kafka.Writer{
		Addr:         kafka.TCP(brokers...),
		Topic:        topic,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 10 * time.Millisecond,
	}
	return &Producer{writer: w}
}

func (p *Producer) Publish(ctx context.Context, msg Message) error {
	return p.writer.WriteMessages(ctx, kafka.Message{
		Key:   msg.Key,
		Value: msg.Value,
	})
}

func (p *Producer) Close() {
	if err := p.writer.Close(); err != nil {
		log.Printf("kafka producer close: %v", err)
	}
}
