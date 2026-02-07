# Contributing

## Development Setup

### Prerequisites

1. Install Node.js 22+ (use nvm: `nvm use`)
2. Install Python 3.12+
3. Install Rust stable
4. Install Docker & Docker Compose
5. Install pnpm: `npm install -g pnpm`

### Initial Setup

```bash
# Clone and enter repo
git clone <repo-url>
cd mcontrol

# Install Node dependencies
pnpm install

# Install Python dependencies
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -e ".[dev]"
cd ../..

# Start development
make dev
```

## Code Style

### TypeScript

- ESLint for linting
- Prettier for formatting (via ESLint)
- Strict TypeScript mode

```bash
pnpm lint        # Check
pnpm lint --fix  # Auto-fix
```

### Python

- Ruff for linting and formatting
- Pyright for type checking

```bash
cd apps/api
ruff check .     # Lint
ruff format .    # Format
pyright          # Type check
```

## Testing

```bash
# All tests
make test

# API only
cd apps/api && pytest

# Desktop only
pnpm --filter desktop test
```

## Git Workflow

1. Create a feature branch from `main`
2. Make changes with clear, atomic commits
3. Run linting and tests before pushing
4. Open a pull request for review

### Commit Messages

Follow conventional commits:

```
feat: add user authentication
fix: resolve connection timeout
docs: update API reference
chore: upgrade dependencies
```

## Database Migrations

```bash
# Create a new migration
make migration
# Enter message when prompted

# Apply migrations
make migrate
```

## Project Structure

- `/apps/desktop` - Tauri + React frontend
- `/apps/api` - FastAPI backend
- `/packages/shared` - Shared schemas
- `/docs` - Documentation
- `/infra` - Infrastructure configs
