# 📋 TODO – Window Management Migration v2.2 (v2.2.0)
Branch: copilot/remove-pygame-migrate-wxpython
Tipo: REFACTOR
Priorità: HIGH
Stato: READY

## 📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
**docs/IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md**

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

## 🎯 Obiettivo Implementazione
Port del pattern architetturale da hs_deckmanager:
• **Dependency Injection** - DependencyContainer per IoC
• **Factory Pattern** - ViewFactory e WidgetFactory per UI creation
• **WindowController** - Gestione gerarchica finestre con parent stack
• **Async Dialog API** - Dialog non-blocking con callback pattern (elimina nested event loops)
• **Benefici**: Migliore testabilità, manutenibilità, scalabilità, eliminazione ShowModal() issues

## 📂 File Coinvolti

### NEW (Infrastructure - DI)
• `src/infrastructure/di/__init__.py` → CREATE
• `src/infrastructure/di/dependency_container.py` → CREATE

### NEW (Infrastructure - Factories)
• `src/infrastructure/ui/factories/__init__.py` → CREATE
• `src/infrastructure/ui/factories/view_factory.py` → CREATE
• `src/infrastructure/ui/factories/widget_factory.py` → CREATE

### NEW (Infrastructure - WindowController)
• `src/infrastructure/ui/window_controller.py` → CREATE

### MODIFY (Application Layer)
• `test.py` → MODIFY (DI integration, async dialog migration)
• `src/application/dialog_manager.py` → MODIFY (add async methods)

### MODIFY (Infrastructure Layer)
• `src/infrastructure/ui/menu_panel.py` → MODIFY (accept container)
• `src/infrastructure/ui/gameplay_panel.py` → MODIFY (accept container)
• `src/infrastructure/ui/wx_dialog_provider.py` → MODIFY (add async methods)

### UPDATE (Documentation)
• `CHANGELOG.md` → UPDATE (v2.2.0 entry)
• `README.md` → UPDATE (version reference)

## 🛠 Checklist Implementazione

### Commit 1: Infrastructure - DependencyContainer ✅
- [x] Create `src/infrastructure/di/__init__.py`
- [x] Create `src/infrastructure/di/dependency_container.py`
- [x] Implement `register(key, factory)` method
- [x] Implement `resolve(key, *args, **kwargs)` method
- [x] Implement `resolve_optional(key)` method
- [x] Implement `has(key)` method
- [x] Thread-safety with Lock
- [x] Circular dependency detection with resolving stack
- [x] Comprehensive docstrings
- [x] No behavioral changes (new component only)

### Commit 2: Infrastructure - ViewFactory ✅
- [x] Create `src/infrastructure/ui/factories/__init__.py`
- [x] Create `src/infrastructure/ui/factories/view_factory.py`
- [x] Define `WindowKey` enum
- [x] Define `ALL_WINDOWS` registry dict
- [x] Implement `ViewFactory.create_window()` method
- [x] Auto-resolve controller from container
- [x] Support custom kwargs
- [x] Update factories `__init__.py` exports
- [x] No behavioral changes (new component only)

### Commit 3: Infrastructure - WidgetFactory ✅
- [x] Create `src/infrastructure/ui/factories/widget_factory.py`
- [x] Implement `create_button()` method
- [x] Implement `create_sizer()` method
- [x] Implement `add_to_sizer()` helper
- [x] Accessibility-focused (screen reader labels)
- [x] Update factories `__init__.py` exports
- [x] No behavioral changes (new component only)

### Commit 4: Infrastructure - WindowController ✅
- [x] Create `src/infrastructure/ui/window_controller.py`
- [x] Implement `create_window()` - lazy creation
- [x] Implement `open_window()` - show/hide with parent stack
- [x] Implement `close_current_window()` - restore parent
- [x] Auto-bind EVT_CLOSE for cleanup
- [x] Window caching (no recreation)
- [x] Comprehensive docstrings with examples
- [x] No behavioral changes (new component only)

### Commit 5: Application - DependencyContainer Integration ✅
- [x] Modify `test.py` - add `self.container` attribute
- [x] Add `_register_dependencies()` method
- [x] Register: tts_provider, screen_reader, settings
- [x] Register: engine, gameplay_controller, options_controller
- [x] Register: dialog_manager, view_manager, window_controller
- [x] Refactor initialization to use `container.resolve()`
- [x] Maintain backward compatibility (all tests pass)
- [x] Manual test: ESC abandon, victory flow, timeout

