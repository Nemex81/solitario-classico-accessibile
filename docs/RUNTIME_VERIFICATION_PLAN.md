# Runtime Verification Plan - Profile System v3.1.3

**Version:** v3.1.3.3  
**Date:** 2026-02-18  
**Status:** Ready for Execution

---

## Overview

This document provides step-by-step manual test procedures to verify the Profile System integration is working correctly in production-like conditions.

## Prerequisites

- Clean test environment
- NVDA screen reader installed (for accessibility tests)
- Access to `~/.solitario/profiles/` directory
- Ability to monitor log files in `./logs/`

---

## Test A: Clean Bootstrap (Guest Profile Creation)

**Objective:** Verify automatic guest profile creation on first launch

### Setup
```bash
# Backup existing profiles
mv ~/.solitario/profiles ~/.solitario/profiles.backup

# Start fresh
rm -rf ~/.solitario/profiles
```

### Execution Steps

1. Launch application
   ```bash
   python acs_wx.py
   ```

2. **Verify bootstrap in terminal:**
   - Look for: "Inizializzazione ProfileService..."
   - Look for: "✓ ProfileService pronto - Profilo attivo: Ospite"

3. **Start a new game** (press O or N)

4. **Play and win the game:**
   - Complete all 4 suits
   - Move all cards to foundation piles

5. **Verify VictoryDialog appears**

6. **Choose "Torna al Menu" (ESC key)**

### Expected Results

✅ **Profile File Created:**
```bash
ls -la ~/.solitario/profiles/profile_000.json
```
File should exist with recent timestamp

✅ **Profile Content:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.'
```

Should contain:
- `profile.profile_id`: "profile_000"
- `profile.profile_name`: "Ospite"
- `profile.is_guest`: true
- `stats.global.total_games`: 1
- `stats.global.total_victories`: 1
- `stats.global.winrate`: 1.0
- `recent_sessions`: array with 1 element
- Session has `end_reason`: "VICTORY"

✅ **Log File:**
```bash
tail -50 ./logs/solitario.log
```

Should show:
- ProfileService initialization
- Guest profile creation
- Session recording event

### Cleanup
```bash
# Restore backup if needed
rm -rf ~/.solitario/profiles
mv ~/.solitario/profiles.backup ~/.solitario/profiles
```

---

## Test B: Voluntary Abandon (ESC → Menu)

**Objective:** Verify abandon flow works without empty windows

### Setup
```bash
# Use existing profile or create fresh one
# Ensure profile_000.json exists
```

### Execution Steps

1. **Launch application**
   ```bash
   python acs_wx.py
   ```

2. **Start new game** (press N)

3. **Make 3-5 moves** (move some cards)

4. **Press ESC key**

5. **Confirm abandon** (select "Sì" in dialog)

### Expected Results

✅ **AbandonDialog appears** with:
- Game statistics displayed
- Two options: "Nuova Partita" / "Menu Principale"

✅ **Choose "Menu Principale" (ESC)**

✅ **Menu appears cleanly:**
- No empty window
- Main menu visible
- TTS announces: "Sei tornato al menu principale"

✅ **Session recorded:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions[-1]'
```

Should show:
- `end_reason`: "ABANDON_EXIT"
- `is_victory`: false
- `moves_count`: 3-5 (as played)
- Recent timestamp

✅ **Stats updated:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.stats.global'
```

Should show:
- `total_games`: increased by 1
- `total_victories`: unchanged
- `winrate`: recalculated

### Log Verification

```bash
tail -100 ./logs/solitario.log | grep -A 5 "abandon"
```

Should show:
- `[DEBUG _safe_abandon] INIZIO`
- `[DEBUG _safe_abandon] Chiamando end_game(ABANDON_EXIT)`
- `[DEBUG handle_game_ended] wants_rematch=False`
- `[DEBUG _safe_return_to_menu] Menu panel mostrato`

---

## Test C: Timer STRICT Timeout

**Objective:** Verify STRICT timeout handling and session recording

### Setup

1. **Configure STRICT timer:**
   - Open options (O key)
   - Set timer: 30 seconds
   - Set mode: STRICT
   - Save options

### Execution Steps

1. **Launch application**

2. **Start new game** (N key)

3. **Wait for timer to expire** (30 seconds)
   - Do NOT make any moves
   - Let timer reach 0:00

### Expected Results

✅ **Timeout announcement:**
- TTS announces: "Tempo scaduto! Partita terminata."

✅ **AbandonDialog appears** with:
- Title: "Tempo Scaduto!"
- Statistics shown
- Three options (with rematch option)

✅ **Choose "Torna al Menu"**

✅ **Session recorded:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions[-1]'
```

