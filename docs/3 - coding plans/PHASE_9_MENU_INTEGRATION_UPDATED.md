# 📝 PHASE 9: Menu Integration - Detailed Implementation Guide

**Status**: Implementation Ready  
**Estimated Time**: 33-49 minuti (3 commit)  
**Branch**: `copilot/implement-profile-system-v3-1-0`  
**Prerequisiti**: Phase 1-8 completate ✅

---

## 🎯 Obiettivo Phase 9

Integrare i dialogs già creati (Phase 5-6) nel sistema menu del gioco:

1. **Commit 9.1**: LastGameDialog + menu "U - Ultima Partita"
2. **Commit 9.2**: Menu "L - Leaderboard Globale"
3. **Commit 9.3**: Profile menu opzione "5" → DetailedStatsDialog

---

## 📝 File Target Identificati

### Entry Point e Menu Principale

**File**: `acs_wx.py` (root directory)  
**Ruolo**: Main entry point del gioco, gestisce menu principale e profile menu  
**Pattern da cercare**:
- Costruzione menu: cerca stringhe come `"Nuova Partita"`, `"Opzioni"`, `"Esci"`
- Handler input: metodo che processa tasti premuti nel menu
- Profile menu: cerca `"Cambia Profilo"`, `"Crea Nuovo"`, `"Statistiche"`

### GameEngine

**File**: `src/application/game_engine.py`  
**Ruolo**: Già modificato in Phase 7, contiene ProfileService e dialog hooks  
**Modifiche necessarie**:
- Add: `self.last_session_outcome` storage
- Add: `show_last_game_summary()` method

---

## 🔍 STEP 0: Scouting (Opzionale - 5 min)

Se i metodi menu non sono evidenti, eseguire prima scouting:

```python
# In acs_wx.py, cercare:

# 1. Main menu builder/display
def show_main_menu(self):  # Possibile nome
    pass

def _build_main_menu(self):  # Possibile nome
    pass

# 2. Menu input handler
def _handle_menu_input(self, key):  # Possibile nome
    pass

def on_key_press(self, event):  # Possibile nome
    pass

# 3. Profile menu handler
def show_profile_menu(self):  # Possibile nome
    pass

def _handle_profile_menu(self, choice):  # Possibile nome
    pass
```

**Report**: Annotare nome metodo + line number prima di procedere.

---

## ✅ COMMIT 9.1: "Ultima Partita" Menu Option (15-22 min)

### 🎯 Obiettivo

Creare dialog LastGameDialog + memorizzare ultima sessione + aggiungere menu "U".

### 📝 File da Creare

**File**: `src/presentation/dialogs/last_game_dialog.py` (NEW)

```python
"""Last game summary dialog (read-only)."""

import wx
from datetime import datetime
from typing import Dict

from src.domain.models.profile import SessionOutcome
from src.presentation.formatters.stats_formatter import StatsFormatter


class LastGameDialog(wx.Dialog):
    """Show summary of last completed game.
    
    Read-only dialog with:
    - Game date/time
    - Outcome (vittoria/abbandono/timeout)
    - Time played, moves, score
    - Game config (difficulty, deck, timer)
    
    Keyboard:
    - ESC: Close
    """
    
    def __init__(self, parent, outcome: SessionOutcome):
        super().__init__(
            parent,
            title="Ultima Partita Giocata",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.outcome = outcome
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(self, label="RIEPILOGO ULTIMA PARTITA")
        font = header.GetFont()
        font.PointSize += 1
        font = font.Bold()
        header.SetFont(font)
        sizer.Add(header, 0, wx.ALL | wx.CENTER, 10)
        
        # Content
        content = self._build_content_text()
        self.text_ctrl = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(450, 250)
        )
        self.text_ctrl.SetName("Riepilogo ultima partita")
        sizer.Add(self.text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Close button
        btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        sizer.Add(btn_close, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build summary content."""
        lines = []
        
        # Date/time
        dt = datetime.fromisoformat(self.outcome.session_date)
        lines.append(f"Data: {dt.strftime('%d/%m/%Y alle %H:%M')}")
        lines.append("")
        
        # Outcome
        outcome_label = "VITTORIA" if self.outcome.is_victory else "SCONFITTA"
        lines.append(f"Esito: {outcome_label}")
        if not self.outcome.is_victory:
            reason = self.formatter.format_end_reason(self.outcome.end_reason)
            lines.append(f"Motivo: {reason}")
        lines.append("")
        
        # Stats
        lines.append(f"Tempo giocato: {self.formatter.format_duration(self.outcome.elapsed_time)}")
        lines.append(f"Mosse: {self.outcome.move_count}")
        
        if self.outcome.is_victory and self.outcome.scoring_enabled:
            lines.append(f"Punteggio: {self.formatter.format_number(self.outcome.final_score)} punti")
        lines.append("")
        
        # Config
        lines.append("[CONFIGURAZIONE]")
        lines.append(f"Difficoltà: Livello {self.outcome.difficulty_level}")
        
        deck_label = "1 mazzo" if self.outcome.deck_count == 1 else f"{self.outcome.deck_count} mazzi"
        lines.append(f"Mazzi: {deck_label}")
        
        if self.outcome.timer_enabled:
            timer_limit = self.formatter.format_time_mm_ss(self.outcome.timer_limit)
            lines.append(f"Timer: {timer_limit} ({self.outcome.timer_mode})")
        else:
            lines.append("Timer: Disabilitato")
        
        return "\n".join(lines)
    
    def _set_focus(self) -> None:
        """Set initial focus."""
        self.text_ctrl.SetFocus()
        
        # TTS announcement
        outcome_label = "Vittoria" if self.outcome.is_victory else "Sconfitta"
        elapsed = self.formatter.format_duration(self.outcome.elapsed_time)
        announcement = f"Ultima partita: {outcome_label}. Tempo: {elapsed}."
        self.SetTitle(announcement)
```

