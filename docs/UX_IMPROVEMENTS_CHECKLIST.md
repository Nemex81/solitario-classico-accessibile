# UX Improvements Checklist - v1.4.2

**Versione**: 1.4.2  
**Branch**: `refactoring-engine`  
**Status**: ⏳ IN PROGRESS (0/5 commits)  
**Inizio**: 08/02/2026  

---

## 📝 Riepilogo Funzionalità

☐ **Welcome Message** nel Game Submenu  
☐ **ESC Dialog** in Main Menu (Esci applicazione)  
☐ **ESC Dialog** in Game Submenu (Torna al main)  
☐ **ESC Dialog** durante Gameplay (Abbandona partita)  
☐ **Virtual Dialog Box** component (base infrastruttura)

---

## Commit #24: Virtual Dialog Box Component

**File**: `src/infrastructure/ui/dialog.py` (NEW)  
**SHA**: `________________`  
**Status**: ⏳ TODO  
**Stima**: 200 linee

### Task List

#### Struttura Base
- ☐ Creare file `dialog.py`
- ☐ Importare dipendenze (pygame, ScreenReader, typing)
- ☐ Definire classe `VirtualDialogBox`

#### Constructor
- ☐ Parametro `message: str` (testo dialog)
- ☐ Parametro `buttons: List[str]` (es. ["Sì", "No"])
- ☐ Parametro `default_button: int = 0` (focus iniziale)
- ☐ Parametro `on_confirm: Callable` (callback OK/Sì)
- ☐ Parametro `on_cancel: Callable` (callback Annulla/No)
- ☐ Parametro `screen_reader: ScreenReader`
- ☐ State: `self.is_open: bool = False`
- ☐ State: `self.current_button: int = default_button`

#### Metodi Pubblici
- ☐ `open() -> None`: Apre dialog + annuncia messaggio
- ☐ `close() -> None`: Chiude dialog
- ☐ `handle_keyboard_events(event) -> None`: Router input
- ☐ Property `is_open -> bool`: Getter stato

#### Navigation Methods
- ☐ `navigate_next() -> str`: Focus pulsante successivo (→ ↓)
- ☐ `navigate_prev() -> str`: Focus pulsante precedente (← ↑)
- ☐ `_announce_current_button() -> None`: Annuncia focus
- ☐ Wrap-around navigation (da ultimo a primo e viceversa)

#### Keyboard Handling
- ☐ Freccia →: `navigate_next()`
- ☐ Freccia ←: `navigate_prev()`
- ☐ Freccia ↓: `navigate_next()`
- ☐ Freccia ↑: `navigate_prev()`
- ☐ INVIO: `confirm_selection()`
- ☐ SPAZIO: `confirm_selection()`
- ☐ ESC: Esegue `on_cancel()` + chiude

#### Shortcut Keys
- ☐ `S` key: Auto-select "Sì" se presente
- ☐ `N` key: Auto-select "No" se presente
- ☐ `O` key: Auto-select "OK" se presente
- ☐ `A` key: Auto-select "Annulla" se presente
- ☐ Case-insensitive matching

#### Confirmation Logic
- ☐ `confirm_selection()`: Identifica pulsante corrente
- ☐ Se primo pulsante (index 0): Esegue `on_confirm()`
- ☐ Se altro pulsante: Esegue `on_cancel()`
- ☐ Chiude dialog dopo callback
- ☐ Gestione callback None (no-op)

#### TTS Announcements
- ☐ `open()`: Annuncia `message` + primo pulsante
- ☐ `navigate_*()`: Annuncia nuovo pulsante focus
- ☐ `confirm_selection()`: Nessun annuncio (callback gestisce)
- ☐ Tutti con `interrupt=True`

### Acceptance Criteria
- ✅ Dialog può essere aperto/chiuso
- ✅ Navigazione ↑↓←→ funziona
- ✅ INVIO conferma pulsante focus
- ✅ ESC chiama on_cancel
- ✅ Shortcut S/N/O/A funzionano
- ✅ TTS annuncia ogni cambio focus
- ✅ Wrap-around navigation attivo

