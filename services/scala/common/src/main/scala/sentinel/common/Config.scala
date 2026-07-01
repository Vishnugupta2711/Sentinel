package sentinel.common

import zio.*

case class AppConfig(
  kafkaBroker: String,
  clickHouseUrl: String,
  groupId: String,
)

object AppConfig:
  val layer: ZLayer[Any, SecurityException, AppConfig] =
    ZLayer.fromZIO(
      for
        broker <- System.envOrElse("KAFKA_BROKER", "localhost:9092")
        chUrl  <- System.envOrElse("CLICKHOUSE_URL", "http://localhost:8123")
        gid    <- System.envOrElse("GROUP_ID", "sentinel")
      yield AppConfig(broker, chUrl, gid),
    )
