# ADR 001: Tauri + Cloud Run Monorepo Architecture

## Status

Accepted

## Context

We need to build a desktop application for managing long-running AI agents. The app requires:
- Native desktop experience (system tray, notifications, keychain access)
- Modern, responsive UI
- Secure credential storage
- Real-time updates
- Cloud-hosted backend for orchestration

## Decision

We will use a monorepo architecture with:
- **Tauri v2** for the desktop shell (Rust + WebView)
- **React + TypeScript** for the UI
- **FastAPI** for the backend API
- **Google Cloud Run** for API hosting

### Rationale

**Tauri over Electron:**
- Significantly smaller bundle size (~10MB vs ~150MB)
- Lower memory footprint
- Native Rust performance for system operations
- Built-in security features (CSP, capability-based permissions)

**Monorepo structure:**
- Shared schemas between frontend and backend
- Unified tooling and CI/CD
- Easier cross-cutting changes
- Single source of truth for types

**Cloud Run over self-hosted:**
- Automatic scaling
- Pay-per-use pricing
- Managed infrastructure
- Easy deployment with containers

## Consequences

### Positive
- Fast, lightweight desktop app
- Type safety across the stack
- Simplified development workflow
- Scalable cloud infrastructure

### Negative
- Tauri has smaller ecosystem than Electron
- Rust learning curve for native features
- Cloud Run cold starts (mitigated by min instances)

### Risks
- Tauri v2 is relatively new (stable as of late 2024)
- Need to manage schema sync between TS and Python

## Related

- ADR 002: Python + FastAPI for API
