# ✅ TODO - BUG #67 & #68 FIXES

> **Checklist Implementazione Rapida**  
> **Versione**: v2.4.2  
> **Branch**: `copilot/refactor-difficulty-options-system`  
> **Data**: 14 Febbraio 2026

---

## 📖 DOCUMENTAZIONE COMPLETA

**⚠️ IMPORTANTE**: Per dettagli completi su ogni modifica (codice completo, rationale, test cases), consulta sempre:

**👉 [`docs/PIANO_IMPLEMENTAZIONE_BUG_67_68.md`](./PIANO_IMPLEMENTAZIONE_BUG_67_68.md)**

Questo file contiene:
- ✅ Codice completo per ogni metodo
- ✅ Analisi tecnica dettagliata
- ✅ Test cases con assert completi
- ✅ Acceptance criteria
- ✅ Istruzioni testing manuale

---

## 🐛 BUG #67: Options Dialog Non Applica Preset

**Problema**: Cambiare difficoltà non aggiorna i widget né applica i preset

### ✅ Commit #1: Fix Preset Application

**File**: `src/infrastructure/ui/options_dialog.py`

#### **Modifica 1: Aggiorna `on_setting_changed()`** (~linea 382)
- [ ] Aggiungi check `if event.GetEventObject() == self.difficulty_radio:`
- [ ] Dentro l'if: chiama `preset = self.options_controller.settings.get_current_preset()`
- [ ] Chiama `preset.apply_to(self.options_controller.settings)`
- [ ] Chiama `self._load_settings_to_widgets()` per refresh
- [ ] Chiama `self._update_widget_lock_states()` per disable locked
- [ ] (Opzionale) TTS announcement: `"<preset.name> applicato. <locked_count> opzioni bloccate"`
- [ ] Aggiorna docstring con v2.4.2 e Bug #67 reference

#### **Modifica 2: Aggiungi `_update_widget_lock_states()`** (~linea 450)
- [ ] Crea nuovo metodo dopo `_save_widgets_to_settings()`
- [ ] Get preset: `preset = self.options_controller.settings.get_current_preset()`
- [ ] Per ogni widget:
  - [ ] `self.draw_count_radio.Enable(not preset.is_locked("draw_count"))`
  - [ ] `self.timer_combo.Enable(not preset.is_locked("max_time_game"))`
  - [ ] `self.shuffle_radio.Enable(not preset.is_locked("shuffle_discards"))`
  - [ ] `self.command_hints_check.Enable(not preset.is_locked("command_hints_enabled"))`
  - [ ] `self.scoring_check.Enable(not preset.is_locked("scoring_enabled"))`
  - [ ] `self.timer_strict_radio.Enable(not preset.is_locked("timer_strict_mode"))`
- [ ] Forza enable: `self.deck_type_radio.Enable(True)` e `self.difficulty_radio.Enable(True)`
- [ ] Docstring completo con esempi

#### **Modifica 3: Aggiorna `_load_settings_to_widgets()`** (~linea 350)
- [ ] Alla FINE del metodo esistente, aggiungi: `self._update_widget_lock_states()`
- [ ] Aggiorna docstring: "Version: v2.4.2 - Added lock state update call"

### 📋 Testing Bug #67
- [ ] **Test Case 1**: Cambia Level 1 → Level 5
  - [ ] Timer combo aggiornato a "15 minuti"
  - [ ] Draw count aggiornato a "3 carte"
  - [ ] Widget bloccati disabilitati (grayed out)
- [ ] **Test Case 2**: Cambia Level 5 → Level 1
  - [ ] Timer combo aggiornato a "0 minuti"
  - [ ] Widget sbloccati riabilitati
- [ ] **Test Case 3**: Apri dialog con Level 5 già impostato
  - [ ] Widget bloccati già disabilitati all'apertura
- [ ] Test manuale con NVDA screen reader
- [ ] Testare tutti i 5 livelli di difficoltà

