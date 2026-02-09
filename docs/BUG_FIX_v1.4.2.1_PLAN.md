# 🐛 BUG FIX PLAN v1.4.2.1 - Deck Type & Ace Validation

**Branch**: `refactoring-engine`  
**Version**: v1.4.2.1 (Hotfix)  
**Date**: 2026-02-09  
**Author**: Nemex81  

---

## 📋 EXECUTIVE SUMMARY

Due bug critici identificati durante testing manuale:

### **Bug #1**: Mazzo Napoletano Non Applicato
- **Severity**: HIGH (feature completely broken)
- **Impact**: User settings ignored, always uses French deck
- **Root Cause**: Hardcoded `FrenchDeck()` in `GameEngine.create()`

### **Bug #2**: Asso Accettato su Seme Sbagliato
- **Severity**: CRITICAL (game rules violation)
- **Impact**: Any ace accepted on any foundation (wrong suit allowed)
- **Root Cause**: Missing suit validation in `can_place_on_foundation()` for empty piles

---

## 🔍 BUG #1 - DETAILED ANALYSIS

### **User Report**
> "Ho selezionato mazzo carte napoletane nelle opzioni ma quando ho avviato la partita il sistema ha allestito con le carte francesi."

### **Root Cause Chain**

```
test.py: SolitarioCleanArch.__init__()
    └─> GameEngine.create(audio_enabled=True, tts_engine="auto")
            └─> deck = FrenchDeck()  ← ALWAYS HARDCODED!
                    └─> deck.crea()
                    └─> deck.mischia()
                    └─> table = GameTable(deck)
```

**Problem**: 
- `GameEngine.create()` does NOT receive `GameSettings` instance
- No way to read user's deck preference
- Always instantiates `FrenchDeck()` regardless of settings

**Current Code** (game_engine.py:77-83):
```python
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1
) -> "GameEngine":
    """Factory method to create fully initialized game engine."""
    
    # Create domain components
    deck = FrenchDeck()  # ← BUG: Hardcoded!
    deck.crea()
    deck.mischia()
```

### **Where Settings ARE Used**

Settings ARE correctly passed to `GamePlayController`:
```python
# gameplay_controller.py:39-42
def __init__(self, engine: GameEngine, screen_reader):
    self.engine = engine
    self.sr = screen_reader
    self.settings = GameSettings()  # ← Settings exist here!
    self.options_controller = OptionsWindowController(self.settings)
```

But `settings` are NOT passed to `engine` during creation!

### **Solution Architecture**

```
test.py: SolitarioCleanArch.__init__()
    ├─> self.settings = GameSettings()  [NEW]
    │
    ├─> GameEngine.create(
    │       audio_enabled=True,
    │       tts_engine="auto",
    │       settings=self.settings  [NEW PARAMETER]
    │   )
    │       └─> Read settings.deck_type
    │       └─> if "french": deck = FrenchDeck()
    │       └─> elif "neapolitan": deck = NeapolitanDeck()
    │
    └─> GamePlayController(
            engine=self.engine,
            screen_reader=self.screen_reader,
            settings=self.settings  [ALREADY EXISTS]
        )
```

### **Code Changes Required**

#### **File 1**: `src/application/game_engine.py`

**Change 1** - Add import:
```python
# Line ~12 (after existing imports)
from src.domain.models.deck import FrenchDeck, NeapolitanDeck  # Add NeapolitanDeck
from src.domain.services.game_settings import GameSettings  # NEW IMPORT
```

**Change 2** - Modify `create()` signature:
```python
# Line ~68
@classmethod
def create(
    cls,
    audio_enabled: bool = True,
    tts_engine: str = "auto",
    verbose: int = 1,
    settings: Optional[GameSettings] = None  # NEW PARAMETER
) -> "GameEngine":
```

**Change 3** - Dynamic deck instantiation:
```python
# Line ~77-83 REPLACE WITH:
# Create domain components
if settings and settings.deck_type == "neapolitan":
    deck = NeapolitanDeck()
else:
    deck = FrenchDeck()  # Default to French

deck.crea()
deck.mischia()
```

#### **File 2**: `test.py`

**Change 1** - Import GameSettings:
```python
# Line ~37 (after GamePlayController import)
from src.domain.services.game_settings import GameSettings  # NEW IMPORT
```

