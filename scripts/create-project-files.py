#!/usr/bin/env python
"""
create-project-files.py — Project Scaffolding (DESIGN/PLAN/TODO)

Crea automaticamente file di progetto da template:
  - DESIGN_<feature>.md
  - PLAN_<feature>_vX.Y.Z.md
  - docs/TODO.md

Uso:
  python scripts/create-project-files.py \\
    --feature "robust-backup" \\
    --version "3.6.0" \\
    --type design

  python scripts/create-project-files.py \\
    --feature "robust-backup" \\
    --version "3.6.0" \\
    --type plan \\
    --design-file "docs/2 - projects/DESIGN_robust_backup.md"
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEMPLATE_DESIGN = """# DESIGN_{feature}

**Status**: DRAFT → REVIEWED (after user approval)
**Data**: {date}
**Versione Target**: {version}
**Autore**: Copilot (Agent-Design)

## Idea Riassunto (3 righe)

[Descrizione concisa di cosa questa feature fa, perché è necessaria, e quale problema risolve]

## Attori e Concetti Chiave

- **Entity A**: [Descrizione ruolo]
- **Service B**: [Descrizione responsabilità]
- **Value Object C**: [Descrizione semantica]

## Flussi Concettuali (NO codice, solo logica)

[Descrizione testuale di come la feature fluisce attraverso i layer]

## Decisioni Architetturali

- **Layer interessati**: Domain / Application / Infrastructure
- **Dependency direction**: Descrizione
- **Pattern usato**: [Strategy / Observer / Factory / etc.]
- **Breaking Changes**: Sì / No (se sì, descrivere impatto)

## Considerazioni

- **Screen reader impact**: [Descrizione accessibilità]
- **Performance impact**: [Descrizione performance]
- **Data migration required**: Sì / No
- **Backward compatibility**: [Descrizione compat]

## Note per l'Implementazione

[Osservazioni aggiuntive utili durante codifica]
"""

TEMPLATE_PLAN = """# PLAN_{feature}_v{version}

**Status**: DRAFT → READY (after user review)
**Data**: {date}
**Versione**: {version}
**Branch**: feature/{feature_slug}
**Autore**: Copilot (Agent-Plan)

## Executive Summary

- **Tipo**: Nuova feature / Bugfix / Refactor
- **Priorità**: Critica / Alta / Media / Bassa
- **Branch da**: main
- **Commit attesi**: N

## Problema / Obiettivo

[Referenza al DESIGN_*.md completato]

