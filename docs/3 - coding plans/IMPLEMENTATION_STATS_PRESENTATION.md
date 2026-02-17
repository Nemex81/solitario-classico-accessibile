# 🔧 IMPLEMENTATION PLAN
# Statistics Presentation & UI/UX Layer — v3.0.0

## 📌 Informazioni Generali

**Feature**: Statistics Presentation & UI/UX Layer  
**Versione Target**: v3.0.0  
**Layer**: Presentation + Application (Dialog + Formatters + GameEngine hooks)  
**Stato**: Implementation Phase — **READY FOR COPILOT**  
**Data Creazione**: 17 Febbraio 2026  
**Prerequisiti**:
- [DESIGN_STATISTICS_PRESENTATION.md](../2%20-%20projects/DESIGN_STATISTICS_PRESENTATION.md) (UI/UX design completo)
- [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md) (data model)
- [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md) (EndReason logic)
- **Profile System v3.0.0 Backend implementato** (ProfileService disponibile)
- **Timer System v2.7.0 implementato** (EndReason enum disponibile)

---

## 🎯 Obiettivo dell'Implementation Plan

Implementare il **layer di presentazione** per statistiche profilo:
- ✅ Dialog vittoria/abbandono con stats integrate
- ✅ Info partita corrente (tasto I durante gameplay)
- ✅ Statistiche dettagliate (3 pagine navigabili)
- ✅ Leaderboard globale (5 classifiche)
- ✅ StatsFormatter class (TTS-friendly)
- ✅ Accessibilità NVDA completa (focus, keyboard nav, announcements)
- ✅ Integration con GameEngine e ProfileService

**Scope**: Solo UI/UX presentation. Backend (ProfileService) già implementato.

---

## 🔄 Workflow Copilot Agent (Checkpoint-Driven)

Ogni commit segue questo pattern:

```
1. 📖 READ: Consulta questo piano + design doc
2. ✅ CHECK: Verifica checklist fase corrente
3. 💻 CODE: Implementa modifiche atomiche (1 dialog o 1 formatter)
4. 🧪 TEST: Scrivi unit tests (formatter) + manual UI test instructions
5. 📝 COMMIT: Messaggio descrittivo + update checklist
6. ♻️ REPEAT: Passa alla fase successiva
```

**Regola d'oro**: Un commit = un dialog o un formatter method. Splitta se >200 righe.

---

## 📊 Progress Tracking (Copilot: Aggiorna Ad Ogni Commit)

### ✅ Phase Completion Checklist

- [ ] **Phase 1**: StatsFormatter class base structure
- [ ] **Phase 2**: Victory dialog (essenziale + dettagli)
- [ ] **Phase 3**: Abandon dialog
- [ ] **Phase 4**: Current game info dialog (tasto I)
- [ ] **Phase 5**: Detailed stats (3 pagine + scroll)
- [ ] **Phase 6**: Leaderboard UI (main + filters)
- [ ] **Phase 7**: GameEngine integration (all hooks)
- [ ] **Phase 8**: NVDA accessibility polish (focus + announcements)
- [ ] **Phase 9**: Menu integration (Ultima Partita, Leaderboard)

**Istruzioni per Copilot**: Dopo ogni commit, spunta `[x]` la fase completata e committa l'aggiornamento di questo file insieme al codice.

---

## 🗂️ Struttura File Target

### Directory Tree (Post-Implementation)

```
src/
├── presentation/
│   ├── formatters/
│   │   ├── stats_formatter.py       # NEW: StatsFormatter class
│   │   └── game_formatter.py        # MODIFIED: +current game info
│   │
│   └── dialogs/
│       ├── victory_dialog.py        # NEW: Victory end dialog
│       ├── abandon_dialog.py        # NEW: Abandon end dialog
│       ├── game_info_dialog.py      # NEW: Current game info (tasto I)
│       ├── detailed_stats_dialog.py # NEW: 3-page stats navigation
│       └── leaderboard_dialog.py    # NEW: Global leaderboard
│
├── application/
│   └── game_engine.py               # MODIFIED: +dialog hooks, +menu options
│
└── tests/
    ├── unit/
    │   ├── test_stats_formatter.py  # NEW: Formatter output tests
    │   └── test_dialog_logic.py     # NEW: Dialog state machine tests
    │
    └── manual/
        └── NVDA_TEST_CHECKLIST.md   # NEW: Manual accessibility tests
```

---

## 🎨 PHASE 1: StatsFormatter Class (Foundation)

### 🎯 Obiettivo

Creare classe `StatsFormatter` per generare stringhe TTS-friendly da dati statistici.

### 📝 Commit 1.1: Create StatsFormatter Base Structure

**File**: `src/presentation/formatters/stats_formatter.py` (NEW)

