# 📋 TODO Template - Progetto Solitario Accessibile

> **Modello standardizzato per file TODO destinati a implementazioni guidate da GitHub Copilot**
> 
> Questo template sintetizza i pattern efficaci utilizzati nelle implementazioni precedenti del progetto.
> Usa questo modello come base per creare nuovi TODO strutturati e completi.

---

## Intestazione Standard

```markdown
# 🚀 TODO: [Nome Feature/Fix] (v[Versione])

**Branch**: `[nome-branch]`  
**Priority**: [HIGH | MEDIUM | LOW]  
**Type**: [BUG FIX | FEATURE | REFACTOR | ENHANCEMENT]  
**Estimated Time**: [X-Y ore]  
**Status**: [📋 READY | 🚧 IN PROGRESS | ✅ COMPLETE | ⏸️ BLOCKED]
```

### Esempio Compilato

```markdown
# 🚀 TODO: Timer Strict Mode Implementation (v1.5.2.2)

**Branch**: `copilot/implement-scoring-system-v2`  
**Priority**: HIGH  
**Type**: BUG FIX + FEATURE  
**Estimated Time**: 40-50 minuti  
**Status**: 📋 READY FOR IMPLEMENTATION
```

---

## 1. OVERVIEW

### 1.1 Problem Statement

**Descrivi il problema da risolvere o la feature da implementare in 3-5 punti con emoji:**

```markdown
### **Problem Statement**

Attualmente:
- ❌ [Problema 1: cosa non funziona]
- ❌ [Problema 2: comportamento errato]
- ❌ [Problema 3: conseguenze]
- ⚠️ [Impatto sul sistema]
```

### 1.2 Solution Design

**Descrivi la soluzione proposta con sottopunti numerati:**

```markdown
### **Solution Design**

Implementare [nome soluzione] con le seguenti caratteristiche:

1. **[Modalità/Componente A]** (default/legacy):
   - [Comportamento 1]
   - [Comportamento 2]
   - [Compatibilità]

2. **[Modalità/Componente B]** (nuovo):
   - [Nuova funzionalità 1]
   - [Nuova funzionalità 2]
   - [Caso d'uso ideale]

### **Architecture Impact**

```plaintext
Domain Layer:
  └─ [File modificato]: +[campo aggiunto]

Application Layer:
  ├─ [Controller A]: +[metodo nuovo]
  └─ [Controller B]: ~[metodo modificato]

Infrastructure Layer:
  └─ [File]: +[evento/handler]

Presentation Layer:
  └─ [Formatter]: +[metodo formattazione]
```
```

---

## 2. FILES TO MODIFY/CREATE

**Lista tutti i file coinvolti con tipo di modifica:**

```markdown
### File 1: `path/to/file.py`
- **Tipo**: [CREATE | MODIFY | DELETE]
- **Scopo**: [Descrizione breve]
- **LOC stimato**: ~[numero] linee

### File 2: `path/to/other_file.py`
- **Tipo**: MODIFY
- **Scopo**: Estendere classe esistente con nuovo metodo
- **LOC stimato**: ~20 linee

### File 3: `tests/unit/test_feature.py`
- **Tipo**: CREATE
- **Scopo**: Test suite per nuova feature
- **LOC stimato**: ~150 linee
```

---

## 3. IMPLEMENTATION STEPS

**Dividi l'implementazione in step atomici con checkboxes:**

```markdown
## ✅ STEP 1: [Nome Step] (tempo stimato)

**File**: `path/to/file.py`

### **Task 1.1: [Descrizione task specifico]**

**Location**: [Metodo/Classe/Linea specifica]

**Add this code**:

```python
# Codice Python con commenti esplicativi
class Example:
    def __init__(self):
        # 🆕 NEW v[versione]: Descrizione
        self.new_field: bool = True