### 📝 File da Modificare: GameEngine

**File**: `src/application/game_engine.py` (MODIFIED)

**Modifiche**:

```python
# 1. Add import
from src.presentation.dialogs.last_game_dialog import LastGameDialog

# 2. Add attribute in __init__()
class GameEngine:
    def __init__(self, ...):
        # ... existing init ...
        self.last_session_outcome: Optional[SessionOutcome] = None

# 3. Store outcome in end_game()
    def end_game(self, end_reason: EndReason) -> None:
        # ... existing logic ...
        
        # Build SessionOutcome
        self.current_session_outcome = self._build_session_outcome(end_reason)
        
        # Store for "Ultima Partita" menu
        self.last_session_outcome = self.current_session_outcome  # ADD THIS LINE
        
        # Record in ProfileService
        if self.profile_service and self.profile_service.active_profile:
            self.profile_service.record_session(self.current_session_outcome)
        
        # ... show victory/abandon dialog ...

# 4. Add show_last_game_summary() method
    def show_last_game_summary(self) -> None:
        """Show last game summary (menu option 'U')."""
        if self.last_session_outcome is None:
            wx.MessageBox(
                "Nessuna partita recente disponibile.\n"
                "Gioca una partita per vedere il riepilogo.",
                "Ultima Partita",
                wx.OK | wx.ICON_INFORMATION
            )
            return
        
        dialog = LastGameDialog(self.parent, self.last_session_outcome)
        dialog.ShowModal()
        dialog.Destroy()
```

### 📝 File da Modificare: Main Menu

**File**: `acs_wx.py` (MODIFIED)

**Dove modificare**: Cerca metodo che costruisce/mostra main menu.

**Pattern atteso**:
```python
def show_main_menu(self):  # O nome simile
    menu_items = [
        "N - Nuova Partita",
        "O - Opzioni",
        "P - Gestione Profili",
        # ... altri items ...
        "E - Esci"
    ]
    
    # Display menu (wx.MessageBox o custom dialog)
    # Get user input
    # Handle selection
```

**Modifiche da fare**:

```python
# 1. Add menu item
def show_main_menu(self):
    menu_items = [
        "N - Nuova Partita",
        "U - Ultima Partita (risultati)",  # ADD THIS
        "O - Opzioni",
        "P - Gestione Profili",
        "L - Leaderboard Globale",  # PREPARAZIONE per 9.2
        "E - Esci"
    ]
    # ... rest of menu logic ...

# 2. Add handler in menu input processor
def _handle_menu_input(self, key):  # O nome simile
    if key == 'N' or key == 'n':
        self.game_engine.new_game()
    elif key == 'U' or key == 'u':  # ADD THIS
        self.game_engine.show_last_game_summary()
    elif key == 'O' or key == 'o':
        self.show_options()
    # ... rest of handlers ...
```