```python
"""Formatter for profile statistics presentation (TTS-friendly)."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.domain.models.profile import SessionOutcome, EndReason
from src.domain.models.statistics import (
    GlobalStats, TimerStats, DifficultyStats, ScoringStats
)


class StatsFormatter:
    """Format profile statistics for screen-reader friendly presentation.
    
    All methods return multi-line strings optimized for NVDA reading.
    Includes proper Italian formatting (thousands separator, plurals).
    """
    
    # ========================================
    # TIME FORMATTING
    # ========================================
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in Italian (human-readable).
        
        Examples:
            42 sec -> "42 secondi"
            90 sec -> "1 minuto e 30 secondi"
            3665 sec -> "1 ora, 1 minuto e 5 secondi"
        """
        if seconds < 60:
            return f"{int(seconds)} secondi"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes < 60:
            if secs == 0:
                return f"{minutes} minuti" if minutes > 1 else "1 minuto"
            return f"{minutes} minuti e {secs} secondi"
        
        hours = minutes // 60
        mins = minutes % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours} ora" if hours == 1 else f"{hours} ore")
        if mins > 0:
            parts.append(f"{mins} minuti" if mins > 1 else f"{mins} minuto")
        if secs > 0:
            parts.append(f"{secs} secondi")
        
        return ", ".join(parts[:-1]) + " e " + parts[-1] if len(parts) > 1 else parts[0]
    
    @staticmethod
    def format_time_mm_ss(seconds: float) -> str:
        """Format time as MM:SS.
        
        Examples:
            42 -> "0:42"
            325 -> "5:25"
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    # ========================================
    # NUMBER FORMATTING
    # ========================================
    
    @staticmethod
    def format_number(value: int) -> str:
        """Format number with thousands separator.
        
        Examples:
            1250 -> "1.250"
            450 -> "450"
        """
        return f"{value:,}".replace(",", ".")
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage.
        
        Examples:
            0.6742 -> "67,4%"
            0.5 -> "50,0%"
        """
        return f"{value * 100:.{decimals}f}%".replace(".", ",")
    
    # ========================================
    # END REASON FORMATTING
    # ========================================
    
    @staticmethod
    def format_end_reason(reason: EndReason) -> str:
        """Format EndReason as Italian label.
        
        Returns:
            Human-readable Italian label for TTS.
        """
        labels = {
            EndReason.VICTORY: "Vittoria",
            EndReason.VICTORY_OVERTIME: "Vittoria (oltre tempo)",
            EndReason.ABANDON_NEW_GAME: "Abbandono (nuova partita)",
            EndReason.ABANDON_EXIT: "Abbandono volontario",
            EndReason.ABANDON_APP_CLOSE: "Chiusura app durante partita",
            EndReason.TIMEOUT_STRICT: "Tempo scaduto"
        }
        return labels.get(reason, reason.value)
```

**Test Coverage** (`tests/unit/test_stats_formatter.py`):

```python
import pytest
from src.presentation.formatters.stats_formatter import StatsFormatter
from src.domain.models.profile import EndReason


class TestStatsFormatterBase:
    """Test StatsFormatter utility methods."""
    
    def test_format_duration_seconds(self):
        assert StatsFormatter.format_duration(42) == "42 secondi"
    
    def test_format_duration_minutes(self):
        assert "5 minuti e 23 secondi" in StatsFormatter.format_duration(323)
    
    def test_format_duration_hours(self):
        result = StatsFormatter.format_duration(3665)  # 1h 1m 5s
        assert "1 ora" in result
        assert "1 minuto" in result
    
    def test_format_time_mm_ss(self):
        assert StatsFormatter.format_time_mm_ss(325) == "5:25"
        assert StatsFormatter.format_time_mm_ss(42) == "0:42"
    
    def test_format_number_thousands(self):
        assert StatsFormatter.format_number(1250) == "1.250"
        assert StatsFormatter.format_number(450) == "450"
    
    def test_format_percentage(self):
        assert StatsFormatter.format_percentage(0.6742) == "67,4%"
        assert StatsFormatter.format_percentage(0.5) == "50,0%"
    
    def test_format_end_reason(self):
        assert StatsFormatter.format_end_reason(EndReason.VICTORY) == "Vittoria"
        assert "oltre tempo" in StatsFormatter.format_end_reason(EndReason.VICTORY_OVERTIME)
```

**Commit Message**:
```
feat(presentation): Create StatsFormatter base utilities

- Time formatting: format_duration(), format_time_mm_ss()
- Number formatting: format_number() (thousands sep), format_percentage()
- EndReason formatting: format_end_reason() Italian labels
- Italian plurals handling (minuto/minuti, ora/ore)
- Tested: 7 test cases for utility methods

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 1
```

**Estimated Time**: 12-18 min  
**Test Count**: 7

**✅ Checkpoint**: Spunta Phase 1 dopo commit.

---

### 📝 Commit 1.2: Add Global Stats Formatting

**File**: `src/presentation/formatters/stats_formatter.py` (MODIFIED)

**Add Method**:

