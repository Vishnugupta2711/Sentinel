package sentinel.cep

import zio.*
import zio.kafka.consumer.*
import zio.kafka.producer.*
import zio.kafka.serde.*
import sentinel.common.*

import java.time.Instant
import java.util.UUID
import io.circe.*
import io.circe.parser.*
import io.circe.syntax.*

case class Alert(
  id: String,
  ruleName: String,
  severity: String,
  message: String,
  eventVersion: Int,
  source: String,
  createdAt: String,
  details: Json,
)

object Alert:
  given encoder: Encoder[Alert] = Encoder.forProduct8(
    "id", "rule_name", "severity", "message",
    "event_version", "source", "created_at", "details",
  )(a => (a.id, a.ruleName, a.severity, a.message, a.eventVersion, a.source, a.createdAt, a.details))

sealed trait CepRule:
  def name: String
  def severity: String
  def evaluate(payload: Json, source: String, version: Int): Option[Alert]

object CepRules:

  val all: List[CepRule] = List(
    MissingVersionRule,
    UnknownSourceRule,
    NullPayloadRule,
  )

  object MissingVersionRule extends CepRule:
    val name     = "missing_version"
    val severity = "WARNING"

    def evaluate(payload: Json, source: String, version: Int): Option[Alert] =
      if version <= 0 then
        Some(Alert(
          id           = UUID.randomUUID().toString,
          ruleName     = name,
          severity     = severity,
          message      = s"Event from $source has no valid version",
          eventVersion = version,
          source       = source,
          createdAt    = Instant.now().toString,
          details      = payload,
        ))
      else None

  object UnknownSourceRule extends CepRule:
    val name     = "unknown_source"
    val severity = "INFO"

    private val knownSources = Set("world-sim")

    def evaluate(payload: Json, source: String, version: Int): Option[Alert] =
      if !knownSources.contains(source) then
        Some(Alert(
          id           = UUID.randomUUID().toString,
          ruleName     = name,
          severity     = severity,
          message      = s"Event from unknown source: $source",
          eventVersion = version,
          source       = source,
          createdAt    = Instant.now().toString,
          details      = payload,
        ))
      else None

  object NullPayloadRule extends CepRule:
    val name     = "null_payload"
    val severity = "CRITICAL"

    def evaluate(payload: Json, source: String, version: Int): Option[Alert] =
      if payload.isNull then
        Some(Alert(
          id           = UUID.randomUUID().toString,
          ruleName     = name,
          severity     = severity,
          message      = s"Event from $source has null payload",
          eventVersion = version,
          source       = source,
          createdAt    = Instant.now().toString,
          details      = payload,
        ))
      else None

object Main extends ZIOAppDefault:

  private val enrichedTopic = "enriched-events"
  private val alertsTopic   = "alerts"

  def run: Task[ExitCode] =
    val program = for
      config   <- ZIO.service[AppConfig]
      producer <- ZIO.service[Producer]
      _        <- Console.printLine(s"sentinel-cep starting — broker: ${config.kafkaBroker}")
      settings  = ConsumerSettings(List(config.kafkaBroker))
                    .withGroupId(s"${config.groupId}-cep")
                    .withMaxPollRecords(100)
      _        <- Consumer
                   .consumeWith(
                     settings,
                     Subscription.topics(enrichedTopic),
                     Serde.byteArray,
                     Serde.byteArray,
                   ) { record =>
                     val body = new String(record.value, java.nio.charset.StandardCharsets.UTF_8)
                     parseEnriched(body) match
                       case Some(enriched) =>
                         val alerts = CepRules.all.flatMap(_.evaluate(enriched.payload, enriched.source, enriched.version))
                         ZIO.foreachDiscard(alerts) { alert =>
                           producer.produce(
                             alertsTopic,
                             alert.severity.getBytes(java.nio.charset.StandardCharsets.UTF_8),
                             alert.asJson.noSpaces.getBytes(java.nio.charset.StandardCharsets.UTF_8),
                             Serde.byteArray,
                             Serde.byteArray,
                           ).ignore
                         }
                       case None =>
                         ZIO.unit
                   }
    yield ExitCode.success

    program.catchAll { e =>
      Console.printLineError(s"cep failed: ${e.getMessage}") *>
      ZIO.succeed(ExitCode.failure)
    }.provide(AppConfig.layer, KafkaProducer.producerLayer)

  private case class EnrichedEventFields(
    version: Int,
    source: String,
    payload: Json,
  )

  private def parseEnriched(json: String): Option[EnrichedEventFields] =
    for
      parsed  <- parse(json).toOption
      cursor   = parsed.hcursor
      version <- cursor.get[Int]("version").toOption
      source  <- cursor.get[String]("source").toOption
      payload <- cursor.get[Json]("payload").toOption
    yield EnrichedEventFields(version, source, payload)
