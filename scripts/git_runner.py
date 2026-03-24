#!/usr/bin/env python3
"""
git_runner.py — Wrapper CLI per operazioni git di Agent-Git.

Sottocomandi disponibili:
  status  — mostra git status e log recente
  commit  — esegue git add . + git commit [+ push opzionale]
  push    — esegue git push su branch specificato
  merge   — esegue git merge --no-ff da source a target
  tag     — propone tag (output solo testuale, non esegue mai)

Output: formato strutturato leggibile da Agent-Git.
Exit code: 0 = successo, 1 = errore o abort.

Uso:
  python scripts/git_runner.py status
  python scripts/git_runner.py commit --message "feat(domain): foo"
  python scripts/git_runner.py commit --message "feat(domain): foo" --push
  python scripts/git_runner.py push --branch main
  python scripts/git_runner.py merge --source feature/x --target main --message "merge: x in main"
  python scripts/git_runner.py tag --name v1.0.0
"""

import argparse
import subprocess
import sys
import traceback
from typing import Optional


_SEP = "\u2500" * 42


def print_report(
    subcommand: str,
    status: str,
    raw_output: str,
    summary_fields: dict[str, str],
    error_message: Optional[str] = None,
) -> None:
    """Stampa un report strutturato nel formato GIT_RUNNER."""
    print(f"GIT_RUNNER: {subcommand} {status}")
    print(_SEP)
    print(raw_output)
    print(_SEP)
    print("RIEPILOGO:")
    for key, value in summary_fields.items():
        print(f"  {key:<10}: {value}")
    if status == "FAIL" and error_message is not None:
        print(f"  {'errore':<10}: {error_message}")