```python
class StatsFormatter:
    # ... existing methods ...
    
    def format_global_stats_summary(self, stats: GlobalStats) -> str:
        """Format global stats summary (for victory dialog footer).
        
        Returns:
            2-3 line summary with victories, winrate.
        """
        victories = self.format_number(stats.total_victories)
        winrate = self.format_percentage(stats.winrate)
        
        return (
            f"Vittorie totali: {victories}\n"
            f"Winrate: {winrate}"
        )
    
    def format_global_stats_detailed(self, stats: GlobalStats, profile_name: str) -> str:
        """Format full global stats page (Page 1 of detailed stats).
        
        Returns:
            Multi-line formatted text for 3-page stats dialog.
        """
        header = f"{'=' * 56}\n"
        header += f"    STATISTICHE PROFILO: {profile_name}\n"
        header += f"{'=' * 56}\n\n"
        
        performance = "PERFORMANCE GLOBALE\n"
        performance += f"Partite totali: {stats.total_games}\n"
        performance += f"Vittorie: {stats.total_victories} ({self.format_percentage(stats.winrate)})\n"
        performance += f"Sconfitte: {stats.total_defeats} ({self.format_percentage(1 - stats.winrate)})\n\n"
        
        streak = "STREAK\n"
        streak += f"Streak corrente: {stats.current_streak} vittorie\n"
        streak += f"Streak massimo: {stats.longest_streak} vittorie consecutive\n\n"
        
        time_stats = "TEMPO\n"
        time_stats += f"Tempo totale giocato: {self.format_duration(stats.total_playtime)}\n"
        time_stats += f"Tempo medio per partita: {self.format_duration(stats.average_game_time)}\n\n"
        
        records = "RECORD PERSONALI\n"
        if stats.fastest_victory < float('inf'):
            records += f"🏆 Vittoria più veloce: {self.format_duration(stats.fastest_victory)}\n"
        if stats.slowest_victory > 0:
            records += f"🏆 Vittoria più lenta: {self.format_duration(stats.slowest_victory)}\n"
        if stats.highest_score > 0:
            records += f"🏆 Punteggio massimo: {self.format_number(stats.highest_score)} punti\n"
        
        footer = f"\n{'─' * 56}\n"
        footer += "Pagina 1/3\n"
        footer += "PAGE DOWN - Pagina successiva\n"
        footer += "ESC - Torna a Gestione Profili"
        
        return header + performance + streak + time_stats + records + footer
```

**Test Coverage** (extend `test_stats_formatter.py`):

```python
from src.domain.models.statistics import GlobalStats

class TestGlobalStatsFormatting:
    def test_format_global_stats_summary(self):
        stats = GlobalStats(
            total_games=42,
            total_victories=28,
            total_defeats=14,
            winrate=0.6667
        )
        formatter = StatsFormatter()
        result = formatter.format_global_stats_summary(stats)
        
        assert "Vittorie totali: 28" in result
        assert "66,7%" in result
    
    def test_format_global_stats_detailed(self):
        stats = GlobalStats(
            total_games=42,
            total_victories=28,
            winrate=0.6667,
            current_streak=3,
            longest_streak=8,
            total_playtime=12300,  # 3h 25min
            fastest_victory=245.0,
            highest_score=1450
        )
        formatter = StatsFormatter()
        result = formatter.format_global_stats_detailed(stats, "Luca")
        
        assert "STATISTICHE PROFILO: Luca" in result
        assert "Partite totali: 42" in result
        assert "Streak corrente: 3" in result
        assert "Pagina 1/3" in result
```

**Commit Message**:
```
feat(presentation): Add global stats formatting methods

- format_global_stats_summary(): 2-line footer for victory dialog
- format_global_stats_detailed(): Full page 1 for detailed stats
- Includes: performance, streak, time, records
- Proper pagination footer (1/3)
- Tested: 2 test cases for global stats output

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 3.2 Page 1
```

**Estimated Time**: 15-20 min  
**Test Count**: 2

---

## 🏆 PHASE 2: Victory Dialog

### 🎯 Obiettivo

Creare dialog vittoria con statistiche integrate.

### 📝 Commit 2.1: Create Victory Dialog Essential

**File**: `src/presentation/dialogs/victory_dialog.py` (NEW)

