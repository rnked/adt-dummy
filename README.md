# adt-dummy

Internal toolbox CLI for querying Trino and running quick diagnostics.

## Usage

```bash
dami doctor
dami shell

dami query "SELECT 1"
dami query -f query.sql --param TABLE=foo --format json --max-rows 200

dami net dns example.com
dami net tcp example.com:443
dami net http https://example.com --method GET --show-body

dami py run script.py -- arg1 arg2
dami py - -- arg1 arg2
dami py edit -- arg1 arg2
```

## Environment variables

All variables are prefixed with `ADT_DUMMY_`.

Local/proxy:
- `ADT_DUMMY_NAMESPACE` (default: `adt-dynamic`)
- `ADT_DUMMY_POD_SELECTOR` (default: `app.kubernetes.io/name=adt-dummy`)
- `ADT_DUMMY_POD` (optional)
- `ADT_DUMMY_KUBECTL_BIN` (default: `kubectl`)
- `ADT_DUMMY_KUBECTL_CONTEXT` (optional)
- `ADT_DUMMY_EXEC_TIMEOUT_SECONDS` (default: `60`)

Trino:
- `ADT_DUMMY_TRINO_HOST`
- `ADT_DUMMY_TRINO_PORT` (default: `443`)
- `ADT_DUMMY_TRINO_HTTP_SCHEME` (default: `https`)
- `ADT_DUMMY_TRINO_USER`
- `ADT_DUMMY_TRINO_PASSWORD`
- `ADT_DUMMY_TRINO_VERIFY` (default: `false`)

Other:
- `ADT_DUMMY_IN_CLUSTER` (set to `1` inside the toolbox pod)
- `ADT_DUMMY_KEEP_TMP` (set to `1` to keep Python temp files)
- `ADT_DUMMY_EDITOR` (override editor used by `dami py edit`)