def run_git(args: list[str]) -> tuple[int, str, str]:
    """Esegue git con gli argomenti forniti via subprocess.

    Restituisce (returncode, stdout, stderr).
    Non solleva eccezioni: CalledProcessError gestito internamente.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as exc:  # noqa: BLE001
        return 1, "", str(exc)


# ---------------------------------------------------------------------------
# Sottocomandi
# ---------------------------------------------------------------------------


def cmd_status() -> int:
    """Esegue git status e git log --oneline -10."""
    rc1, out1, err1 = run_git(["status"])
    rc2, out2, err2 = run_git(["log", "--oneline", "-10"])

    raw = f"--- git status ---\n{out1}{err1}\n--- git log --oneline -10 ---\n{out2}{err2}"

    # Estrai branch corrente dal testo di git status
    branch = "sconosciuto"
    for line in out1.splitlines():
        if line.startswith("On branch "):
            branch = line.removeprefix("On branch ").strip()
            break

    if rc1 != 0 or rc2 != 0:
        print_report(
            "STATUS",
            "FAIL",
            raw,
            {},
            error_message="Uno o più comandi git status/log hanno fallito.",
        )
        return 1

    print_report("STATUS", "OK", raw, {"branch": branch})
    return 0


def cmd_commit(message: str, push: bool) -> int:
    """Esegue git add . + git commit [+ push se richiesto]."""

    # 1. Verifica modifiche presenti
    rc, out, err = run_git(["status", "--porcelain"])
    if rc != 0:
        print_report(
            "COMMIT",
            "FAIL",
            f"{out}{err}",
            {},
            error_message="git status fallito.",
        )
        return 1
    if not out.strip():
        print_report(
            "COMMIT",
            "FAIL",
            out,
            {},
            error_message="Nessuna modifica rilevata. Niente da committare.",
        )
        return 1

    # 2. git add .
    rc, out_add, err_add = run_git(["add", "."])
    if rc != 0:
        print_report(
            "COMMIT",
            "FAIL",
            f"{out_add}{err_add}",
            {},
            error_message=err_add.strip() or "git add fallito.",
        )
        return 1

    # 3. Cattura stat staged
    _, out_stat, _ = run_git(["diff", "--staged", "--stat"])
    # Conta righe file (ultima riga è il riepilogo)
    stat_lines = [l for l in out_stat.splitlines() if l.strip()]
    files_count = str(max(0, len(stat_lines) - 1)) if stat_lines else "0"

    # 4. git commit
    rc, out_commit, err_commit = run_git(["commit", "-m", message])
    if rc != 0:
        # Rollback stage
        run_git(["reset"])
        print_report(
            "COMMIT",
            "FAIL",
            f"{out_commit}{err_commit}",
            {},
            error_message=err_commit.strip() or "git commit fallito.",
        )
        return 1

    # Cattura branch corrente
    _, branch_out, _ = run_git(["branch", "--show-current"])
    branch = branch_out.strip() or "sconosciuto"

    summary: dict[str, str] = {
        "branch": branch,
        "messaggio": message[:60],
        "files": files_count,
        "push": "non richiesto",
    }

    raw_output = f"--- git add . ---\n{out_add}\n--- git diff --staged --stat ---\n{out_stat}\n--- git commit ---\n{out_commit}"

    # 5. Push opzionale
    if push:
        rc, out_push, err_push = run_git(["push", "origin", branch])
        raw_output += f"\n--- git push origin {branch} ---\n{out_push}{err_push}"
        if rc != 0:
            summary["push"] = "FALLITO"
            summary["nota"] = "commit locale eseguito, push fallito"
            print_report(
                "COMMIT",
                "FAIL",
                raw_output,
                summary,
                error_message=err_push.strip() or "git push fallito.",
            )
            return 1
        summary["push"] = f"eseguito \u2192 origin/{branch}"

    print_report("COMMIT", "OK", raw_output, summary)
    return 0


def cmd_push(branch: str) -> int:
    """Esegue git push origin <branch>."""

    # 1. Working tree pulito
    rc, out, err = run_git(["status", "--porcelain"])
    if rc != 0:
        print_report(
            "PUSH",
            "FAIL",
            f"{out}{err}",
            {},
            error_message="git status fallito.",
        )
        return 1
    if out.strip():
        print_report(
            "PUSH",
            "FAIL",
            out,
            {},
            error_message="Working tree non pulito. Committa prima.",
        )
        return 1

    # 2. Push
    rc, out_push, err_push = run_git(["push", "origin", branch])
    raw = f"--- git push origin {branch} ---\n{out_push}{err_push}"
    if rc != 0:
        print_report(
            "PUSH",
            "FAIL",
            raw,
            {},
            error_message=err_push.strip() or "git push fallito.",
        )
        return 1

    print_report(
        "PUSH",
        "OK",
        raw,
        {"branch": branch, "remote": f"origin/{branch} aggiornato"},
    )
    return 0


def cmd_merge(source: str, target: str, message: str) -> int:
    """Esegue git merge --no-ff da source a target."""

    # 1. Working tree pulito
    rc, out, err = run_git(["status", "--porcelain"])
    if rc != 0:
        print_report(
            "MERGE",
            "FAIL",
            f"{out}{err}",
            {},
            error_message="git status fallito.",
        )
        return 1
    if out.strip():
        print_report(
            "MERGE",
            "FAIL",
            out,
            {},
            error_message="Working tree non pulito. Impossibile fare merge.",
        )
        return 1

    # 2. Branch iniziale per ripristino
    _, branch_out, _ = run_git(["branch", "--show-current"])
    initial_branch = branch_out.strip() or "sconosciuto"

    # 3. Checkout target
    rc, out_co, err_co = run_git(["checkout", target])
    if rc != 0:
        print_report(
            "MERGE",
            "FAIL",
            f"{out_co}{err_co}",
            {},
            error_message=err_co.strip() or f"git checkout {target} fallito.",
        )
        return 1

    # 4. Merge
    rc, out_merge, err_merge = run_git(["merge", "--no-ff", source, "-m", message])
    raw = f"--- git checkout {target} ---\n{out_co}\n--- git merge --no-ff {source} ---\n{out_merge}{err_merge}"
    if rc != 0:
        # Recovery automatico
        run_git(["merge", "--abort"])
        run_git(["checkout", initial_branch])
        print_report(
            "MERGE",
            "FAIL",
            raw,
            {"nota": f"merge abortito, ripristinato branch {initial_branch}"},
            error_message=err_merge.strip() or "git merge fallito.",
        )
        return 1

    print_report(
        "MERGE",
        "OK",
        raw,
        {
            "source": source,
            "target": target,
            "messaggio": message[:60],
        },
    )
    return 0


def cmd_tag(name: str, push: bool) -> int:
    """Propone un tag senza eseguire nulla."""
    lines = [
        f"# Comandi da eseguire manualmente nel terminale:",
        f"git tag {name}",
    ]
    if push:
        lines.append(f"git push origin {name}")
    raw = "\n".join(lines)

    print(f"GIT_RUNNER: TAG PROPOSTO")
    print(_SEP)
    print(raw)
    print(_SEP)
    print("RIEPILOGO:")
    print(f"  {'tag':<10}: {name}")
    print(f"  {'azione':<10}: proposto \u2014 eseguire manualmente")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Wrapper CLI per operazioni git di Agent-Git."
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # status
    subparsers.add_parser("status", help="Mostra git status e log recente.")

    # commit
    p_commit = subparsers.add_parser("commit", help="Esegui git add + commit.")
    p_commit.add_argument("--message", required=True, help="Messaggio di commit.")
    p_commit.add_argument(
        "--push",
        action="store_true",
        default=False,
        help="Esegui git push dopo il commit.",
    )

    # push
    p_push = subparsers.add_parser("push", help="Esegui git push su branch.")
    p_push.add_argument("--branch", required=True, help="Nome del branch da pushare.")

    # merge
    p_merge = subparsers.add_parser("merge", help="Esegui git merge --no-ff.")
    p_merge.add_argument("--source", required=True, help="Branch sorgente.")
    p_merge.add_argument("--target", required=True, help="Branch target.")
    p_merge.add_argument("--message", required=True, help="Messaggio di merge.")

    # tag
    p_tag = subparsers.add_parser("tag", help="Proponi tag (solo testuale, mai eseguito).")
    p_tag.add_argument("--name", required=True, help="Nome del tag.")
    p_tag.add_argument(
        "--push",
        action="store_true",
        default=False,
        help="Includi git push origin <tag> nel testo proposto.",
    )

    return parser


def main() -> int:
    try:
        parser = build_parser()
        args = parser.parse_args()

        if args.subcommand == "status":
            return cmd_status()
        elif args.subcommand == "commit":
            return cmd_commit(args.message, args.push)
        elif args.subcommand == "push":
            return cmd_push(args.branch)
        elif args.subcommand == "merge":
            return cmd_merge(args.source, args.target, args.message)
        elif args.subcommand == "tag":
            return cmd_tag(args.name, args.push)
        else:
            print(f"Sottocomando sconosciuto: {args.subcommand}", file=sys.stderr)
            return 1

    except Exception:  # noqa: BLE001
        tb = traceback.format_exc()
        print(f"GIT_RUNNER: ERRORE IMPREVISTO")
        print(_SEP)
        print(tb)
        print(_SEP)
        print("RIEPILOGO:")
        print(f"  {'errore':<10}: errore imprevisto \u2014 notifica Agent-Git")
        return 1


if __name__ == "__main__":
    sys.exit(main())
