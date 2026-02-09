# ✅ BUG FIX CHECKLIST v1.4.2.1

**Branch**: `refactoring-engine`  
**Version**: v1.4.2.1 (Hotfix)  
**Date Started**: 2026-02-09  
**Status**: 🟡 IN PROGRESS

---

## 🎯 OVERVIEW

**Total Tasks**: 23  
**Completed**: 2/23 (⬛⬛⬛⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜) 9%

**Bug Fixes**:
- 🐛 Bug #1: Mazzo Napoletano Non Applicato (HIGH)
- 🐛 Bug #2: Asso Accettato su Seme Sbagliato (CRITICAL)

---

## 📋 DOCUMENTATION (2/2) ✅

- [x] 📝 Create comprehensive plan document
  - File: `docs/BUG_FIX_v1.4.2.1_PLAN.md`
  - Commit: `736db48`
  - Status: ✅ COMPLETE

- [x] 📝 Create tracking checklist
  - File: `docs/BUG_FIX_v1.4.2.1_CHECKLIST.md`
  - Commit: (this file)
  - Status: ✅ COMPLETE

---

## 🐛 BUG #1: DECK TYPE NOT APPLIED (0/9)

### **Phase 1.1: Code Modifications** (0/5)

- [ ] **File 1**: Modify `src/application/game_engine.py`
  - [ ] Add import: `NeapolitanDeck`
  - [ ] Add import: `GameSettings`
  - [ ] Add import: `Optional` (if not present)
  - [ ] Modify `create()` signature: add `settings` parameter
  - [ ] Replace hardcoded `FrenchDeck()` with dynamic instantiation
  - Lines affected: ~5 additions, ~8 modifications
  - Complexity: LOW

- [ ] **File 2**: Modify `test.py`
  - [ ] Add import: `GameSettings`
  - [ ] Create `self.settings = GameSettings()` instance
  - [ ] Pass `settings` to `GameEngine.create()`
  - [ ] Pass `settings` to `GamePlayController()`
  - Lines affected: ~10 modifications
  - Complexity: LOW

- [ ] **File 3**: Modify `src/application/gameplay_controller.py`
  - [ ] Accept `settings` parameter in `__init__()`
  - [ ] Use provided `settings` or create new (backward compat)
  - Lines affected: ~5 modifications
  - Complexity: LOW

- [ ] **Verify imports consistency**
  - [ ] Check all `from` statements are correct
  - [ ] Verify no circular import issues
  - [ ] Test imports: `python -c "from src.application.game_engine import GameEngine"`

- [ ] **Code review self-check**
  - [ ] All type hints correct
  - [ ] Backward compatibility maintained
  - [ ] No hardcoded values
  - [ ] Default fallback to French deck works

### **Phase 1.2: Testing** (0/4)

- [ ] **Test 1**: Default French Deck
  - [ ] Start app (no options change)
  - [ ] New game
  - [ ] Verify 52 cards dealt
  - [ ] Check TTS says "Carte Francesi" (if implemented)

- [ ] **Test 2**: Neapolitan Deck Selection
  - [ ] Open options (O key)
  - [ ] Toggle deck to Napoletane (ENTER on option 1)
  - [ ] Save (S key)
  - [ ] Start new game (N)
  - [ ] Verify 40 cards dealt (count stock + tableau)
  - [ ] Check card values: max=10 (no Jack/Queen/King)
  - [ ] Verify suit names: Denari, Coppe, Spade, Bastoni

- [ ] **Test 3**: Settings Persistence
  - [ ] Set Napoletane, save, close game
  - [ ] Reopen game
  - [ ] New game
  - [ ] Verify Napoletane still selected

- [ ] **Test 4**: Mid-Game Block
  - [ ] Start game with French deck
  - [ ] During gameplay, try to open options (O)
  - [ ] Verify: "Non puoi aprire le opzioni durante una partita!"
  - [ ] Confirm block works

---

## 🐛 BUG #2: ACE SUIT VALIDATION (0/12)

### **Phase 2.1: Code Modifications** (0/6)

- [ ] **File 1**: Modify `src/domain/models/pile.py`
  - [ ] Add import: `Optional` to typing
  - [ ] Add `assigned_suit: Optional[str] = None` parameter to `__init__()`
  - [ ] Add `self.assigned_suit = assigned_suit` attribute
  - [ ] Update docstring with new parameter
  - Lines affected: ~5 additions
  - Complexity: LOW

- [ ] **File 2**: Modify `src/domain/models/table.py`
  - [ ] Replace foundation pile creation with dynamic suit assignment
  - [ ] Use `deck.SEMI` to get suit names from deck
  - [ ] Create loop: `for suit in deck.SEMI`
  - [ ] Assign `assigned_suit=suit` to each foundation
  - Lines affected: ~8 modifications
  - Complexity: MEDIUM

