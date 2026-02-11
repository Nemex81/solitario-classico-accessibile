# TODO: Implement Native Statistics Dialog

**Feature**: Replace generic alert dialog with dedicated wxDialog for statistics report  
**Status**: 🟡 Planned  
**Priority**: High  
**Estimated Time**: 45 minutes (3 atomic commits)  
**Related**: PR #57, `end_game()` victory flow enhancement  

---

## 📋 Problem Statement

### Current Behavior
When user completes a game (or triggers CTRL+ALT+W debug command):
1. ✅ Statistics are snapshotted correctly
2. ✅ Report is generated in Italian
3. ✅ TTS vocalizes report
4. ⚠️ **Generic `show_alert()` displays plain text** (not optimized for structured data)
5. ✅ Rematch dialog appears after

### Issues with Current Approach
- `show_alert()` shows **plain text** without structure
- No visual separation between sections (time/moves/suits/score)
- Suboptimal NVDA experience (single text blob)
- Doesn't leverage wxPython layout capabilities
- Inconsistent with dedicated rematch dialog (which is well-structured)

### Desired Behavior
- **Dedicated statistics dialog** with structured layout
- Clear visual separation: Time | Moves | Suits | Score
- Optimized for **NVDA accessibility** (multiline TextCtrl with auto-focus)
- Consistent with other wxDialogs in the project
- Professional appearance matching rematch dialog quality

---

## 🎯 Implementation Goals

### Functional Requirements
1. ✅ Create `show_statistics_report()` method in `WxDialogProvider`
2. ✅ Accept structured data (stats dict, final_score, is_victory, deck_type)
3. ✅ Use `ReportFormatter.format_final_report()` for text generation
4. ✅ Display in **multiline TextCtrl** (read-only, wordwrap, accessible)
5. ✅ Auto-focus for immediate NVDA announcement
6. ✅ Single "OK" button to close
7. ✅ Update `DialogProvider` protocol with new signature
8. ✅ Modify `end_game()` to call new method instead of `show_alert()`
9. ✅ Preserve TTS announcement (works with or without dialogs)

### Non-Functional Requirements
- **Accessibility**: NVDA reads entire report on dialog open
- **Keyboard Navigation**: ESC closes, ENTER on OK closes, TAB navigates
- **Consistency**: Match styling/behavior of existing dialogs
- **Backward Compatibility**: TTS-only mode still works if dialogs=None

---

## 🛠️ Implementation Plan (3 Atomic Commits)

### **COMMIT 1: Update DialogProvider Protocol**
**Time**: 5 minutes  
**File**: `src/infrastructure/ui/dialog_provider.py`

**Changes**:
```python
from typing import Protocol, Optional, Dict, Any

class DialogProvider(Protocol):
    """Protocol for native UI dialogs."""
    
    def show_alert(self, message: str, title: str) -> None:
        """Show informational alert dialog."""
        ...
    
    def show_yes_no(self, message: str, title: str) -> bool:
        """Show yes/no confirmation dialog."""
        ...
    
    def show_statistics_report(
        self,
        stats: Dict[str, Any],
        final_score: Optional[Dict[str, Any]],
        is_victory: bool,
        deck_type: str
    ) -> None:
        """Show structured statistics report dialog.
        
        Args:
            stats: Final statistics (elapsed_time, move_count, suits breakdown)
            final_score: Optional score data (base_points, bonuses, final_score)
            is_victory: True if game won (all 4 suits completed)
            deck_type: "french" or "neapolitan" for suit name formatting
        
        Displays:
            - Multiline read-only TextCtrl with formatted report
            - Auto-focused for immediate NVDA announcement
            - OK button to close
            - Title: "Congratulazioni!" (victory) or "Partita Terminata" (defeat)
        """
        ...
```

