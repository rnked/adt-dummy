"""Commit command."""

import json
import re

import click

from adt_dummy.core.errors import AppError
from adt_dummy.core.proc import run_command
from adt_dummy.services import llm

MAX_COMMIT_DIFF_BYTES = 50 * 1024
COMMIT_MESSAGE_RE = re.compile(r"^(feat|fix|chore):\s+\S.*$")
COMMIT_SYSTEM_PROMPT = """You generate git commit messages from staged diffs.

Rules:
- Return exactly 3 options.
- Return English only.
- Every option must start with one of: feat:, fix:, chore:
- Use a short imperative subject line.
- Keep the message specific to the diff.
- Do not use markdown.
- Return JSON only as an array of strings.
"""


def _ensure_local(ctx):
    if ctx.obj.get("in_cluster"):
        raise AppError("dami commit is local-only.")


def _staged_diff():
    result = run_command(
        ["git", "diff", "--cached", "--no-ext-diff", "--unified=0", "--no-color"]
    )
    diff_text = result.stdout.strip()
    if not diff_text:
        raise AppError("No staged changes found. Stage changes before running dami commit.")

    diff_size = len(diff_text.encode("utf-8"))
    if diff_size > MAX_COMMIT_DIFF_BYTES:
        raise AppError(
            "Staged diff is too large for LLM commit generation: "
            f"{diff_size} bytes > {MAX_COMMIT_DIFF_BYTES} bytes. "
            "Split the changes into smaller commits or stage fewer files."
        )
    return diff_text


def _choose_commit(candidates):
    for index, candidate in enumerate(candidates, start=1):
        click.echo(f"{index}. {candidate}")
    click.echo("Enter a number from 1 to 3, or press 0 to cancel.")

    choice = click.prompt("Choose commit", type=click.IntRange(0, len(candidates)))
    if choice == 0:
        return None
    return candidates[choice - 1]


def _strip_code_fences(text):
    text = text.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _parse_commit_candidates(text):
    normalized = _strip_code_fences(text)

    try:
        payload = json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise AppError("AI Gateway returned invalid JSON for commit options") from exc

    if not isinstance(payload, list) or len(payload) != 3:
        raise AppError("AI Gateway must return exactly 3 commit options")

    candidates = []
    for item in payload:
        if not isinstance(item, str):
            raise AppError("AI Gateway returned a non-string commit option")
        candidate = item.strip()
        if not COMMIT_MESSAGE_RE.match(candidate):
            raise AppError(
                "AI Gateway returned an invalid commit format. Expected feat:/fix:/chore:"
            )
        candidates.append(candidate)

    return candidates


def _generate_commit_candidates(diff_text, model):
    content = llm.chat_completion_text(
        messages=[
            {"role": "system", "content": COMMIT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Generate 3 commit message options for this staged diff:\n\n"
                + diff_text,
            },
        ],
        model=model,
        temperature=0.2,
    )
    return _parse_commit_candidates(content)


@click.command(
    name="commit",
    help="Generate commit messages from the staged diff and apply the selected one.",
)
@click.option("--model", default=llm.DEFAULT_MODEL, show_default=True, help="LLM model.")
@click.pass_context
def commit_cmd(ctx, model):
    _ensure_local(ctx)
    diff_text = _staged_diff()
    candidates = _generate_commit_candidates(diff_text, model=model)
    selected_commit = _choose_commit(candidates)
    if selected_commit is None:
        click.echo("Commit cancelled.")
        return
    run_command(["git", "commit", "-m", selected_commit])
    click.echo(f"Created commit: {selected_commit}")
