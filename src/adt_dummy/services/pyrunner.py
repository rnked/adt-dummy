"""Python runner for in-cluster execution."""

import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from adt_dummy.core import env
from adt_dummy.core.errors import AppError


def run_code(code, args):
    session_id = uuid.uuid4().hex
    base_dir = Path("/tmp/adt-dummy")
    session_dir = base_dir / session_id
    script_path = session_dir / "script.py"

    try:
        session_dir.mkdir(parents=True, exist_ok=True)
        script_path.write_text(code)

        result = subprocess.run(
            [sys.executable, str(script_path)] + list(args),
            text=True,
            capture_output=True,
        )

        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)

        return result.returncode
    except OSError as exc:
        raise AppError(f"Failed to run python script: {exc}") from exc
    finally:
        if not env.get_bool_env("ADT_DUMMY_KEEP_TMP", default=False):
            try:
                shutil.rmtree(session_dir)
            except OSError:
                pass