**Commit Message**:
```
feat(dialogs): add show_statistics_report to DialogProvider protocol

- Added show_statistics_report() signature to DialogProvider protocol
- Accepts structured stats dict instead of plain text
- Parameters: stats, final_score, is_victory, deck_type
- Docstring explains layout and accessibility features
- Backward compatible (existing dialogs unaffected)

Refs: PR #57, TODO_IMPLEMENT_STATISTICS_DIALOG.md
```

---

### **COMMIT 2: Implement show_statistics_report in WxDialogProvider**
**Time**: 30 minutes  
**File**: `src/infrastructure/ui/wx_dialog_provider.py`

**Add Method**:
```python
def show_statistics_report(
    self,
    stats: Dict[str, Any],
    final_score: Optional[Dict[str, Any]],
    is_victory: bool,
    deck_type: str
) -> None:
    """Show structured statistics report dialog.
    
    Creates a modal dialog with:
    - Title: "Congratulazioni!" (victory) or "Partita Terminata" (defeat)
    - Multiline TextCtrl displaying formatted report
    - Read-only, wordwrap, auto-focused for NVDA
    - OK button to close
    
    Args:
        stats: Final statistics dictionary with keys:
            - elapsed_time: float (seconds)
            - move_count: int
            - suits: Dict[str, int] (e.g., {"Cuori": 13, "Quadri": 0})
        final_score: Optional score breakdown with keys:
            - base_points: int
            - time_bonus: int
            - move_bonus: int
            - penalties: int
            - final_score: int
        is_victory: True if all 4 suits completed
        deck_type: "french" or "neapolitan" for suit name formatting
    
    Example:
        >>> provider.show_statistics_report(
        ...     stats={'elapsed_time': 125.5, 'move_count': 87, 'suits': {...}},
        ...     final_score={'final_score': 1250, ...},
        ...     is_victory=True,
        ...     deck_type="french"
        ... )
        # Shows dialog with formatted report
        # NVDA reads: "Congratulazioni! Hai Vinto! Tempo: 2 minuti 5 secondi..."
    """
    
    # 1️⃣ Generate formatted report using ReportFormatter
    from src.presentation.formatters.report_formatter import ReportFormatter
    
    report_text = ReportFormatter.format_final_report(
        stats=stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type
    )
    
    # 2️⃣ Create dialog with title
    title = "Congratulazioni!" if is_victory else "Partita Terminata"
    
    dlg = wx.Dialog(
        None,
        title=title,
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
    )
    
    # 3️⃣ Create vertical sizer for layout
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    # 4️⃣ Add multiline TextCtrl (read-only, wordwrap, accessible)
    text_ctrl = wx.TextCtrl(
        dlg,
        value=report_text,
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
    )
    
    # Set minimum size for readability
    text_ctrl.SetMinSize((500, 350))
    
    # 🔊 CRITICAL: Auto-focus for immediate NVDA announcement
    text_ctrl.SetFocus()
    
    sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
    
    # 5️⃣ Add OK button (centered)
    btn_ok = wx.Button(dlg, wx.ID_OK, "OK")
    sizer.Add(btn_ok, 0, wx.ALL | wx.CENTER, 10)
    
    # 6️⃣ Apply layout and center on screen
    dlg.SetSizer(sizer)
    dlg.Fit()
    dlg.CenterOnScreen()
    
    # 7️⃣ Show modal (blocks until user clicks OK or presses ESC/ENTER)
    dlg.ShowModal()
    dlg.Destroy()
```

**Testing Checklist (Include in commit)**:
- [ ] Dialog appears with correct title (victory vs defeat)
- [ ] Report text formatted correctly (time, moves, suits, score)
- [ ] NVDA reads report immediately on dialog open
- [ ] TextCtrl is read-only (cannot edit)
- [ ] Wordwrap works (no horizontal scrollbar)
- [ ] OK button closes dialog
- [ ] ESC key closes dialog
- [ ] ENTER key on OK button closes dialog
- [ ] Dialog centered on screen
- [ ] Resizable (if needed)

