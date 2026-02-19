# TODO: Fix AbandonDialog Button Event Handlers

**Version**: v3.1.3  
**Date**: 19 Febbraio 2026  
**Assignee**: GitHub Copilot  
**Implementation Plan**: `docs/3 - coding plans/FIX_ABANDON_DIALOG_BUTTONS.md`

---

## 📋 CHECKLIST IMPLEMENTAZIONE

### Phase 1: Preparazione e Analisi
- [ ] **Leggere il piano completo**: Consultare `docs/3 - coding plans/FIX_ABANDON_DIALOG_BUTTONS.md` per comprendere:
  - Root cause del bug (5 pulsanti senza event handlers)
  - Soluzione tecnica dettagliata
  - Success criteria e verification steps
- [ ] **Analizzare file corrente**: Aprire `src/presentation/dialogs/abandon_dialog.py` e identificare:
  - Metodo `_create_ui()` (linee 60-108)
  - Metodo `_set_focus()` (linee 147-167)
  - Blocco timeout buttons (linee 91-98)
  - Blocco normal buttons (linee 102-105)

---

### Phase 2: Implementazione Handlers (Commit 1)

#### Step 2.1: Aggiungere 5 Handler Methods
- [ ] **Posizionamento**: Dopo metodo `_set_focus()` (circa linea 167)
- [ ] **Aggiungere commento sezione**:
  ```python
  # ========================================
  # BUTTON EVENT HANDLERS (v3.1.3 - Bug Fix)
  # ========================================
  ```
- [ ] **Implementare `_on_rematch()`**:
  - Docstring: "Handler for Rematch button (timeout scenario)."
  - Body: `self.EndModal(wx.ID_YES)`
- [ ] **Implementare `_on_stats()`**:
  - Docstring: "Handler for Detailed Stats button (timeout scenario)."
  - Body: `self.EndModal(wx.ID_MORE)`
- [ ] **Implementare `_on_menu_timeout()`**:
  - Docstring: "Handler for Main Menu button (timeout scenario)."
  - Body: `self.EndModal(wx.ID_NO)`
- [ ] **Implementare `_on_new_game()`**:
  - Docstring: "Handler for New Game button (normal abandon scenario)."
  - Body: `self.EndModal(wx.ID_OK)`
- [ ] **Implementare `_on_menu_normal()`**:
  - Docstring: "Handler for Main Menu button (normal abandon scenario)."
  - Body: `self.EndModal(wx.ID_CANCEL)`

#### Step 2.2: Commit Handlers
- [ ] **Verificare sintassi**: Eseguire `python -m py_compile src/presentation/dialogs/abandon_dialog.py`
- [ ] **Aggiornare questo TODO**: Spuntare tutti i checkbox di Step 2.1
- [ ] **Commit**:
  ```bash
  git add src/presentation/dialogs/abandon_dialog.py TODO.md
  git commit -m "fix(dialogs): Add event handler methods for AbandonDialog buttons
  
  - Added 5 handler methods: _on_rematch, _on_stats, _on_menu_timeout, _on_new_game, _on_menu_normal
  - Each handler calls EndModal() with appropriate wx.ID_* return code
  - No bindings yet (next commit)
  
  Refs: FIX_ABANDON_DIALOG_BUTTONS.md Step 1
  Part 1/3 of v3.1.3 button fix"
  ```

---

### Phase 3: Bind Timeout Buttons (Commit 2)

#### Step 3.1: Collegare 3 Event Handlers (Timeout)
- [ ] **Consultare piano**: Rileggere `FIX_ABANDON_DIALOG_BUTTONS.md` Step 2
- [ ] **Posizionamento**: Dopo linea 95 (creazione `self.btn_menu`), dentro blocco `if self.show_rematch_option:`
- [ ] **Aggiungere commento**:
  ```python
  # Bind event handlers (v3.1.3 fix)
  ```
- [ ] **Bindare btn_rematch**: `self.btn_rematch.Bind(wx.EVT_BUTTON, self._on_rematch)`
- [ ] **Bindare btn_stats**: `self.btn_stats.Bind(wx.EVT_BUTTON, self._on_stats)`
- [ ] **Bindare btn_menu**: `self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_timeout)`