Should show:
- `end_reason`: "TIMEOUT_STRICT"
- `is_victory`: false
- `timer_enabled`: true
- `timer_limit`: 30
- `timer_mode`: "STRICT"
- `timer_expired`: true
- `overtime_duration`: 0

✅ **Stats updated:**
- Timer stats should show timeout recorded

### Log Verification

```bash
tail -100 ./logs/solitario.log | grep -i "timeout\|timer"
```

Should show:
- Timer expiry detection
- end_game(TIMEOUT_STRICT) called
- Callback flow executed

---

## Test D: Timer PERMISSIVE Overtime Victory

**Objective:** Verify PERMISSIVE mode allows overtime and records it correctly

### Setup

1. **Configure PERMISSIVE timer:**
   - Open options (O key)
   - Set timer: 30 seconds
   - Set mode: PERMISSIVE
   - Save options

### Execution Steps

1. **Launch application**

2. **Start new game** (N key)

3. **Wait for timer to expire** (30 seconds)

4. **Verify overtime announcement:**
   - TTS should announce: "Tempo scaduto! Continua in modalità overtime."

5. **Continue playing and complete the game:**
   - Win the game after timer expired

### Expected Results

✅ **VictoryDialog appears** (not timeout dialog)

✅ **Session recorded:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions[-1]'
```

Should show:
- `end_reason`: "VICTORY_OVERTIME"
- `is_victory`: true
- `timer_enabled`: true
- `timer_limit`: 30
- `timer_mode`: "PERMISSIVE"
- `timer_expired`: true
- `overtime_duration`: > 0 (time played after timeout)

✅ **Stats updated:**
- Victory counted
- Overtime stats recorded
- Winrate recalculated

### Log Verification

```bash
tail -100 ./logs/solitario.log | grep -i "overtime"
```

Should show:
- Overtime mode started
- Victory with overtime
- Correct end_reason

---

## Test E: Dirty Shutdown Recovery

**Objective:** Verify orphaned session recovery on app restart

### Setup
```bash
# Clean profile for clear testing
rm ~/.solitario/profiles/profile_000.json
```

### Execution Steps

1. **Launch application**

2. **Start new game** (N key)

3. **Make 5-10 moves**

4. **Force quit application** (without saving)
   ```bash
   # In another terminal:
   pkill -9 python
   ```
   Or close terminal window abruptly

5. **Restart application immediately**
   ```bash
   python acs_wx.py
   ```

### Expected Results

✅ **Recovery detected:**

Check log file:
```bash
tail -50 ./logs/solitario.log | grep -i "recovery\|orphan"
```

Should show recovery logic executed

✅ **Session file check:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions'
```

Should contain:
- Orphaned session entry (if recovery implemented)
- Or clean state (if recovery clears partial sessions)

✅ **App starts normally:**
- No crash
- Main menu appears
- Guest profile loaded

### Notes

- Recovery behavior depends on implementation
- May record partial session or clear it
- Should NOT crash on startup

---

## Test F: Multiple Profiles & Default Selection

**Objective:** Verify default profile selection works

### Execution Steps

1. **Create second profile:**
   - Menu → "Gestione Profili" (G key)
   - Create new profile "Test"

2. **Set as default:**
   - Select "Test" profile
   - Choose "Imposta come Predefinito"

3. **Restart application**

4. **Verify correct profile loaded:**
   - Check active profile name in UI
   - Should be "Test" not "Ospite"

### Expected Results

✅ **Default profile loaded:**
```bash
tail -20 ./logs/solitario.log | grep "Profilo attivo"
```

Should show: "Profilo attivo: Test"