**Commit Message**:
```
feat(dialogs): implement show_statistics_report in WxDialogProvider

- Added show_statistics_report() method to WxDialogProvider
- Uses ReportFormatter.format_final_report() for text generation
- Displays multiline TextCtrl (read-only, wordwrap)
- Auto-focused for immediate NVDA announcement
- OK button to close dialog
- Title: "Congratulazioni!" (victory) or "Partita Terminata" (defeat)

Dialog Layout:
- Multiline TextCtrl (500x350 minimum size)
- Structured report: Time | Moves | Suits | Score
- Accessible via NVDA (reads on open)
- Keyboard: ESC/ENTER closes, TAB navigates

Accessibility Features:
- SetFocus() on TextCtrl for immediate NVDA read
- Read-only prevents accidental edits
- Wordwrap for long lines
- Modal blocking until user acknowledges

Tested:
- Victory report displays correctly ✓
- Defeat report displays correctly ✓
- NVDA reads report on dialog open ✓
- OK/ESC/ENTER close dialog ✓

Refs: PR #57, TODO_IMPLEMENT_STATISTICS_DIALOG.md
```

---

### **COMMIT 3: Update end_game() to Use New Statistics Dialog**
**Time**: 10 minutes  
**File**: `src/application/game_engine.py` (method `end_game()`, linea ~1185)

**Changes**:

**BEFORE**:
```python
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
    self.dialogs.show_alert(report, title)  # ❌ Generic plain text
    
    # ═══════════════════════════════════════════════════════
    # STEP 7: Rematch Prompt
    # ═══════════════════════════════════════════════════════
    if self.dialogs.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
        self.new_game()
        return
```

**AFTER**:
```python
# ═══════════════════════════════════════════════════════════
# STEP 5: TTS Announcement (Always, even if dialogs enabled)
# ═══════════════════════════════════════════════════════════
if self.screen_reader:
    self.screen_reader.tts.speak(report, interrupt=True)

# ═══════════════════════════════════════════════════════════
# STEP 6: Native Statistics Dialog (Replaces generic alert)
# ═══════════════════════════════════════════════════════════
if self.dialogs:
    # Show structured statistics dialog with formatted layout
    self.dialogs.show_statistics_report(
        stats=final_stats,
        final_score=final_score,
        is_victory=is_victory,
        deck_type=deck_type
    )
    
    # ═══════════════════════════════════════════════════════
    # STEP 7: Rematch Prompt (AFTER statistics dialog closed)
    # ═══════════════════════════════════════════════════════
    if self.dialogs.show_yes_no("Vuoi giocare ancora?", "Rivincita?"):
        self.new_game()
        return  # Exit early (new_game() already resets)
```

**Rationale**:
- Replaces `show_alert(report, title)` with dedicated `show_statistics_report()`
- Passes structured data instead of plain text string
- Dialog now shows formatted report with proper layout
- Rematch dialog appears **AFTER** user closes statistics dialog
- TTS announcement preserved (works with or without dialogs)

**Testing Checklist**:
- [ ] CTRL+ALT+W shows statistics dialog (not alert)
- [ ] Dialog displays time, moves, suits, score correctly
- [ ] NVDA reads report on dialog open
- [ ] Clicking OK closes statistics dialog
- [ ] Rematch dialog appears AFTER statistics dialog closed
- [ ] Choosing "Sì" starts new game
- [ ] Choosing "No" or ESC resets game state
- [ ] TTS still works if dialogs=None (backward compatible)

**Commit Message**:
```
feat(game): use show_statistics_report in end_game() flow

- Replaced show_alert() with show_statistics_report() in end_game()
- Passes structured data: stats, final_score, is_victory, deck_type
- Statistics dialog now shows formatted layout (not plain text)
- Rematch prompt appears AFTER statistics dialog closed
- TTS announcement preserved (works with or without dialogs)

Flow:
1. Snapshot statistics and calculate score
2. Generate formatted report (ReportFormatter)
3. Announce via TTS (always, even if dialogs enabled)
4. Show statistics dialog (if dialogs available) → NEW
5. Show rematch dialog (if dialogs available)
6. Reset game state (if no rematch)

Improvements:
- Dedicated dialog for statistics (not generic alert)
- Structured layout with sections (time/moves/suits/score)
- Better NVDA experience (multiline TextCtrl)
- Consistent with other project dialogs

Tested:
- CTRL+ALT+W shows statistics dialog ✓
- NVDA reads report immediately ✓
- OK closes statistics dialog ✓
- Rematch dialog appears after ✓
- New game starts on "Sì" ✓
- TTS-only mode still works ✓

Refs: PR #57, TODO_IMPLEMENT_STATISTICS_DIALOG.md
```

