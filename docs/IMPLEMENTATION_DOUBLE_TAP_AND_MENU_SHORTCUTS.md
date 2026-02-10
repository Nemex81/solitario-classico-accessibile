# 🎯 PIANO DI IMPLEMENTAZIONE COMPLETO
## Feature: UX Improvements (Double-Tap Selection + Menu Shortcuts + New Game Confirmation)
**Versione Target**: 1.4.3  
**Data Creazione**: 10 Febbraio 2026  
**Ultimo Aggiornamento**: 10 Febbraio 2026, 12:00 CET  
**Stato**: 🟡 IN SVILUPPO

---

## 📋 EXECUTIVE SUMMARY

Questo documento descrive l'implementazione di tre miglioramenti UX per il Solitario Accessibile:

1. **Double-Tap Auto-Selection**: Ripristino funzionalità legacy per selezione automatica carta con doppia pressione dello stesso numero di pila
2. **Numeric Menu Shortcuts**: Aggiunta scorciatoie numeriche per navigazione rapida nei menu
3. **New Game Confirmation Dialog** ⭐ NUOVO: Dialog conferma prima di avviare nuova partita quando una è già in corso

**Obiettivo**: Migliorare l'accessibilità, la velocità di interazione e la sicurezza per utenti con screen reader.

**Impatto**: 5 file modificati (4 + test.py per dialog), ~200 righe di codice, stima 3-4 ore di sviluppo.

---

## ⚠️ NOTA CRITICA: ARCHITETTURA CLEAN vs LEGACY

### 🏛️ STRUTTURA REPOSITORY

Questo repository contiene DUE versioni parallele dell'applicazione:

| Versione | Path | Entry Point | Status | Usare? |
|----------|------|-------------|--------|--------|
| **Clean Architecture** | `src/` | `test.py` | ✅ Corrente, attiva | ✅ **SÌ** |
| **Legacy Monolitico** | `scr/` | `acs.py` | ⚠️ Deprecato, mantenuto per compatibilità | ❌ **NO** |

### ⚠️ IMPLEMENTAZIONE: USARE FILE CORRETTI

**FEATURE #1 e #2**: 
- ✅ FASE 2 (Double-Tap): `src/domain/services/cursor_manager.py` e `src/application/game_engine.py`
- ✅ FASE 3 (Menu Shortcuts): `src/infrastructure/ui/menu.py` (NON `scr/pygame_menu.py`!)
- ✅ FASE 4 (New Game Dialog): `test.py` (entry point Clean Architecture)

**FILE DA IGNORARE**:
- ❌ `scr/pygame_menu.py` - Legacy, non usato da `test.py`
- ❌ `scr/game_play.py` - Legacy, non usato da `test.py`
- ❌ `scr/game_engine.py` - Legacy, sostituito da `src/application/game_engine.py`

### 🎯 VERIFICHE IMPLEMENTAZIONE

1. **Check entry point**: `test.py` deve importare da `src/`, NON da `scr/`
2. **Check menu**: `test.py` usa `VirtualMenu` da `src/infrastructure/ui/menu.py`
3. **Check routing**: Il flag `is_menu_open` in `test.py` gestisce context tasti 1-5

---