### Test
```python
# Test istanza base
dialog = VirtualDialogBox(
    message="Vuoi continuare?",
    buttons=["Sì", "No"],
    default_button=0,
    on_confirm=lambda: print("CONFIRMED"),
    on_cancel=lambda: print("CANCELLED"),
    screen_reader=sr
)
assert not dialog.is_open

# Test open
dialog.open()
assert dialog.is_open
assert dialog.current_button == 0

# Test navigate
msg = dialog.navigate_next()
assert dialog.current_button == 1
assert "No" in msg

# Test wrap-around
msg = dialog.navigate_next()
assert dialog.current_button == 0  # Wraps to first
assert "Sì" in msg

# Test confirm
dialog.confirm_selection()  # Should print "CONFIRMED"
assert not dialog.is_open
```

---

## Commit #25: ESC Dialog in Main Menu

**File**: `test.py` (MODIFY)  
**SHA**: `________________`  
**Status**: ⏳ TODO  
**Dipendenze**: Commit #24

### Task List

#### Import
- ☐ Aggiungere `from src.infrastructure.ui.dialog import VirtualDialogBox`

#### Initialization
- ☐ In `__init__()`: Creare `self.exit_dialog = None`
- ☐ In `__init__()`: Aggiungere flag `self.exit_dialog_open = False`

#### Dialog Creation Method
- ☐ Metodo `show_exit_dialog()` 
- ☐ Messaggio: "Vuoi uscire dall'applicazione?"
- ☐ Pulsanti: ["OK", "Annulla"]
- ☐ Default button: 0 (OK)
- ☐ on_confirm: `self.quit_app`
- ☐ on_cancel: `self.close_exit_dialog`
- ☐ Annuncio vocale messaggio + "OK"

#### Event Routing
- ☐ In `handle_events()`: Check se main menu è attivo
- ☐ Intercettare ESC key quando `is_menu_open=True`
- ☐ NON intercettare se submenu è aperto
- ☐ Chiamare `show_exit_dialog()`
- ☐ Se dialog aperto: Routare eventi a `self.exit_dialog`
- ☐ Bloccare eventi menu quando dialog aperto

#### Dialog Close Handler
- ☐ Metodo `close_exit_dialog()`
- ☐ Chiudere dialog
- ☐ Annunciare ritorno al menu
- ☐ Reset flag `exit_dialog_open`

### Acceptance Criteria
- ✅ ESC in main menu apre dialog
- ✅ Dialog annuncia messaggio + "OK"
- ✅ Frecce navigano tra OK/Annulla
- ✅ INVIO su OK chiude app
- ✅ INVIO su Annulla torna al menu
- ✅ ESC nel dialog = Annulla
- ✅ Shortcut O/A funzionano

### Test
1. Avvia app → Main menu
2. Premi ESC
3. ✅ Senti: "Vuoi uscire dall'applicazione? OK."
4. Premi A
5. ✅ Torna al menu
6. Premi ESC
7. Premi O
8. ✅ App chiusa

---

## Commit #26: ESC Dialog in Game Submenu

**File**: `test.py` (MODIFY)  
**SHA**: `________________`  
**Status**: ⏳ TODO  
**Dipendenze**: Commit #24

### Task List

#### Initialization
- ☐ In `__init__()`: Creare `self.return_to_main_dialog = None`
- ☐ In `__init__()`: Aggiungere flag `self.return_dialog_open = False`

#### Dialog Creation Method
- ☐ Metodo `show_return_to_main_dialog()`
- ☐ Messaggio: "Vuoi tornare al menu principale?"
- ☐ Pulsanti: ["Sì", "No"]
- ☐ Default button: 0 (Sì)
- ☐ on_confirm: `self.confirm_return_to_main`
- ☐ on_cancel: `self.close_return_dialog`

#### Confirm Handler
- ☐ Metodo `confirm_return_to_main()`
- ☐ Chiudere game submenu: `self.menu.close_submenu()`
- ☐ Annunciare ritorno
- ☐ Ri-annunciare main menu
- ☐ Reset flag

