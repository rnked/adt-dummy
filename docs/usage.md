# Usage

`adt-dummy` is the primary entrypoint inside the container. If no args are provided, it drops into an interactive bash shell.

## Entrypoint
```bash
adt-dummy               # interactive shell
adt-dummy --help        # show help
adt-dummy <command>     # run any command directly
```

## HTTP health server
Serves JSON `{"status":"ok"}` on `/`, `/health`, `/healthz`.
```bash
adt-dummy http-health --port 8080 --host 0.0.0.0
```
Environment:
- `ADT_DUMMY_PORT`, default 8080
- `ADT_DUMMY_HOST`, default 0.0.0.0

## PostgreSQL / Greenplum
Wrapper over `psql` for PostgreSQL/Greenplum.
```bash
psql-helper --host db --port 5432 --user app --db appdb --query "select 1"
psql-helper --host gp --file /tmp/query.sql
```
Environment:
- `ADT_DUMMY_PGHOST`, `ADT_DUMMY_PGPORT`, `ADT_DUMMY_PGUSER`, `ADT_DUMMY_PGDATABASE`, `ADT_DUMMY_PGPASSWORD`

## Trino
Wrapper over the Trino CLI.
```bash
trino-helper --host trino.example.com --port 8080 --user analyst --catalog hive --schema default --query "select 1"
```
Environment:
- `ADT_DUMMY_TRINO_HOST`, `ADT_DUMMY_TRINO_PORT`, `ADT_DUMMY_TRINO_USER`, `ADT_DUMMY_TRINO_CATALOG`, `ADT_DUMMY_TRINO_SCHEMA`

## Kubernetes usage
- Launch a throwaway pod: `kubectl run adt-dummy --restart=Never -it --image=<registry>/adt-dummy:latest -- adt-dummy`
- Exec into an existing pod: `kubectl exec -it deploy/your-app -- adt-dummy`

## Notes
- All helper scripts live in `/opt/adt-dummy/scripts` and are on `PATH`.
- Non-prefixed env vars remain supported but `ADT_DUMMY_` is preferred for clarity and to avoid collisions.
