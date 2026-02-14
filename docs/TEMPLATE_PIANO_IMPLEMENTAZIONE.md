# 📋 Template Piano di Implementazione

> **QUESTO È UN MODELLO** - Usalo come base per creare nuovi piani di implementazione.  
> Rimuovi sezioni irrilevanti, personalizza contenuti, mantieni struttura coerente.

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

**Esempio (Feature)**:
> Implementare Clean Architecture a strati: Domain Models → Domain Service → Application Controllers → Presentation Formatters → Infrastructure Storage. ScoringService calcola punteggi come dependency opzionale (None = free-play mode).

**Esempio (Bugfix)**:
> Usare **Semi-Modal Pattern**: `ShowModal()` chiamato da `wx.CallAfter()` per evitare nested event loops. Dialog si chiude sempre con `Destroy()`, callback invocato in contesto deferito.

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

[Lista numerata requisiti con comportamento atteso e file coinvolti]

### 1. [Nome Requisito]

**Comportamento Atteso**:
1. [Step 1 utente]
2. [Step 2 sistema]
3. [Step 3 risposta]

**File Coinvolti**:
- `percorso/file1.py` - [Ruolo, già corretto ✅ / DA FIXARE 🔧]
- `percorso/file2.py` - [Ruolo, MODIFICARE ⚙️]

**Esempio**:
```python
# Codice esemplificativo comportamento
```

---

## 🏗️ Architettura (solo per FEATURE/REFACTORING)

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [ComponentName]                                       │   │
│  │ - metodo1()                                           │   │
│  │ - metodo2()                                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ [Controller]           │  │ [Controller]            │    │
│  └────────────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ [Models]               │  │ [Services]              │    │
│  └────────────────────────┘  └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [Storage/UI/External]                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

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
**Linee**: [XXX-YYY] (metodo/classe target)

#### Codice Attuale (se modifica)

```python
# Codice esistente da modificare
def metodo_vecchio():
    # Implementazione attuale
    pass
```

**Problemi**:
- ❌ [Problema 1]
- ❌ [Problema 2]

#### Codice Nuovo/Modificato

```python
# Nuova implementazione
def metodo_nuovo():
    """Docstring completa con Args, Returns, Examples, Version.
    
    Args:
        param1: Descrizione
        
    Returns:
        Tipo: Descrizione
        
    Example:
        >>> metodo_nuovo()
        'risultato'
        
    Version:
        v[X.Y.Z]: [Descrizione modifica]
    """
    # Implementazione nuova
    pass
```

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

## 🎓 Architectural Patterns Reference

### [Nome Pattern]

**Quando Usare**: [Contesto applicabilità]

**Pattern**:
```python
# Codice template pattern
def pattern_template():
    """Esempio implementazione pattern."""
    pass
```

**Caratteristiche**:
- [Caratteristica 1]
- [Caratteristica 2]

**Pro/Contro**:
- ✅ Pro: [Vantaggio]
- ⚠️ Contro: [Limitazione]

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

## 📊 Progress Tracking (opzionale)

| Fase | Status | Commit | Data Completamento | Note |
|------|--------|--------|-------------------|------|
| Fase 1 | [ ] | - | - | |
| Fase 2 | [ ] | - | - | |
| Testing | [ ] | - | - | |
| Review | [ ] | - | - | |
| Merge | [ ] | - | - | |

---

**Fine Template Piano Implementazione**

**Template Version**: v1.0  
**Ultima Modifica**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Basato su**: 20+ piani completati nel progetto solitario-classico-accessibile  

---

## 🎯 Istruzioni Uso Template

### Come Usare Questo Template

1. **Duplica file**: `cp TEMPLATE_PIANO_IMPLEMENTAZIONE.md PLAN_[FEATURE_NAME].md`
2. **Rimuovi sezioni irrilevanti**:
   - Feature: Rimuovi "Root Cause"
   - Bugfix: Rimuovi "Architettura", enfatizza "Root Cause"
   - Refactoring: Mantieni tutto, enfatizza "Testing Strategy"
3. **Personalizza header**: Compila Executive Summary con valori reali
4. **Espandi sezioni**: Aggiungi dettagli specifici per la tua implementazione
5. **Mantieni struttura**: Non riordinare sezioni, mantieni coerenza
6. **Usa emoji**: Mantieni emoji per leggibilità (🔴🟠🟡🟢✅❌⚠️)

### Sezioni Obbligatorie (sempre)

- Executive Summary
- Piano di Implementazione (almeno 1 fase)
- Testing Strategy (almeno unit tests)
- Commit Strategy (conventional commits)

### Sezioni Opzionali (usa se rilevanti)

- Root Cause (solo bugfix)
- Architettura (solo feature/refactoring complessi)
- Patterns Reference (solo se introduci nuovo pattern)
- Progress Tracking (per piani multi-settimana)

### Best Practices

✅ **DO**:
- Usa code blocks con syntax highlighting
- Includi esempi concreti (non placeholder vaghi)
- Specifica file:linee esatte per modifiche
- Documenta rationale decisioni architetturali
- Scrivi test PRIMA di implementare (TDD)
- Commit atomici con message conventional commits

❌ **DON'T**:
- Non lasciare TODO vaghi ("implementare feature")
- Non dimenticare testing strategy
- Non assumere conoscenza implicita (spiega tutto)
- Non mischiare feature diverse nello stesso piano
- Non skippare documentazione docstring

### Quando Creare Nuovo Piano

**Crea piano se**:
- Feature richiede >2 ore sviluppo
- Modifica tocca >3 file
- Introduce nuovo pattern architetturale
- Ha rischio regressione MEDIO/ALTO
- Richiede coordinamento multi-fase

**Non serve piano se**:
- Typo fix (<5 linee)
- Aggiornamento documentazione solo
- Aggiunta test singolo
- Refactoring cosmetico (rename variabile)

### Esempio Workflow Completo

1. **Discussione iniziale** → Identifica problema/feature
2. **Crea piano** → Usa questo template
3. **Review piano** → Valida approccio (non implementazione)
4. **Implementa fase 1** → Segui piano, commit atomico
5. **Test fase 1** → Verifica success criteria
6. **Ripeti 4-5** per fasi successive
7. **Final review** → Test completo end-to-end
8. **Merge branch** → Aggiorna piano → sposta in `completed - [NOME].md`
9. **Update CHANGELOG** → Documenta versione release

---

**Happy Planning! 🚀**
