#!/usr/bin/env python3
"""
validate_gates.py -- Valida il frontmatter YAML dei documenti di progetto.

Controlla che i file DESIGN_*.md, PLAN_*.md e TODO.md abbiano
un frontmatter YAML valido con i campi obbligatori.

Uso:
    python scripts/validate_gates.py --check-design docs/2\ -\ projects/DESIGN_audio.md
    python scripts/validate_gates.py --check-plan docs/2\ -\ projects/PLAN_audio.md
    python scripts/validate_gates.py --check-all
    python scripts/validate_gates.py --help

Exit code: 0 se valido o warning, 1 se errori bloccanti.
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Tentativo import yaml; se mancante, parsing minimale
try:
    import yaml
    HAS_YAML: bool = True
except ImportError:
    HAS_YAML = False


# Campi obbligatori per tipo di documento
REQUIRED_FIELDS: Dict[str, List[str]] = {
    "design": ["type", "feature", "status", "agent"],
    "plan": ["type", "feature", "status", "agent"],
    "todo": ["type", "feature", "status"],
}

# Valori ammessi per campi chiave
VALID_STATUS: List[str] = ["DRAFT", "IN REVIEW", "REVIEWED", "FROZEN",
                           "READY", "IN PROGRESS", "COMPLETED", "DONE",
                           "BLOCKED"]
VALID_TYPE: List[str] = ["design", "plan", "todo"]


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Estrae e parsa il frontmatter YAML da un file Markdown.

    Il frontmatter deve essere delimitato da linee '---' all'inizio del file.

    Args:
        content: Contenuto completo del file.

    Returns:
        Dizionario con i campi del frontmatter, o None se non presente.
    """
    lines: List[str] = content.split("\n")

    # Cerca prima riga '---'
    start_idx: int = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            start_idx = i
            break
        # Ignora righe vuote prima del frontmatter
        if stripped:
            return None

    if start_idx < 0:
        return None

    # Cerca seconda riga '---'
    end_idx: int = -1
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx < 0:
        return None

    yaml_text: str = "\n".join(lines[start_idx + 1:end_idx])
    if not yaml_text.strip():
        return None

    if HAS_YAML:
        try:
            data = yaml.safe_load(yaml_text)
            if isinstance(data, dict):
                return data  # type: ignore[return-value]
            return None
        except yaml.YAMLError:
            return None
    else:
        # Parsing minimale key: value
        data_min: Dict[str, str] = {}
        for line in yaml_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                data_min[key.strip()] = value.strip()
        return data_min if data_min else None


def validate_document(
    filepath: str,
    doc_type: str,
) -> Tuple[int, List[str]]:
    """Valida un singolo documento di progetto.

    Args:
        filepath: Percorso al file Markdown da validare.
        doc_type: Tipo di documento ('design', 'plan', 'todo').

    Returns:
        Tupla (exit_code, lista_messaggi).
        exit_code: 0=ok o warning, 1=errore bloccante.
    """
    messages: List[str] = []

    if not os.path.isfile(filepath):
        messages.append(f"ERRORE: file non trovato: {filepath}")
        return 1, messages

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        messages.append(f"ERRORE: impossibile leggere {filepath}: {exc}")
        return 1, messages

    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        messages.append(
            f"GATE WARN: {os.path.basename(filepath)}\n"
            f"           Frontmatter YAML assente (formato legacy pre v1.2.0).\n"
            f"           Aggiungi frontmatter per abilitare gate automatici."
        )
        return 0, messages

    # Verifica tipo
    fm_type: str = str(frontmatter.get("type", "")).lower()
    if fm_type != doc_type:
        messages.append(
            f"ERRORE: type '{fm_type}' non corrisponde al tipo atteso "
            f"'{doc_type}' in {filepath}"
        )
        return 1, messages

    # Verifica campi obbligatori
    required = REQUIRED_FIELDS.get(doc_type, [])
    missing: List[str] = []
    for field in required:
        if field not in frontmatter or not frontmatter[field]:
            missing.append(field)

    if missing:
        messages.append(
            f"ERRORE: campi mancanti in {filepath}: {', '.join(missing)}"
        )
        return 1, messages

    # Verifica status valido
    fm_status: str = str(frontmatter.get("status", "")).upper()
    if fm_status and fm_status not in VALID_STATUS:
        messages.append(
            f"GATE WARN: {os.path.basename(filepath)}  "
            f"status '{fm_status}' non standard."
        )
        return 0, messages

    messages.append(f"OK: {filepath} valido ({doc_type})")
    return 0, messages


