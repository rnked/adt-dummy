# adt-dummy service overview

This project provides a CLI tool (`dami`) used as an internal toolbox. The same binary runs in two contexts:

1) Local laptop: `dami` proxies commands into the toolbox pod via `kubectl exec`.
2) In-cluster: `dami __remote` executes the real logic directly inside the pod.

## How it works

### Local execution (proxy mode)
- `dami` runs on the user's laptop.
- It discovers a toolbox pod by namespace and label selector (or an explicit pod name).
- The command is re-invoked inside the pod as `dami __remote <command>`.
- SQL and Python code are passed over stdin to avoid quoting issues.

### In-cluster execution (remote mode)
- `ADT_DUMMY_IN_CLUSTER=1` is set in the pod.
- `dami __remote` calls the in-cluster implementations directly.
- Trino connectivity uses Basic Authentication via the Python trino client.

## Commands

- `dami doctor`
  - Local: checks kubectl, context, namespace access, pod discovery, and exec permissions.
  - In-cluster: verifies required Trino env vars are present (password is not printed).

- `dami shell`
  - Local: opens an interactive shell in the pod via `kubectl exec`.
  - In-cluster: starts `/bin/bash` if present, else `/bin/sh`.

- `dami query`
  - Reads SQL from argument or file and applies `--param KEY=VALUE` substitutions (`{{KEY}}`).
  - Read-only by default; blocks DDL/DML unless `--allow-write` is used.
  - Supports output formats: table, csv, json.
  - Enforces `--max-rows` to avoid large accidental outputs.

- `dami net dns|tcp|http`
  - DNS uses `socket.getaddrinfo` and prints A/AAAA.
  - TCP performs a connect check with timeout.
  - HTTP uses `requests` and supports headers, data/json payloads, and body output.

- `dami py run|edit|-`
  - Sends Python code to the pod, writes it to `/tmp/adt-dummy/<session-id>/script.py`, and executes it.
  - Cleans up temp files unless `ADT_DUMMY_KEEP_TMP=1`.

## Environment variables

All variables are prefixed with `ADT_DUMMY_`. See `.env.example` for full list and defaults.

Key groups:
- Local proxy: namespace, pod selector, kubectl binary/context, exec timeout.
- Trino: host, port, http scheme, user, password, verify.
- Runtime: `ADT_DUMMY_IN_CLUSTER`, `ADT_DUMMY_KEEP_TMP`, `ADT_DUMMY_EDITOR`.

## Kubernetes deployment

The Helm chart deploys a single toolbox pod. 
Required items:

- Image in Artifactory: `artifactory.raiffeisen.ru/odt-docker/adt-dummy:<tag>`
- Image pull secret: `artifactory-pull-secret`
- Secret: `adt-dummy-secrets` containing `ADT_DUMMY_*`

## Security and safety

- SQL is read-only by default and blocks DDL/DML unless explicitly allowed.
- Credentials are read from env vars and never printed.
- Python temp files are cleaned up unless `ADT_DUMMY_KEEP_TMP=1`.
