# 📖 IMPLEMENTATION GUIDE: Victory Flow & Native Dialogs System

**Version**: v1.6.0  
**Created**: 2026-02-11  
**Author**: Nemex81  
**Status**: 🟡 DRAFT - Ready for Implementation

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Context & Motivation](#context--motivation)
3. [Architecture Overview](#architecture-overview)
4. [Component Specifications](#component-specifications)
5. [Integration Points](#integration-points)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Implementation Details](#implementation-details)
8. [Testing Strategy](#testing-strategy)
9. [Migration Notes](#migration-notes)
10. [Future Enhancements](#future-enhancements)

---

## 📊 Executive Summary

### What

Implementation of **two critical features** for game completion flow:

1. **Native Dialog Boxes System**: Replace virtual dialogs (TTS-only) with real wxPython modal dialogs for tactile feedback and screen reader compatibility
2. **Victory Flow with Final Report**: Complete end-game statistics with suit tracking, final report formatting, and rematch prompt

### Why

The current architecture (v1.5.x) lacks:
- **Tactile feedback** for critical game events (victory, defeat, errors)
- **Suit progress tracking** (carte_per_seme, semi_completati)
- **Comprehensive final report** like legacy version
- **Testing utilities** for victory flow validation

### How

Following **Clean Architecture principles** with minimal invasiveness:
- DialogProvider abstraction in Infrastructure layer (Dependency Injection)
- Suit statistics tracking in GameService (Domain Services)
- Report formatting in Presentation layer (Single Responsibility)
- Optional dialogs via factory parameter (Open/Closed Principle)

### Impact

- **355 new LOC** (3 new files)
- **105 modified LOC** (3 existing files)
- **Zero breaking changes** (all opt-in)
- **~5 hours** estimated implementation time

---

## 🎯 Context & Motivation

### Current State (v1.5.2.4)

#### Virtual Dialogs

The new architecture (`src/`) uses **TTS-only announcements** for all user feedback:

```python
# Current approach in GameEngine
if self.screen_reader:
    self.screen_reader.tts.speak("Hai vinto!", interrupt=True)
# No visual/tactile feedback for non-visual users
```

**Problems**:
- **No confirmation dialogs**: User can't pause on important messages
- **No input prompts**: Can't ask "Vuoi giocare ancora?"
- **Screen reader dependency**: Breaks if TTS unavailable
- **Inconsistent UX**: Legacy version had rich dialog support

#### Missing Suit Statistics

GameService tracks basic stats but not suit-specific progress:

```python
# Current tracking (GameService)
self.move_count: int = 0
self.elapsed_time: float = 0.0
# Missing: carte_per_seme, semi_completati
```

**Problems**:
- **Incomplete reports**: Can't show "Cuori: 13/13, Quadri: 7/13..."
- **No completion percentage**: Can't calculate 75% progress
- **Testing difficulty**: Can't verify suit progression logic

#### No Victory Testing

No way to simulate victory without completing entire game manually.

**Problem**: Slow development iteration for end-game features.

### Legacy Reference (scr/game_engine.py)

The old version had all missing features:

```python
# DialogBox integration
from my_lib.dialog_box import DialogBox

class EngineData(DialogBox):
    def __init__(self, tavolo):
        super().__init__()  # Inherit wx dialog methods
        self.carte_per_seme = [0, 0, 0, 0]
        self.semi_completati = 0
        # ...

# Suit tracking
def aggiorna_statistiche_semi(self):
    for i in range(4):
        pile_index = 7 + i
        num_carte = self.tavolo.pile[pile_index].get_len()
        self.carte_per_seme[i] = num_carte
        if num_carte == 13:  # French deck
            self.semi_completati += 1

# Final report
def get_report_game(self):
    string = "Partita terminata,\n"
    string += f"minuti trascorsi: {minuti_trascorsi}.\n"
    for i in range(4):
        nome_seme = nomi_semi[i]
        string += f"{nome_seme}: {self.final_carte_per_seme[i]} carte.\n"
    # ...
    self.create_alert_box(string, "Report Finale")
```

**Key patterns to preserve**:
- ✅ Snapshot `final_*` attributes before reset
- ✅ Dialog inheritance for clean integration
- ✅ Italian suit names dynamically derived from deck
- ✅ Completion percentage calculation

### Design Goals for v1.6.0

1. **Preserve Clean Architecture**: No domain contamination with wxPython
2. **Opt-in Dialogs**: Backward compatible (TTS-only still works)
3. **Feature Parity**: Match legacy report completeness
4. **Testability**: Mock dialogs for automated tests
5. **Debug Support**: Victory simulation command (CTRL+ALT+W)

---

## 🏗️ Architecture Overview

### Clean Architecture Compliance

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ReportFormatter (new)                          │   │
│  │  - format_final_report()                        │   │
│  │  - format_suit_statistics()                     │   │
│  │  - format_victory_message()                     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ uses
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │  GameEngine (modified)                          │   │
│  │  + dialog_provider: Optional[DialogProvider]    │   │
│  │  + end_game(is_victory: bool) → None           │   │
│  │  + _debug_force_victory() → str                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ coordinates
┌─────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  GameService (modified)                         │   │
│  │  + carte_per_seme: List[int]                    │   │
│  │  + semi_completati: int                         │   │
│  │  + final_carte_per_seme: List[int]              │   │
│  │  + final_semi_completati: int                   │   │
│  │  + get_final_statistics() → Dict               │   │
│  │  - _update_suit_statistics() → None            │   │
│  │  - _snapshot_statistics() → None               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ depends on
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  DialogProvider (interface) (new)               │   │
│  │  + show_alert(message, title) → None           │   │
│  │  + show_yes_no(question, title) → bool         │   │
│  │  + show_input(question, title, default) → str  │   │
│  └─────────────────────────────────────────────────┘   │
│                          ▲                              │
│                          │ implements                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  WxDialogProvider (new)                         │   │
│  │  - Uses wx.MessageDialog                        │   │
│  │  - Uses wx.TextEntryDialog                      │   │
│  │  - Manages wx.App() lifecycle                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
GameEngine (Application)
    ↓ optional injection
DialogProvider (Infrastructure Interface)
    ↓ runtime binding
WxDialogProvider (Infrastructure Implementation)
    ↓ uses
wxPython library
```

**Key principle**: Domain and Application layers know only the **interface**, never the concrete wxPython implementation.

---

## 🧩 Component Specifications

### 1. DialogProvider (Interface)

**File**: `src/infrastructure/ui/dialog_provider.py`  
**Type**: Abstract Base Class (Protocol)  
**Purpose**: Define contract for dialog operations

#### Interface Definition

```python
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
    """
    
    @abstractmethod
    def show_alert(self, message: str, title: str) -> None:
        """Show informational alert dialog (OK button only).
        
        Args:
            message: Main content (can be multi-line)
            title: Dialog window title
            
        Blocks until user dismisses dialog.
        
        Example:
            >>> provider.show_alert(
            ...     "Hai vinto!\nMosse: 85\nTempo: 3:45",
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
            True if Yes clicked, False if No or dialog closed
            
        Example:
            >>> if provider.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
            ...     start_new_game()
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
            User input string, or None if cancelled
            
        Example:
            >>> name = provider.show_input(
            ...     "Inserisci il tuo nome:",
            ...     "Configurazione",
            ...     default="Giocatore 1"
            ... )
        """
        pass
```

#### Design Rationale

- **ABC over Protocol**: Explicit inheritance for clear intent
- **No async**: All dialogs are modal (blocking by design)
- **Optional return**: Input dialog can be cancelled
- **Italian docstrings**: Match project language conventions

---

### 2. WxDialogProvider (Implementation)

**File**: `src/infrastructure/ui/wx_dialog_provider.py`  
**Type**: Concrete Implementation  
**Purpose**: wxPython-based dialog system

#### Implementation Strategy

```python
import wx
from typing import Optional
from src.infrastructure.ui.dialog_provider import DialogProvider

class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Platform support:
        - Windows: Full support (NVDA, JAWS tested)
        - Linux: Partial (Orca may have focus issues with modals)
        - macOS: Not tested (should work with VoiceOver)
    
    Known limitations:
        - Multiple wx.App() instances per session (harmless but verbose logs)
        - Focus stealing from pygame window (restored on close)
        - No async support (intentional - simplifies screen reader integration)
    """
    
    def show_alert(self, message: str, title: str) -> None:
        """Show modal alert with OK button.
        
        Uses wx.MessageDialog with wx.OK | wx.ICON_INFORMATION.
        Screen reader announces title + message when dialog opens.
        """
        app = wx.App()  # Create app instance
        dlg = wx.MessageDialog(
            None,  # No parent window
            message,
            title,
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        wx.Yield()  # Process pending events
    
    def show_yes_no(self, question: str, title: str) -> bool:
        """Show modal Yes/No dialog.
        
        Uses wx.MessageDialog with wx.YES_NO | wx.NO_DEFAULT.
        NO is default to prevent accidental confirmations.
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

#### Legacy Compatibility

This implementation **exactly matches** the pattern from `my_lib/wx_dialog_box.py`:

```python
# Legacy pattern (preserved)
app = wx.App()  # New instance each time
dlg = wx.MessageDialog(...)
result = dlg.ShowModal()
dlg.Destroy()
wx.Yield()  # Important for screen reader focus restoration
```

**Why this works**:
- pygame runs its own event loop
- wxPython dialogs are modal (block pygame loop)
- wx.Yield() ensures pending events processed
- Focus returns to pygame window automatically

---

### 3. Suit Statistics Tracking (GameService)

**File**: `src/domain/services/game_service.py` (modified)  
**Type**: Domain Service Extension  
**Purpose**: Track per-suit progress for reporting

#### New Attributes

```python
class GameService:
    def __init__(self, ...):
        # ... existing attributes ...
        
        # ✨ NEW: Live suit statistics
        self.carte_per_seme: List[int] = [0, 0, 0, 0]
        #   Index mapping: 0=Hearts, 1=Diamonds, 2=Clubs, 3=Spades
        #   For Neapolitan: 0=Coppe, 1=Denari, 2=Bastoni, 3=Spade
        
        self.semi_completati: int = 0
        #   Increments when a suit reaches full count (13 or 10)
        
        # ✨ NEW: Snapshot for final report (preserved during reset)
        self.final_carte_per_seme: List[int] = [0, 0, 0, 0]
        self.final_semi_completati: int = 0
```

#### Update Logic

```python
def move_card(
    self,
    source: Pile,
    target: Pile,
    card_count: int,
    is_foundation: bool
) -> Tuple[bool, str]:
    """Execute card move with suit statistics tracking."""
    
    # ... existing validation and move logic ...
    
    # ✨ NEW: Update suit stats after foundation move
    if success and is_foundation:
        self._update_suit_statistics()
    
    return success, message

def _update_suit_statistics(self) -> None:
    """Update live suit statistics by scanning foundation piles.
    
    Called after every successful move to foundation.
    Recalculates from scratch (idempotent).
    
    Foundation pile indices: 7, 8, 9, 10
    Suit order matches deck.SUITS order.
    """
    # Get cards needed for complete suit (13 French, 10 Neapolitan)
    cards_per_suit = len(self.table.mazzo.VALUES)
    
    # Reset completed counter
    self.semi_completati = 0
    
    # Scan all 4 foundation piles
    for i in range(4):
        pile_index = 7 + i
        foundation_pile = self.table.pile_semi[i]
        
        # Count cards in this suit
        num_cards = foundation_pile.get_card_count()
        self.carte_per_seme[i] = num_cards
        
        # Check if suit completed
        if num_cards == cards_per_suit:
            self.semi_completati += 1
```

#### Snapshot Logic

```python
def _snapshot_statistics(self) -> None:
    """Snapshot current statistics before reset.
    
    Called by end_game() to preserve final values.
    Uses .copy() to avoid reference sharing.
    """
    self.final_carte_per_seme = self.carte_per_seme.copy()
    self.final_semi_completati = self.semi_completati

def get_final_statistics(self) -> Dict[str, Any]:
    """Get snapshot of final statistics.
    
    Returns:
        Dictionary with all final game statistics including:
        - move_count, elapsed_time (existing)
        - carte_per_seme, semi_completati (new)
        - completion_percentage (calculated)
        
    Example:
        >>> stats = service.get_final_statistics()
        >>> print(stats['carte_per_seme'])  # [13, 10, 7, 0]
        >>> print(stats['completion_percentage'])  # 57.7
    """
    # Calculate total cards in foundations
    total_foundation_cards = sum(self.final_carte_per_seme)
    total_deck_cards = self.table.mazzo.get_total_cards()
    
    completion_pct = (total_foundation_cards / total_deck_cards) * 100
    
    return {
        "move_count": self.move_count,
        "elapsed_time": self.get_elapsed_time(),
        "carte_per_seme": self.final_carte_per_seme,
        "semi_completati": self.final_semi_completati,
        "total_foundation_cards": total_foundation_cards,
        "completion_percentage": completion_pct
    }
```

#### Reset Behavior

```python
def reset_game(self) -> None:
    """Reset game state for new game.
    
    IMPORTANT: Does NOT clear final_* snapshot attributes.
    This allows consulting last game stats after reset.
    """
    # Reset live counters
    self.move_count = 0
    self.carte_per_seme = [0, 0, 0, 0]
    self.semi_completati = 0
    # ...
    
    # ✅ Preserve final_* for post-game consultation
    # final_carte_per_seme unchanged
    # final_semi_completati unchanged
```

---

### 4. ReportFormatter (Presentation)

**File**: `src/presentation/formatters/report_formatter.py` (new)  
**Type**: Static Formatter  
**Purpose**: Generate Italian TTS-optimized final reports

#### Core Method

```python
class ReportFormatter:
    """Format final game reports for TTS and dialog display.
    
    All methods are static (stateless formatting).
    Output optimized for Italian screen readers (NVDA, JAWS).
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
            is_victory: Whether game was won
            deck_type: "french" or "neapolitan" for suit names
            
        Returns:
            Multi-line Italian report string
            
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
        
        # Victory/defeat header
        if is_victory:
            lines.append("Hai Vinto!")
            lines.append("Complimenti, vittoria spumeggiante!")
        else:
            lines.append("Partita terminata.")
        
        lines.append("")  # Blank line
        
        # Time and moves
        elapsed = int(stats['elapsed_time'])
        minutes = elapsed // 60
        seconds = elapsed % 60
        lines.append(f"Tempo trascorso: {minutes} minuti e {seconds} secondi.")
        lines.append(f"Spostamenti totali: {stats['move_count']}.")
        
        # Reshuffles (if any)
        if 'recycle_count' in stats and stats['recycle_count'] > 0:
            lines.append(f"Rimischiate: {stats['recycle_count']}.")
        
        lines.append("")  # Blank line
        
        # Suit statistics
        lines.append("--- Statistiche Pile Semi ---")
        suit_names = ReportFormatter._get_suit_names(deck_type)
        
        for i, suit_name in enumerate(suit_names):
            count = stats['carte_per_seme'][i]
            max_cards = 13 if deck_type == "french" else 10
            
            if count == max_cards:
                lines.append(f"{suit_name}: {count} carte (completo!).")
            else:
                lines.append(f"{suit_name}: {count} carte.")
        
        lines.append("")  # Blank line
        
        # Completion summary
        lines.append(
            f"Semi completati: {stats['semi_completati']} su 4."
        )
        lines.append(
            f"Completamento totale: {stats['total_foundation_cards']} "
            f"su {52 if deck_type == 'french' else 40} carte "
            f"({stats['completion_percentage']:.1f}%)."
        )
        
        # Scoring (if available)
        if final_score:
            lines.append("")  # Blank line
            lines.append(f"Punteggio finale: {final_score.total_score} punti.")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_suit_names(deck_type: str) -> List[str]:
        """Get localized suit names for deck type."""
        if deck_type == "neapolitan":
            return ["Coppe", "Denari", "Bastoni", "Spade"]
        else:  # french
            return ["Cuori", "Quadri", "Fiori", "Picche"]
```

#### TTS Optimization Rules

1. **Short sentences**: Max 10-12 words per line
2. **No symbols**: Use words ("completo!" not "✅")
3. **Clear numbers**: "3 minuti" not "3m"
4. **Pause markers**: Blank lines → natural pauses
5. **Punctuation**: Period ends each statement for breath

---

### 5. GameEngine Integration

**File**: `src/application/game_engine.py` (modified)

#### Constructor Changes

```python
def __init__(
    self,
    ...,
    dialog_provider: Optional[DialogProvider] = None  # NEW
):
    # ... existing initialization ...
    
    # Dialog integration (opt-in)
    self.dialogs = dialog_provider
```

#### Factory Method Changes

```python
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1,
    settings: Optional[GameSettings] = None,
    use_native_dialogs: bool = False  # NEW parameter
) -> "GameEngine":
    # ... existing initialization ...
    
    # Create dialog provider if requested
    dialog_provider = None
    if use_native_dialogs:
        from src.infrastructure.ui.wx_dialog_provider import WxDialogProvider
        dialog_provider = WxDialogProvider()
    
    return cls(
        table, service, rules, cursor, selection,
        screen_reader, settings, score_storage,
        dialog_provider  # NEW argument
    )
```

#### End Game Method (Complete Rewrite)

```python
def end_game(self, is_victory: bool) -> None:
    """Handle game end with full reporting and rematch prompt.
    
    Flow:
    1. Snapshot statistics (including suits)
    2. Calculate final score (if scoring enabled)
    3. Save score to storage (if available)
    4. Generate complete report
    5. Announce via TTS (always)
    6. Show native dialog (if available)
    7. Prompt for rematch (if dialogs available)
    8. Reset game state
    
    Args:
        is_victory: True if all 4 suits completed
        
    Side effects:
        - Stops game timer
        - Saves score to JSON (if scoring enabled)
        - May start new game (if user chooses rematch)
    """
    
    # === STEP 1: Snapshot Statistics ===
    self.service._snapshot_statistics()
    final_stats = self.service.get_final_statistics()
    
    # === STEP 2: Calculate Final Score ===
    final_score = None
    if self.settings and self.settings.scoring_enabled and self.service.scoring:
        final_score = self.service.scoring.calculate_final_score(
            elapsed_seconds=final_stats['elapsed_time'],
            move_count=final_stats['move_count'],
            is_victory=is_victory,
            timer_strict_mode=self.settings.timer_strict_mode
        )
    
    # === STEP 3: Save Score ===
    if final_score and self.score_storage:
        self.score_storage.save_score(final_score)
    
    # === STEP 4: Generate Report ===
    deck_type = self.settings.deck_type if self.settings else "french"
    report = ReportFormatter.format_final_report(
        stats=final_stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type
    )
    
    # === STEP 5: TTS Announcement (Always) ===
    if self.screen_reader:
        self.screen_reader.tts.speak(report, interrupt=True)
    
    # === STEP 6: Native Dialog (Optional) ===
    if self.dialogs:
        title = "Congratulazioni!" if is_victory else "Partita Terminata"
        self.dialogs.show_alert(report, title)
        
        # === STEP 7: Rematch Prompt ===
        if self.dialogs.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
            self.new_game()
            return  # Don't reset twice
    
    # === STEP 8: Reset Game State ===
    # Note: If rematch chosen, new_game() already reset
    self.service.reset_game()
```

#### Debug Victory Command

```python
def _debug_force_victory(self) -> str:
    """🔥 DEBUG ONLY: Simulate victory for testing end_game flow.
    
    Keyboard binding: CTRL+ALT+W
    
    WARNING: Remove this method before production release!
    
    Simulates victory without actually completing the game.
    Useful for testing:
    - Final report formatting
    - Dialog appearance
    - Score calculation
    - Rematch flow
    
    Returns:
        Confirmation message for TTS
        
    Example:
        >>> engine._debug_force_victory()
        "Vittoria simulata attivata! Report finale in arrivo."
    """
    if not self.is_game_running():
        return "Nessuna partita in corso da vincere!"
    
    # Stop game timer (preserves elapsed_time)
    self.service._game_running = False
    
    # Trigger victory flow
    self.end_game(is_victory=True)
    
    return "Vittoria simulata attivata! Report finale in arrivo."
```

---

## 🔄 Data Flow Diagrams

### Victory Flow (Complete Path)

```
┌─────────────────────────────────────────────────────────────────┐
│                  USER COMPLETES LAST MOVE                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  GameEngine.execute_move()                                      │
│  ├─ service.move_card() → success                               │
│  ├─ service._update_suit_statistics()                           │
│  └─ if service.is_victory(): end_game(is_victory=True)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  GameEngine.end_game(is_victory=True)                           │
│                                                                 │
│  Step 1: service._snapshot_statistics()                         │
│          ├─ final_carte_per_seme = [13,13,13,13]               │
│          ├─ final_semi_completati = 4                           │
│          └─ Preserves before reset                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: service.get_final_statistics()                         │
│          Returns: {                                             │
│            move_count: 85,                                      │
│            elapsed_time: 225.3,                                 │
│            carte_per_seme: [13,13,13,13],                       │
│            semi_completati: 4,                                  │
│            completion_percentage: 100.0                         │
│          }                                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: scoring.calculate_final_score() (if enabled)           │
│          Calculates: base + bonuses + multipliers               │
│          Returns: FinalScore(total_score=1523, ...)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: score_storage.save_score() (if enabled)                │
│          Saves to: ~/.solitario/scores.json                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: ReportFormatter.format_final_report()                  │
│          Generates Italian multi-line report                    │
│          Returns: "Hai Vinto!\n\nTempo trascorso: ..."          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: screen_reader.tts.speak(report)  [ALWAYS]             │
│          Announces complete report via TTS                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 7: dialogs.show_alert(report, title)  [IF AVAILABLE]     │
│          Shows wxPython modal dialog                            │
│          User reads at own pace, presses OK                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 8: dialogs.show_yes_no("Rivincita?")  [IF AVAILABLE]     │
│          ├─ YES → GameEngine.new_game()                         │
│          └─ NO  → service.reset_game() (stay in game over)      │
└─────────────────────────────────────────────────────────────────┘
```

### Debug Victory Flow (Shortcut)

```
User presses CTRL+ALT+W
    ↓
main.py event handler
    ↓
engine._debug_force_victory()
    ├─ Check if game running
    ├─ Stop timer (preserve elapsed_time)
    └─ Call end_game(is_victory=True)
        ↓
    [Follows same flow as normal victory above]
```

---

## 🛠️ Implementation Details

### File Structure Changes

```
src/
├── infrastructure/
│   └── ui/                      # NEW DIRECTORY
│       ├── __init__.py          # NEW: 10 LOC
│       ├── dialog_provider.py   # NEW: 80 LOC
│       └── wx_dialog_provider.py # NEW: 120 LOC
│
├── domain/services/
│   └── game_service.py          # MODIFIED: +80 LOC
│       # Added:
│       #   - carte_per_seme, semi_completati attributes
│       #   - final_* snapshot attributes
│       #   - _update_suit_statistics()
│       #   - _snapshot_statistics()
│       #   - get_final_statistics()
│
├── application/
│   └── game_engine.py           # MODIFIED: +150 LOC
│       # Added:
│       #   - dialog_provider parameter
│       #   - end_game() complete rewrite
│       #   - _debug_force_victory()
│       # Modified:
│       #   - __init__() signature
│       #   - create() factory
│
└── presentation/formatters/
    └── report_formatter.py      # NEW: 200 LOC
        # Contains:
        #   - format_final_report()
        #   - format_suit_statistics()
        #   - _get_suit_names()
```

### Import Dependencies

```python
# New imports in game_engine.py
from typing import Optional
from src.infrastructure.ui.dialog_provider import DialogProvider
from src.presentation.formatters.report_formatter import ReportFormatter

# New imports in game_service.py
from typing import List, Dict, Any

# New imports in wx_dialog_provider.py
import wx
from typing import Optional
from src.infrastructure.ui.dialog_provider import DialogProvider
```

### Type Hints Conventions

```python
# Use explicit Optional for clarity
def show_input(...) -> Optional[str]:  # Can return None

# Use List from typing (not list) for Python 3.8 compatibility
from typing import List
self.carte_per_seme: List[int] = [0, 0, 0, 0]

# Use Dict from typing for complex structures
from typing import Dict, Any
def get_final_statistics(self) -> Dict[str, Any]:
```

---

## 🧪 Testing Strategy

### Manual Testing Checklist

#### Test Case 1: Victory with Dialogs Enabled

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
```

**Steps**:
1. Play game to completion (all 52 cards in foundations)
2. Observe final move triggers victory detection

**Expected Results**:
- ✅ TTS announces complete report
- ✅ wxPython alert dialog appears with full report
- ✅ Report includes:
  - "Hai Vinto!" header
  - Tempo trascorso (minutes:seconds)
  - Spostamenti totali (move count)
  - 4 suits shown as "completo!"
  - "Semi completati: 4 su 4"
  - "Completamento totale: 52 su 52 carte (100.0%)"
- ✅ Dialog has OK button (closes on click)
- ✅ After closing, "Rivincita?" Yes/No dialog appears
- ✅ Clicking Yes starts new game
- ✅ Clicking No returns to game over state

#### Test Case 2: Debug Victory Command

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
# Make a few moves but don't complete
```

**Steps**:
1. Press CTRL+ALT+W

**Expected Results**:
- ✅ TTS announces "Vittoria simulata attivata!"
- ✅ Victory flow triggers immediately
- ✅ Report shows incomplete suits (e.g., "Cuori: 3 carte")
- ✅ Completion percentage < 100%
- ✅ Rematch dialog still appears

#### Test Case 3: Victory without Dialogs (TTS only)

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=False)  # Default
engine.new_game()
```

**Steps**:
1. Use CTRL+ALT+W to simulate victory

**Expected Results**:
- ✅ TTS announces complete report
- ❌ No wxPython dialogs appear
- ✅ Game resets automatically (no rematch prompt)
- ✅ Can start new game manually

#### Test Case 4: Suit Statistics Accuracy

**Setup**:
```python
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
```

**Steps**:
1. Move Ace of Hearts to foundation → check stats
2. Move 2 of Hearts to foundation → check stats
3. Complete Hearts suit (all 13 cards) → check stats
4. Complete Diamonds suit → check stats
5. Simulate victory with CTRL+ALT+W

**Expected Results**:
- ✅ After step 1: carte_per_seme = [1, 0, 0, 0]
- ✅ After step 2: carte_per_seme = [2, 0, 0, 0]
- ✅ After step 3: carte_per_seme = [13, 0, 0, 0], semi_completati = 1
- ✅ After step 4: carte_per_seme = [13, 13, 0, 0], semi_completati = 2
- ✅ Final report shows:
  - "Cuori: 13 carte (completo!)."
  - "Quadri: 13 carte (completo!)."
  - "Fiori: 0 carte."
  - "Picche: 0 carte."
  - "Semi completati: 2 su 4."

#### Test Case 5: Neapolitan Deck Suit Names

**Setup**:
```python
settings = GameSettings()
settings.deck_type = "neapolitan"
engine = GameEngine.create(settings=settings, use_native_dialogs=True)
engine.new_game()
```

**Steps**:
1. Simulate victory with CTRL+ALT+W

**Expected Results**:
- ✅ Report uses Italian suit names:
  - "Coppe: X carte."
  - "Denari: X carte."
  - "Bastoni: X carte."
  - "Spade: X carte."
- ✅ Total cards: "X su 40 carte" (not 52)
- ✅ Complete suit shows 10 cards (not 13)

### Automated Testing (Optional)

```python
# tests/integration/test_victory_flow.py
import pytest
from src.application.game_engine import GameEngine
from src.infrastructure.ui.dialog_provider import DialogProvider

class MockDialogProvider(DialogProvider):
    """Test double for dialog testing."""
    
    def __init__(self):
        self.last_alert_message = None
        self.last_alert_title = None
        self.last_yes_no_question = None
        self.yes_no_result = False
    
    def show_alert(self, message: str, title: str) -> None:
        self.last_alert_message = message
        self.last_alert_title = title
    
    def show_yes_no(self, question: str, title: str) -> bool:
        self.last_yes_no_question = question
        return self.yes_no_result
    
    def show_input(self, question: str, title: str, default: str = "") -> Optional[str]:
        return "test_input"

def test_victory_report_contains_all_statistics():
    """Verify final report includes all required statistics."""
    mock_dialogs = MockDialogProvider()
    engine = GameEngine.create(dialog_provider=mock_dialogs)
    engine.new_game()
    
    # Simulate victory
    engine._debug_force_victory()
    
    # Verify alert was shown
    assert mock_dialogs.last_alert_message is not None
    assert "Tempo trascorso:" in mock_dialogs.last_alert_message
    assert "Spostamenti totali:" in mock_dialogs.last_alert_message
    assert "Semi completati:" in mock_dialogs.last_alert_message
    assert "Completamento totale:" in mock_dialogs.last_alert_message
    
    # Verify rematch prompt
    assert mock_dialogs.last_yes_no_question == "Vuoi giocare ancora?"

def test_suit_statistics_update_on_foundation_move():
    """Verify suit stats increment correctly."""
    engine = GameEngine.create()
    engine.new_game()
    
    # Initial state
    assert engine.service.carte_per_seme == [0, 0, 0, 0]
    assert engine.service.semi_completati == 0
    
    # Move Ace to foundation (manual pile manipulation for test)
    # Note: In real test, would use actual move logic
    # This is pseudocode for illustration
    source = engine.table.pile_base[0]
    target = engine.table.pile_semi[0]  # Hearts foundation
    
    # Simulate moving Ace
    engine.service.move_card(source, target, 1, is_foundation=True)
    
    # Verify stats updated
    assert engine.service.carte_per_seme[0] == 1  # Hearts count
    assert engine.service.semi_completati == 0    # Not complete yet
```

---

## 🔄 Migration Notes

### Backward Compatibility

**✅ 100% backward compatible**

All changes are **opt-in** via new parameters:

```python
# Old code (still works)
engine = GameEngine.create()
engine.new_game()
# Behavior: TTS-only, no dialogs, basic stats

# New code (opt-in dialogs)
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
# Behavior: TTS + native dialogs, full stats
```

### Existing Codebases

No changes required to existing code that uses GameEngine.

If dialogs desired, add single parameter:

```diff
  engine = GameEngine.create(
      audio_enabled=True,
      tts_engine="nvda",
-     verbose=1
+     verbose=1,
+     use_native_dialogs=True  # NEW
  )
```

### Configuration Files

No configuration file changes needed.

Dialogs are programmatically enabled at runtime.

### Dependencies

Add to `requirements.txt` if missing:

```
wxPython>=4.1.0
```

Install via:

```bash
pip install wxPython
```

---

## 🚀 Future Enhancements

### Phase 2: Extended Dialog Usage

After v1.6.0 stabilizes, consider using dialogs for:

1. **Critical Errors**: Disk full, save file corrupted
2. **Confirm Actions**: "Sei sicuro di voler resettare la partita?"
3. **Settings Input**: Complex options like custom timer values
4. **High Scores**: Show top 10 scores in formatted dialog

### Phase 3: Rich Report Formatting

Enhance ReportFormatter with:

1. **HTML Export**: Save report as `report.html` with CSS styling
2. **Chart Generation**: Pie chart for suit completion (matplotlib)
3. **Comparison**: "Questo è il tuo miglior tempo!"
4. **Achievements**: "Unlock: Prima vittoria senza rimescolate"

### Phase 4: Dialog Theming

Customize wxPython dialogs:

1. **Dark Mode**: Match system preferences
2. **Font Size**: User-adjustable for low vision
3. **High Contrast**: For accessibility compliance
4. **Custom Icons**: Branded alert/question icons

### Phase 5: Alternative Dialog Backends

Implement additional DialogProvider implementations:

1. **TerminalDialogProvider**: For CLI-only environments
2. **WebDialogProvider**: For future web version
3. **GtkDialogProvider**: Native Linux dialogs (GTK3)
4. **QtDialogProvider**: Cross-platform Qt alternative

---

## 📚 References

### Code References

- **Legacy Dialog System**: `my_lib/dialog_box.py`, `my_lib/wx_dialog_box.py`
- **Legacy Statistics**: `scr/game_engine.py` lines 50-90 (attributes), 800-850 (methods)
- **Current Architecture**: `src/application/game_engine.py`
- **Scoring System**: `src/domain/services/scoring_service.py`

### External Documentation

- **wxPython Dialogs**: https://docs.wxpython.org/wx.MessageDialog.html
- **Clean Architecture**: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- **NVDA Screen Reader**: https://www.nvaccess.org/
- **WCAG Accessibility**: https://www.w3.org/WAI/WCAG21/quickref/

### Project Documents

- **TODO Template**: `docs/TODO.md`
- **Scoring Implementation**: `docs/IMPLEMENTATION_SCORING_SYSTEM.md`
- **Changelog**: `CHANGELOG.md`
- **README**: `README.md`

---

## 🎓 Learning Resources

### For Contributors

If implementing this system, study these patterns:

1. **Dependency Injection**: DialogProvider abstraction
2. **Snapshot Pattern**: Statistics preservation before reset
3. **Factory Method**: GameEngine.create() with multiple parameters
4. **Strategy Pattern**: Different dialog implementations

### Code Examples to Review

```python
# Pattern 1: Optional dependency injection
class GameEngine:
    def __init__(self, ..., dialog_provider: Optional[DialogProvider] = None):
        self.dialogs = dialog_provider  # None is valid!
    
    def end_game(self):
        if self.dialogs:  # Guard clause
            self.dialogs.show_alert(...)

# Pattern 2: Snapshot before mutation
class GameService:
    def _snapshot_statistics(self):
        self.final_carte_per_seme = self.carte_per_seme.copy()  # .copy() critical!
    
    def reset_game(self):
        self.carte_per_seme = [0, 0, 0, 0]  # Live data reset
        # final_carte_per_seme preserved!

# Pattern 3: Static formatting
class ReportFormatter:
    @staticmethod
    def format_final_report(...) -> str:
        # No instance state, pure function
        pass
```

---

## ✅ Pre-Implementation Checklist

Before starting implementation, verify:

- [ ] wxPython installed (`pip install wxPython`)
- [ ] Current GameEngine compiles and runs
- [ ] Legacy dialog code reviewed (`my_lib/wx_dialog_box.py`)
- [ ] TODO file created from template
- [ ] Branch created: `feature/victory-flow-dialogs`
- [ ] Tests disabled if implementing incrementally
- [ ] Screen reader available for testing (NVDA/JAWS)

---

## 📝 Implementation Notes for Copilot

### Critical Requirements

1. **Never break existing code**: All changes must be backward compatible
2. **Type hints everywhere**: Every new method/attribute fully typed
3. **Docstrings mandatory**: Google style for all public API
4. **Italian strings**: All user-facing text in Italian
5. **TTS optimization**: Short sentences, clear punctuation

### Common Pitfalls to Avoid

❌ **Don't**:
- Import wxPython in domain/application layers (except DialogProvider interface)
- Mutate `carte_per_seme` without calling `.copy()` for snapshot
- Skip `wx.Yield()` after dialog destruction
- Use f-strings with symbols (`🎉` breaks TTS)

✅ **Do**:
- Guard all dialog calls with `if self.dialogs:`
- Call `_snapshot_statistics()` BEFORE reset
- Use `Optional[T]` for nullable types
- Test both with/without dialogs enabled

### Testing During Development

After each phase, run:

```python
# Quick smoke test
engine = GameEngine.create(use_native_dialogs=True)
engine.new_game()
engine._debug_force_victory()  # Should show dialogs
```

---

## 📄 Document Revision History

| Version | Date       | Author   | Changes                          |
|---------|------------|----------|----------------------------------|
| 1.0     | 2026-02-11 | Nemex81  | Initial comprehensive guide      |

---

**End of Implementation Guide**

For implementation checklist, see `docs/TODO_VICTORY_FLOW_DIALOGS.md`
