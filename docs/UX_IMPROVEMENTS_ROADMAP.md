# UX Improvements Roadmap - v1.4.2

**Branch**: `refactoring-engine`  
**Status**: 📋 PLANNING  
**Target**: Migliorare UX con messaggi di benvenuto e dialog conferma ESC

---

## 🎯 Obiettivi

### 1. **Welcome Message nel Game Submenu**
Quando l'utente fa INVIO su "Gioca al solitario classico", aggiungere:
- ✅ Frase di benvenuto
- ✅ Breve descrizione comandi navigazione menu
- ✅ Lettura automatica della prima voce ("Nuova partita")

**Esempio vocale**:
```
"Benvenuto nel menu di gioco del Solitario!
Usa frecce su e giù per navigare, Invio per selezionare.
Nuova partita."
```

---

### 2. **Dialog Conferma ESC - Main Menu**
**Contesto**: Menu principale (Gioca / Esci)  
**Trigger**: Pressione tasto ESC

**Comportamento**:
- Apre dialog: "Vuoi uscire dall'applicazione?"
- Pulsanti: **OK** (focus attivo) / Annulla
- OK → Chiude applicazione
- Annulla → Ritorna al menu principale

**Comandi**:
- `↑↓` o `←→`: Naviga tra pulsanti
- `INVIO` o `SPAZIO`: Conferma selezione
- `ESC`: Equivalente ad Annulla
- `O`: Equivalente ad OK (shortcut)
- `A` o `N`: Equivalente ad Annulla (shortcut)

---

### 3. **Dialog Conferma ESC - Game Submenu**
**Contesto**: Menu di gioco (Nuova partita / Opzioni / Chiudi)  
**Trigger**: Pressione tasto ESC o INVIO su "Chiudi"

**Comportamento**:
- Apre dialog: "Vuoi tornare al menu principale?"
- Pulsanti: **Sì** (focus attivo) / No
- Sì → Torna al main menu
- No → Resta nel game submenu

**Comandi**:
- `↑↓` o `←→`: Naviga tra pulsanti
- `INVIO` o `SPAZIO`: Conferma selezione
- `ESC`: Equivalente a No (rimane nel menu)
- `S`: Equivalente a Sì (shortcut)
- `N`: Equivalente a No (shortcut)

---

### 4. **Dialog Conferma ESC - Durante Gameplay**
**Contesto**: Partita in corso  
**Trigger**: Pressione tasto ESC

**Comportamento**:
- Apre dialog: "Vuoi abbandonare la partita e tornare al menu di gioco?"
- Pulsanti: **Sì** (focus attivo) / No
- Sì → Abbandona partita → Game submenu
- No → Riprende gameplay

**Comandi**:
- `↑↓` o `←→`: Naviga tra pulsanti
- `INVIO` o `SPAZIO`: Conferma selezione
- `ESC`: Secondo ESC conferma Sì (doppio ESC per uscita rapida)
- `S`: Equivalente a Sì (shortcut)
- `N`: Equivalente a No (shortcut)

---

## 🏗️ Architettura

### **Nuovo Componente: VirtualDialogBox**
**Path**: `src/infrastructure/ui/dialog.py`

**Responsabilità**:
- Gestione dialog box virtuali (solo audio)
- Focus management tra pulsanti
- Keyboard navigation (↑↓←→ + INVIO/ESC)
- Callback per azioni OK/Cancel
- Annunci TTS con focus corrente

**API**:
```python
class VirtualDialogBox:
    def __init__(
        self,
        message: str,
        buttons: List[str],  # ["OK", "Annulla"] o ["Sì", "No"]
        default_button: int = 0,  # Index del pulsante con focus
        on_confirm: Callable = None,
        on_cancel: Callable = None,
        screen_reader: ScreenReader = None
    )
    
    def open(self) -> None:
        """Apre dialog e annuncia messaggio + pulsante focus."""
    
    def close(self) -> None:
        """Chiude dialog."""
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Gestisce navigazione e conferma."""
    
    def navigate_next(self) -> str:
        """Focus al prossimo pulsante (→ o ↓)."""
    
    def navigate_prev(self) -> str:
        """Focus al pulsante precedente (← o ↑)."""
    
    def confirm_selection(self) -> None:
        """Conferma pulsante con focus (INVIO/SPAZIO)."""
    
    @property
    def is_open(self) -> bool:
        """True se dialog è attivo."""
```

