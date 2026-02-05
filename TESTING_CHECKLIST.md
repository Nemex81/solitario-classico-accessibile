# 📋 Testing Checklist - Timer & Shuffle Feature

## 🎯 Overview
This document provides a comprehensive testing checklist for the timer decrement fix (F3) and the new shuffle mode feature (F5).

---

## ✅ Test 1: F3 Timer Decrement

### Prerequisites
- Start the application
- Press **O** to open options

### Test Cases

#### TC1.1: Basic Decrement
- [ ] Press **F4** to set timer to 5 minutes
- [ ] Press **F3** → Timer should show 5 minutes (at minimum, won't go lower)
- [ ] Vocal message: "Timer impostato a 5 minuti."

#### TC1.2: Multiple Decrements
- [ ] Press **F4** multiple times to set timer to 30 minutes
- [ ] Press **F3** → Timer should decrease to 25 minutes
- [ ] Press **F3** → Timer should decrease to 20 minutes
- [ ] Vocal messages correct for each step

#### TC1.3: Minimum Limit (5 minutes)
- [ ] Set timer to 5 minutes
- [ ] Press **F3** → Timer should stay at 5 minutes (not go to 0 or negative)
- [ ] OR timer is disabled (returns to -1)
- [ ] Appropriate vocal message

#### TC1.4: From Disabled to Active
- [ ] Press **CTRL+F3** to disable timer
- [ ] Verify message: "il timer è stato disattivato!"
- [ ] Press **F3** → Timer should be set to 5 minutes
- [ ] Vocal message: "Timer impostato a 5 minuti."

---

## ✅ Test 2: F4 Timer Increment

### Test Cases

#### TC2.1: Basic Increment
- [ ] Press **O** to open options
- [ ] Timer disabled by default
- [ ] Press **F4** → Timer set to 5 minutes
- [ ] Press **F4** → Timer increases to 10 minutes
- [ ] Vocal messages correct

#### TC2.2: Maximum Limit (60 minutes)
- [ ] Press **F4** repeatedly until timer reaches 60 minutes
- [ ] Press **F4** again → Timer should stay at 60 minutes OR wrap to disabled
- [ ] Appropriate vocal message

#### TC2.3: Increment from Middle Value
- [ ] Set timer to 25 minutes
- [ ] Press **F4** → Timer should increase to 30 minutes
- [ ] Verify vocal message

---

## ✅ Test 3: F5 Shuffle Mode Toggle

### Prerequisites
- Start the application
- Press **O** to open options

### Test Cases

#### TC3.1: Default State
- [ ] Fresh start → shuffle_discards should be **False** (Inversion mode)
- [ ] Press **I** to read settings
- [ ] Verify: "Modalità riciclo scarti: INVERSIONE SEMPLICE"

#### TC3.2: Toggle to Shuffle
- [ ] Press **F5** in options
- [ ] Vocal message: "Modalità riciclo scarti: MESCOLATA CASUALE."
- [ ] Press **I** to verify settings updated

#### TC3.3: Toggle Back to Inversion
- [ ] Press **F5** again
- [ ] Vocal message: "Modalità riciclo scarti: INVERSIONE SEMPLICE."
- [ ] Press **I** to verify settings updated

#### TC3.4: Multiple Toggles
- [ ] Press **F5** 10 times rapidly
- [ ] Verify toggle works consistently
- [ ] Final state should alternate correctly

#### TC3.5: Cannot Change During Game
- [ ] Press **O** to close options
- [ ] Press **N** to start a new game
- [ ] Try pressing **F5**
- [ ] Should NOT work or give error message
- [ ] Expected: "Non puoi modificare la modalità di riciclo scarti durante una partita!"

#### TC3.6: Requires Options Open
- [ ] Close options with **O** (no game running)
- [ ] Try pressing **F5**
- [ ] Expected message: "Devi prima aprire le opzioni con il tasto O!"

---

## ✅ Test 4: Card Recycling - Inversion Mode

### Prerequisites
- Press **O**, set shuffle mode to **Inversion** (press F5 if needed until "INVERSIONE SEMPLICE")
- Press **O** to close options
- Press **N** to start new game

### Test Cases

#### TC4.1: Basic Inversion Behavior
- [ ] Play game until deck (mazzo riserve) is empty
- [ ] Press **SPACE** to draw
- [ ] Vocal message: "Rimescolo gli scarti in mazzo riserve!"
- [ ] Note the order of cards that appear
- [ ] Play until deck empty again
- [ ] Order should be predictable/reversed from first pass

#### TC4.2: Verify Card Order
- [ ] Note top 3 cards in discard pile before recycle
- [ ] Trigger recycle
- [ ] Bottom card of discard pile should now be on top of deck (inverted)
- [ ] Draw to verify

---

## ✅ Test 5: Card Recycling - Shuffle Mode

### Prerequisites
- Press **O**, toggle shuffle mode to **Shuffle** (F5 until "MESCOLATA CASUALE")
- Press **O** to close options
- Press **N** to start new game

### Test Cases

#### TC5.1: Basic Shuffle Behavior
- [ ] Play game until deck is empty
- [ ] Press **SPACE** to draw
- [ ] Vocal message: "Rimescolo gli scarti in modo casuale nel mazzo riserve!"
- [ ] Note the order of cards that appear

#### TC5.2: Randomness Verification
- [ ] Repeat game multiple times (at least 3)
- [ ] Each time deck is recycled, card order should be different
- [ ] Order should NOT be simply reversed
- [ ] Should feel like a genuine shuffle

#### TC5.3: No Card Loss/Duplication
- [ ] During recycling in shuffle mode
- [ ] All cards from discard pile should move to deck
- [ ] No cards lost
- [ ] No cards duplicated
- [ ] Total card count remains 52

---

## ✅ Test 6: Settings Info Report

### Test Cases

#### TC6.1: Read Settings with I Key
- [ ] Press **O** to open options
- [ ] Press **I**
- [ ] Should vocalize:
  - Difficulty level
  - Timer status (active/disabled and duration)
  - Shuffle mode (Inversion/Shuffle)

#### TC6.2: Settings Update After Toggle
- [ ] Press **I** to read initial settings
- [ ] Press **F5** to toggle shuffle mode
- [ ] Press **I** again
- [ ] Shuffle mode status should be updated

#### TC6.3: Settings with Timer Changes
- [ ] Press **F3** or **F4** to change timer
- [ ] Press **I**
- [ ] Timer value should reflect the change

---

## ✅ Test 7: Reset Behavior

### Test Cases

#### TC7.1: Shuffle Mode Resets on New Game
- [ ] Press **O**, set shuffle mode to **Shuffle** (MESCOLATA CASUALE)
- [ ] Press **O** to close options
- [ ] Press **N** to start game
- [ ] Play or abandon game (ESC)
- [ ] Press **O** to open options again
- [ ] Press **I** to check settings
- [ ] ⚠️ **CRITICAL**: Shuffle mode should be reset to **INVERSIONE SEMPLICE** (default)

#### TC7.2: Timer Preserved Between Games
- [ ] Set timer to 20 minutes
- [ ] Start a game, then abandon it
- [ ] Open options again
- [ ] Timer should still be at 20 minutes (NOT reset)

#### TC7.3: Difficulty Resets on New Game
- [ ] Set difficulty to 3
- [ ] Start and abandon game
- [ ] Difficulty should reset to 1

---

## ✅ Test 8: Integration Tests

### TC8.1: Complete Game with Inversion
1. [ ] Open options, ensure Inversion mode
2. [ ] Set timer to 10 minutes
3. [ ] Start new game
4. [ ] Play until deck recycles (at least once)
5. [ ] Verify inversion message and behavior
6. [ ] Complete or abandon game
7. [ ] Verify shuffle mode reset to default

### TC8.2: Complete Game with Shuffle
1. [ ] Open options, set Shuffle mode
2. [ ] Set timer to 15 minutes
3. [ ] Start new game
4. [ ] Play until deck recycles (at least once)
5. [ ] Verify shuffle message and behavior
6. [ ] Complete or abandon game
7. [ ] Verify shuffle mode reset to default

### TC8.3: Multiple Games with Mode Changes
1. [ ] Game 1: Play with Inversion mode
2. [ ] After game, change to Shuffle mode
3. [ ] Game 2: Play with Shuffle mode
4. [ ] After game, change back to Inversion
5. [ ] Game 3: Play with Inversion mode
6. [ ] Verify mode changes work across multiple games

---

## ✅ Test 9: Accessibility Testing

### Prerequisites
- Screen reader software (NVDA, JAWS, or similar)

### Test Cases

#### TC9.1: F3/F4 Vocal Feedback
- [ ] All timer change messages are read correctly
- [ ] Clear and understandable
- [ ] No garbled or missing text

#### TC9.2: F5 Vocal Feedback
- [ ] Toggle messages are clear
- [ ] "INVERSIONE SEMPLICE" read correctly
- [ ] "MESCOLATA CASUALE" read correctly
- [ ] Screen reader doesn't cut off messages

#### TC9.3: Settings Info Vocal Output
- [ ] Press **I** to read settings
- [ ] All information vocalized clearly
- [ ] Proper pauses between items
- [ ] Easy to understand

#### TC9.4: Recycling Messages
- [ ] Both recycling messages clear and distinct
- [ ] User can tell which mode is active from message alone

---

## ✅ Test 10: Error Handling

### Test Cases

#### TC10.1: F5 Without Options Open
- [ ] Close options (or don't open them)
- [ ] Press **F5**
- [ ] Should get error: "Devi prima aprire le opzioni con il tasto O!"

#### TC10.2: F5 During Active Game
- [ ] Start a game
- [ ] Try pressing **F5** during gameplay
- [ ] Should get error: "Non puoi modificare la modalità di riciclo scarti durante una partita!"

#### TC10.3: F3/F4 Without Options Open
- [ ] Close options
- [ ] Press **F3** or **F4**
- [ ] Should not work or give appropriate error

#### TC10.4: Timer Limits
- [ ] Try to set timer below 5 minutes
- [ ] Should stay at 5 or disable
- [ ] Try to set timer above 60 minutes
- [ ] Should stay at 60 or wrap appropriately

---

## ✅ Test 11: Performance Testing

### Test Cases

#### TC11.1: Shuffle Performance
- [ ] Trigger card recycle in shuffle mode
- [ ] Should be instantaneous (< 100ms perceivable delay)
- [ ] No lag or freeze
- [ ] `random.shuffle()` on 52 cards is fast

#### TC11.2: Multiple Rapid Toggles
- [ ] Press **F5** 50 times rapidly
- [ ] Should handle all inputs
- [ ] No crashes or hangs
- [ ] Final state correct

---

## 📊 Summary Checklist

### Critical Tests (Must Pass)
- [ ] F3 decrements timer correctly
- [ ] F4 increments timer correctly
- [ ] Timer respects 5-min minimum and 60-min maximum
- [ ] F5 toggles shuffle mode
- [ ] Shuffle mode resets to default on new game
- [ ] Inversion mode works (default behavior maintained)
- [ ] Shuffle mode randomizes correctly
- [ ] No card loss during recycling
- [ ] Settings info shows shuffle mode
- [ ] All vocal messages correct

### Optional Tests (Nice to Have)
- [ ] Performance is good
- [ ] Error messages are clear
- [ ] Multiple games work smoothly
- [ ] Screen reader compatibility

---

## 🐛 Bug Reporting

If you find issues during testing:

1. **Note the test case number** (e.g., TC4.1)
2. **Describe what happened** vs what was expected
3. **Steps to reproduce**
4. **Any error messages**
5. **Your environment** (Python version, OS, screen reader if applicable)

---

## ✅ Sign-Off

**Tester Name:** ___________________  
**Date:** ___________________  
**All Critical Tests Passed:** ☐ Yes ☐ No  
**Ready for Production:** ☐ Yes ☐ No  

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________