**Change 2** - Create settings instance:
```python
# Line ~108 (in SolitarioCleanArch.__init__, BEFORE engine creation)
# Application: Game settings
print("Inizializzazione impostazioni...")
self.settings = GameSettings()
print("✓ Settings pronti")
```

**Change 3** - Pass settings to engine:
```python
# Line ~117 (modify existing engine creation)
self.engine = GameEngine.create(
    audio_enabled=(self.screen_reader is not None),
    tts_engine="auto",
    verbose=1,
    settings=self.settings  # NEW PARAMETER
)
```

**Change 4** - Pass settings to controller:
```python
# Line ~124 (modify existing controller creation)
self.gameplay_controller = GamePlayController(
    engine=self.engine,
    screen_reader=self.screen_reader if self.screen_reader else self._dummy_sr(),
    settings=self.settings  # ADD THIS PARAMETER
)
```

#### **File 3**: `src/application/gameplay_controller.py`

**Change 1** - Accept settings parameter:
```python
# Line ~36 (modify __init__ signature)
def __init__(self, engine: GameEngine, screen_reader, settings: GameSettings = None):
    self.engine = engine
    self.sr = screen_reader
    
    # Use provided settings or create new (backward compatibility)
    self.settings = settings if settings else GameSettings()
```

### **Testing Verification**

**Test Case 1**: Default French Deck
```
1. Start application (no options change)
2. New game
3. Check TTS announces "Carte Francesi"
4. Verify 52 cards (13 per suit)
```

**Test Case 2**: Neapolitan Deck Selection
```
1. Menu → Opzioni
2. Navigate to "Tipo mazzo"
3. Press ENTER/SPACE → Toggle to "Napoletane"
4. Press S to save
5. New game
6. Verify TTS announces "Carte Napoletane"
7. Verify 40 cards (10 per suit)
8. Verify King value = 10 (not 13)
```

---

## 🔍 BUG #2 - DETAILED ANALYSIS

### **User Report**
> "Ho fatto spazio mentre avevo il cursore sulla pila picche, il sistema, invece di darmi errore mi ha fatto posizionare l'asso di fiori nel seme picche. Ho provato a inserire il 2 di fiori sull'asso di picche e il sistema ha risposto con un 'mossa non consentita'."

### **Reproduction Steps**
1. Play game until Ace of Clubs available
2. Navigate to Spades foundation (SHIFT+4)
3. Move Ace of Clubs to Spades foundation → **ACCEPTED** (WRONG!)
4. Get 2 of Clubs
5. Try to place 2 of Clubs on Ace of Clubs (on Spades pile) → **REJECTED** (correct)

**Result**: Ace placed on wrong foundation, but subsequent cards correctly validated

### **Root Cause**

**File**: `src/domain/rules/solitaire_rules.py` (line ~125)

```python
def can_place_on_foundation(self, card: Card, target_pile: Pile) -> bool:
    """Check if a card can be placed on a foundation pile."""
    
    # CRITICAL: Empty foundation accepts only Aces
    if target_pile.is_empty():
        return card.get_value == 1  # ← BUG: Only checks value!
        # Missing: card.get_suit == target_pile.assigned_suit
```

**Analysis**:
- When foundation is **empty**: Only checks if card is an Ace (value == 1)
- Does NOT check if ace's suit matches foundation's assigned suit
- When foundation is **non-empty**: Correctly checks suit + value
- Result: **Any ace accepted on any foundation**, but subsequent cards properly validated

### **Current Behavior (Wrong)**

```
Foundation Piles (Empty):
├─ Pile 7 (Cuori)   → Accepts ANY ace (♥♦♣♠)
├─ Pile 8 (Quadri)  → Accepts ANY ace (♥♦♣♠)
├─ Pile 9 (Fiori)   → Accepts ANY ace (♥♦♣♠)
└─ Pile 10 (Picche) → Accepts ANY ace (♥♦♣♠)

After first ace placed:
└─ Pile 10 (has Ace♣) → Only accepts 2♣ (correct!)
                      → Rejects 2♠ (correct!)
```

### **Expected Behavior (Fixed)**

