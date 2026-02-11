# TODO: Fix Difficulty Levels 4-5 Bugs

**Priority**: HIGH  
**Affects**: Difficulty levels 4 (Expert) and 5 (Master)  
**Impact**: Critical gameplay bugs preventing proper difficulty configuration  
**Estimated LOC**: ~46 lines (production code only)

---

## 🐛 BUG #1: `draw_count` Not Configured for Levels 4-5

### Problem Description

When difficulty is set to level 4 or 5, the `draw_count` (cards drawn per click) falls into the fallback case and defaults to 1 card instead of 3 cards.

### Current Behavior

**File**: `src/application/game_engine.py`  
**Method**: `_apply_game_settings()` (lines ~1060-1066)

```python
if self.settings.difficulty_level == 1:
    self.draw_count = 1
elif self.settings.difficulty_level == 2:
    self.draw_count = 2
elif self.settings.difficulty_level == 3:
    self.draw_count = 3
else:
    # Fallback for invalid values
    self.draw_count = 1  # ❌ BUG: Levels 4-5 get 1 card instead of 3!
```

### Expected Behavior

- **Level 4 (Expert)**: Should draw 3 cards per click (same as level 3)
- **Level 5 (Master)**: Should draw 3 cards per click (same as level 3)

### Root Cause

Missing explicit cases for `difficulty_level == 4` and `difficulty_level == 5` in the if-elif chain.

### Fix Implementation

**Location**: `src/application/game_engine.py`, method `_apply_game_settings()`

**Replace lines ~1060-1066 with**:

```python
# 1️⃣ Draw count from difficulty
if self.settings.difficulty_level == 1:
    self.draw_count = 1
elif self.settings.difficulty_level == 2:
    self.draw_count = 2
elif self.settings.difficulty_level == 3:
    self.draw_count = 3
elif self.settings.difficulty_level == 4:
    self.draw_count = 3  # ✅ Level 4: 3 cards (Expert)
elif self.settings.difficulty_level == 5:
    self.draw_count = 3  # ✅ Level 5: 3 cards (Master)
else:
    # Fallback for invalid values
    self.draw_count = 1
```

**Lines Added**: 4  
**Lines Modified**: 0  
**Lines Deleted**: 0

---

## 🐛 BUG #2: Timer Constraints Not Enforced for Levels 4-5

### Problem Description

Difficulty levels 4 and 5 require **mandatory timer constraints**, but these are not validated or enforced anywhere in the code. Users can disable the timer or set invalid values.

### Current Behavior

- **Level 4 (Expert)**: Timer is optional (should be mandatory, 5-60 minutes)
- **Level 5 (Master)**: Timer is optional (should be mandatory, 5-20 minutes)

### Expected Behavior

| Level | Timer Requirement | Valid Range |
|-------|------------------|-------------|
| 1-3 | Optional | 5-60 minutes OR OFF |
| 4 (Expert) | **MANDATORY** | 5-60 minutes |
| 5 (Master) | **MANDATORY** | 5-20 minutes |

### Validation Rules

#### Level 4 (Expert)
- If `max_time_game <= 0` (timer OFF): **Force enable** with default 30 minutes (1800 seconds)
- If `max_time_game < 300` (< 5 min): Increase to 300 seconds (5 minutes)
- If `max_time_game > 3600` (> 60 min): Decrease to 3600 seconds (60 minutes)

#### Level 5 (Master)
- If `max_time_game <= 0` (timer OFF): **Force enable** with default 15 minutes (900 seconds)
- If `max_time_game < 300` (< 5 min): Increase to 300 seconds (5 minutes)
- If `max_time_game > 1200` (> 20 min): **Decrease to 1200 seconds (20 minutes)**

### Root Cause

No validation logic exists in:
1. `GameEngine._apply_game_settings()` - when starting a new game
2. `GameEngine.create()` - when creating the engine with settings

### Fix Implementation

#### A) Add Validation in `_apply_game_settings()`

**Location**: `src/application/game_engine.py`, method `_apply_game_settings()`

**Add after draw_count configuration (after line ~1066)**:

