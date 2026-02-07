# ADR 002: Python + FastAPI for API

## Status

Accepted

## Context

We need to choose a backend technology for the Mission Control API. Requirements:
- LLM provider integration (Anthropic, OpenAI, etc.)
- Async I/O for concurrent operations
- Strong typing support
- Good ecosystem for AI/ML tooling

## Decision

We will use **Python 3.12+** with **FastAPI** for the API backend.

### Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastAPI | Async-first, auto OpenAPI docs, Pydantic integration |
| ORM | SQLAlchemy 2.0 | Async support, mature ecosystem |
| Migrations | Alembic | Standard choice, works well with SQLAlchemy |
| Type Checking | Pyright | Fast, accurate, LSP support |
| Linting | Ruff | Fast, replaces flake8/isort/black |
| Testing | pytest | De facto standard, great plugin ecosystem |

### Rationale

**Python over Node.js/Go:**
- Native support in all major LLM SDKs (anthropic, openai, google-generativeai)
- Rich ecosystem for AI/ML tooling
- Familiar to most developers
- FastAPI provides modern async patterns

**FastAPI over Django/Flask:**
- Native async support (critical for LLM calls)
- Automatic OpenAPI documentation
- Pydantic for request/response validation
- Type hints throughout

## Consequences

### Positive
- First-class LLM SDK support
- Type safety with Pydantic
- Auto-generated API docs
- Easy async operations

### Negative
- GIL limits CPU parallelism (not a concern for I/O-bound work)
- Slightly slower than compiled languages
- Need to maintain Python dependencies separately

### Risks
- Need to ensure proper async patterns throughout
- Memory usage requires monitoring for long-running processes

## Related

- ADR 001: Tauri + Cloud Run Monorepo
