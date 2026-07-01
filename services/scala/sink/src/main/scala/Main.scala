package sentinel.sink

import zio.*
import zio.kafka.consumer.*
import zio.kafka.serde.*
import sentinel.common.*

object Main extends ZIOAppDefault:

  def run: Task[ExitCode] =
    val program = for
      config      <- ZIO.service[AppConfig]
      clickHouse  <- ZIO.service[ClickHouseClient]
      _           <- Console.printLine(s"sentinel-sink starting — broker: ${config.kafkaBroker} clickhouse: ${config.clickHouseUrl}")
      settings     = ConsumerSettings(List(config.kafkaBroker))
                       .withGroupId(s"${config.groupId}-sink")
                       .withMaxPollRecords(500)
      _           <- Consumer
                      .consumeWith(
                        settings,
                        Subscription.topics("enriched-events"),
                        Serde.byteArray,
                        Serde.byteArray,
                      ) { record =>
                        val insert = s"INSERT INTO sentinel.events FORMAT JSONEachRow ${new String(record.value, java.nio.charset.StandardCharsets.UTF_8)}"
                        clickHouse.execute(insert).ignore
                      }
    yield ExitCode.success

    program.catchAll { e =>
      Console.printLineError(s"sink failed: ${e.getMessage}") *>
      ZIO.succeed(ExitCode.failure)
    }.provide(AppConfig.layer, ClickHouseClient.layer)