### ✅ Validation Commit 9.1

**Test manuali**:
1. Gioca una partita (vittoria o sconfitta)
2. Torna al menu principale
3. Premi "U"
4. Verifica: LastGameDialog appare con dati corretti
5. Verifica: ESC chiude dialog
6. Premi "U" prima di giocare: verifica messaggio "Nessuna partita recente"

**Commit message**:
```
feat(presentation): Add "Ultima Partita" menu option [Phase 9.1/9]

- Create LastGameDialog: read-only summary of last game
- GameEngine: store last_session_outcome after end_game()
- GameEngine: add show_last_game_summary() method
- Main menu: add "U - Ultima Partita" option
- Shows: date, outcome, time, moves, score, config
- Message box if no recent game available

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 9.1
```

---

## ✅ COMMIT 9.2: Leaderboard Menu Option (8-12 min)

### 🎯 Obiettivo

Aggiungere voce menu "L - Leaderboard Globale" e collegare a LeaderboardDialog (già creato in Phase 6).

### 📝 File da Modificare: Main Menu

**File**: `acs_wx.py` (MODIFIED)

**Modifiche**:

```python
# 1. Verifica che menu item "L" sia già presente (preparato in 9.1)
def show_main_menu(self):
    menu_items = [
        "N - Nuova Partita",
        "U - Ultima Partita",
        "O - Opzioni",
        "P - Gestione Profili",
        "L - Leaderboard Globale",  # QUESTA RIGA
        "E - Esci"
    ]
    # ... menu display logic ...

# 2. Add handler in menu input processor
def _handle_menu_input(self, key):  # O nome simile
    if key == 'N' or key == 'n':
        self.game_engine.new_game()
    elif key == 'U' or key == 'u':
        self.game_engine.show_last_game_summary()
    elif key == 'L' or key == 'l':  # ADD THIS HANDLER
        self._show_leaderboard()
    elif key == 'O' or key == 'o':
        self.show_options()
    # ... rest of handlers ...

# 3. Add _show_leaderboard() method
def _show_leaderboard(self):
    """Show global leaderboard dialog."""
    from src.presentation.dialogs.leaderboard_dialog import LeaderboardDialog
    
    # LeaderboardDialog needs ProfileService to load all profiles
    profile_service = self.game_engine.profile_service
    
    if profile_service is None:
        wx.MessageBox(
            "Servizio profili non disponibile.",
            "Errore",
            wx.OK | wx.ICON_ERROR
        )
        return
    
    dialog = LeaderboardDialog(self, profile_service)
    dialog.ShowModal()
    dialog.Destroy()
```

### ✅ Validation Commit 9.2

**Test manuali**:
1. Dal menu principale, premi "L"
2. Verifica: LeaderboardDialog appare
3. Verifica: Mostra 5 classifiche (winrate, vittorie, tempo, punteggio, streak)
4. Verifica: Profilo corrente evidenziato con "← TU"
5. Verifica: ESC chiude dialog e torna al menu

**Commit message**:
```
feat(presentation): Add leaderboard to main menu [Phase 9.2/9]

- Main menu: add "L - Leaderboard Globale" option
- Handler: _show_leaderboard() opens LeaderboardDialog (Phase 6)
- Uses ProfileService to load all profiles
- Shows 5 rankings: winrate, victories, fastest time, score, streak
- Returns to main menu on ESC

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 9.2
```

---

## ✅ COMMIT 9.3: Wire Detailed Stats to Profile Menu (10-15 min)

### 🎯 Obiettivo

Collegare l'opzione "5. Statistiche Dettagliate" del profile menu al DetailedStatsDialog (già creato in Phase 5).

### 📝 File da Modificare: Profile Menu

**File**: `acs_wx.py` (MODIFIED)

**Dove modificare**: Cerca metodo che gestisce profile management menu.

**Pattern atteso**:
```python
def show_profile_menu(self):  # O nome simile
    menu_items = [
        "1. Cambia Profilo",
        "2. Crea Nuovo Profilo",
        "3. Rinomina Profilo Corrente",
        "4. Elimina Profilo",
        "5. Statistiche Dettagliate",  # QUESTA OPZIONE GIÀ ESISTE
        "0. Torna al Menu Principale"
    ]
    
    # Get user choice
    # Handle choice
```

