#!/bin/bash
# sync-versions.sh - Synchronize version across all project files
#
# Usage: ./sync-versions.sh <version>
# Example: ./sync-versions.sh 2026.02.07.1

set -euo pipefail

VERSION="${1:-}"

if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 2026.02.07.1"
  exit 1
fi

# Validate CalVer format (YYYY.MM.DD.Build or semver for testing)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
  echo "Error: Version must be in format YYYY.MM.DD.Build (e.g., 2026.02.07.1) or semver (e.g., 0.0.1)"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Syncing version $VERSION across all files..."

# 1. Root package.json
echo "  Updating /package.json"
if command -v jq &> /dev/null; then
  jq --arg v "$VERSION" '.version = $v' "$REPO_ROOT/package.json" > "$REPO_ROOT/package.json.tmp" && \
    mv "$REPO_ROOT/package.json.tmp" "$REPO_ROOT/package.json"
else
  sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$REPO_ROOT/package.json" && \
    rm -f "$REPO_ROOT/package.json.bak"
fi

# 2. Desktop app package.json
echo "  Updating /apps/desktop/package.json"
if command -v jq &> /dev/null; then
  jq --arg v "$VERSION" '.version = $v' "$REPO_ROOT/apps/desktop/package.json" > "$REPO_ROOT/apps/desktop/package.json.tmp" && \
    mv "$REPO_ROOT/apps/desktop/package.json.tmp" "$REPO_ROOT/apps/desktop/package.json"
else
  sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$REPO_ROOT/apps/desktop/package.json" && \
    rm -f "$REPO_ROOT/apps/desktop/package.json.bak"
fi

# 3. Tauri config
echo "  Updating /apps/desktop/src-tauri/tauri.conf.json"
if command -v jq &> /dev/null; then
  jq --arg v "$VERSION" '.version = $v' "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json" > "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json.tmp" && \
    mv "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json.tmp" "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json"
else
  sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json" && \
    rm -f "$REPO_ROOT/apps/desktop/src-tauri/tauri.conf.json.bak"
fi

# 4. Cargo.toml
echo "  Updating /apps/desktop/src-tauri/Cargo.toml"
sed -i.bak "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" "$REPO_ROOT/apps/desktop/src-tauri/Cargo.toml" && \
  rm -f "$REPO_ROOT/apps/desktop/src-tauri/Cargo.toml.bak"

# 5. API pyproject.toml
echo "  Updating /apps/api/pyproject.toml"
sed -i.bak "s/^version = \"[^\"]*\"/version = \"$VERSION\"/" "$REPO_ROOT/apps/api/pyproject.toml" && \
  rm -f "$REPO_ROOT/apps/api/pyproject.toml.bak"

# 6. Shared package.json
echo "  Updating /packages/shared/package.json"
if command -v jq &> /dev/null; then
  jq --arg v "$VERSION" '.version = $v' "$REPO_ROOT/packages/shared/package.json" > "$REPO_ROOT/packages/shared/package.json.tmp" && \
    mv "$REPO_ROOT/packages/shared/package.json.tmp" "$REPO_ROOT/packages/shared/package.json"
else
  sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$REPO_ROOT/packages/shared/package.json" && \
    rm -f "$REPO_ROOT/packages/shared/package.json.bak"
fi

echo "Version sync complete!"
echo ""
echo "Updated files:"
echo "  - /package.json"
echo "  - /apps/desktop/package.json"
echo "  - /apps/desktop/src-tauri/tauri.conf.json"
echo "  - /apps/desktop/src-tauri/Cargo.toml"
echo "  - /apps/api/pyproject.toml"
echo "  - /packages/shared/package.json"
