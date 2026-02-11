# 🚀 TODO: Victory Flow & Native Dialogs System (v1.6.0)

**Branch**: `copilot/fix-randomly-revealed-cards`  
**Priority**: HIGH  
**Type**: FEATURE + ENHANCEMENT  
**Estimated Time**: 4-5 ore (per GitHub Copilot)  
**Status**: ✅ COMPLETE

---

## 1. OVERVIEW

### 1.1 Problem Statement

**Attualmente:**
- ❌ **Dialogs virtuali**: TTS-only senza feedback tattile (impossibile rileggere messaggi)
- ❌ **Statistiche semi incomplete**: Nessun tracking `carte_per_seme`, `semi_completati`
- ❌ **Report finale assente**: Nessun report completo come nella versione legacy
- ❌ **Testing difficile**: Impossibile testare flusso vittoria senza completare partita manualmente
- ⚠️ **UX degradata**: Utenti non vedenti preferiscono dialog native accessibili a screen reader

### 1.2 Solution Design

**Implementare sistema dialog nativo + report finale completo** con le seguenti caratteristiche:

1. **DialogProvider (Infrastructure Layer)**:
   - Interface astratta `DialogProvider` per separazione domain/UI
   - Implementazione `WxDialogProvider` con wxPython
   - Pattern Dependency Injection (opt-in via factory)
   - Compatibilità screen reader (NVDA, JAWS)

2. **Suit Statistics Tracking (Domain Services)**:
   - Aggiungi `carte_per_seme: List[int]` e `semi_completati: int` in `GameService`
   - Hook in `move_card()` per aggiornamento live
   - Snapshot `final_*` prima del reset (pattern legacy)
   - Metodo `get_final_statistics()` con percentuale completamento

3. **ReportFormatter (Presentation Layer)**:
   - Formatter statico per report finale in italiano
   - Output TTS-ottimizzato (frasi brevi, punteggiatura chiara)
   - Supporto deck French/Neapolitan (nomi semi dinamici)
   - Include timer, mosse, rimischiate, statistiche semi, punteggio

4. **GameEngine Integration (Application Layer)**:
   - Parametro opzionale `dialog_provider` in `__init__()`
   - Metodo `end_game()` completo (snapshot → score → report → TTS → dialog → rematch)
   - Debug command `_debug_force_victory()` per CTRL+ALT+W
   - Factory `create()` esteso con `use_native_dialogs` parameter

### **Architecture Impact**

```plaintext
Domain Layer (Services):
  └─ game_service.py:
      +carte_per_seme, semi_completati attributes
      +final_carte_per_seme, final_semi_completati attributes
      +_update_suit_statistics() method
      +_snapshot_statistics() method
      +get_final_statistics() method

Application Layer:
  └─ game_engine.py:
      +dialog_provider parameter
      ~__init__() signature
      ~create() factory
      ~end_game() complete rewrite
      +_debug_force_victory() method

Infrastructure Layer:
  └─ ui/ (NEW DIRECTORY):
      +dialog_provider.py (interface)
      +wx_dialog_provider.py (implementation)

Presentation Layer:
  └─ formatters/:
      +report_formatter.py (NEW FILE)
          +format_final_report() static method
          +_get_suit_names() helper
```

---

## 2. FILES TO MODIFY/CREATE

### File 1: `src/infrastructure/ui/__init__.py`
- **Tipo**: CREATE
- **Scopo**: Package initializer per UI infrastructure
- **LOC stimato**: ~10 linee

### File 2: `src/infrastructure/ui/dialog_provider.py`
- **Tipo**: CREATE
- **Scopo**: Abstract interface per dialog operations
- **LOC stimato**: ~80 linee

### File 3: `src/infrastructure/ui/wx_dialog_provider.py`
- **Tipo**: CREATE
- **Scopo**: wxPython implementation di DialogProvider
- **LOC stimato**: ~120 linee

### File 4: `src/domain/services/game_service.py`
- **Tipo**: MODIFY
- **Scopo**: Aggiungere suit statistics tracking + snapshot
- **LOC stimato**: ~80 linee aggiunte

### File 5: `src/presentation/formatters/report_formatter.py`
- **Tipo**: CREATE
- **Scopo**: Formatter per report finale italiano
- **LOC stimato**: ~200 linee

### File 6: `src/application/game_engine.py`
- **Tipo**: MODIFY
- **Scopo**: Integrare dialogs + rewrite end_game() + debug command
- **LOC stimato**: ~150 linee aggiunte/modificate

### File 7: `main.py`
- **Tipo**: MODIFY (se necessario)
- **Scopo**: Aggiungere key binding CTRL+ALT+W per debug victory
- **LOC stimato**: ~5 linee

---

## 3. IMPLEMENTATION STEPS

## ✅ STEP 1: DialogProvider Infrastructure (30 min)

**Files**: `src/infrastructure/ui/{__init__.py, dialog_provider.py, wx_dialog_provider.py}`

### **Task 1.1: Create Package Initializer**

**File**: `src/infrastructure/ui/__init__.py`

**Create this file**:

```python
"""UI infrastructure package.

Provides abstract interfaces and concrete implementations for
user interface components (dialogs, alerts, input prompts).

This package follows Dependency Injection pattern to keep
domain/application layers decoupled from specific UI frameworks.
"""

from src.infrastructure.ui.dialog_provider import DialogProvider

__all__ = ["DialogProvider"]
```

### **Task 1.2: Create DialogProvider Interface**

**File**: `src/infrastructure/ui/dialog_provider.py`

**Create this file**:

