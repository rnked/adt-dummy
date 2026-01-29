# adt-dummy: quickstart for data scientists

This guide assumes you have a working Python 3.9 environment and a kubectl config that can access
our cluster. You do not need to know Kubernetes internals; follow the steps.

## 1) Clone the repo

```bash
git clone <repo-url>
cd adt-dummy
```

## 2) Create a Python environment and install the CLI

```bash
python3.9 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e .
```

After this, the `dami` command is available in your shell.

## 3) Configure local environment variables

We do not auto-load `.env` files. If you want to use `.env.example`, copy it and `source` it.

```bash
cp .env.example .env
# edit .env with your values
set -a
. ./.env
set +a
```

Minimum local variables for proxy mode:
- `ADT_DUMMY_NAMESPACE`
- `ADT_DUMMY_POD_SELECTOR` (default is fine in most cases)
- `ADT_DUMMY_KUBECTL_CONTEXT` (only if you use multiple contexts)

## 4) Verify access to the toolbox pod

```bash
dami doctor
```

Expected output (example):
- Mode: local
- Selected pod: adt-dummy-...

If this fails, ask DevOps for:
- kubeconfig access to the namespace
- RBAC permission for `pods/exec`
- the toolbox deployment is running

## 5) Run queries (read-only by default)

### Simple query
```bash
dami query "SELECT 1"
```

### Query from file
```bash
dami query -f query.sql
```

### Parameter substitution
In your SQL, use `{{KEY}}` placeholders:
```sql
SELECT * FROM {{TABLE}} WHERE dt = '{{DATE}}'
```

Then run:
```bash
dami query -f query.sql --param TABLE=some_table --param DATE=2024-01-01
```

### Output formats
```bash
dami query "SELECT 1" --format json
```

### Read-only safety
DDL/DML is blocked unless you explicitly allow it:
```bash
dami query "DELETE FROM x" --allow-write
```

## 6) Run Python code inside the toolbox pod

### Run a local script file
```bash
dami py run script.py -- arg1 arg2
```

### Run code from stdin
```bash
cat script.py | dami py - -- arg1 arg2
```

### Edit a temporary script and run it
```bash
dami py edit -- arg1 arg2
```

You can set the editor with `ADT_DUMMY_EDITOR` (default: `vi`).

## 7) Network checks

```bash
dami net dns example.com
dami net tcp example.com:443
dami net http https://example.com --show-body
```

## Troubleshooting

- `dami doctor` fails locally: check kubectl context and permissions.
- `dami query` fails in-cluster: DevOps should verify Trino env vars in the secret.
- `ImagePullBackOff`: image tag or pull secret is wrong.

## What DevOps is responsible for

- Deploying the Helm chart to the cluster.
- Creating Kubernetes secrets:
  - `artifactory-pull-secret`
  - `adt-dummy-secrets` with `ADT_DUMMY_TRINO_*`
- Ensuring users can `kubectl exec` into the toolbox pod.
