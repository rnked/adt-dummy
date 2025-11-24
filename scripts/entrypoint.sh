#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'EOF'
ADT Dummy toolbox entrypoint.
Usage:
  adt-dummy                      # start an interactive shell
  adt-dummy http-health [--port PORT] [--host HOST]
  adt-dummy --help

Common tools are available in PATH: curl, wget, dig, nc, psql, trino, jq.
Helper shortcuts: psql-helper, trino-helper, http-health.
EOF
}

cmd="${1:-}"
case "${cmd}" in
  "" )
    exec bash
    ;;
  http-health )
    shift
    exec /opt/adt-dummy/scripts/http-health.sh "$@"
    ;;
  -h|--help|help )
    show_help
    ;;
  * )
    exec "$@"
    ;;
esac