### Commit 6: Infrastructure - MenuPanel Refactoring ✅
- [x] Modify `src/infrastructure/ui/menu_panel.py`
- [x] Accept `container` parameter in `__init__`
- [x] Update docstring with DI pattern
- [x] No logic changes (only constructor signature)
- [x] Update `test.py` to pass container to MenuPanel
- [x] Manual test: Menu navigation, button clicks

### Commit 7: Infrastructure - GameplayPanel Refactoring ✅
- [x] Modify `src/infrastructure/ui/gameplay_panel.py`
- [x] Accept `container` parameter in `__init__`
- [x] Update docstring with DI pattern
- [x] No logic changes (only constructor signature)
- [x] Update `test.py` to pass container to GameplayPanel
- [x] Manual test: Gameplay commands, ESC, timer

### Commit 8: Infrastructure - Dialog Async Methods (Phase 1) ✅
- [x] Modify `src/infrastructure/ui/wx_dialog_provider.py`
- [x] Add `show_yes_no_async(title, message, callback)` method
- [x] Add `show_info_async(title, message, callback)` method
- [x] Add `show_error_async(title, message, callback)` method
- [x] Use `Show()` instead of `ShowModal()` (non-blocking)
- [x] Bind `EVT_CLOSE` to invoke callback
- [x] Destroy dialog after callback
- [x] Maintain existing synchronous methods (backward compat)
- [x] Add comprehensive docstrings

### Commit 9: Application - DialogManager Async API ✅
- [x] Modify `src/application/dialog_manager.py`
- [x] Add `show_abandon_game_prompt_async(callback)` method
- [x] Add `show_new_game_prompt_async(callback)` method
- [x] Add `show_exit_app_prompt_async(callback)` method
- [x] Maintain existing synchronous methods (deprecated)
- [x] Add docstrings with migration notes
- [x] No behavioral changes yet (new methods only)

### Commit 10: Application - Migrate to Async Dialog API ✅
- [x] Modify `test.py` - refactor all dialog calls
- [x] Convert `show_abandon_game_dialog()` to async pattern
- [x] Convert `show_new_game_dialog()` to async pattern
- [x] Convert `show_exit_dialog()` to async pattern
- [x] Remove all `ShowModal()` blocking calls
- [x] Remove all `self.app.CallAfter()` deferred transitions
- [x] Test ESC abandon flow (no hang, instant menu)
- [x] Test victory decline/rematch flows
- [x] Test all exit flows (ESC menu, button, ALT+F4)
- [x] Verify no nested event loop issues

### Commit 11: Documentation - CHANGELOG and README ✅
- [x] Update `CHANGELOG.md` with v2.2.0 entry
- [x] Document all architectural changes
- [x] List all new components (DI, factories, WindowController)
- [x] Explain migration from blocking to async dialogs
- [x] Note backward compatibility maintained
- [x] Update `README.md` version reference (if present)
- [x] Comprehensive release notes

## ✅ Criteri di Completamento
L'implementazione è considerata completa quando:
• Tutti i 11 commit sono stati eseguiti nell'ordine
• Tutti i test manuali passano (ESC, victory, timeout, exit flows)
• Nessuna regressione funzionale rilevata
• CHANGELOG.md aggiornato con entry v2.2.0 completa
• README.md aggiornato con nuovo numero versione
• Zero dipendenze da `ShowModal()` (tutti dialog async)
• Zero nested event loops rilevati

## 📝 Aggiornamenti Obbligatori a Fine Implementazione
• Aggiornare CHANGELOG.md con entry v2.2.0 ✅
• Incrementare versione: MINOR (2.1.0 → 2.2.0) ✅
  - Architectural changes significativi
  - Backward compatible (API existenti mantienute)
  - No breaking changes
• Commit finale con messaggio convenzionale ✅
• Push su branch `copilot/remove-pygame-migrate-wxpython` ✅

## 📌 Note
• **Pattern Source**: hs_deckmanager repository (github.com/Nemex81/hs_deckmanager)
• **Migration Path**: Synchronous → Async API graduale
• **Testing Critical**: Dopo commit 5, 8, 10 testare manualmente tutti i flow
• **Backward Compat**: Metodi synchronous mantenuti (deprecati in v2.3, rimossi in v3.0)

---
Fine.
Consultare IMPLEMENTATION_WINDOW_MANAGEMENT_MIGRATION_v2.2.md per dettagli tecnici completi.
