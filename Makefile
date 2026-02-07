.PHONY: dev dev-api dev-desktop build test lint typecheck docker-up docker-down clean

# Start everything: Docker (Postgres + Redis) + API + Desktop
dev: docker-up
	@echo "Starting API and Desktop..."
	@trap 'make docker-down' EXIT; \
	(cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000) & \
	(cd apps/desktop && pnpm dev) & \
	wait

# Docker + API server only
dev-api: docker-up
	@echo "Starting API server..."
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000

# Desktop app only (expects API running)
dev-desktop:
	@echo "Starting Desktop app..."
	cd apps/desktop && pnpm dev

# Start Docker containers
docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 3

# Stop Docker containers
docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

# Build all packages
build:
	pnpm -r build

# Run all tests
test:
	@echo "Running API tests..."
	cd apps/api && .venv/bin/pytest
	@echo "Running Desktop tests..."
	pnpm --filter desktop test

# Run linters
lint:
	@echo "Running Python linter..."
	cd apps/api && .venv/bin/ruff check .
	@echo "Running TypeScript linter..."
	pnpm -r lint

# Run type checkers
typecheck:
	@echo "Running Python type checker..."
	cd apps/api && .venv/bin/pyright
	@echo "Running TypeScript type checker..."
	pnpm -r typecheck

# Clean build artifacts
clean:
	rm -rf node_modules
	rm -rf apps/*/node_modules
	rm -rf packages/*/node_modules
	rm -rf apps/desktop/dist
	rm -rf apps/desktop/src-tauri/target
	rm -rf apps/api/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Install dependencies
install:
	pnpm install
	cd apps/api && pip install -e ".[dev]"

# Run database migrations
migrate:
	cd apps/api && .venv/bin/alembic upgrade head

# Create a new migration
migration:
	@read -p "Migration message: " msg; \
	cd apps/api && .venv/bin/alembic revision --autogenerate -m "$$msg"
