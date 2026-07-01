FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /build/gateway ./cmd/gateway && \
    CGO_ENABLED=0 go build -o /build/core ./cmd/core

FROM alpine:3.21
RUN apk --no-cache add ca-certificates tzdata
RUN addgroup -S sentinel && adduser -S -G sentinel sentinel
COPY --from=builder /build/* /usr/local/bin/
USER sentinel
EXPOSE 8080 9000