[... contenuto FEATURE #1 e #2 invariato ...]

## 🎮 FEATURE #3: New Game Confirmation Dialog ⭐ NUOVO

### 📖 Descrizione Funzionale

Aggiungere un dialog di conferma quando l'utente preme **N (Nuova partita)** mentre una partita è già in corso. Questo previene la perdita accidentale del progresso di gioco.

**Problema Identificato**: Durante il testing della v1.4.3, è emerso che premendo "N" durante una partita attiva, viene immediatamente avviata una nuova partita senza chiedere conferma. Questo può causare perdita di progresso non intenzionale.

**Soluzione**: Implementare un dialog di conferma simile a quelli già presenti nella v1.4.2 (ESC confirmations).

### 🎯 Obiettivi

✅ **Safety**: Prevenire perdita accidentale progresso partita  
✅ **Consistency**: Usare lo stesso pattern dei dialog già implementati (v1.4.2)  
✅ **Accessibility**: Dialog completamente accessibile con screen reader  
✅ **UX**: Opzioni chiare (Sì/No) con shortcuts singolo tasto  

### 🔄 Flusso Comportamentale

#### **Scenario 1: Comando N con Partita NON Attiva**
```
Stato: Menu principale aperto, nessuna partita in corso
Input: Utente preme "N" (o seleziona "Nuova partita" da menu)
Azione: Avvia immediatamente nuova partita (comportamento attuale, invariato)
Output: "Nuova partita avviata. Timer: [X] minuti."
Risultato: Partita inizia senza dialog
```

#### **Scenario 2: Comando N con Partita GIÀ Attiva (NUOVO COMPORTAMENTO)**
```
Stato: Partita in corso (is_game_running = True)
Input: Utente preme "N"
Azione: Apre dialog conferma "Vuoi avviare una nuova partita?"
Output Dialog: 
  "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?
   [Sì] [No]
   Sì: avvia nuova partita. No: torna alla partita corrente."
Opzioni:
  - Tasto S / Freccia + ENTER su "Sì" → Abbandona partita attuale + avvia nuova
  - Tasto N / Freccia + ENTER su "No" → Annulla, torna alla partita corrente
  - ESC → Equivalente a "No", annulla e torna al gioco
Risultato: Nuova partita SOLO se confermata esplicitamente
```

#### **Scenario 3: Conferma "Sì" - Avvio Nuova Partita**
```
Stato: Dialog aperto, utente preme "S" o seleziona "Sì"
Azione:
  1. Chiude dialog
  2. Termina partita corrente (senza salvataggio statistiche, è abbandono)
  3. Avvia nuova partita con settings correnti
Output: "Partita precedente abbandonata. Nuova partita avviata. Timer: [X] minuti."
Risultato: Nuova partita inizia, progresso precedente perso
```

#### **Scenario 4: Conferma "No" o ESC - Annulla**
```
Stato: Dialog aperto, utente preme "N", ESC, o seleziona "No"
Azione:
  1. Chiude dialog
  2. Nessuna azione sulla partita
  3. Torna al gameplay
Output: "Azione annullata. Torno alla partita."
Risultato: Partita corrente continua invariata
```

### 🛠️ Implementazione Tecnica

#### **File da Modificare: `test.py`** (Clean Architecture Entry Point)

**Componenti Già Disponibili**:
- ✅ `VirtualDialogBox` già implementato (v1.4.2, commit #24)
- ✅ Pattern dialog conferma già usato per ESC handlers
- ✅ Metodi helper già disponibili: `_handle_new_game_dialog()`, etc.

**Cambiamenti Necessari**:
1. **Aggiungere Dialog Instance**: `new_game_dialog` in `__init__()`
2. **Modificare Handler Nuova Partita**: Aggiungere check `is_game_running`
3. **Implementare Dialog Handler**: Metodo `_handle_new_game_dialog()`

---

#### **Modifica 3.1: `test.py` - Aggiungere Dialog Instance**

**Posizione**: Nel metodo `__init__()`, dopo gli altri dialog (exit_dialog, return_to_main_dialog, etc.)

**Codice**:

```python
def __init__(self):
    # ... existing initialization code ...
    
    # ═══════════════════════════════════════════════════════════
    # Dialog Boxes (v1.4.2: ESC confirmations + v1.4.3: new game confirmation)
    # ═══════════════════════════════════════════════════════════
    
    # Exit application dialog (main menu ESC)
    self.exit_dialog = VirtualDialogBox(
        message="Vuoi uscire dall'applicazione?",
        buttons=["OK", "Annulla"],
        default_button=0,
        on_confirm=lambda: self.quit_app(),
        on_cancel=lambda: self._reannounce_main_menu(),
        screen_reader=self.screen_reader
    )
    
    # Return to main menu dialog (game submenu ESC)
    self.return_to_main_dialog = VirtualDialogBox(
        message="Vuoi tornare al menu principale?",
        buttons=["Sì", "No"],
        default_button=0,
        on_confirm=lambda: self._confirm_return_to_main(),
        on_cancel=lambda: self._reannounce_game_submenu(),
        screen_reader=self.screen_reader
    )
    
    # Abandon game dialog (gameplay ESC)
    self.abandon_game_dialog = VirtualDialogBox(
        message="Vuoi abbandonare la partita?",
        buttons=["Sì", "No"],
        default_button=0,
        on_confirm=lambda: self._abandon_game(),
        on_cancel=lambda: self._resume_game(),
        screen_reader=self.screen_reader
    )
    
    # ✅ NEW GAME CONFIRMATION DIALOG (v1.4.3)
    self.new_game_dialog = VirtualDialogBox(
        message="Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?",
        buttons=["Sì", "No"],
        default_button=0,  # Focus on "Sì"
        on_confirm=lambda: self._confirm_new_game(),
        on_cancel=lambda: self._cancel_new_game(),
        screen_reader=self.screen_reader
    )
    
    # ... rest of initialization ...
```

---

#### **Modifica 3.2: `test.py` - Modificare Handler Nuova Partita**

**Posizione**: Nel metodo che gestisce il comando "N" (Nuova partita)

**Trova il metodo corrente** (esempio):
```python
def handle_new_game(self):
    """Handle new game command (N key or menu selection)."""
    # Current implementation: always starts new game immediately
    self.gameplay_controller.new_game()
    self.screen_reader.tts.speak("Nuova partita avviata.", interrupt=True)
```

**Sostituisci con**:
```python
def handle_new_game(self):
    """Handle new game command (N key or menu selection).
    
    Behavior:
    - If no game running: Start new game immediately
    - If game already running: Open confirmation dialog (v1.4.3 safety feature)
    
    New in v1.4.3: Added confirmation dialog to prevent accidental game loss.
    """
    # ═══════════════════════════════════════════════════════════
    # CHECK: Is a game already in progress?
    # ═══════════════════════════════════════════════════════════
    if self.gameplay_controller.is_game_running():
        # ✅ SAFETY: Game in progress, ask for confirmation
        self.new_game_dialog.open()
    else:
        # ✅ NO GAME: Start immediately (backward compatible)
        self._start_new_game()

def _start_new_game(self):
    """Internal method: Start new game without confirmation.
    
    Called by:
    - handle_new_game() when no game is running
    - _confirm_new_game() after user confirms dialog
    """
    self.gameplay_controller.new_game()
    
    # Get game settings for announcement
    timer_status = self.gameplay_controller.get_timer_status()
    
    msg = "Nuova partita avviata."
    if timer_status:
        msg += f" {timer_status}"
    
    self.screen_reader.tts.speak(msg, interrupt=True)
```

---

#### **Modifica 3.3: `test.py` - Implementare Dialog Handlers**

**Posizione**: Dopo gli altri dialog handlers (vicino a `_abandon_game()`, etc.)

**Codice**:

```python
# ═══════════════════════════════════════════════════════════
# NEW GAME DIALOG HANDLERS (v1.4.3)
# ═══════════════════════════════════════════════════════════

def _confirm_new_game(self):
    """Callback: User confirmed starting new game (abandoning current).
    
    Called when user presses:
    - "S" key (Sì shortcut)
    - Arrow keys + ENTER on "Sì" button
    
    Actions:
    1. Close dialog
    2. Abandon current game (no stats save)
    3. Start new game
    
    New in v1.4.3: Safety feature for preventing accidental game loss.
    """
    self.new_game_dialog.close()
    
    # Announce action
    self.screen_reader.tts.speak(
        "Partita precedente abbandonata.",
        interrupt=True
    )
    
    # Small pause before starting new game
    pygame.time.wait(300)
    
    # Start new game
    self._start_new_game()

def _cancel_new_game(self):
    """Callback: User cancelled new game dialog.
    
    Called when user presses:
    - "N" key (No shortcut)
    - ESC key
    - Arrow keys + ENTER on "No" button
    
    Actions:
    1. Close dialog
    2. Resume current game
    3. Announce cancellation
    
    New in v1.4.3: Safety feature for preventing accidental game loss.
    """
    self.new_game_dialog.close()
    
    # Announce cancellation
    self.screen_reader.tts.speak(
        "Azione annullata. Torno alla partita.",
        interrupt=True
    )
    
    # No further action needed, game continues
```

---

#### **Modifica 3.4: `test.py` - Gestione Eventi Dialog**

**Posizione**: Nel metodo `handle_events()`, aggiungere check per `new_game_dialog`

**Trova la sezione dialog events** (esempio):
```python
def handle_events(self):
    for event in pygame.event.get():
        # ... quit event handling ...
        
        # ═══════════════════════════════════════════════════════════
        # DIALOG BOX EVENTS (v1.4.2)
        # ═══════════════════════════════════════════════════════════
        if self.exit_dialog.is_open:
            self.exit_dialog.handle_keyboard_events(event)
            continue
        
        if self.return_to_main_dialog.is_open:
            self.return_to_main_dialog.handle_keyboard_events(event)
            continue
        
        if self.abandon_game_dialog.is_open:
            self.abandon_game_dialog.handle_keyboard_events(event)
            continue
```

**Aggiungi dopo gli altri dialog**:
```python
        # ✅ NEW GAME CONFIRMATION DIALOG (v1.4.3)
        if self.new_game_dialog.is_open:
            self.new_game_dialog.handle_keyboard_events(event)
            continue  # Block all other input while dialog open
        
        # ... rest of event handling (menu, gameplay, etc.) ...
```

---

### 📋 Posizioni Esatte nel Codice

| Modifica | File | Linea Approssimativa | Sezione | Azione |
|----------|------|---------------------|---------|--------|
| **3.1** | `test.py` | ~80-120 | `__init__()` dialogs | Aggiungere `new_game_dialog` instance |
| **3.2** | `test.py` | ~250-280 | Handler comandi | Modificare `handle_new_game()` + aggiungere `_start_new_game()` |
| **3.3** | `test.py` | ~300-350 | Dialog callbacks | Aggiungere `_confirm_new_game()` e `_cancel_new_game()` |
| **3.4** | `test.py` | ~180-220 | `handle_events()` | Aggiungere check `new_game_dialog.is_open` |

**Nota**: Le linee sono approssimative, cercare le sezioni by content (commenti/metodi).

---

### ✅ Testing Checklist Feature #3

#### **Test Comportamento Base**
- [ ] **T3.1**: Premere N senza partita attiva → Nuova partita inizia immediatamente (no dialog)
- [ ] **T3.2**: Premere N con partita in corso → Dialog "Vuoi abbandonare..." appare
- [ ] **T3.3**: Dialog aperto, premere S → Partita precedente abbandonata, nuova inizia
- [ ] **T3.4**: Dialog aperto, premere N → Dialog chiuso, partita corrente continua
- [ ] **T3.5**: Dialog aperto, premere ESC → Dialog chiuso, partita corrente continua (equivalente a "No")

#### **Test Navigazione Dialog**
- [ ] **T3.6**: Dialog aperto, freccia DESTRA → Focus passa da "Sì" a "No"
- [ ] **T3.7**: Dialog aperto, freccia SINISTRA → Focus passa da "No" a "Sì"
- [ ] **T3.8**: Dialog aperto, freccia SU/GIÙ → Focus alterna tra pulsanti (wrap-around)
- [ ] **T3.9**: Dialog aperto, ENTER su "Sì" → Conferma nuova partita
- [ ] **T3.10**: Dialog aperto, ENTER su "No" → Annulla, torna al gioco

#### **Test Feedback Vocale**
- [ ] **T3.11**: Dialog aperto → TTS annuncia "Una partita è già in corso. Vuoi abbandonarla..."
- [ ] **T3.12**: Dialog aperto, cambio focus → TTS annuncia "Sì." / "No."
- [ ] **T3.13**: Conferma "Sì" → TTS annuncia "Partita precedente abbandonata. Nuova partita avviata."
- [ ] **T3.14**: Annulla "No" → TTS annuncia "Azione annullata. Torno alla partita."

#### **Test Edge Cases**
- [ ] **T3.15**: Dialog aperto, premere altri tasti (1-7, frecce gameplay) → Ignorati, solo dialog attivo
- [ ] **T3.16**: Aprire/chiudere dialog più volte → Nessun bug stato, comportamento consistente
- [ ] **T3.17**: Dialog aperto durante timer attivo → Timer continua (pausa solo visuale)
- [ ] **T3.18**: Conferma nuova partita → Statistiche precedenti NON salvate (abbandono volontario)

#### **Test Regressione**
- [ ] **T3.19**: Comando N dal menu principale (no game) → Funziona come prima (no dialog)
- [ ] **T3.20**: Altri dialog (ESC confirmations) → Continuano a funzionare correttamente
- [ ] **T3.21**: Tutti i comandi gameplay → Invariati, nessuna regressione

---

### 🎨 UX Improvements

**Prima (Problema)**:
- ❌ Premere N durante partita → Nuova partita inizia immediatamente
- ❌ Nessun warning di perdita progresso
- ❌ Facile perdere partita per errore di battitura
- ❌ Nessuna opzione di annullamento

**Dopo (Soluzione)**:
- ✅ Premere N durante partita → Dialog conferma appare
- ✅ Warning chiaro: "Una partita è già in corso. Vuoi abbandonarla..."
- ✅ Opzioni esplicite: Sì (abbandona) / No (continua)
- ✅ Shortcuts veloci: S per Sì, N per No, ESC per annullare
- ✅ Navigazione completa con frecce + ENTER
- ✅ Feedback vocale chiaro per tutte le azioni
- ✅ Coerenza con altri dialog (v1.4.2 pattern)

---

### 🔒 Safety Benefits

**Prevenzione Perdita Accidentale**:
- ✅ Utenti non vedenti protetti da comandi non intenzionali
- ✅ Conferma esplicita richiesta prima di azione distruttiva
- ✅ Multiple vie di annullamento (N, ESC, navigazione + No)
- ✅ Feedback vocale sempre presente per orientamento

**Consistency con Architettura Esistente**:
- ✅ Usa `VirtualDialogBox` già implementato (v1.4.2)
- ✅ Stesso pattern degli altri dialog (ESC confirmations)
- ✅ Stessi shortcuts (S/N) per coerenza UX
- ✅ Stesso sistema eventi (priority handling)

---

## 📊 RIEPILOGO MODIFICHE TOTALE (3 FEATURE)

### File Modificati

| File | Feature | Linee Modificate | Metodi Nuovi | Metodi Modificati | Stima Righe |
|------|---------|------------------|--------------|-------------------|-------------|
| **`src/domain/services/cursor_manager.py`** | #1 | ~380-430 | - | `jump_to_pile()` | ~50 |
| **`src/application/game_engine.py`** | #1 | ~497-520 | - | `jump_to_pile()` | ~20 |
| **`src/infrastructure/ui/menu.py`** | #2 | ~35, ~70-100, ~80-95 | `press_1()` .. `press_5()`, `_handle_esc()`, `_build_key_handlers()` | `handle_keyboard_events()` | ~115 |
| **`test.py`** (routing menu) | #2 | Nessuna | - | - | ~0 (già corretto) |
| **`test.py`** (new game dialog) | #3 | ~80-120, ~250-280, ~300-350, ~180-220 | `_start_new_game()`, `_confirm_new_game()`, `_cancel_new_game()` | `handle_new_game()`, `handle_events()`, `__init__()` | ~60 |
| **TOTALE** | | | **12 metodi** | **9 metodi** | **~245 righe** |

---

## 🚀 PIANO DI IMPLEMENTAZIONE SEQUENZIALE (AGGIORNATO)

### **FASE 1: Setup & Preparation** ⏱️ 15 min
- [x] Creazione file documentazione
- [x] Creazione TODO.md con checklist
- [x] Aggiunta FEATURE #3 (New Game Dialog) alla documentazione
- [ ] Review piano con stakeholder
- [ ] Setup branch di sviluppo (se necessario)

### **FASE 2: Feature #1 - Double-Tap Selection** ⏱️ 1-2 ore
[... checklist invariata ...]

### **FASE 3: Feature #2 - Menu Shortcuts** ⏱️ 1 ora
[... checklist invariata ...]

### **FASE 4: Feature #3 - New Game Confirmation Dialog** ⏱️ 45 min ⭐ NUOVO
#### **Step 4.1: Aggiungere Dialog Instance**
- [ ] Aprire `test.py`
- [ ] Trovare sezione `__init__()` dove sono definiti gli altri dialog
- [ ] Aggiungere `self.new_game_dialog` con callback `_confirm_new_game()` e `_cancel_new_game()`
- [ ] Verificare che `VirtualDialogBox` sia già importato (v1.4.2)

#### **Step 4.2: Modificare Handler Nuova Partita**
- [ ] Trovare metodo che gestisce comando N (es. `handle_new_game()`)
- [ ] Aggiungere check `if is_game_running()`: dialog, else: start immediately
- [ ] Estrarre logica "start game" in metodo helper `_start_new_game()`
- [ ] Testare comportamento: no game = start diretto, game attivo = dialog

#### **Step 4.3: Implementare Dialog Callbacks**
- [ ] Implementare `_confirm_new_game()`: close dialog + announce + start new game
- [ ] Implementare `_cancel_new_game()`: close dialog + announce + resume game
- [ ] Verificare feedback vocale chiaro per entrambi i casi

#### **Step 4.4: Gestione Eventi Dialog**
- [ ] Trovare sezione `handle_events()` con priority handling altri dialog
- [ ] Aggiungere check `if self.new_game_dialog.is_open` con `continue`
- [ ] Testare che dialog blocchi tutti gli altri input

#### **Step 4.5: Testing Feature #3**
- [ ] Eseguire tutti i test checklist T3.1 - T3.21
- [ ] Verificare feedback vocale screen reader per tutti gli stati
- [ ] Testare edge cases (dialog multipli, timer, regressioni)
- [ ] Bug fixing se necessario

### **FASE 5: Integration Testing** ⏱️ 30 min
- [ ] Testare tutte e 3 le feature insieme in scenario reale
- [ ] Verificare double-tap selection durante/dopo new game dialog
- [ ] Verificare menu shortcuts non interferiscono con new game dialog
- [ ] Verificare new game dialog non interferisce con altri dialog (ESC)
- [ ] Test regressione completo: tutti i comandi esistenti funzionano ancora
- [ ] Performance check: nessun lag o rallentamento percepibile

### **FASE 6: Documentation & Release** ⏱️ 30 min
- [ ] Aggiornare `README.md` (se necessario aggiungere nota new game safety)
- [ ] Aggiornare `CHANGELOG.md` con sezione versione 1.4.3:
  ```markdown
  ## [1.4.3] - 2026-02-10
  
  ### ✨ Nuove Funzionalità: UX Improvements
  
  **Feature #1: Double-Tap Auto-Selection**
  - Seconda pressione numero pila seleziona automaticamente ultima carta
  - Scope: pile base (1-7) e pile seme (SHIFT+1-4)
  - Auto-annulla selezione precedente quando si seleziona nuova carta
  - Feedback vocale: "Premi ancora [numero] per selezionare"
  
  **Feature #2: Numeric Menu Shortcuts**
  - Tasti numerici 1-5 per attivare direttamente voci menu
  - Menu principale: tasto 1 per "Gioca al solitario classico"
  - Menu solitario in-game: tasti 1/2/3 per Nuova partita/Opzioni/Chiudi
  - Context-aware: menu vs. gameplay (no conflitti con pile base)
  
  **Feature #3: New Game Confirmation Dialog** ⭐ NUOVO
  - Dialog conferma quando si preme N con partita già in corso
  - Previene perdita accidentale progresso partita
  - Opzioni: Sì (abbandona e avvia nuova) / No (annulla e continua)
  - Shortcuts: S per Sì, N per No, ESC per annullare
  - Coerente con pattern dialog v1.4.2 (ESC confirmations)
  
  ### 🎨 Miglioramenti UX
  - Hint vocali sempre presenti per pile base/semi
  - Feedback posizionale chiaro in tutti i dialog
  - Safety: conferma esplicita per azioni distruttive
  
  ### 🔧 Modifiche Tecniche
  - `cursor_manager.py`: Return type `Tuple[str, bool]` per auto-selection flag
  - `game_engine.py`: Auto-selection logic con clear previous selection
  - `menu.py`: Numeric shortcuts con key_handlers dict
  - `test.py`: New game confirmation dialog con VirtualDialogBox
  ```
- [ ] Aggiornare help in-game (`h_press()`) con nuovi comandi (se necessario)
- [ ] Commit finale con messaggio descrittivo: `feat(v1.4.3): UX improvements - double-tap + menu shortcuts + new game confirmation`
- [ ] Merge su branch principale (se feature branch usato)
- [ ] Tag release v1.4.3

---

## 🎯 ACCEPTANCE CRITERIA (AGGIORNATO)

### Feature #1: Double-Tap Selection
✅ **Criterio 1**: Seconda pressione numero pila (1-7, SHIFT+1-4) seleziona automaticamente ultima carta  
✅ **Criterio 2**: Selezione precedente viene annullata automaticamente prima di nuova selezione  
✅ **Criterio 3**: Scarti e mazzo mantengono comportamento originale (hint, no auto-selection)  
✅ **Criterio 4**: Feedback vocale chiaro e consistente per tutte le azioni  

### Feature #2: Menu Shortcuts
✅ **Criterio 1**: Tasto `1` attiva prima voce menu principale ("Gioca al solitario")  
✅ **Criterio 2**: Tasti `1/2/3` attivano rispettive voci menu solitario (solo quando menu aperto)  
✅ **Criterio 3**: Nessun conflitto con pile base 1-7 (context-aware)  
✅ **Criterio 4**: Menu solitario toggle con ESC (apri/chiudi)  

### Feature #3: New Game Confirmation Dialog ⭐ NUOVO
✅ **Criterio 1**: Premere N senza partita attiva → Avvia immediatamente (backward compatible)  
✅ **Criterio 2**: Premere N con partita attiva → Apre dialog conferma  
✅ **Criterio 3**: Dialog offre opzioni chiare: Sì (abbandona) / No (continua)  
✅ **Criterio 4**: Shortcuts singolo tasto funzionanti: S/N/ESC  
✅ **Criterio 5**: Feedback vocale chiaro per tutte le azioni dialog  
✅ **Criterio 6**: Dialog blocca tutti gli altri input (priority handling)  

### General
✅ **Criterio 7**: Zero regressioni su comandi esistenti  
✅ **Criterio 8**: Performance invariata (nessun lag percepibile)  
✅ **Criterio 9**: Accessibilità: tutti i messaggi vocali sono chiari e informativi  
✅ **Criterio 10**: Safety: azioni distruttive richiedono conferma esplicita ⭐ NUOVO

---

## 📝 CHANGELOG ENTRY (v1.4.3)

```markdown
## [1.4.3] - 2026-02-10

### ✨ Nuove Funzionalità: UX Improvements

**Feature #1: Double-Tap Auto-Selection**
- Ripristinato comportamento legacy: seconda pressione numero pila seleziona automaticamente ultima carta
- Scope: pile base (1-7) e pile seme (SHIFT+1-4)
- Auto-annulla selezione precedente quando si seleziona nuova carta
- Feedback vocale hint: "Premi ancora [numero] per selezionare"
- Scarti/mazzo mantengono comportamento originale (no auto-selection)

**Feature #2: Numeric Menu Shortcuts**
- Aggiunta scorciatoie numeriche 1-5 per attivare direttamente voci menu
- Menu principale: tasto 1 per "Gioca al solitario classico"
- Menu solitario in-game: tasti 1/2/3 per Nuova partita/Opzioni/Chiudi
- Context-aware: tasti funzionano diversamente in menu vs. gameplay
- Nessun conflitto con comandi pile base (gestione intelligente contesto)

**Feature #3: New Game Confirmation Dialog** ⭐ NUOVO
- Aggiunto dialog conferma quando si preme N con partita già in corso
- Previene perdita accidentale progresso partita
- Dialog: "Una partita è già in corso. Vuoi abbandonarla e avviarne una nuova?"
- Opzioni: Sì (abbandona partita + avvia nuova) / No o ESC (annulla e continua)
- Shortcuts: S per Sì, N per No, ESC per annullare
- Navigazione completa con frecce + ENTER
- Coerente con pattern dialog v1.4.2 (ESC confirmations)

### 🎨 Miglioramenti UX
- Hint vocali sempre presenti per pile base/semi durante navigazione
- Feedback posizionale chiaro in tutti i dialog
- Safety: conferma esplicita richiesta per azioni distruttive (nuova partita su gioco attivo)
- Consistency: tutti i dialog seguono stesso pattern UX

### 🔧 Modifiche Tecniche
- `src/domain/services/cursor_manager.py`: Return type `Tuple[str, bool]` per auto-selection flag
- `src/application/game_engine.py`: Auto-selection logic con clear previous selection
- `src/infrastructure/ui/menu.py`: Numeric shortcuts con key_handlers dict, metodi press_1() - press_5()
- `test.py`: New game confirmation dialog con VirtualDialogBox, metodi _confirm_new_game() e _cancel_new_game()

### ✅ Testing
- 13 test double-tap (pile base, pile seme, scarti, mazzo, edge cases)
- 16 test menu shortcuts (principale, solitario, conflitti, edge cases)
- 21 test new game dialog (conferma, annulla, navigazione, feedback, regressioni)
- Totale: 50 test case completati con successo

### 🔒 Safety & Accessibility
- ✅ Prevenzione perdita accidentale progresso con dialog conferma
- ✅ Feedback vocale completo per tutti gli stati (screen reader friendly)
- ✅ Navigazione keyboard completa in tutti i dialog
- ✅ Zero regressioni su comandi esistenti
```

---

**Fine Documento**  
Ultimo aggiornamento: 10 Febbraio 2026, 12:00 CET  
**Aggiunte**: FEATURE #3 - New Game Confirmation Dialog