---

## 📋 Implementation Plan - 5 Commits

### **Commit #24: Virtual Dialog Box Component**
**File**: `src/infrastructure/ui/dialog.py` (NEW)

**Contenuto**:
- Classe `VirtualDialogBox`
- Keyboard navigation (↑↓←→)
- Button focus management
- TTS announcements
- Callback execution
- Shortcut keys (S/N/O/A)

**Test manuale**:
```python
# Test dialog Sì/No
dialog = VirtualDialogBox(
    message="Vuoi continuare?",
    buttons=["Sì", "No"],
    default_button=0,
    on_confirm=lambda: print("Confermato!"),
    on_cancel=lambda: print("Annullato!"),
    screen_reader=sr
)
```

**Stima**: ~200 linee  
**Complessità**: Media

---

### **Commit #25: ESC Dialog in Main Menu**
**File**: `test.py` (MODIFY)

**Modifiche**:
1. Aggiungere `self.exit_dialog` in `__init__`
2. Modificare `handle_events()` per intercettare ESC nel main menu
3. Aggiungere metodo `show_exit_dialog()`
4. Routing eventi a dialog quando aperto

**Flow**:
```
Main Menu → ESC pressed
  ↓
Open dialog "Vuoi uscire?"
  ↓
User navigates (↑↓) and selects
  ↓
OK → quit_app()
Annulla → Close dialog, stay in menu
```

**Stima**: ~50 linee  
**Complessità**: Bassa

---

### **Commit #26: ESC Dialog in Game Submenu**
**File**: `test.py` (MODIFY)

**Modifiche**:
1. Aggiungere `self.return_to_main_dialog` in `__init__`
2. Modificare `handle_game_submenu_selection()` per item 2 (Chiudi)
3. Intercettare ESC quando game submenu è attivo
4. Aggiungere metodo `show_return_to_main_dialog()`

**Flow**:
```
Game Submenu → ESC pressed OR INVIO on "Chiudi"
  ↓
Open dialog "Vuoi tornare al menu principale?"
  ↓
User navigates and selects
  ↓
Sì → Close submenu, return to main menu
No → Stay in game submenu
```

**Stima**: ~60 linee  
**Complessità**: Bassa

---

### **Commit #27: ESC Dialog During Gameplay**
**File**: `test.py` (MODIFY)

**Modifiche**:
1. Aggiungere `self.abandon_game_dialog` in `__init__`
2. Modificare `handle_events()` per intercettare ESC durante gameplay
3. Aggiungere metodo `show_abandon_game_dialog()`
4. Gestire doppio ESC per conferma rapida (opzionale)

**Flow**:
```
Gameplay → ESC pressed
  ↓
Open dialog "Vuoi abbandonare la partita?"
  ↓
User navigates and selects
  ↓
Sì → Return to game submenu
No → Resume gameplay
```

**Feature avanzata - Doppio ESC**:
- Primo ESC: Apre dialog
- Secondo ESC entro 2 secondi: Conferma Sì automaticamente

**Stima**: ~70 linee  
**Complessità**: Media

---

### **Commit #28: Welcome Message in Game Submenu**
**File**: `src/infrastructure/ui/menu.py` (MODIFY)

**Modifiche**:
1. Aggiungere metodo `announce_welcome()` in `VirtualMenu`
2. Chiamare `announce_welcome()` quando submenu viene aperto
3. Concatenare: benvenuto + comandi + prima voce

**Messaggio**:
```
"Benvenuto nel menu di gioco del Solitario!
Usa frecce su e giù per navigare tra le voci.
Premi Invio per selezionare.
Posizione corrente: Nuova partita."
```

**Parametri configurabili**:
```python
VirtualMenu(
    ...,
    welcome_message: Optional[str] = None,
    show_controls_hint: bool = True
)
```

**Stima**: ~40 linee  
**Complessità**: Bassa

