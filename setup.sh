#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=false
DOCTOR=false

case "${1:-}" in
  --dry-run) DRY_RUN=true ;;
  --doctor) DOCTOR=true; DRY_RUN=true ;;
  "") ;;
  *) echo "Unknown arg: $1"; exit 2 ;;
esac

cd "$ROOT"

need_cmd() {
  command -v "$1" >/dev/null || {
    echo "❌ missing command: $1"
    exit 1
  }
}

warn() { echo "⚠ $*"; }
ok() { echo "✓ $*"; }

if $DOCTOR; then
  echo "▶ sswg_mvm_1.0 doctor"

  need_cmd python3
  need_cmd pipx

  # Prefer pipx-provided tools (Crostini best practice)
  for tool in pytest ruff black pip-audit bandit; do
    if command -v "$tool" >/dev/null; then
      ok "$tool ($(command -v "$tool"))"
    else
      echo "❌ missing $tool"
      echo "   run: ~/github/pipx-bootstrap.sh"
      exit 1
    fi
  done

  # Check pytest-cov availability (plugin)
  if pytest --help 2>/dev/null | grep -q -- '--cov'; then
    ok "pytest-cov available"
  else
    warn "pytest-cov not available to pytest"
    echo "   fix: pipx inject pytest pytest-cov"
  fi

  # Generated-artifact ignore hints (non-fatal)
  if [[ -d data/outputs || -d data/workflows || -d data/profiling ]]; then
    warn "generated outputs detected under data/ (fine locally, should be gitignored by subpath)"
  fi
  if ls build/*.dot >/dev/null 2>&1; then
    warn "generated .dot files detected under build/ (fine locally, should be gitignored by subpath)"
  fi

  echo "✓ doctor complete"
  exit 0
fi

echo "✓ setup: no actions (tools are managed via pipx; use make preflight)"

