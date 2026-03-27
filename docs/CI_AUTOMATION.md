# CI/CD Automazione Locale

## Introduzione

Questo documento descrive come impostare **automazioni locali** per il ciclo di sviluppo, eliminando compiti ripetitivi e garantendo quality gates consistenti prima di ogni commit/release.

**Obiettivo**: Sviluppatore esegue pochi comandi semplici, rest è automatizzato.

---

## 🛠️ Componenti Principali

### 1. Pre-Commit Hook (Git Hook)

**Scopo**: Validare sintassi, type hints, logging prima di ogni commit.

**File**: `.git/hooks/pre-commit` (creato automaticamente da setup)

**Checklist Eseguita**:
```bash
✓ Syntax validation: python -m py_compile
✓ Type hints: mypy src/ --strict --python-version 3.8
✓ Import cycles: pylint --disable=all --enable=cyclic-import
✓ No print statements: grep -r "print(" src/ (must = 0)
✓ Unit tests: pytest -m "not gui" --cov=src (soglia coverage da pyproject.toml)
```

**Configurazione**: Vedi sezione [Setup Pre-Commit](#setup-pre-commit) sotto.

---

### 2. Ci-Validate Script

**Scopo**: Esecuzione pre-commit checklist **on-demand** senza hook.

**File**: `scripts/ci-local-validate.py`

**Esecuzione**:
```bash
python scripts/ci-local-validate.py

# Output:
# ✓ Syntax check passed
# ✓ Type hints: 0 errors
# ✓ Imports: 0 cycles
# ✗ Print statements: 2 found in src/presentation/dialogs.py
# ✗ Unit tests: coverage 82% (target 85%)
#
# Summary: 2 failures. Fix before commit.
```

**Opzioni**:
```bash
python scripts/ci-local-validate.py --skip-tests  # Salta test coverage (veloce)
python scripts/ci-local-validate.py --fix         # Auto-fix import issues
python scripts/ci-local-validate.py --verbose     # Dettagli completi
```

---

### 3. Generate-Changelog Script

**Scopo**: Analizzare commit messages e suggerire CHANGELOG update + semantic versioning.

**File**: `scripts/generate-changelog.py`

**Esecuzione**:
```bash
python scripts/generate-changelog.py

# Output:
# Commits since last tag (v3.5.0):
# - feat(domain): aggiunto ProfileStorageV2
# - fix(ui): corretto null pointer exception
# - docs(api): aggiornato ProfileService
#
# Suggested Version: v3.6.0 (MAJOR.MINOR=+1, PATCH=0)
# Reason: 1x feat: (MINOR bump)
#
# CHANGELOG Draft:
# ## [3.6.0] - 2026-03-17
# ### Added
# - ProfileStorageV2 per backup automatico
# ### Fixed
# - Null pointer exception in UI dialogs
# ### Changed
# - API.md updated with new entries
#
# Confirm? (yes/edit/cancel)
```

**Opzioni**:
```bash
python scripts/generate-changelog.py --force-version 3.6.0  # Override suggerita
python scripts/generate-changelog.py --dry-run              # No write CHANGELOG
python scripts/generate-changelog.py --list-commits         # Mostra commit analizzati
```

---

### 4. Build-Release Script

**Scopo**: Build cx_freeze, versioning, package creation, SHA256 checksum.

**File**: `scripts/build-release.py`

**Esecuzione**:
```bash
python scripts/build-release.py --version 3.6.0

# Output:
# Building solitario v3.6.0...
# ✓ Version check: pyproject.toml updated
# ✓ cx_freeze build: Starting...
#   Compiling src/... ✓
#   Creating exe... ✓
#   Output: dist/solitario-classico/solitario.exe (2.1 MB)
# ✓ Checksum: dist/solitario-classico/solitario.exe.sha256 (16e3f2a...)
# ✓ MANIFEST: dist/solitario-classico/MANIFEST.txt (dependencies listed)
#
# Release Package Ready:
#   dist/solitario-classico/
#     ├── solitario.exe
#     ├── solitario.exe.sha256
#     └── MANIFEST.txt
#
# Next: git tag v3.6.0 && git push origin tags/v3.6.0
```

**Opzioni**:
```bash
python scripts/build-release.py --version 3.6.0 --skip-test  # Non esegui test
python scripts/build-release.py --clean                      # Pulisci build artefatti vecchi
python scripts/build-release.py --output dist/custom/        # Custom output dir
```

---

### 5. Sync-Documentation Script

**Scopo**: Validare sincronizzazione docs (API.md, ARCHITECTURE.md, links).

**File**: `scripts/sync-documentation.py`

**Esecuzione**:
```bash
python scripts/sync-documentation.py

# Output:
# Scanning src/infrastructure/ui/ for public APIs...
# ✓ Found: AudioManager class → API.md entry exists
# ✓ Found: SoundMixer class → API.md entry exists
# ✗ Missing: ProfileService.backup_automatic() → not in API.md
#
# Checking ARCHITECTURE.md...
# ✓ Layer separation: Domain → Application → Infrastructure ✓
# ✓ Data flow diagram sections: present
#
# Link Validation:
# ✓ docs/WORKFLOW.md → docs/CI_AUTOMATION.md (ok)
# ✗ docs/API.md → DESIGN_audio_system.md (file not found)
#
# Summary:
# API entries missing: 1
# Documentation links broken: 1
# Recommendation: Add API.md entry for ProfileService.backup_automatic()
#                Remove broken DESIGN_audio_system.md reference
```

**Opzioni**:
```bash
python scripts/sync-documentation.py --fix-links      # Auto-remove broken references
python scripts/sync-documentation.py --generate-api   # Auto-generate API entries (risky!)
python scripts/sync-documentation.py --check-only     # No write, report only
```

---

### 6. Create-Project-Files Script

**Scopo**: Scaffolding automatico DESIGN/PLAN/TODO dal template.

**File**: `scripts/create-project-files.py`

**Esecuzione**:
```bash
python scripts/create-project-files.py \
  --feature "robust-profile-backup" \
  --version "3.6.0" \
  --type design

# Output:
# Creating DESIGN_robust_profile_backup.md...
# ✓ File created: docs/2 - projects/DESIGN_robust_profile_backup.md
# ✓ Status: DRAFT
# ✓ Template filled with default sections
#
# Next: Edit DESIGN_robust_profile_backup.md → confirm status REVIEWED
```

**Workflow Completo**:
```bash
# Step 1: Create DESIGN
python scripts/create-project-files.py --feature "feature-name" --version "3.6.0" --type design

# [User edits DESIGN_feature-name.md, confirm REVIEWED status]

# Step 2: Create PLAN
python scripts/create-project-files.py \
  --feature "feature-name" \
  --version "3.6.0" \
  --type plan \
  --design-file "docs/2 - projects/DESIGN_feature-name.md"

# [User edits PLAN_feature-name_v3.6.0.md, confirm READY status]

# Step 3: Create TODO (automaticamente da PLAN)
python scripts/create-project-files.py \
  --feature "feature-name" \
  --version "3.6.0" \
  --type todo \
  --plan-file "docs/3 - coding plans/PLAN_feature-name_v3.6.0.md"
# ✓ docs/TODO.md creato e pronto
```

---

## 🔧 Setup Automazione

### Setup Pre-Commit Hook

```bash
# 1. Copia template hook
cp scripts/pre-commit-hook-template.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 2. Verifica:
cat .git/hooks/pre-commit  # mostra contenuto hook
```

**Contenuto Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
# Pre-commit validation hook
# Eseguito automaticamente prima di git commit

set -e  # Exit on first error

echo "Running pre-commit checks..."

# 1. Syntax check
python -m py_compile src/**/*.py || {
    echo "✗ Syntax check failed"
    exit 1
}

# 2. Type hints (mypy)
mypy src/ --strict --python-version 3.8 || {
    echo "✗ Type hints check failed"
    exit 1
}

# 3. Import cycles
pylint src/ --disable=all --enable=cyclic-import || {
    echo "✗ Import cycle check failed"
    exit 1
}

# 4. No print statements
if grep -r "print(" src/ --include="*.py" | grep -v "__main__"; then
    echo "✗ Found print() statements in src/ (not allowed)"
    exit 1
fi

# 5. Unit tests + coverage
pytest -m "not gui" --cov=src --cov-report=term || {
    echo "✗ Test coverage check failed"
    exit 1
}

echo "✓ All pre-commit checks passed"
exit 0
```

### Disable Hook (When Needed)

```bash
# Temporaneamente disabilita hook
git commit --no-verify -m "message"

# Riabilita
# (hook automaticamente eseguito prossimo commit)
```

---

## 📊 Workflow Automazione (Diagramma)

```
Developer esegue: git commit -m "feat(domain): aggiunto X"
    ↓
→ Pre-commit hook si attiva
    → python scripts/ci-local-validate.py (automatico)
      ✓ Syntax, type hints, imports, logging, test coverage
    → Se OK: commit proceed
    → Se FAIL: commit bloccato, mostra errori
    ↓
Developer esegue: python scripts/generate-changelog.py
    → Analizza commit messages da ultimo tag
    → Suggerisce versione (SemVer)
    → Draft CHANGELOG section
    → User confirm: yes/edit/cancel
    ↓
Developer esegue: python scripts/sync-documentation.py
    → Valida API.md, ARCHITECTURE.md, broken links
    → Propone fix se necessario
    ↓
Developer esegue: python scripts/build-release.py --version X.Y.Z
    → Build cx_freeze executable
    → Crea checksum SHA256
    → Genera MANIFEST.txt
    → Output: dist/solitario-classico/solitario.exe ready
```

---

## 🎯 Comandi Frequenti (Copy-Paste Ready)

### Pre-Release Checklist (Eseguire in ordine)

```bash
# 1. Valida codice
python scripts/ci-local-validate.py --verbose

# 2. Suggerisce versione + aggiorna CHANGELOG
python scripts/generate-changelog.py

# 3. Sincronizza documentazione
python scripts/sync-documentation.py --check-only

# 4. Build release
python scripts/build-release.py --version 3.6.0

# 5. Test hand-built executable (manual)
dist/solitario-classico/solitario.exe

# 6. Git tag + push (manual)
git tag v3.6.0
git push origin main
git push origin v3.6.0
```

### Daily Development Loop

```bash
# Durante codifica:
python scripts/ci-local-validate.py --skip-tests  # Veloce check syntax + types

# Prima di commit:
python scripts/ci-local-validate.py              # Full check (pre-commit hook)

# Dopo commit:
python scripts/generate-changelog.py --dry-run   # Preview versioning

# Prima di release:
python scripts/sync-documentation.py             # Ensure docs ready
python scripts/build-release.py --version X.Y.Z  # Build executable
```

---

## 📋 File di Configurazione Necessari

| File | Scopo | Creato da |
|------|-------|----------|
| `pyproject.toml` | Config progetto (versione, entry points) | Manual setup |
| `setup.py` | Config cx_freeze build | Manual setup |
| `pytest.ini` | Config pytest (markers, paths) | Esiste già |
| `mypy.ini` | Config mypy (strict mode) | Esiste già |
| `.github/workflows/` | GitHub Actions CI/CD (opzionale) | Manual |
| `scripts/pre-commit-hook-template.sh` | Template hook | Script template fornito |

---

## 🐛 Troubleshooting

### Pre-commit hook non eseguito

```bash
# Verifica hook esiste e è eseguibile:
ls -la .git/hooks/pre-commit

# Se non esiste, ricrea:
cp scripts/pre-commit-hook-template.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Commit bloccato per coverage basso

```bash
# Opzione 1: Aggiungi test mancanti
pytest -m "not gui" --cov=src --cov-report=html
# Apri htmlcov/index.html per vedere dove coverage è bassa

# Opzione 2: Temporaneamente bypass hook
git commit --no-verify -m "wip: incomplete feature"
```

### Checksum mismatch dopo build

```bash
# Ricrea checksum per file:
sha256sum dist/solitario-classico/solitario.exe > \
  dist/solitario-classico/solitario.exe.sha256

# Verifica:
sha256sum -c dist/solitario-classico/solitario.exe.sha256
```

### CHANGELOG analysis non trovato commit

```bash
# Verifica ultimo tag
git tag --list | sort -V | tail -1

# Se niente tag, initial release:
python scripts/generate-changelog.py --force-version 1.0.0
```

---

## Configurazione AUTOMATION_TOKEN (GitHub Actions)

Il workflow `assistant-commit.yml` utilizza un Personal Access Token (PAT) per
operazioni git automatizzate (push branch, apertura PR). Il token e salvato
come repository secret con il nome `AUTOMATION_TOKEN`.

### Creazione Token

1. Vai su GitHub: Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Crea un nuovo token con queste impostazioni:
   - **Repository access**: Solo questo repository
   - **Permissions richieste**:
     - Contents: Read and write
     - Pull requests: Read and write
     - Metadata: Read-only (selezionato automaticamente)
   - **Expiration**: Scegli una durata adeguata (consigliato: 90 giorni)
3. Copia il token generato

### Aggiunta come Repository Secret

1. Vai su GitHub: Repository > Settings > Secrets and variables > Actions
2. Clicca "New repository secret"
3. Nome: `AUTOMATION_TOKEN`
4. Valore: incolla il token copiato
5. Salva

### Sicurezza

- Non condividere mai il token in chiaro nel codice o nei log
- Il token ha scope limitato al singolo repository
- Ruota il token periodicamente (prima della scadenza)
- Se compromesso, revoca immediatamente da GitHub Settings > Developer settings
- I workflow CI standard (`ci.yml`) non richiedono questo token

### Verifica

Per verificare che il token sia configurato correttamente:

```bash
# Controlla che il secret esista (dalla pagina Secrets del repository)
# Il valore non e mai visibile dopo il salvataggio

# Test manuale: trigger del workflow assistant-commit
# Se il push fallisce con 403, il token manca o ha permessi insufficienti
```

---

## Cross-References

- **Agenti Orchestrazione**: [.github/AGENTS.md](../.github/AGENTS.md)
- **Workflow Dettagliato**: [docs/WORKFLOW.md](WORKFLOW.md)
- **Copilot Instructions**: [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Script Source Code**: [scripts/](../scripts/)

---

**Versione**: 1.2.0 -- 21 Marzo 2026