```python
"""Victory dialog with integrated statistics."""

import wx
from typing import Dict

from src.domain.models.profile import SessionOutcome, EndReason
from src.presentation.formatters.stats_formatter import StatsFormatter


class VictoryDialog(wx.Dialog):
    """Victory end game dialog with stats summary.
    
    Shows:
    - Victory message
    - Time, moves, score (if enabled)
    - Timer info (if enabled + overtime warning)
    - Profile stats update (victories, winrate)
    - Record notifications
    
    Keyboard:
    - ENTER: New game
    - D: Detailed stats (future)
    - ESC: Main menu
    """
    
    def __init__(self, parent, outcome: SessionOutcome, profile_summary: Dict):
        super().__init__(
            parent,
            title="Vittoria!",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.outcome = outcome
        self.profile_summary = profile_summary
        self.formatter = StatsFormatter()
        
        self._create_ui()
        self._set_focus()
    
    def _create_ui(self) -> None:
        """Create dialog UI elements."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Victory header
        header = wx.StaticText(self, label="═" * 45)
        header_title = wx.StaticText(self, label="           VITTORIA!")
        header_bottom = wx.StaticText(self, label="═" * 45)
        
        font_header = header_title.GetFont()
        font_header.PointSize += 2
        font_header = font_header.Bold()
        header_title.SetFont(font_header)
        
        sizer.Add(header, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(header_title, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(header_bottom, 0, wx.ALL | wx.EXPAND, 5)
        
        # Stats content (TextCtrl readonly)
        content = self._build_content_text()
        self.stats_text = wx.TextCtrl(
            self,
            value=content,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(500, 300)
        )
        self.stats_text.SetName("Statistiche vittoria")
        sizer.Add(self.stats_text, 1, wx.ALL | wx.EXPAND, 10)
        
        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_new_game = wx.Button(self, wx.ID_OK, "Nuova Partita (INVIO)")
        self.btn_menu = wx.Button(self, wx.ID_CANCEL, "Menu Principale (ESC)")
        
        btn_sizer.Add(self.btn_new_game, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_menu, 0, wx.ALL, 5)
        
        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        self.SetSizer(sizer)
        self.Fit()
    
    def _build_content_text(self) -> str:
        """Build victory stats content text."""
        lines = []
        
        # Time and moves
        lines.append(f"Tempo: {self.formatter.format_duration(self.outcome.elapsed_time)}")
        lines.append(f"Mosse: {self.outcome.move_count}")
        lines.append(f"Ricicli tallone: {self.outcome.recycle_count}")
        lines.append("")
        
        # Timer info
        if self.outcome.timer_enabled:
            if self.outcome.end_reason == EndReason.VICTORY_OVERTIME:
                lines.append(f"⚠ Overtime: +{self.formatter.format_duration(self.outcome.overtime_duration)}")
                # Calculate penalty (100pt/min already applied)
                overtime_min = int(self.outcome.overtime_duration / 60) + 1
                penalty = overtime_min * 100
                lines.append(f"  Penalità punteggio: -{penalty} punti")
            else:
                lines.append(f"✓ Completato entro il limite ({self.formatter.format_time_mm_ss(self.outcome.timer_limit)})")
            lines.append("")
        
        # Scoring
        if self.outcome.scoring_enabled:
            lines.append(f"Punteggio: {self.formatter.format_number(self.outcome.final_score)} punti")
            quality_label = self._get_quality_label(self.outcome.quality_multiplier)
            lines.append(f"Qualità vittoria: {quality_label} (x{self.outcome.quality_multiplier:.1f})")
            lines.append("")
        
        # Profile stats
        lines.append("[STATISTICHE PROFILO - Aggiornate]")
        lines.append(f"Vittorie totali: {self.profile_summary['total_victories']}")
        lines.append(f"Winrate: {self.formatter.format_percentage(self.profile_summary['winrate'])}")
        lines.append("")
        
        # Record notification
        if self.profile_summary.get('new_record'):
            lines.append("🏆 NUOVO RECORD: Vittoria più veloce!")
            if 'previous_record' in self.profile_summary:
                prev = self.formatter.format_duration(self.profile_summary['previous_record'])
                lines.append(f"  Precedente: {prev}")
        
        return "\n".join(lines)
    
    def _get_quality_label(self, quality: float) -> str:
        """Get quality label from multiplier."""
        if quality >= 1.8:
            return "Eccellente"
        elif quality >= 1.4:
            return "Buona"
        else:
            return "Media"
    
    def _set_focus(self) -> None:
        """Set initial focus and TTS announcement."""
        self.stats_text.SetFocus()
        
        # TTS announcement (via accessible name)
        elapsed = self.formatter.format_duration(self.outcome.elapsed_time)
        score_part = ""
        if self.outcome.scoring_enabled:
            score_part = f" Punteggio: {self.outcome.final_score} punti."
        
        announcement = (
            f"Vittoria! Completato in {elapsed} con {self.outcome.move_count} mosse."
            f"{score_part} Vittorie totali: {self.profile_summary['total_victories']}."
        )
        
        if self.profile_summary.get('new_record'):
            announcement += " Nuovo record personale: vittoria più veloce!"
        
        self.SetName(announcement)
```

**Manual Test** (`tests/manual/NVDA_TEST_CHECKLIST.md`):

```markdown
## Victory Dialog

- [ ] Dialog opens with focus on stats text
- [ ] NVDA announces victory summary on open
- [ ] Arrow keys navigate through stats lines
- [ ] Tab navigates to buttons
- [ ] ENTER triggers "Nuova Partita"
- [ ] ESC closes dialog
- [ ] Record notification announced if present
- [ ] Overtime warning clear if present
```

**Commit Message**:
```
feat(presentation): Create victory dialog with stats integration

- Essential victory info: time, moves, score, timer status
- Profile stats footer: victories, winrate
- Overtime warning for VICTORY_OVERTIME
- Record notification support (🏆 icon)
- Quality label: Eccellente/Buona/Media
- NVDA focus on stats text with TTS announcement
- Keyboard: ENTER (new game), ESC (menu)
- Manual test checklist included

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 2.2
```

**Estimated Time**: 25-35 min  
**Test Count**: Manual checklist (7 items)

**✅ Checkpoint**: Spunta Phase 2 dopo questo commit.

---

## ❌ PHASE 3: Abandon Dialog

### 📝 Commit 3.1: Create Abandon Dialog

**File**: `src/presentation/dialogs/abandon_dialog.py` (NEW)

**Note**: Simile a VictoryDialog ma con contenuto diverso. Codice completo nel commit, qui solo diff principali:

**Key Differences**:
- Header: "PARTITA ABBANDONATA" invece di "VITTORIA!"
- Content: Mostra progressione (carte in fondazione %), motivo abbandono
- No scoring details (partita non finita)
- Footer: Sconfitte totali, winrate updated, streak interrotto

**Commit Message**:
```
feat(presentation): Create abandon dialog

- Minimalist layout: time played, moves, progression %
- EndReason display (abbandono volontario, timeout, etc.)
- Impact on stats: winrate, streak interrupted
- Profile stats footer updated
- NVDA focus with appropriate announcement
- Keyboard: ENTER (new game), ESC (menu)

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 2.3
```

**Estimated Time**: 20-30 min  
**Test Count**: Manual checklist (6 items)

---

## ℹ️ PHASE 4: Current Game Info Dialog

### 📝 Commit 4.1: Create Game Info Dialog (Tasto I)

