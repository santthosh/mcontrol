# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mission Control ("mcontrol") is a desktop app for managing long-running AI agents. The architecture is a Tauri thin client communicating via REST + WebSocket to a FastAPI backend deployed on Cloud Run, with Firestore for persistence.

## Repository Structure

```
mcontrol/
├── apps/
│   ├── desktop/          # Tauri v2 + React 18 + TypeScript + Vite + Tailwind
│   └── api/              # FastAPI + Firestore + Firebase Auth (Python 3.12+)
├── packages/
│   └── shared/           # Shared schemas (Zod for TS, Pydantic for Python)
├── docs/                 # Architecture, API spec, ADRs
├── infra/
│   ├── clouddeploy/      # Cloud Run service config
│   ├── firebase/         # Firebase emulator config
│   └── terraform/        # IaC for GCP (dev, staging, prod environments)
├── specs/                # Project specifications
├── .github/workflows/    # CI/CD (ci.yml, deploy.yml, release.yml)
├── docker-compose.yml    # Local dev: Firebase Emulator (Firestore + Auth)
└── firebase.json         # Firebase emulator port config
```

Uses **pnpm workspaces** (`pnpm@9`, Node.js >=22) for package management.

## Build and Development Commands

All commands run from repo root via Makefile:

```bash
make dev               # Start everything: Firebase Emulator + API + Desktop
make dev-api           # Firebase Emulator + API server only
make dev-desktop       # Desktop app only (default: local API)
make dev-desktop ENV=dev      # Desktop pointing at dev API
make dev-desktop ENV=staging  # Desktop pointing at staging API
make build             # Build all packages (pnpm -r build)
make test              # Run all tests (pytest for API, Vitest for desktop)
make lint              # Run ruff (Python) + ESLint (TypeScript)
make typecheck         # Run pyright + tsc --noEmit
make install           # Install all dependencies (pnpm + pip)
make clean             # Remove build artifacts and caches
make docker-up         # Start Firebase Emulator
make docker-down       # Stop Firebase Emulator
make version VERSION=YYYY.MM.DD.N   # Sync CalVer version across files
make release VERSION=YYYY.MM.DD.N   # Tag and prepare release
```

### Individual app commands

**Desktop (apps/desktop/):**
```bash
pnpm --filter desktop dev    # Tauri dev mode with HMR
pnpm --filter desktop build  # Build desktop binary
pnpm --filter desktop test   # Run Vitest
```

**API (apps/api/):**
```bash
cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000
cd apps/api && .venv/bin/pytest
cd apps/api && .venv/bin/ruff check .
cd apps/api && .venv/bin/pyright
```

## Architecture

- **Desktop**: Tauri v2 shell (Rust) with React frontend. Thin client that communicates with API via REST + WebSocket.
- **API**: FastAPI service on Cloud Run. Handles business logic, LLM orchestration, persistence.
- **Database**: Firestore (Firebase) for document storage. Local dev uses Firebase Emulator via Docker. PostgreSQL + Redis planned for production (deps included, see `infra/secrets.example`).
- **Auth**: Firebase Auth (bypass with `AUTH_DISABLED=true` for local dev).

## Shared Schemas

Schemas defined in TypeScript (Zod) as source of truth in `packages/shared/`, with codegen to Pydantic models for Python (`pnpm --filter @mcontrol/shared generate:pydantic`). Core types: Task, TeamMember, Model, Credential, UserSettings.

## Key Environment Variables

See `apps/api/.env.example`:
- `FIREBASE_PROJECT_ID` - Firebase project ID (default: `mcontrol-dev`)
- `FIRESTORE_EMULATOR_HOST` - Firestore emulator address (default: `localhost:8080`)
- `FIREBASE_AUTH_EMULATOR_HOST` - Auth emulator address (default: `localhost:9099`)
- `AUTH_DISABLED=true` - Skip auth validation in local dev
- `API_HOST` / `API_PORT` - API bind address (default: `0.0.0.0:8000`)

Production secrets managed via GCP Secret Manager (see `infra/secrets.example`).

## Deployment

- **Environments**: dev, staging, production with separate Terraform state
- **API**: Containerized (Dockerfile in `apps/api/`), deployed to Cloud Run via GitHub Actions
- **Desktop**: Multi-platform builds (macOS universal, Windows, Linux) via GitHub Actions release workflow
- **Versioning**: CalVer format `YYYY.MM.DD.Build` (e.g., `2026.02.07.1`)
- **Pipeline**: CI checks → build Docker image → deploy dev (auto) → staging (approval) → prod (approval)

## Toolchain

- Node.js 22 LTS (see `.nvmrc`)
- pnpm 9 (see `package.json` packageManager field)
- Python 3.12+
- Rust stable (see `rust-toolchain.toml`)
- Terraform (for GCP infrastructure)
