📋 TODO – Bug #68.4 Regressione Async Dialogs (v2.5.0)
Branch: copilot/refactor-difficulty-options-system
Tipo: FIX (Regressione da COMMIT 3 Copilot)
Priorità: 🔴 CRITICA (app crasha al termine partita)
Stato: READY

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
docs/PLAN_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante l'implementazione.
Il piano completo contiene analisi root cause, flussi, edge case e dettagli tecnici.

🎯 Obiettivo Implementazione
Breve descrizione:
• **REGRESSIONE**: Copilot COMMIT 3 ha introdotto check `IsMainLoopRunning()` troppo aggressivo
• **PROBLEMA**: `show_statistics_report()` (sincrono) crea nested event loop che confonde check
• **SOLUZIONE**: Refactor `show_statistics_report()` a pattern async (OPZIONE C)
• **IMPATTO**: Risolve crash, completa Bug #68, architettura 100% async consistente
• **SCOPE**: 2 file modificati + 1 check rimosso = 3 commit atomici

📂 File Coinvolti
• src/infrastructure/ui/wx_dialog_provider.py → MODIFY (2 modifiche):
  1. Refactor show_statistics_report() → show_statistics_report_async()
  2. Rimuovere check IsMainLoopRunning() da show_yes_no_async()
• src/application/game_engine.py → MODIFY:
  - Update end_game() per usare callback chain async
• docs/TODO_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md → UPDATE (questo file)
• docs/PLAN_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md → REFERENCE

🛠 Checklist Implementazione

🔴 COMMIT 1: Refactor show_statistics_report_async (wx_dialog_provider.py)
• [ ] Aggiungere parametro `callback: Callable[[], None]` alla firma
• [ ] Creare wrapper interno `show_modal_and_callback()`
• [ ] Spostare logica esistente dentro wrapper
• [ ] Rimuovere `app = wx.App()` (usa parent esistente)
• [ ] Invocare `callback()` DOPO `dlg.Destroy()`
• [ ] Chiamare con `wx.CallAfter(show_modal_and_callback)`
• [ ] Docstring completa (Args, Flow, Example, Version v2.5.0)
• [ ] Mantenere metodo originale `show_statistics_report()` come DEPRECATED wrapper

🟡 COMMIT 2: Update end_game() callback chain (game_engine.py)
• [ ] Creare funzione `on_stats_closed()` (callback primo dialog)
• [ ] Dentro `on_stats_closed()`, chiamare `show_rematch_prompt_async()`
• [ ] Cambiare `show_statistics_report()` → `show_statistics_report_async(callback=on_stats_closed)`
• [ ] Aggiungere log: "Statistics closed, showing rematch prompt..."
• [ ] Verificare nessuna modifica a `on_rematch_result()` (già corretto)

🟢 COMMIT 3: Rimuovi IsMainLoopRunning check (wx_dialog_provider.py)
• [ ] In `show_yes_no_async()`, linea ~267
• [ ] Rimuovere blocco `if app and app.IsMainLoopRunning():`
• [ ] Rimuovere blocco `else: callback(False)`
• [ ] Mantenere solo `wx.CallAfter(show_modal_and_callback)`
• [ ] Rationale: Con tutti dialog async, wx.App è sempre valido

Presentation / Accessibilità
• ✅ Nessuna modifica UI (messaggi invariati)
• ✅ Pattern async mantiene accessibilità NVDA
• ✅ Keyboard shortcuts (OK/ESC) funzionano identicamente

Testing
• [ ] Test 1: CTRL+ALT+W → stats dialog appare
• [ ] Test 2: INVIO su OK → stats chiude, rematch dialog appare (NO CRASH!)
• [ ] Test 3: YES su rematch → nuova partita inizia
• [ ] Test 4: NO su rematch → menu visibile immediatamente (Bug #68)
• [ ] Test 5: Multiple rematches → tutti funzionano
• [ ] Test 6: ESC durante stats → chiude, mostra rematch
• [ ] Test 7: Log completo (ogni step loggato, no "buchi")

✅ Criteri di Completamento
L'implementazione è considerata completa quando:
• [ ] COMMIT 1: show_statistics_report_async() implementato
• [ ] COMMIT 2: end_game() usa callback chain
• [ ] COMMIT 3: IsMainLoopRunning check rimosso
• [ ] Sintassi validata (python -m py_compile su entrambi i file)
• [ ] Nessun crash AttributeError al termine partita
• [ ] Flusso completo: stats → rematch → scelta → azione
• [ ] Log completi senza "buchi" (ogni dialog loggato)
• [ ] Bug #68 completamente risolto (menu visibile dopo decline)
• [ ] Zero regressioni su altri flussi (ESC, nuova partita, exit)

📝 Aggiornamenti Obbligatori a Fine Implementazione
• [ ] COMMIT 1 message:
      refactor(dialogs): Convert show_statistics_report to async pattern
• [ ] COMMIT 2 message:
      refactor(game): Update end_game() to use async callback chain
• [ ] COMMIT 3 message:
      fix(dialogs): Remove IsMainLoopRunning check (no longer needed)
• [ ] Test manuale completo (7 scenari)
• [ ] Verifica log completi (controlla file solitaire.log)
• [ ] Aggiorna questo TODO con checkmarks
• [ ] Marca Bug #68 come COMPLETED definitivamente

📌 Note Operative

🔥 ROOT CAUSE (dalla regressione):
```
Log output:
⚠️ wx.App not active, skipping async dialog
→ Game ended callback - Rematch: False
→ Returning to main menu...
```

**Problema**: `show_statistics_report()` (sincrono) crea nested event loop:
1. Crea `wx.App()` instance
2. `ShowModal()` blocca event loop principale
3. Quando termina, `wx.GetApp()` ritorna app distrutta
4. `show_yes_no_async()` check fallisce → salta dialog → crash!

**Soluzione**: Rendere `show_statistics_report()` async come tutti gli altri dialog.

🎯 CALLBACK CHAIN (dopo fix):
```
end_game()
  ↓
  show_statistics_report_async(callback=on_stats_closed)
    ↓ [User preme OK]
    ↓ on_stats_closed() chiamato
    ↓
    show_rematch_prompt_async(callback=on_rematch_result)
      ↓ [User sceglie YES/NO]
      ↓ on_rematch_result(wants_rematch) chiamato
      ↓
      self.callback(wants_rematch) → acs_wx.handle_game_ended()
```

✅ VANTAGGI OPZIONE C:
- Architettura 100% async (nessun dialog sincrono)
- Zero nested event loops (nessun wx.App multiplo)
- Log completi (ogni callback tracciabile)
- Bug #68 completamente risolto
- Manutenibilità futura (pattern unico)

🔍 Quick Reference Code Positions

**File 1**: src/infrastructure/ui/wx_dialog_provider.py
- Linea ~442: show_statistics_report() → refactor async
- Linea ~267: show_yes_no_async() → rimuovi check IsMainLoopRunning

**File 2**: src/application/game_engine.py
- Linea ~1137: end_game() → aggiungi on_stats_closed callback

Fine.