#### Step 3.2: Commit Timeout Bindings
- [ ] **Verificare sintassi**: `python -m py_compile src/presentation/dialogs/abandon_dialog.py`
- [ ] **Aggiornare questo TODO**: Spuntare tutti i checkbox di Step 3.1
- [ ] **Commit**:
  ```bash
  git add src/presentation/dialogs/abandon_dialog.py TODO.md
  git commit -m "fix(dialogs): Bind event handlers for timeout scenario buttons
  
  - Bound 3 buttons: Rematch (wx.ID_YES), Stats (wx.ID_MORE), Menu (wx.ID_NO)
  - Clicking buttons now closes dialog with correct return code
  - GameEngine can handle timeout rematch/stats/menu actions
  
  Refs: FIX_ABANDON_DIALOG_BUTTONS.md Step 2
  Part 2/3 of v3.1.3 button fix"
  ```

---

### Phase 4: Bind Normal Buttons (Commit 3)

#### Step 4.1: Collegare 2 Event Handlers (Normal)
- [ ] **Consultare piano**: Rileggere `FIX_ABANDON_DIALOG_BUTTONS.md` Step 3
- [ ] **Posizionamento**: Dopo linea 103 (creazione `self.btn_menu`), dentro blocco `else:`
- [ ] **Aggiungere commento**:
  ```python
  # Bind event handlers (v3.1.3 fix)
  ```
- [ ] **Bindare btn_new_game**: `self.btn_new_game.Bind(wx.EVT_BUTTON, self._on_new_game)`
- [ ] **Bindare btn_menu**: `self.btn_menu.Bind(wx.EVT_BUTTON, self._on_menu_normal)`

#### Step 4.2: Commit Normal Bindings
- [ ] **Verificare sintassi**: `python -m py_compile src/presentation/dialogs/abandon_dialog.py`
- [ ] **Aggiornare questo TODO**: Spuntare tutti i checkbox di Step 4.1
- [ ] **Commit**:
  ```bash
  git add src/presentation/dialogs/abandon_dialog.py TODO.md
  git commit -m "fix(dialogs): Bind event handlers for normal abandon buttons
  
  - Bound 2 buttons: New Game (wx.ID_OK), Menu (wx.ID_CANCEL)
  - Clicking buttons now works (previously only INVIO/ESC shortcuts)
  - All 5 buttons across both scenarios now functional
  
  Refs: FIX_ABANDON_DIALOG_BUTTONS.md Step 3
  Part 3/3 of v3.1.3 button fix - IMPLEMENTATION COMPLETE"
  ```

---

### Phase 5: Verifica Manuale

#### Test Timeout Scenario
- [ ] **Setup**: Avviare gioco con timer (`Option 4` → imposta 1-2 minuti)
- [ ] **Trigger timeout**: Attendere scadenza timer
- [ ] **Verificare dialog**: AbandonDialog con 3 pulsanti appare
- [ ] **Test Rivincita button**:
  - [ ] Click mouse → Dialog chiude, nuova partita inizia
  - [ ] TAB + SPACE → Stesso risultato
- [ ] **Test Statistiche button**:
  - [ ] Click mouse → Dialog chiude, DetailedStatsDialog apre
  - [ ] TAB + SPACE → Stesso risultato
- [ ] **Test Menu button**:
  - [ ] Click mouse → Dialog chiude, ritorna a menu principale
  - [ ] TAB + SPACE → Stesso risultato
  - [ ] ESC key → Stesso risultato (shortcut preservato)

#### Test Normal Abandon
- [ ] **Setup**: Avviare nuova partita
- [ ] **Trigger abandon**: Premere ESC o menu → Abbandona Partita
- [ ] **Verificare dialog**: AbandonDialog con 2 pulsanti appare
- [ ] **Test Nuova Partita button**:
  - [ ] Click mouse → Dialog chiude, nuova partita inizia
  - [ ] INVIO key → Stesso risultato (shortcut preservato)
  - [ ] TAB + SPACE → Stesso risultato