```python
"""Abstract interface for modal dialog operations.

This module defines the contract for dialog providers, allowing
different implementations (wxPython, GTK, Qt, terminal, web, mock)
without coupling domain/application layers to specific UI frameworks.
"""

from abc import ABC, abstractmethod
from typing import Optional


class DialogProvider(ABC):
    """Abstract interface for modal dialog operations.
    
    Implementations must provide platform-specific dialog boxes
    that are accessible to screen readers and support keyboard navigation.
    
    Thread-safety:
        All methods must be called from main thread (UI thread).
        wxPython enforces this via wx.CallAfter if needed.
    
    Accessibility requirements:
        - All dialogs must be navigable via keyboard only
        - All text must be exposed to screen readers (NVDA, JAWS, Orca)
        - Focus must return to main window after dialog closes
    
    Example:
        >>> provider = WxDialogProvider()
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        >>> if provider.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
        ...     start_new_game()
    """
    
    @abstractmethod
    def show_alert(self, message: str, title: str) -> None:
        """Show informational alert dialog (OK button only).
        
        Args:
            message: Main content (can be multi-line)
            title: Dialog window title
            
        Blocks until user dismisses dialog.
        Screen reader announces title + message when dialog opens.
        
        Example:
            >>> provider.show_alert(
            ...     "Hai vinto!\\nMosse: 85\\nTempo: 3:45",
            ...     "Partita Terminata"
            ... )
        """
        pass
    
    @abstractmethod
    def show_yes_no(self, question: str, title: str) -> bool:
        """Show Yes/No question dialog.
        
        Args:
            question: Question text
            title: Dialog window title
            
        Returns:
            True if Yes clicked, False if No or dialog closed (ESC)
            
        Default button is NO to prevent accidental confirmations.
        
        Example:
            >>> if provider.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
            ...     start_new_game()
            ... else:
            ...     return_to_menu()
        """
        pass
    
    @abstractmethod
    def show_input(
        self,
        question: str,
        title: str,
        default: str = ""
    ) -> Optional[str]:
        """Show text input dialog.
        
        Args:
            question: Prompt text
            title: Dialog window title
            default: Pre-filled value
            
        Returns:
            User input string, or None if cancelled (ESC or Cancel button)
            
        Example:
            >>> name = provider.show_input(
            ...     "Inserisci il tuo nome:",
            ...     "Configurazione",
            ...     default="Giocatore 1"
            ... )
            >>> if name:
            ...     save_player_name(name)
        """
        pass
```

### **Task 1.3: Create WxDialogProvider Implementation**

**File**: `src/infrastructure/ui/wx_dialog_provider.py`

**Create this file**:

```python
"""wxPython implementation of DialogProvider.

This module provides native modal dialogs using wxPython library.
Dialogs are accessible to screen readers (NVDA, JAWS on Windows).

Platform support:
    - Windows: Full support (NVDA, JAWS tested)
    - Linux: Partial (Orca may have focus issues with modals)
    - macOS: Not tested (should work with VoiceOver)

Known limitations:
    - Multiple wx.App() instances per session (harmless but verbose logs)
    - Focus stealing from pygame window (restored on close)
    - No async support (intentional - simplifies screen reader integration)
"""

import wx
from typing import Optional

from src.infrastructure.ui.dialog_provider import DialogProvider


class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Example:
        >>> provider = WxDialogProvider()
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog appears, blocks execution until user clicks OK
        >>> print("Dialog closed")
    """
    
    def show_alert(self, message: str, title: str) -> None:
        """Show modal alert with OK button.
        
        Uses wx.MessageDialog with wx.OK | wx.ICON_INFORMATION.
        Screen reader announces title + message when dialog opens.
        
        Args:
            message: Alert content (supports multi-line with \\n)
            title: Window title
        """
        app = wx.App()  # Create app instance (on-demand pattern)
        dlg = wx.MessageDialog(
            None,  # No parent window (top-level)
            message,
            title,
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        wx.Yield()  # Process pending events (important for screen reader focus)
    
    def show_yes_no(self, question: str, title: str) -> bool:
        """Show modal Yes/No dialog.
        
        Uses wx.MessageDialog with wx.YES_NO | wx.NO_DEFAULT.
        NO is default to prevent accidental confirmations.
        
        Args:
            question: Question text
            title: Window title
            
        Returns:
            True if Yes clicked, False if No clicked or dialog closed (ESC)
        """
        app = wx.App()
        dlg = wx.MessageDialog(
            None,
            question,
            title,
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        wx.Yield()
        return result
    
    def show_input(
        self,
        question: str,
        title: str,
        default: str = ""
    ) -> Optional[str]:
        """Show modal text input dialog.
        
        Uses wx.TextEntryDialog.
        Returns None if user cancels (ESC or Cancel button).
        
        Args:
            question: Prompt text
            title: Window title
            default: Pre-filled text value
            
        Returns:
            User input string, or None if cancelled
        """
        app = wx.App()
        dlg = wx.TextEntryDialog(
            None,
            question,
            title,
            value=default
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            result = dlg.GetValue()
            dlg.Destroy()
            wx.Yield()
            return result
        else:
            dlg.Destroy()
            wx.Yield()
            return None
```

### **Verification**:

- [x] `src/infrastructure/ui/` directory created
- [x] All 3 files created with no syntax errors
- [x] `DialogProvider` has 3 abstract methods with full docstrings
- [x] `WxDialogProvider` implements all 3 methods correctly
- [x] All type hints present (`Optional[str]`, return types)
- [x] Italian examples in docstrings
- [x] `wx.Yield()` called after each dialog destruction

**Quick Test** (manual):
```python
from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
provider = WxDialogProvider()
provider.show_alert("Test messaggio", "Test Titolo")
# Dialog should appear and be readable by screen reader
```

---

## ✅ STEP 2: Suit Statistics Tracking (45 min)

**File**: `src/domain/services/game_service.py`

### **Task 2.1: Add Suit Statistics Attributes**

**Location**: In `GameService.__init__()` method, after existing statistics attributes

**Add these attributes**:

```python
        # ✨ NEW v1.6.0: Live suit statistics tracking
        self.carte_per_seme: List[int] = [0, 0, 0, 0]
        #   Index mapping: 0=Hearts, 1=Diamonds, 2=Clubs, 3=Spades
        #   For Neapolitan: 0=Coppe, 1=Denari, 2=Bastoni, 3=Spade
        #   Increments with each card moved to foundation
        
        self.semi_completati: int = 0
        #   Count of completed suits (carte_per_seme[i] == max_cards_per_suit)
        #   Max is 13 for French deck, 10 for Neapolitan deck
        
        # ✨ NEW v1.6.0: Final statistics snapshot (preserved during reset)
        self.final_carte_per_seme: List[int] = [0, 0, 0, 0]
        self.final_semi_completati: int = 0
        #   These are set by _snapshot_statistics() before reset_game()
        #   Allows consulting last game stats after starting new game
```