```
Foundation Piles (Empty):
├─ Pile 7 (Cuori)   → Only accepts Ace♥
├─ Pile 8 (Quadri)  → Only accepts Ace♦
├─ Pile 9 (Fiori)   → Only accepts Ace♣
└─ Pile 10 (Picche) → Only accepts Ace♠

After correct ace placed:
└─ Pile 9 (has Ace♣) → Only accepts 2♣ (correct!)
```

### **Architectural Decision: Fixed Assignment**

**Two possible approaches**:

#### **Approach A: Dynamic Assignment** (Rejected)
- Empty foundation accepts any ace
- First ace determines foundation's suit
- Flexible but confusing (piles labeled "Cuori", etc.)

#### **Approach B: Fixed Assignment** (✅ Selected)
- Each foundation has fixed assigned suit from start
- Empty foundation only accepts ace of that suit
- Clear, predictable, matches TTS announcements

**Rationale**: 
- Piles already named "Pila semi Cuori", "Pila semi Quadri", etc.
- User expects Cuori pile to only contain hearts
- Consistent with traditional Solitaire rules

### **Solution Architecture**

#### **Step 1**: Add `assigned_suit` to Pile model

**File**: `src/domain/models/pile.py`

```python
class Pile:
    """Represents a pile of cards."""
    
    def __init__(
        self, 
        name: str = "Pila senza nome", 
        pile_type: str = "unknown",
        assigned_suit: Optional[str] = None  # NEW PARAMETER
    ) -> None:
        self.cards: List[Card] = []
        self.name: str = name
        self.pile_type: str = pile_type
        self.assigned_suit: Optional[str] = assigned_suit  # NEW ATTRIBUTE
```

#### **Step 2**: Assign fixed suits to foundations

**File**: `src/domain/models/table.py`

```python
# Line ~42-46 REPLACE WITH:
# 4 foundation piles (one per suit) with FIXED suit assignment
self.pile_semi: List[Pile] = [
    Pile(name="Pila semi Cuori", pile_type="semi", assigned_suit="Cuori"),
    Pile(name="Pila semi Quadri", pile_type="semi", assigned_suit="Quadri"),
    Pile(name="Pila semi Fiori", pile_type="semi", assigned_suit="Fiori"),
    Pile(name="Pila semi Picche", pile_type="semi", assigned_suit="Picche")
]
```

**Important**: Suit names must match `Card.get_suit` return values!

#### **Step 3**: Validate ace suit in rules

**File**: `src/domain/rules/solitaire_rules.py`

```python
# Line ~125-130 REPLACE WITH:
def can_place_on_foundation(self, card: Card, target_pile: Pile) -> bool:
    """Check if a card can be placed on a foundation pile."""
    
    # CRITICAL: Empty foundation accepts only Aces OF THE CORRECT SUIT
    if target_pile.is_empty():
        is_ace = card.get_value == 1
        
        # If pile has assigned suit, validate it
        if target_pile.assigned_suit is not None:
            correct_suit = card.get_suit == target_pile.assigned_suit
            return is_ace and correct_suit
        
        # No assigned suit (backward compatibility)
        return is_ace
```

### **Suit Name Consistency Check**

Must verify that suit names match across:

**Card.get_suit** (property in card.py):
```python
@property
def get_suit(self) -> str:
    return self.suit  # Returns: "Cuori", "Quadri", "Fiori", "Picche"
```

**FrenchDeck** (src/domain/models/deck.py):
```python
SEMI = ["Cuori", "Quadri", "Fiori", "Picche"]  # ✓ Match!
```

**NeapolitanDeck** (same file):
```python
SEMI = ["Denari", "Coppe", "Spade", "Bastoni"]  # Different names!
```

**⚠️ CRITICAL**: Neapolitan deck has different suit names!

**Solution**: Foundation assigned_suit must be deck-agnostic or use indices

**Alternative Implementation** (Index-Based):
```python
# table.py - Use suit indices instead of names
self.pile_semi: List[Pile] = [
    Pile(name=f"Pila semi {suit}", pile_type="semi", assigned_suit_index=i)
    for i, suit in enumerate(["Cuori", "Quadri", "Fiori", "Picche"])
]

# solitaire_rules.py - Validate by index
if target_pile.assigned_suit_index is not None:
    correct_suit = self._get_suit_index(card) == target_pile.assigned_suit_index
```