- [ ] **File 3**: Modify `src/domain/rules/solitaire_rules.py`
  - [ ] Locate `can_place_on_foundation()` method (~line 125)
  - [ ] Modify empty pile check to validate suit
  - [ ] Add: `is_ace = card.get_value == 1`
  - [ ] Add: `correct_suit = card.get_suit == target_pile.assigned_suit`
  - [ ] Return: `is_ace and correct_suit` (with None check)
  - [ ] Maintain backward compatibility for None assigned_suit
  - Lines affected: ~10 modifications
  - Complexity: MEDIUM

- [ ] **Verify suit name consistency**
  - [ ] Check `FrenchDeck.SEMI = ["Cuori", "Quadri", "Fiori", "Picche"]`
  - [ ] Check `NeapolitanDeck.SEMI = ["Denari", "Coppe", "Spade", "Bastoni"]`
  - [ ] Check `Card.get_suit` returns same format
  - [ ] Verify string comparison will work

- [ ] **Test backward compatibility**
  - [ ] Create test pile without assigned_suit
  - [ ] Verify old behavior: any ace accepted
  - [ ] Ensure no crashes when assigned_suit is None

- [ ] **Code review self-check**
  - [ ] Suit validation logic correct
  - [ ] None-safe checks in place
  - [ ] Works for both French and Neapolitan decks
  - [ ] Doesn't break existing tests

### **Phase 2.2: Testing - French Deck** (0/3)

- [ ] **Test 1**: Correct Ace Placement (French)
  - [ ] Get Ace of Hearts (Asso di Cuori)
  - [ ] Navigate to Hearts foundation (SHIFT+1)
  - [ ] Place ace → MUST BE ACCEPTED ✓
  - [ ] Repeat for all 4 suits:
    - [ ] Ace♥ on Pile 7 (Cuori)
    - [ ] Ace♦ on Pile 8 (Quadri)
    - [ ] Ace♣ on Pile 9 (Fiori)
    - [ ] Ace♠ on Pile 10 (Picche)

- [ ] **Test 2**: Wrong Ace Placement (French)
  - [ ] Get Ace of Clubs (Asso di Fiori)
  - [ ] Navigate to Spades foundation (SHIFT+4)
  - [ ] Try to place → MUST BE REJECTED ✗
  - [ ] Verify TTS: "Mossa non valida per fondazione"
  - [ ] Test cross-suit rejections:
    - [ ] Ace♣ on Hearts pile → ✗
    - [ ] Ace♥ on Clubs pile → ✗
    - [ ] Ace♦ on Spades pile → ✗

- [ ] **Test 3**: Subsequent Cards After Ace (French)
  - [ ] Place Ace♣ on Clubs foundation correctly
  - [ ] Get 2♣ (2 of Clubs)
  - [ ] Place on Ace♣ → MUST BE ACCEPTED ✓
  - [ ] Get 2♠ (2 of Spades)
  - [ ] Try to place on foundation with Ace♣ → MUST BE REJECTED ✗
  - [ ] Get 3♣
  - [ ] Place on 2♣ → MUST BE ACCEPTED ✓

### **Phase 2.3: Testing - Neapolitan Deck** (0/3)

- [ ] **Test 4**: Correct Ace Placement (Neapolitan)
  - [ ] Change deck to Napoletane in options
  - [ ] New game
  - [ ] Verify foundation names use Neapolitan suits
  - [ ] Place aces correctly:
    - [ ] Asso Denari on Pile 7
    - [ ] Asso Coppe on Pile 8
    - [ ] Asso Spade on Pile 9
    - [ ] Asso Bastoni on Pile 10

- [ ] **Test 5**: Wrong Ace Placement (Neapolitan)
  - [ ] Get Asso Denari
  - [ ] Try on Coppe foundation → MUST BE REJECTED ✗
  - [ ] Try on Spade foundation → MUST BE REJECTED ✗
  - [ ] Try on Bastoni foundation → MUST BE REJECTED ✗
  - [ ] Place on Denari foundation → MUST BE ACCEPTED ✓

- [ ] **Test 6**: Subsequent Cards After Ace (Neapolitan)
  - [ ] Place Asso Bastoni correctly
  - [ ] Place 2 Bastoni on Asso → ✓
  - [ ] Try 2 Denari on foundation with Asso Bastoni → ✗
  - [ ] Complete sequence up to Re (10) → all ✓

---

## 📦 COMMITS (0/2)

- [ ] **Commit #29**: `fix(game): Apply deck type from settings`
  - Files: `game_engine.py`, `test.py`, `gameplay_controller.py`
  - Message template:
    ```
    fix(game): Apply deck type from settings
    
    GameEngine now reads deck_type from GameSettings and instantiates
    the correct deck (FrenchDeck or NeapolitanDeck) dynamically.
    
    Changes:
    - Add settings parameter to GameEngine.create()
    - Import NeapolitanDeck in game_engine.py
    - Pass settings from test.py to engine creation
    - Accept settings in GamePlayController
    
    Fixes: #BUG-001 (Mazzo napoletano non applicato)
    
    Testing:
    - ✓ Default French deck works
    - ✓ Neapolitan selection creates 40-card deck
    - ✓ Settings persist across sessions
    - ✓ Mid-game modification blocked
    ```
  - Status: ⏳ PENDING
  - Link: (will add after commit)