**File**: `src/presentation/dialogs/game_info_dialog.py` (NEW)

**Features**:
- Tempo trascorso + timer rimanente (se attivo)
- Mosse, pescate, ricicli
- Fondazioni: totale + breakdown per seme
- Punteggio provvisorio (se scoring enabled)
- Read-only, no actions (solo ESC per chiudere)

**Commit Message**:
```
feat(presentation): Create current game info dialog (tasto I)

- Triggered by 'I' key during gameplay
- Shows: time, timer remaining, moves, foundations breakdown
- Provisional score if scoring enabled
- Read-only info dialog (ESC to close)
- NVDA announces key stats on open
- Foundation cards per suit (4 suits breakdown)

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 2.1
```

**Estimated Time**: 15-25 min  
**Test Count**: Manual checklist (5 items)

**✅ Checkpoint**: Spunta Phase 4 dopo commit.

---

## 📈 PHASE 5: Detailed Stats (3 Pagine)

### 📝 Commit 5.1: Create Detailed Stats Dialog Page 1 (Global)

**File**: `src/presentation/dialogs/detailed_stats_dialog.py` (NEW)

**Structure**:
- wx.TextCtrl multiline readonly
- 3 pages stored in `self.pages: List[str]`
- Current page: `self.current_page: int`
- Keyboard: Arrow UP/DOWN (scroll), PageUp/PageDown (change page), ESC (close)

**Page 1 Content** (usa `StatsFormatter.format_global_stats_detailed()`):
- Performance globale
- Streak corrente/massimo
- Tempo totale/medio
- Record personali

**Commit Message**:
```
feat(presentation): Create detailed stats dialog with Page 1

- Multi-page dialog structure (3 pages total)
- Page 1: Global stats (performance, streak, time, records)
- TextCtrl readonly with scroll support
- Keyboard: PageDown (next), Arrow keys (scroll lines)
- NVDA announces page number on change
- Uses StatsFormatter.format_global_stats_detailed()

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 3.2 Page 1
```

**Estimated Time**: 20-30 min  
**Test Count**: Manual checklist (8 items)

---

### 📝 Commit 5.2: Add Detailed Stats Page 2 (Timer Performance)

**File**: `src/presentation/formatters/stats_formatter.py` (ADD METHOD)

**New Method**:
```python
def format_timer_stats_detailed(self, stats: TimerStats) -> str:
    """Format Page 2: Timer performance analytics."""
    # Header
    # Partite con timer attivo
    # Breakdown: within time, overtime, timeout
    # Overtime analytics (avg, max)
    # Breakdown per modalità (STRICT/PERMISSIVE)
    # Footer: Pagina 2/3
```

**File**: `src/presentation/dialogs/detailed_stats_dialog.py` (MODIFIED)

**Add**:
- `self.pages[1] = formatter.format_timer_stats_detailed(timer_stats)`

**Commit Message**:
```
feat(presentation): Add detailed stats Page 2 (timer performance)

- Timer analytics: within time, overtime, timeout breakdown
- Overtime statistics (avg, max)
- Performance by mode (STRICT vs PERMISSIVE)
- Efficiency time vs limit
- Integrated into detailed stats dialog page navigation

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 3.2 Page 2
```

**Estimated Time**: 18-25 min  
**Test Count**: 1 formatter test

---

### 📝 Commit 5.3: Add Detailed Stats Page 3 (Scoring + Difficulty)

**File**: `src/presentation/formatters/stats_formatter.py` (ADD METHOD)

**New Method**:
```python
def format_scoring_difficulty_stats(
    self,
    scoring_stats: ScoringStats,
    difficulty_stats: DifficultyStats
) -> str:
    """Format Page 3: Scoring + difficulty breakdown."""
    # Header
    # Scoring stats: avg, highest, quality distribution
    # Performance per difficulty (1-5 levels)
    #   - Partite, vittorie, winrate, avg score per level
    # Footer: Pagina 3/3, ESC per tornare
```

**Commit Message**:
```
feat(presentation): Add detailed stats Page 3 (scoring + difficulty)

- Scoring analytics: avg, highest, quality distribution
- Performance breakdown by difficulty level (1-5)
- Per-level stats: games, victories, winrate, avg score
- Complete 3-page detailed stats navigation
- Page 3 footer indicates last page

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 3.2 Page 3
```

**Estimated Time**: 20-28 min  
**Test Count**: 1 formatter test

**✅ Checkpoint**: Spunta Phase 5 dopo commit 5.3.

---

## 🏅 PHASE 6: Leaderboard UI

### 📝 Commit 6.1: Create Leaderboard Main Dialog

**File**: `src/presentation/dialogs/leaderboard_dialog.py` (NEW)

**Features**:
- Calcola on-demand (scan all profiles)
- 5 classifiche: Winrate, Vittorie Totali, Record Tempo, Record Punteggio, Streak Massimo
- Evidenzia profilo corrente con `← TU`
- TextCtrl readonly multiline
- Keyboard: Arrow keys (scroll), F (filter difficulty - future), ESC (close)

**Logic**:
```python
def _calculate_leaderboard(self, metric: str) -> List[Dict]:
    """Calculate leaderboard for specific metric.
    
    Args:
        metric: "winrate" | "victories" | "fastest_time" | "highest_score" | "streak"
    
    Returns:
        Sorted list (top 10) with profile_name, value
    """
    # Load all profiles from ProfileService
    # Filter out guest
    # Extract metric from each profile
    # Sort descending
    # Return top 10
```

