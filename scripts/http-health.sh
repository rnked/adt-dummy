#!/usr/bin/env bash
set -euo pipefail

PORT="${ADT_DUMMY_PORT:-8080}"
HOST="${ADT_DUMMY_HOST:-0.0.0.0}"

usage() {
  cat <<'EOF'
Simple HTTP health server.

Usage:
  http-health [--port PORT] [--host HOST]

Environment:
  ADT_DUMMY_PORT   Port to listen on (default 8080)
  ADT_DUMMY_HOST   Host interface to bind (default 0.0.0.0)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    -h|--help|help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

export PORT HOST

python - <<'PY'
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

port = int(os.environ.get("PORT", "8080"))
host = os.environ.get("HOST", "0.0.0.0")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return  # quiet logs

    def do_GET(self):
        if self.path not in ("/health", "/healthz", "/"):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found\n")
            return
        payload = {
            "status": "ok",
            "path": self.path,
        }
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer((host, port), Handler)
    print(f"Serving health endpoint on http://{host}:{port}", flush=True)
    server.serve_forever()
PY
