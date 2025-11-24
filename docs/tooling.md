# Tooling

Core utilities shipped in the `adt-dummy` image.

## System / Shell
- bash, coreutils, procps (ps, top), less, grep/sed/awk (gawk), vim-tiny

## Networking / Connectivity
- curl, wget
- iproute2 (`ip`, `ss`)
- netcat-openbsd (`nc`)
- bind-tools (`dig`, `nslookup`, `host`)
- telnet

## JSON / CLI formatting
- jq

## Python (3.9.12)
- pip
- Libraries: trino==0.326.0, urllib3==1.26.18, requests==2.31.0, idna==3.7, psycopg2-binary==2.9.9

## Databases (CLI)
- `psql` (PostgreSQL / Greenplum client)
- Helper wrappers: `psql-helper`, `trino-helper`
- Trino CLI (`/usr/local/bin/trino`)

## Misc / Healthcheck
- Java runtime (for Trino CLI)
- `http-health` (simple Python HTTP health server)
