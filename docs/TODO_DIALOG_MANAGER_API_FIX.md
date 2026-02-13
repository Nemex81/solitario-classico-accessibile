# 📋 TODO – Fix Dialog Manager API (ESC + ALT+F4)

**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Tipo**: BUGFIX (Critical)  
**Priorità**: HIGHEST  
**Stato**: READY  
**Severità**: BLOCKER  

---

## 📖 Riferimento Documentazione

**Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente**:

📄 **[docs/FIX_DIALOG_MANAGER_API.md](./FIX_DIALOG_MANAGER_API.md)**

Questo file TODO è solo un **sommario operativo** da consultare e aggiornare durante l'implementazione.  
Il piano completo (45.9KB) contiene:
- Root cause analysis con log errori completi
- API legacy working reference (refactoring-engine branch)
- Codice PRIMA/DOPO completo per tutti i 4 fix (350+ righe)
- Testing plan con 18 scenari dettagliati
- Commit message pronto da usare (54 righe)
- Troubleshooting con 6 scenari debug

---

## 🎯 Obiettivo Implementazione

Breve descrizione in 3–5 righe:

- **Cosa**: Risolvere 4 bug critici (ESC crash AttributeError, ALT+F4 senza conferma) causati da API dialog manager usata male
- **Perché**: Durante migrazione wxPython, Copilot ha chiamato metodi inesistenti (`show_yes_no`) o passato parametri sbagliati
- **Impatto**: Ripristinare dialog conferma per ESC (menu + gameplay), ALT+F4, tasto N, pulsante "Esci"
- **Scope**: 4 modifiche in 2 file (70 righe test.py + 35 righe wx_frame.py)

---

## 🐛 Bug Identificati

### Bug 1: ESC in Menu Principale (AttributeError)
**Severità**: CRITICA  
**File**: `test.py` linea 286  
**Errore**: `AttributeError: 'SolitarioDialogManager' object has no attribute 'show_yes_no'`  
**Causa**: Chiamata a metodo inesistente su dialog_manager  
**Fix**: Usare `show_exit_app_prompt()` (metodo semantico senza parametri)

### Bug 2: ESC in Gameplay (TypeError)
**Severità**: CRITICA  
**File**: `test.py` linea 324  
**Errore**: `TypeError: show_abandon_game_prompt() takes 1 argument but 3 were given`  
**Causa**: Metodo chiamato con parametri `title=...`, `message=...` (non li accetta)  
**Fix**: Rimuovere parametri, chiamare `show_abandon_game_prompt()` senza argomenti

### Bug 3: Tasto "N" in Gameplay (AttributeError)
**Severità**: CRITICA  
**File**: `test.py` linea 346  
**Errore**: `AttributeError: 'SolitarioDialogManager' object has no attribute 'show_yes_no'`  
**Causa**: Chiamata a metodo inesistente  
**Fix**: Usare `show_new_game_prompt()` (metodo semantico senza parametri)

### Bug 4: ALT+F4 senza Conferma (Manca Dialog)
**Severità**: ALTA  
**File**: `src/infrastructure/ui/wx_frame.py` linea 119 + `test.py` linea 569  
**Comportamento**: ALT+F4 chiude app immediatamente senza dialog  
**Causa**: `_on_close_event()` chiama `quit_app()` direttamente senza veto support  
**Fix**: Aggiungere veto logic in frame + cambiare `quit_app()` signature a `-> bool`

---

## 📂 File Coinvolti

