package kafka

import (
	"context"
	"log"

	"github.com/segmentio/kafka-go"
)

type Consumer struct {
	reader *kafka.Reader
}

func NewConsumer(brokers []string, topic, groupID string) *Consumer {
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:     brokers,
		Topic:       topic,
		GroupID:     groupID,
		MinBytes:    10e3,
		MaxBytes:    10e6,
		MaxWait:     1,
		StartOffset: kafka.LastOffset,
	})
	return &Consumer{reader: r}
}

func (c *Consumer) Consume(ctx context.Context, handler func(key, value []byte) error) {
	for {
		m, err := c.reader.ReadMessage(ctx)
		if err != nil {
			log.Printf("kafka read error: %v", err)
			return
		}
		if err := handler(m.Key, m.Value); err != nil {
			log.Printf("kafka handler error: %v", err)
		}
	}
}

func (c *Consumer) Close() {
	if err := c.reader.Close(); err != nil {
		log.Printf("kafka consumer close: %v", err)
	}
}