```

**Context**: [Dove inserire il codice rispetto al codice esistente]

**Expected Result**:

```python
# Come dovrebbe apparire il codice finale
```

### **Task 1.2: [Secondo task dello step]**

[Ripeti struttura]

### **Verification**:

- [ ] Campo aggiunto con type hint corretto
- [ ] Default value impostato
- [ ] Commento inline presente
- [ ] Docstring aggiornato

---

## ✅ STEP 2: [Secondo Step] (tempo stimato)

[Ripeti struttura dello STEP 1]
```

### Pattern Ricorrenti per Step Comuni

#### Step per Domain Models

```markdown
## ✅ STEP X: Add [Field/Class] to Domain Model

**File**: `src/domain/models/[model_name].py`

### **Task X.1: Add New Field**

**Location**: In `[ClassName].__init__()` method

**Add this code**:

```python
# [Descrizione campo] (v[versione])
self.[field_name]: [Type] = [default_value]
#   [Spiegazione valori possibili]
```

### **Task X.2: Update Docstring**

**Location**: Class docstring

**Add to Attributes section**:

```python
"""
Attributes:
    [field_name] ([Type]): [Descrizione completa]
        - [Dettaglio 1]
        - [Dettaglio 2]
"""
```

### **Verification**:
- [ ] Type hint presente
- [ ] Default value backward compatible
- [ ] Docstring aggiornato
```

#### Step per Test Suite

```markdown
## ✅ STEP X: Create Test Suite

**File**: `tests/unit/test_[feature].py`

### **Task X.1: Setup Test Class**

```python
import pytest
from src.[module] import [Class]

class Test[Feature]:
    @pytest.fixture
    def [fixture_name](self):
        # Setup fixture
        return [instance]
    
    def test_[scenario_name](self, [fixture_name]):
        # Arrange
        [setup]
        
        # Act
        [action]
        
        # Assert
        assert [condition], "[error message]"
```

### **Verification**:
- [ ] Almeno [N] test implementati
- [ ] Tutti i test passano
- [ ] Coverage ≥ [%]
```

---

## 4. TEST CASES

**Documenta scenari di test con setup/azioni/risultati attesi:**

```markdown
### **Test Scenario 1: [Nome Scenario]**

**Setup**:
```python
settings.option_a = value_a
settings.option_b = value_b
engine = GameEngine.create(settings=settings)
```

**Actions**:
1. [Azione 1]
2. [Azione 2]
3. [Azione 3]

**Expected Results**:
- ✅ `[assertion_1] == [expected_value_1]`
- ✅ `[assertion_2] == [expected_value_2]`
- ✅ TTS announces: "[messaggio atteso]"
- ✅ Console shows: `[log output atteso]`

---

### **Test Scenario 2: [Edge Case]**

[Ripeti struttura]
```

### Tabella Riassuntiva Scenari (Opzionale)

```markdown
| # | Scenario | Stato Iniziale | Azione | Risultato Atteso |
|---|----------|----------------|--------|------------------|
| 1 | [Nome] | [Setup] | [Action] | [Expected] |
| 2 | [Nome] | [Setup] | [Action] | [Expected] |
```

---

## 5. ACCEPTANCE CRITERIA

**Lista criteri di accettazione per completamento:**

```markdown
### Functional Requirements
- [ ] [Feature A] funziona correttamente
- [ ] [Feature B] gestisce edge case [X]
- [ ] [Opzione C] salvata/caricata correttamente

### Non-Functional Requirements
- [ ] Performance: [metrica] < [valore]
- [ ] Accessibility: Tutti i comandi accessibili via tastiera
- [ ] UX: Messaggi TTS chiari e completi

### Quality Requirements
- [ ] Test coverage ≥ [%]
- [ ] Zero breaking changes
- [ ] Backward compatibility mantenuta
- [ ] Docstring completi al 100%
- [ ] Type hints al 100%

### No Regressions
- [ ] [Feature esistente 1] non influenzata
- [ ] [Feature esistente 2] funziona come prima
- [ ] Tutte le test suite esistenti passano
```

---

## 6. IMPLEMENTATION SUMMARY

