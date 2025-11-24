#!/usr/bin/env bash
set -euo pipefail

# Unified PostgreSQL/Greenplum helper (psql)
# Prefers ADT_DUMMY_ variables, falls back to standard PG vars.
HOST="${ADT_DUMMY_PGHOST:-localhost}"
PORT="${ADT_DUMMY_PGPORT:-5432}"
USER="${ADT_DUMMY_PGUSER:-postgres}"
DB="${ADT_DUMMY_PGDATABASE:-postgres}"
PASSWORD="${ADT_DUMMY_PGPASSWORD:-}"
QUERY=""
FILE=""

usage() {
  cat <<'EOF'
psql helper for PostgreSQL/Greenplum.

Usage:
  psql-helper [--host HOST] [--port PORT] [--user USER] [--db DATABASE] [--password PASS] [--query SQL | --file FILE] [--] [psql args...]

Environment defaults (preferred first):
  ADT_DUMMY_PGHOST, ADT_DUMMY_PGPORT, ADT_DUMMY_PGUSER, ADT_DUMMY_PGDATABASE, ADT_DUMMY_PGPASSWORD
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --user) USER="${2:-}"; shift 2 ;;
    --db|--database) DB="${2:-}"; shift 2 ;;
    --password) PASSWORD="${2:-}"; shift 2 ;;
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

export PGPASSWORD="${PASSWORD}"

cmd=(psql -h "${HOST}" -p "${PORT}" -U "${USER}" -d "${DB}")
[[ -n "${FILE}" ]] && cmd+=(-f "${FILE}")
[[ -n "${QUERY}" ]] && cmd+=(-c "${QUERY}")

cmd+=("$@")

exec "${cmd[@]}"