#### Event Routing - ESC Key
- ☐ In `handle_events()`: Check se game submenu attivo
- ☐ Verificare `self.menu.active_submenu is not None`
- ☐ Intercettare ESC quando submenu attivo
- ☐ Chiamare `show_return_to_main_dialog()`
- ☐ Routare eventi a dialog quando aperto

#### Event Routing - "Chiudi" Item
- ☐ Modificare `handle_game_submenu_selection()`
- ☐ Item 2 ("Chiudi"): Chiamare `show_return_to_main_dialog()`
- ☐ NON chiudere submenu direttamente

### Acceptance Criteria
- ✅ ESC in game submenu apre dialog
- ✅ INVIO su "Chiudi" apre dialog
- ✅ Dialog annuncia "Vuoi tornare...? Sì."
- ✅ Navigazione funziona
- ✅ Sì torna al main menu
- ✅ No resta in game submenu
- ✅ Shortcut S/N funzionano

### Test
1. Main menu → INVIO su "Gioca"
2. Game submenu aperto
3. Premi ESC
4. ✅ Dialog aperto
5. Premi N
6. ✅ Resta in submenu
7. Naviga a "Chiudi"
8. Premi INVIO
9. ✅ Dialog aperto di nuovo
10. Premi S
11. ✅ Torna al main menu

---

## Commit #27: ESC Dialog During Gameplay

**File**: `test.py` (MODIFY)  
**SHA**: `________________`  
**Status**: ⏳ TODO  
**Dipendenze**: Commit #24

### Task List

#### Initialization
- ☐ In `__init__()`: Creare `self.abandon_game_dialog = None`
- ☐ In `__init__()`: Aggiungere flag `self.abandon_dialog_open = False`

#### Dialog Creation Method
- ☐ Metodo `show_abandon_game_dialog()`
- ☐ Messaggio: "Vuoi abbandonare la partita e tornare al menu di gioco?"
- ☐ Pulsanti: ["Sì", "No"]
- ☐ Default button: 0 (Sì)
- ☐ on_confirm: `self.confirm_abandon_game`
- ☐ on_cancel: `self.close_abandon_dialog`

#### Confirm Handler
- ☐ Metodo `confirm_abandon_game()`
- ☐ Chiudere dialog
- ☐ Tornare al game submenu (non main menu!)
- ☐ Settare `is_menu_open = True`
- ☐ Ri-annunciare game submenu
- ☐ Reset flag

#### Cancel Handler
- ☐ Metodo `close_abandon_dialog()`
- ☐ Chiudere dialog
- ☐ Annunciare ripresa gioco
- ☐ Reset flag

#### Event Routing
- ☐ In `handle_events()`: Check gameplay attivo
- ☐ Verificare `is_menu_open=False` AND `is_options_mode=False`
- ☐ Intercettare ESC key
- ☐ Bloccare chiamata a `return_to_menu()`
- ☐ Chiamare `show_abandon_game_dialog()`
- ☐ Routare eventi a dialog quando aperto
- ☐ Bloccare eventi gameplay quando dialog aperto

#### Doppio ESC Feature (BONUS)
- ☐ Tracciare timestamp primo ESC
- ☐ Se secondo ESC entro 2 secondi: Conferma automatica
- ☐ Annunciare "Uscita rapida" quando attivato
- ☐ Reset timer dopo timeout

### Acceptance Criteria
- ✅ ESC durante gioco apre dialog
- ✅ Dialog non interrompe GameEngine
- ✅ Sì torna al game submenu (non main!)
- ✅ No riprende gioco
- ✅ Navigazione funziona
- ✅ Shortcut S/N funzionano
- ✅ (BONUS) Doppio ESC conferma automaticamente

### Test
1. Avvia partita (N)
2. Gioca qualche mossa
3. Premi ESC
4. ✅ Dialog aperto, gioco in pausa
5. Premi ↓ (naviga a No)
6. Premi INVIO
7. ✅ Gioco riprende
8. Premi ESC
9. Premi ESC entro 1 secondo
10. ✅ (BONUS) Conferma automatica, vai a game submenu

