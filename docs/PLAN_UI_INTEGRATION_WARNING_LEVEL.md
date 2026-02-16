# Piano Integrazione UI - Opzione Avvisi Malus

**Data**: 16 Febbraio 2026  
**Versione Target**: v2.6.1 (fix addizionale indipendente)  
**Branch**: `fix/ui-warning-level-option`  
**Priorità**: MEDIA (enhancement accessibilità)  
**Dipendenze**: PR #66 (sistema warning levels già implementato)  
**Stato Verifica**: ✅ APPROVATO (16/02/2026 - riferimenti tecnici verificati)

---

## Executive Summary

Il sistema di livelli di verbosità warnings è **completamente implementato** a livello architetturale (Domain, GameSettings, ScoringService), ma manca l'**esposizione nell'interfaccia utente** del menu Opzioni.

### Stato Attuale (Implementato in PR #66)

✅ **Domain Layer**: `ScoreWarningLevel` enum (4 livelli) - **VERIFICATO** in `src/domain/models/scoring.py`  
✅ **GameSettings**: `cycle_score_warning_level()` e `get_score_warning_level_display()` - **VERIFICATO**  
✅ **ScoringService**: Warnings level-aware con tag-based detection  
✅ **GameEngine**: TTS warnings integrati in `_announce_draw_threshold_warning()`  
✅ **Persistenza**: Serializzazione/deserializzazione funzionante - **VERIFICATO** in `to_dict()`/`load_from_dict()`  

⚠️ **MANCA**: Binding UI nel menu opzioni (tasto F9 o equivalente)

### Obiettivo Fix

Aggiungere **Opzione 9** nel menu Opzioni principale:
- **Nome**: "Avvisi Soglie Punteggio"
- **Tasto**: F9 (o alternativa se conflitto)
- **Comportamento**: Cicla tra DISABLED → MINIMAL → BALANCED → COMPLETE
- **Display**: Visualizza livello corrente (es. "Equilibrati")

---

## Verifica Tecnica Pre-Implementazione

**Data Verifica**: 16 Febbraio 2026, 15:15 CET  
**Risultato**: ✅ TUTTI I RIFERIMENTI VERIFICATI

### Componenti Verificati

#### 1. ScoreWarningLevel Enum
**File**: `src/domain/models/scoring.py`  
**Stato**: ✅ CONFERMATO

```python
class ScoreWarningLevel(IntEnum):
    DISABLED = 0   # Nessun warning
    MINIMAL = 1    # Solo transizioni 0pt → penalità
    BALANCED = 2   # Transizioni + escalation (DEFAULT)
    COMPLETE = 3   # Pre-warnings + tutte soglie
```

**Mapping Soglie per Livello** (da codice reale):

| Livello | Stock Draw Warnings | Recycle Warnings |
|---------|---------------------|------------------|
| **DISABLED** | Nessuno | Nessuno |
| **MINIMAL** | Draw 21 (prima penalità) | Recycle 3 (prima penalità) |
| **BALANCED** | Draw 21, Draw 41 (escalation) | Recycle 3, Recycle 4 |
| **COMPLETE** | Draw 20 (pre), 21, 41 | Recycle 3, 4, 5 |

⚠️ **NOTA IMPORTANTE**: La soglia recycle per MINIMAL è **3** (non 4). Il primo warning recycle avviene al terzo riciclo per tutti i livelli ≥ MINIMAL.

#### 2. GameSettings Methods
**File**: `src/domain/services/game_settings.py`  
**Stato**: ✅ CONFERMATO (righe ~1045-1100)

```python
def cycle_score_warning_level(self) -> Tuple[bool, str]:
    """Cycle through score warning levels.
    Sequence: DISABLED → MINIMAL → BALANCED → COMPLETE → DISABLED
    Returns: (success, message with level description)
    """
    # Implementazione già presente e funzionante
    
def get_score_warning_level_display(self) -> str:
    """Get human-readable warning level for options display.
    Returns: Short description ("Disattivati", "Minimi", "Equilibrati", "Completi")
    """
    # Implementazione già presente e funzionante
```

**Pattern Return**: Entrambi i metodi seguono convenzioni esistenti:
- `cycle_*()` ritorna `(bool, str)` - compatibile con altri handler
- `get_*_display()` ritorna `str` - compatibile con formatter
- Validazione `validate_not_running()` presente
- Logging automatico con `log.settings_changed()`

#### 3. Persistenza
**File**: `src/domain/services/game_settings.py`  
**Stato**: ✅ CONFERMATO (righe ~1102-1160)