[Descrizione misurabile dell'obiettivo]

## File Coinvolti

```
src/domain/
  - new_entity.py (CREATE)
  - existing_service.py (MODIFY)
src/application/
  - use_case.py (CREATE)
src/infrastructure/
  - adapter.py (MODIFY)
tests/
  - test_new_entity.py (CREATE)
  - test_use_case.py (CREATE)
docs/
  - API.md (MODIFY - add entries)
  - ARCHITECTURE.md (MODIFY - update flow)
```

## Fasi di Implementazione

### Fase 1: [Nome Fase]

**Descrizione**: [Cosa si crea/modifica]

- **File**: src/domain/...
- **Dipendenze**: Nessuna (prima fase)
- **Type hints**: 100% required
- **Logging**: Use domain logger
- **Test**: Unit test required

### Fase 2: [Nome Fase]

**Descrizione**: [Cosa si crea/modifica]

- **File**: src/application/...
- **Dipendenze**: Fase 1 completata
- **Type hints**: 100% required
- **Test**: Integration test required

### Fase 3: [Nome Fase]

**Descrizione**: [Cosa si crea/modifica]

- **File**: src/infrastructure/...
- **Dipendenze**: Fase 1-2 completate

### Fase 4: Documentation & Tests

**Descrizione**: Update API.md, ARCHITECTURE.md, reach 85%+ coverage

- **File**: docs/API.md, docs/ARCHITECTURE.md, tests/
- **Test Coverage Target**: 85% minimum

## Test Plan

- **Unit Tests**: Domain entities (70% of coverage)
- **Integration Tests**: UseCase orchestration (15%)
- **E2E Tests**: Full workflow (15%)
- **Coverage Target**: 85% minimum (85% pre-commit, 90% release)

## Criteri di Completamento

- [x] Tutte le fasi breakken down in chiaro dettaglio
- [x] File coinvolti listati con operazioni
- [x] Dipendenze tra fasi identificate
- [ ] User review completed and READY status assigned

## Note

[Qualsiasi nota su insidie, tech decisions, etc.]
"""

TEMPLATE_TODO = """# TODO: Implementazione PLAN_{feature}_v{version}

**Link Progetto**: [PLAN_{feature}_v{version}](3%20-%20coding%20plans/PLAN_{feature}_v{version}.md)

**Status**: IN PROGRESS

**Versione Target**: {version}

**Branch**: feature/{feature_slug}

## Istruzioni per Copilot

Esegui `/start` per riprendere dall'ultima fase completata.

Ogni fase = esattamente 1 commit atomico.

NON anticipare fasi future. NON accorpare fasi.

## Obiettivo in 3-5 Righe

[Copia da PLAN executive summary]

## File Coinvolti

[Copia da PLAN file list]

## Checklist Implementazione

- [ ] **FASE 1: Domain Layer**
  - [ ] Crea/modifica: src/domain/...
  - [ ] Commit: feat(domain): [descrizione]
  - [ ] Type hints: 100%
  - [ ] Logging: usato

- [ ] **FASE 2: Application Layer**
  - [ ] Crea/modifica: src/application/...
  - [ ] Commit: feat(application): [descrizione]
  - [ ] Type hints: 100%

- [ ] **FASE 3: Infrastructure Layer**
  - [ ] Crea/modifica: src/infrastructure/...
  - [ ] Commit: feat(infrastructure): [descrizione]

- [ ] **FASE 4: Tests & Docs**
  - [ ] Crea tests: tests/...
  - [ ] Modifica: docs/API.md
  - [ ] Modifica: docs/ARCHITECTURE.md
  - [ ] Commit: docs(api): [descrizione]
  - [ ] Coverage: >= 85%

## Test Execution

```bash
pytest -m "not gui" --cov=src --cov-report=term --cov-fail-under=85
```

## Notes

[Work-in-progress notes, blockers, decisions]
"""

def create_design_file(feature: str, version: str) -> bool:
    """Crea DESIGN_<feature>.md."""
    project_dir = Path("docs/2 - projects")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"DESIGN_{feature}.md"
    filepath = project_dir / filename
    
    if filepath.exists():
        logger.warning(f"File already exists: {filepath}")
        return False
    
    content = TEMPLATE_DESIGN.format(
        feature=feature,
        version=version,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✓ Created: {filepath}")
    return True

def create_plan_file(feature: str, version: str) -> bool:
    """Crea PLAN_<feature>_vX.Y.Z.md."""
    plan_dir = Path("docs/3 - coding plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    feature_slug = feature.replace(" ", "-")
    filename = f"PLAN_{feature}_{version}.md"
    filepath = plan_dir / filename
    
    if filepath.exists():
        logger.warning(f"File already exists: {filepath}")
        return False
    
    content = TEMPLATE_PLAN.format(
        feature=feature,
        feature_slug=feature_slug,
        version=version,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✓ Created: {filepath}")
    return True

def create_todo_file(feature: str, version: str) -> bool:
    """Crea docs/TODO.md."""
    filepath = Path("docs/TODO.md")
    
    feature_slug = feature.replace(" ", "-")
    
    content = TEMPLATE_TODO.format(
        feature=feature,
        feature_slug=feature_slug,
        version=version,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"✓ Created: {filepath}")
    return True

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create project files from templates"
    )
    parser.add_argument(
        "--feature",
        type=str,
        required=True,
        help="Feature name (slug format: robust-backup)"
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Target version (e.g., 3.6.0)"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["design", "plan", "todo", "all"],
        required=True,
        help="Type of file(s) to create"
    )
    
    args = parser.parse_args()
    
    # Validate version format
    if not all(part.isdigit() for part in args.version.split('.')):
        logger.error(f"Invalid version format: {args.version}")
        return 1
    
    logger.info(f"Creating project files for '{args.feature}' (v{args.version})...")
    
    files_created = 0
    
    if args.type in ("design", "all"):
        if create_design_file(args.feature, args.version):
            files_created += 1
    
    if args.type in ("plan", "all"):
        if create_plan_file(args.feature, args.version):
            files_created += 1
    
    if args.type in ("todo", "all"):
        if create_todo_file(args.feature, args.version):
            files_created += 1
    
    print("\n" + "="*60)
    if files_created > 0:
        logger.info(f"✅ Created {files_created} file(s) successfully!")
        logger.info("Next steps:")
        logger.info(f"  1. Edit created files")
        logger.info(f"  2. Update status: DRAFT → REVIEWED (for DESIGN)")
        logger.info(f"  3. Update status: DRAFT → READY (for PLAN)")
        logger.info(f"  4. Run `/start` to begin implementation")
        return 0
    else:
        logger.warning("No files created (check if they already exist)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
