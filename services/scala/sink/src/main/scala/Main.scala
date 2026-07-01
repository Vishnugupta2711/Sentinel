package sentinel.sink

import zio.*

object Main extends ZIOAppDefault:
  def run: Task[ExitCode] =
    for
      _ <- Console.printLine("sentinel-sink starting")
      _ <- ZIO.never
    yield ExitCode.success