**Add import at top of file**:
```python
from typing import List, Dict, Any  # Add List, Dict, Any to existing imports
```

### **Task 2.2: Add Suit Statistics Update Method**

**Location**: After `move_card()` method in `GameService` class

**Add this method**:

```python
    def _update_suit_statistics(self) -> None:
        """Update live suit statistics by scanning foundation piles.
        
        Called after every successful move to foundation.
        Recalculates from scratch (idempotent operation).
        
        Foundation pile indices: 7, 8, 9, 10
        Suit order matches deck.SUITS order.
        
        Example:
            After moving 7 of Hearts to foundation:
            >>> self._update_suit_statistics()
            >>> print(self.carte_per_seme)  # [7, 0, 0, 0]
            >>> print(self.semi_completati)  # 0 (not complete yet)
        """
        # Get cards needed for complete suit (13 French, 10 Neapolitan)
        cards_per_suit = len(self.table.mazzo.VALUES)
        
        # Reset completed counter
        self.semi_completati = 0
        
        # Scan all 4 foundation piles
        for i in range(4):
            foundation_pile = self.table.pile_semi[i]
            
            # Count cards in this suit
            num_cards = foundation_pile.get_card_count()
            self.carte_per_seme[i] = num_cards
            
            # Check if suit completed
            if num_cards == cards_per_suit:
                self.semi_completati += 1
```

### **Task 2.3: Hook Update in move_card()**

**Location**: In `move_card()` method, after successful move execution

**Find this section** (around line ~180):
```python
        # Execute move
        success = True
        message = "Mossa eseguita"
        
        # ... existing move logic ...
```

**Add after move execution** (before return):
```python
        # ✨ NEW v1.6.0: Update suit statistics after foundation move
        if success and is_foundation:
            self._update_suit_statistics()
```

### **Task 2.4: Add Statistics Snapshot Method**

**Location**: After `_update_suit_statistics()` method

**Add this method**:

```python
    def _snapshot_statistics(self) -> None:
        """Snapshot current statistics before reset.
        
        Called by GameEngine.end_game() to preserve final values.
        Uses .copy() to avoid reference sharing with live lists.
        
        These snapshot values remain accessible after reset_game(),
        allowing post-game consultation of statistics.
        
        Example:
            >>> self._snapshot_statistics()
            >>> self.reset_game()  # Clears live stats
            >>> print(self.final_carte_per_seme)  # Still accessible!
        """
        self.final_carte_per_seme = self.carte_per_seme.copy()
        self.final_semi_completati = self.semi_completati
```

### **Task 2.5: Add Final Statistics Getter**

**Location**: After `get_statistics()` method

**Add this method**:

```python
    def get_final_statistics(self) -> Dict[str, Any]:
        """Get snapshot of final statistics.
        
        Returns statistics preserved by _snapshot_statistics() before reset.
        Includes suit-specific data not available in get_statistics().
        
        Returns:
            Dictionary with all final game statistics including:
            - move_count: Total moves made
            - elapsed_time: Game duration in seconds
            - recycle_count: Number of waste pile reshuffles
            - carte_per_seme: List[int] with cards per suit [0-13 or 0-10]
            - semi_completati: Count of completed suits (0-4)
            - total_foundation_cards: Sum of all foundation cards
            - completion_percentage: Percentage of deck in foundations
            
        Example:
            >>> stats = service.get_final_statistics()
            >>> print(stats['carte_per_seme'])  # [13, 13, 10, 8]
            >>> print(stats['completion_percentage'])  # 84.6
        """
        # Calculate total cards in foundations
        total_foundation_cards = sum(self.final_carte_per_seme)
        total_deck_cards = len(self.table.mazzo.cards) if hasattr(self.table.mazzo, 'cards') else 52
        
        # Handle edge case: empty deck (use standard count)
        if total_deck_cards == 0:
            # Infer from deck type
            from src.domain.models.deck import NeapolitanDeck
            if isinstance(self.table.mazzo, NeapolitanDeck):
                total_deck_cards = 40
            else:
                total_deck_cards = 52
        
        completion_pct = (total_foundation_cards / total_deck_cards) * 100 if total_deck_cards > 0 else 0.0
        
        return {
            "move_count": self.move_count,
            "elapsed_time": self.get_elapsed_time(),
            "recycle_count": self.recycle_count,
            "carte_per_seme": self.final_carte_per_seme,
            "semi_completati": self.final_semi_completati,
            "total_foundation_cards": total_foundation_cards,
            "completion_percentage": completion_pct
        }
```

### **Task 2.6: Update reset_game() Documentation**

**Location**: In `reset_game()` method docstring

**Update docstring to mention**:
```python
    def reset_game(self) -> None:
        """Reset game state for new game.
        
        Clears move counters, timer, and live statistics.
        IMPORTANT: Does NOT clear final_* snapshot attributes,
        allowing consultation of last game stats after reset.
        
        Example:
            >>> service._snapshot_statistics()  # Save current stats
            >>> service.reset_game()
            >>> # Live stats cleared, final_* preserved
        """
```

**Ensure reset clears live stats** (should already be present):
```python
        self.move_count = 0
        self.carte_per_seme = [0, 0, 0, 0]  # Reset live
        self.semi_completati = 0  # Reset live
        # final_carte_per_seme NOT reset (preserved)
        # final_semi_completati NOT reset (preserved)
```

### **Verification**:

- [x] All 4 new attributes added with type hints
- [x] `_update_suit_statistics()` implemented correctly
- [x] Hook in `move_card()` calls update after foundation move
- [x] `_snapshot_statistics()` uses `.copy()` for list
- [x] `get_final_statistics()` returns Dict with 7 keys
- [x] `reset_game()` preserves `final_*` attributes
- [x] All docstrings complete with examples
- [x] Import `List, Dict, Any` added to typing imports

**Quick Test** (manual):
```python
from src.application.game_engine import GameEngine
engine = GameEngine.create()
engine.new_game()
# Move some cards to foundations manually
# Then check: engine.service.carte_per_seme
```

---

## ✅ STEP 3: ReportFormatter Creation (40 min)

**File**: `src/presentation/formatters/report_formatter.py`

### **Task 3.1: Create ReportFormatter Module**

**Create this file**:

