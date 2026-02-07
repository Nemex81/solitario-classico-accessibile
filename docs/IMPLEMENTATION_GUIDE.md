# 🚀 GUIDA OPERATIVA IMPLEMENTAZIONE - Refactoring Engine

> **Documento esecutivo per Copilot Agent**  
> **Obiettivo**: Implementare 13 commit per migrare `scr/` → `src/`  
> **Riferimento Piano Completo**: [REFACTORING_PLAN.md](./REFACTORING_PLAN.md)

---

## 🎯 COMMIT #1 - MIGRATE DECK MODELS (PRIORITÀ MASSIMA)

### Obiettivo
Portare `scr/decks.py` → `src/domain/models/deck.py` con tutti i fix v1.3.3

### File da Creare
```
src/domain/models/deck.py (NUOVO)
```

### Istruzioni Precise

1. **Copia il file source** da `scr/decks.py` (SHA: `cb52fbfa6eae546b2e6bad56fee32d86f5d0042a`)

2. **Modifica gli import**:
   ```python
   # PRIMA (legacy)
   from scr.cards import Card
   from my_lib.dialog_box import DialogBox
   
   # DOPO (nuovo)
   from src.domain.models.card import Card
   # Rimuovere completamente import my_lib
   ```

3. **Mantieni TUTTE le classi**:
   - `ProtoDeck` (classe base)
   - `FrenchDeck` (52 carte)
   - `NeapolitanDeck` (40 carte)

4. **CRITICO - Metodo is_king()**:
   ```python
   def is_king(self, card: Card) -> bool:
       """Verifica se una carta è un Re per questo mazzo.
       
       Args:
           card: La carta da verificare
           
       Returns:
           True se la carta è un Re (13 francese, 10 napoletano)
       """
       return card.get_value == self.FIGURE_VALUES.get("Re")
   ```
   **Questo metodo risolve bug #28 e #29**

5. **Aggiungi type hints completi**:
   ```python
   from typing import List, Optional
   from dataclasses import dataclass
   ```

6. **Aggiungi docstrings** (Google style) per:
   - Ogni classe
   - Ogni metodo pubblico
   - Parametri e return values

### Testing Obbligatorio

Crea `tests/unit/domain/models/test_deck.py`:

```python
import pytest
from src.domain.models.deck import FrenchDeck, NeapolitanDeck, ProtoDeck
from src.domain.models.card import Card


class TestFrenchDeck:
    def test_creates_52_cards(self):
        deck = FrenchDeck()
        deck.crea()
        assert len(deck.cards) == 52
    
    def test_is_king_value_13(self):
        deck = FrenchDeck()
        deck.crea()
        # Trova un Re (valore 13)
        king = next(c for c in deck.cards if c.get_value == 13)
        assert deck.is_king(king) is True
    
    def test_is_not_king_queen(self):
        deck = FrenchDeck()
        deck.crea()
        # Trova una Regina (valore 12)
        queen = next(c for c in deck.cards if c.get_value == 12)
        assert deck.is_king(queen) is False


class TestNeapolitanDeck:
    def test_creates_40_cards(self):
        deck = NeapolitanDeck()
        deck.crea()
        assert len(deck.cards) == 40
    
    def test_is_king_value_10(self):
        """CRITICO: Re napoletano ha valore 10 (fix #28)"""
        deck = NeapolitanDeck()
        deck.crea()
        # Trova un Re (valore 10)
        king = next(c for c in deck.cards if c.get_value == 10)
        assert deck.is_king(king) is True
    
    def test_is_not_king_cavallo(self):
        """Cavallo (9) non è Re"""
        deck = NeapolitanDeck()
        deck.crea()
        cavallo = next(c for c in deck.cards if c.get_value == 9)
        assert deck.is_king(cavallo) is False
    
    def test_no_8_9_10_numeric_cards(self):
        """Napoletano ha solo 1-7, Regina(8), Cavallo(9), Re(10)"""
        deck = NeapolitanDeck()
        assert 8 not in deck.VALUES
        assert 9 not in deck.VALUES
        assert 10 not in deck.VALUES


class TestDeckInterface:
    """Test API comune ProtoDeck"""
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_get_total_cards(self, deck_class):
        deck = deck_class()
        total = deck.get_total_cards()
        assert total in [52, 40]
    
    @pytest.mark.parametrize("deck_class", [FrenchDeck, NeapolitanDeck])
    def test_mischia_randomizes(self, deck_class):
        deck = deck_class()
        deck.crea()
        original = deck.cards.copy()
        deck.mischia()
        # Probabilità bassissima che rimangano identiche
        assert deck.cards != original
```

