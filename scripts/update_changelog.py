#!/usr/bin/env python3
"""
Script per aggiungere voci a FRAMEWORK_CHANGELOG.md
"""
import re

file_path = r".github/FRAMEWORK_CHANGELOG.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# MOD-4a: Aggiungi git-merge.prompt.md a Fixed
fixed_insert = """- `git-merge.prompt.md`: fix frontmatter — delimitatori corretti
  da `***` a `---`. Model gpt-5-mini e tools ora parsabili da VS Code.
"""

# Sostituisci la riga "### Fixed" + blank + prima voce con Fixed + blank + nuova voce + prima voce
content = re.sub(
    r"(### Fixed)\n\n(- `Agent-Git\.md`: rimossa)",
    r"\1\n\n" + fixed_insert + r"\2",
    content
)

# MOD-4b: Aggiungi Agent-Release a Changed
changed_insert = """- `Agent-Release.md`: passo 4 "CREATE GIT TAG" aggiornato per
  delegare ad Agent-Git (OP-5) invece di proporre testo generico.
  Aggiunte Regole Operative coerenti con git policy centralizzata.
  Aggiunto riferimento a git-execution.skill.md.
"""

# Trova la riga "- `Agent-Orchestrator.md`: ripristinato" nel contesto di "### Changed"
# e inserisci prima di essa
content = re.sub(
    r"(### Changed\n.*?)^(- `Agent-Orchestrator\.md`: ripristinato)",
    r"\1" + changed_insert + r"\2",
    content,
    flags=re.MULTILINE | re.DOTALL
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ FRAMEWORK_CHANGELOG.md aggiornato")
print("  - MOD-4a: git-merge.prompt.md aggiunto a Fixed")
print("  - MOD-4b: Agent-Release.md aggiunto a Changed")
