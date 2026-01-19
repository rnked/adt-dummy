"""Process execution helpers."""

import shutil
import subprocess

from adt_dummy.core.errors import AppError


def which_or_error(binary):
    path = shutil.which(binary)
    if not path:
        raise AppError(f"Required executable not found in PATH: {binary}")
    return path


def run_command(args, input_text=None, timeout=None, check=True):
    try:
        result = subprocess.run(
            args,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise AppError(f"Executable not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise AppError(f"Command timed out after {timeout}s: {' '.join(args)}") from exc

    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Command failed"
        raise AppError(message, exit_code=result.returncode)
    return result


def run_interactive(args):
    try:
        return subprocess.call(args)
    except FileNotFoundError as exc:
        raise AppError(f"Executable not found: {args[0]}") from exc