**Commit Message**:
```
feat(presentation): Create global leaderboard dialog

- 5 leaderboards: winrate, victories, fastest time, score, streak
- On-demand calculation (scan profiles on open)
- Current profile highlighted with "← TU"
- Guest profile excluded
- Scroll keyboard navigation
- Top 10 ranking per metric
- Uses ProfileService to load all profiles

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 4.2
```

**Estimated Time**: 30-40 min  
**Test Count**: Manual checklist (6 items) + 1 unit test for calc logic

**✅ Checkpoint**: Spunta Phase 6 dopo commit.

---

## 🔗 PHASE 7: GameEngine Integration

### 📝 Commit 7.1: Integrate Victory/Abandon Dialogs in end_game()

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:
```python
from src.presentation.dialogs.victory_dialog import VictoryDialog
from src.presentation.dialogs.abandon_dialog import AbandonDialog

def end_game(self, end_reason: EndReason) -> None:
    # ... existing timer stop, session outcome build ...
    
    # Record session (ProfileService)
    self.profile_service.record_session(self.current_session_outcome)
    
    # Get updated profile summary
    profile_summary = {
        'total_victories': self.profile_service.global_stats.total_victories,
        'winrate': self.profile_service.global_stats.winrate,
        'new_record': self._check_new_record(self.current_session_outcome),
        # ... other summary fields ...
    }
    
    # Show appropriate dialog
    if end_reason.is_victory():
        dialog = VictoryDialog(self.parent, self.current_session_outcome, profile_summary)
    else:
        dialog = AbandonDialog(self.parent, self.current_session_outcome, profile_summary)
    
    result = dialog.ShowModal()
    dialog.Destroy()
    
    if result == wx.ID_OK:
        # User chose "Nuova Partita"
        self.new_game()
    else:
        # User chose "Menu Principale" (ESC)
        self.show_main_menu()

def _check_new_record(self, outcome: SessionOutcome) -> bool:
    """Check if outcome beats personal record."""
    if not outcome.is_victory:
        return False
    
    prev_fastest = self.profile_service.global_stats.fastest_victory
    return outcome.elapsed_time < prev_fastest
```

**Commit Message**:
```
feat(game-engine): Integrate victory/abandon dialogs in end_game()

- Replace old end game dialog with new stats-integrated dialogs
- Victory: VictoryDialog with profile summary
- Defeat: AbandonDialog with end reason
- Record detection: _check_new_record() helper
- Profile summary built from ProfileService.global_stats
- Dialog result handling: OK=new game, CANCEL=menu

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 6.1
```

**Estimated Time**: 15-25 min  
**Test Count**: 2 integration tests

---

### 📝 Commit 7.2: Add Game Info Dialog Hook (Tasto I)

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:
```python
from src.presentation.dialogs.game_info_dialog import GameInfoDialog

def _setup_key_bindings(self):
    # ... existing bindings ...
    
    # Tasto I: Info partita corrente
    self.Bind(wx.EVT_CHAR_HOOK, self._on_key_press)

def _on_key_press(self, event: wx.KeyEvent):
    key = event.GetKeyCode()
    
    if key == ord('I') or key == ord('i'):
        if self.game_active:  # Solo durante partita
            self._show_game_info()
        return
    
    event.Skip()

def _show_game_info(self):
    """Show current game info dialog (tasto I)."""
    # Build current game data
    game_data = {
        'elapsed_time': self.game_service.get_elapsed_time(),
        'timer_config': {
            'enabled': self.game_settings.max_time_game > 0,
            'limit': self.game_settings.max_time_game,
            'remaining': self._get_timer_remaining()
        },
        'move_count': self.game_service.move_count,
        'foundation_cards': sum(self.game_service.carte_per_seme),
        'foundation_breakdown': list(self.game_service.carte_per_seme),
        'recycle_count': self.game_service.recycle_count,
        'provisional_score': self._get_provisional_score() if self.game_settings.scoring_enabled else None
    }
    
    dialog = GameInfoDialog(self.parent, game_data)
    dialog.ShowModal()
    dialog.Destroy()

def _get_timer_remaining(self) -> float:
    """Get timer remaining seconds."""
    if self.game_settings.max_time_game <= 0:
        return 0.0
    elapsed = self.game_service.get_elapsed_time()
    return max(0.0, self.game_settings.max_time_game - elapsed)
```

**Commit Message**:
```
feat(game-engine): Add game info dialog hook (tasto I)

- Bind 'I' key during gameplay
- Show GameInfoDialog with current game data
- Data: elapsed, timer remaining, moves, foundations, score
- Provisional score calculation if scoring enabled
- Only active during game (not in menu)
- Timer remaining helper method

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 2.1
```

**Estimated Time**: 12-18 min  
**Test Count**: 1 integration test

**✅ Checkpoint**: Spunta Phase 7 dopo commit 7.2.

---

## 🎧 PHASE 8: NVDA Accessibility Polish

### 📝 Commit 8.1: Polish Dialog Accessibility

**Files**: All dialogs (victory, abandon, game_info, detailed_stats, leaderboard)

**Changes**:
1. **Focus Management**:
   - Ogni dialog setta focus su elemento principale (non label)
   - `SetFocus()` chiamato dopo UI creation