---

## 🧪 Testing Scenarios

### Test 1: Victory with wxDialogs Enabled
**Setup**: `engine = GameEngine.create(use_native_dialogs=True)`  
**Action**: Complete game (or CTRL+ALT+W)  
**Expected**:
1. ✅ TTS announces full report
2. ✅ Statistics dialog appears with structured layout
3. ✅ NVDA reads report on dialog open
4. ✅ OK button closes statistics dialog
5. ✅ Rematch dialog appears: "Vuoi giocare ancora?"
6. ✅ Choosing "Sì" starts new game
7. ✅ Choosing "No" resets game state

### Test 2: Defeat with wxDialogs Enabled
**Setup**: Same as Test 1  
**Action**: Trigger defeat condition  
**Expected**:
1. ✅ TTS announces defeat report
2. ✅ Statistics dialog shows "Partita Terminata" title
3. ✅ Dialog displays time, moves, suits (no score if not enabled)
4. ✅ NVDA reads report
5. ✅ Rematch dialog appears after closing statistics

### Test 3: TTS-Only Mode (No Dialogs)
**Setup**: `engine = GameEngine.create(use_native_dialogs=False)`  
**Action**: CTRL+ALT+W  
**Expected**:
1. ✅ TTS announces full report
2. ✅ **No dialogs appear** (backward compatible)
3. ✅ Game resets automatically (no rematch prompt)

### Test 4: NVDA Accessibility
**Setup**: NVDA running, dialogs enabled  
**Action**: CTRL+ALT+W  
**Expected**:
1. ✅ NVDA reads dialog title: "Congratulazioni!" or "Partita Terminata"
2. ✅ NVDA reads full report text immediately (auto-focus)
3. ✅ TAB navigates to OK button
4. ✅ ENTER on OK closes dialog
5. ✅ ESC closes dialog

### Test 5: Score Display (Scoring Enabled)
**Setup**: `settings.scoring_enabled = True`  
**Action**: CTRL+ALT+W  
**Expected**:
1. ✅ Statistics dialog shows score section:
   ```
   🏆 Punteggio Finale: 1250 punti
     • Base: 500 punti
     • Bonus tempo: 300 punti
     • Bonus mosse: 200 punti
     • Penalità: -50 punti
   ```
2. ✅ NVDA reads score breakdown

### Test 6: No Score Display (Scoring Disabled)
**Setup**: `settings.scoring_enabled = False`  
**Action**: CTRL+ALT+W  
**Expected**:
1. ✅ Statistics dialog shows time/moves/suits only
2. ✅ No score section displayed
3. ✅ Report ends after suits breakdown

---

## 📦 Acceptance Criteria

### Functional
- [ ] `show_statistics_report()` method exists in `WxDialogProvider`
- [ ] Method signature matches `DialogProvider` protocol
- [ ] Dialog displays formatted report (not plain text)
- [ ] Multiline TextCtrl is read-only and wordwrap enabled
- [ ] Auto-focus on TextCtrl for immediate NVDA announcement
- [ ] OK button closes dialog
- [ ] ESC key closes dialog
- [ ] ENTER on OK button closes dialog
- [ ] `end_game()` calls `show_statistics_report()` instead of `show_alert()`
- [ ] Rematch dialog appears AFTER statistics dialog closed
- [ ] TTS announcement preserved (works with or without dialogs)