### Commit Message Template

```
feat(domain): Migrate deck models from scr/ with is_king() fix

- Add src/domain/models/deck.py with ProtoDeck base class
- Implement FrenchDeck (52 cards) and NeapolitanDeck (40 cards)
- Include is_king() method for correct King validation
  * French King value: 13
  * Neapolitan King value: 10
- Add full type hints and Google-style docstrings
- Remove legacy my_lib dependencies
- Add comprehensive test suite (14 tests)

Migrated from: scr/decks.py (SHA: cb52fbf)
Fixes: #28, #29 (v1.3.3 Re napoletano hotfix)
Testing: pytest tests/unit/domain/models/test_deck.py -v
```

### Verifiche Pre-Commit

```bash
# 1. Test passano
pytest tests/unit/domain/models/test_deck.py -v

# 2. Type checking
mypy src/domain/models/deck.py --strict

# 3. Nessun import scr/
grep -r "from scr" src/domain/models/deck.py  # deve essere vuoto
grep -r "import scr" src/domain/models/deck.py  # deve essere vuoto

# 4. Coverage >80%
pytest tests/unit/domain/models/test_deck.py --cov=src/domain/models/deck --cov-report=term-missing
```

### Definition of Done

- [x] File `src/domain/models/deck.py` creato
- [x] Tutte e 3 le classi migrate (ProtoDeck, FrenchDeck, NeapolitanDeck)
- [x] Metodo `is_king()` incluso e funzionante
- [x] Import aggiornati (no `scr/`, no `my_lib`)
- [x] Type hints completi (List, Optional, etc.)
- [x] Docstrings Google-style per tutte le classi/metodi
- [x] Test suite con 14+ test creata
- [x] Tutti i test passano (100%)
- [x] `mypy --strict` passa
- [x] Coverage >80%
- [x] Commit message segue template
- [x] Branch merged in `refactoring-engine`

---

## 📊 SEQUENZA COMMIT (Overview)

| # | Fase | File Target | Status |
|---|------|-------------|--------|
| **1** | Domain Models | `deck.py` | ⏳ **CORRENTE** |
| 2 | Domain Models | `table.py` | ⏸️ Pending |
| 3 | Domain Rules | `solitaire_rules.py` | ⏸️ Pending |
| 4 | Domain Services | `game_service.py` | ⏸️ Pending |
| 5 | Infrastructure | `screen_reader.py` | ⏸️ Pending |
| 6 | Infrastructure | `menu.py` | ⏸️ Pending |
| 7 | Application | `input_handler.py` | ⏸️ Pending |
| 8 | Application | `game_settings.py` | ⏸️ Pending |
| 9 | Presentation | `game_formatter.py` | ⏸️ Pending |
| 10 | Integration | `test.py` | ⏸️ Pending |
| 11 | Integration | `di_container.py` | ⏸️ Pending |
| 12 | Testing | `integration tests` | ⏸️ Pending |
| 13 | Documentation | `MIGRATION_GUIDE.md` | ⏸️ Pending |

**Dopo Commit #1**: Creare issue per Commit #2

---

## 🔧 Template Issue per Copilot

