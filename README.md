# adt-dummy

Internal toolbox CLI for data workflows. The same `dami` binary runs in two modes:

- Local : `dami` proxies commands into a toolbox pod via `kubectl exec`.
- Inside the pod: `dami __remote` executes the real logic directly.

## Prerequisites (local)

- `kubectl` (Homebrew: `brew install kubernetes-cli`)
- Teleport client `tsh` (install from Managed Software Center)
- Python `3.9.12`

Authenticate with Teleport before using `dami`:

```bash
tsh login --proxy=teleport.raiffeisen.ru:443
```

## Quickstart (local)

```bash
# 1) Clone

git clone <repo-url>
cd adt-dummy

# 2) Install
pip install -U pip
pip install -e .

# 3) Verify

dami doctor
```

## Common commands

```bash
# Query Trino (read-only by default)
dami query "SELECT 1"

# Query from file with params
dami query -f query.sql --param TABLE=my_table --param DATE=2024-01-01

# Write output to a local file
dami query "SELECT 1" --format json --output result.json

# Python in the pod
dami py run script.py -- arg1 arg2
echo 'print("hi")' | dami py -

# Network checks
dami net dns example.com
dami net tcp example.com:443
dami net http https://example.com --show-body

# List pods in the current namespace
dami ls

# Switch clusters (tsh kube login)
dami go prod
```

## How it works (short)

- Local mode: `dami` discovers a toolbox pod in the configured namespace and runs
  `dami __remote <command>` inside it. SQL and Python code are sent via stdin.
- In-cluster mode: `ADT_DUMMY_IN_CLUSTER=1` is set in the container. The hidden
  `__remote` group executes the real logic (Trino, Python, net checks).

## Read-only safety for queries

`dami query` is **read-only by default**. DDL/DML is blocked unless you pass
`--allow-write`.

```bash
dami query "DELETE FROM table" --allow-write
```

## Environment variables

All variables are prefixed with `ADT_DUMMY_`. Use `.env.example` as a template.

Local / proxy:
- `ADT_DUMMY_NAMESPACE` (default: `adt-dynamic`)
- `ADT_DUMMY_POD_SELECTOR` (default: `app.kubernetes.io/name=adt-dummy`)
- `ADT_DUMMY_POD` (optional explicit pod name)
- `ADT_DUMMY_KUBECTL_BIN` (default: `kubectl`)
- `ADT_DUMMY_KUBECTL_CONTEXT` (optional)
- `ADT_DUMMY_EXEC_TIMEOUT_SECONDS` (default: `60`)

Cluster switching (tsh):
- `ADT_DUMMY_CLUSTER_PROD`
- `ADT_DUMMY_CLUSTER_PREVIEW`
- `ADT_DUMMY_CLUSTER_TEST`

Trino (in-cluster; can be set locally for testing):
- `ADT_DUMMY_TRINO_HOST`
- `ADT_DUMMY_TRINO_PORT` (default: `443`)
- `ADT_DUMMY_TRINO_HTTP_SCHEME` (default: `https`)
- `ADT_DUMMY_TRINO_USER`
- `ADT_DUMMY_TRINO_PASSWORD`
- `ADT_DUMMY_TRINO_VERIFY` (default: `false`)

Other:
- `ADT_DUMMY_IN_CLUSTER` (set to `1` inside the pod)
- `ADT_DUMMY_KEEP_TMP` (set to `1` to keep Python temp files)
- `ADT_DUMMY_EDITOR` (editor used by `dami py edit`)
