package sentinel.common

import zio.*
import zio.test.*
import zio.test.Assertion.*

object ConfigSpec extends ZIOSpecDefault:
  def spec = suite("ConfigSpec")(
    test("loads default configuration when environment variables are missing") {
      for
        config <- ZIO.service[AppConfig]
      yield assertTrue(
        config.kafkaBroker == "localhost:9092",
        config.clickHouseUrl == "http://localhost:8123",
        config.groupId == "sentinel"
      )
    }.provideLayer(AppConfig.layer),
    
    test("loads configuration from environment variables") {
      for
        _      <- TestSystem.putEnv("KAFKA_BROKER", "kafka:9093")
        _      <- TestSystem.putEnv("CLICKHOUSE_URL", "http://clickhouse:8123")
        _      <- TestSystem.putEnv("GROUP_ID", "test-group")
        config <- ZIO.service[AppConfig].provideLayer(AppConfig.layer)
      yield assertTrue(
        config.kafkaBroker == "kafka:9093",
        config.clickHouseUrl == "http://clickhouse:8123",
        config.groupId == "test-group"
      )
    }
  )
