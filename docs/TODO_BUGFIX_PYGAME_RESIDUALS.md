# 📋 TODO – Fix Pygame Residuals in wxPython (v1.7.5 Bugfix)

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo**: FIX  
**Priorità**: HIGH  
**Stato**: READY  

---

## 📖 Riferimento Documentazione

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente**:

📄 **[docs/BUGFIX_PYGAME_RESIDUALS_WX.md](./BUGFIX_PYGAME_RESIDUALS_WX.md)**

Questo file TODO è solo un **sommario operativo** da consultare e aggiornare durante l'implementazione.  
Il piano completo contiene:
- Analisi root cause con stack trace completo
- Codice PRIMA/DOPO per tutti i 3 fix
- Testing plan con 5 scenari dettagliati
- Commit message pronto da usare (35 righe)
- Troubleshooting e verifica rapida

---

## 🎯 Obiettivo Implementazione

Breve descrizione in 3–5 righe:

- **Cosa**: Risolvere 2 bug critici (ENTER non seleziona + ESC crash AttributeError) causati da residui pygame
- **Perché**: Copilot ha mappato 60+ tasti correttamente ma non ha aggiornato metodi helper legacy
- **Impatto**: Ripristinare funzionalità ENTER/ESC per completare 100% migrazione wxPython
- **Scope**: 3 modifiche chirurgiche in 2 file (15 minuti stimati)

---

## 🐛 Bug Identificati

### Bug 1: ENTER Key Handler (pygame residual)
**Severità**: CRITICA  
**File**: `src/application/gameplay_controller.py` linea 323  
**Errore**: `pygame.error: video system not initialized`  
**Causa**: `_select_card()` chiama `pygame.key.get_mods()` in contesto wxPython  
**Fix**: Rimuovere check modifiers pygame (già gestiti da caller)

### Bug 2: ESC Dialog Method Name (typo)
**Severità**: CRITICA  
**File**: `test.py` linea 304  
**Errore**: `AttributeError: 'SolitarioDialogManager' object has no attribute 'show_yes_no'`  
**Causa**: Nome metodo sbagliato + parametri invertiti  
**Fix**: `show_yes_no()` → `show_yes_no_dialog(title, message)`

---

## 📂 File Coinvolti

### Fix 1 + Fix 2
- 🔧 `src/application/gameplay_controller.py` → **MODIFY**
  - Linee 318-332: Semplificare `_select_card()` (rimuovere pygame)
  - Linea ~337 (nuova): Aggiungere `_select_from_waste()` helper

### Fix 3
- 🔧 `test.py` → **MODIFY**
  - Linee 302-315: Correggere `show_abandon_game_dialog()`

### Documentazione
- 📝 `CHANGELOG.md` → **UPDATE** (entry v1.7.5 bugfix)

---

## 🛠️ Checklist Implementazione

### 🔧 Fix 1: Semplificare `_select_card()` (rimuovere pygame)

**File**: `src/application/gameplay_controller.py`  
**Linee**: 318-332

#### Modifiche
- [ ] Aprire file `src/application/gameplay_controller.py`
- [ ] Navigare a linea 318 (metodo `_select_card`)
- [ ] **RIMUOVERE** intero blocco linee 318-332 (14 righe)
- [ ] **SOSTITUIRE** con codice da piano completo (sezione "Fix 1 - Codice DOPO")
- [ ] Verificare che:
  - [ ] NON ci sia più `pygame.key.get_mods()` nel metodo
  - [ ] NON ci sia più `if mods & KMOD_CTRL:`
  - [ ] Metodo chiami solo `self.engine.select_card_at_cursor()`
  - [ ] Docstring aggiornata menzioni v1.7.5

#### Testing Post-Fix 1
- [ ] Avviare gioco: `python test.py`
- [ ] Nuova partita → Premi **1** per andare a pila 1
- [ ] Premi **ENTER**
- [ ] Verifica: Carta selezionata (TTS "Carta selezionata: ...")
- [ ] Verifica: Nessun crash `pygame.error`
- [ ] Log console: Nessun traceback

---

### 🔧 Fix 2: Aggiungere `_select_from_waste()` helper

**File**: `src/application/gameplay_controller.py`  
**Posizione**: Dopo linea 337 (subito dopo `_select_card`, prima di `_move_cards`)

#### Modifiche
- [ ] Aprire file `src/application/gameplay_controller.py`
- [ ] Navigare a linea ~337 (fine metodo `_select_card`)
- [ ] **INSERIRE** nuovo metodo da piano completo (sezione "Fix 2 - Codice da AGGIUNGERE")
- [ ] Verificare che:
  - [ ] Metodo si chiama `_select_from_waste(self)`
  - [ ] Docstring completa presente
  - [ ] Corpo chiama `self.engine.select_from_waste()`
  - [ ] Posizionato nella sezione "AZIONI CARTE"

