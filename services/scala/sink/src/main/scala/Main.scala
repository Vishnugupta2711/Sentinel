package sentinel.sink

import zio.*
import zio.kafka.consumer.*
import zio.kafka.serde.*
import sentinel.common.*

object Main extends ZIOAppDefault:

  private val enrichedTopic = "enriched-events"

  private val createTable: String =
    """CREATE TABLE IF NOT EXISTS sentinel.events (
      |  version UInt32,
      |  source String,
      |  received_at String,
      |  valid UInt8,
      |  payload String
      |) ENGINE = MergeTree()
      |ORDER BY (source, received_at)""".stripMargin

  private val createDb: String = "CREATE DATABASE IF NOT EXISTS sentinel"

  private def initSchema(ch: ClickHouseClient): Task[Unit] =
    ch.execute(createDb).ignore *>
      ch.execute(createTable).ignore

  def run: Task[ExitCode] =
    val program = for
      config     <- ZIO.service[AppConfig]
      clickHouse <- ZIO.service[ClickHouseClient]
      _          <- Console.printLine(
                      s"sentinel-sink starting — broker: ${config.kafkaBroker} clickhouse: ${config.clickHouseUrl}",
                    )
      _          <- initSchema(clickHouse)
      settings    = ConsumerSettings(List(config.kafkaBroker))
                      .withGroupId(s"${config.groupId}-sink")
                      .withMaxPollRecords(500)
      _          <- Consumer
                     .consumeWith(
                       settings,
                       Subscription.topics(enrichedTopic),
                       Serde.byteArray,
                       Serde.byteArray,
                     ) { record =>
                       val body  = new String(record.value, java.nio.charset.StandardCharsets.UTF_8)
                       val query = s"INSERT INTO sentinel.events FORMAT JSONEachRow $body"
                       clickHouse.execute(query).ignore
                     }
    yield ExitCode.success

    program.catchAll { e =>
      Console.printLineError(s"sink failed: ${e.getMessage}") *>
      ZIO.succeed(ExitCode.failure)
    }.provide(AppConfig.layer, ClickHouseClient.layer)