```python
# 1.5️⃣ VALIDATE TIMER CONSTRAINTS FOR LEVELS 4-5
if self.settings.difficulty_level >= 4:
    if self.settings.max_time_game <= 0:
        # Timer not enabled → force default
        if self.settings.difficulty_level == 4:
            self.settings.max_time_game = 1800  # 30 minutes (middle of 5-60 range)
        else:  # Level 5
            self.settings.max_time_game = 900   # 15 minutes (middle of 5-20 range)
        
        if self.screen_reader:
            minutes = self.settings.max_time_game // 60
            self.screen_reader.tts.speak(
                f"Livello {self.settings.difficulty_level} richiede timer obbligatorio. "
                f"Impostato automaticamente a {minutes} minuti.",
                interrupt=False
            )
    else:
        # Timer enabled → validate range
        if self.settings.difficulty_level == 4:
            # Level 4: 5-60 minutes (300-3600 seconds)
            if self.settings.max_time_game < 300:
                self.settings.max_time_game = 300
                if self.screen_reader:
                    self.screen_reader.tts.speak(
                        "Livello Esperto: limite minimo 5 minuti. Timer aumentato.",
                        interrupt=False
                    )
            elif self.settings.max_time_game > 3600:
                self.settings.max_time_game = 3600
                if self.screen_reader:
                    self.screen_reader.tts.speak(
                        "Livello Esperto: limite massimo 60 minuti. Timer ridotto.",
                        interrupt=False
                    )
        else:  # Level 5
            # Level 5: 5-20 minutes (300-1200 seconds)
            if self.settings.max_time_game < 300:
                self.settings.max_time_game = 300
                if self.screen_reader:
                    self.screen_reader.tts.speak(
                        "Livello Maestro: limite minimo 5 minuti. Timer aumentato.",
                        interrupt=False
                    )
            elif self.settings.max_time_game > 1200:
                self.settings.max_time_game = 1200
                if self.screen_reader:
                    self.screen_reader.tts.speak(
                        "Livello Maestro: limite massimo 20 minuti. Timer ridotto.",
                        interrupt=False
                    )
```

**Lines Added**: ~38

---

#### B) Add Validation in `create()` Factory Method

**Location**: `src/application/game_engine.py`, method `create()`

**Add before creating ScoringService (before line ~159)**:

```python
# Create scoring service if enabled (v2.0.0)
scoring = None
if settings and settings.scoring_enabled:
    # 🆕 VALIDATE TIMER CONSTRAINTS FOR LEVELS 4-5
    if settings.difficulty_level >= 4:
        if settings.max_time_game <= 0:
            # Force timer for levels 4-5
            if settings.difficulty_level == 4:
                settings.max_time_game = 1800  # 30 min default
            else:  # Level 5
                settings.max_time_game = 900   # 15 min default
        elif settings.difficulty_level == 5:
            # Enforce 5-20 minute range for level 5
            settings.max_time_game = max(300, min(1200, settings.max_time_game))
        elif settings.difficulty_level == 4:
            # Enforce 5-60 minute range for level 4
            settings.max_time_game = max(300, min(3600, settings.max_time_game))
    
    scoring_config = ScoringConfig()
    scoring = ScoringService(
        config=scoring_config,
        difficulty_level=settings.difficulty_level,
        deck_type=settings.deck_type,
        draw_count=settings.draw_count,
        timer_enabled=settings.max_time_game > 0,
        timer_limit_seconds=settings.max_time_game
    )
```

**Lines Added**: ~12

---

## 🧪 Test Cases

### Test Case 1: Level 4 with Timer OFF

**Setup**:
```python
settings.difficulty_level = 4
settings.max_time_game = -1  # Timer OFF
engine = GameEngine.create(settings=settings)
engine.new_game()
```

**Expected Results**:
- ✅ `engine.draw_count == 3`
- ✅ `settings.max_time_game == 1800` (forced to 30 minutes)
- ✅ TTS announces: "Livello 4 richiede timer obbligatorio. Impostato automaticamente a 30 minuti."

---

### Test Case 2: Level 5 with Timer 45 Minutes (Out of Range)

**Setup**:
```python
settings.difficulty_level = 5
settings.max_time_game = 2700  # 45 minutes (> 20 max)
engine = GameEngine.create(settings=settings)
engine.new_game()
```

**Expected Results**:
- ✅ `engine.draw_count == 3`
- ✅ `settings.max_time_game == 1200` (clamped to 20 minutes)
- ✅ TTS announces: "Livello Maestro: limite massimo 20 minuti. Timer ridotto."

---

### Test Case 3: Level 5 with Timer 2 Minutes (Out of Range)

