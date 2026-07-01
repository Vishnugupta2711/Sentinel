package sentinel.cep

import zio.*

object Main extends ZIOAppDefault:
  def run: Task[ExitCode] =
    for
      _ <- Console.printLine("sentinel-cep starting")
      _ <- ZIO.never
    yield ExitCode.success