### ✅ Definition of Done - Bug #67
- [ ] Codice implementato come da piano
- [ ] Docstrings complete
- [ ] Type hints corretti
- [ ] Tutti i test case passano
- [ ] Nessuna regressione

---

## 🐛 BUG #68: Dialog "Vuoi Rigiocare?" - Crash

**Problema**: Crash quando utente clicca NO su "Vuoi giocare ancora?"

### ✅ Commit #2: Fix Decline Rematch Crash

**File 1**: `acs_wx.py`

#### **Modifica 1: Fix `handle_game_ended()`** (~linea 605-620)
- [ ] Linea ~614 (rematch=True): Cambia `self.app.CallAfter` → `wx.CallAfter`
- [ ] Linea ~620 (rematch=False): Cambia `self.app.CallAfter` → `wx.CallAfter`
- [ ] Linea ~620: Cambia `_safe_decline_to_menu` → `_safe_return_to_main_menu`
- [ ] Aggiorna docstring con v2.4.2 e Bug #68 reference
- [ ] Aggiungi commenti separatori per rematch=True/False

#### **Modifica 2: Aggiungi `_safe_return_to_main_menu()`** (~linea 625)
- [ ] Crea nuovo metodo dopo `handle_game_ended()`
- [ ] Step 1: `self.engine.service.reset_game()` + log
- [ ] Step 2: `self.view_manager.show_panel("menu")` + log
- [ ] Step 3: TTS announcement (se disponibile)
- [ ] Docstring completo con esempio e rationale CallAfter
- [ ] Log dettagliati per ogni step

**File 2**: `src/infrastructure/ui/wx_dialog_provider.py`

#### **Modifica 3: Fix `show_yes_no_async()`** (~linea 276)
- [ ] Prima di `wx.CallAfter()`, aggiungi check:
  ```python
  app = wx.GetApp()
  if app and app.IsMainLoopRunning():
      wx.CallAfter(show_modal_and_callback)
  else:
      print("⚠️ wx.App not active, skipping async dialog")
      callback(False)
  ```
- [ ] Aggiorna docstring con v2.4.2 e Bug #68.3 reference
- [ ] Documenta safety check nel docstring

### 📋 Testing Bug #68
- [ ] **Test Case 1**: Win game → Decline rematch
  - [ ] Nessun crash
  - [ ] Ritorno al menu principale
  - [ ] TTS annuncia "Sei tornato al menu principale"
- [ ] **Test Case 2**: Win game → Accept rematch
  - [ ] Nuova partita inizia correttamente
  - [ ] Nessun crash
- [ ] **Test Case 3**: Chiusura app durante dialog (ALT+F4)
  - [ ] Nessun crash durante cleanup
  - [ ] Nessun AssertionError "No wx.App created yet"
- [ ] Test con vittoria (CTRL+ALT+W)
- [ ] Test con sconfitta (timer scaduto)

### ✅ Definition of Done - Bug #68
- [ ] Codice implementato come da piano
- [ ] Docstrings complete
- [ ] Type hints corretti
- [ ] Tutti i test case passano
- [ ] Nessuna regressione

---

## 📊 RIEPILOGO MODIFICHE

| File | Modifiche | Linee ~Nuove |
|------|-----------|-------------|
| `src/infrastructure/ui/options_dialog.py` | 3 modifiche | ~75 |
| `acs_wx.py` | 2 modifiche | ~40 |
| `src/infrastructure/ui/wx_dialog_provider.py` | 1 modifica | ~10 |
| **TOTALE** | **6 modifiche** | **~125** |

---

## 🚀 WORKFLOW IMPLEMENTAZIONE

### Step 1: Implementa Bug #67
```bash
# Branch già esistente
git checkout copilot/refactor-difficulty-options-system

# Modifica options_dialog.py (3 modifiche)
# Testa manualmente

git add src/infrastructure/ui/options_dialog.py
git commit -m "fix(ui): apply preset values when difficulty changes in Options Dialog

- Intercept difficulty_radio change in on_setting_changed()
- Call preset.apply_to(settings) to apply preset values
- Refresh ALL widgets via _load_settings_to_widgets()
- Add _update_widget_lock_states() to disable locked widgets
- Add TTS announcement for preset application

Fixes #67 - Options Dialog preset application
Version: v2.4.2"
```

