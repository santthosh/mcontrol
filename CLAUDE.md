# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mission Control ("mcontrol") is a desktop app for managing long-running AI agents. The architecture is a Tauri thin client communicating via REST + WebSocket to a FastAPI backend deployed on Cloud Run, with Postgres and Redis for persistence.

## Repository Structure

```
mcontrol/
├── apps/
│   ├── desktop/          # Tauri v2 + React 18 + TypeScript + Vite + Tailwind
│   └── api/              # FastAPI + SQLAlchemy + Alembic (Python 3.12+)
├── packages/
│   └── shared/           # Shared schemas (Zod for TS, Pydantic for Python)
├── docs/                 # Architecture, API spec, ADRs
├── infra/                # Docker Compose, GCP config
└── docker-compose.yml    # Local dev: Postgres 16 + Redis 7
```

Uses **pnpm workspaces** for package management.

## Build and Development Commands

All commands run from repo root via Makefile:

```bash
make dev           # Start everything: Docker (Postgres + Redis) + API + Desktop
make dev-api       # Docker + API server only
make dev-desktop   # Desktop app only (expects API running)
make build         # Build all packages
make test          # Run all tests (pytest for API, Vitest for desktop)
make lint          # Run ruff (Python) + ESLint (TypeScript)
make typecheck     # Run mypy/pyright + tsc --noEmit
```

### Individual app commands

**Desktop (apps/desktop/):**
```bash
pnpm --filter desktop dev    # Tauri dev mode with HMR
pnpm --filter desktop build  # Build macOS binary
```

**API (apps/api/):**
```bash
uvicorn app.main:app --reload --port 8000
pytest                       # Run API tests
```

## Architecture

- **Desktop**: Tauri v2 shell (Rust) with React frontend. Thin client that communicates with API.
- **API**: FastAPI service on Cloud Run. Handles business logic, LLM orchestration, persistence.
- **Database**: PostgreSQL 16 via SQLAlchemy async, migrations with Alembic.
- **Cache**: Redis 7 for real-time features.
- **Auth**: Firebase Auth (stubbed with `AUTH_DISABLED=true` bypass for local dev).

## Shared Schemas

Schemas defined in TypeScript (Zod) as source of truth in `packages/shared/`, with codegen to Pydantic models for Python. Core types: Task, TeamMember, Model, Credential, UserSettings.

## Key Environment Variables

See `apps/api/.env.example`:
- `DATABASE_URL` - Postgres connection string
- `REDIS_URL` - Redis connection string
- `FIREBASE_PROJECT_ID` - Firebase project for auth
- `AUTH_DISABLED=true` - Skip auth validation in local dev

## Toolchain

- Node.js 22 LTS (see `.nvmrc`)
- Python 3.12+
- Rust stable (see `rust-toolchain.toml`)