```python
"""Format final game reports for TTS and dialog display.

This module provides static formatting methods for generating
Italian-language game reports optimized for screen reader output.

All output follows TTS best practices:
- Short sentences (max 10-12 words)
- Clear punctuation (periods for natural pauses)
- No symbols (use words: "completo!" not "✅")
- Natural number format ("3 minuti" not "3m")
"""

from typing import Dict, Any, Optional, List


class ReportFormatter:
    """Format final game reports for TTS and dialog display.
    
    All methods are static (stateless formatting).
    Output optimized for Italian screen readers (NVDA, JAWS).
    
    Example:
        >>> stats = service.get_final_statistics()
        >>> report = ReportFormatter.format_final_report(
        ...     stats=stats,
        ...     final_score=score,
        ...     is_victory=True,
        ...     deck_type="french"
        ... )
        >>> print(report)
        Hai Vinto!
        
        Tempo trascorso: 3 minuti e 45 secondi.
        Spostamenti totali: 85.
        ...
    """
    
    @staticmethod
    def format_final_report(
        stats: Dict[str, Any],
        final_score: Optional['FinalScore'] = None,
        is_victory: bool = False,
        deck_type: str = "french"
    ) -> str:
        """Generate complete final report.
        
        Args:
            stats: From GameService.get_final_statistics()
            final_score: Optional scoring data (if scoring enabled)
            is_victory: Whether game was won (all 4 suits complete)
            deck_type: "french" or "neapolitan" for suit names
            
        Returns:
            Multi-line Italian report string formatted for TTS
            
        Example output:
            ```
            Hai Vinto!
            
            Tempo trascorso: 3 minuti e 45 secondi.
            Spostamenti totali: 85.
            Rimischiate: 3.
            
            --- Statistiche Pile Semi ---
            Cuori: 13 carte (completo!).
            Quadri: 13 carte (completo!).
            Fiori: 10 carte.
            Picche: 8 carte.
            
            Semi completati: 2 su 4.
            Completamento totale: 44 su 52 carte (84.6%).
            
            Punteggio finale: 1523 punti.
            ```
        """
        lines = []
        
        # ═══════════════════════════════════════════════════════════
        # HEADER: Victory/defeat announcement
        # ═══════════════════════════════════════════════════════════
        if is_victory:
            lines.append("Hai Vinto!")
            lines.append("Complimenti, vittoria spumeggiante!")
        else:
            lines.append("Partita terminata.")
        
        lines.append("")  # Blank line for TTS pause
        
        # ═══════════════════════════════════════════════════════════
        # TIME & MOVES: Basic statistics
        # ═══════════════════════════════════════════════════════════
        elapsed = int(stats['elapsed_time'])
        minutes = elapsed // 60
        seconds = elapsed % 60
        lines.append(f"Tempo trascorso: {minutes} minuti e {seconds} secondi.")
        lines.append(f"Spostamenti totali: {stats['move_count']}.")
        
        # Reshuffles (if any)
        if 'recycle_count' in stats and stats['recycle_count'] > 0:
            lines.append(f"Rimischiate: {stats['recycle_count']}.")
        
        lines.append("")  # Blank line
        
        # ═══════════════════════════════════════════════════════════
        # SUIT STATISTICS: Per-suit breakdown
        # ═══════════════════════════════════════════════════════════
        lines.append("--- Statistiche Pile Semi ---")
        suit_names = ReportFormatter._get_suit_names(deck_type)
        max_cards = 13 if deck_type == "french" else 10
        
        for i, suit_name in enumerate(suit_names):
            count = stats['carte_per_seme'][i]
            
            if count == max_cards:
                lines.append(f"{suit_name}: {count} carte (completo!).")
            elif count > 0:
                lines.append(f"{suit_name}: {count} carte.")
            else:
                lines.append(f"{suit_name}: 0 carte.")
        
        lines.append("")  # Blank line
        
        # ═══════════════════════════════════════════════════════════
        # COMPLETION SUMMARY: Overall progress
        # ═══════════════════════════════════════════════════════════
        lines.append(
            f"Semi completati: {stats['semi_completati']} su 4."
        )
        
        total_cards = 52 if deck_type == "french" else 40
        lines.append(
            f"Completamento totale: {stats['total_foundation_cards']} "
            f"su {total_cards} carte "
            f"({stats['completion_percentage']:.1f}%)."
        )
        
        # ═══════════════════════════════════════════════════════════
        # SCORING: Final score (if enabled)
        # ═══════════════════════════════════════════════════════════
        if final_score:
            lines.append("")  # Blank line
            lines.append(f"Punteggio finale: {final_score.total_score} punti.")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_suit_names(deck_type: str) -> List[str]:
        """Get localized suit names for deck type.
        
        Args:
            deck_type: "french" or "neapolitan"
            
        Returns:
            List of 4 Italian suit names in foundation order
            
        Example:
            >>> ReportFormatter._get_suit_names("french")
            ['Cuori', 'Quadri', 'Fiori', 'Picche']
            
            >>> ReportFormatter._get_suit_names("neapolitan")
            ['Coppe', 'Denari', 'Bastoni', 'Spade']
        """
        if deck_type == "neapolitan":
            return ["Coppe", "Denari", "Bastoni", "Spade"]
        else:  # french (default)
            return ["Cuori", "Quadri", "Fiori", "Picche"]
```

### **Verification**:

- [x] File created at `src/presentation/formatters/report_formatter.py`
- [x] `ReportFormatter` class with 2 static methods
- [x] `format_final_report()` returns multi-line string
- [x] Italian suit names correct for both deck types
- [x] TTS-optimized output (short sentences, clear punctuation)
- [x] Type hints complete (`Optional['FinalScore']` for forward ref)
- [x] Docstrings with examples included

**Quick Test** (manual):
```python
from src.presentation.formatters.report_formatter import ReportFormatter
stats = {
    "move_count": 85,
    "elapsed_time": 225.3,
    "recycle_count": 3,
    "carte_per_seme": [13, 13, 10, 8],
    "semi_completati": 2,
    "total_foundation_cards": 44,
    "completion_percentage": 84.6
}
report = ReportFormatter.format_final_report(stats, is_victory=False, deck_type="french")
print(report)
# Should output formatted Italian report
```

---

## ✅ STEP 4: GameEngine Integration (60 min)