#### Testing Post-Fix 2
- [ ] Avviare gioco: `python test.py`
- [ ] Nuova partita → Premi **D** per pescare 3 carte
- [ ] Cursore su pila qualsiasi (non scarti)
- [ ] Premi **CTRL+ENTER**
- [ ] Verifica: Carta da scarti selezionata (TTS "Selezionata carta da scarti: ...")
- [ ] Verifica: Nessun AttributeError
- [ ] Verifica: Comportamento diverso da plain ENTER

---

### 🔧 Fix 3: Correggere dialog ESC

**File**: `test.py`  
**Linee**: 302-315

#### Modifiche
- [ ] Aprire file `test.py`
- [ ] Navigare a linea 302 (metodo `show_abandon_game_dialog`)
- [ ] **RIMUOVERE** intero blocco linee 302-315 (14 righe)
- [ ] **SOSTITUIRE** con codice da piano completo (sezione "Fix 3 - Codice DOPO")
- [ ] Verificare che:
  - [ ] Nome metodo: `show_yes_no_dialog` (non `show_yes_no`)
  - [ ] Parametri: `title="Abbandono Partita"` PRIMO
  - [ ] Parametri: `message="Vuoi abbandonare..."` SECONDO
  - [ ] Docstring espansa con dettagli dialog behavior

#### Testing Post-Fix 3
- [ ] Avviare gioco: `python test.py`
- [ ] Nuova partita → Gioca qualche mossa
- [ ] Premi **ESC**
- [ ] Verifica: Dialog appare (titolo "Abbandono Partita")
- [ ] Verifica: Nessun AttributeError crash
- [ ] Premi **NO** o **ESC**
- [ ] Verifica: Ritorno a gameplay
- [ ] Premi **ESC** di nuovo → Premi **YES**
- [ ] Verifica: Ritorno a menu principale

---

## 🧪 Testing Completo

### Test Regression: Altri Tasti (campione 13 comandi)

**Procedura**: Dopo aver applicato tutti i 3 fix, testare che nessun altro comando si sia rotto.

- [ ] **1-7**: Vai pila base → Funziona ✅
- [ ] **SHIFT+1-4**: Vai fondazioni → Funziona ✅
- [ ] **SHIFT+S**: Vai scarti → Funziona ✅
- [ ] **SHIFT+M**: Vai mazzo → Funziona ✅
- [ ] **Frecce**: Navigazione cursore → Funziona ✅
- [ ] **HOME/END**: Prima/ultima carta → Funziona ✅
- [ ] **TAB**: Pila tipo diverso → Funziona ✅
- [ ] **DELETE**: Annulla selezione → Funziona ✅
- [ ] **SPACE**: Sposta carte → Funziona ✅
- [ ] **D/P**: Pesca dal mazzo → Funziona ✅
- [ ] **F/G/R**: Info queries → Funziona ✅
- [ ] **N**: Nuova partita → Funziona ✅
- [ ] **O**: Opzioni → Funziona ✅

### Test Cross-Check: Pygame Legacy

**Procedura**: Confrontare comportamento con branch pygame per validare parità.

- [ ] Checkout `refactoring-engine` → Testa ENTER/CTRL+ENTER/ESC
- [ ] Annota comportamento esatto
- [ ] Checkout `copilot/remove-pygame-migrate-wxpython` → Testa ENTER/CTRL+ENTER/ESC
- [ ] Confronta: Comportamento identico? ✅
- [ ] Unica differenza: UI nativa wxPython (accettabile)

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando:

### Modifiche Codice
- [ ] Fix 1 applicato: `_select_card()` semplificato (no pygame)
- [ ] Fix 2 applicato: `_select_from_waste()` aggiunto
- [ ] Fix 3 applicato: `show_abandon_game_dialog()` corretto
- [ ] Codice formattato correttamente (PEP8)
- [ ] Docstring aggiornate (tutti e 3 i metodi)
- [ ] Import verificati (nessun pygame inutilizzato)

### Testing
- [ ] ENTER seleziona carta (no crash pygame.error)
- [ ] CTRL+ENTER seleziona da scarti (no AttributeError)
- [ ] ESC apre dialog (no AttributeError)
- [ ] Regression check passato (13 comandi campione)
- [ ] Cross-check con pygame legacy (comportamento identico)

### Commit
- [ ] Commit message scritto (usa quello dal piano completo)
- [ ] Conventional Commits format: `fix(wx): resolve pygame residuals...`
- [ ] Branch pushed: `git push origin copilot/remove-pygame-migrate-wxpython`

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

### Documentazione
- [ ] Aggiornare `CHANGELOG.md` con entry v1.7.5:
  ```markdown
  ## [1.7.5] - 2026-02-13
  ### Fixed
  - ENTER key not selecting cards during gameplay (pygame residual)
  - CTRL+ENTER not selecting from waste (missing helper method)
  - ESC key crashing with AttributeError (wrong dialog method name)
  ```
