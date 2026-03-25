"""Test smoke per scripts.git_runner."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from scripts import git_runner


def make_run_git_stub(
    responses: Iterable[tuple[int, str, str]],
) -> Callable[[list[str]], tuple[int, str, str]]:
    iterator = iter(responses)

    def _stub(args: list[str]) -> tuple[int, str, str]:
        return next(iterator)

    return _stub


def test_cmd_tag_reports_ok(capsys) -> None:
    result = git_runner.cmd_tag("v1.2.3", push=True)

    captured = capsys.readouterr().out

    assert result == 0
    assert "GIT_RUNNER: TAG OK" in captured
    assert "git tag v1.2.3" in captured
    assert "git push origin v1.2.3" in captured


def test_cmd_push_fails_when_branch_missing(monkeypatch, capsys) -> None:
    monkeypatch.setattr(git_runner, "local_branch_exists", lambda branch: False)

    result = git_runner.cmd_push("missing-branch")
    captured = capsys.readouterr().out

    assert result == 1
    assert "GIT_RUNNER: PUSH FAIL" in captured
    assert "Branch locale non trovato: missing-branch." in captured


def test_cmd_commit_reports_changelog_modified(monkeypatch, capsys) -> None:
    stub = make_run_git_stub(
        [
            (0, " M CHANGELOG.md\n M foo.py\n", ""),
            (0, "", ""),
            (0, " foo.py | 1 +\n CHANGELOG.md | 2 ++\n 2 files changed, 3 insertions(+)", ""),
            (0, "foo.py\nCHANGELOG.md\n", ""),
            (0, "", ""),
            (0, "[main abc1234] feat(test): sample\n 2 files changed\n", ""),
            (0, "main\n", ""),
        ]
    )
    monkeypatch.setattr(git_runner, "run_git", stub)

    result = git_runner.cmd_commit("feat(test): sample", push=False)
    captured = capsys.readouterr().out

    assert result == 0
    assert "GIT_RUNNER: COMMIT OK" in captured
    assert "changelog" in captured.lower()
    assert "modificato" in captured


def test_cmd_merge_reports_conflicts(monkeypatch, capsys) -> None:
    stub = make_run_git_stub(
        [
            (0, "", ""),
            (0, "feature/test\n", ""),
            (0, "", ""),
            (1, "", "CONFLICT (content): Merge conflict in file.txt"),
            (0, "", ""),
            (0, "", ""),
        ]
    )
    monkeypatch.setattr(git_runner, "run_git", stub)

    result = git_runner.cmd_merge("feature/test", "main", "merge: feature/test in main")
    captured = capsys.readouterr().out

    assert result == 1
    assert "GIT_RUNNER: MERGE FAIL" in captured
    assert "tipo_errore" in captured
    assert "conflitti" in captured