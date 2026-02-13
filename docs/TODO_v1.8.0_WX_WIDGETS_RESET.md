# 📋 TODO – Native wx Widgets + Reset Gameplay (v1.8.0)

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo**: FEATURE + FIX  
**Priorità**: HIGH  
**Stato**: READY → IN PROGRESS

---

## 📖 Riferimento Documentazione

**OBBLIGATORIO** consultare prima di implementare:

📄 **Piano Completo**: [`docs/WX_OPTIONS_WIDGETS_RESET_GAMEPLAY_v1.8.0.md`](./WX_OPTIONS_WIDGETS_RESET_GAMEPLAY_v1.8.0.md)

> Questo file TODO è solo un **sommario operativo** per consultazione rapida durante implementazione.  
> Il piano completo contiene analisi dettagliata, codice esatto, testing checklist e architettura.

---

## 🎯 Obiettivo Implementazione

**Feature Principale**: Convertire OptionsDialog da virtuale (audio-only) a **native wx widgets** (RadioBox, CheckBox, ComboBox) per tutte le 8 opzioni.

**Bug Fix Critico**: Garantire `engine.reset_game()` in **tutti** gli scenari di abbandono partita (ESC, doppio ESC, timeout STRICT, rifiuto rematch).

**Impatto**:
- ✅ Accessibilità NVDA perfetta (widget nativi letti automaticamente)
- ✅ UI visibile per mouse users (click su widget)
- ✅ Navigazione standard wxPython (TAB + frecce)
- ✅ Stato gioco sempre pulito dopo abbandono

---

## 📂 File Coinvolti

- `src/infrastructure/ui/options_dialog.py` → **MODIFY** (rewrite completo UI)
- `test.py` → **MODIFY** (`show_options()` + 4 metodi reset)
- `CHANGELOG.md` → **UPDATE** (release notes v1.8.0)

---

## 🛠 Checklist Implementazione (6 STEP)

### ✅ STEP 1: Widget Nativi Opzioni 1-4
- [ ] Rimuovi `EVT_CHAR_HOOK` per navigazione virtuale (frecce/numeri)
- [ ] Riscrivi `_create_ui()` con RadioBox (Tipo Mazzo, Difficoltà, Carte Pescate)
- [ ] Aggiungi CheckBox + ComboBox per Timer (enable + durata)
- [ ] Aggiungi `_load_settings_to_widgets()` per prime 4 opzioni
- [ ] Chiama load in `_create_ui()`
- [ ] **Commit**: `feat(options): add native wx widgets for options 1-4`

### ✅ STEP 2: Widget Nativi Opzioni 5-8 + Pulsanti
- [ ] Estendi `_create_ui()` con RadioBox (Riciclo Scarti, Modalità Timer)
- [ ] Aggiungi CheckBox standalone (Suggerimenti, Punti)
- [ ] Aggiungi pulsanti Salva/Annulla con mnemonics (ALT+S, ALT+A)
- [ ] Estendi `_load_settings_to_widgets()` per ultime 4 opzioni
- [ ] Chiama `Fit()` per auto-resize dialog
- [ ] **Commit**: `feat(options): add native wx widgets for options 5-8 and buttons`

### ✅ STEP 3: Event Binding + Live Sync
- [ ] Aggiungi `_bind_widget_events()` (collega tutti i widget)
- [ ] Aggiungi `on_setting_changed()` (live update + DIRTY tracking)
- [ ] Aggiungi `on_timer_toggled()` (enable/disable ComboBox)
- [ ] Aggiungi `on_save_click()` / `on_cancel_click()`
- [ ] Aggiungi `_save_widgets_to_settings()` (widget → settings mapping)
- [ ] Chiama binding in `_create_ui()`
- [ ] **Commit**: `feat(options): implement widget event binding and settings sync`

### ✅ STEP 4: ESC Intelligente + open_window()
- [ ] Aggiungi `on_key_down()` con ESC smart (chiama `close_window()`)
- [ ] Bind `EVT_CHAR_HOOK` in `__init__` per ESC
- [ ] Modifica `show_options()` in test.py (aggiungi `open_window()` call)
- [ ] Vocalizza opening message con TTS
- [ ] Log dialog result (OK/CANCEL)
- [ ] **Commit**: `feat(options): implement smart ESC with save confirmation`

### ✅ STEP 5: Fix Reset Gameplay (4 scenari)
- [ ] `show_abandon_game_dialog()`: Aggiungi `engine.reset_game()` prima di `return_to_menu()`
- [ ] `confirm_abandon_game()`: Aggiungi reset (doppio ESC)
- [ ] `_handle_game_over_by_timeout()`: Aggiungi reset (timeout STRICT)
- [ ] `handle_game_ended()`: Aggiungi reset se user rifiuta rematch
- [ ] Aggiungi log console per ogni reset
- [ ] **Commit**: `fix(gameplay): add explicit reset_game() on all abandon scenarios`

### ✅ STEP 6: Aggiorna CHANGELOG.md
- [ ] Aggiungi sezione `## [1.8.0] - 2026-02-13` in cima
- [ ] Sezioni: Added, Fixed, Changed, Removed, Technical, Migration Notes, Breaking Changes
- [ ] **Commit**: `docs(changelog): add v1.8.0 release notes`

