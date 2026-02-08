.PHONY: dev dev-api dev-desktop build test lint typecheck docker-up docker-down clean install

# Firebase emulator environment variables
export FIRESTORE_EMULATOR_HOST=localhost:8080
export FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
export FIREBASE_PROJECT_ID=mcontrol-dev

# Start everything: Docker (Firebase Emulator) + API + Desktop
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

# Start Docker containers (Firebase Emulator)
docker-up:
	@echo "Starting Firebase Emulator..."
	docker-compose up -d
	@echo "Waiting for emulator to be ready..."
	@sleep 5

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
	cd apps/api && FIRESTORE_EMULATOR_HOST=localhost:8080 FIREBASE_PROJECT_ID=mcontrol-dev .venv/bin/pytest
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

# Sync version across all files (for testing locally)
# Usage: make version VERSION=2026.02.07.1
version:
ifndef VERSION
	$(error VERSION is required. Usage: make version VERSION=2026.02.07.1)
endif
	@echo "Syncing version $(VERSION) across all files..."
	@.github/scripts/sync-versions.sh $(VERSION)

# Create and push a release tag (triggers GitHub Actions release workflow)
# Usage: make release VERSION=2026.02.07.1
release:
ifndef VERSION
	$(error VERSION is required. Usage: make release VERSION=2026.02.07.1)
endif
	@echo "Creating release v$(VERSION)..."
	@.github/scripts/sync-versions.sh $(VERSION)
	@git add -A
	@git commit -m "chore: bump version to $(VERSION)" || echo "No version changes to commit"
	@git tag -a "v$(VERSION)" -m "Release $(VERSION)"
	@echo ""
	@echo "Release tag v$(VERSION) created locally."
	@echo "To publish the release, run:"
	@echo "  git push origin main && git push origin v$(VERSION)"
