package sentinel.streams

import zio.*
import zio.kafka.consumer.*
import zio.kafka.serde.*

object Main extends ZIOAppDefault:

  private val settings: ConsumerSettings =
    ConsumerSettings(List("localhost:9092"))
      .withGroupId("sentinel-streams")

  def run: Task[ExitCode] =
    (for
      _ <- Console.printLine("sentinel-streams starting")
      _ <- ZIO.never
    yield ExitCode.success)
      .provide(Consumer.live, ZLayer.succeed(settings))