**Modifiche**:

```python
# Handler profile menu input
def _handle_profile_menu(self, choice: int):  # O nome simile
    if choice == 1:
        self._change_profile()
    elif choice == 2:
        self._create_profile()
    elif choice == 3:
        self._rename_profile()
    elif choice == 4:
        self._delete_profile()
    elif choice == 5:  # WIRE THIS OPTION
        self._show_detailed_stats()
    elif choice == 0:
        self.show_main_menu()

# Add _show_detailed_stats() method
def _show_detailed_stats(self):
    """Show detailed profile statistics (3 pages)."""
    from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
    
    profile_service = self.game_engine.profile_service
    
    if profile_service is None or profile_service.active_profile is None:
        wx.MessageBox(
            "Nessun profilo attivo.",
            "Errore",
            wx.OK | wx.ICON_ERROR
        )
        return
    
    # Build stats data
    stats_data = {
        'profile_name': profile_service.active_profile.profile_name,
        'global_stats': profile_service.global_stats,
        'timer_stats': profile_service.timer_stats,
        'difficulty_stats': profile_service.difficulty_stats,
        'scoring_stats': profile_service.scoring_stats
    }
    
    dialog = DetailedStatsDialog(self, stats_data)
    dialog.ShowModal()
    dialog.Destroy()
```

### ✅ Validation Commit 9.3

**Test manuali**:
1. Dal menu principale, vai a "P - Gestione Profili"
2. Premi "5" (Statistiche Dettagliate)
3. Verifica: DetailedStatsDialog appare con 3 pagine
4. Verifica: PageDown/PageUp cambiano pagina
5. Verifica: Pagina 1 mostra stats globali
6. Verifica: Pagina 2 mostra stats timer
7. Verifica: Pagina 3 mostra stats difficoltà/punteggio
8. Verifica: ESC chiude dialog e torna al profile menu

**Commit message**:
```
feat(presentation): Wire detailed stats to profile menu [Phase 9.3/9]

- Profile menu: wire option "5. Statistiche Dettagliate"
- Handler: _show_detailed_stats() opens DetailedStatsDialog (Phase 5)
- Loads stats from active profile (ProfileService)
- Shows 3 pages: global, timer, scoring/difficulty
- Page navigation: PageUp/PageDown
- Returns to profile menu on ESC

Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 9.3
```

---

## ✅ Phase 9 COMPLETA!

### 📊 Risultati Finali

**Commit totali**: 3  
**Tempo effettivo**: 33-49 minuti  
**File creati**: 1 (`last_game_dialog.py`)  
**File modificati**: 2 (`acs_wx.py`, `game_engine.py`)

**Funzionalità implementate**:
- ✅ Menu "U - Ultima Partita" funzionante
- ✅ Menu "L - Leaderboard Globale" funzionante
- ✅ Profile menu "5" collegato a DetailedStatsDialog
- ✅ Tutti i dialogs già creati (Phase 5-6) ora accessibili da menu

### 📝 Update TODO.md e Implementation Plan

Dopo commit 9.3, aggiornare:

```markdown
# In TODO.md
- [x] **Phase 9.1**: "Ultima Partita" menu option
- [x] **Phase 9.2**: Leaderboard menu option
- [x] **Phase 9.3**: Detailed stats in profile menu
- [x] **✅ Feature 3 COMPLETATA** (spunta questa checkbox)

# In IMPLEMENTATION_STATS_PRESENTATION.md
- [x] **Phase 9**: Menu integration (Ultima Partita, Leaderboard)
```

### 🧪 Testing Finale

Eseguire **manual NVDA checklist** completa (30+ items) per validare:
- Tutti i dialogs accessibili
- Focus management corretto
- TTS announcements appropriati
- Keyboard navigation funzionante
- Menu integration seamless

---

## 🚀 Pronto per Merge!

Dopo Phase 9 completa + testing NVDA:

1. **Update CHANGELOG.md** con v3.1.0 features
2. **Update README.md** se necessario (screenshot menu)
3. **Commit finale**: `chore: Complete v3.1.0 - Stats Presentation UI`
4. **Tag release**: `git tag v3.1.0`
5. **Merge** `copilot/implement-profile-system-v3-1-0` → `refactoring-engine`

**Feature Stack 100% completa!** 🎉
