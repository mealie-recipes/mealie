#!/usr/bin/env bash

set -euo pipefail

HOOK_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$HOOK_DIR/../.." && pwd)"
AGENTS_STATE_DIR="${AGENTS_STATE_DIR:-$REPO_ROOT/.agents/state}"
AGENTS_ARTIFACT_DIR="${AGENTS_ARTIFACT_DIR:-$REPO_ROOT/.agents/artifacts}"
AGENTS_LOG_DIR="$AGENTS_STATE_DIR/logs"
AGENTS_DATA_DIR="$AGENTS_STATE_DIR/data"
MEALIE_API_PORT="${MEALIE_API_PORT:-9000}"
MEALIE_WEB_PORT="${MEALIE_WEB_PORT:-3000}"
MEALIE_API_URL="${MEALIE_API_URL:-http://127.0.0.1:$MEALIE_API_PORT}"
MEALIE_WEB_URL="${MEALIE_WEB_URL:-http://127.0.0.1:$MEALIE_WEB_PORT}"

export PATH="$AGENTS_STATE_DIR/bin:$PATH"

mkdir -p "$AGENTS_STATE_DIR" "$AGENTS_LOG_DIR" "$AGENTS_ARTIFACT_DIR"
cd "$REPO_ROOT"

note() { printf '[agents] %s\n' "$*"; }
fail() { printf '[agents] error: %s\n' "$*" >&2; exit 1; }
require_command() { command -v "$1" >/dev/null 2>&1 || fail "missing command '$1'; run .agents/hooks/setup"; }

pid_file() { printf '%s/%s.pid\n' "$AGENTS_STATE_DIR" "$1"; }

service_pid() {
  local file
  file="$(pid_file "$1")"
  [ -f "$file" ] || return 1
  local pid
  pid="$(cat "$file")"
  case "$pid" in (*[!0-9]*|'') return 1 ;; esac
  kill -0 "$pid" 2>/dev/null || return 1
  printf '%s\n' "$pid"
}

port_is_open() {
  python3 - "$1" <<'PY'
import socket, sys
with socket.socket() as sock:
    sock.settimeout(0.25)
    raise SystemExit(0 if sock.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
}

stop_pid_tree() {
  local pid="$1" child children
  children="$(pgrep -P "$pid" 2>/dev/null || true)"
  kill "$pid" 2>/dev/null || true
  for child in $children; do stop_pid_tree "$child"; done
}

agent_browser() {
  AGENT_BROWSER_SESSION="${AGENT_BROWSER_SESSION:-mealie-agent}" command agent-browser "$@"
}
