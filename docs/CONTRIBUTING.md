# 🤝 Contributing to Mission Control

First off, thank you for considering contributing to Mission Control! It's people like you that make this project great. 🎉

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Code Style](#-code-style)
- [Testing](#-testing)
- [Submitting Changes](#-submitting-changes)
- [Project Structure](#-project-structure)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Node.js | 22+ | [nodejs.org](https://nodejs.org/) or `nvm use` |
| Python | 3.12+ | [python.org](https://python.org/) |
| Rust | stable | [rustup.rs](https://rustup.rs/) |
| Docker | latest | [docker.com](https://docker.com/) |
| pnpm | 9+ | `npm install -g pnpm` |

### Initial Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/mcontrol.git
cd mcontrol

# 2. Add upstream remote
git remote add upstream https://github.com/santthosh/mcontrol.git

# 3. Install Node.js dependencies
pnpm install

# 4. Set up Python virtual environment
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cd ../..

# 5. Copy environment file
cp apps/api/.env.example apps/api/.env

# 6. Start development
make dev
```

## 💻 Development Workflow

### Branching Strategy

We use a simple branching model:

- `main` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

```bash
# Create a feature branch
git checkout -b feature/my-awesome-feature

# Keep your branch up to date
git fetch upstream
git rebase upstream/main
```

### Running the Development Environment

```bash
# Start everything (recommended)
make dev

# Or start components individually
make docker-up    # Start Postgres + Redis
make dev-api      # Start API server
make dev-desktop  # Start desktop app
```

### Hot Reloading

Both the API and desktop app support hot reloading:

- **API**: Changes to Python files auto-reload uvicorn
- **Desktop**: Changes to React files trigger Vite HMR

## 🎨 Code Style

### TypeScript

We use ESLint with strict TypeScript rules.

```bash
# Check for issues
pnpm lint

# Auto-fix issues
pnpm lint --fix

# Type check
pnpm typecheck
```

**Guidelines:**

- ✅ Use TypeScript strict mode
- ✅ Prefer `const` over `let`
- ✅ Use meaningful variable names
- ✅ Add types to function parameters and returns
- ❌ Avoid `any` type

### Python

We use Ruff for linting and formatting, and Pyright for type checking.

```bash
cd apps/api

# Lint
.venv/bin/ruff check .

# Format
.venv/bin/ruff format .

# Type check
.venv/bin/pyright
```

**Guidelines:**

- ✅ Follow PEP 8 (enforced by Ruff)
- ✅ Use type hints for all functions
- ✅ Write docstrings for public functions
- ✅ Keep functions small and focused
- ❌ Avoid mutable default arguments

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, semicolons, etc.) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

**Examples:**

```bash
feat(api): add user authentication endpoint
fix(desktop): resolve connection timeout on slow networks
docs: update API reference with new endpoints
chore(deps): upgrade FastAPI to 0.110.0
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run API tests only
cd apps/api && .venv/bin/pytest

# Run API tests with coverage
cd apps/api && .venv/bin/pytest --cov=app --cov-report=html

# Run desktop tests only
pnpm --filter desktop test
```

### Writing Tests

**API Tests (pytest):**

```python
# tests/test_feature.py
import pytest
from fastapi.testclient import TestClient

def test_feature_works(client: TestClient):
    response = client.get("/api/feature")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

**Desktop Tests (Vitest):**

```typescript
// src/components/Feature.test.tsx
import { describe, it, expect } from "vitest";

describe("Feature", () => {
  it("should work correctly", () => {
    expect(true).toBe(true);
  });
});
```

## 📤 Submitting Changes

### Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks** before submitting:
   ```bash
   make lint
   make typecheck
   make test
   ```

3. **Create a Pull Request** with:
   - Clear title following commit conventions
   - Description of changes
   - Screenshots for UI changes
   - Link to related issue (if applicable)

### PR Checklist

- [ ] Code follows the project style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No unrelated changes included

### Review Process

1. A maintainer will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. 🎉 Celebrate your contribution!

## 📁 Project Structure

```
mcontrol/
├── 📱 apps/
│   ├── desktop/              # Tauri + React desktop app
│   │   ├── src/              # React components
│   │   ├── src-tauri/        # Rust Tauri code
│   │   └── package.json
│   └── api/                  # FastAPI backend
│       ├── app/              # Application code
│       │   ├── routes/       # API endpoints
│       │   ├── models/       # SQLAlchemy models
│       │   ├── middleware/   # Request middleware
│       │   └── lib/          # Utilities
│       ├── alembic/          # Database migrations
│       ├── tests/            # pytest tests
│       └── pyproject.toml
├── 📦 packages/
│   └── shared/               # Shared TypeScript schemas
│       ├── src/              # Zod schemas
│       └── python/           # Generated Pydantic models
├── 📚 docs/                  # Documentation
├── 🔧 infra/                 # Infrastructure configs
├── 🐳 docker-compose.yml     # Local development services
├── 📋 Makefile               # Development commands
└── 📄 package.json           # Workspace configuration
```

## 🆘 Getting Help

- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Bug Reports**: Open an issue with the bug template
- 💡 **Feature Requests**: Open an issue with the feature template

---

Thank you for contributing! 🙌
