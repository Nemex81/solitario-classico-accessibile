# Piano Integrazione UI - Opzione Avvisi Malus

**Data**: 16 Febbraio 2026  
**Versione Target**: v2.6.1 (fix addizionale indipendente)  
**Branch**: `fix/ui-warning-level-option`  
**Priorità**: MEDIA (enhancement accessibilità)  
**Dipendenze**: PR #66 (sistema warning levels già implementato)  

---

## Executive Summary

Il sistema di livelli di verbosità warnings è **completamente implementato** a livello architetturale (Domain, GameSettings, ScoringService), ma manca l'**esposizione nell'interfaccia utente** del menu Opzioni.

### Stato Attuale (Implementato in PR #66)

✅ **Domain Layer**: `ScoreWarningLevel` enum (4 livelli)  
✅ **GameSettings**: `cycle_score_warning_level()` e `get_score_warning_level_display()`  
✅ **ScoringService**: Warnings level-aware con tag-based detection  
✅ **GameEngine**: TTS warnings integrati in `_announce_draw_threshold_warning()`  
✅ **Persistenza**: Serializzazione/deserializzazione funzionante  

⚠️ **MANCA**: Binding UI nel menu opzioni (tasto F9 o equivalente)

### Obiettivo Fix

Aggiungere **Opzione 9** nel menu Opzioni principale:
- **Nome**: "Avvisi Soglie Punteggio"
- **Tasto**: F9 (o alternativa se conflitto)
- **Comportamento**: Cicla tra DISABLED → MINIMAL → BALANCED → COMPLETE
- **Display**: Visualizza livello corrente (es. "Equilibrati")

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
```python
# Cerca nel repository per pattern tipo:
if event.key == pygame.K_F8:  # Opzione esistente
    success, msg = engine.settings.cycle_*()  # Pattern da replicare
```

**File Candidati**:
- `acs.py` (probabile main application)
- `test.py` (se è entry point development)
- `src/application/game_controller.py` (se esiste controller centralizzato)

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
```

**Note Implementative**:
- **Tasto**: F9 (verificare se libero, altrimenti F10 o altro)
- **Interrupt**: `True` per feedback immediato (come altre opzioni)
- **Metodo**: `cycle_score_warning_level()` **già implementato** in GameSettings
- **TTS Path**: Verificare sintassi corretta `engine.screen_reader.tts.speak()`

### Fase 3: Aggiornare Display Opzioni (20 min)

**Se esiste `OptionsFormatter` o equivalente**:

```python
# In metodo get_options_display() o template stringa
options_text = f"""
Opzioni di Gioco:
1. Difficoltà: {settings.get_difficulty_display()} (F1)
2. Pescate: {settings.get_draw_count_display()} (F2)
...
8. [Opzione Esistente] (F8)
9. Avvisi Soglie Punteggio: {settings.get_score_warning_level_display()} (F9)

Premi ESC per uscire senza salvare.
"""
```

**Se display dinamico**:
```python
# Aggiungere entry a lista opzioni
OPTIONS = [
    # ... opzioni esistenti ...
    {
        "name": "Avvisi Soglie Punteggio",
        "key": "F9",
        "display_func": lambda: settings.get_score_warning_level_display()
    }
]
```

### Fase 4: Verificare Persistenza (5 min)

**Già implementato in PR #66**, ma verificare che:

✅ Metodo `settings.to_dict()` include `"score_warning_level"`  
✅ Metodo `settings.load_from_dict()` deserializza correttamente  
✅ File `settings.json` (o equivalente) salvato al cambio opzione  

**Test Manuale**:
1. Modificare opzione via F9 → cambiare livello → uscire app
2. Riaprire app → verificare che livello sia persistito

### Fase 5: Test Accessibilità (15 min)

**Checklist Test con NVDA**:

- [ ] F9 cicla correttamente tra 4 livelli (DISABLED → MINIMAL → BALANCED → COMPLETE → loop)
- [ ] TTS annuncia nome livello dopo ciclo (es. "Avvisi soglie punteggio: Equilibrati.")
- [ ] Display opzioni visualizza livello corrente
- [ ] Navigazione frecce (se menu usa frecce) funziona su opzione 9
- [ ] Tasto I (info/recap opzioni) include opzione 9
- [ ] ESC senza salvare resetta correttamente livello originale
- [ ] Conferma salva applica nuovo livello

**Test Funzionale Warnings**:
1. Impostare livello DISABLED → giocare → superare soglia draw 21 → **NO warning**
2. Impostare livello MINIMAL → giocare → superare soglia draw 21 → **warning vocale**
3. Impostare livello BALANCED → giocare → superare draw 21 e 41 → **2 warnings**
4. Impostare livello COMPLETE → giocare → superare draw 20, 21, 41 → **3 warnings**

---

## Commit Strategy (Singolo Commit Atomico)

```
fix(ui): expose score warning level option in options menu

Completes PR #66 implementation by adding UI binding for
score_warning_level option in options menu.

Changes:
- Add F9 key handler in [file_name] options menu
- Call existing cycle_score_warning_level() method
- Update options display to show option 9 with current level
- Add TTS announcement for level changes
- Verify persistence already working (no changes needed)

Accessibility:
- Tested with NVDA screen reader
- Immediate TTS feedback on level change
- Display updates correctly show current level

Files modified:
- [entry_point_file.py] (+10 lines: F9 handler)
- [options_formatter.py] (+5 lines: display update)

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
- [ ] Test manuali con NVDA completati
- [ ] Test funzionali warnings per ogni livello OK
- [ ] Nessuna regressione su altre opzioni menu

### Qualità Codice
- [ ] Zero breaking changes
- [ ] Coerente con pattern esistente (altri handler F1-F8)
- [ ] Type hints corretti (se file usa typing)
- [ ] Commit message descrittivo

---

## Rischi e Mitigazioni

### Rischio 1: Tasto F9 Conflitto
**Probabilità**: BASSA  
**Impact**: BASSO  
**Mitigazione**: Se F9 già usato, usare F10 o Shift+F8. Documentare nel commit.

### Rischio 2: Entry Point Non Ovvio
**Probabilità**: MEDIA  
**Impact**: MEDIO (ritardo identificazione)  
**Mitigazione**: Grep per pattern `pygame.K_F` nel repository. Chiedere conferma su file principale.

### Rischio 3: Display Formatter Complesso
**Probabilità**: BASSA  
**Impact**: BASSO  
**Mitigazione**: Formatter già esiste per altre opzioni. Replicare pattern.

---

## Definition of Done

1. ✅ Codice committato su branch `fix/ui-warning-level-option`
2. ✅ Test manuali accessibilità con NVDA passati
3. ✅ Test funzionali warnings per 4 livelli OK
4. ✅ Persistenza verificata (salvataggio/caricamento)
5. ✅ Nessuna regressione rilevata
6. ✅ Commit message conforme a Conventional Commits
7. ✅ PR aperta con descrizione dettagliata
8. ✅ Screenshot/video demo (se richiesto)

---

## Next Steps Immediati

1. **Identificare file entry point** (cerca pattern `pygame.K_F` in `*.py`)
2. **Verificare tasto F9 libero** (o scegliere alternativa)
3. **Implementare handler** (10 righe codice)
4. **Testare con NVDA** (15 minuti)
5. **Committare** (singolo commit atomico)
6. **Aprire PR** con link a questo piano

---

**Piano pronto per implementazione** 🚀  
**Effort**: ~1 ora  
**Rischio**: BASSO  
**Valore**: ALTO (completa feature accessibilità PR #66)
