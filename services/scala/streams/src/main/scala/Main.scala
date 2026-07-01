package sentinel.streams

import zio.*
import zio.kafka.consumer.*
import zio.kafka.producer.*
import zio.kafka.serde.*
import sentinel.common.*

import java.time.Instant
import io.circe.*
import io.circe.parser.*
import io.circe.syntax.*

case class EnrichedEvent(
  version: Int,
  source: String,
  receivedAt: String,
  valid: Boolean,
  payload: Json,
)

object EnrichedEvent:
  given encoder: Encoder[EnrichedEvent] = Encoder.forProduct5(
    "version", "source", "received_at", "valid", "payload",
  )(e => (e.version, e.source, e.receivedAt, e.valid, e.payload))

object Main extends ZIOAppDefault:

  private val rawTopic       = "raw-events"
  private val enrichedTopic  = "enriched-events"

  def run: Task[ExitCode] =
    val program = for
      config   <- ZIO.service[AppConfig]
      _        <- Console.printLine(s"sentinel-streams starting — broker: ${config.kafkaBroker}")
      settings  = ConsumerSettings(List(config.kafkaBroker))
                    .withGroupId(s"${config.groupId}-streams")
                    .withMaxPollRecords(100)
      producer <- ZIO.service[Producer]
      _        <- Consumer
                   .consumeWith(
                     settings,
                     Subscription.topics(rawTopic),
                     Serde.byteArray,
                     Serde.byteArray,
                   ) { record =>
                     val raw     = record.value
                     val json    = parse(new String(raw, java.nio.charset.StandardCharsets.UTF_8))
                     val valid   = json.isRight
                     val now     = Instant.now().toString
                     val version = json.map(_.hcursor.get[Int]("version")).getOrElse(Right(0)).getOrElse(0)

                     val enriched = EnrichedEvent(
                       version   = version,
                       source    = "world-sim",
                       receivedAt = now,
                       valid     = valid,
                       payload   = json.getOrElse(Json.Null),
                     )

                     producer
                       .produce(
                         enrichedTopic,
                         enriched.version.toString.getBytes(java.nio.charset.StandardCharsets.UTF_8),
                         enriched.asJson.noSpaces.getBytes(java.nio.charset.StandardCharsets.UTF_8),
                         Serde.byteArray,
                         Serde.byteArray,
                       )
                       .ignore
                   }
    yield ExitCode.success

    program.catchAll { e =>
      Console.printLineError(s"streams failed: ${e.getMessage}") *>
      ZIO.succeed(ExitCode.failure)
    }.provide(AppConfig.layer, KafkaProducer.producerLayer)