**Decision**: Use **name-based** but map dynamically:
```python
# In table.py
deck_suits = self.mazzo.SEMI  # Get suits from deck
self.pile_semi: List[Pile] = [
    Pile(name=f"Pila semi {suit}", pile_type="semi", assigned_suit=suit)
    for suit in deck_suits
]
```

### **Code Changes Required**

#### **File 1**: `src/domain/models/pile.py`

**Change 1** - Add assigned_suit parameter:
```python
# Line ~20-26 (modify __init__)
def __init__(
    self, 
    name: str = "Pila senza nome", 
    pile_type: str = "unknown",
    assigned_suit: Optional[str] = None  # NEW
) -> None:
    """Initialize a pile.
    
    Args:
        name: Human-readable name for the pile (for TTS feedback)
        pile_type: Type identifier ("base", "semi", "mazzo", "scarti")
        assigned_suit: Fixed suit for foundation piles (e.g., "Cuori")
    """
    self.cards: List[Card] = []
    self.name: str = name
    self.pile_type: str = pile_type
    self.assigned_suit: Optional[str] = assigned_suit  # NEW
```

**Change 2** - Add import for Optional:
```python
# Line ~7 (modify import)
from typing import List, Optional  # Add Optional
```

#### **File 2**: `src/domain/models/table.py`

**Change 1** - Assign suits dynamically from deck:
```python
# Line ~39-46 REPLACE WITH:
# 4 foundation piles (one per suit) with FIXED suit assignment from deck
deck_suits = deck.SEMI  # Get suit names from deck (French or Neapolitan)
self.pile_semi: List[Pile] = [
    Pile(
        name=f"Pila semi {suit}", 
        pile_type="semi", 
        assigned_suit=suit
    )
    for suit in deck_suits
]
```

#### **File 3**: `src/domain/rules/solitaire_rules.py`

**Change 1** - Add suit validation for empty foundations:
```python
# Line ~125-135 REPLACE WITH:
def can_place_on_foundation(self, card: Card, target_pile: Pile) -> bool:
    """Check if a card can be placed on a foundation pile.
    
    Rules:
    - Empty pile: only Aces (value == 1) OF THE CORRECT SUIT
    - Non-empty pile: same suit + ascending value (value + 1)
    
    Args:
        card: Card to place
        target_pile: Target foundation pile
        
    Returns:
        True if move is valid
    """
    # CRITICAL: Empty foundation accepts only Aces OF CORRECT SUIT
    if target_pile.is_empty():
        is_ace = card.get_value == 1
        
        # Validate suit if pile has assigned suit
        if target_pile.assigned_suit is not None:
            correct_suit = card.get_suit == target_pile.assigned_suit
            return is_ace and correct_suit
        
        # No assigned suit (backward compatibility for tests)
        return is_ace
    
    # Non-empty foundation: get top card
    top_card = target_pile.get_top_card()
    if top_card is None:
        return False
    
    # Must be same suit AND ascend by 1 (unchanged)
    return (
        card.get_suit == top_card.get_suit and
        card.get_value == top_card.get_value + 1
    )
```

### **Testing Verification**

**Test Case 1**: Ace on Correct Foundation
```
1. Get Ace of Hearts (Asso di Cuori)
2. Navigate to Hearts foundation (SHIFT+1)
3. Move Ace → MUST BE ACCEPTED
4. TTS: "Carta spostata: Asso di Cuori su Pila semi Cuori"
```

**Test Case 2**: Ace on Wrong Foundation (Blocked)
```
1. Get Ace of Clubs (Asso di Fiori)
2. Navigate to Spades foundation (SHIFT+4)
3. Try to move Ace → MUST BE REJECTED
4. TTS: "Mossa non valida per fondazione"
```

**Test Case 3**: All Four Aces Correct Placement
```
1. Place Ace♥ on Pile 7 (Cuori) → ✓
2. Place Ace♦ on Pile 8 (Quadri) → ✓
3. Place Ace♣ on Pile 9 (Fiori) → ✓
4. Place Ace♠ on Pile 10 (Picche) → ✓
```

