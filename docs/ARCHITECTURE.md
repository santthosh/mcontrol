# Architecture

## System Overview

Mission Control is a desktop application for managing long-running AI agents. It follows a thin client architecture where the desktop app communicates with a cloud-hosted API service.

```
┌─────────────────┐     REST/WS     ┌─────────────────┐
│                 │◄───────────────►│                 │
│  Tauri Desktop  │                 │  FastAPI on     │
│  (React + Rust) │                 │  Cloud Run      │
│                 │                 │                 │
└─────────────────┘                 └────────┬────────┘
                                             │
                                    ┌────────┴────────┐
                                    │                 │
                              ┌─────▼─────┐     ┌─────▼─────┐
                              │           │     │           │
                              │ Postgres  │     │   Redis   │
                              │   (SQL)   │     │  (Cache)  │
                              │           │     │           │
                              └───────────┘     └───────────┘
```

## Components

### Desktop App (apps/desktop/)

- **Technology**: Tauri v2 + React 18 + TypeScript + Vite + Tailwind
- **Purpose**: Native desktop shell with modern web UI
- **Responsibilities**:
  - User interface for agent management
  - Real-time updates via WebSocket
  - Secure credential storage (via system keychain)

### API Service (apps/api/)

- **Technology**: FastAPI + SQLAlchemy + Alembic (Python 3.12+)
- **Deployment**: Google Cloud Run
- **Responsibilities**:
  - Business logic and orchestration
  - LLM provider integration
  - Data persistence and caching
  - Authentication (Firebase Auth)

### Database

- **PostgreSQL 16**: Primary data store
  - User accounts
  - Team members (agent configurations)
  - Tasks and execution history
  - Credentials (encrypted)

- **Redis 7**: Caching and real-time features
  - WebSocket session management
  - Rate limiting
  - Task queue (future)

## GCP Services

| Service | Purpose |
|---------|---------|
| Cloud Run | API hosting |
| Cloud SQL | PostgreSQL database |
| Memorystore | Redis cache |
| Secret Manager | API keys, credentials |
| Firebase Auth | User authentication |

## Data Flow

1. User interacts with desktop app
2. App sends REST request to API (or WebSocket message)
3. API authenticates via Firebase token
4. API processes request, interacts with DB/cache
5. API orchestrates LLM calls if needed
6. Response sent back to desktop app
7. UI updates with new state

## Security

- Firebase Auth for user authentication
- All credentials stored encrypted in database
- Secrets managed via GCP Secret Manager
- CORS restricted to allowed origins
- HTTPS/WSS in production

## Shared Schemas

TypeScript Zod schemas serve as the source of truth, with Pydantic models generated for Python. This ensures type consistency across the stack.

```
packages/shared/
├── src/           # TypeScript Zod schemas
└── python/        # Generated Pydantic models
```
