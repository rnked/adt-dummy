# adt-dummy

Containerized toolbox for quick network, DNS, and database diagnostics inside Kubernetes clusters. Designed to be run with `kubectl exec` for ad-hoc troubleshooting.

## What you get
- Shell utilities: bash, coreutils, procps, grep/sed/awk, vim-tiny, less.
- Network/DNS: curl, wget, ip/ss, nc, dig/host/nslookup, telnet.
- JSON/Python: jq, Python 3.9.12 with requests, urllib3, idna, trino, psycopg2-binary.
- Databases: psql client (PostgreSQL/Greenplum), Trino CLI (+ Java runtime).
- Health: lightweight HTTP health server.

## Quick start
Build and run locally (requires BuildKit and Artifactory access for base image and pip):
```bash
DOCKER_BUILDKIT=1 docker build -t adt-dummy \
  --secret id=artifactory_user,src=/path/to/user.txt \
  --secret id=artifactory_password,src=/path/to/password.txt \
  .

docker run --rm -it adt-dummy adt-dummy --help
docker run --rm -p 8080:8080 adt-dummy adt-dummy http-health --port 8080
```

Typical k8s troubleshooting pod:
```bash
kubectl run adt-dummy --restart=Never -it --image=<registry>/adt-dummy:latest -- adt-dummy
kubectl exec -it deploy/your-app -- adt-dummy
```

## Commands
- `adt-dummy` (default): interactive shell, or pass a command to exec.
- `adt-dummy http-health [--port PORT] [--host HOST]`: simple JSON health endpoint.
- `psql-helper`: psql wrapper for PostgreSQL/Greenplum.
- `trino-helper`: Trino CLI wrapper.

## Configuration
Environment variables use the `ADT_DUMMY_` prefix:
- PostgreSQL/Greenplum: `ADT_DUMMY_PGHOST`, `ADT_DUMMY_PGPORT`, `ADT_DUMMY_PGUSER`, `ADT_DUMMY_PGDATABASE`, `ADT_DUMMY_PGPASSWORD`.
- Trino: `ADT_DUMMY_TRINO_HOST`, `ADT_DUMMY_TRINO_PORT`, `ADT_DUMMY_TRINO_USER`, `ADT_DUMMY_TRINO_CATALOG`, `ADT_DUMMY_TRINO_SCHEMA`.
- Health server: `ADT_DUMMY_PORT`, `ADT_DUMMY_HOST`.

More details in `docs/usage.md`, `docs/tooling.md`, and `docs/architecture.md`.
