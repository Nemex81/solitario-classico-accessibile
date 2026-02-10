[Il contenuto completo del file con le seguenti modifiche nella FASE 4]

## 🆕 FASE 4: Feature #3 - New Game Confirmation Dialog ⭐ NUOVO

### 📝 Problema Identificato

**Issue**: Durante testing v1.4.3, è emerso che premendo "N" (Nuova partita) durante una partita già in corso, viene immediatamente avviata una nuova partita senza chiedere conferma. Questo può causare **perdita accidentale del progresso** di gioco.

**Root Cause**: Il dialog è implementato SOLO per la selezione menu, ma NON per il comando tastiera "N" premuto durante il gameplay. Il metodo `_new_game()` in `gameplay_controller.py` ha un TODO ma non chiama il dialog.

**Soluzione**: Implementare dialog di conferma sia da menu CHE da comando "N" tastiera, usando callback architecture per chiamare il dialog di test.py.

---

### ⚠️ REQUISITO CRITICO: DUE PERCORSI DA IMPLEMENTARE

**Percorso 1: Menu → Nuova Partita** (✅ GIÀ IMPLEMENTATO da Copilot)
- File: `test.py`, metodo `handle_game_submenu_selection()`
- Status: ✅ Implementato correttamente

**Percorso 2: Comando Tastiera "N" durante Gameplay** (❌ DA IMPLEMENTARE)
- File: `src/application/gameplay_controller.py`, metodo `_new_game()`
- Status: ❌ NON implementato - ha solo TODO comment
- Soluzione: Aggiungere callback a test.py

---

### Step 4.0: Modifica GamePlayController (⭐ NUOVO)

- [ ] **Aprire file**: `src/application/gameplay_controller.py`
- [ ] **Metodo `__init__()`** (riga ~35-55):
  - [ ] Aggiungere parametro: `on_new_game_request: Optional[Callable[[], None]] = None`
  - [ ] Salvare: `self.on_new_game_request = on_new_game_request`
  - [ ] Documentare: "Callback quando utente richiede nuova partita con gioco attivo (v1.4.3)"
- [ ] **Metodo `_new_game()`** (riga ~353-365):
  - [ ] Trovare sezione con TODO: "Implementare dialog conferma in futuro"
  - [ ] Sostituire TODO con check reale:
    ```python
    if not game_over and self.on_new_game_request is not None:
        # Game in progress AND callback available
        self.on_new_game_request()  # Trigger dialog via callback
        return  # Don't start game yet, wait for confirmation
    ```
  - [ ] Rimuovere `pass` statement dopo TODO
  - [ ] Mantenere `self.engine.new_game()` per caso no-game o no-callback

#### Test Checklist Step 4.0
- [ ] **T0.1**: Callback None + nessuna partita → Avvia immediatamente (backward compatible)
- [ ] **T0.2**: Callback set + nessuna partita → Avvia immediatamente (no dialog needed)
- [ ] **T0.3**: Callback set + partita attiva → Chiama callback + NON avvia
- [ ] **T0.4**: Callback None + partita attiva → Avvia immediatamente (backward compatible)

---

### Step 4.0b: Collegare Callback in test.py

- [ ] **Aprire file**: `test.py`
- [ ] **Trovare sezione**: Inizializzazione `gameplay_controller` (riga ~150-160)
- [ ] **Modifica instantiation**:
  ```python
  self.gameplay_controller = GamePlayController(
      engine=self.engine,
      screen_reader=self.screen_reader,
      settings=self.settings,
      on_new_game_request=lambda: self.show_new_game_dialog()  # NEW (v1.4.3)
  )
  ```

#### Test Checklist Step 4.0b
- [ ] **T0.5**: Callback correttamente passato al controller
- [ ] **T0.6**: Lambda function risolve `self.show_new_game_dialog` correttamente
- [ ] **T0.7**: Nessun errore a runtime durante instantiation

---

### Step 4.1: Aggiungere Dialog Instance (`test.py`)

[... contenuto invariato, già completato da Copilot ...]

### Step 4.2: Modificare Handler Nuova Partita (`test.py`)

[... contenuto invariato, già completato da Copilot per path MENU ...]

### Step 4.3: Implementare Dialog Callbacks (`test.py`)

[... contenuto invariato, già completato da Copilot ...]

### Step 4.4: Gestione Eventi Dialog (`test.py`)

[... contenuto invariato, già completato da Copilot ...]

---

### Step 4.5: Testing Feature #3 Completo (AGGIORNATO)

#### Test Comportamento Base
- [ ] **T3.1**: Premere N senza partita attiva → Nuova partita inizia immediatamente (no dialog)
- [ ] **T3.2**: ⭐ Premere N **DURANTE GAMEPLAY** con partita in corso → Dialog "Vuoi abbandonare..." appare
- [ ] **T3.2b**: ⭐ Selezionare "Nuova partita" **DAL MENU** con partita in corso → Dialog appare (già implementato)
- [ ] **T3.3**: Dialog aperto, premere S → Partita precedente abbandonata, nuova inizia
- [ ] **T3.4**: Dialog aperto, premere N → Dialog chiuso, partita corrente continua
- [ ] **T3.5**: Dialog aperto, premere ESC → Dialog chiuso, partita corrente continua

[... resto dei test invariato ...]

---

## 📝 NOTES

### Session Log

[... log precedenti invariati ...]

**2026-02-10 12:25 CET (CORREZIONE CRITICA - Feature #3 Incompleta)**
- ⚠️ **PROBLEMA IDENTIFICATO**: Copilot ha implementato dialog SOLO per path menu
- ❌ **MANCANTE**: Dialog NON triggato da comando "N" tastiera durante gameplay
- 🔍 **ROOT CAUSE**: `gameplay_controller._new_game()` ha TODO ma non chiama dialog
- ✅ **SOLUZIONE**: Aggiungere callback `on_new_game_request` a gameplay_controller
- ✅ Aggiornato TODO.md con Step 4.0 e 4.0b (modifiche gameplay_controller + test.py)
- ✅ Aggiornato documentazione completa con sezione gameplay_controller
- 🔄 **PROSSIMO**: Implementare Step 4.0 e 4.0b per completare Feature #3

---

**Stato Attuale**: Feature #3 implementata al 50% - menu OK, keyboard command mancante
**Action Required**: Implementare Step 4.0 (gameplay_controller callback) + Step 4.0b (test.py collegamento)

---

**Fine TODO**  
Ultimo aggiornamento: 10 Febbraio 2026, 12:25 CET - Feature #3 correzione in corso