### Step 2: Implementa Bug #68
```bash
# Stesso branch

# Modifica acs_wx.py (2 modifiche)
# Modifica wx_dialog_provider.py (1 modifica)
# Testa manualmente

git add acs_wx.py src/infrastructure/ui/wx_dialog_provider.py
git commit -m "fix(app): fix decline rematch crash and return to main menu

- Fix self.app.CallAfter → wx.CallAfter (global function)
- Create _safe_return_to_main_menu() method
- Add wx.App safety check in wx_dialog_provider.py
- Return to main menu when user declines rematch

Fixes #68 - Decline rematch crash
Version: v2.4.2"
```

### Step 3: Testing Finale
```bash
# Test completo manuale
python acs_wx.py

# Bug #67
# - Premi O (Options)
# - Cambia difficoltà da 1 a 5
# - Verifica widget aggiornati e bloccati

# Bug #68
# - Nuova partita
# - CTRL+ALT+W (force victory)
# - Clicca NO su rematch
# - Verifica ritorno al menu (no crash)
```

### Step 4: Push e PR
```bash
git push origin copilot/refactor-difficulty-options-system

# Crea PR su GitHub
# Titolo: "fix: Options Dialog preset & decline rematch crash (Bug #67, #68)"
# Descrizione: Link a questo TODO e al PIANO_IMPLEMENTAZIONE
```

---

## ✅ ACCEPTANCE CRITERIA GLOBALE

### Bug #67
- [ ] ✅ Cambiare difficoltà aggiorna TUTTI i widget automaticamente
- [ ] ✅ Preset valori applicati correttamente (timer, draw_count, shuffle, ecc.)
- [ ] ✅ Widget bloccati disabilitati visivamente (grayed out)
- [ ] ✅ Widget bloccati già disabilitati quando si apre dialog
- [ ] ✅ Funziona con tutti i 5 livelli di difficoltà
- [ ] ✅ Nessuna regressione su altre opzioni

### Bug #68
- [ ] ✅ Nessun crash quando utente clicca NO su rematch
- [ ] ✅ Ritorno al menu principale dopo decline
- [ ] ✅ TTS annuncia "Sei tornato al menu principale"
- [ ] ✅ Nuova partita inizia correttamente se utente clicca YES
- [ ] ✅ Nessun crash durante chiusura app (ALT+F4)
- [ ] ✅ Funziona sia con vittoria che con sconfitta

### Generale
- [ ] ✅ Codice pulito e ben documentato
- [ ] ✅ Test manuali passano
- [ ] ✅ NVDA screen reader compatibile
- [ ] ✅ Log chiari per debugging
- [ ] ✅ Zero regressioni su altre funzionalità

---

## 📞 RIFERIMENTI

- **Piano Completo**: [`docs/PIANO_IMPLEMENTAZIONE_BUG_67_68.md`](./PIANO_IMPLEMENTAZIONE_BUG_67_68.md)
- **Architecture**: [`docs/ARCHITECTURE.md`](./ARCHITECTURE.md)
- **Preset Implementation**: `src/domain/models/difficulty_preset.py`
- **Options Dialog**: `src/infrastructure/ui/options_dialog.py`
- **Main App**: `acs_wx.py`

**Issues**:
- #67 - Options Dialog preset application
- #68 - Decline rematch crash
- #62 - PR originale preset system

**Version**: v2.4.2  
**Branch**: `copilot/refactor-difficulty-options-system`  
**Status**: ⏳ Pending - 0/2 Commits Completati  
**Last Update**: 2026-02-14 21:53 CET

---

**🎯 RICORDA**: Consulta sempre il piano completo per codice e dettagli!