```python
def to_dict(self) -> dict:
    return {
        # ... altri campi ...
        "score_warning_level": self.score_warning_level.name,  # Serializzazione string
    }

def load_from_dict(self, data: dict) -> None:
    # Gestione retrocompat + error handling già implementata
    # Fallback a BALANCED se valore invalido/mancante
```

**Retrocompatibilità**: Gestione automatica di:
- Valori string (`"BALANCED"`) - formato v2.6.0
- Valori int (`2`) - formato alternativo
- Valori mancanti - default BALANCED
- Valori invalidi - fallback BALANCED con warning log

### Punti di Attenzione Implementazione

1. **TTS Path**: Verificare sintassi corretta durante Fase 1
   - Pattern atteso: `engine.screen_reader.tts.speak(msg, interrupt=True)`
   - Cercare esempi esistenti nel file entry point

2. **Entry Point**: Identificare file corretto (probabile `acs.py` o `test.py`)
   - Grep per `pygame.K_F` per trovare handler esistenti
   - Replicare esattamente struttura handler F1-F8

3. **Test Soglie**: Usare mapping verificato sopra per test funzionali
   - MINIMAL: testare draw 21 e recycle 3 (NON recycle 4)
   - BALANCED: testare draw 21, 41 e recycle 3, 4
   - COMPLETE: testare tutte (draw 20, 21, 41; recycle 3, 4, 5)

---

## Analisi File Interessati

Dalla ricerca repository, il menu opzioni principale è gestito da:

### File Primario: `acs.py` o `test.py`

Probabilmente il file entry point dell'applicazione contiene:
- Loop principale pygame
- Event handler per tasti nel menu opzioni
- Chiamate a `settings.cycle_*()` methods
- TTS announcements per feedback

**Azione**: Identificare il file corretto e aggiungere handler F9.

### File Formattazione: `src/presentation/formatters/options_formatter.py`

Potrebbe contenere:
- Metodo `get_options_display()` che formatta la lista opzioni
- Template stringa per visualizzazione menu

**Azione**: Aggiungere riga opzione 9 al template.

---

## Implementazione

### Fase 1: Identificare Entry Point (10 min)

**Ricerca Pattern**:
```bash
# Cerca file con handler pygame esistenti
grep -r "pygame.K_F" *.py

# Output atteso: file principale con pattern tipo:
# if event.key == pygame.K_F1:
#     success, msg = engine.settings.cycle_difficulty()
```

**File Candidati**:
- `acs.py` (probabile main application)
- `test.py` (se è entry point development)
- `src/application/game_controller.py` (se esiste controller centralizzato)

**Verifiche da Fare**:
1. Individuare sezione "options menu" o "menu opzioni"
2. Confermare path TTS: `engine.screen_reader.tts.speak()`
3. Verificare se F9 è già usato (conflitto)

### Fase 2: Aggiungere Handler Tasto (15 min)

**Codice da Aggiungere** (nel file identificato, sezione options menu):

```python
# In event handler del menu opzioni (dopo altri tasti F1-F8)
elif event.key == pygame.K_F9:
    # Cicla livello warning
    success, msg = engine.settings.cycle_score_warning_level()
    if success:
        # Annuncia nuovo livello via TTS
        if engine.screen_reader:
            engine.screen_reader.tts.speak(msg, interrupt=True)
    else:
        # Gestione errore (es. partita in corso)
        if engine.screen_reader:
            engine.screen_reader.tts.speak(msg, interrupt=True)
```

**Note Implementative**:
- **Tasto**: F9 (verificare se libero, altrimenti F10 o altro)
- **Interrupt**: `True` per feedback immediato (come altre opzioni)
- **Metodo**: `cycle_score_warning_level()` **già implementato** in GameSettings
- **Pattern**: Replicare ESATTAMENTE struttura handler esistenti F1-F8
- **Error Handling**: Gestire caso `success=False` (partita in corso)

### Fase 3: Aggiornare Display Opzioni (20 min)

**Se esiste `OptionsFormatter` o equivalente**:

```python
# In metodo get_options_display() o template stringa
options_text = f"""
Opzioni di Gioco:
1. Difficoltà: {settings.get_difficulty_display()} (F1)
2. Pescate: {settings.get_draw_count_display()} (F2)
3. Timer: {settings.get_timer_display()} (F3)
4. Modalità Riciclo: {settings.get_shuffle_mode_display()} (F4)
5. Suggerimenti: {settings.get_command_hints_display()} (F5)
6. Sistema Punti: {settings.get_scoring_display()} (F6)
7. Modalità Timer: {settings.get_timer_strict_mode_display()} (F7)
8. [Opzione Esistente] (F8)
9. Avvisi Soglie Punteggio: {settings.get_score_warning_level_display()} (F9)

Premi ESC per uscire senza salvare, INVIO per confermare.
"""
```