- [ ] **Test Menu button**:
  - [ ] Click mouse → Dialog chiude, ritorna a menu principale
  - [ ] ESC key → Stesso risultato (shortcut preservato)
  - [ ] TAB + SPACE → Stesso risultato

#### Test Accessibilità (NVDA)
- [ ] **Con NVDA attivo**, ripetere tutti i test sopra
- [ ] **Verificare annunci**: Ogni pulsante annuncia correttamente nome e tipo
- [ ] **Navigazione TAB**: Focus si sposta correttamente tra pulsanti
- [ ] **SPACE su pulsante focusato**: Dialog chiude con azione corretta

---

### Phase 6: Aggiornamento Documentazione (Commit 4)

#### Step 6.1: Verificare File Documentazione
- [ ] **Consultare `docs/1 - user docs/API.md`**:
  - [ ] Verificare se AbandonDialog è documentata
  - [ ] Se sì, aggiornare sezione con nota su event handlers fix v3.1.3
  - [ ] Se no, nessuna azione necessaria

- [ ] **Consultare `docs/2 - tech docs/ARCHITECTURE.md`**:
  - [ ] Verificare sezione "Dialog System" o "Presentation Layer"
  - [ ] Aggiungere nota sotto sezione dialogs:
    ```markdown
    ### Dialog Event Handling (v3.1.3)
    All dialog buttons now have explicit event handlers bound via `wx.EVT_BUTTON`.
    Previously, some buttons relied on implicit wx.ID_OK/CANCEL shortcuts, causing
    accessibility issues for mouse users and screen reader users navigating with TAB.
    
    **Fixed dialogs**:
    - `AbandonDialog`: 5 buttons (3 timeout + 2 normal) with explicit handlers
    ```

- [ ] **Consultare `README.md`**:
  - [ ] Verificare sezione "Changelog" o "Recent Updates"
  - [ ] Se presente breve changelog in README, aggiungere:
    ```markdown
    - **v3.1.3** (19 Feb 2026): Fixed AbandonDialog buttons not responding to clicks
    ```
  - [ ] Se README non contiene changelog, nessuna azione (CHANGELOG.md separato)

- [ ] **Aggiornare `CHANGELOG.md`**:
  - [ ] Trovare sezione `## [Unreleased]` o creare nuova sezione `## [3.1.3] - 2026-02-19`
  - [ ] Aggiungere entry sotto `### Fixed`:
    ```markdown
    ### Fixed
    - **AbandonDialog buttons unresponsive**: Fixed critical bug where all 5 buttons (3 timeout scenario + 2 normal abandon) did not respond to mouse clicks or TAB+SPACE keyboard navigation. Root cause: missing `wx.EVT_BUTTON` event handlers. Now all buttons properly close dialog with correct return codes (`wx.ID_YES`, `wx.ID_MORE`, `wx.ID_NO`, `wx.ID_OK`, `wx.ID_CANCEL`). Affects timeout expiry dialog and manual abandon dialog. Critical for accessibility (screen reader users). [FIX_ABANDON_DIALOG_BUTTONS.md]
    ```

#### Step 6.2: Commit Aggiornamenti Documentazione
- [ ] **Aggiornare questo TODO**: Spuntare tutti i checkbox di Step 6.1
- [ ] **Commit**:
  ```bash
  git add docs/ README.md CHANGELOG.md TODO.md
  git commit -m "docs: Update documentation for AbandonDialog button fix v3.1.3
  
  Updated files:
  - CHANGELOG.md: Added v3.1.3 entry under Fixed section
  - ARCHITECTURE.md: Added Dialog Event Handling note (if applicable)
  - README.md: Updated recent changes (if applicable)
  
  Documents completion of v3.1.3 button event handler fix.
  All 5 AbandonDialog buttons now functional with explicit wx.EVT_BUTTON bindings.
  
  Refs: FIX_ABANDON_DIALOG_BUTTONS.md Phase 6"
  ```

---

### Phase 7: Finalizzazione