---

## Commit #28: Welcome Message in Game Submenu

**File**: `src/infrastructure/ui/menu.py` (MODIFY)  
**SHA**: `________________`  
**Status**: ⏳ TODO  
**Dipendenze**: Nessuna (indipendente)

### Task List

#### Constructor Parameters
- ☐ Aggiungere parametro `welcome_message: Optional[str] = None`
- ☐ Aggiungere parametro `show_controls_hint: bool = True`
- ☐ Salvare in `self.welcome_message`
- ☐ Salvare in `self.show_controls_hint`

#### Welcome Method
- ☐ Metodo `announce_welcome() -> str`
- ☐ Costruire messaggio multi-parte:
  1. Welcome message (se presente)
  2. Controls hint (se abilitato)
  3. Annuncio prima voce menu
- ☐ Separare parti con newline o pausa
- ☐ Annunciare con `screen_reader.tts.speak()`

#### Default Controls Hint
- ☐ Testo: "Usa frecce su e giù per navigare tra le voci. Premi Invio per selezionare."
- ☐ Concatenare a welcome message

#### Integration
- ☐ Modificare `_announce_menu_open()` per accettare flag
- ☐ O creare metodo separato chiamato da `open_submenu()`
- ☐ Chiamare `announce_welcome()` quando submenu aperto
- ☐ NON chiamare per main menu (solo submenu)

#### Test.py Integration
- ☐ In `test.py`: Aggiungere welcome message al game submenu
- ☐ Messaggio: "Benvenuto nel menu di gioco del Solitario!"
- ☐ Abilitare `show_controls_hint=True`

### Acceptance Criteria
- ✅ INVIO su "Gioca" annuncia welcome + controls + prima voce
- ✅ Main menu NON annuncia welcome (solo submenu)
- ✅ Messaggio chiaro e conciso
- ✅ TTS non interrotto da eventi successivi
- ✅ Pausa adeguata tra welcome e annuncio voce

### Test
1. Avvia app → Main menu
2. Premi ↓ + INVIO su "Gioca"
3. ✅ Senti:
   - "Benvenuto nel menu di gioco del Solitario!"
   - "Usa frecce su e giù per navigare. Premi Invio per selezionare."
   - "Posizione corrente: Nuova partita."
4. Naviga con ↑↓
5. ✅ Normale annuncio voci (senza welcome)
6. Premi ESC, poi riapri
7. ✅ Welcome annunciato di nuovo

---

## 📊 Progress Summary

### Commits Completed: 0 / 5

- ☐ Commit #24: Virtual Dialog Box Component
- ☐ Commit #25: ESC Dialog in Main Menu
- ☐ Commit #26: ESC Dialog in Game Submenu
- ☐ Commit #27: ESC Dialog During Gameplay
- ☐ Commit #28: Welcome Message in Game Submenu

### Files Modified: 0 / 3

- ☐ `src/infrastructure/ui/dialog.py` (NEW)
- ☐ `src/infrastructure/ui/menu.py` (MODIFY)
- ☐ `test.py` (MODIFY)

### Total Lines Added: ~420

- dialog.py: ~200 linee
- menu.py: ~40 linee
- test.py: ~180 linee (somma commits 25+26+27)

---

## 🏁 Completion Criteria

### Funzionalità
- ✅ Tutti i 5 commit pushati
- ✅ Tutti i test manuali passati
- ✅ Nessun regression (features esistenti funzionanti)
- ✅ Welcome message funzionante
- ✅ 3 dialog ESC funzionanti

### Documentazione
- ✅ CHANGELOG.md aggiornato (v1.4.2)
- ✅ README.md aggiornato (se necessario)
- ✅ Questa checklist completata (☐ → ✅)

### Code Quality
- ✅ Nessun warning lint
- ✅ Docstring completi
- ✅ Type hints presenti
- ✅ Nessun codice duplicato

---

**Last Updated**: 08/02/2026 17:00 CET  
**Next Action**: Implementare Commit #24 (Dialog component)  
**ETA Completion**: ~3-4 ore