**Tabella riassuntiva modifiche:**

```markdown
| File | Metodo/Classe | Tipo Modifica | LOC |
|------|---------------|---------------|-----|
| `src/domain/models/[file].py` | `[Class].[method]` | Add field | +4 |
| `src/application/[file].py` | `[Class].[method]` | Add method | +38 |
| `test.py` | `[method]` | Modify | ~12 |
| `tests/unit/test_[file].py` | `Test[Class]` | Create | +60 |
| **TOTAL** | | | **~114 LOC** |
```

---

## 7. COMMIT MESSAGE TEMPLATE

**Template per commit message convenzionale:**

```markdown
[type]([scope]): [short description in lowercase]

[OPTIONAL] BREAKING: [description if breaking changes]

Fixed:
- [Bug 1 description]
- [Bug 2 description]

Added:
- [Feature 1 description]
- [Feature 2 description]

Modified files:
- [file 1] ([change summary])
- [file 2] ([change summary])

Testing:
- [Test category 1] verified
- [Test category 2] verified

Refs: docs/TODO_[FILENAME].md
```

### Tipi Commit Convenzionali

- `feat`: Nuova feature
- `fix`: Bug fix
- `refactor`: Refactoring senza cambio funzionalità
- `docs`: Solo documentazione
- `test`: Aggiunta/modifica test
- `chore`: Manutenzione (build, deps)

---

## 8. DOCUMENTATION UPDATES

**Checklist aggiornamenti documentazione:**

```markdown
### **README.md**

**Location**: [Sezione specifica]

**Add this section**:

```markdown
### [Feature Name] (v[versione])