✅ **Profile file check:**
```bash
cat ~/.solitario/profiles/profile_001.json | jq '.profile.is_default'
```

Should return: true

---

## Test G: NVDA Accessibility

**Objective:** Verify screen reader announcements work correctly

### Prerequisites
- NVDA screen reader running
- NVDA speech output audible

### Execution Steps

1. **Launch with NVDA:**
   ```bash
   # NVDA should already be running
   python acs_wx.py
   ```

2. **Navigate main menu:**
   - Use arrow keys
   - Listen for menu item announcements

3. **Test abandon flow:**
   - Start game (N)
   - Press ESC
   - Listen for: "Partita in corso. Abbandonare?"
   - Confirm
   - Listen for AbandonDialog announcements

4. **Test victory:**
   - Complete game
   - Listen for: "Hai vinto!" announcement
   - Listen for VictoryDialog content

5. **Test timeout:**
   - Let timer expire
   - Listen for timeout announcement

### Expected Results

✅ **All announcements heard:**
- Menu navigation announces items
- Dialogs announce title and options
- Game state changes announced
- Errors announced clearly

✅ **TTS timing:**
- Important announcements use `interrupt=True`
- Navigation uses `interrupt=False`
- No announcements cut off inappropriately

---

## Test H: "Ultima Partita" Menu

**Objective:** Verify last game display works

### Execution Steps

1. **Play a game** (any outcome)

2. **Return to menu**

3. **Click "Ultima Partita" button** (U key)

### Expected Results

✅ **LastGameDialog appears** with:
- End reason displayed
- Statistics shown
- Victory/abandon/timeout indicated correctly

✅ **Data matches profile:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions[-1]'
```

Dialog data should match last session in profile

---

## Summary Checklist

After completing all tests, verify:

- [ ] Test A: Guest profile created automatically ✅
- [ ] Test B: Abandon flow clean (no empty window) ✅
- [ ] Test C: STRICT timeout recorded correctly ✅
- [ ] Test D: PERMISSIVE overtime victory recorded ✅
- [ ] Test E: Dirty shutdown handled gracefully ✅
- [ ] Test F: Default profile selection works ✅
- [ ] Test G: NVDA accessibility functional ✅
- [ ] Test H: Last game display works ✅

## Common Issues & Troubleshooting

### Empty Window After Abandon

**Symptom:** Window goes blank after ESC abandon

**Debug:**
```bash
tail -100 ./logs/solitario.log | grep -i "panel\|menu"
```

**Look for:**
- Panel hide/show sequence
- Double transition warnings
- Menu panel show confirmation

### Stats Not Recording

**Symptom:** Profile file not updated after game

**Debug:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions | length'
```

**Check:**
- ProfileService initialized correctly
- end_game() calls record_session()
- No exceptions in log file

### Timer Fields Wrong

**Symptom:** timer_mode shows wrong value

**Debug:**
```bash
cat ~/.solitario/profiles/profile_000.json | jq '.recent_sessions[-1] | {timer_enabled, timer_limit, timer_mode}'
```

**Expected mapping:**
- max_time_game > 0 → timer_enabled: true
- max_time_game value → timer_limit
- timer_strict_mode → "STRICT" or "PERMISSIVE"

---

## Log Analysis Commands

**View all debug flow:**
```bash
tail -200 ./logs/solitario.log | grep DEBUG
```

**Check session recording:**
```bash
tail -100 ./logs/solitario.log | grep "record_session\|SessionOutcome"
```

**View callback flow:**
```bash
tail -100 ./logs/solitario.log | grep "callback\|handle_game_ended"
```

**Check panel transitions:**
```bash
tail -100 ./logs/solitario.log | grep "panel_hidden\|panel_shown\|show_panel"
```

---

## Reporting Issues

When reporting issues found during verification:

1. **Include test name** (e.g., "Test B: Voluntary Abandon")
2. **Steps to reproduce** (exact sequence)
3. **Expected vs actual result**
4. **Relevant log snippet** (10-20 lines)
5. **Profile file state** (if relevant)
6. **Screenshots** (if UI issue)

---

**End of Runtime Verification Plan**