- [ ] Marcare questo TODO come DONE
- [ ] Spostare piano completo in `docs/completed - BUGFIX_PYGAME_RESIDUALS_WX.md`

### Versioning
- [ ] **NO incremento versione** (già v1.7.5 dal keyboard mapping)
- [ ] Questo è un bugfix post-implementazione (stesso minor version)

### Merge Preparation
- [ ] Tutti i test passano
- [ ] Zero warning nel log
- [ ] Pronto per merge in `main`

---

## 📌 Note Operative Rapide

### Verifica Rapida Pre-Commit (4 comandi bash)

```bash
# 1. Verifica sintassi Python
python -m py_compile src/application/gameplay_controller.py
python -m py_compile test.py

# 2. Verifica pygame.key.get_mods RIMOSSO
grep -n "pygame.key.get_mods" src/application/gameplay_controller.py
# Output atteso: VUOTO (nessuna linea)

# 3. Verifica _select_from_waste AGGIUNTO
grep -n "def _select_from_waste" src/application/gameplay_controller.py
# Output atteso: Linea ~337 trovata

# 4. Verifica dialog corretto
grep -n "show_yes_no_dialog" test.py
# Output atteso: 3 occorrenze (linee ~281, ~304, ~322)
```

### Ordine Ottimale Implementazione

**Suggerito**: Applicare fix in questo ordine per testing incrementale.

1. **Fix 1** (semplifica `_select_card`) → Testa ENTER
2. **Fix 2** (aggiungi `_select_from_waste`) → Testa CTRL+ENTER
3. **Fix 3** (correggi dialog ESC) → Testa ESC
4. **Regression check** → Testa 13 comandi campione
5. **Commit unico** con tutti i 3 fix

**Rationale**: Fix correlati (risoluzione residui pygame), commit atomico facilita eventuale revert.

### Troubleshooting Rapido

**Se ENTER continua a non funzionare**:
- Verifica che `_select_card()` NON contenga più `pygame.key.get_mods()`
- Aggiungi `print("ENTER pressed")` in `_select_card()` per debug
- Verifica che `handle_wx_key_event()` linea ~764 chiami `self._select_card()`

**Se CTRL+ENTER genera AttributeError**:
- Verifica che `_select_from_waste()` esista (grep per "def _select_from_waste")
- Verifica posizione: dopo `_select_card`, prima di `_move_cards`
- Verifica che `handle_wx_key_event()` linea ~739 chiami `self._select_from_waste()`

**Se ESC continua a crashare**:
- Verifica nome metodo: `show_yes_no_dialog` (non `show_yes_no`)
- Verifica ordine parametri: `title` PRIMA, `message` DOPO
- Verifica che tutti i 3 dialog nel file usino stesso pattern

---

## 🚦 Stato Avanzamento

**Aggiornare questa sezione durante l'implementazione**:

- [ ] **Fix 1**: Semplifica `_select_card()` - `NOT STARTED`
- [ ] **Fix 2**: Aggiungi `_select_from_waste()` - `NOT STARTED`
- [ ] **Fix 3**: Correggi dialog ESC - `NOT STARTED`
- [ ] **Testing ENTER**: Plain + CTRL - `NOT STARTED`
- [ ] **Testing ESC**: Dialog YES/NO/ESC - `NOT STARTED`
- [ ] **Regression Check**: 13 comandi - `NOT STARTED`
- [ ] **Cross-Check**: Pygame legacy - `NOT STARTED`
- [ ] **Commit**: Con message piano completo - `NOT STARTED`
- [ ] **Documentazione**: CHANGELOG aggiornato - `NOT STARTED`

---

## 🎉 Risultato Finale Atteso

Una volta completati i 3 fix:

✅ **ENTER funzionante**: Seleziona carta sul focus (no crash pygame)  
✅ **CTRL+ENTER funzionante**: Seleziona da scarti (nuovo helper method)  
✅ **ESC funzionante**: Apre dialog abbandono (no AttributeError)  
✅ **Zero dipendenze pygame**: Codice wxPython 100% pulito  
✅ **60+ comandi operativi**: Nessuna regressione  
✅ **Ready for merge**: Migrazione wxPython completata al 100%  

---

**Fine TODO Operativo**

Per analisi root cause completa, codice PRIMA/DOPO dettagliato, e commit message pronto, consultare:  
📄 **[docs/BUGFIX_PYGAME_RESIDUALS_WX.md](./BUGFIX_PYGAME_RESIDUALS_WX.md)**

---

**Document Version**: v1.0  
**Last Updated**: 2026-02-13  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Status**: READY  
**Estimated Time**: 15 minuti
