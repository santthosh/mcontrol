<p align="center">
  <img src="https://placehold.co/120x120/0ea5e9/white?text=M" alt="Mission Control Logo" width="120" height="120">
</p>

<h1 align="center">Mission Control</h1>

<p align="center">
  <strong>🚀 A powerful desktop app for managing long-running AI agents</strong>
</p>

<p align="center">
  <a href="https://github.com/santthosh/mcontrol/actions/workflows/ci.yml">
    <img src="https://github.com/santthosh/mcontrol/actions/workflows/ci.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://github.com/santthosh/mcontrol/blob/main/LICENSE.md">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/santthosh/mcontrol/releases">
    <img src="https://img.shields.io/github/v/release/santthosh/mcontrol?include_prereleases" alt="Release">
  </a>
  <img src="https://img.shields.io/badge/node-%3E%3D22-brightgreen" alt="Node.js">
  <img src="https://img.shields.io/badge/python-%3E%3D3.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/rust-stable-orange" alt="Rust">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## ✨ Features

- 🤖 **AI Agent Management** - Monitor and control long-running AI agents from a single dashboard
- ⚡ **Real-time Updates** - WebSocket-powered live status updates and notifications
- 🔒 **Secure by Design** - Firebase authentication with credential encryption
- 🖥️ **Native Desktop Experience** - Built with Tauri for a lightweight, fast native app
- 🌐 **Cloud-Ready** - Scalable backend designed for Google Cloud Run
- 📦 **Monorepo Architecture** - Shared schemas between frontend and backend

## 🏗️ Architecture

| Component | Technology |
|-----------|------------|
| **Desktop** | Tauri v2 + React 18 + TypeScript + Vite + Tailwind |
| **API** | FastAPI + SQLAlchemy + Alembic (Python 3.12+) |
| **Database** | PostgreSQL 16 + Redis 7 |
| **Deployment** | Google Cloud Run |

```
mcontrol/
├── 📱 apps/
│   ├── desktop/          # Tauri + React frontend
│   └── api/              # FastAPI backend
├── 📦 packages/
│   └── shared/           # Shared schemas (Zod/Pydantic)
├── 📚 docs/              # Documentation
├── 🔧 infra/             # Infrastructure configs
└── 🐳 docker-compose.yml # Local dev services
```

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 22+** - [Download](https://nodejs.org/) or use `nvm use`
- **Python 3.12+** - [Download](https://python.org/)
- **Rust** - [Install](https://rustup.rs/)
- **Docker** - [Download](https://docker.com/)
- **pnpm** - `npm install -g pnpm`

### Installation

```bash
# Clone the repository
git clone https://github.com/santthosh/mcontrol.git
cd mcontrol

# Install Node.js dependencies
pnpm install

# Install Python dependencies
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cd ../..

# Start development (Docker + API + Desktop)
make dev
```

### Verify Installation

Once running, you should see:

- 🟢 **API**: http://localhost:8000/api/health returns `{"status":"ok"}`
- 🟢 **Desktop**: Native app window with "Connected" indicator
- 🟢 **Docs**: http://localhost:8000/api/docs for Swagger UI

## 🛠️ Development

```bash
# Start all services
make dev

# Start individual components
make dev-api      # API server only
make dev-desktop  # Desktop app only

# Code quality
make lint         # Run linters (ruff + ESLint)
make typecheck    # Run type checkers (pyright + tsc)
make test         # Run all tests

# Database
make migrate      # Run migrations
make migration    # Create new migration
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](./docs/ARCHITECTURE.md) | System design and component overview |
| [API Reference](./docs/API.md) | REST and WebSocket API documentation |
| [Contributing](./docs/CONTRIBUTING.md) | Development workflow and guidelines |
| [ADRs](./docs/ADR/) | Architecture Decision Records |

## 🤝 Contributing

We love contributions! Please see our [Contributing Guide](./docs/CONTRIBUTING.md) for details.

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](./LICENSE.md) file for details.

## 🙏 Acknowledgments

- [Tauri](https://tauri.app/) - For the amazing desktop framework
- [FastAPI](https://fastapi.tiangolo.com/) - For the high-performance API framework
- [Anthropic](https://anthropic.com/) - For Claude AI assistance

---

<p align="center">
  Made with ❤️ by the Mission Control team
</p>