**Test Case 4**: Cross-Suit Rejection
```
1. Ace♣ on Pile 7 (Cuori) → ✗
2. Ace♥ on Pile 9 (Fiori) → ✗
3. Ace♦ on Pile 10 (Picche) → ✗
```

**Test Case 5**: Subsequent Cards Correct
```
1. Place Ace♣ on Pile 9 (Fiori) → ✓
2. Place 2♣ on Ace♣ → ✓
3. Try 2♠ on Ace♣ → ✗ (different suit)
4. Try 3♣ on 2♣ → ✗ (skip value)
5. Place 3♣ on 2♣ → ✓
```

**Test Case 6**: Neapolitan Deck Suit Names
```
1. Change deck to Napoletane
2. New game
3. Verify foundations named: "Denari", "Coppe", "Spade", "Bastoni"
4. Test Asso placement with correct deck suit names
```

---

## 📦 IMPLEMENTATION PLAN

### **Phase 1**: Bug #1 (Deck Type)
- **Files**: `game_engine.py`, `test.py`, `gameplay_controller.py`
- **Lines**: ~40 total
- **Complexity**: LOW (parameter passing)
- **Dependencies**: None
- **Testing**: Manual deck selection

### **Phase 2**: Bug #2 (Ace Validation)
- **Files**: `pile.py`, `table.py`, `solitaire_rules.py`
- **Lines**: ~25 total
- **Complexity**: MEDIUM (domain logic)
- **Dependencies**: Phase 1 complete (for Neapolitan deck testing)
- **Testing**: Manual ace placement

### **Commit Strategy**

**Commit #29**: `fix(game): Apply deck type from settings`
```
- Add GameSettings parameter to GameEngine.create()
- Read deck_type from settings
- Instantiate FrenchDeck or NeapolitanDeck dynamically
- Pass settings from test.py to engine
- Import NeapolitanDeck in game_engine.py

Files modified:
- src/application/game_engine.py
- test.py
- src/application/gameplay_controller.py

Fixes: #BUG-001 (Mazzo napoletano non applicato)
```

**Commit #30**: `fix(rules): Validate ace suit in foundation placement`
```
- Add assigned_suit attribute to Pile model
- Assign fixed suits to foundation piles from deck
- Validate ace suit in can_place_on_foundation()
- Support both French and Neapolitan deck suit names

Files modified:
- src/domain/models/pile.py
- src/domain/models/table.py
- src/domain/rules/solitaire_rules.py

Fixes: #BUG-002 (Asso accettato su seme sbagliato)
```

---

## 🚨 EDGE CASES & CONSIDERATIONS

### **Edge Case 1**: Settings Modified During Gameplay
**Scenario**: User opens options mid-game and changes deck  
**Current Behavior**: Blocked by `validate_not_running()`  
**Fix**: Already handled ✓

### **Edge Case 2**: No Settings Provided to Engine
**Scenario**: Legacy code calls `GameEngine.create()` without settings  
**Expected**: Default to French deck (backward compatible)  
**Implementation**: `settings: Optional[GameSettings] = None` + fallback  
**Fix**: Included in solution ✓

### **Edge Case 3**: Foundation Already Has Wrong Ace
**Scenario**: Bug already occurred, pile has Ace♣ but labeled "Picche"  
**Impact**: Subsequent 2♣ correctly rejected (suit mismatch)  
**Solution**: User must restart game after fix applied  
**Documentation**: Add to CHANGELOG ✓

### **Edge Case 4**: Neapolitan Deck Suit Ordering
**French**: Cuori, Quadri, Fiori, Picche  
**Neapolitan**: Denari, Coppe, Spade, Bastoni  
**Solution**: Foundation piles use `deck.SEMI` dynamically  
**Testing**: Verify SHIFT+1-4 navigation works correctly ✓

### **Edge Case 5**: Unit Tests with Unassigned Suits
**Scenario**: Existing tests create Pile() without assigned_suit  
**Expected**: Tests should still pass (backward compatibility)  
**Implementation**: `assigned_suit=None` (optional parameter)  
**Validation**: Only applied when assigned_suit is not None  
**Fix**: Included in solution ✓

---

## 📊 BEFORE/AFTER COMPARISON

### **Bug #1: Deck Type Selection**

