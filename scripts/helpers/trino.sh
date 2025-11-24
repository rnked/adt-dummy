#!/usr/bin/env bash
set -euo pipefail

HOST="${ADT_DUMMY_TRINO_HOST:-localhost}"
PORT="${ADT_DUMMY_TRINO_PORT:-8080}"
USER="${ADT_DUMMY_TRINO_USER:-trino}"
CATALOG="${ADT_DUMMY_TRINO_CATALOG:-}"
SCHEMA="${ADT_DUMMY_TRINO_SCHEMA:-}"
QUERY=""
FILE=""
EXTRA_OPTS=()

usage() {
  cat <<'EOF'
Trino CLI helper.

Usage:
  trino-helper [--host HOST] [--port PORT] [--user USER] [--catalog CATALOG] [--schema SCHEMA] [--query SQL | --file FILE] [--] [trino args...]

Environment defaults:
  ADT_DUMMY_TRINO_HOST, ADT_DUMMY_TRINO_PORT, ADT_DUMMY_TRINO_USER, ADT_DUMMY_TRINO_CATALOG, ADT_DUMMY_TRINO_SCHEMA
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --user) USER="${2:-}"; shift 2 ;;
    --catalog) CATALOG="${2:-}"; shift 2 ;;
    --schema) SCHEMA="${2:-}"; shift 2 ;;
    --query) QUERY="${2:-}"; shift 2 ;;
    --file) FILE="${2:-}"; shift 2 ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if [[ -n "${QUERY}" && -n "${FILE}" ]]; then
  echo "Choose either --query or --file, not both." >&2
  exit 1
fi

cmd=(trino --server "${HOST}:${PORT}" --user "${USER}")
[[ -n "${CATALOG}" ]] && cmd+=(--catalog "${CATALOG}")
[[ -n "${SCHEMA}" ]] && cmd+=(--schema "${SCHEMA}")
[[ -n "${FILE}" ]] && cmd+=(--file "${FILE}")
[[ -n "${QUERY}" ]] && cmd+=(--execute "${QUERY}")

cmd+=("$@" "${EXTRA_OPTS[@]}")

exec "${cmd[@]}"
