# 📋 Template Piano di Implementazione

> **QUESTO È UN MODELLO** - Usalo come base per creare nuovi piani di implementazione.  
> Rimuovi sezioni irrilevanti, personalizza contenuti, mantieni struttura coerente.
>
> **Nota**: le regole generali di commit, logging, workflow e testing sono descritte
> in `.github/copilot-instructions.md`. Questo template si concentra sulla
> struttura del piano; non copia le policy.

---

## 📊 Executive Summary

**Tipo**: [FEATURE | BUGFIX | REFACTORING | MIGRATION]  
**Priorità**: [🔴 CRITICA | 🟠 ALTA | 🟡 MEDIA | 🟢 BASSA]  
**Stato**: [DRAFT | READY | IN PROGRESS | COMPLETED]  
**Branch**: `[nome-branch]`  
**Versione Target**: `v[X.Y.Z]`  
**Data Creazione**: [YYYY-MM-DD]  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: [X ore totali] ([Y ore Copilot] + [Z ore review/testing])  
**Commits Previsti**: [N commit atomici]

---

### Problema/Obiettivo

[Descrizione concisa del problema da risolvere o feature da implementare]

**Esempio (Feature)**:
> Implementare sistema di punteggi completo con calcolo real-time, moltiplicatori di difficoltà, bonus tempo, e persistenza statistiche JSON.

**Esempio (Bugfix)**:
> I dialog asincroni non si chiudono mai quando l'utente clicca YES/NO, causando blocco interfaccia e impossibilità di continuare il gioco.

---

### Root Cause (solo per BUGFIX)

[Analisi tecnica della causa radice del bug con tracce errore e flusso chiamate]

**Esempio**:
```
Traceback (most recent call last):
  File "src/infrastructure/ui/gameplay_panel.py", line 130, in on_key_down
    self._select_card()
  File "src/application/gameplay_controller.py", line 323, in _select_card
    mods = pygame.key.get_mods()
           ^^^^^^^^^^^^^^^^^^^^^
pygame.error: video system not initialized
```

**Flusso chiamate**:
```
GameplayPanel.on_key_down()          (wxPython event)
  └─> GameplayController._select_card()
      └─> pygame.key.get_mods()         ❌ ERRORE QUI!
```

**Causa radice**:
- Il metodo `_select_card()` usa pygame in contesto wxPython dove pygame non è inizializzato

---

### Soluzione Proposta

[Descrizione high-level della soluzione con pattern architetturali e rationale]

*Esempio*: Implementare Clean Architecture a strati e documentare le dipendenze in
`docs/ARCHITECTURE.md`.

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | [CRITICA \| ALTA \| MEDIA \| BASSA] | [Descrizione impatto utente] |
| **Scope** | [N file \| M modifiche] | [Lista file coinvolti] |
| **Rischio regressione** | [ALTO \| MEDIO \| BASSO] | [Aree a rischio] |
| **Breaking changes** | [SÌ \| NO] | [Dettagli compatibilità] |
| **Testing** | [COMPLESSO \| MEDIO \| SEMPLICE] | [Scenario testing] |

---

## 🎯 Requisiti Funzionali

[Lista numerata dei requisiti con comportamento atteso. Indica anche file chiave.
]

### 1. [Nome Requisito]

**Comportamento Atteso**:
1. [Step utente]
2. [Risposta sistema]

**File Coinvolti**:
- `src/…` – ruolo descrizione

*(Esempio di snippet se necessario)*


---

## 🏗️ Architettura (solo per FEATURE/REFACTORING)

### Layer Diagram

```
PRESENTATION (UI, Dialogs, Formatters)
       ↓
APPLICATION (Controllers, Use Cases, Game Engine)
       ↓
DOMAIN (Models, Services, Business Rules)
       ↓
INFRASTRUCTURE (Storage, External Services, UI Framework)
```

**Regole dipendenze**: Domain zero dipendenze esterne, Application dipende solo da Domain, Infrastructure implementa interfacce Domain.

Vedi `docs/ARCHITECTURE.md` per diagramma dettagliato e regole layer.

### File Structure

```
src/
├── domain/
│   ├── models/
│   │   └── nuovo_modello.py              # NEW
│   └── services/
│       ├── servizio_esistente.py         # MODIFIED
│       └── nuovo_servizio.py             # NEW
├── application/
│   ├── controller_esistente.py           # MODIFIED
│   └── nuovo_controller.py               # NEW
├── presentation/
│   └── formatters/
│       └── nuovo_formatter.py            # NEW
└── infrastructure/
    ├── ui/
    │   └── componente_ui.py              # MODIFIED
    └── storage/
        └── nuovo_storage.py              # NEW

tests/
├── unit/
│   ├── test_nuovo_modello.py             # NEW: [N] tests
│   └── test_nuovo_servizio.py            # NEW: [M] tests
└── integration/
    └── test_integrazione.py              # NEW: [K] tests

docs/
├── [NOME_PIANO].md                       # THIS FILE
└── TODO_[FEATURE].md                     # Tracking checklist
```