**Se display dinamico**:
```python
# Aggiungere entry a lista opzioni
OPTIONS = [
    # ... opzioni esistenti 0-7 ...
    {
        "name": "Avvisi Soglie Punteggio",
        "key": "F9",
        "display_func": lambda: settings.get_score_warning_level_display()
    }
]
```

### Fase 4: Verificare Persistenza (5 min)

**Già implementato in PR #66**, verificare funzionamento:

✅ Metodo `settings.to_dict()` include `"score_warning_level"` (STRING format)  
✅ Metodo `settings.load_from_dict()` deserializza correttamente  
✅ File `settings.json` (o equivalente) salvato al cambio opzione  

**Test Manuale Persistenza**:
1. Avviare app → entrare opzioni → modificare livello via F9 (es. MINIMAL)
2. Confermare salvataggio (INVIO) → uscire app
3. Riaprire app → entrare opzioni → verificare livello = MINIMAL
4. Controllare file JSON (es. `cat ~/.config/acs/settings.json | grep score_warning`)

### Fase 5: Test Accessibilità (15 min)

**Checklist Test con NVDA**:

- [ ] F9 cicla correttamente tra 4 livelli (DISABLED → MINIMAL → BALANCED → COMPLETE → loop)
- [ ] TTS annuncia nome livello dopo ciclo (es. "Avvisi soglie punteggio: Equilibrati.")
- [ ] Display opzioni visualizza livello corrente
- [ ] Navigazione frecce (se menu usa frecce) funziona su opzione 9
- [ ] Tasto I (info/recap opzioni) include opzione 9
- [ ] ESC senza salvare resetta correttamente livello originale
- [ ] Conferma salva (INVIO) applica nuovo livello

**Test Funzionale Warnings** (con mapping verificato):

**Test 1 - DISABLED**:
1. Impostare livello DISABLED → iniziare partita
2. Pescare 25 volte (superare draw 21)
3. Riciclare 5 volte (superare recycle 3)
4. **Atteso**: NESSUN warning TTS emesso

**Test 2 - MINIMAL**:
1. Impostare livello MINIMAL → iniziare partita
2. Pescare 25 volte
3. **Atteso al draw 21**: Warning TTS "Attenzione: penalità pesca attiva..."
4. Riciclare 5 volte
5. **Atteso al recycle 3**: Warning TTS "Attenzione: penalità riciclo -10 punti"
6. **Totale warnings**: 2

**Test 3 - BALANCED**:
1. Impostare livello BALANCED → iniziare partita
2. Pescare 45 volte
3. **Atteso al draw 21**: Warning 1
4. **Atteso al draw 41**: Warning 2 "Penalità aumentata -2 punti"
5. Riciclare 5 volte
6. **Atteso al recycle 3**: Warning 3
7. **Atteso al recycle 4**: Warning 4 "Penalità aumentata -20 punti"
8. **Totale warnings**: 4

**Test 4 - COMPLETE**:
1. Impostare livello COMPLETE → iniziare partita
2. Pescare 45 volte
3. **Atteso al draw 20**: Pre-warning "Prossima pesca avrà penalità"
4. **Atteso al draw 21**: Warning "Penalità attiva -1pt"
5. **Atteso al draw 41**: Warning "Penalità aumentata -2pt"
6. Riciclare 6 volte
7. **Atteso al recycle 3**: Warning
8. **Atteso al recycle 4**: Warning
9. **Atteso al recycle 5**: Warning
10. **Totale warnings**: 6

---

## Commit Strategy (Singolo Commit Atomico)

```
fix(ui): expose score warning level option in options menu

Completes PR #66 implementation by adding UI binding for
score_warning_level option in options menu.

Changes:
- Add F9 key handler in [file_name] options menu
- Call existing cycle_score_warning_level() method (GameSettings)
- Update options display to show option 9 with current level
- Add TTS announcement for level changes
- Verify persistence already working (no changes needed)

Accessibility:
- Tested with NVDA screen reader
- Immediate TTS feedback on level change
- Display updates correctly show current level
- Keyboard-only navigation preserved

Files modified:
- [entry_point_file.py] (+12 lines: F9 handler with error handling)
- [options_formatter.py] (+1 line: option 9 in display template)

Testing:
- Manual accessibility tests with NVDA: PASSED
- Functional warnings tests (all 4 levels): PASSED
- Persistence test (save/load): PASSED
- Regression tests (other options): PASSED

No breaking changes.
No new dependencies.
Backward compatible (default BALANCED preserved).

Related: PR #66 (scoring warning system)
Closes: #ISSUE-WARNING-UI
```

