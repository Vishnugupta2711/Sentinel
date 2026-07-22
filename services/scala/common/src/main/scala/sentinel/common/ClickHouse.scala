package sentinel.common

import zio.*
import java.net.http.*
import java.net.URI

trait ClickHouseClient:
  def execute(query: String): Task[String]

object ClickHouseClient:
  val layer: ZLayer[AppConfig, Throwable, ClickHouseClient] =
    ZLayer.fromZIO(
      for
        config <- ZIO.service[AppConfig]
        client <- ZIO.attempt {
          val http   = HttpClient.newHttpClient()
          val uri    = URI.create(s"${config.clickHouseUrl}/?default_format=JSONEachRow")
          new ClickHouseClient:
            def execute(query: String): Task[String] =
              ZIO.attemptBlocking {
                val requestBuilder = HttpRequest.newBuilder()
                  .uri(uri)
                  .header("Content-Type", "text/plain")
                  .POST(HttpRequest.BodyPublishers.ofString(query))

                if (uri.getUserInfo != null) {
                  val auth = java.util.Base64.getEncoder.encodeToString(uri.getUserInfo.getBytes("UTF-8"))
                  requestBuilder.header("Authorization", s"Basic $$auth")
                }

                val request = requestBuilder.build()
                http.send(request, HttpResponse.BodyHandlers.ofString()).body()
              }
        }
      yield client,
    )
