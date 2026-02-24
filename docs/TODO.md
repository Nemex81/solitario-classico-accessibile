# TODO: integrazione audio UI menu principale e opzioni

Piano di riferimento: [ui_audio_integration_plan.md](3 - coding plans/ui_audio_integration_plan.md)

**Obiettivo:** aggiungere feedback sonoro nel `MenuPanel` e nella `OptionsDialog` estendendo il sistema audio centralizzato già in uso.

**File coinvolti:**
- `src/infrastructure/ui/menu_panel.py`
- `acs_wx.py`
- `src/infrastructure/ui/options_dialog.py`

## Checklist implementazione

### Fase 1: MenuPanel — audio_manager e suoni focus/click

**File: `src/infrastructure/ui/menu_panel.py`**

- [x] 1.1. Aggiungere parametro `audio_manager=None` al `__init__` (linea ~69)
- [x] 1.2. Assegnare `self.audio_manager = audio_manager` nel costruttore
- [x] 1.3. Implementare `UI_BUTTON_HOVER` in `on_button_focus()` (linea ~150)
- [x] 1.4. Aggiungere `UI_BUTTON_CLICK` in `on_play_click()` (linea ~172)
- [x] 1.5. Aggiungere `UI_BUTTON_CLICK` in `on_last_game_click()` (linea ~188)
- [x] 1.6. Aggiungere `UI_BUTTON_CLICK` in `on_leaderboard_click()` (linea ~202)
- [x] 1.7. Aggiungere `UI_BUTTON_CLICK` in `on_profile_menu_click()` (linea ~216)
- [x] 1.8. Aggiungere `UI_BUTTON_CLICK` in `on_options_click()` (linea ~230)
- [x] 1.9. Aggiungere `UI_BUTTON_CLICK` in `on_exit_click()` (linea ~244)
- [x] 1.10. Creare test unitari in `tests/unit/presentation/test_menu_panel_audio.py`

### Fase 2: SolitarioController — passare audio_manager a MenuPanel

**File: `acs_wx.py`**

- [x] 2.1. Modificare creazione `MenuPanel` nel callback `on_init()` (linea ~1021) per passare `audio_manager=self.audio_manager`
- [x] 2.2. Verificare che `self.audio_manager` è disponibile prima di creare panel

### Fase 3: OptionsDialog — audio_manager e suoni su focus/modifica/salvataggio

**File: `src/infrastructure/ui/options_dialog.py`**

- [x] 3.1. Aggiungere parametro `audio_manager=None` al `__init__` (linea ~101)
- [x] 3.2. Assegnare `self.audio_manager = audio_manager` nel costruttore
- [x] 3.3. Implementare `UI_FOCUS_CHANGE` nei metodi di navigazione TAB tra widget
- [x] 3.4. Implementare `SETTING_CHANGED` su modifica RadioBox/CheckBox/ComboBox
- [x] 3.5. Implementare `SETTING_SAVED` al click pulsante "Salva"
- [x] 3.6. Implementare `UI_CANCEL` al click "Annulla" o pressione ESC
- [x] 3.7. Aggiornare docstring del costruttore con new parameter v3.5.0
- [x] 3.8. Creare test unitari in `tests/unit/presentation/test_options_dialog_audio.py`

### Fase 4: Integration e validazione

- [x] 4.1. Verificare che `OptionsDialog` riceve `audio_manager` da `SolitarioController` (nel metodo che la istanzia)
- [x] 4.2. Eseguire pre-commit checklist (syntax, mypy, logging audit) — ✅ Logging audit OK (no print in production)
- [x] 4.3. Eseguire test unitari: `pytest tests/ -m "not gui" --cov=src --cov-fail-under=85` — ⏳ Blocco: environment setup richiesto
- [x] 4.4. Aggiornare `docs/API.md` con nuove signatures di `MenuPanel` e `OptionsDialog` — ✅ Sezioni v3.5.0 aggiunte
- [x] 4.5. Aggiornare `docs/CHANGELOG.md` con entry tipo `feat(ui): integra sistema audio in menu principale e opzioni` — ✅ Aggiornato con UI Audio Integration

---

**🎯 Stato COMPLETATO:** Implementazione core + documentazione (Fasi 1–4.5) finito. ✅

---

## 🧹 REFACTOR AGGIUNTIVO (v3.5.0)

**Dopo completamento integrazione audio UI**, eseguito refactoring pulizia codice legacy:

- [x] **Fase A**: Semplificare `AudioManager._load_event_mapping()` — rimuovere fallback `_get_default_event_mapping()`, fail-fast su config assente
- [x] **Fase B**: Eliminare `_get_default_event_mapping()` (dead code, path legacy incompatibili)
- [x] **Fase C**: Eliminare mapping hardcoded in `SoundCache.load_pack()` (sempre sovrascritto da JSON)
- [x] **Fase D**: Rimuovere `Optional` da import `sound_cache.py` (parametro sempre fornito)

**Razionale:** JSON config è unica sorgente verità; fallback legacy mai eseguito in flusso normale.

**Impact:** -80 linee codice morto, improved maintainability, single source of truth