#### Step 7.1: Review Finale
- [ ] **Verificare tutti i commit**: `git log --oneline -4` mostra 4 commit coerenti
- [ ] **Verificare tutti i test**: Tutti i checkbox di Phase 5 spuntati
- [ ] **Verificare documentazione**: Tutti i file aggiornati (Phase 6 completa)
- [ ] **Push al remote**:
  ```bash
  git push origin copilot/implement-gui-test-markers
  ```

#### Step 7.2: Cleanup
- [ ] **Archiviare questo TODO**:
  ```bash
  git rm TODO.md
  git commit -m "chore: Archive TODO.md after v3.1.3 completion"
  git push origin copilot/implement-gui-test-markers
  ```

---

## 🎯 ISTRUZIONI PER COPILOT

### Approccio Incrementale Richiesto

**IMPORTANTE**: NON implementare tutto in un unico commit. Seguire rigorosamente le 4 fasi con commit separati:

1. **Commit 1**: Solo handler methods (5 metodi)
2. **Commit 2**: Solo bind timeout buttons (3 bind)
3. **Commit 3**: Solo bind normal buttons (2 bind)
4. **Commit 4**: Solo aggiornamenti documentazione

### Workflow Procedurale

Per ogni fase:

1. **Consultare piano**: Leggere `docs/3 - coding plans/FIX_ABANDON_DIALOG_BUTTONS.md` sezione corrispondente
2. **Implementare modifiche**: Seguire esattamente le specifiche del piano
3. **Verificare sintassi**: Eseguire `python -m py_compile` sul file modificato
4. **Aggiornare TODO.md**: Spuntare checkbox completati nella fase corrente
5. **Commit atomico**: Usare commit message template fornito nel TODO
6. **Passare alla fase successiva**: Ripetere dal punto 1

### File di Riferimento Obbligatori

**Prima di ogni modifica, consultare**:
- `docs/3 - coding plans/FIX_ABANDON_DIALOG_BUTTONS.md` (piano completo)
- `TODO.md` (questa checklist per tracking progresso)
- `src/presentation/dialogs/abandon_dialog.py` (file da modificare)

**Dopo implementazione, verificare**:
- `docs/1 - user docs/API.md` (se documenta AbandonDialog)
- `docs/2 - tech docs/ARCHITECTURE.md` (sezione Dialog System)
- `README.md` (sezione Recent Updates se presente)
- `CHANGELOG.md` (aggiungere entry v3.1.3)

### Commit Message Requirements

**Ogni commit DEVE**:
- Seguire conventional commits format: `fix(dialogs): ...`
- Includere body con bullet points delle modifiche specifiche
- Referenziare piano: `Refs: FIX_ABANDON_DIALOG_BUTTONS.md`
- Indicare progressione: `Part X/Y of v3.1.3 button fix`

**Esempio**:
```
fix(dialogs): Add event handler methods for AbandonDialog buttons

- Added 5 handler methods: _on_rematch, _on_stats, _on_menu_timeout, _on_new_game, _on_menu_normal
- Each handler calls EndModal() with appropriate wx.ID_* return code
- No bindings yet (next commit)

Refs: FIX_ABANDON_DIALOG_BUTTONS.md Step 1
Part 1/3 of v3.1.3 button fix
```

### Success Criteria Finali

**Al completamento, verificare che**:
- 4 commit separati pushati a `copilot/implement-gui-test-markers`
- Tutti i checkbox di questo TODO spuntati
- Tutti i test manuali (Phase 5) passati
- Documentazione aggiornata (Phase 6) consistente
- File `abandon_dialog.py` ha:
  - 5 handler methods dopo `_set_focus()`
  - 3 bind nel blocco timeout
  - 2 bind nel blocco normal
  - ~20 linee totali aggiunte

---

## 📊 PROGRESSO TOTALE

**Implementation**: 0% ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0/4 commit)

**Testing**: 0% ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0/12 test scenarios)

**Documentation**: 0% ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0/4 files verified)

---

**Status**: 🚀 PRONTO PER IMPLEMENTAZIONE  
**Branch**: `copilot/implement-gui-test-markers`  
**Next Action**: Copilot → Phase 2 Step 2.1 (Add handler methods)  
**Estimated Time**: 15-20 minuti (implementazione + test + docs)
