from click.testing import CliRunner
import pytest

from adt_dummy.commands.commit import MAX_COMMIT_DIFF_BYTES, _parse_commit_candidates, commit_cmd
from adt_dummy.core.errors import AppError


class DummyResult:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_parse_commit_candidates_strips_code_fences():
    raw = (
        '```json\n["feat: add commit command", "fix: handle empty diff", '
        '"chore: update docs"]\n```'
    )
    parsed = _parse_commit_candidates(raw)

    assert parsed == [
        "feat: add commit command",
        "fix: handle empty diff",
        "chore: update docs",
    ]


def test_parse_commit_candidates_rejects_invalid_prefix():
    with pytest.raises(AppError):
        _parse_commit_candidates(
            '["docs: add readme", "fix: handle empty diff", "chore: update docs"]'
        )


def test_commit_command_commits_selected_message(monkeypatch):
    commands = []

    def fake_run_command(args, input_text=None, timeout=None, check=True):
        commands.append(args)
        if args[:3] == ["git", "diff", "--cached"]:
            return DummyResult(stdout="diff --git a/foo.py b/foo.py\n+print('hi')\n")
        if args[:2] == ["git", "commit"]:
            return DummyResult(stdout="[main 1234567] fix: handle empty diff\n")
        raise AssertionError(args)

    monkeypatch.setattr("adt_dummy.commands.commit.run_command", fake_run_command)
    monkeypatch.setattr(
        "adt_dummy.commands.commit.llm.chat_completion_text",
        lambda messages, model="base", temperature=None, timeout=30: (
            '["feat: add commit command", "fix: handle empty diff", "chore: update docs"]'
        ),
    )

    runner = CliRunner()
    result = runner.invoke(
        commit_cmd, ["--model", "base"], obj={"in_cluster": False}, input="2\n"
    )

    assert result.exit_code == 0
    assert ["git", "commit", "-m", "fix: handle empty diff"] in commands
    assert "1. feat: add commit command" in result.output
    assert "2. fix: handle empty diff" in result.output
    assert "Enter a number from 1 to 3, or press Ctrl+C to cancel." in result.output
    assert "Created commit: fix: handle empty diff" in result.output


def test_commit_command_requires_staged_diff(monkeypatch):
    monkeypatch.setattr(
        "adt_dummy.commands.commit.run_command",
        lambda args, input_text=None, timeout=None, check=True: DummyResult(stdout=""),
    )

    runner = CliRunner()
    result = runner.invoke(commit_cmd, obj={"in_cluster": False})

    assert result.exit_code != 0
    assert isinstance(result.exception, AppError)
    assert (
        str(result.exception)
        == "No staged changes found. Stage changes before running dami commit."
    )


def test_commit_command_rejects_large_staged_diff(monkeypatch):
    large_diff = "a" * (MAX_COMMIT_DIFF_BYTES + 1)

    monkeypatch.setattr(
        "adt_dummy.commands.commit.run_command",
        lambda args, input_text=None, timeout=None, check=True: DummyResult(stdout=large_diff),
    )

    runner = CliRunner()
    result = runner.invoke(commit_cmd, obj={"in_cluster": False})

    assert result.exit_code != 0
    assert isinstance(result.exception, AppError)
    assert (
        str(result.exception)
        == "Staged diff is too large for LLM commit generation: "
        f"{MAX_COMMIT_DIFF_BYTES + 1} bytes > {MAX_COMMIT_DIFF_BYTES} bytes. "
        "Split the changes into smaller commits or stage fewer files."
    )