---

## 📝 Piano di Implementazione

[Breakdown in fasi/commit atomici con codice specifico]

### FASE/COMMIT 1: [Nome Descrittivo]

**Priorità**: [🔴 CRITICA | 🟠 ALTA | 🟡 MEDIA | 🟢 BASSA]  
**File**: `percorso/file.py`  

#### Codice Attuale (se modifica)

[Includi solo se necessario un breve snippet di riferimento]

#### Codice Nuovo/Modificato

[Mostra l'algoritmo o la firma modificata; documenta versioni e motivi]

**Vantaggi**:
- ✅ [Vantaggio 1]
- ✅ [Vantaggio 2]

#### Rationale

[Spiegazione dettagliata del perché questa soluzione è corretta]

**Perché funziona**:
1. [Motivo tecnico 1]
2. [Motivo architetturale 2]
3. [Motivo di compatibilità 3]

**Non ci sono regressioni perché**:
- [Evidenza 1]
- [Evidenza 2]

#### Testing Fase 1

**File**: `tests/unit/test_componente.py`

```python
def test_comportamento_nuovo():
    """Test del nuovo comportamento."""
    result = metodo_nuovo()
    assert result == 'atteso'
```

**Commit Message**:
```
feat|fix|refactor([scope]): [descrizione breve]

[Descrizione dettagliata con bullet points]

Impact:
- [Impatto 1]
- [Impatto 2]

Testing:
- [Test 1]
- [Test 2]
```

---

### FASE/COMMIT 2: [Nome Fase 2]

[Ripetere struttura della Fase 1]

---

## 🧪 Testing Strategy

### Unit Tests ([N totale] tests)

#### `tests/unit/test_[componente].py` ([M] tests)
- [ ] Test [funzionalità 1]
- [ ] Test [funzionalità 2]
- [ ] Test [edge case 1]
- [ ] Test [error handling]
- [ ] Test immutabilità/thread-safety

### Integration Tests ([K totale] tests)

#### `tests/integration/test_[feature].py` ([L] tests)
- [ ] Test flusso completo [scenario 1]
- [ ] Test interazione [componente A] + [componente B]
- [ ] Test con dependency None (graceful degradation)
- [ ] Test compatibilità backwards

### Acceptance Tests (End-to-End)

```python
def test_scenario_completo():
    """Test end-to-end del flusso utente completo.
    
    Simula: [descrizione scenario realistico]
    """
    # Setup
    # Azioni
    # Assertions
```

**Manual Testing Checklist**:
- [ ] [Scenario manuale 1]
- [ ] [Scenario manuale 2]
- [ ] [Test accessibilità TTS]
- [ ] [Test performance]

---

## 🎓 Architectural Patterns Reference (se applicabile)

### [Nome Pattern]

**Quando Usare**: [contesto applicabilità]  
**Descrizione**: [pattern in 2-3 righe o link docs]  
**Pro/Contro**: [trade-off chiave]

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [ ] [Criterio 1] - [Metodo verifica]
- [ ] [Criterio 2] - [Metodo verifica]

**Tecnici**:
- [ ] Zero breaking changes per utenti esistenti
- [ ] Test coverage ≥ [X]% per nuovo codice
- [ ] Performance: [metrica] < [soglia]
- [ ] Memory: No leaks dopo [N] cicli

**Code Quality**:
- [ ] Tutti i commit compilano senza errori
- [ ] PEP8 compliant (pycodestyle)
- [ ] Type hints completi (mypy --strict)
- [ ] Docstring complete (Google style)
- [ ] CHANGELOG.md aggiornato

**Accessibilità** (se applicabile):
- [ ] NVDA legge tutti i messaggi TTS
- [ ] TAB navigation funzionante
- [ ] Keyboard shortcuts documentati
- [ ] Focus management corretto

### Performance Requirements

- [ ] [Operazione 1] < [X]ms per call
- [ ] [Operazione 2] < [Y]MB memoria
- [ ] [Operazione 3] supporta [N] elementi concorrenti

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T

```python
# WRONG - [Spiegazione problema]
def anti_pattern():
    # Codice da evitare
    pass
```

**Perché non funziona**:
- [Motivo 1]
- [Motivo 2]

### ✅ DO

```python
# CORRECT - [Spiegazione soluzione]
def pattern_corretto():
    # Codice da seguire
    pass
```

**Perché funziona**:
- [Motivo 1]
- [Motivo 2]

---

## 📦 Commit Strategy

### Atomic Commits ([N] totali)

1. **Commit 1**: [Scope] - [Descrizione breve]
   - `tipo(scope): descrizione conventional commits`
   - Files: `file1.py`, `file2.py`
   - Tests: `test_file1.py`

2. **Commit 2**: [Scope] - [Descrizione breve]
   - `tipo(scope): descrizione`
   - Files: `file3.py`
   - Tests: `test_file3.py`

**Conventional Commits Types**:
- `feat`: Nuova feature
- `fix`: Bugfix
- `refactor`: Refactoring senza cambio funzionalità
- `docs`: Solo documentazione
- `test`: Aggiunta/modifica tests
- `perf`: Performance improvement
- `chore`: Maintenance task

---

## 📚 References

### Documentazione Esterna
- [Link 1 - Nome risorsa](url)
- [Link 2 - API docs](url)
- [Link 3 - Pattern guide](url)

### Internal Architecture Docs
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `docs/API.md` - Public API reference
- `docs/[ALTRO_PIANO].md` - Piano implementazione correlato

### Related Code Files
- `src/path/file1.py` - [Descrizione ruolo]
- `src/path/file2.py` - [Descrizione ruolo]
- `test.py` - [Entry point]

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Fase 1**:
   - Apri file `[percorso]`
   - Naviga a linea [XXX]
   - Sostituisci con codice da "Fase 1 - Codice Nuovo"
   - Salva file

2. **Fase 2**:
   - [Step-by-step instructions]

3. **Testing**:
   - Esegui `python -m pytest tests/unit/test_[nome].py`
   - Verifica output atteso: [descrizione]

4. **Commit**:
   - `git add [files]`
   - `git commit -m "[message]"`

### Verifica Rapida Pre-Commit

```bash
# Sintassi Python
python -m py_compile src/**/*.py

# Type checking (opzionale)
mypy src/ --strict

# Code style
pycodestyle src/ --max-line-length=120

# Tests
python -m pytest tests/ -v

# Coverage (opzionale)
coverage run -m pytest tests/
coverage report --show-missing
```

### Troubleshooting

**Se [problema 1]**:
- Verifica [condizione 1]
- Controlla [condizione 2]
- Debug con `print("[marker]")` in `[file:line]`

**Se [problema 2]**:
- [Soluzione alternativa]

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **[Obiettivo 1]**: [Descrizione verificabile]
✅ **[Obiettivo 2]**: [Descrizione verificabile]  
✅ **[Obiettivo 3]**: [Descrizione verificabile]

**Metriche Successo**:
- Coverage: [X]%
- Performance: [metrica] = [valore]
- User feedback: [criterio]

---

## 📞 Support and Questions

Per domande o problemi durante l'implementazione:

1. **Riferimento**: Questo documento (`docs/[NOME_PIANO].md`)
2. **Codice Esistente**: Studiare pattern in `[file_esempio.py]`
3. **Documentation**: [Link docs rilevanti]
4. **GitHub Issues**: Aprire issue con tag `[tag1]`, `[tag2]`

---

## 📊 Progress Tracking

| Fase | Status | Commit | Data Completamento | Note |
|------|--------|--------|-------------------|------|
| Fase 1 | [ ] | - | - | |
| Fase 2 | [ ] | - | - | |
| Testing | [ ] | - | - | |
| Review | [ ] | - | - | |
| Merge | [ ] | - | - | |

---

**Fine Template Piano Implementazione**

**Template Version**: v1.1 (ottimizzato -15.7%)  
**Ultima Modifica**: 2026-02-22  
**Autore**: AI Assistant + Nemex81  
**Basato su**: 20+ piani completati nel progetto solitario-classico-accessibile  

---

## 🎯 Uso Template

### Quando Usare

✅ Feature richiede >2 ore sviluppo  
✅ Modifica tocca >3 file  
✅ Introduce nuovo pattern architetturale  
✅ Ha rischio regressione MEDIO/ALTO  
✅ Richiede coordinamento multi-fase

❌ NON serve per typo fix, doc-only updates, test singoli, rename variabili

### Come Usare

1. Duplica: `cp TEMPLATE_PIANO_IMPLEMENTAZIONE.md PLAN_[FEATURE_NAME].md`
2. Rimuovi sezioni irrilevanti (Feature: rimuovi Root Cause; Bugfix: rimuovi Architettura)
3. Compila Executive Summary con valori reali
4. Espandi Piano Implementazione con fasi specifiche
5. Mantieni struttura e emoji per accessibilità

### Workflow

DESIGN (concept) → PLAN (questo template, decisioni tecniche) → TODO (tracking operativo) → Implementazione per fasi → Test → Merge → CHANGELOG

Usa PLAN per API, layer assignment, file structure, testing strategy. Dopo PLAN approvato (stato READY), crea TODO.md per tracking.

### Sezioni Obbligatorie

- Executive Summary
- Piano di Implementazione (≥1 fase)
- Testing Strategy (≥unit tests)
- Commit Strategy (conventional commits)

### Sezioni Opzionali

- Root Cause (solo bugfix)
- Architettura (solo feature/refactoring complessi)
- Patterns Reference (solo se nuovo pattern)
- Progress Tracking (backup stato implementazione)

---

**Happy Planning! 🚀**
