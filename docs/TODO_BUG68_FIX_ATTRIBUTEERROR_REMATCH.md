📋 TODO – Bug #68.4 AttributeError Fix (v2.5.0)
Branch: copilot/refactor-difficulty-options-system
Tipo: FIX
Priorità: HIGH
Stato: READY

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
docs/PLAN_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante l'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

🎯 Obiettivo Implementazione
Breve descrizione:
• Aggiungere metodo show_rematch_prompt_async() in WxDialogProvider
• Risolvere AttributeError quando GameEngine.end_game() chiama il metodo
• Completare Bug #68 refactoring (ultimo tassello mancante)
• Pattern: wrapper che delega a show_yes_no_async() esistente
• Impatto: gioco non crasha più al termine partita, flusso rivincita completo

📂 File Coinvolti
• src/infrastructure/ui/wx_dialog_provider.py → MODIFY (aggiungi metodo dopo linea ~305)
• docs/TODO_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md → UPDATE (questo file)
• docs/PLAN_BUG68_FIX_ATTRIBUTEERROR_REMATCH.md → REFERENCE

🛠 Checklist Implementazione

Logica / Dominio
• ✅ Nessuna modifica necessaria (fix infrastruttura)

Application / Controller
• ✅ Nessuna modifica necessaria (GameEngine già corretto)

Infrastructure
• [ ] Aggiungere show_rematch_prompt_async() in WxDialogProvider
• [ ] Metodo delega a show_yes_no_async() con messaggio italiano
• [ ] Docstring completa con Args, Returns, Example, Version
• [ ] Consistente con altri metodi async (show_info_async, show_error_async)

Presentation / Accessibilità
• ✅ Messaggi TTS già corretti ("Rivincita?", "Vuoi giocare ancora?")
• ✅ Dialog nativo wxPython (NVDA compatible)
• ✅ Keyboard shortcuts (YES/NO/ESC)

Testing
• [ ] Test manuale: CTRL+ALT+W → nessun crash
• [ ] Test manuale: Completa partita → dialog rivincita appare
• [ ] Test manuale: YES → nuova partita inizia
• [ ] Test manuale: NO → menu visibile immediatamente (Bug #68 verificato)
• [ ] Test manuale: Multiple rematches in sequenza
• [ ] Test regressione: ESC abandon game funziona ancora

✅ Criteri di Completamento
L'implementazione è considerata completa quando:
• [ ] Metodo show_rematch_prompt_async() aggiunto in WxDialogProvider
• [ ] Sintassi validata (python -m py_compile)
• [ ] Nessun crash AttributeError al termine partita
• [ ] Dialog rivincita appare e funziona correttamente
• [ ] Bug #68 completamente risolto (menu visibile dopo decline)
• [ ] Nessuna regressione su altri dialog async

📝 Aggiornamenti Obbligatori a Fine Implementazione
• [ ] Commit con messaggio conventional:
      fix(dialogs): Add show_rematch_prompt_async() to WxDialogProvider
• [ ] Test manuale completo (5 scenari)
• [ ] Verifica sintassi: python -m py_compile src/infrastructure/ui/wx_dialog_provider.py
• [ ] Aggiorna questo TODO con checkmarks
• [ ] Marca Bug #68 come COMPLETED in issue tracker

📌 Note Operative
• Metodo è 10 righe totali (wrapper minimale)
• Nessun breaking change (solo aggiunta metodo)
• Zero rischio regressione (metodo nuovo, chiamato solo da GameEngine.end_game())
• Pattern identico a show_abandon_game_prompt_async() in DialogManager
• Questo è il QUARTO e ULTIMO fix per Bug #68 (COMMIT 1-3 già completati)

🔍 Quick Reference Code
Dove: src/infrastructure/ui/wx_dialog_provider.py, dopo linea ~305
Cosa: Aggiungi metodo show_rematch_prompt_async(callback)
Come: Delega a self.show_yes_no_async("Rivincita?", "Vuoi giocare ancora?", callback)

Fine.