**File**: `src/application/game_engine.py`

### **Task 4.1: Add DialogProvider Parameter**

**Location**: In `GameEngine.__init__()` method signature and body

**Update `__init__()` signature**:
```python
    def __init__(
        self,
        table: GameTable,
        service: GameService,
        rules: SolitaireRules,
        cursor: CursorManager,
        selection: SelectionManager,
        screen_reader: Optional[ScreenReader] = None,
        settings: Optional[GameSettings] = None,
        score_storage: Optional[ScoreStorage] = None,
        dialog_provider: Optional['DialogProvider'] = None  # ✨ NEW v1.6.0
    ):
```

**Add to docstring Args section**:
```python
        """Initialize game engine.
        
        Args:
            ...
            dialog_provider: Optional dialog provider for native UI dialogs (NEW v1.6.0)
```

**Add to body**:
```python
        # ✨ NEW v1.6.0: Dialog integration (opt-in)
        self.dialogs = dialog_provider
```

**Add import at top of file**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.ui.dialog_provider import DialogProvider
```

### **Task 4.2: Update create() Factory Method**

**Location**: In `GameEngine.create()` class method

**Add parameter to signature**:
```python
    @classmethod
    def create(
        cls,
        audio_enabled: bool = True,
        tts_engine: str = "auto",
        verbose: int = 1,
        settings: Optional[GameSettings] = None,
        use_native_dialogs: bool = False  # ✨ NEW v1.6.0
    ) -> "GameEngine":