2. **Accessible Names**:
   - `SetName()` su tutti i TextCtrl con contenuto significativo
   - Button labels include shortcut ("Nuova Partita (INVIO)")

3. **Help Text**:
   - Pulsanti disabilitati hanno `SetHelpText()` che spiega perché

4. **Tab Order**:
   - Verificato ordine logico (top-to-bottom)
   - Controlli decorativi esclusi

**Commit Message**:
```
feat(presentation): Polish NVDA accessibility for all dialogs

- Focus management: SetFocus() on main content element
- Accessible names: SetName() with meaningful labels
- Help text: SetHelpText() for disabled buttons
- Tab order: Logical navigation (top-to-bottom)
- Button labels include keyboard shortcuts
- No redundant announcements (skip decorative elements)

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 5
```

**Estimated Time**: 20-30 min  
**Test Count**: Manual NVDA checklist update (all dialogs)

**✅ Checkpoint**: Spunta Phase 8 dopo commit.

---

## 📋 PHASE 9: Menu Integration

### 📝 Commit 9.1: Add "Ultima Partita" Menu Option

**File**: `src/application/game_engine.py` (MODIFIED)

**Changes**:
```python
class GameEngine:
    def __init__(self):
        # ... existing init ...
        self.last_session_outcome: Optional[SessionOutcome] = None
    
    def end_game(self, end_reason: EndReason):
        # ... existing end game logic ...
        
        # Store last session for "Ultima Partita" menu
        self.last_session_outcome = self.current_session_outcome
        
        # ... show dialog ...
    
    def show_last_game_summary(self):
        """Show last game summary ("Ultima Partita" menu option)."""
        if self.last_session_outcome is None:
            wx.MessageBox(
                "Nessuna partita recente disponibile.",
                "Ultima Partita",
                wx.OK | wx.ICON_INFORMATION
            )
            return
        
        # Show simplified summary dialog
        from src.presentation.dialogs.last_game_dialog import LastGameDialog
        dialog = LastGameDialog(self.parent, self.last_session_outcome)
        dialog.ShowModal()
        dialog.Destroy()
```

**File**: `src/presentation/dialogs/last_game_dialog.py` (NEW)

**Simple read-only dialog**:
- Data/ora partita
- Esito (vittoria/abbandono)
- Tempo, mosse, punteggio
- Difficoltà, mazzo, timer
- Solo ESC per chiudere

**Menu Integration** (main menu):
```python
def _build_main_menu(self):
    menu_items = [
        "N - Nuova Partita",
        "U - Ultima Partita (risultati)",  # NEW
        "O - Opzioni",
        # ...
    ]
```

**Commit Message**:
```
feat(presentation): Add "Ultima Partita" menu option

- Store last_session_outcome in GameEngine
- LastGameDialog: Simple read-only summary
- Shows: date, outcome, time, moves, score, config
- Menu integration: "U" key in main menu
- Persists until new game started
- Message if no recent game available

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 2.4
```

**Estimated Time**: 15-22 min  
**Test Count**: Manual test

---

### 📝 Commit 9.2: Add Leaderboard Menu Option