[Descrizione feature orientata all'utente]

**Caratteristiche**:
- ✨ [Caratteristica 1]
- 🔧 [Caratteristica 2]
- 📊 [Caratteristica 3]

**Configurazione**: [Come abilitare/configurare]
```

---

### **CHANGELOG.md**

**Location**: Top of file

**Add this section**:

```markdown
## [v[versione]] - [YYYY-MM-DD]

### Fixed
- **[BUG #X]**: [Descrizione fix]

### Added
- **[Feature Name]**: [Descrizione]
  - [Dettaglio 1]
  - [Dettaglio 2]

### Changed
- **[Component]**: [Descrizione modifica]

### Technical Details
- `[file.py]`: [modifica]
- `[file2.py]`: [modifica]
```
```

---

## 9. IMPLEMENTATION CHECKLIST

**Checklist finale prima del commit:**

```markdown
### Code Quality
- [ ] Tutti i type hints presenti
- [ ] Tutti i docstrings completi (Google style)
- [ ] Nessun TODO/FIXME nel codice
- [ ] Nessun codice commentato
- [ ] Style PEP 8 rispettato
- [ ] Nessun import inutilizzato

### Testing
- [ ] Tutti gli unit test passano
- [ ] Tutti gli integration test passano
- [ ] Coverage ≥ [%] per nuovo codice
- [ ] Test manuali completati
- [ ] Nessun warning nei test

### Documentation
- [ ] README.md aggiornato
- [ ] CHANGELOG.md aggiornato
- [ ] Docstring completi
- [ ] TODO checklist completo

### Functionality
- [ ] Feature principale funziona
- [ ] Edge cases gestiti
- [ ] Error handling robusto
- [ ] Backward compatibility OK
- [ ] Zero regressioni

### Accessibility (per progetti audiogame)
- [ ] Comandi tastiera documentati
- [ ] Messaggi TTS in italiano
- [ ] Nessuna informazione solo visiva
- [ ] Screen reader friendly
```

---

## 10. NOTES FOR COPILOT

**Sezione dedicata a GitHub Copilot con note implementative:**

```markdown
### **Context for AI Assistant**

[Descrizione high-level della feature per fornire contesto]

### **Key Design Decisions**

1. **[Decisione 1]**: [Motivazione]
2. **[Decisione 2]**: [Motivazione]
3. **[Decisione 3]**: [Motivazione]

### **Edge Cases to Handle**

- [Edge case 1]: [Come gestire]
- [Edge case 2]: [Come gestire]
- [Edge case 3]: [Come gestire]

### **Testing Priorities**

1. [Test prioritario 1] (critico)
2. [Test prioritario 2] (importante)
3. [Test prioritario 3] (nice-to-have)

### **Future Enhancements** (non in questo TODO)

- [Enhancement 1]
- [Enhancement 2]
- [Enhancement 3]

### **Dependencies/Prerequisites**

- ✅ [Prerequisito 1] già completato
- ✅ [Prerequisito 2] già completato
- ⏸️ [Prerequisito 3] da completare prima
```

---

## 11. COMPLETION CRITERIA

**Definisci quando il TODO è considerato completo:**

```markdown
## ✅ COMPLETION CRITERIA

Questo TODO è **COMPLETE** quando:

- [ ] Tutti gli step implementati con codice fornito
- [ ] Tutti i test scenarios passano
- [ ] README e CHANGELOG aggiornati
- [ ] Commit pushato su branch `[nome-branch]`
- [ ] Nessuna regressione nelle feature esistenti
- [ ] [Requisito accessibilità specifico]
- [ ] [Requisito performance specifico]

**Estimated completion**: [tempo stimato] per sviluppatore esperto

---

**Created**: [YYYY-MM-DD HH:MM TZ]  
**Branch**: `[nome-branch]`  
**Version**: v[versione]  
**Priority**: [HIGH | MEDIUM | LOW]  
**Assignee**: [GitHub Copilot | Developer Name]

---

END OF TODO
```

---

## 📖 GUIDA ALL'USO DEL TEMPLATE

### Quando Usare Questo Template

✅ **Usa questo template per**:
- Implementazioni guidate da GitHub Copilot
- Feature complesse con più file modificati
- Bug fix che richiedono refactoring strutturato
- Task con test suite da creare
- Modifiche architetturali multi-layer

❌ **NON usare per**:
- Fix typo o piccole correzioni (< 10 LOC)
- Aggiornamenti documentazione puri
- Bump versioni dipendenze
- Task già iniziati (usa per task nuovi)

### Come Compilare il Template

1. **Copia questo file** come base: `TODO_[FEATURE_NAME].md`
2. **Compila sezione 1-2**: Overview + Files (5-10 min)
3. **Espandi sezione 3**: Implementation Steps dettagliati (20-30 min)
4. **Documenta sezione 4**: Test scenarios concreti (10-15 min)
5. **Completa sezione 5-11**: Criteri, commit template, note (15-20 min)
6. **Review**: Verifica completezza e chiarezza (5 min)

### Best Practices

✨ **DO**:
- Sii specifico: indica file, metodi, linee esatte
- Fornisci codice completo nei task (no placeholder)
- Includi context/location per ogni snippet
- Usa emoji per categorizzare (🆕 ✅ ❌ ⚠️)
- Numera step in ordine di esecuzione
- Aggiungi stime tempo realistiche

❌ **DON'T**:
- Generalizzare troppo ("modifica il file X")
- Omettere type hints/docstring nei codice
- Saltare verification checklist
- Dimenticare test scenarios
- Ignorare documentazione updates
- Usare solo inglese (progetto italiano)

### Sezioni Opzionali

Puoi **omettere** queste sezioni se non applicabili:
- **Tabella riassuntiva test** (se < 3 scenari)
- **Architecture Impact** (se modifiche solo in 1 layer)
- **Future Enhancements** (se scope ben definito)
- **Dependencies** (se task standalone)

Puoi **aggiungere** sezioni custom:
- **Migration Guide** (se breaking changes)
- **Performance Benchmarks** (se ottimizzazioni)
- **Security Considerations** (se input utente)

---

## 🎯 ESEMPI DI RIFERIMENTO

### TODO Completi da Studiare

Nel progetto esistono 3 TODO ben strutturati da usare come riferimento:

1. **`TODO_timer_strict_mode_v1.5.2.2.md`**
   - ✅ Ottimo per: Feature + Bug Fix, multi-file, eventi UI
   - 📊 Complessità: ALTA (4 file, 6 step, 70 min)
   - 🔍 Studia: Sezione "Implementation Steps" dettagliata

2. **`TODO_FIX_DIFFICULTY_LEVELS_4_5.md`**
   - ✅ Ottimo per: Bug Fix puro, validazione constraints
   - 📊 Complessità: MEDIA (1 file, 2 bug, 40 min)
   - 🔍 Studia: Sezione "Test Cases" con tabelle

3. **`TODO_SCORING.md`**
   - ✅ Ottimo per: Feature complessa multi-layer, 8 fasi
   - 📊 Complessità: MOLTO ALTA (12+ file, 8 commit, 5 ore)
   - 🔍 Studia: Struttura a "Phases" con acceptance criteria

### Pattern Specifici Identificati

#### Pattern: Bug Fix con Root Cause Analysis

```markdown
## 🐛 BUG #X: [Titolo Bug]

### Problem Description
[Descrizione problema]

### Current Behavior
**File**: `path/to/file.py`  
**Method**: `method_name()` (lines ~XX-YY)

```python
# Codice problematico attuale
```

### Expected Behavior
[Comportamento atteso]

### Root Cause
[Analisi causa radice]

### Fix Implementation
[Soluzione step-by-step]
```

#### Pattern: Feature con Modalità Alternative

```markdown
### Solution Design

1. **STRICT Mode** (default):
   - [Comportamento conservativo]
   - [Compatibilità legacy]

2. **PERMISSIVE Mode** (nuovo):
   - [Comportamento flessibile]
   - [Caso d'uso casual]
```

#### Pattern: Step con Verifica Incrementale

```markdown
## ✅ STEP X: [Nome]

### Task X.1: [Task]
[Implementazione]

### Task X.2: [Task]
[Implementazione]

### Verification:
- [ ] [Check tecnico 1]
- [ ] [Check tecnico 2]
- [ ] [Check funzionale 3]

**Commit when all checkboxes checked**
```

---

## 📚 CONVENZIONI PROGETTO SPECIFICHE

### Architettura Clean (4 Layer)

Il progetto usa Clean Architecture, rispetta questa struttura:

```
src/
├── domain/           # Logica business pura (no dipendenze)
│   ├── models/       # Entità, Value Objects
│   └── services/     # Use cases, regole business
├── application/      # Orchestrazione, controllers
├── infrastructure/   # Persistence, I/O, external
└── presentation/     # UI, formatters, TTS
```

**Regole**:
- Domain NON importa mai da Application/Infrastructure/Presentation
- Application può importare solo da Domain
- Infrastructure può importare da Domain
- Presentation può importare da Domain + Application

### Convenzioni Codice Python

- **Type hints**: Obbligatori per tutti i parametri/return
- **Docstrings**: Google style, obbligatori per public API
- **Naming**: `snake_case` per funzioni/variabili, `PascalCase` per classi
- **String literals**: Italiano per messaggi utente, inglese per codice
- **Constants**: `UPPER_SNAKE_CASE` con prefisso modulo se ambigui

### Convenzioni Testing

- **Framework**: pytest
- **Struttura**: `tests/unit/[layer]/test_[module].py`
- **Pattern**: Arrange-Act-Assert con commenti espliciti
- **Fixtures**: Definire in `conftest.py` se riusate in >2 test
- **Coverage**: Target 90%+ per nuovo codice

### Convenzioni Accessibilità (Audiogame)

- **TTS**: Tutti i messaggi in italiano chiaro
- **Keyboard only**: Nessuna dipendenza da mouse
- **Screen reader**: Evitare simboli (es: → diventa "poi")
- **Feedback**: Ogni azione deve avere feedback TTS

---

## 🔄 WORKFLOW COPILOT CONSIGLIATO

### Fase 1: Preparazione (10-20% tempo)

1. **Leggi TODO completo** 2 volte
2. **Identifica dipendenze** tra step
3. **Prepara branch** git
4. **Verifica prerequisiti** (file esistenti, test suite funzionanti)

### Fase 2: Implementazione Incrementale (60-70% tempo)

Per ogni STEP:

1. **Leggi tutti i task dello step**
2. **Implementa task uno alla volta** (non skip)
3. **Testa dopo ogni task** se possibile
4. **Completa verification checklist**
5. **Commit solo se checklist OK**

NON procedere a STEP successivo se verification ha ✗

### Fase 3: Integration Testing (10-15% tempo)

1. **Esegui tutti gli scenari di test** documentati
2. **Verifica acceptance criteria**
3. **Test regressione** sulle feature esistenti
4. **Fix eventuali fallimenti** prima di procedere

### Fase 4: Documentation & Cleanup (10-15% tempo)

1. **Aggiorna README.md**
2. **Aggiorna CHANGELOG.md**
3. **Rivedi docstrings** aggiunti
4. **Esegui linter** (flake8, black)
5. **Commit finale** con message dal template

---

## ✅ CHECKLIST: "È un Buon TODO?"

Usa questa checklist per validare il tuo TODO prima di passarlo a Copilot:

### Completezza

- [ ] Ogni step ha almeno 1 verification checkbox
- [ ] Ogni file modificato ha path completo
- [ ] Ogni snippet ha indicazione Location precisa
- [ ] Almeno 3 test scenarios documentati
- [ ] Acceptance criteria coprono funzionalità + qualità + no regressioni

### Chiarezza

- [ ] Titolo descrive chiaramente la feature/fix
- [ ] Overview spiega "perché" oltre al "cosa"
- [ ] Step numerati in ordine logico di esecuzione
- [ ] Codice fornito è completo (no placeholder `# TODO`)
- [ ] Commit message template pronto per copy-paste

### Praticità

- [ ] Stime tempo realistiche (verifica con TODO simili)
- [ ] Ogni step completabile in < 30 min
- [ ] Verification checklist actionable (no vaghezza)
- [ ] Test scenarios riproducibili con setup esatto
- [ ] Note for Copilot menzionano edge cases noti

### Manutenibilità

- [ ] File path seguono struttura progetto
- [ ] Type hints presenti in tutti gli snippet
- [ ] Docstrings presenti per public API
- [ ] Documentation updates inclusi
- [ ] Backward compatibility menzionata se rilevante

**Score**: ___ / 20

- ≥ 18: TODO eccellente, pronto per Copilot ✅
- 15-17: TODO buono, rivedere items mancanti 🟡
- < 15: TODO incompleto, espandere prima di usare ❌

---

## 📝 NOTE FINALI

### Quando Deviare dal Template

Questo template è una **guida**, non una prigione. Devia quando:

- **Task molto semplice** (< 50 LOC, 1 file): Usa versione ridotta (solo sezioni 1-3-5)
- **Spike/Esplorazione**: Ometti test dettagliati, aggiungi sezione "Questions to Answer"
- **Hotfix produzione**: Prioritizza sezione "Fix Implementation", minimizza resto
- **Refactoring puro**: Espandi sezione "Acceptance Criteria" con metriche (coverage, complexity)

### Miglioramenti Futuri Template

Versioni future potrebbero includere:

- [ ] Sezione "Dependencies Graph" visuale
- [ ] Template per TODO multi-sprint
- [ ] Checklist specifica per PR review
- [ ] Sezione "Rollback Plan" per feature rischiose

### Feedback

Per migliorare questo template:

1. Crea issue su GitHub con tag `template-improvement`
2. Includi esempio TODO che non si adatta bene
3. Suggerisci sezioni mancanti o ridondanti

---

**Template Version**: 1.0.0  
**Last Updated**: 2026-02-11  
**Maintainer**: Nemex81  
**License**: MIT (come progetto principale)

---

END OF TEMPLATE