---

## Effort Totale Stimato

| Fase | Descrizione | Tempo |
|------|-------------|-------|
| 1 | Identificare entry point | 10 min |
| 2 | Aggiungere handler F9 | 15 min |
| 3 | Aggiornare display opzioni | 20 min |
| 4 | Verificare persistenza | 5 min |
| 5 | Test accessibilità + funzionali | 15 min |
| **Totale** | | **65 min (~1 ora)** |

---

## Acceptance Criteria

### Funzionale
- [ ] Opzione 9 visibile nel menu opzioni
- [ ] Tasto F9 (o alternativa) cicla tra livelli
- [ ] Display mostra livello corrente (Disattivato/Minimo/Equilibrato/Completo)
- [ ] TTS annuncia cambio livello immediatamente
- [ ] Persistenza funziona (livello salvato tra sessioni)

### Accessibilità
- [ ] Navigazione screen reader funziona su opzione 9
- [ ] Feedback TTS immediato e chiaro
- [ ] Nessuna violazione WCAG (tastiera-only navigation OK)

### Testing
- [ ] Test manuali con NVDA completati (checklist sopra)
- [ ] Test funzionali warnings per 4 livelli OK (con mapping verificato)
- [ ] Nessuna regressione su altre opzioni menu

### Qualità Codice
- [ ] Zero breaking changes
- [ ] Coerente con pattern esistente (altri handler F1-F8)
- [ ] Type hints corretti (se file usa typing)
- [ ] Commit message descrittivo conforme Conventional Commits

---

## Rischi e Mitigazioni

### Rischio 1: Tasto F9 Conflitto
**Probabilità**: BASSA  
**Impact**: BASSO  
**Mitigazione**: Se F9 già usato, usare F10 o Shift+F8. Documentare nel commit.

### Rischio 2: Entry Point Non Ovvio
**Probabilità**: MEDIA  
**Impact**: MEDIO (ritardo identificazione)  
**Mitigazione**: Grep per pattern `pygame.K_F` nel repository. Verificare file root.

### Rischio 3: Display Formatter Complesso
**Probabilità**: BASSA  
**Impact**: BASSO  
**Mitigazione**: Formatter già esiste per altre opzioni. Replicare pattern esistente.

### Rischio 4: Path TTS Sintassi Diversa
**Probabilità**: BASSA  
**Impact**: BASSO (facile fix)  
**Mitigazione**: Verificare path TTS in Fase 1 cercando esempi nel file entry point.

---

## Definition of Done

1. ✅ Codice committato su branch `fix/ui-warning-level-option`
2. ✅ Test manuali accessibilità con NVDA passati (7 checklist items)
3. ✅ Test funzionali warnings per 4 livelli OK (4 test scenarios)
4. ✅ Persistenza verificata (salvataggio/caricamento/retrocompat)
5. ✅ Nessuna regressione rilevata su altre 8 opzioni
6. ✅ Commit message conforme a Conventional Commits
7. ✅ PR aperta con descrizione dettagliata + link a questo piano
8. ✅ Screenshot/video demo (opzionale, se richiesto)

---

## Next Steps Immediati

1. **Identificare file entry point** - `grep -r "pygame.K_F" *.py`
2. **Verificare tasto F9 libero** - controllare conflitti nel file identificato
3. **Verificare path TTS** - cercare esempi `screen_reader.tts.speak()` nel codice
4. **Implementare handler** (~12 righe codice con error handling)
5. **Aggiornare display** (1 riga nel template opzioni)
6. **Testare con NVDA** (checklist 7 items + 4 scenari funzionali)
7. **Committare** (singolo commit atomico conforme Conventional Commits)
8. **Aprire PR** con link a questo piano

---

## Changelog Verifica

**v1.0** (16/02/2026 15:00) - Piano iniziale creato  
**v1.1** (16/02/2026 15:20) - Aggiunta sezione "Verifica Tecnica Pre-Implementazione"  
- Confermati riferimenti `ScoreWarningLevel`, `cycle_score_warning_level()`, persistenza
- Chiarito mapping soglie warnings (MINIMAL: recycle 3, non 4)
- Aggiunti test scenari dettagliati con mapping verificato
- Espanso error handling nel codice esempio
- Aggiunto grep command per identificazione entry point

---

**Piano pronto per implementazione** 🚀  
**Effort**: ~1 ora  
**Rischio**: BASSO  
**Valore**: ALTO (completa feature accessibilità PR #66)  
**Stato Verifica**: ✅ APPROVATO - Tutti i riferimenti tecnici confermati