**File**: Main menu (wherever it's defined)

**Changes**:
```python
menu_items = [
    "N - Nuova Partita",
    "U - Ultima Partita",
    "O - Opzioni",
    "P - Gestione Profili",
    "L - Leaderboard Globale",  # NEW
    "G - Gioca come Ospite",
    "E - Esci"
]

def _handle_menu_selection(self, key):
    if key == 'L' or key == 'l':
        self._show_leaderboard()
```

**Commit Message**:
```
feat(presentation): Add leaderboard to main menu

- Menu option "L": Leaderboard Globale
- Opens LeaderboardDialog with 5 rankings
- Available from main menu (not during game)
- Returns to menu on ESC

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 4.1
```

**Estimated Time**: 8-12 min  
**Test Count**: Manual test

---

### 📝 Commit 9.3: Add Detailed Stats to Profile Management Menu

**File**: Profile management menu (wherever defined)

**Changes**:
```python
profile_menu_items = [
    "1. Cambia Profilo",
    "2. Crea Nuovo Profilo",
    "3. Rinomina Profilo Corrente",
    "4. Elimina Profilo",
    "5. Statistiche Dettagliate",  # ALREADY EXISTS, just wire it
    # ...
]

def _handle_profile_menu(self, choice):
    if choice == 5:
        self._show_detailed_stats()

def _show_detailed_stats(self):
    """Show detailed stats dialog (3 pages)."""
    from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
    
    # Load stats from active profile
    stats_data = {
        'profile_name': self.profile_service.active_profile.profile_name,
        'global_stats': self.profile_service.global_stats,
        'timer_stats': self.profile_service.timer_stats,
        'difficulty_stats': self.profile_service.difficulty_stats,
        'scoring_stats': self.profile_service.scoring_stats
    }
    
    dialog = DetailedStatsDialog(self.parent, stats_data)
    dialog.ShowModal()
    dialog.Destroy()
```

**Commit Message**:
```
feat(presentation): Wire detailed stats to profile management menu

- Option 5 in profile menu opens DetailedStatsDialog
- Loads current profile stats from ProfileService
- 3-page navigation (global, timer, scoring/difficulty)
- Returns to profile menu on ESC

Refs: DESIGN_STATISTICS_PRESENTATION.md Section 3.1
```

**Estimated Time**: 10-15 min  
**Test Count**: Manual test

**✅ Checkpoint**: Spunta Phase 9 dopo commit 9.3. **Stats Presentation v3.0.0 completa!**

---

## ✅ Final Validation Checklist

**Copilot: Esegui questi check prima di dichiarare feature completa**

### Code Quality

- [ ] Tutti i commit seguono Conventional Commits format
- [ ] Nessun hardcoded magic number (use constants)
- [ ] Typing completo (no `Any` type hints)
- [ ] Docstring su tutti i dialog/formatter pubblici
- [ ] Italian text review (no typos, proper plurals)

### Testing

- [ ] Formatter unit tests passano (15+ tests)
- [ ] Manual NVDA checklist completata (30+ items)
- [ ] Dialogs aprono correttamente (no crash)
- [ ] Navigation keyboard funziona (arrow, tab, page)
- [ ] TTS announcements non ridondanti

### Functionality

- [ ] Victory dialog mostra stats aggiornate
- [ ] Abandon dialog mostra motivo corretto
- [ ] Game info dialog mostra dati correnti
- [ ] Detailed stats 3 pagine navigabili
- [ ] Leaderboard calcola ranking correttamente
- [ ] Menu options "U" e "L" funzionano
- [ ] Profile management "5" apre stats

### Accessibility

- [ ] Focus iniziale corretto su tutti i dialog
- [ ] Tab order logico
- [ ] ESC chiude tutti i dialog
- [ ] Pulsanti con shortcuts labeled
- [ ] Help text su disabled buttons
- [ ] Nessun spam TTS (decorative elements skipped)

### Documentation

- [ ] CHANGELOG.md aggiornato con v3.0.0 UI features
- [ ] Questo file aggiornato con check spuntati
- [ ] NVDA_TEST_CHECKLIST.md completo (30+ items)
- [ ] Screenshots/video demo (opzionale)

---

## 📊 Commit Summary (Final)

| Phase | Commits | Description | Time | Tests |
|---|---|---|---|---|
| **1** | 1.1, 1.2 | StatsFormatter base + global | 27-38 min | 9 |
| **2** | 2.1 | Victory dialog | 25-35 min | Manual |
| **3** | 3.1 | Abandon dialog | 20-30 min | Manual |
| **4** | 4.1 | Game info dialog | 15-25 min | Manual |
| **5** | 5.1-5.3 | Detailed stats 3 pages | 58-83 min | 2 + Manual |
| **6** | 6.1 | Leaderboard | 30-40 min | 1 + Manual |
| **7** | 7.1, 7.2 | GameEngine integration | 27-43 min | 3 |
| **8** | 8.1 | NVDA accessibility polish | 20-30 min | Manual |
| **9** | 9.1-9.3 | Menu integration | 33-49 min | Manual |
| **TOTAL** | **12-15 commits** | | **255-373 min** | **15 unit + 30+ manual** |

**Realistic Estimate**: GitHub Copilot Agent completes Stats Presentation in **2-3 hours** (iterative, manual tests in between).

---

## 🎯 Implementation Order Summary

**Sequenza completa per Copilot**:

```
1. Timer System v2.7.0 (45-70 min)
   └─ EndReason enum + timer logic
   
2. Profile System v3.0.0 Backend (2-2.5 ore)
   └─ Data models + storage + ProfileService
   
3. Stats Presentation v3.0.0 Frontend (2-3 ore)
   └─ Dialogs + formatters + menu integration
```

**Totale**: ~5-6 ore agent time per feature stack completo.

---

## 🔗 Known Limitations

### Dialog Design

**Limitation**: Dialogs sono text-based (wx.TextCtrl readonly). No fancy tables/grids.

**Rationale**: Screen-reader friendly. Grid navigation complessa per NVDA.

**Future**: v3.1+ potrebbe aggiungere grafici (se accessibili con NVDA).

### Leaderboard Calculation

**Limitation**: On-demand calculation (scan all profiles ogni volta).

**Impact**: Con 50+ profili, latenza 100-200ms all'apertura.

**Future**: v3.1 cache leaderboard (invalidate on profile update).

### Manual Testing

**Limitation**: UI testing è manuale (no automated tests).

**Rationale**: wxPython UI automation complessa. NVDA testing richiede human.

**Mitigation**: Checklist dettagliata per ogni dialog.

---

## 📚 Riferimenti

- **Design Doc**: [DESIGN_STATISTICS_PRESENTATION.md](../2%20-%20projects/DESIGN_STATISTICS_PRESENTATION.md)
- **Profile System**: [DESIGN_PROFILE_STATISTICS_SYSTEM.md](../2%20-%20projects/DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Timer System**: [DESIGN_TIMER_MODE_SYSTEM.md](../2%20-%20projects/DESIGN_TIMER_MODE_SYSTEM.md)
- **Profile Implementation**: [IMPLEMENTATION_PROFILE_SYSTEM.md](IMPLEMENTATION_PROFILE_SYSTEM.md)
- **Timer Implementation**: [IMPLEMENTATION_TIMER_SYSTEM.md](IMPLEMENTATION_TIMER_SYSTEM.md)
- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)

---

**Documento creato**: 17 Febbraio 2026, 14:00 CET  
**Autore**: Luca (utente) + Perplexity AI (technical planning)  
**Status**: **Ready for Copilot Agent execution** ✅  
**Estimated Completion**: 2-3 hours agent time (manual tests in between commits)