```markdown
## [FASE 1 - Commit #1] Migrate Deck Models to src/domain

**Obiettivo**: Portare `scr/decks.py` → `src/domain/models/deck.py` con fix v1.3.3

### File da Creare
- `src/domain/models/deck.py` (NUOVO)
- `tests/unit/domain/models/test_deck.py` (NUOVO)

### Implementazione
Vedi [IMPLEMENTATION_GUIDE.md](./docs/IMPLEMENTATION_GUIDE.md) sezione "COMMIT #1"

### Checklist
- [ ] Copia `ProtoDeck`, `FrenchDeck`, `NeapolitanDeck` da scr/decks.py
- [ ] Includi metodo `is_king()` (CRITICO per #28, #29)
- [ ] Aggiorna import: `from src.domain.models.card import Card`
- [ ] Rimuovi dipendenze `my_lib`
- [ ] Type hints completi
- [ ] Docstrings Google-style
- [ ] Crea test suite (14+ test)
- [ ] `pytest` passa (100%)
- [ ] `mypy --strict` passa
- [ ] Coverage >80%

### Definition of Done
- [ ] Codice implementato
- [ ] Test passano
- [ ] Type checking OK
- [ ] Nessun import scr/ o my_lib
- [ ] Commit message template seguito
- [ ] PR pronta per review

### Riferimenti
- Piano completo: [REFACTORING_PLAN.md](./docs/REFACTORING_PLAN.md)
- Guida operativa: [IMPLEMENTATION_GUIDE.md](./docs/IMPLEMENTATION_GUIDE.md)
- Source file: `scr/decks.py` (SHA: cb52fbf)
- Issues correlate: #28, #29
```

---

## 📖 Risorse per Copilot

### Documentazione Esistente
- **REFACTORING_PLAN.md**: Piano completo 13 commit (50 KB)
- **IMPLEMENTATION_SUMMARY.md**: Tracker avanzamento (14 KB)
- **ARCHITECTURE.md**: Architettura Clean Arch
- **TESTING_CHECKLIST.md**: Checklist test completa

### Comandi Utili

```bash
# Avvia branch
git checkout refactoring-engine
git pull origin refactoring-engine
git checkout -b feature/migrate-decks-to-domain

# Sviluppo
pytest tests/unit/domain/models/test_deck.py -v --watch
mypy src/domain/models/deck.py

# Pre-commit checks
pytest tests/unit/domain/models/ -v --cov=src/domain/models --cov-report=term-missing
mypy src/domain/models/ --strict
ruff check src/domain/models/

# Commit
git add src/domain/models/deck.py tests/unit/domain/models/test_deck.py
git commit -F- <<EOF
feat(domain): Migrate deck models from scr/ with is_king() fix

- Add src/domain/models/deck.py with ProtoDeck base class
- Implement FrenchDeck (52 cards) and NeapolitanDeck (40 cards)
- Include is_king() method for correct King validation
  * French King value: 13
  * Neapolitan King value: 10
- Add full type hints and Google-style docstrings
- Remove legacy my_lib dependencies
- Add comprehensive test suite (14 tests)

Migrated from: scr/decks.py (SHA: cb52fbf)
Fixes: #28, #29 (v1.3.3 Re napoletano hotfix)
Testing: pytest tests/unit/domain/models/test_deck.py -v
EOF

# Push e PR
git push origin feature/migrate-decks-to-domain
gh pr create --base refactoring-engine --title "[FASE 1 - Commit #1] Migrate Deck Models" --body-file .github/PR_TEMPLATE.md
```

---

## ⚠️ Note Critiche per Copilot

### ❌ NON FARE
1. **Non modificare** `scr/decks.py` (legacy deve rimanere intatto)
2. **Non importare** da `scr/` nel nuovo codice `src/`
3. **Non usare** `my_lib` (dependency legacy)
4. **Non saltare** il metodo `is_king()` (fix critico #28, #29)
5. **Non ignorare** i test (coverage >80% obbligatorio)

### ✅ FARE SEMPRE
1. **Copia esatta** del codice da `scr/` (stessa logica)
2. **Aggiorna import** per usare `src/`
3. **Type hints completi** su tutto
4. **Docstrings** Google-style per ogni metodo pubblico
5. **Test estensivi** per ogni funzionalità
6. **Verifica mypy** --strict prima del commit
7. **Nessuna regressione** (tutto deve funzionare come prima)

---

## 🎯 Obiettivo Finale

**Al completamento dei 13 commit**:
- ✅ `src/` completo con Clean Architecture
- ✅ `test.py` entry point funzionante
- ✅ Feature parity 100% con v1.3.3
- ✅ `acs.py` legacy ancora funzionante (no breaking)
- ✅ Test coverage >80%
- ✅ Documentazione completa

**Prossimo Step**: Creare Issue #1 e assegnare a Copilot

---

**Creato**: 2026-02-07 11:40 CET  
**Per**: GitHub Copilot Agent  
**Progetto**: solitario-classico-accessibile  
**Branch**: refactoring-engine
