package sentinel.cep

import zio.*
import zio.kafka.consumer.*
import zio.kafka.serde.*
import sentinel.common.*

object Main extends ZIOAppDefault:

  def run: Task[ExitCode] =
    val program = for
      config <- ZIO.service[AppConfig]
      _      <- Console.printLine(s"sentinel-cep starting — broker: ${config.kafkaBroker}")
      settings = ConsumerSettings(List(config.kafkaBroker))
                   .withGroupId(s"${config.groupId}-cep")
                   .withMaxPollRecords(100)
      _      <- Consumer
                 .consumeWith(
                   settings,
                   Subscription.topics("enriched-events"),
                   Serde.byteArray,
                   Serde.byteArray,
                 ) { record =>
                   Console.printLine(s"cep received ${record.value.length} bytes").ignore
                 }
    yield ExitCode.success

    program.catchAll { e =>
      Console.printLineError(s"cep failed: ${e.getMessage}") *>
      ZIO.succeed(ExitCode.failure)
    }.provide(AppConfig.layer)