- [ ] **Commit #30**: `fix(rules): Validate ace suit in foundation placement`
  - Files: `pile.py`, `table.py`, `solitaire_rules.py`
  - Message template:
    ```
    fix(rules): Validate ace suit in foundation placement
    
    Foundation piles now have fixed assigned suits and only accept
    aces of the matching suit when empty. This prevents placing
    Ace of Clubs on Spades foundation, etc.
    
    Changes:
    - Add assigned_suit attribute to Pile model
    - Assign fixed suits to foundations from deck.SEMI
    - Validate ace suit in can_place_on_foundation()
    - Support both French and Neapolitan deck suit names
    
    Fixes: #BUG-002 (Asso accettato su seme sbagliato)
    
    Testing:
    - ✓ Correct ace placement accepted (all 4 suits)
    - ✓ Wrong suit ace placement rejected
    - ✓ Subsequent cards validated correctly
    - ✓ Works with both French and Neapolitan decks
    - ✓ Backward compatible with tests (assigned_suit=None)
    ```
  - Status: ⏳ PENDING
  - Link: (will add after commit)

---

## 📝 CHANGELOG UPDATE (0/1)

- [ ] **Update CHANGELOG.md**
  - [ ] Add section for v1.4.2.1
  - [ ] Document both bug fixes
  - [ ] List all modified files
  - [ ] Reference commit SHAs
  - [ ] Add testing notes
  - File: `CHANGELOG.md`
  - Commit message: `docs: Update CHANGELOG for v1.4.2.1 bug fixes`

---

## 🧪 REGRESSION TESTING (0/3)

- [ ] **Regression Test 1**: Existing Features
  - [ ] Card movement (single + multi-card)
  - [ ] Draw from stock (D/P keys)
  - [ ] Foundation moves (correct suit, already working)
  - [ ] Tableau moves (alternating colors)
  - [ ] Empty pile King placement
  - [ ] Victory detection

- [ ] **Regression Test 2**: Options Window
  - [ ] Open/close (O key)
  - [ ] Navigate all 5 options
  - [ ] Modify each option
  - [ ] Save/discard dialogs
  - [ ] Settings persistence

- [ ] **Regression Test 3**: Dialogs & Navigation
  - [ ] ESC in main menu (exit dialog)
  - [ ] ESC in game submenu (return dialog)
  - [ ] ESC during gameplay (abandon dialog)
  - [ ] Double-ESC quick exit
  - [ ] All TTS announcements working

---

## 🏁 COMPLETION CRITERIA

### **Bug #1 Resolved**:
- [ ] French deck works (default)
- [ ] Neapolitan deck selectable and applied
- [ ] TTS announces correct deck type
- [ ] Card counts correct (52 vs 40)
- [ ] King values correct (13 vs 10)

### **Bug #2 Resolved**:
- [ ] Ace♥ only on Hearts foundation
- [ ] Ace♦ only on Diamonds foundation
- [ ] Ace♣ only on Clubs foundation
- [ ] Ace♠ only on Spades foundation
- [ ] Wrong suit gives error message
- [ ] Works for both deck types

### **Quality Checks**:
- [ ] No new bugs introduced
- [ ] All existing features work
- [ ] Code is clean and documented
- [ ] Commits are atomic
- [ ] CHANGELOG updated

---

## 📊 PROGRESS TRACKING

**Session 1** (2026-02-09 00:00-00:10):  
✅ Documentation created (2 files)  
⏳ Ready to start implementation

**Session 2** (Upcoming):  
⏳ Bug #1 implementation (Commit #29)  
⏳ Bug #1 testing

**Session 3** (Upcoming):  
⏳ Bug #2 implementation (Commit #30)  
⏳ Bug #2 testing

**Session 4** (Upcoming):  
⏳ Regression testing  
⏳ CHANGELOG update  
⏳ Final verification

---

## 📝 NOTES

**Important Reminders**:
- Test with NVDA screen reader for full accessibility check
- Verify both French and Neapolitan decks thoroughly
- Check that existing unit tests still pass
- Update documentation if behavior changes
- Consider adding unit tests for new validation logic

**Known Limitations**:
- Existing savegames with wrong ace placement will need restart
- No migration path for corrupted game states
- User must manually start new game after fix applied

**Future Enhancements** (Not in scope):
- Auto-detect and fix corrupted foundation piles
- Add visual indicators for assigned suits
- Implement savegame validation

---

**Last Updated**: 2026-02-09 00:08 CET  
**Next Review**: After Commit #29 completion  
**Final Review**: After all tests pass

---

**🚀 Ready to implement!** Follow the checklist and mark each item as you complete it.
