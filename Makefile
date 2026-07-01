.PHONY: run build up down logs test lint format clean deploy backup healthcheck status \
        buf-gen buf-lint proto-java build-go test-go build-scala test-scala test-all

# ═══════════════════════════════════════════════════════════════
# PRODUCTION DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

deploy: ## Full production deployment (single command)
	@echo "═══════════════════════════════════════════════"
	@echo "  Sentinel — Production Deployment"
	@echo "═══════════════════════════════════════════════"
	docker compose up -d --build --remove-orphans
	@echo "Waiting for services to stabilize..."
	@sleep 20
	@$(MAKE) healthcheck
	@echo "═══════════════════════════════════════════════"
	@echo "  ✓ Sentinel is LIVE"
	@echo "  Frontend:   http://localhost"
	@echo "  Backend:    http://localhost:8000"
	@echo "  Swagger:    http://localhost:8000/docs"
	@echo "  Grafana:    http://localhost:3001"
	@echo "  Prometheus: http://localhost:9090"
	@echo "═══════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════════
# INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════

up: ## Start all containers
	docker compose up -d

down: ## Stop all containers
	docker compose down

restart: ## Restart all containers
	docker compose restart

build: ## Build all images
	docker compose build --parallel

pull: ## Pull latest images
	docker compose pull

logs: ## Tail all container logs
	docker compose logs -f --tail=100

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker compose logs -f frontend

status: ## Show container status
	@docker compose ps
	@echo ""
	@echo "─── Resource Usage ───────────────────────────"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════
# HEALTH & MONITORING
# ═══════════════════════════════════════════════════════════════

healthcheck: ## Run comprehensive health check
	@bash scripts/healthcheck.sh

# ═══════════════════════════════════════════════════════════════
# BACKUPS
# ═══════════════════════════════════════════════════════════════

backup: ## Run full backup (PostgreSQL + Redis + config)
	@bash scripts/backup.sh

# ═══════════════════════════════════════════════════════════════
# PROTOBUF CONTRACTS
# ═══════════════════════════════════════════════════════════════

buf-lint: ## Lint protobuf contracts
	cd contracts && buf lint

buf-gen: ## Generate code from protobuf contracts (Go, Python, TS)
	cd contracts && buf generate

proto-java: ## Generate Java protobuf classes for Scala services
	protoc --java_out=services/scala/common/src/main/java --proto_path=contracts/proto contracts/proto/*.proto

buf-gen-all: buf-gen proto-java ## Generate all protobuf code (Go + Python + TS + Java)

# ═══════════════════════════════════════════════════════════════
# GO SERVICES
# ═══════════════════════════════════════════════════════════════

build-go: ## Build Go services
	cd services/go && go build ./cmd/gateway && go build ./cmd/core

test-go: ## Run Go tests
	cd services/go && go test ./...

lint-go: ## Lint Go code
	cd services/go && go vet ./...

# ═══════════════════════════════════════════════════════════════
# SCALA SERVICES
# ═══════════════════════════════════════════════════════════════

build-scala: proto-java ## Build Scala services (regenerates Java protos first)
	cd services/scala && sbt compile

test-scala: ## Run Scala tests
	cd services/scala && sbt test

# ═══════════════════════════════════════════════════════════════
# ALL TESTS
# ═══════════════════════════════════════════════════════════════

test-all: test-backend test-go test-scala ## Run all tests

# ═══════════════════════════════════════════════════════════════
# BACKEND DEVELOPMENT
# ═══════════════════════════════════════════════════════════════

run-backend: ## Run backend in dev mode
	cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test-backend: ## Run backend tests
	cd backend && poetry run pytest

lint-backend: ## Lint backend code
	cd backend && poetry run ruff check .
	cd backend && poetry run black --check .
	cd backend && poetry run isort --check-only .

format-backend: ## Format backend code
	cd backend && poetry run ruff check --fix .
	cd backend && poetry run black .
	cd backend && poetry run isort .

# ═══════════════════════════════════════════════════════════════
# FRONTEND DEVELOPMENT
# ═══════════════════════════════════════════════════════════════

run-frontend: ## Run frontend in dev mode
	cd frontend && pnpm run dev

build-frontend: ## Build frontend
	cd frontend && pnpm run build

lint-frontend: ## Lint frontend code
	cd frontend && pnpm run lint

format-frontend: ## Format frontend code
	cd frontend && pnpm run format

# ═══════════════════════════════════════════════════════════════
# COMPOUND COMMANDS
# ═══════════════════════════════════════════════════════════════

run: up run-backend run-frontend

test: test-backend test-go test-scala

lint: buf-lint lint-backend lint-frontend lint-go

format: format-backend format-frontend

# ═══════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════

clean: down ## Stop containers and clean build artifacts
	rm -rf backend/dist backend/build backend/*.egg-info
	rm -rf frontend/.next frontend/out
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

clean-all: clean ## Deep clean including Docker volumes
	docker compose down -v --remove-orphans
	docker image prune -f

clean-gen: ## Clean all generated protobuf code
	rm -rf contracts/gen/ services/scala/common/src/main/java/sentinel/

# ═══════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
