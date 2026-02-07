# Mission Control

Desktop app for managing long-running AI agents.

## Architecture

- **Desktop**: Tauri v2 + React 18 + TypeScript + Vite + Tailwind
- **API**: FastAPI + SQLAlchemy + Alembic (Python 3.12+)
- **Database**: PostgreSQL 16 + Redis 7
- **Deployment**: Google Cloud Run

## Prerequisites

- Node.js 22+ (see `.nvmrc`)
- Python 3.12+
- Rust stable (see `rust-toolchain.toml`)
- Docker & Docker Compose
- pnpm 9+

## Quick Start

```bash
# Install dependencies
pnpm install
cd apps/api && pip install -e ".[dev]"

# Start everything (Docker + API + Desktop)
make dev

# Or start components individually:
make dev-api      # API only
make dev-desktop  # Desktop only (expects API running)
```

## Development

```bash
make test      # Run all tests
make lint      # Run linters
make typecheck # Run type checkers
make migrate   # Run database migrations
```

## Project Structure

```
mcontrol/
├── apps/
│   ├── desktop/          # Tauri + React frontend
│   └── api/              # FastAPI backend
├── packages/
│   └── shared/           # Shared schemas (Zod/Pydantic)
├── docs/                 # Documentation
├── infra/                # Infrastructure configs
└── docker-compose.yml    # Local dev services
```

## API Endpoints

- `GET /api/health` - Health check
- `WS /api/ws` - WebSocket for real-time updates

## Documentation

- [Architecture](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Contributing](./docs/CONTRIBUTING.md)
- [ADRs](./docs/ADR/)

## License

Private - All rights reserved
