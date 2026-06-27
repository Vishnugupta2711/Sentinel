FROM python:3.10-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.4.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# ─── Runtime stage ──────────────────────────────────────────────
FROM python:3.10-slim

# Security: install curl for healthcheck only; no build tools
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Security: create a non-root application user
RUN groupadd --gid 1001 sentinel \
    && useradd --uid 1001 --gid sentinel --shell /bin/bash --create-home sentinel

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY . .

# Security: hand ownership to the app user, make code read-only
RUN chown -R sentinel:sentinel /app && chmod -R 550 /app

USER sentinel

EXPOSE 8000

# NOTE: Single worker is intentional.
# Sentinel uses in-memory state (asyncio.Queue, deque, dict singletons) that
# are NOT shared across OS processes. Running multiple uvicorn workers would
# create isolated state per process, breaking WebSocket fanout and the
# intelligence pipeline. For horizontal scaling, run multiple containers
# behind a load balancer with a shared Redis pub/sub layer.
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--access-log"]
