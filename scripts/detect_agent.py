#!/usr/bin/env python3
"""
detect_agent.py -- Rileva l'agente Copilot appropriato per un task.

Uso:
    python scripts/detect_agent.py "descrizione del task"
    echo "descrizione" | python scripts/detect_agent.py
    python scripts/detect_agent.py --list
    python scripts/detect_agent.py --help

Exit code: 0 se agente rilevato, 1 se AMBIGUOUS o errore.
"""

import argparse
import sys
from typing import Dict, List, Optional, Tuple


# Mappa keyword bilingue (italiano + inglese) per ogni agente
AGENT_KEYWORDS: Dict[str, List[str]] = {
    "Agent-Analyze": [
        # italiano
        "analizza", "studia", "qual è", "come funziona", "trova dove",
        "esplora", "cerca", "verifica cosa", "mostrami", "descrivi",
        "spiega", "capire", "investigare", "esaminare",
        # inglese
        "analyze", "study", "explore", "find where", "how does",
        "discover", "investigate", "examine", "show me",
    ],
    "Agent-Design": [
        # italiano
        "disegna", "progetta", "architetto", "refactor struttura",
        "nuovo pattern", "design", "struttura come", "come dovrebbe",
        "riprogetta", "riorganizza architettura",
        # inglese
        "design", "architect", "refactor structure", "new pattern",
        "architectural", "redesign", "structure",
    ],
    "Agent-Plan": [
        # italiano
        "pianifica", "breaking down", "step by step", "dividi in fasi",
        "roadmap", "crea piano", "quanti step", "fase per fase",
        "pianificazione", "suddividi",
        # inglese
        "plan", "phases", "milestones", "divide into steps",
    ],
    "Agent-Code": [
        # italiano
        "implementa", "codifica", "scrivi il codice", "procedi",
        "inizia a scrivere", "aggiungi funzione", "modifica",
        "correggi il bug", "fix", "sviluppa",
        # inglese
        "implement", "code", "write", "develop", "add feature",
        "modify", "fix bug", "create function",
    ],
    "Agent-Validate": [
        # italiano
        "testa", "valida", "coverage", "quali test mancano",
        "controlla qualità", "verifica test", "esegui test",
        "quanta coverage", "verifica copertura",
        # inglese
        "test", "validate", "quality assurance",
        "check tests", "run tests", "missing tests",
    ],
    "Agent-Docs": [
        # italiano
        "aggiorna docs", "sync docs", "changelog", "aggiorna api",
        "documenta", "sincronizza documentazione", "scrivi api",
        "aggiorna architettura", "aggiorna readme",
        # inglese
        "update docs", "sync docs", "document",
        "api update", "architecture update", "readme",
    ],
    "Agent-Release": [
        # italiano
        "rilascia", "versione", "build release", "crea package",
        "pacchettizza", "nuova versione", "prepara rilascio",
        "incrementa versione", "pubblica",
        # inglese
        "release", "version", "build", "package", "deploy",
        "new version", "publish", "bump version",
    ],
}

# Ordine di priorita in caso di parita di match
AGENT_PRIORITY: List[str] = [
    "Agent-Analyze",
    "Agent-Design",
    "Agent-Plan",
    "Agent-Code",
    "Agent-Validate",
    "Agent-Docs",
    "Agent-Release",
]


def detect_agent(description: str) -> Tuple[str, Dict[str, int]]:
    """Rileva l'agente appropriato dalla descrizione del task.

    Args:
        description: Descrizione testuale del task.

    Returns:
        Tupla (nome_agente, conteggi_match).
        nome_agente e "AMBIGUOUS" se nessuna keyword corrisponde.
        conteggi_match e un dizionario agente -> numero di keyword trovate.
    """
    desc_lower: str = description.lower()
    match_counts: Dict[str, int] = {}

    for agent_name in AGENT_PRIORITY:
        keywords = AGENT_KEYWORDS[agent_name]
        count: int = 0
        for kw in keywords:
            if kw in desc_lower:
                count += 1
        if count > 0:
            match_counts[agent_name] = count

    if not match_counts:
        return "AMBIGUOUS", match_counts

    # Ordina per conteggio decrescente, poi per priorita (ordine in AGENT_PRIORITY)
    best_agent: str = max(
        match_counts.keys(),
        key=lambda a: (match_counts[a], -AGENT_PRIORITY.index(a)),
    )
    return best_agent, match_counts


def format_agent_list() -> str:
    """Formatta la lista di tutti gli agenti con le loro keyword.

    Returns:
        Stringa formattata con agenti e keyword.
    """
    lines: List[str] = []
    lines.append("Agenti disponibili e keyword di rilevamento:")
    lines.append("")
    for agent_name in AGENT_PRIORITY:
        keywords = AGENT_KEYWORDS[agent_name]
        lines.append(f"  {agent_name}:")
        # Raggruppa keyword su righe da max 70 caratteri
        current_line: str = "    "
        for i, kw in enumerate(keywords):
            separator = ", " if i > 0 else ""
            if len(current_line) + len(separator) + len(kw) > 70:
                lines.append(current_line)
                current_line = "    " + kw
            else:
                current_line += separator + kw
        if current_line.strip():
            lines.append(current_line)
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Costruisce il parser degli argomenti CLI.

    Returns:
        Parser configurato.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Rileva l'agente Copilot appropriato per un task "
            "basandosi su keyword nella descrizione."
        ),
        epilog=(
            "Esempi:\n"
            '  python scripts/detect_agent.py "analizza il sistema audio"\n'
            '  python scripts/detect_agent.py "implementa backup profili"\n'
            "  python scripts/detect_agent.py --list\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "description",
        nargs="?",
        default=None,
        help="Descrizione del task da analizzare.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Stampa tutti gli agenti con le loro keyword.",
    )
    return parser


def main() -> int:
    """Entrypoint principale dello script.

    Returns:
        Exit code: 0 se agente rilevato, 1 se AMBIGUOUS o errore.
    """
    parser = build_parser()
    args = parser.parse_args()

    # Modalita --list: stampa agenti e termina
    if args.list:
        sys.stdout.write(format_agent_list() + "\n")
        return 0

    # Recupera descrizione da argomento o stdin
    description: Optional[str] = args.description
    if description is None:
        # Prova a leggere da stdin
        if sys.stdin.isatty():
            sys.stderr.write(
                "ERRORE: nessuna descrizione fornita.\n"
                "Uso: python scripts/detect_agent.py \"descrizione del task\"\n"
            )
            return 1
        description = sys.stdin.readline().strip()

    if not description:
        sys.stderr.write("ERRORE: descrizione vuota.\n")
        return 1

    agent, match_counts = detect_agent(description)

    if agent == "AMBIGUOUS":
        sys.stdout.write("AMBIGUOUS\n")
        return 1

    sys.stdout.write(agent + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