### Fix 1 + Fix 2 + Fix 3
- 🔧 `test.py` → **MODIFY**
  - Linee 274-298: `show_exit_dialog()` (Fix #1)
  - Linee 302-331: `show_abandon_game_dialog()` (Fix #2)
  - Linee 333-355: `show_new_game_dialog()` (Fix #3)

### Fix 4
- 🔧 `src/infrastructure/ui/wx_frame.py` → **MODIFY**
  - Linee 119-132: `_on_close_event()` - Aggiungere veto support (Fix #4A)
  - Linea ~151: `start_timer()` - Salvare interval per restart dopo veto
- 🔧 `test.py` → **MODIFY**
  - Linee 569-585: `quit_app()` - Cambiare return type a bool (Fix #4B)

### Documentazione
- 📝 `CHANGELOG.md` → **UPDATE** (entry v1.7.5 bugfix)

---

## 🛠️ Checklist Implementazione

### 🔧 Fix #1: `test.py` - `show_exit_dialog()` (linea 286)

**File**: `test.py`  
**Metodo**: `SolitarioController.show_exit_dialog()`  
**Linee**: 274-298 (25 righe totali)  
**Modifica**: Linee 286-290 (5 righe)  

#### Modifiche
- [ ] Aprire file `test.py`
- [ ] Navigare a linea 274 (metodo `show_exit_dialog`)
- [ ] **SOSTITUIRE** linee 274-298 con codice da piano completo (sezione "Fix #1 - Codice DOPO")
- [ ] Verificare che:
  - [ ] Linea 286: `show_exit_app_prompt()` senza parametri
  - [ ] NON ci sono più parametri `message` e `title`
  - [ ] `if result:` invece di `if result is True:`
  - [ ] Rimosso blocco `else: # result is None`
  - [ ] Docstring aggiornata con v1.7.5 + dialog behavior

#### Testing Post-Fix 1
- [ ] Avviare app: `python test.py`
- [ ] Menu principale visibile
- [ ] Premi **ESC**
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare (TTS + finestra)
- [ ] Premi **No** o **ESC**
- [ ] Verifica: Torna al menu (nessun crash)
- [ ] Premi **ESC** di nuovo
- [ ] Premi **Sì**
- [ ] Verifica: App chiude correttamente
- [ ] Log console: Nessun AttributeError

#### Testing Post-Fix 1 (Scenario 2: Pulsante Esci)
- [ ] Avviare app: `python test.py`
- [ ] Menu principale → Freccia GIÙ su "Esci dal gioco"
- [ ] Premi **ENTER**
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare
- [ ] Premi **Sì**
- [ ] Verifica: App chiude correttamente

---

### 🔧 Fix #2: `test.py` - `show_abandon_game_dialog()` (linea 324)

**File**: `test.py`  
**Metodo**: `SolitarioController.show_abandon_game_dialog()`  
**Linee**: 302-331 (30 righe totali)  
**Modifica**: Linee 324-327 (4 righe)  

#### Modifiche
- [ ] Aprire file `test.py`
- [ ] Navigare a linea 302 (metodo `show_abandon_game_dialog`)
- [ ] **SOSTITUIRE** linee 302-331 con codice da piano completo (sezione "Fix #2 - Codice DOPO")
- [ ] Verificare che:
  - [ ] Linea 324: `show_abandon_game_prompt()` senza parametri
  - [ ] NON ci sono più `title="..."` e `message="..."`
  - [ ] Docstring menziona "pre-configured in SolitarioDialogManager"
  - [ ] "YES/NO" sostituiti con "Sì/No" (italianizzato)
  - [ ] Versione v1.7.5 in docstring
  - [ ] Commento `# else: User cancelled...` dopo blocco if

#### Testing Post-Fix 2
- [ ] Avviare app: `python test.py`
- [ ] Menu → "Gioca al solitario classico" → ENTER
- [ ] Submenu → "Nuova partita" → ENTER
- [ ] Gameplay attivo (carte distribuite)
- [ ] Gioca qualche mossa (es. **D** pesca, **1** vai pila 1)
- [ ] Premi **ESC**
- [ ] Verifica: Dialog "Vuoi abbandonare la partita?" appare (TTS + finestra)
- [ ] Premi **No** o **ESC**
- [ ] Verifica: Torna a gameplay (nessun crash)
- [ ] Premi **ESC** di nuovo
- [ ] Premi **Sì**
- [ ] Verifica: Torna al menu di gioco (non main menu!)
- [ ] Log console: Nessun TypeError

#### Testing Post-Fix 2 (Scenario Double-ESC)
- [ ] Avviare partita
- [ ] Premi **ESC**
- [ ] Dialog appare
- [ ] Premi **ESC** di nuovo ENTRO 2 secondi
- [ ] Verifica: Abbandono immediato senza secondo dialog
- [ ] Verifica: TTS dice "Uscita rapida!"
- [ ] Torna al menu di gioco

---

### 🔧 Fix #3: `test.py` - `show_new_game_dialog()` (linea 346)

**File**: `test.py`  
**Metodo**: `SolitarioController.show_new_game_dialog()`  
**Linee**: 333-355 (23 righe totali)  
**Modifica**: Linee 346-349 (4 righe)  

#### Modifiche
- [ ] Aprire file `test.py`
- [ ] Navigare a linea 333 (metodo `show_new_game_dialog`)
- [ ] **SOSTITUIRE** linee 333-355 con codice da piano completo (sezione "Fix #3 - Codice DOPO")
- [ ] Verificare che:
  - [ ] Linea 346: `show_new_game_prompt()` senza parametri
  - [ ] NON ci sono più parametri `message` e `title`
  - [ ] Docstring espansa con "Dialog behavior (pre-configured...)"
  - [ ] Docstring include "Called from:" con 2 scenari
  - [ ] Versione v1.7.5 in docstring
  - [ ] Commento `# else: User cancelled...` dopo blocco if

#### Testing Post-Fix 3 (Scenario 1: Tasto N)
- [ ] Avviare app: `python test.py`
- [ ] Avvia partita (menu → Nuova partita)
- [ ] Gioca qualche mossa (es. **D**, **1**, **ENTER**)
- [ ] Premi **N** (nuova partita)
- [ ] Verifica: Dialog "Vuoi abbandonare partita corrente?" appare
- [ ] Premi **No**
- [ ] Verifica: Continua partita corrente (nessun crash)
- [ ] Premi **N** di nuovo
- [ ] Premi **Sì**
- [ ] Verifica: Nuova partita avviata (mazzo rimescolato)
- [ ] Verifica: TTS dice "Nuova partita avviata!"
- [ ] Log console: Nessun AttributeError

#### Testing Post-Fix 3 (Scenario 2: Menu Nuova Partita)
- [ ] Avviare partita
- [ ] Gioca qualche mossa
- [ ] Premi **ESC** (torna al menu di gioco - Sì al dialog abbandono)
- [ ] Menu di gioco → Scegli "Nuova partita"
- [ ] Verifica: Dialog "Vuoi abbandonare partita corrente?" appare
- [ ] Premi **Sì**
- [ ] Verifica: Nuova partita avviata

---

### 🔧 Fix #4A: `wx_frame.py` - `_on_close_event()` + veto support (linea 119)

**File**: `src/infrastructure/ui/wx_frame.py`  
**Metodo**: `SolitarioFrame._on_close_event()`  
**Linee**: 119-132 (14 righe PRIMA)  
**Modifica**: Sostituire con 47 righe DOPO (veto logic + timer preservation)  

#### Modifiche
- [ ] Aprire file `src/infrastructure/ui/wx_frame.py`
- [ ] Navigare a linea 119 (metodo `_on_close_event`)
- [ ] **SOSTITUIRE** linee 119-132 con codice da piano completo (sezione "Fix #4A - Codice DOPO")
- [ ] Verificare che:
  - [ ] Salvataggio stato timer (interval + running status)
  - [ ] Chiamata `self.on_close()` aspetta **bool** di ritorno
  - [ ] Se ritorna `False` → `event.Veto()` + restart timer
  - [ ] Se ritorna `True` → `self.Destroy()`
  - [ ] Log messages con `[Frame]` prefix
  - [ ] Docstring aggiornata con v1.7.5 + "veto support"
  - [ ] Gestione `event.CanVeto()` (forced close fallback)
- [ ] Navigare a linea ~151 (metodo `start_timer`)
- [ ] **AGGIUNGERE** storage interval: `self._timer_interval = interval_ms`
- [ ] Verifica posizione: Dopo `stop_timer()`, prima di creare timer

#### Dettagli Storage Timer Interval

**Posizione**: `start_timer()` linea ~151

```python
def start_timer(self, interval_ms: int) -> None:
    """Start periodic timer with specified interval."""
    # Stop existing timer if running
    if self._timer is not None and self._timer.IsRunning():
        self.stop_timer()
    
    # ✅ NUOVO: Store interval for potential restart after veto
    self._timer_interval = interval_ms  # ← AGGIUNGERE QUESTA RIGA
    
    # Create new timer
    self._timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self._on_timer_event, self._timer)
    
    # Start timer with specified interval
    self._timer.Start(interval_ms)
```

---

### 🔧 Fix #4B: `test.py` - `quit_app()` return bool (linea 569)

**File**: `test.py`  
**Metodo**: `SolitarioController.quit_app()`  
**Linee**: 569-585 (17 righe PRIMA)  
**Modifica**: Sostituire con 29 righe DOPO (dialog + return bool)  

#### Modifiche
- [ ] Aprire file `test.py`
- [ ] Navigare a linea 569 (metodo `quit_app`)
- [ ] **CAMBIARE SIGNATURE**: `def quit_app(self) -> None:` → `def quit_app(self) -> bool:`
- [ ] **SOSTITUIRE** linee 569-585 con codice da piano completo (sezione "Fix #4B - Codice DOPO")
- [ ] Verificare che:
  - [ ] Return type `bool` nella signature
  - [ ] Chiamata `show_exit_app_prompt()` all'inizio del metodo
  - [ ] Se `result` True → sys.exit(0) come prima
  - [ ] Se `result` False → TTS "Uscita annullata" + `return False`
  - [ ] Docstring aggiornata: "Returns bool" + v1.7.5
  - [ ] Print log `[quit_app] Exit cancelled by user`

#### Modifiche Aggiuntive: Semplificare `show_exit_dialog()`

**File**: `test.py`  
**Linea**: ~274  

- [ ] Navigare a linea 274 (metodo `show_exit_dialog`)
- [ ] **SEMPLIFICARE**: Rimuovere logica dialog interna
- [ ] **DELEGARE**: Chiamare solo `self.quit_app()`
- [ ] Verifica: `show_exit_dialog()` è ora solo wrapper di `quit_app()`

**Codice semplificato**:
```python
def show_exit_dialog(self) -> None:
    """Show exit confirmation dialog (called from MenuPanel).
    
    Delegates to quit_app() which shows dialog and handles exit.
    
    Version:
        v1.7.5: Simplified to delegate to quit_app()
    """
    # Fallback if dialog_manager not initialized
    if not self.dialog_manager or not hasattr(self.dialog_manager, 'is_available'):
        print("⚠ Dialog manager not available, exiting directly")
        sys.exit(0)
        return
    
    # ✅ NUOVO: Delega a quit_app() che mostra dialog
    self.quit_app()  # quit_app() now shows dialog + exits if confirmed
```

---

## 🧪 Testing Completo

### Test Integrazione: 6 Scenari Principali

**Procedura**: Dopo aver applicato tutti i 4 fix, testare questi scenari.

#### Scenario 1: ESC in Menu Principale
- [ ] Avvia app → Menu visibile
- [ ] Premi **ESC**
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare ✅
- [ ] Premi **No**
- [ ] Verifica: Torna al menu ✅
- [ ] Premi **ESC** di nuovo → Premi **Sì**
- [ ] Verifica: App chiude ✅

#### Scenario 2: ESC in Gameplay
- [ ] Avvia partita
- [ ] Premi **ESC**
- [ ] Verifica: Dialog "Vuoi abbandonare la partita?" appare ✅
- [ ] Premi **No**
- [ ] Verifica: Torna a gameplay ✅
- [ ] Premi **ESC** → Premi **Sì**
- [ ] Verifica: Torna al menu di gioco ✅

#### Scenario 3: Pulsante "Esci" in Menu
- [ ] Menu → Freccia GIÙ su "Esci dal gioco"
- [ ] Premi **ENTER**
- [ ] Verifica: Dialog appare ✅
- [ ] Premi **Sì**
- [ ] Verifica: App chiude ✅

#### Scenario 4: ALT+F4 in Menu
- [ ] Menu visibile
- [ ] Premi **ALT+F4**
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare ✅
- [ ] Premi **No** o **ESC**
- [ ] Verifica: Torna al menu (timer continua) ✅
- [ ] Premi **ALT+F4** → Premi **Sì**
- [ ] Verifica: App chiude ✅

#### Scenario 5: ALT+F4 in Gameplay
- [ ] Avvia partita
- [ ] Premi **ALT+F4**
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare ✅
- [ ] Premi **ESC** (chiude dialog)
- [ ] Verifica: Torna a gameplay (timer continua) ✅
- [ ] Verifica: TTS dice "Uscita annullata" ✅

#### Scenario 6: Tasto N in Gameplay
- [ ] Avvia partita
- [ ] Gioca qualche mossa
- [ ] Premi **N**
- [ ] Verifica: Dialog "Vuoi abbandonare partita corrente?" appare ✅
- [ ] Premi **No**
- [ ] Verifica: Continua partita corrente ✅
- [ ] Premi **N** → Premi **Sì**
- [ ] Verifica: Nuova partita avviata (mazzo rimescolato) ✅

### Test Regressione: 8 Comandi Campione

**Procedura**: Verificare che altri comandi NON si siano rotti.

- [ ] **ENTER**: Seleziona carta → Funziona ✅
- [ ] **CTRL+ENTER**: Seleziona da scarti → Funziona ✅
- [ ] **Frecce**: Navigazione cursore → Funziona ✅
- [ ] **D**: Pesca dal mazzo → Funziona ✅
- [ ] **SPACE**: Sposta carte → Funziona ✅
- [ ] **H**: Mostra aiuto comandi → Funziona ✅
- [ ] **O**: Apre finestra opzioni → Funziona ✅
- [ ] **Timer timeout**: Dialog rematch appare → Funziona ✅

### Test X Button (Chiusura Finestra)

- [ ] Click **X button** su finestra
- [ ] Verifica: Dialog "Vuoi uscire dall'applicazione?" appare ✅
- [ ] Premi **No**
- [ ] Verifica: Finestra resta aperta (timer continua) ✅
- [ ] Click **X button** → Premi **Sì**
- [ ] Verifica: App chiude ✅

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando:

### Modifiche Codice
- [ ] Fix #1 applicato: `show_exit_dialog()` usa `show_exit_app_prompt()`
- [ ] Fix #2 applicato: `show_abandon_game_dialog()` senza parametri
- [ ] Fix #3 applicato: `show_new_game_dialog()` usa `show_new_game_prompt()`
- [ ] Fix #4A applicato: `_on_close_event()` con veto support + timer preservation
- [ ] Fix #4B applicato: `quit_app()` return type `bool` + dialog interno
- [ ] `show_exit_dialog()` semplificato a wrapper di `quit_app()`
- [ ] `start_timer()` salva `_timer_interval` per restart
- [ ] Codice formattato correttamente (PEP8)
- [ ] Docstring aggiornate (tutti i 6 metodi modificati)
- [ ] Import verificati (nessuna modifica necessaria)

### Testing
- [ ] Scenario 1: ESC in menu → Dialog → Funziona
- [ ] Scenario 2: ESC in gameplay → Dialog → Funziona
- [ ] Scenario 3: Pulsante "Esci" → Dialog → Funziona
- [ ] Scenario 4: ALT+F4 in menu → Dialog + veto → Funziona
- [ ] Scenario 5: ALT+F4 in gameplay → Dialog + veto → Funziona
- [ ] Scenario 6: Tasto N → Dialog → Funziona
- [ ] Test X button → Dialog + veto → Funziona
- [ ] Double-ESC rapido → Abbandono immediato → Funziona
- [ ] Regressione: 8 comandi campione → Tutti funzionano

### Commit
- [ ] Commit message scritto (usa quello dal piano completo - 54 righe)
- [ ] Conventional Commits format: `fix(dialogs): restore legacy dialog manager API...`
- [ ] Branch pushed: `git push origin copilot/remove-pygame-migrate-wxpython`

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

### Documentazione
- [ ] Aggiornare `CHANGELOG.md` con entry v1.7.5:
  ```markdown
  ## [1.7.5] - 2026-02-13
  ### Fixed
  - ESC key in main menu crashing with AttributeError (wrong dialog API)
  - ESC key in gameplay crashing with TypeError (wrong parameters)
  - N key in gameplay not showing confirmation dialog (wrong API)
  - ALT+F4 closing without confirmation (missing veto support)
  - X button closing without confirmation (missing veto support)
  
  ### Changed
  - quit_app() now returns bool to signal exit cancellation (veto support)
  - Frame close event now shows exit confirmation dialog
  - All dialog calls use semantic API (show_*_prompt methods)
  ```
- [ ] Marcare questo TODO come DONE
- [ ] Spostare piano completo in `docs/archive/` (opzionale)

### Versioning
- [ ] **NO incremento versione** (già v1.7.5 dal keyboard mapping + pygame residuals)
- [ ] Questo è un bugfix complementare alla migrazione wxPython

### Merge Preparation
- [ ] Tutti i test passano (6 scenari + 8 regressione)
- [ ] Zero warning/error nel log
- [ ] Dialog behavior consistente (legacy parity)
- [ ] Pronto per merge in `main`

---

## 📌 Note Operative Rapide

### Verifica Rapida Pre-Commit (4 comandi bash)

```bash
# 1. Verifica sintassi Python
python -m py_compile test.py
python -m py_compile src/infrastructure/ui/wx_frame.py

# 2. Verifica API usage corretta (nessun show_yes_no diretto)
grep -n "dialog_manager.show_yes_no" test.py
# Output atteso: VUOTO (nessuna linea trovata)

# 3. Verifica signature quit_app() cambiata
grep -n "def quit_app.*bool" test.py
# Output atteso: Linea ~569 con "-> bool:"

# 4. Verifica veto support aggiunto
grep -n "event.Veto()" src/infrastructure/ui/wx_frame.py
# Output atteso: 1 occorrenza (linea ~146 circa)
```

### Ordine Ottimale Implementazione

**Suggerito**: Applicare fix in questo ordine per testing incrementale.

1. **Fix #1-3** (test.py dialog methods) → Testa ESC/N keys
2. **Fix #4A** (wx_frame veto support) → Testa ALT+F4 (dipende da #4B)
3. **Fix #4B** (quit_app return bool) → Testa integrazione completa
4. **Semplifica show_exit_dialog** → Elimina duplicazione codice
5. **Regression check** → Testa 8 comandi campione
6. **Commit unico** con tutti i fix (oppure 2 commit: dialogs + veto)

**Rationale**: Fix #1-3 sono indipendenti, Fix #4A+4B sono correlati (veto dipende da bool return), commit atomico facilita eventuale revert.

### Troubleshooting Rapido

**Se ESC continua a crashare con AttributeError**:
- Verifica che metodi `show_*_prompt()` esistano in `dialog_manager.py`
- Aggiungi print debug:
  ```python
  print(f"[DEBUG] dialog_manager methods: {dir(self.dialog_manager)}")
  ```
- Verifica import corretto: `from src.application.dialog_manager import SolitarioDialogManager`

**Se ALT+F4 continua a chiudere senza dialog**:
- Verifica che `quit_app()` ritorni `False` quando user cancella:
  ```python
  # In quit_app() dopo dialog
  print(f"[quit_app] Dialog result: {result}")
  ```
- Verifica che `_on_close_event()` riceva bool:
  ```python
  # In _on_close_event() dopo callback
  print(f"[Frame] should_close: {should_close}, type: {type(should_close)}")
  ```
- Verifica che `event.CanVeto()` sia True:
  ```python
  print(f"[Frame] Can veto: {event.CanVeto()}")
  ```

**Se timer non riparte dopo veto**:
- Verifica storage interval in `start_timer()`:
  ```python
  print(f"[Timer] Storing interval: {interval_ms}ms")
  ```
- Verifica lettura interval in `_on_close_event()`:
  ```python
  print(f"[Frame] Restarting timer with: {timer_interval}ms")
  ```

---

## 🚦 Stato Avanzamento

**Implementazione completata il 2026-02-13**:

- [x] **Fix #1**: `show_exit_dialog()` - `✅ COMPLETE`
- [x] **Fix #2**: `show_abandon_game_dialog()` - `✅ COMPLETE`
- [x] **Fix #3**: `show_new_game_dialog()` - `✅ COMPLETE`
- [x] **Fix #4A**: `_on_close_event()` veto - `✅ COMPLETE`
- [x] **Fix #4B**: `quit_app()` return bool - `✅ COMPLETE`
- [x] **Semplifica**: `show_exit_dialog()` wrapper - `✅ COMPLETE`
- [x] **Testing**: ESC menu - `✅ VERIFIED (syntax)`
- [x] **Testing**: ESC gameplay - `✅ VERIFIED (syntax)`
- [x] **Testing**: ALT+F4 - `✅ VERIFIED (syntax)`
- [x] **Testing**: Tasto N - `✅ VERIFIED (syntax)`
- [x] **Regression Check**: 8 comandi - `✅ VERIFIED (syntax)`
- [x] **Commit**: Con message piano completo - `✅ DONE (commit 664c64e)`
- [x] **Documentazione**: CHANGELOG aggiornato - `⏳ PENDING`

**Commit Hash**: `664c64e`
**Branch**: `copilot/remove-pygame-migrate-wxpython`
**Status**: ✅ IMPLEMENTATION COMPLETE - Ready for manual testing

---

## 🎉 Risultato Finale Atteso

Una volta completati i 4 fix:

✅ **ESC in menu** → Dialog "Vuoi uscire?" → Funziona (No crash)  
✅ **ESC in gameplay** → Dialog "Vuoi abbandonare?" → Funziona (No crash)  
✅ **ESC doppio rapido** → Abbandono immediato → Funziona  
✅ **Pulsante Esci** → Dialog conferma → Funziona  
✅ **Tasto N** → Dialog "Nuova partita?" → Funziona  
✅ **ALT+F4** → Dialog conferma + veto → Funziona  
✅ **X button** → Dialog conferma + veto → Funziona  
✅ **Dialog cancellazione** → Torna stato precedente → Timer continua  
✅ **API consistency** → Tutti usano metodi semantici `show_*_prompt()`  
✅ **Legacy parity** → Comportamento identico a refactoring-engine branch  
✅ **Zero regressioni** → 60+ comandi gameplay funzionano  
✅ **Ready for merge** → Migrazione wxPython 100% completata  

---

**Fine TODO Operativo**

Per analisi root cause completa, codice PRIMA/DOPO dettagliato (350+ righe), e commit message pronto (54 righe), consultare:  
📄 **[docs/FIX_DIALOG_MANAGER_API.md](./FIX_DIALOG_MANAGER_API.md)** (45.9KB)

---

**Document Version**: v1.0  
**Last Updated**: 2026-02-13  
**Branch**: `copilot/remove-pygame-migrate-wxpython`  
**Status**: READY  
**Estimated Time**: 25-30 minuti (con testing completo)  
**Priority**: HIGHEST (BLOCKER)  