---

## 🧪 Test Plan

### **Test Case 1: Main Menu ESC**
1. Avvia app → Main menu
2. Premi ESC
3. ✅ Senti: "Vuoi uscire dall'applicazione? OK."
4. Premi ↓
5. ✅ Senti: "Annulla"
6. Premi INVIO
7. ✅ Dialog chiuso, resta nel main menu
8. Premi ESC di nuovo
9. Premi INVIO (su OK)
10. ✅ Applicazione chiusa

### **Test Case 2: Game Submenu ESC**
1. Avvia partita → Game submenu
2. ✅ Senti benvenuto + "Nuova partita"
3. Premi ESC
4. ✅ Senti: "Vuoi tornare al menu principale? Sì."
5. Premi N (shortcut No)
6. ✅ Resta in game submenu
7. Naviga a "Chiudi"
8. Premi INVIO
9. ✅ Stesso dialog
10. Premi S (shortcut Sì)
11. ✅ Torna al main menu

### **Test Case 3: Gameplay ESC**
1. Avvia partita (N)
2. Durante gioco, premi ESC
3. ✅ Senti: "Vuoi abbandonare la partita? Sì."
4. Premi ←
5. ✅ Senti: "No"
6. Premi SPAZIO
7. ✅ Riprende gameplay
8. Premi ESC di nuovo
9. Premi ESC subito (doppio ESC)
10. ✅ Conferma automatica, torna a game submenu

### **Test Case 4: Navigation in Dialog**
1. Apri qualsiasi dialog
2. Premi ↑
3. ✅ Wrap-around all'ultimo pulsante
4. Premi →
5. ✅ Wrap-around al primo pulsante
6. Premi ↓ e ← alternativamente
7. ✅ Navigazione funzionante in entrambe le direzioni

---

## 📊 Progress Tracking

| Commit | Descrizione | File | Linee | Status |
|--------|-------------|------|-------|--------|
| #24 | Virtual Dialog Box | `dialog.py` | ~200 | ⏳ TODO |
| #25 | ESC in Main Menu | `test.py` | ~50 | ⏳ TODO |
| #26 | ESC in Game Submenu | `test.py` | ~60 | ⏳ TODO |
| #27 | ESC in Gameplay | `test.py` | ~70 | ⏳ TODO |
| #28 | Welcome Message | `menu.py` | ~40 | ⏳ TODO |
| **TOTALE** | **v1.4.2 Complete** | **3 files** | **~420** | **0/5** |

---

## 🎨 Design Notes

### **Accessibilità**
- **Shortcuts singolo tasto**: S/N per Sì/No, O/A per OK/Annulla
- **Navigazione ridondante**: ↑↓ E ←→ funzionano entrambe
- **Annunci verbosi**: Sempre annunciare messaggio + pulsante focus
- **Feedback immediato**: TTS interrompe sempre (interrupt=True)
- **Doppio ESC**: Feature power user per uscita rapida

### **Consistenza UX**
- Tutti i dialog usano stessa classe `VirtualDialogBox`
- Focus sempre sul pulsante "affermativo" (OK/Sì) di default
- ESC sempre equivalente a "negativo" (Annulla/No)
- Messaggi chiari e concisi (max 2 frasi)

### **Estensibilità Futura**
- `VirtualDialogBox` riutilizzabile per altri dialog:
  - Conferma nuovo gioco (se partita in corso)
  - Conferma chiusura opzioni con modifiche
  - Alert vittoria con statistiche
  - Alert sconfitta (tempo scaduto)

---

## 🚀 Next Steps

1. ✅ Review e approvazione roadmap
2. ⏳ Implementare Commit #24 (Dialog component)
3. ⏳ Implementare Commits #25-27 (ESC handling)
4. ⏳ Implementare Commit #28 (Welcome message)
5. ⏳ Testing completo con utente non vedente
6. ⏳ Update CHANGELOG v1.4.2
7. ⏳ Merge in main branch

---

**Estimated Total Time**: 3-4 ore  
**Priority**: Alta (UX critica per accessibilità)  
**Blockers**: Nessuno (componenti indipendenti)