**Setup**:
```python
settings.difficulty_level = 5
settings.max_time_game = 120  # 2 minutes (< 5 min)
engine = GameEngine.create(settings=settings)
engine.new_game()
```

**Expected Results**:
- ✅ `engine.draw_count == 3`
- ✅ `settings.max_time_game == 300` (increased to 5 minutes)
- ✅ TTS announces: "Livello Maestro: limite minimo 5 minuti. Timer aumentato."

---

### Test Case 4: Level 2 - Normal Behavior (No Changes)

**Setup**:
```python
settings.difficulty_level = 2
settings.max_time_game = -1  # Timer OFF
engine = GameEngine.create(settings=settings)
engine.new_game()
```

**Expected Results**:
- ✅ `engine.draw_count == 2`
- ✅ `settings.max_time_game == -1` (timer remains optional)
- ✅ No timer warnings announced

---

### Test Case 5: Level 4 with Valid Timer (30 minutes)

**Setup**:
```python
settings.difficulty_level = 4
settings.max_time_game = 1800  # 30 minutes (valid)
engine = GameEngine.create(settings=settings)
engine.new_game()
```

**Expected Results**:
- ✅ `engine.draw_count == 3`
- ✅ `settings.max_time_game == 1800` (unchanged)
- ✅ No warnings (already valid)

---

## 📊 Implementation Summary

| File | Method | Modification Type | LOC |
|------|--------|------------------|-----|
| `src/application/game_engine.py` | `_apply_game_settings()` | Add draw_count cases | +4 |
| `src/application/game_engine.py` | `_apply_game_settings()` | Add timer validation | +38 |
| `src/application/game_engine.py` | `create()` | Add timer validation | +12 |
| **TOTAL** | | | **~54 LOC** |

---

## ✅ Acceptance Criteria

### Draw Count Fix
- [ ] Level 4 draws 3 cards per click
- [ ] Level 5 draws 3 cards per click
- [ ] Levels 1-3 unchanged (1, 2, 3 cards respectively)

### Timer Validation Fix
- [ ] Level 4: Timer forced to 5-60 minutes range
- [ ] Level 5: Timer forced to 5-20 minutes range
- [ ] Level 4 with timer OFF: Auto-set to 30 minutes with TTS announcement
- [ ] Level 5 with timer OFF: Auto-set to 15 minutes with TTS announcement
- [ ] Level 5 with timer > 20 min: Clamped to 20 minutes with TTS announcement
- [ ] Level 5 with timer < 5 min: Increased to 5 minutes with TTS announcement
- [ ] Levels 1-3: Timer remains optional (no validation)

### No Regressions
- [ ] Levels 1-3 behavior unchanged
- [ ] No breaking changes to existing code
- [ ] No impact on scoring calculations

---

## 📝 Commit Message Template

```
fix(application): Fix draw_count and timer constraints for difficulty levels 4-5

Two critical bugs fixed:

1. draw_count not configured for levels 4-5
   - Level 4 now draws 3 cards (was 1)
   - Level 5 now draws 3 cards (was 1)

2. Timer constraints not enforced for levels 4-5
   - Level 4: Timer mandatory (5-60 minutes)
   - Level 5: Timer mandatory (5-20 minutes)
   - Auto-correction with TTS feedback
   - Validation in both create() and _apply_game_settings()

Fixes gameplay bugs preventing proper Expert/Master difficulty.

Refs: docs/TODO_FIX_DIFFICULTY_LEVELS_4_5.md
```

---

## 🔗 Related Documentation

- `docs/IMPLEMENTATION_SCORING_SYSTEM.md` - Scoring system specification (levels 4-5 constraints)
- `src/domain/models/scoring.py` - ScoringConfig with difficulty multipliers
- `src/application/game_engine.py` - GameEngine implementation

---

## 🚀 Implementation Notes

### Why Two Validation Points?

1. **`create()` factory**: Validates settings at engine creation (before game starts)
2. **`_apply_game_settings()`**: Validates settings at new game start (runtime changes)

This ensures constraints are enforced regardless of when settings change.

### TTS Announcements

All validation corrections include TTS feedback for accessibility:
- Clear explanation of why timer was changed
- Exact new timer value in minutes
- Non-intrusive (interrupt=False)

### Backward Compatibility

- No breaking changes to existing API
- Levels 1-3 behavior unchanged
- Settings validation only affects levels 4-5