**BEFORE** ❌:
```python
# User selects Napoletane in options
settings.deck_type = "neapolitan"  # Saved!

# Engine creation ignores settings
engine = GameEngine.create()
    └─> deck = FrenchDeck()  # Always French!

# Result: French deck used despite user preference
```

**AFTER** ✅:
```python
# User selects Napoletane in options
settings.deck_type = "neapolitan"  # Saved!

# Engine creation reads settings
engine = GameEngine.create(settings=settings)
    └─> if settings.deck_type == "neapolitan":
            deck = NeapolitanDeck()  # Correct!

# Result: Neapolitan deck used as configured
```

### **Bug #2: Ace Foundation Validation**

**BEFORE** ❌:
```python
# User has Ace of Clubs (Asso di Fiori)
# Cursor on Spades foundation (Pila semi Picche)

can_place_on_foundation(Ace♣, Pile_Picche_Empty):
    if target_pile.is_empty():
        return card.get_value == 1  # True (it's an ace)
        # Missing: Check if suit matches!

# Result: Ace♣ placed on Spades foundation (WRONG!)

# Next card: 2♣
can_place_on_foundation(2♣, Pile_Picche_Has_Ace♣):
    top = Ace♣
    return (2♣.suit == Ace♣.suit and 2♣.value == Ace♣.value + 1)
    # "Fiori" == "Fiori" ✓, but pile labeled "Picche" (confusing!)
```

**AFTER** ✅:
```python
# User has Ace of Clubs (Asso di Fiori)
# Cursor on Spades foundation (Pila semi Picche, assigned_suit="Picche")

can_place_on_foundation(Ace♣, Pile_Picche_Empty):
    if target_pile.is_empty():
        is_ace = card.get_value == 1  # True
        if target_pile.assigned_suit:
            correct_suit = card.get_suit == target_pile.assigned_suit
            # "Fiori" == "Picche" → False!
        return is_ace and correct_suit  # False

# Result: Ace♣ rejected on Spades foundation ✓

# Try correct foundation (Pile Fiori, assigned_suit="Fiori")
can_place_on_foundation(Ace♣, Pile_Fiori_Empty):
    is_ace = True
    correct_suit = "Fiori" == "Fiori"  # True!
    return True

# Result: Ace♣ accepted on Clubs foundation ✓
```

---

## 🎯 SUCCESS CRITERIA

### **Bug #1 Fixed**:
- ✅ Neapolitan deck selected in options
- ✅ New game uses 40 cards (not 52)
- ✅ TTS announces "Carte Napoletane"
- ✅ King value = 10 (Neapolitan Re, not French King=13)
- ✅ Settings persist across game sessions

### **Bug #2 Fixed**:
- ✅ Ace♥ only accepted on Hearts foundation
- ✅ Ace♦ only accepted on Diamonds foundation
- ✅ Ace♣ only accepted on Clubs foundation
- ✅ Ace♠ only accepted on Spades foundation
- ✅ Wrong suit ace placement gives TTS error
- ✅ Correct validation for both French and Neapolitan decks
- ✅ Existing tests still pass (backward compatible)

---

## 📝 NOTES FOR IMPLEMENTATION

### **Import Additions Needed**

**game_engine.py**:
```python
from typing import Optional  # Add if not present
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.services.game_settings import GameSettings
```

**test.py**:
```python
from src.domain.services.game_settings import GameSettings
```

**pile.py**:
```python
from typing import List, Optional  # Add Optional
```

### **Type Hints to Verify**

All new parameters use proper type hints:
- `settings: Optional[GameSettings] = None`
- `assigned_suit: Optional[str] = None`

### **Backward Compatibility**

Both fixes maintain backward compatibility:
- Engine.create() works without settings (defaults to French)
- Pile() works without assigned_suit (None = no validation)

---

## 🔗 RELATED ISSUES

- **#BUG-001**: Mazzo napoletano non applicato (OPEN → Will fix)
- **#BUG-002**: Asso accettato su seme sbagliato (OPEN → Will fix)
- **#FEATURE-08**: GameSettings integration (DONE - v1.4.1)
- **#FEATURE-09**: OptionsWindowController (DONE - v1.4.1)

---

**END OF PLAN** - Ready for implementation! 🚀