def detect_doc_type(filepath: str) -> Optional[str]:
    """Rileva il tipo di documento dal nome del file.

    Args:
        filepath: Percorso al file.

    Returns:
        'design', 'plan', 'todo' o None se non riconosciuto.
    """
    basename: str = os.path.basename(filepath).upper()
    if basename.startswith("DESIGN"):
        return "design"
    if basename.startswith("PLAN"):
        return "plan"
    if "TODO" in basename:
        return "todo"
    return None


def check_all(directory: str) -> Tuple[int, List[str]]:
    """Valida tutti i documenti DESIGN/PLAN/TODO in una directory.

    Args:
        directory: Percorso alla directory da scansionare.

    Returns:
        Tupla (exit_code_max, tutti_messaggi).
    """
    all_messages: List[str] = []
    max_code: int = 0

    if not os.path.isdir(directory):
        all_messages.append(f"ERRORE: directory non trovata: {directory}")
        return 1, all_messages

    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".md"):
            continue
        doc_type = detect_doc_type(filename)
        if doc_type is None:
            continue
        filepath = os.path.join(directory, filename)
        code, msgs = validate_document(filepath, doc_type)
        all_messages.extend(msgs)
        max_code = max(max_code, code)

    if not all_messages:
        all_messages.append(
            f"INFO: nessun documento DESIGN/PLAN/TODO trovato in {directory}"
        )

    return max_code, all_messages


def build_parser() -> argparse.ArgumentParser:
    """Costruisce il parser degli argomenti CLI.

    Returns:
        Parser configurato.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Valida il frontmatter YAML dei documenti DESIGN, PLAN e TODO."
        ),
        epilog=(
            "Exit codes:\n"
            "  0 = tutti i documenti validi o solo warning\n"
            "  1 = errori bloccanti trovati\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check-design",
        metavar="FILE",
        help="Valida un documento DESIGN_*.md.",
    )
    parser.add_argument(
        "--check-plan",
        metavar="FILE",
        help="Valida un documento PLAN_*.md.",
    )
    parser.add_argument(
        "--check-todo",
        metavar="FILE",
        help="Valida un documento TODO*.md.",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help=(
            "Valida tutti i DESIGN/PLAN/TODO nelle directory "
            "docs/2 - projects/ e docs/3 - coding plans/."
        ),
    )
    return parser


def main() -> int:
    """Entrypoint principale dello script.

    Returns:
        Exit code: 0=ok/warning, 1=errore.
    """
    parser = build_parser()
    args = parser.parse_args()

    # Nessuna opzione specificata
    if not any([args.check_design, args.check_plan,
                args.check_todo, args.check_all]):
        parser.print_help()
        return 1

    max_code: int = 0

    if args.check_design:
        code, msgs = validate_document(args.check_design, "design")
        for msg in msgs:
            sys.stdout.write(msg + "\n")
        max_code = max(max_code, code)

    if args.check_plan:
        code, msgs = validate_document(args.check_plan, "plan")
        for msg in msgs:
            sys.stdout.write(msg + "\n")
        max_code = max(max_code, code)

    if args.check_todo:
        code, msgs = validate_document(args.check_todo, "todo")
        for msg in msgs:
            sys.stdout.write(msg + "\n")
        max_code = max(max_code, code)

    if args.check_all:
        dirs_to_scan = [
            "docs/2 - projects",
            "docs/3 - coding plans",
        ]
        for scan_dir in dirs_to_scan:
            code, msgs = check_all(scan_dir)
            for msg in msgs:
                sys.stdout.write(msg + "\n")
            max_code = max(max_code, code)

    return max_code


if __name__ == "__main__":
    sys.exit(main())
