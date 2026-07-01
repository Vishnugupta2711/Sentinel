FROM eclipse-temurin:17-jdk-jammy AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://github.com/sbt/sbt/releases/download/v1.12.13/sbt-1.12.13.tgz | tar xz -C /usr/local --strip-components=1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY project/ project/
COPY build.sbt .
RUN sbt update
COPY . .
RUN sbt compile

FROM eclipse-temurin:17-jre-alpine
RUN apk --no-cache add ca-certificates tzdata && \
    addgroup -S sentinel && adduser -S -G sentinel sentinel
COPY --from=builder /app/common/target /app/common
COPY --from=builder /app/streams/target /app/streams
COPY --from=builder /app/cep/target /app/cep
COPY --from=builder /app/sink/target /app/sink
USER sentinel
ENTRYPOINT ["sh", "-c", "java -cp \"/app/common/classes:/app/common/dependency/*:/app/$SERVICE/classes:/app/$SERVICE/dependency/*\" sentinel.${SERVICE}.Main"]
