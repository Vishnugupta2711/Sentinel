package sentinel.common

import zio.*
import zio.kafka.producer.*

object KafkaProducer:
  val producerLayer: ZLayer[AppConfig, Throwable, Producer] =
    ZLayer.fromZIO(
      for config <- ZIO.service[AppConfig]
      yield ProducerSettings(List(config.kafkaBroker)),
    ) >>> Producer.live