---

## 🧪 Testing Rapido (Post-Implementation)

### Test Critici (Fai Questi)
- [ ] **Widget Visibili**: Apri opzioni → vedi 8 widget + 2 pulsanti
- [ ] **TAB Navigation**: TAB passa tra widget, frecce cambiano valore
- [ ] **Timer Enable/Disable**: CheckBox timer abilita/disabilita ComboBox
- [ ] **Salva/Annulla**: Modifiche persistono con Salva, rollback con Annulla
- [ ] **ESC Senza Modifiche**: Chiude direttamente
- [ ] **ESC Con Modifiche**: Mostra dialog conferma (Sì/No/Annulla)
- [ ] **Reset ESC**: Abbandona partita → verifica console log reset
- [ ] **Reset Doppio ESC**: ESC 2x veloce → verifica reset
- [ ] **Reset Timeout**: Timer scade (STRICT) → verifica reset
- [ ] **Reset No Rematch**: Vinci + clicca Menu → verifica reset

### Test Completi (Se Hai Tempo)
Vedi checklist completa (20 test) nel piano: sezione "Testing Checklist Completo"

---

## ✅ Criteri di Completamento

L'implementazione è considerata **DONE** quando:

- ✅ Tutti i 6 STEP completati con commit corretto per ognuno
- ✅ Widget nativi funzionano (TAB navigation + click mouse)
- ✅ ESC intelligente funziona (conferma se DIRTY)
- ✅ Reset gameplay garantito in tutti i 4 scenari
- ✅ CHANGELOG.md aggiornato con v1.8.0
- ✅ Almeno i 10 test critici passano

---

## 📝 Aggiornamenti Obbligatori (già nel piano)

- ✅ `CHANGELOG.md` aggiornato (STEP 6)
- ✅ Versione incrementata: `1.7.5 → 1.8.0` (MINOR)
- ✅ Commit messages convenzionali (già nel piano)
- ✅ Push su branch `copilot/remove-pygame-migrate-wxpython`

---

## 🚨 Breaking Changes

**ATTENZIONE**: Navigazione opzioni **completamente riscritta**:

❌ **Rimosso**:
- Frecce SU/GIÙ per navigare tra opzioni
- Numeri 1-8 per saltare a opzione
- Comandi T/+/-/I/H (funzionalità spostate in widget)

✅ **Nuovo**:
- TAB per navigare tra widget
- Frecce SU/GIÙ per cambiare valore **dentro** widget corrente
- SPACE per toggle CheckBox
- Mouse click su tutti i widget

---

## 📌 Note Rapide

### Widget Mapping (8 opzioni)
1. **Tipo Mazzo** → RadioBox (Francese/Napoletano)
2. **Difficoltà** → RadioBox (1/2/3 carte)
3. **Carte Pescate** → RadioBox (1/2/3)
4. **Timer** → CheckBox (enable) + ComboBox (5-60 min)
5. **Riciclo Scarti** → RadioBox (Inversione/Mescolata)
6. **Suggerimenti** → CheckBox (ON/OFF)
7. **Sistema Punti** → CheckBox (ON/OFF)
8. **Modalità Timer** → RadioBox (STRICT/PERMISSIVE)

### Reset Gameplay (4 scenari)
1. **ESC + conferma Sì** → `show_abandon_game_dialog()`
2. **Doppio ESC (< 2s)** → `confirm_abandon_game()`
3. **Timeout STRICT** → `_handle_game_over_by_timeout()`
4. **Rifiuto rematch** → `handle_game_ended()`

### Commit Sequence
```
1. feat(options): add native wx widgets for options 1-4
2. feat(options): add native wx widgets for options 5-8 and buttons
3. feat(options): implement widget event binding and settings sync
4. feat(options): implement smart ESC with save confirmation
5. fix(gameplay): add explicit reset_game() on all abandon scenarios
6. docs(changelog): add v1.8.0 release notes
```

---

## 🎯 Stato Attuale

**Ultimo aggiornamento**: 2026-02-13 18:00 CET

### Progresso Globale: 6/6 STEP (100%) ✅ COMPLETE

| STEP | Stato | Commit SHA | Note |
|------|-------|------------|------|
| 1 | ✅ COMPLETE | 699a8b2 | Widget opzioni 1-4 |
| 2 | ✅ COMPLETE | bd51240 | Widget opzioni 5-8 + pulsanti |
| 3 | ✅ COMPLETE | ace0024 | Event binding + sync |
| 4 | ✅ COMPLETE | 3436fe0 | ESC smart + open_window() |
| 5 | ✅ COMPLETE | 8e4f57b | Reset gameplay fixes |
| 6 | ✅ COMPLETE | ce7e8eb | CHANGELOG update |

### Implementazione Completata! 🎉
✅ **Tutti i 6 STEP completati con successo**
✅ **Tutti i commit pushed su branch**
✅ **CHANGELOG.md aggiornato con v1.8.0**
✅ **Pronto per review e merge**

---

**Fine TODO v1.8.0**

Implementazione completata al 100%!
Il documento completo (`WX_OPTIONS_WIDGETS_RESET_GAMEPLAY_v1.8.0.md`) resta la fonte di verità tecnica.