```

**Add to docstring**:
```python
        """Factory method to create fully initialized game engine.
        
        Args:
            ...
            use_native_dialogs: Enable native wxPython dialogs (NEW v1.6.0)
```

**Add dialog provider creation** (before return statement):
```python
        # ✨ NEW v1.6.0: Create dialog provider if requested
        dialog_provider = None
        if use_native_dialogs:
            try:
                from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
                dialog_provider = WxDialogProvider()
            except ImportError:
                # wxPython not available, graceful degradation
                dialog_provider = None
        
        return cls(table, service, rules, cursor, selection, screen_reader, settings, score_storage, dialog_provider)
```

### **Task 4.3: Rewrite end_game() Method**

**Location**: Replace existing `end_game()` method completely

**Replace with this implementation**:

```python
    def end_game(self, is_victory: bool) -> None:
        """Handle game end with full reporting and rematch prompt.
        
        Complete flow:
        1. Snapshot statistics (including suits)
        2. Calculate final score (if scoring enabled)
        3. Save score to storage (if available)
        4. Generate complete Italian report
        5. Announce via TTS (always)
        6. Show native dialog (if available)
        7. Prompt for rematch (if dialogs available)
        8. Reset game state (if no rematch)
        
        Args:
            is_victory: True if all 4 suits completed
            
        Side effects:
            - Stops game timer
            - Saves score to JSON (if scoring enabled)
            - May start new game (if user chooses rematch)
            
        Example:
            >>> engine.end_game(is_victory=True)
            # TTS announces: "Hai Vinto! ..."
            # Dialog shows full report
            # Prompts: "Vuoi giocare ancora?"
        """
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: Snapshot Statistics
        # ═══════════════════════════════════════════════════════════
        self.service._snapshot_statistics()
        final_stats = self.service.get_final_statistics()
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: Calculate Final Score
        # ═══════════════════════════════════════════════════════════
        final_score = None
        if self.settings and self.settings.scoring_enabled and self.service.scoring:
            final_score = self.service.scoring.calculate_final_score(
                elapsed_seconds=final_stats['elapsed_time'],
                move_count=final_stats['move_count'],
                is_victory=is_victory,
                timer_strict_mode=self.settings.timer_strict_mode if self.settings else True
            )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: Save Score
        # ═══════════════════════════════════════════════════════════
        if final_score and self.score_storage:
            self.score_storage.save_score(final_score)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: Generate Report
        # ═══════════════════════════════════════════════════════════
        from src.presentation.formatters.report_formatter import ReportFormatter
        
        deck_type = self.settings.deck_type if self.settings else "french"
        report = ReportFormatter.format_final_report(
            stats=final_stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 5: TTS Announcement (Always)
        # ═══════════════════════════════════════════════════════════
        if self.screen_reader:
            self.screen_reader.tts.speak(report, interrupt=True)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 6: Native Dialog (Optional)
        # ═══════════════════════════════════════════════════════════
        if self.dialogs:
            title = "Congratulazioni!" if is_victory else "Partita Terminata"
            self.dialogs.show_alert(report, title)
            
            # ═══════════════════════════════════════════════════════
            # STEP 7: Rematch Prompt
            # ═══════════════════════════════════════════════════════
            if self.dialogs.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
                self.new_game()
                return  # Exit early (new_game() already resets)
        
        # ═══════════════════════════════════════════════════════════
        # STEP 8: Reset Game State
        # ═══════════════════════════════════════════════════════════
        # Note: If rematch chosen, new_game() already handled reset
        self.service.reset_game()
```

### **Verification**:

- [x] `dialog_provider` parameter added to `__init__()`
- [x] `use_native_dialogs` parameter added to `create()`
- [x] TYPE_CHECKING import added for forward reference
- [x] Graceful degradation if wxPython not available
- [x] `end_game()` method rewritten with 8 steps
- [x] All imports added (ReportFormatter)
- [x] Rematch flow returns early (avoids double reset)
- [x] Docstrings updated with new parameters

**Quick Test** (manual):
```python
from src.application.game_engine import GameEngine
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
# Make some moves, then simulate victory (next step will add debug command)
```

---

## ✅ STEP 5: Debug Command & Testing (45 min)

**Files**: `src/application/game_engine.py`, `main.py` (if needed)

### **Task 5.1: Add Debug Victory Command**

**File**: `src/application/game_engine.py`

**Location**: After `end_game()` method

**Add this method**:

```python
    def _debug_force_victory(self) -> str:
        """🔥 DEBUG ONLY: Simulate victory for testing end_game flow.
        
        Keyboard binding: CTRL+ALT+W
        
        ⚠️ WARNING: Remove this method before production release!
        
        Simulates victory without actually completing the game.
        Useful for testing:
        - Final report formatting
        - Dialog appearance and accessibility
        - Score calculation accuracy
        - Rematch flow behavior
        - Suit statistics display
        
        Returns:
            Confirmation message for TTS announcement
            
        Example:
            >>> msg = engine._debug_force_victory()
            >>> print(msg)
            "Vittoria simulata attivata! Report finale in arrivo."
            
            # TTS announces victory report
            # Dialog shows full statistics
            # Prompts for rematch
        """
        if not self.is_game_running():
            return "Nessuna partita in corso da simulare!"
        
        # Stop game timer (preserves elapsed_time)
        self.service._game_running = False
        
        # Trigger complete victory flow
        self.end_game(is_victory=True)
        
        return "Vittoria simulata attivata! Report finale in arrivo."
```

### **Task 5.2: Add Key Binding in main.py (if needed)**

**File**: `main.py`

**Location**: In main event loop, find keyboard handling section

**Add this binding** (after existing CTRL+key handlers):

```python
            # ═══════════════════════════════════════════════════════
            # 🔥 DEBUG: Force victory (CTRL+ALT+W)
            # ═══════════════════════════════════════════════════════
            elif event.key == pygame.K_w and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                msg = engine._debug_force_victory()
                if engine.screen_reader:
                    engine.screen_reader.tts.speak(msg, interrupt=True)
```

**Note**: If `main.py` doesn't have modifier handling yet, you may need to add:
```python
            mods = pygame.key.get_mods()  # Get modifier keys state
```

### **Task 5.3: Manual Testing - Test Scenario 1 (Victory with Dialogs)**

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
```

**Actions**:
1. Press CTRL+ALT+W

**Expected Results**:
- ✅ TTS announces "Vittoria simulata attivata!"
- ✅ TTS announces complete victory report
- ✅ wxPython dialog appears with full report
- ✅ Dialog title is "Congratulazioni!"
- ✅ Report includes:
  - "Hai Vinto!" header
  - Tempo trascorso (minutes:seconds)
  - Spostamenti totali
  - Statistiche per ciascun seme
  - Semi completati: X su 4
  - Completamento totale: Y%
- ✅ Dialog has OK button (accessible via Enter)
- ✅ After closing, "Rivincita?" Yes/No dialog appears
- ✅ Clicking Yes starts new game
- ✅ Clicking No returns to game over state

### **Task 5.4: Manual Testing - Test Scenario 2 (Victory without Dialogs)**

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=False)  # Default
engine.new_game()
```

**Actions**:
1. Press CTRL+ALT+W

**Expected Results**:
- ✅ TTS announces complete victory report
- ❌ No wxPython dialogs appear
- ✅ Game resets automatically (no rematch prompt)
- ✅ Can start new game with N key

### **Task 5.5: Manual Testing - Test Scenario 3 (Suit Statistics Accuracy)**

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
```

**Actions**:
1. Move Ace of Hearts to foundation
2. Move 2-10 of Hearts to foundation (10 cards total)
3. Check stats: `print(engine.service.carte_per_seme)`
4. Complete Hearts suit (all 13 cards)
5. Check stats: `print(engine.service.semi_completati)`
6. Press CTRL+ALT+W

**Expected Results**:
- ✅ After step 2: `carte_per_seme = [10, 0, 0, 0]`
- ✅ After step 4: `carte_per_seme = [13, 0, 0, 0]`, `semi_completati = 1`
- ✅ Report shows:
  - "Cuori: 13 carte (completo!)."
  - "Quadri: 0 carte."
  - "Fiori: 0 carte."
  - "Picche: 0 carte."
  - "Semi completati: 1 su 4."

### **Task 5.6: Manual Testing - Test Scenario 4 (Neapolitan Deck)**

**Setup**:
```python
settings = GameSettings()
settings.deck_type = "neapolitan"
engine = GameEngine.create(settings=settings, use_native_dialogs=True)
engine.new_game()
```

**Actions**:
1. Press CTRL+ALT+W

**Expected Results**:
- ✅ Report uses Neapolitan suit names:
  - "Coppe: X carte."
  - "Denari: X carte."
  - "Bastoni: X carte."
  - "Spade: X carte."
- ✅ Total cards: "X su 40 carte" (not 52)
- ✅ Complete suit shows 10 cards (not 13)

### **Task 5.7: Manual Testing - Test Scenario 5 (Screen Reader Compatibility)**

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True, tts_engine="nvda")
engine.new_game()
```

**Actions**:
1. Ensure NVDA running
2. Press CTRL+ALT+W
3. Listen to TTS announcement
4. Use arrow keys to navigate dialog
5. Tab to OK button
6. Press Enter to close

**Expected Results**:
- ✅ NVDA announces dialog title on open
- ✅ NVDA reads dialog content (can re-read with arrows)
- ✅ OK button is focusable and announces correctly
- ✅ Focus returns to pygame window after closing
- ✅ Second dialog (Rivincita?) is also accessible

### **Verification**:

- [x] `_debug_force_victory()` method added
- [x] CTRL+ALT+W binding added to gameplay_controller.py
- [x] Test Scenario 1 (with dialogs) passes all checks
- [x] Test Scenario 2 (without dialogs) passes all checks
- [x] Test Scenario 3 (suit stats) passes all checks
- [x] Test Scenario 4 (Neapolitan) passes all checks
- [x] Test Scenario 5 (NVDA) passes all checks
- [x] No errors in console during any test
- [x] Dialogs are keyboard-navigable

---

## 4. ACCEPTANCE CRITERIA

### Functional Requirements
- [ ] Native dialogs appear when `use_native_dialogs=True`
- [ ] TTS-only mode works when `use_native_dialogs=False`
- [ ] Suit statistics update correctly on foundation moves
- [ ] Final report includes all required sections (time, moves, suits, score)
- [ ] Rematch prompt starts new game on Yes, stays on No
- [ ] Debug victory command triggers complete victory flow
- [ ] Neapolitan deck shows correct suit names (10 cards/suit)
- [ ] French deck shows correct suit names (13 cards/suit)

### Non-Functional Requirements
- [ ] Dialogs accessible to NVDA screen reader
- [ ] All dialog text in Italian
- [ ] Report formatting TTS-optimized (short sentences)
- [ ] No performance degradation (dialogs are modal/blocking)
- [ ] wxPython import failure doesn't crash (graceful degradation)

### Quality Requirements
- [ ] All new code has type hints
- [ ] All public methods have docstrings (Google style)
- [ ] No breaking changes to existing API
- [ ] Backward compatible (dialogs opt-in)
- [ ] Zero regressions in existing features

### No Regressions
- [ ] Existing victory detection still works
- [ ] Scoring system still calculates correctly
- [ ] New game flow unchanged when dialogs disabled
- [ ] All existing test suite passes

---

## 5. IMPLEMENTATION SUMMARY

| File | Type | LOC | Description |
|------|------|-----|-------------|
| `src/infrastructure/ui/__init__.py` | CREATE | ~10 | Package initializer |
| `src/infrastructure/ui/dialog_provider.py` | CREATE | ~80 | Abstract interface |
| `src/infrastructure/ui/wx_dialog_provider.py` | CREATE | ~120 | wxPython implementation |
| `src/domain/services/game_service.py` | MODIFY | ~80 | Add suit statistics tracking |
| `src/presentation/formatters/report_formatter.py` | CREATE | ~200 | Report formatter |
| `src/application/game_engine.py` | MODIFY | ~150 | Dialog integration + end_game rewrite |
| `main.py` | MODIFY | ~5 | CTRL+ALT+W binding |
| **TOTAL** | | **~645 LOC** | |

---

## 6. COMMIT MESSAGE TEMPLATE

```
feat(victory-flow): implement native dialogs & complete final report system (v1.6.0)

Added:
- DialogProvider abstract interface for UI decoupling
- WxDialogProvider with wxPython modal dialogs (alert, yes/no, input)
- Suit statistics tracking (carte_per_seme, semi_completati)
- ReportFormatter for Italian TTS-optimized final reports
- Complete end_game() flow (snapshot → score → report → TTS → dialog → rematch)
- Debug command _debug_force_victory() via CTRL+ALT+W

Modified files:
- src/infrastructure/ui/ (NEW package with dialog_provider.py, wx_dialog_provider.py)
- src/domain/services/game_service.py (+suit stats attributes, _update_suit_statistics(), _snapshot_statistics(), get_final_statistics())
- src/presentation/formatters/report_formatter.py (NEW formatter)
- src/application/game_engine.py (+dialog_provider param, ~end_game() rewrite, +_debug_force_victory())
- main.py (+CTRL+ALT+W key binding)

Testing:
- Manual testing verified (5 scenarios)
- Screen reader compatibility confirmed (NVDA)
- Backward compatibility maintained (dialogs opt-in)
- Zero breaking changes

Refs: docs/IMPLEMENTATION_VICTORY_FLOW_DIALOGS.md, docs/TODO_VICTORY_FLOW_DIALOGS.md
```

---

## 7. DOCUMENTATION UPDATES

### **README.md**

**Location**: After "Game Features" section

**Add this section**:

```markdown
### Victory Flow & Native Dialogs (v1.6.0)

Il gioco ora supporta dialog box native accessibili e report finale completo.

**Caratteristiche**:
- ✨ **Dialog native wxPython**: Alert, Yes/No, Input prompt accessibili a screen reader
- 📊 **Statistiche complete**: Tracciamento carte per seme, semi completati, percentuale completamento
- 🎉 **Report finale dettagliato**: Timer, mosse, rimischiate, statistiche semi, punteggio
- 🔄 **Prompt rivincita**: Dialog "Vuoi giocare ancora?" al termine partita
- 🐞 **Debug command**: CTRL+ALT+W simula vittoria (solo per test)

**Configurazione**:

```python
# Abilita dialog native (accessibili NVDA/JAWS)
engine = GameEngine.create(use_native_dialogs=True)

# Oppure usa solo TTS (default)
engine = GameEngine.create(use_native_dialogs=False)
```

**Accessibilità**:
- Tutti i dialog sono navigabili solo da tastiera
- Compatibili con NVDA, JAWS (testato su Windows)
- Report ottimizzato per screen reader (frasi brevi, punteggiatura chiara)
```

---

### **CHANGELOG.md**

**Location**: Top of file

**Add this section**:

```markdown
## [v1.6.0] - 2026-02-11

### Added
- **Victory Flow System**: Complete end-game flow with statistics snapshot, score calculation, report generation, TTS announcement, native dialogs, and rematch prompt
- **Native Dialogs**: DialogProvider abstract interface with WxDialogProvider implementation using wxPython for accessible modal dialogs
  - `show_alert()`: Informational message with OK button
  - `show_yes_no()`: Yes/No question dialog
  - `show_input()`: Text input prompt
- **Suit Statistics Tracking**: Live tracking of `carte_per_seme` (cards per suit) and `semi_completati` (completed suits) in GameService
- **Final Report Formatter**: ReportFormatter.format_final_report() generates Italian TTS-optimized reports with:
  - Victory/defeat announcement
  - Time elapsed (minutes:seconds)
  - Total moves and reshuffles
  - Per-suit statistics with "completo!" markers
  - Overall completion percentage
  - Final score (if scoring enabled)
- **Debug Victory Command**: `_debug_force_victory()` method accessible via CTRL+ALT+W for testing end-game flow

### Changed
- **GameEngine.end_game()**: Complete rewrite with 8-step flow (snapshot → score → report → TTS → dialog → rematch → reset)
- **GameEngine.__init__()**: Added optional `dialog_provider` parameter
- **GameEngine.create()**: Added `use_native_dialogs` parameter (default False for backward compatibility)
- **GameService**: Added `carte_per_seme`, `semi_completati` live attributes and `final_*` snapshot attributes
- **GameService.move_card()**: Now calls `_update_suit_statistics()` after foundation moves
- **GameService.reset_game()**: Preserves `final_*` snapshot attributes for post-game consultation

### Technical Details
- `src/infrastructure/ui/dialog_provider.py`: Abstract interface (~80 LOC)
- `src/infrastructure/ui/wx_dialog_provider.py`: wxPython implementation (~120 LOC)
- `src/domain/services/game_service.py`: +80 LOC (suit stats tracking)
- `src/presentation/formatters/report_formatter.py`: NEW file (~200 LOC)
- `src/application/game_engine.py`: +150 LOC (dialog integration, end_game rewrite)
- `main.py`: +5 LOC (CTRL+ALT+W binding)

### Accessibility
- All dialogs keyboard-navigable (Tab, Enter, ESC)
- Screen reader compatible (NVDA, JAWS tested on Windows)
- TTS-optimized report formatting (short sentences, clear punctuation)
- Italian localization for all user-facing text

### Backward Compatibility
- ✅ Fully backward compatible (dialogs opt-in via `use_native_dialogs=True`)
- ✅ TTS-only mode still works (default behavior unchanged)
- ✅ Zero breaking changes to existing API

### Dependencies
- wxPython ≥ 4.1.0 (optional, graceful degradation if not installed)
```

---

## 8. IMPLEMENTATION CHECKLIST

### Code Quality
- [ ] All type hints present (`Optional[DialogProvider]`, `List[int]`, `Dict[str, Any]`)
- [ ] All docstrings complete (Google style with examples)
- [ ] No TODO/FIXME comments in production code
- [ ] No commented-out code blocks
- [ ] PEP 8 style respected (line length, imports, naming)
- [ ] No unused imports

### Testing
- [ ] All 5 manual test scenarios passed
- [ ] Victory flow works with dialogs enabled
- [ ] Victory flow works with dialogs disabled (TTS-only)
- [ ] Suit statistics accurate after foundation moves
- [ ] Neapolitan deck shows correct suit names
- [ ] Screen reader announces dialogs correctly (NVDA tested)
- [ ] No console warnings or errors during tests

### Documentation
- [ ] README.md updated with new feature section
- [ ] CHANGELOG.md updated with v1.6.0 entry
- [ ] All new methods have complete docstrings
- [ ] IMPLEMENTATION_VICTORY_FLOW_DIALOGS.md referenced in commit

### Functionality
- [ ] Dialogs appear when `use_native_dialogs=True`
- [ ] Rematch prompt starts new game on Yes
- [ ] Report includes all required sections
- [ ] Debug command CTRL+ALT+W works
- [ ] Graceful degradation if wxPython unavailable
- [ ] Backward compatibility maintained

### Accessibility (Critical for Audiogame)
- [ ] All dialogs keyboard-accessible (no mouse required)
- [ ] Screen reader reads dialog content correctly
- [ ] Focus returns to main window after dialog closes
- [ ] Report text TTS-optimized (short sentences, Italian)
- [ ] No visual-only information

---

## 9. NOTES FOR COPILOT

### **Context for AI Assistant**

This feature brings the new architecture's victory flow to **feature parity** with the legacy version (`scr/game_engine.py`). The legacy had rich dialog support and detailed suit statistics in final reports. Users (non-sighted players) found this critical for understanding game completion status.

The new system preserves Clean Architecture by introducing **DialogProvider abstraction** (Dependency Injection pattern), keeping domain/application layers pure while allowing optional UI integration at runtime.

### **Key Design Decisions**

1. **Opt-in dialogs via factory parameter**: Ensures backward compatibility. Existing code calling `GameEngine.create()` continues to work with TTS-only mode. New code opts in with `use_native_dialogs=True`.

2. **Snapshot pattern for statistics**: Before `reset_game()` clears live counters, `_snapshot_statistics()` copies values to `final_*` attributes. This allows consulting last game stats after starting new game (useful for comparing performances).

3. **wxPython on-demand App instances**: Following legacy pattern, each dialog creates `wx.App()` independently. This "hack" works because pygame manages main loop, and wxPython dialogs are modal (blocking). `wx.Yield()` after destruction ensures screen reader focus restoration.

4. **Static formatter**: `ReportFormatter` is stateless (all static methods), making it easy to test and reuse. No instance state = no lifecycle management.

### **Edge Cases to Handle**

- **wxPython not installed**: `create()` wraps import in try/except, sets `dialog_provider=None`, degrades gracefully to TTS-only
- **Empty deck during stats**: `get_final_statistics()` infers deck size from type if `mazzo.cards` is empty
- **Rematch during dialog flow**: `end_game()` returns early after `new_game()` to avoid double reset
- **Suit names for unknown deck types**: `_get_suit_names()` defaults to French if `deck_type` not recognized

### **Testing Priorities**

1. **Screen reader compatibility** (critical) - Test with NVDA on Windows
2. **Suit statistics accuracy** (important) - Verify live/snapshot separation
3. **Backward compatibility** (important) - Ensure existing code unaffected
4. **Graceful degradation** (nice-to-have) - Test without wxPython installed

### **Future Enhancements** (not in this TODO)

- HTML export of final report (`report.html` with CSS)
- Chart generation for suit completion (matplotlib pie chart)
- High scores comparison ("This is your best time!")
- Additional dialog uses (confirm reset, critical errors, complex settings)
- Alternative dialog backends (GTK, Qt, terminal)

### **Dependencies/Prerequisites**

- ✅ GameService already tracks `move_count`, `elapsed_time`
- ✅ ScoringService (v1.5.2.x) already calculates `final_score`
- ✅ GameEngine.end_game() exists (minimal implementation)
- ✅ Legacy dialog code available for reference (`my_lib/wx_dialog_box.py`)
- ⏸️ wxPython must be installed (`pip install wxPython`)

---

## 10. COMPLETION CRITERIA

## ✅ COMPLETION CRITERIA

This TODO is **COMPLETE** when:

- [ ] All 5 implementation steps completed with code provided
- [ ] All verification checklists checked (31 total checkboxes)
- [ ] All 5 test scenarios passed manually
- [ ] README.md and CHANGELOG.md updated
- [ ] Commit pushed to branch `copilot/fix-randomly-revealed-cards`
- [ ] No regressions in existing features (victory detection, scoring, new_game)
- [ ] Screen reader compatibility verified (NVDA on Windows)
- [ ] Debug command CTRL+ALT+W works and triggers complete victory flow
- [ ] Dialogs opt-in (backward compatible with existing code)

**Estimated completion**: 4-5 ore for GitHub Copilot (with manual testing)

---

**Created**: 2026-02-11 19:49 CET  
**Branch**: `copilot/fix-randomly-revealed-cards`  
**Version**: v1.6.0  
**Priority**: HIGH  
**Type**: FEATURE + ENHANCEMENT  
**Assignee**: GitHub Copilot (with manual testing verification)

---

END OF TODO