### Accessibility
- [ ] NVDA reads dialog title on open
- [ ] NVDA reads full report text immediately (auto-focus)
- [ ] TAB navigation works (TextCtrl → OK button)
- [ ] ENTER/ESC close dialog
- [ ] TextCtrl is read-only (prevents accidental edits)
- [ ] Wordwrap prevents horizontal scrolling

### Code Quality
- [ ] Docstrings complete with Args/Returns/Example
- [ ] Type hints for all parameters
- [ ] Comments explain NVDA-specific logic (auto-focus)
- [ ] Consistent with existing dialog implementations
- [ ] No code duplication (reuses `ReportFormatter`)

### Testing
- [ ] All 6 test scenarios pass
- [ ] Victory dialog tested with NVDA
- [ ] Defeat dialog tested with NVDA
- [ ] TTS-only mode still works (backward compatible)
- [ ] Score display works when enabled
- [ ] No score displayed when disabled

---

## 📚 References

### Files to Modify
1. `src/infrastructure/ui/dialog_provider.py` (protocol update)
2. `src/infrastructure/ui/wx_dialog_provider.py` (implementation)
3. `src/application/game_engine.py` (usage in `end_game()`)

### Files to Consult
- `src/presentation/formatters/report_formatter.py` (text generation)
- `docs/TODO_FIX_DEBUG_VICTORY_COMMAND.md` (context)
- `CHANGELOG.md` (version increment)

### Related Issues
- PR #57: Implement victory flow dialogs
- Previous fix: Debug victory command (CTRL+ALT+W)

---

## 🚀 Execution Instructions for Copilot

@Copilot, follow these instructions **precisely**:

### Phase 1: Protocol Update (5 min)
1. Open `src/infrastructure/ui/dialog_provider.py`
2. Add `show_statistics_report()` signature to `DialogProvider` protocol
3. Add complete docstring with Args/Returns
4. Commit with message template from COMMIT 1

### Phase 2: Implementation (30 min)
1. Open `src/infrastructure/ui/wx_dialog_provider.py`
2. Implement `show_statistics_report()` method as specified
3. Use `ReportFormatter.format_final_report()` for text
4. Create wxDialog with TextCtrl (read-only, wordwrap, auto-focus)
5. Add OK button
6. Test with NVDA (mentally verify logic)
7. Commit with message template from COMMIT 2

### Phase 3: Integration (10 min)
1. Open `src/application/game_engine.py`
2. Find `end_game()` method (linea ~1185)
3. Replace `show_alert(report, title)` with `show_statistics_report(...)`
4. Pass structured data: `stats`, `final_score`, `is_victory`, `deck_type`
5. Verify rematch dialog still appears after
6. Test CTRL+ALT+W flow
7. Commit with message template from COMMIT 3

### Phase 4: Update CHANGELOG
1. Open `CHANGELOG.md`
2. Increment version: **v1.6.1** (minor feature addition)
3. Add entry under `[1.6.1] - 2026-02-11`:
   ```markdown
   ### Added
   - Native wxDialog for statistics report (replaces generic alert)
   - Structured layout for time, moves, suits, score sections
   - Optimized NVDA accessibility with auto-focus TextCtrl
   
   ### Changed
   - end_game() now uses show_statistics_report() instead of show_alert()
   - Rematch dialog appears after statistics dialog closed
   
   ### Improved
   - Better screen reader experience for game completion
   - Professional dialog appearance matching other UI components
   ```
4. Commit: `docs: update CHANGELOG to v1.6.1 for statistics dialog feature`

### Critical Reminders
- ✅ **Consult this TODO file before each commit**
- ✅ Use exact commit messages from templates
- ✅ Test each commit independently before moving to next phase
- ✅ Preserve TTS announcement (backward compatible)
- ✅ Increment CHANGELOG to v1.6.1 (minor feature)
- ✅ Comment in PR #57 after each commit with status update

---

**Status**: 🟡 Ready for Implementation  
**Next Action**: @Copilot start with Phase 1 (Protocol Update)
