# Architecture

`adt-dummy` is a slim Python-based container that layers common troubleshooting tools with small helper scripts.

## Layout
- Base image: `artifactory.raiffeisen.ru/python-community-docker/python:3.9.12-slim-rbru`
- Workdir: `/opt/adt-dummy`
- Scripts: `/opt/adt-dummy/scripts` (entrypoint, health, helpers)
- Symlinks:
  - `/usr/local/bin/adt-dummy` -> entrypoint
  - `/usr/local/bin/http-health` -> health server
  - `/usr/local/bin/psql-helper`, `/usr/local/bin/trino-helper`
  - Trino CLI at `/usr/local/bin/trino`
- Build requires BuildKit with secrets `artifactory_user` / `artifactory_password` for pip indexes.

## Entrypoint flow
- Container ENTRYPOINT: `/opt/adt-dummy/scripts/entrypoint.sh`
- No args: starts interactive bash
- `http-health`: runs a small Python HTTP server for liveness checks
- Any other args: exec the provided command

## Configuration
- Environment variables use the `ADT_DUMMY_` prefix:
  - PostgreSQL/Greenplum: `ADT_DUMMY_PGHOST`, `ADT_DUMMY_PGPORT`, `ADT_DUMMY_PGUSER`, `ADT_DUMMY_PGDATABASE`, `ADT_DUMMY_PGPASSWORD`
  - Trino: `ADT_DUMMY_TRINO_HOST`, `ADT_DUMMY_TRINO_PORT`, `ADT_DUMMY_TRINO_USER`, `ADT_DUMMY_TRINO_CATALOG`, `ADT_DUMMY_TRINO_SCHEMA`
  - Health: `ADT_DUMMY_PORT`, `ADT_DUMMY_HOST`

## Deployment
- Built to run as a disposable diagnostics pod via `kubectl run` or `kubectl exec`.
- A Helm chart scaffold exists in `charts/adt-dummy/` for cluster installs; customize image/tag, resources, and RBAC as needed.
