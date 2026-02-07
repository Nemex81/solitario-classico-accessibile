## 🎯 **PIANO IMPLEMENTAZIONE INCREMENTALE - MIGRAZIONE `scr/` → `src/`**

### 📋 **OBIETTIVO FINALE**
Migrare tutte le funzionalità da `scr/` a `src/` con architettura Clean Architecture, mantenendo `acs.py` legacy funzionante e usando `test.py` come nuovo entry point.

***

## 🏗️ **FASE 1: DOMAIN LAYER - MODELS FONDAMENTALI**

### **Commit 1: Migra ProtoDeck e implementazioni concrete**
**Branch:** `feature/migrate-decks-to-domain`

**Obiettivo:** Portare `scr/decks.py` → `src/domain/models/deck.py` con tutti i fix recenti

**File da creare/modificare:**
- `src/domain/models/deck.py` (NUOVO)

**Implementazione:**
```python
# src/domain/models/deck.py

"""Domain models for card decks.

This module contains the base ProtoDeck class and concrete implementations
for French and Neapolitan card decks, migrated from legacy scr/decks.py
with all recent fixes including is_king() method for correct King validation.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random

from src.domain.models.card import Card


class ProtoDeck:
    """Base model for card deck management.
    
    Supports different deck types (French, Neapolitan) with polymorphic
    behavior for deck-specific rules like King validation.
    """
    
    SUITES: List[str] = []
    VALUES: List[str] = []
    FIGURE_VALUES: dict = {}
    
    def __init__(self):
        self.cards: List[Card] = []
        self.tipo: Optional[str] = None
    
    # [COPIARE TUTTI I METODI DA scr/decks.py]
    # - get_suits()
    # - crea()
    # - pesca()
    # - mischia()
    # - is_king() ← IMPORTANTE! Fix recente
    # - get_total_cards()
    # - reset()
    # ... ecc
```

**Checklist:**
- [ ] Copia classe `ProtoDeck` completa da `scr/decks.py` (SHA: cb52fbf)
- [ ] Copia classe `FrenchDeck` completa
- [ ] Copia classe `NeapolitanDeck` completa
- [ ] Includi metodo `is_king()` (fix Re napoletano valore 10)
- [ ] Aggiorna import: `from src.domain.models.card import Card`
- [ ] Rimuovi dipendenze da `my_lib` (sostituire con logica locale)
- [ ] Aggiungi docstrings Python per ogni metodo
- [ ] Aggiungi type hints completi

**Testing:**
- [ ] Test unitari per `is_king()` con entrambi i mazzi
- [ ] Test creazione mazzo completo (52 carte francese, 40 napoletane)
- [ ] Test mischia/pesca/reset

**Commit Message:**
```
feat(domain): Migrate deck models from scr/ with is_king() fix

- Add src/domain/models/deck.py with ProtoDeck base class
- Implement FrenchDeck (52 cards) and NeapolitanDeck (40 cards)
- Include is_king() method for correct King validation (fixes #28)
- French King value: 13, Neapolitan King value: 10
- Add full type hints and docstrings
- Remove legacy my_lib dependencies

Migrated from: scr/decks.py (SHA: cb52fbf)
Related: #29 (v1.3.3 hotfix)
```

***

### **Commit 2: Migra game_table con logica pile e distribuzione**
**Branch:** `feature/migrate-game-table-to-domain`

**Obiettivo:** Portare `scr/game_table.py` → `src/domain/models/table.py` + aggiornare `pile.py`

**File da creare/modificare:**
- `src/domain/models/table.py` (NUOVO)
- `src/domain/models/pile.py` (AGGIORNARE - già esiste)

**Implementazione:**
```python
# src/domain/models/table.py

"""Domain model for game table with card piles.

Manages the 7 base piles, 4 foundation piles, stock and waste piles.
Includes logic for card distribution and pile validation.
"""

from typing import List, Optional
from dataclasses import dataclass

from src.domain.models.pile import Pile
from src.domain.models.deck import ProtoDeck
from src.domain.models.card import Card


class GameTable:
    """Represents the solitaire game table with all piles.
    
    Structure:
    - pile_base[0-6]: 7 tableau piles (1-7 cards each)
    - pile_semi[0-3]: 4 foundation piles (by suit)
    - pile_mazzo: stock pile
    - pile_scarti: waste pile
    """
    
    def __init__(self, deck: ProtoDeck):
        self.mazzo = deck
        self.pile_base: List[Pile] = []
        self.pile_semi: List[Pile] = []
        self.pile_mazzo: Optional[Pile] = None
        self.pile_scarti: Optional[Pile] = None
    
    # [COPIARE METODI DA scr/game_table.py]
    # - crea_pile_gioco()
    # - distribuisci_carte() ← Fix dinamico 12/24 carte
    # - put_to_base() ← Usa mazzo.is_king(card)
    # - verifica_vittoria() ← Fix range(7, 11)
    # ... ecc
```

**Checklist:**
- [ ] Copia classe `Tavolo` → rinomina `GameTable` da `scr/game_table.py` (SHA: bc810ba)
- [ ] Aggiorna `distribuisci_carte()` con calcolo dinamico carte riserve
- [ ] Aggiorna `put_to_base()` per usare `self.mazzo.is_king(card)`
- [ ] Aggiungi `verifica_vittoria()` con fix `range(7, 11)` per 4 pile
- [ ] Integra con `src/domain/models/pile.py` esistente
- [ ] Rimuovi dipendenze legacy
- [ ] Type hints completi

**Testing:**
- [ ] Test distribuzione 28 carte + riserve (24 francese, 12 napoletano)
- [ ] Test Re su pila vuota (entrambi i mazzi)
- [ ] Test verifica vittoria con 4 pile complete

**Commit Message:**
```
feat(domain): Migrate game table with dynamic card distribution

- Add src/domain/models/table.py with GameTable class
- Implement dynamic reserve calculation (52-28=24 or 40-28=12)
- Use deck.is_king() for empty pile validation
- Fix verifica_vittoria() to check all 4 foundation piles
- Integration with existing Pile model

Migrated from: scr/game_table.py (SHA: bc810ba)
Fixes: #25 (IndexError on deck switching)
Related: #26, #28, #29
```

***

## 🏗️ **FASE 2: DOMAIN LAYER - RULES & SERVICES**

### **Commit 3: Estrai regole di validazione mosse da game_engine**
**Branch:** `feature/extract-move-validation-rules`

**Obiettivo:** Estrarre logica validazione mosse da `scr/game_engine.py` → `src/domain/rules/`

**File da creare/modificare:**
- `src/domain/rules/solitaire_rules.py` (NUOVO)
- Aggiornare `src/domain/rules/move_validator.py` (già esiste)

**Implementazione:**
```python
# src/domain/rules/solitaire_rules.py

"""Solitaire game rules and move validation logic.

Extracted from legacy game_engine.py to separate business rules
from application logic.
"""

from typing import Optional
from src.domain.models.card import Card
from src.domain.models.pile import Pile
from src.domain.models.deck import ProtoDeck


class SolitaireRules:
    """Business rules for classic solitaire game."""
    
    def __init__(self, deck: ProtoDeck):
        self.deck = deck
    
    def can_place_on_base_pile(
        self, 
        card: Card, 
        target_pile: Pile
    ) -> bool:
        """Validate if card can be placed on tableau pile.
        
        Rules:
        - Empty pile: only Kings allowed (deck-specific value)
        - Non-empty: alternating colors, descending values
        """
        if target_pile.is_empty():
            return self.deck.is_king(card)
        
        top_card = target_pile.get_top_card()
        # ... logica colori alternati e valori decrescenti
    
    def can_place_on_foundation(
        self,
        card: Card,
        target_pile: Pile
    ) -> bool:
        """Validate if card can be placed on foundation pile.
        
        Rules:
        - Empty pile: only Aces
        - Non-empty: same suit, ascending values
        """
        # ... implementazione
    
    # [ALTRI METODI DA ESTRARRE DA game_engine.py]
    # - can_move_sequence()
    # - is_valid_auto_move()
    # - check_win_condition()
```

**Checklist:**
- [ ] Identifica metodi validazione in `scr/game_engine.py` (linee ~200-600)
- [ ] Estrai logica pura senza side effects
- [ ] Metodi stateless che ricevono stato come parametri
- [ ] Integra con `MoveValidator` esistente
- [ ] Type hints e docstrings completi

**Testing:**
- [ ] Test alternanza colori (rosso/nero)
- [ ] Test valori decrescenti/crescenti
- [ ] Test King su pila vuota (entrambi mazzi)
- [ ] Test Asso su fondazione vuota

**Commit Message:**
```
feat(domain/rules): Extract move validation logic from game_engine

- Add src/domain/rules/solitaire_rules.py
- Extract pure business rules from legacy monolithic engine
- Stateless validation methods with explicit parameters
- Support for deck-specific rules (King values)
- Integration with existing MoveValidator

Extracted from: scr/game_engine.py (lines 200-600)
```

***

### **Commit 4: Migra logica gameplay core a game_service**
**Branch:** `feature/migrate-gameplay-logic-to-service`

**Obiettivo:** Estrarre logica gameplay da `scr/game_engine.py` → `src/domain/services/game_service.py`

**File da modificare:**
- `src/domain/services/game_service.py` (AGGIORNARE - già esiste)

**Implementazione:**
```python
# src/domain/services/game_service.py (AGGIORNARE)

"""Domain service for game state management.

Orchestrates game logic using domain models and rules.
"""

from typing import Optional, List, Tuple
from src.domain.models.table import GameTable
from src.domain.models.card import Card
from src.domain.rules.solitaire_rules import SolitaireRules


class GameService:
    """Core game logic service."""
    
    def __init__(self, table: GameTable, rules: SolitaireRules):
        self.table = table
        self.rules = rules
        self.move_count = 0
        self.start_time: Optional[float] = None
    
    # [METODI DA MIGRARE DA game_engine.py]
    def move_card(
        self,
        source_pile_idx: int,
        target_pile_idx: int,
        card_count: int = 1
    ) -> Tuple[bool, str]:
        """Move card(s) from source to target pile.
        
        Returns:
            (success, message)
        """
        # Validazione con rules
        # Esecuzione mossa
        # Aggiornamento stato
    
    def draw_cards(self, count: int = 1) -> List[Card]:
        """Draw cards from stock to waste pile."""
        # ... implementazione
    
    def auto_move_to_foundation(self) -> bool:
        """Attempt automatic move to foundation piles."""
        # ... implementazione
    
    def check_game_over(self) -> Tuple[bool, str]:
        """Check if game is won, lost, or still playable."""
        # Usa table.verifica_vittoria()
        # Controlla timer (se abilitato)
```

**Checklist:**
- [ ] Estrai metodi gameplay da `scr/game_engine.py` (linee ~600-1200)
- [ ] Integra con `GameTable` e `SolitaireRules`
- [ ] Gestione stato partita (mosse, tempo, punteggio)
- [ ] Metodi per statistiche dinamiche (pile semi)
- [ ] Separare logica da UI/presentazione

**Testing:**
- [ ] Test sequenza mosse valide/invalide
- [ ] Test pesca carte e rimescolamento
- [ ] Test auto-move fondazioni
- [ ] Test check vittoria (4 pile complete)

**Commit Message:**
```
feat(domain/services): Migrate core gameplay logic to GameService

- Extend src/domain/services/game_service.py with game orchestration
- Add move_card(), draw_cards(), auto_move_to_foundation()
- Integrate with GameTable and SolitaireRules
- Track game state: moves, time, score
- Support dynamic statistics for both deck types

Migrated from: scr/game_engine.py (lines 600-1200, SHA: b47634e)
```

***

## 🏗️ **FASE 3: INFRASTRUCTURE LAYER**

### **Commit 5: Migra ScreenReader a infrastructure/accessibility**
**Branch:** `feature/migrate-screen-reader-to-infrastructure`

**Obiettivo:** `scr/screen_reader.py` → `src/infrastructure/accessibility/screen_reader.py`

**File da creare/modificare:**
- `src/infrastructure/accessibility/screen_reader.py` (NUOVO)
- `src/infrastructure/accessibility/__init__.py` (AGGIORNARE)

**Implementazione:**
```python
# src/infrastructure/accessibility/screen_reader.py

"""Screen reader integration for accessibility.

Provides text-to-speech functionality using platform-specific APIs.
Migrated from legacy scr/screen_reader.py with zero functional changes.
"""

from typing import Optional
import platform

# Import platform-specific TTS libraries
# ... (mantenere logica esistente)


class ScreenReader:
    """Screen reader adapter for voice output.
    
    Supports:
    - Windows: SAPI/Narrator
    - macOS: AVSpeechSynthesizer
    - Linux: espeak/speech-dispatcher
    """
    
    def __init__(self):
        self.platform = platform.system()
        self._initialize_engine()
    
    def vocalizza(self, text: str, interrupt: bool = True) -> None:
        """Speak text using platform TTS."""
        # [COPIA ESATTA DA scr/screen_reader.py]
    
    # ... altri metodi invariati
```

**Checklist:**
- [ ] Copia `scr/screen_reader.py` → `src/infrastructure/accessibility/` (SHA: 38a7e08)
- [ ] **ZERO modifiche logica** (funziona, non toccare!)
- [ ] Aggiorna solo import paths se necessario
- [ ] Mantieni compatibilità API esatta
- [ ] Type hints e docstrings

**Testing:**
- [ ] Test inizializzazione su ogni piattaforma
- [ ] Test vocalizzazione base
- [ ] Test interrupt/queue

**Commit Message:**
```
feat(infrastructure): Migrate ScreenReader to accessibility layer

- Move scr/screen_reader.py → src/infrastructure/accessibility/
- Zero functional changes (working module, preserve behavior)
- Add type hints and docstrings
- Platform-agnostic TTS adapter (Windows/macOS/Linux)

Migrated from: scr/screen_reader.py (SHA: 38a7e08)
No breaking changes.
```

***

### **Commit 6: Migra PyGame UI components a infrastructure/ui**
**Branch:** `feature/migrate-pygame-ui-to-infrastructure`

**Obiettivo:** `scr/pygame_menu.py` → `src/infrastructure/ui/menu.py`

**File da creare/modificare:**
- `src/infrastructure/ui/menu.py` (NUOVO)
- `src/infrastructure/ui/__init__.py` (AGGIORNARE)

**Implementazione:**
```python
# src/infrastructure/ui/menu.py

"""PyGame menu UI component.

Simple keyboard-navigable menu for game options.
"""

import pygame
from typing import List, Callable, Optional

from src.infrastructure.accessibility.screen_reader import ScreenReader


class PyGameMenu:
    """Menu component with screen reader support."""
    
    def __init__(
        self,
        items: List[str],
        callback: Callable[[int], None],
        screen: pygame.Surface,
        screen_reader: Optional[ScreenReader] = None
    ):
        self.items = items
        self.callback = callback
        self.screen = screen
        self.screen_reader = screen_reader
        self.selected_index = 0
    
    # [COPIA METODI DA scr/pygame_menu.py]
    def next_item(self) -> None:
        """Move to next menu item."""
    
    def prev_item(self) -> None:
        """Move to previous menu item."""
    
    def execute(self) -> None:
        """Execute selected item callback."""
    
    def handle_keyboard_events(self, event: pygame.event.Event) -> None:
        """Handle keyboard input."""
```

**Checklist:**
- [ ] Copia `scr/pygame_menu.py` → `src/infrastructure/ui/menu.py` (SHA: af78880)
- [ ] Mantieni compatibilità API
- [ ] Integra con nuovo path ScreenReader
- [ ] Type hints completi

**Commit Message:**
```
feat(infrastructure/ui): Migrate PyGame menu component

- Move scr/pygame_menu.py → src/infrastructure/ui/menu.py
- Rename PyMenu → PyGameMenu for clarity
- Update ScreenReader import path
- Add type hints and docstrings

Migrated from: scr/pygame_menu.py (SHA: af78880)
```

***

## 🏗️ **FASE 4: APPLICATION LAYER**

### **Commit 7: Migra event handling e gameplay orchestration**
**Branch:** `feature/migrate-game-play-to-application`

**Obiettivo:** `scr/game_play.py` → Integra in `src/application/game_controller.py`

**File da modificare:**
- `src/application/game_controller.py` (AGGIORNARE - già esiste)
- `src/application/input_handler.py` (NUOVO)

**Implementazione:**
```python
# src/application/input_handler.py (NUOVO)

"""Input handling for game commands.

Maps keyboard events to game commands with support for
modifiers (SHIFT, CTRL) and accessibility shortcuts.
"""

import pygame
from typing import Callable, Dict
from enum import Enum


class GameCommand(Enum):
    """Available game commands."""
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    SELECT_CARD = "select_card"
    DRAW_CARDS = "draw_cards"
    # ... altri comandi
    QUICK_ACCESS_PILE_1 = "quick_pile_1"  # SHIFT+1 (v1.3.0)
    # ... ecc


class InputHandler:
    """Handles keyboard input and command dispatch."""
    
    def __init__(self):
        self.key_bindings: Dict[int, GameCommand] = {}
        self._initialize_bindings()
    
    def _initialize_bindings(self) -> None:
        """Setup default keyboard bindings."""
        # Arrow keys, number keys, function keys
        # SHIFT+1-4 per fondazioni (v1.3.0)
        # SHIFT+S/M per scarti/mazzo (v1.3.0)
    
    def handle_event(
        self,
        event: pygame.event.Event
    ) -> Optional[GameCommand]:
        """Convert pygame event to game command."""
        # Gestione SHIFT/CTRL modifiers
        # Double-tap detection (v1.3.0)


# src/application/game_controller.py (AGGIORNARE)

class GameController:
    """Application controller orchestrating game flow."""
    
    def __init__(
        self,
        game_service: GameService,
        formatter: GameFormatter,
        input_handler: InputHandler
    ):
        self.game_service = game_service
        self.formatter = formatter
        self.input_handler = input_handler
    
    # [METODI DA MIGRARE DA game_play.py]
    def handle_command(self, command: GameCommand) -> str:
        """Execute game command and return feedback message."""
        # Chiama game_service
        # Formatta risposta con formatter
        # Restituisce messaggio per screen reader
```

**Checklist:**
- [ ] Estrai logica input da `scr/game_play.py` (SHA: 3af5ecc)
- [ ] Crea `InputHandler` per binding tastiera
- [ ] Supporta SHIFT+1-4, SHIFT+S, SHIFT+M (v1.3.0)
- [ ] Double-tap navigation (v1.3.0)
- [ ] Integra in `GameController` esistente
- [ ] Separa input handling da game logic

**Testing:**
- [ ] Test tutti i command binding
- [ ] Test SHIFT modifiers
- [ ] Test double-tap same pile

**Commit Message:**
```
feat(application): Migrate input handling and game orchestration

- Add src/application/input_handler.py for keyboard commands
- Extend GameController with command execution
- Support SHIFT shortcuts (v1.3.0 features)
- Double-tap navigation for quick access
- Separate input handling from game logic

Migrated from: scr/game_play.py (SHA: 3af5ecc)
Features: #19 (double-tap), #20 (SHIFT shortcuts)
```

***

### **Commit 8: Integra timer e difficoltà management**
**Branch:** `feature/add-timer-and-difficulty-management`

**Obiettivo:** Aggiungere gestione timer e difficoltà estratta da `game_engine.py`

**File da creare/modificare:**
- `src/application/game_settings.py` (NUOVO)
- `src/domain/services/game_service.py` (AGGIORNARE)

**Implementazione:**
```python
# src/application/game_settings.py

"""Game settings and configuration management.

Handles timer, difficulty, deck type, and other game options.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class DeckType(Enum):
    FRENCH = "french"
    NEAPOLITAN = "neapolitan"


class DrawMode(Enum):
    ONE_CARD = 1
    THREE_CARDS = 3


@dataclass
class GameSettings:
    """Game configuration settings."""
    
    deck_type: DeckType = DeckType.FRENCH
    draw_mode: DrawMode = DrawMode.THREE_CARDS
    timer_enabled: bool = False
    timer_duration_minutes: int = 10
    shuffle_discards: bool = False  # F5 toggle (v1.1.0)
    
    def toggle_shuffle_mode(self) -> bool:
        """Toggle shuffle/invert mode for discard pile."""
        self.shuffle_discards = not self.shuffle_discards
        return self.shuffle_discards


class TimerManager:
    """Manages game timer with F3 controls."""
    
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
    
    def start(self) -> None:
        """Start or resume timer."""
    
    def stop(self) -> float:
        """Stop timer and return elapsed time."""
    
    def get_remaining_time(self) -> Optional[int]:
        """Get remaining seconds if timer enabled."""
    
    def decrease_timer(self, minutes: int = 5) -> int:
        """F3: Decrease timer by N minutes."""
```

**Checklist:**
- [ ] Estrai logica timer da `scr/game_engine.py` (F2/F3/F4 handlers)
- [ ] Gestione difficoltà (1 o 3 carte)
- [ ] F5 toggle shuffle mode (v1.1.0)
- [ ] F1 cambio mazzo (francese/napoletano)
- [ ] Salvare impostazioni tra partite

**Testing:**
- [ ] Test timer start/stop/resume
- [ ] Test F3 decremento 5 minuti
- [ ] Test F5 toggle shuffle

**Commit Message:**
```
feat(application): Add timer and game settings management

- Add src/application/game_settings.py
- GameSettings dataclass with all options
- TimerManager for F2/F3/F4 controls
- Support F5 shuffle toggle (v1.1.0)
- Support F1 deck switching

Extracted from: scr/game_engine.py
Features: #15 (F3/F5), #24 (mazzo napoletano)
```

***

## 🏗️ **FASE 5: PRESENTATION LAYER**

### **Commit 9: Estendi formatter con statistiche dinamiche**
**Branch:** `feature/extend-formatter-with-stats`

**Obiettivo:** Aggiungere formattazione statistiche da `game_engine.py` → `game_formatter.py`

**File da modificare:**
- `src/presentation/game_formatter.py` (AGGIORNARE - già esiste)

**Implementazione:**
```python
# src/presentation/game_formatter.py (AGGIORNARE)

"""Game output formatting for screen reader.

Formats game state, moves, and statistics into Italian text.
"""

from typing import List
from src.domain.models.table import GameTable
from src.domain.models.deck import DeckType


class GameFormatter:
    """Formats game information for voice output."""
    
    def __init__(self, language: str = "it"):
        self.language = language
    
    # [METODI ESISTENTI]
    
    # [NUOVI METODI DA game_engine.py]
    def format_foundation_stats(
        self,
        table: GameTable
    ) -> str:
        """Format foundation piles statistics.
        
        Example: "Cuori: 5 su 13 (38%)"
        
        Dynamic for deck type (13 for French, 10 for Neapolitan).
        """
        stats = []
        max_cards = table.mazzo.get_total_cards() // 4
        
        for i, pile in enumerate(table.pile_semi):
            suit_name = table.mazzo.SUITES[i]
            count = pile.get_card_count()
            percentage = (count / max_cards) * 100
            stats.append(
                f"{suit_name.capitalize()}: {count} su {max_cards} "
                f"({percentage:.0f}%)"
            )
        
        return "\n".join(stats)
    
    def format_game_report(
        self,
        moves: int,
        time_elapsed: float,
        difficulty: str,
        foundation_stats: str
    ) -> str:
        """Format complete game statistics report."""
        # [LOGICA DA get_report_game() in game_engine.py]
```

**Checklist:**
- [ ] Estrai metodi formattazione da `scr/game_engine.py`
- [ ] `format_foundation_stats()` dinamico per tipo mazzo
- [ ] `format_game_report()` completo
- [ ] `format_move_hint()` per suggerimenti
- [ ] Supporto plurali/singolari italiano

**Testing:**
- [ ] Test formattazione statistiche francese (13 carte)
- [ ] Test formattazione statistiche napoletano (10 carte)
- [ ] Test report finale partita

**Commit Message:**
```
feat(presentation): Extend formatter with dynamic statistics

- Add format_foundation_stats() with deck-specific max values
- Add format_game_report() for complete game summary
- Dynamic formatting for French (13) and Neapolitan (10) decks
- Italian localization with proper plurals

Extracted from: scr/game_engine.py (statistics methods)
Related: #24 (mazzo napoletano stats)
```

***

## 🏗️ **FASE 6: ENTRY POINT E INTEGRAZIONE**

### **Commit 10: Crea nuovo entry point in test.py**
**Branch:** `feature/create-clean-arch-entry-point`

**Obiettivo:** Creare entry point completo in `test.py` usando architettura `src/`

**File da modificare:**
- `test.py` (RISCRIVERE COMPLETAMENTE)

**Implementazione:**
```python
# test.py

"""Entry point for Clean Architecture version.

Launches the solitaire game using src/ modules with proper
dependency injection and separation of concerns.

Usage:
    python test.py
"""

import sys
import pygame
from pygame.locals import QUIT

# Domain imports
from src.domain.models.deck import FrenchDeck, NeapolitanDeck
from src.domain.models.table import GameTable
from src.domain.rules.solitaire_rules import SolitaireRules

# Application imports
from src.application.game_settings import GameSettings, DeckType, TimerManager
from src.application.input_handler import InputHandler, GameCommand

# Infrastructure imports
from src.infrastructure.di_container import get_container
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.ui.menu import PyGameMenu

# Presentation imports
from src.presentation.game_formatter import GameFormatter


class SolitarioCleanArch:
    """Main application class using Clean Architecture."""
    
    def __init__(self):
        """Initialize application with dependency injection."""
        pygame.init()
        pygame.font.init()
        
        # Setup display
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Solitario Accessibile - Clean Architecture")
        self.screen.fill((255, 255, 255))
        pygame.display.flip()
        
        # Dependency Injection Container
        self.container = get_container()
        
        # Infrastructure
        self.screen_reader = ScreenReader()
        
        # Settings
        self.settings = GameSettings(
            deck_type=DeckType.FRENCH,
            timer_enabled=False
        )
        
        # Domain setup
        self.deck = self._create_deck(self.settings.deck_type)
        self.table = GameTable(self.deck)
        self.table.distribuisci_carte(self.deck)
        self.rules = SolitaireRules(self.deck)
        
        # Application setup
        self.game_controller = self.container.get_game_controller(language="it")
        self.input_handler = InputHandler()
        self.timer_manager = TimerManager(self.settings)
        
        # Presentation
        self.formatter = self.container.get_formatter(language="it")
        
        # Menu
        self.menu = PyGameMenu(
            items=["Gioca al solitario classico", "Esci dal gioco"],
            callback=self.handle_menu_selection,
            screen=self.screen,
            screen_reader=self.screen_reader
        )
        
        # State
        self.is_menu_open = True
        self.is_running = True
    
    def _create_deck(self, deck_type: DeckType):
        """Factory for deck creation."""
        if deck_type == DeckType.FRENCH:
            return FrenchDeck()
        elif deck_type == DeckType.NEAPOLITAN:
            return NeapolitanDeck()
        else:
            raise ValueError(f"Unknown deck type: {deck_type}")
    
    def handle_menu_selection(self, selected_item: int) -> None:
        """Handle menu item selection."""
        if selected_item == 0:
            self.is_menu_open = False
            self.start_game()
        elif selected_item == 1:
            self.quit_app()
    
    def start_game(self) -> None:
        """Start new game."""
        self.screen_reader.vocalizza("Nuova partita iniziata")
        if self.settings.timer_enabled:
            self.timer_manager.start()
    
    def handle_events(self) -> None:
        """Main event loop."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit_app()
                return
            
            if self.is_menu_open:
                self.menu.handle_keyboard_events(event)
            else:
                command = self.input_handler.handle_event(event)
                if command:
                    response = self.game_controller.handle_command(command)
                    if response:
                        self.screen_reader.vocalizza(response)
    
    def quit_app(self) -> None:
        """Clean shutdown."""
        self.screen_reader.vocalizza("Chiusura in corso")
        pygame.time.wait(500)
        self.is_running = False
        pygame.quit()
        sys.exit(0)
    
    def run(self) -> None:
        """Main game loop."""
        clock = pygame.time.Clock()
        
        while self.is_running:
            pygame.event.pump()
            self.handle_events()
            pygame.display.update()
            clock.tick(60)  # 60 FPS


def main():
    """Application entry point."""
    print("🎴 Solitario Accessibile - Clean Architecture Version")
    print("=" * 60)
    print("Entry point: test.py")
    print("Architecture: src/ (Clean Architecture)")
    print("Legacy: acs.py still available with scr/")
    print("=" * 60)
    
    app = SolitarioCleanArch()
    app.run()


if __name__ == "__main__":
    main()
```

**Checklist:**
- [ ] Inizializza tutti i layer (Domain → Application → Infrastructure → Presentation)
- [ ] Usa DI Container per orchestrazione
- [ ] Integra ScreenReader per accessibilità
- [ ] Menu iniziale funzionante
- [ ] Game loop completo con event handling
- [ ] Gestione graceful shutdown
- [ ] Commenti e docstrings esplicativi

**Testing:**
- [ ] Test avvio applicazione
- [ ] Test menu navigazione (UP/DOWN/ENTER)
- [ ] Test avvio partita
- [ ] Test comandi base (frecce, selezione, pesca)
- [ ] Test chiusura pulita

**Commit Message:**
```
feat: Create Clean Architecture entry point in test.py

- Complete application bootstrap with all layers
- Domain: Deck, Table, Rules
- Application: Controller, InputHandler, Settings
- Infrastructure: ScreenReader, PyGame UI, DI
- Presentation: Formatter

Full feature parity with scr/ legacy version:
- Menu navigation with screen reader
- Game loop with keyboard commands
- SHIFT shortcuts and double-tap (v1.3.0)
- Timer management (F2/F3/F4)
- Deck switching (F1)
- All v1.3.3 fixes included

Entry points:
- test.py: NEW Clean Architecture (src/)
- acs.py: LEGACY still working (scr/)

Ready for full migration testing.
```

***

### **Commit 11: Aggiorna DI Container con tutti i componenti**
**Branch:** `feature/update-di-container-complete`

**Obiettivo:** Completare `di_container.py` con factory per tutti i componenti

**File da modificare:**
- `src/infrastructure/di_container.py` (AGGIORNARE - già esiste)

**Implementazione:**
```python
# src/infrastructure/di_container.py (AGGIORNARE)

"""Dependency injection container - COMPLETE VERSION.

Manages creation and lifecycle of all application components.
"""

from typing import Any, Dict, cast, Optional

# Domain
from src.domain.models.deck import FrenchDeck, NeapolitanDeck, ProtoDeck
from src.domain.models.table import GameTable
from src.domain.rules.solitaire_rules import SolitaireRules

# Application
from src.application.commands import CommandHistory
from src.application.game_controller import GameController
from src.application.game_settings import GameSettings, DeckType, TimerManager
from src.application.input_handler import InputHandler

# Infrastructure
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.ui.menu import PyGameMenu

# Presentation
from src.presentation.game_formatter import GameFormatter

# Domain services
from src.domain.services.game_service import GameService


class DIContainer:
    """Complete dependency injection container."""
    
    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._settings: Optional[GameSettings] = None
    
    # [METODI GIÀ ESISTENTI]
    # - get_move_validator()
    # - get_game_service()
    # - get_formatter()
    # - get_command_history()
    # - get_game_controller()
    
    # [NUOVI METODI]
    
    def get_settings(self) -> GameSettings:
        """Get or create GameSettings singleton."""
        if self._settings is None:
            self._settings = GameSettings()
        return self._settings
    
    def get_deck(self, deck_type: DeckType) -> ProtoDeck:
        """Factory for deck creation."""
        if deck_type == DeckType.FRENCH:
            return FrenchDeck()
        elif deck_type == DeckType.NEAPOLITAN:
            return NeapolitanDeck()
        raise ValueError(f"Unknown deck type: {deck_type}")
    
    def get_table(self, deck: ProtoDeck) -> GameTable:
        """Create GameTable with deck."""
        return GameTable(deck)
    
    def get_rules(self, deck: ProtoDeck) -> SolitaireRules:
        """Get or create SolitaireRules for deck."""
        key = f"rules_{deck.tipo}"
        if key not in self._instances:
            self._instances[key] = SolitaireRules(deck)
        return cast(SolitaireRules, self._instances[key])
    
    def get_input_handler(self) -> InputHandler:
        """Get or create InputHandler singleton."""
        if "input_handler" not in self._instances:
            self._instances["input_handler"] = InputHandler()
        return cast(InputHandler, self._instances["input_handler"])
    
    def get_screen_reader(self) -> ScreenReader:
        """Get or create ScreenReader singleton."""
        if "screen_reader" not in self._instances:
            self._instances["screen_reader"] = ScreenReader()
        return cast(ScreenReader, self._instances["screen_reader"])
    
    def get_timer_manager(self, settings: Optional[GameSettings] = None) -> TimerManager:
        """Get or create TimerManager."""
        if "timer_manager" not in self._instances:
            if settings is None:
                settings = self.get_settings()
            self._instances["timer_manager"] = TimerManager(settings)
        return cast(TimerManager, self._instances["timer_manager"])
    
    # ... altri factory methods


# Global container
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get global DIContainer instance."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container() -> None:
    """Reset global container (useful for testing)."""
    global _container
    _container = None
```

**Checklist:**
- [ ] Factory methods per tutti i componenti Domain
- [ ] Factory methods per Application layer
- [ ] Factory methods per Infrastructure
- [ ] Gestione lifetime (singleton vs transient)
- [ ] Type hints completi

**Commit Message:**
```
feat(infrastructure): Complete DI container with all components

- Add factory methods for Domain models (Deck, Table, Rules)
- Add factory methods for Application (InputHandler, TimerManager)
- Add factory methods for Infrastructure (ScreenReader)
- Proper lifetime management (singletons vs factories)
- Full type safety with casts

Complete container for Clean Architecture bootstrap.
```

***

## 🏗️ **FASE 7: TESTING E FINALIZZAZIONE**

### **Commit 12: Aggiungi test di integrazione end-to-end**
**Branch:** `feature/add-integration-tests`

**Obiettivo:** Test completi per verificare migrazione corretta

**File da creare:**
- `tests/integration/test_clean_arch_bootstrap.py` (NUOVO)
- `tests/integration/test_feature_parity.py` (NUOVO)

**Implementazione:**
```python
# tests/integration/test_clean_arch_bootstrap.py

"""Integration tests for Clean Architecture bootstrap.

Verifies that all components wire together correctly and
the application can start without errors.
"""

import pytest
import pygame

from src.infrastructure.di_container import get_container, reset_container


class TestCleanArchBootstrap:
    """Test complete application bootstrap."""
    
    def setup_method(self):
        """Reset container before each test."""
        reset_container()
        pygame.init()
    
    def teardown_method(self):
        """Cleanup after each test."""
        pygame.quit()
    
    def test_container_creates_all_components(self):
        """Verify DI container can create all components."""
        container = get_container()
        
        # Domain
        deck = container.get_deck(DeckType.FRENCH)
        assert deck is not None
        assert len(deck.cards) == 52
        
        table = container.get_table(deck)
        assert table is not None
        
        rules = container.get_rules(deck)
        assert rules is not None
        
        # Application
        controller = container.get_game_controller()
        assert controller is not None
        
        input_handler = container.get_input_handler()
        assert input_handler is not None
        
        # Infrastructure
        screen_reader = container.get_screen_reader()
        assert screen_reader is not None
    
    def test_application_starts_without_errors(self):
        """Verify test.py can initialize."""
        # Import triggers bootstrap
        from test import SolitarioCleanArch
        
        # Should not raise
        app = SolitarioCleanArch()
        assert app.is_running is True
        
        # Cleanup
        app.is_running = False
    
    # ... altri test


# tests/integration/test_feature_parity.py

"""Feature parity tests: scr/ (legacy) vs src/ (new).

Verifies that all features from v1.3.3 work correctly
in the new Clean Architecture.
"""

import pytest
from src.domain.models.deck import FrenchDeck, NeapolitanDeck


class TestFeatureParity:
    """Test that all v1.3.3 features work in src/."""
    
    def test_king_to_empty_pile_french(self):
        """Test Re francese (13) can move to empty pile."""
        # Replicare test da tests/unit/scr/test_king_to_empty_base_pile.py
        # ma usando componenti src/
    
    def test_king_to_empty_pile_neapolitan(self):
        """Test Re napoletano (10) can move to empty pile."""
        # Fix #28, #29
    
    def test_deck_switching_dynamic_distribution(self):
        """Test F1 deck switch with correct reserve cards."""
        # French: 28 + 24 = 52
        # Neapolitan: 28 + 12 = 40
        # Fix #25, #26
    
    def test_double_tap_navigation(self):
        """Test SHIFT+1-4 double-tap selection."""
        # Feature #19, #20 (v1.3.0)
    
    def test_shift_shortcuts(self):
        """Test SHIFT+S (scarti), SHIFT+M (mazzo)."""
        # Feature v1.3.0
    
    def test_f3_timer_decrease(self):
        """Test F3 decreases timer by 5 minutes."""
        # Fix #15
    
    def test_f5_shuffle_toggle(self):
        """Test F5 toggles shuffle/invert mode."""
        # Feature v1.1.0
    
    def test_dynamic_statistics_formatting(self):
        """Test stats show 'X su 13' (French) or 'X su 10' (Neapolitan)."""
        # Feature #24 (v1.3.2)
    
    def test_win_condition_all_four_piles(self):
        """Test victory checks all 4 foundation piles."""
        # Fix v1.3.2
    
    # ... altri test per tutte le feature v1.3.3
```

**Checklist:**
- [ ] Test bootstrap completo applicazione
- [ ] Test ogni feature v1.3.3 con componenti `src/`
- [ ] Test regressione (niente breaking changes)
- [ ] Coverage > 80%

**Commit Message:**
```
test: Add integration tests for Clean Architecture

- Add test_clean_arch_bootstrap.py for DI container
- Add test_feature_parity.py for v1.3.3 features
- Verify all fixes work with src/ components
- Test coverage for critical paths

Validates complete migration from scr/ to src/.
```

***

### **Commit 13: Documentazione completa migrazione**
**Branch:** `feature/add-migration-documentation`

**Obiettivo:** Documentare architettura e processo di migrazione

**File da creare/modificare:**
- `docs/MIGRATION_GUIDE.md` (NUOVO)
- `docs/ARCHITECTURE.md` (AGGIORNARE)
- `README.md` (AGGIORNARE)

**Implementazione:**

```markdown
# docs/MIGRATION_GUIDE.md

# Guida Migrazione scr/ → src/

## Panoramica

Questo documento descrive la migrazione completa del codice da architettura
monolitica (`scr/`) a Clean Architecture (`src/`).

## Motivazioni

1. **Separazione responsabilità**: Logica business ≠ UI ≠ Infrastructure
2. **Testabilità**: Componenti isolati facilmente testabili
3. **Manutenibilità**: Modifiche localizzate senza side effects
4. **Scalabilità**: Aggiungere feature senza toccare core

## Mapping scr/ → src/

### Domain Layer (Business Logic)

| Legacy (scr/)        | New (src/)                        | Commit  |
|---------------------|-----------------------------------|---------|
| `cards.py`          | `domain/models/card.py`           | Preesistente |
| `decks.py`          | `domain/models/deck.py`           | #1      |
| `pile.py`           | `domain/models/pile.py`           | Preesistente |
| `game_table.py`     | `domain/models/table.py`          | #2      |
| `game_engine.py` (validazione) | `domain/rules/solitaire_rules.py` | #3 |
| `game_engine.py` (logica) | `domain/services/game_service.py` | #4 |

### Application Layer (Orchestrazione)

| Legacy (scr/)        | New (src/)                        | Commit  |
|---------------------|-----------------------------------|---------|
| `game_play.py` (input) | `application/input_handler.py` | #7 |
| `game_play.py` (gameplay) | `application/game_controller.py` | #7 |
| `game_engine.py` (settings) | `application/game_settings.py` | #8 |

### Infrastructure Layer (Adattatori)

| Legacy (scr/)        | New (src/)                        | Commit  |
|---------------------|-----------------------------------|---------|
| `screen_reader.py`  | `infrastructure/accessibility/screen_reader.py` | #5 |
| `pygame_menu.py`    | `infrastructure/ui/menu.py`       | #6      |
| N/A                 | `infrastructure/di_container.py`  | #11     |

### Presentation Layer (Formattazione)

| Legacy (scr/)        | New (src/)                        | Commit  |
|---------------------|-----------------------------------|---------|
| `game_engine.py` (stats) | `presentation/game_formatter.py` | #9 |

### Entry Points

| File        | Usa         | Status     | Note                    |
|------------|-------------|------------|-------------------------|
| `acs.py`   | `scr/`      | ✅ Working | Legacy, mantieni intatto |
| `test.py`  | `src/`      | ✅ Working | Nuovo, Clean Arch       |

## Come Testare

### Legacy (scr/)
```bash
python acs.py
```

### Clean Architecture (src/)
```bash
python test.py
```

### Test Suite
```bash
pytest tests/integration/test_feature_parity.py -v
```

## Feature Parity v1.3.3

Tutte le funzionalità legacy sono state migrate:

- [x] Mazzo francese (52 carte) e napoletano (40 carte)
- [x] Fix Re napoletano su pila vuota (is_king)
- [x] Distribuzione dinamica carte riserve (24 vs 12)
- [x] Double-tap navigation (SHIFT+1-4)
- [x] Quick access shortcuts (SHIFT+S/M)
- [x] Timer management (F2/F3/F4)
- [x] Shuffle toggle (F5)
- [x] Statistiche dinamiche per tipo mazzo
- [x] Verifica vittoria 4 pile fondazioni
- [x] Screen reader accessibility
- [x] Tutte le feature v1.3.3

## Prossimi Passi

1. Test estensivi con utenti
2. Eventuali fix su `src/`
3. Quando stabile, deprecare `scr/`
4. Eventuale rimozione `scr/` in v2.0.0
```

```markdown
# docs/ARCHITECTURE.md (AGGIORNARE)

# Architettura Solitario Accessibile

## Clean Architecture (src/)

### Struttura

```
src/
├── domain/              # Business logic (core)
│   ├── models/         # Entità e value objects
│   │   ├── card.py
│   │   ├── deck.py     ← Mazzi (francese/napoletano)
│   │   ├── pile.py
│   │   └── table.py    ← Tavolo con 7+4 pile
│   ├── rules/          # Regole del gioco
│   │   ├── solitaire_rules.py
│   │   └── move_validator.py
│   ├── services/       # Logica orchestrazione
│   │   └── game_service.py
│   └── interfaces/     # Contratti astratti
│
├── application/        # Use cases e orchestrazione
│   ├── commands.py     # Command pattern (undo/redo)
│   ├── game_controller.py  # Orchestratore principale
│   ├── game_settings.py    # Timer, difficoltà, ecc
│   └── input_handler.py    # Keyboard → Commands
│
├── infrastructure/     # Adattatori esterni
│   ├── di_container.py     # Dependency Injection
│   ├── accessibility/
│   │   └── screen_reader.py  ← TTS per accessibilità
│   └── ui/
│       └── menu.py           ← PyGame menu
│
└── presentation/       # Output formatting
    └── game_formatter.py   # Testo per screen reader
```

### Flusso Dati

```
User Input (Keyboard)
    ↓
InputHandler (converte eventi → comandi)
    ↓
GameController (applica comando)
    ↓
GameService (esegue logica business)
    ↓
SolitaireRules (valida mossa)
    ↓
GameTable/Deck (modifica stato)
    ↓
GameFormatter (formatta output)
    ↓
ScreenReader (vocalizza)
    ↓
User (feedback audio)
```

### Principi

1. **Dependency Rule**: Dipendenze puntano verso il centro (Domain)
2. **No side effects in Domain**: Pura logica business
3. **Interfaces over implementations**: Dependency Injection
4. **Single Responsibility**: Ogni classe ha un solo motivo per cambiare

## Legacy Architecture (scr/)

**Status**: Deprecated ma funzionante

Architettura monolitica con file "Dio" (`game_engine.py` 43 KB).
Mantieni per backward compatibility ma non estendere.

Entry point: `acs.py`
```

```markdown
# README.md (AGGIORNARE - solo sezione rilevante)

## 🚀 Come Avviare

### Versione Corrente (Clean Architecture)

```bash
python test.py
```

**Features**:
- Architettura pulita e modulare
- Facile da testare e estendere
- Tutte le funzionalità v1.3.3 incluse

### Versione Legacy (Compatibilità)

```bash
python acs.py
```

**Note**: Usa architettura legacy `scr/`. Funzionale ma deprecata.

## 📁 Struttura Progetto

```
solitario-classico-accessibile/
├── test.py              ← NUOVO entry point (Clean Arch)
├── acs.py               ← Legacy entry point (funzionante)
├── src/                 ← Architettura Clean
│   ├── domain/         ← Business logic puro
│   ├── application/    ← Use cases
│   ├── infrastructure/ ← Adapter esterni
│   └── presentation/   ← Formatting output
├── scr/                 ← Legacy (deprecato)
└── tests/
    ├── unit/
    └── integration/     ← Test migrazione
```

## 🔧 Sviluppo

### Setup

```bash
pip install -r requirements.txt
```

### Test

```bash
# Test suite completo
pytest tests/

# Test solo integrazione
pytest tests/integration/ -v

# Test feature parity
pytest tests/integration/test_feature_parity.py -v
```

### Architettura

Vedi [ARCHITECTURE.md](docs/ARCHITECTURE.md) per dettagli completi.
```

**Checklist:**
- [ ] Documentazione completa migrazione
- [ ] Diagrammi architettura (opzionale)
- [ ] Mapping file legacy → nuovo
- [ ] Istruzioni testing
- [ ] Feature parity checklist

**Commit Message:**
```
docs: Add complete migration documentation

- Add MIGRATION_GUIDE.md with scr/ → src/ mapping
- Update ARCHITECTURE.md with Clean Arch details
- Update README.md with new entry points
- Document all 13 migration commits
- Feature parity checklist for v1.3.3

Completes migration documentation.
```

***

## 📊 **RIEPILOGO PIANO COMPLETO**

### **13 Commit Totali - Organizzati in 7 Fasi**

| Fase | Commit | Branch | Obiettivo | File Coinvolti |
|------|--------|--------|-----------|----------------|
| **1. Domain Models** | #1 | `feature/migrate-decks-to-domain` | Mazzi con is_king() | `deck.py` |
| | #2 | `feature/migrate-game-table-to-domain` | Tavolo + pile | `table.py`, `pile.py` |
| **2. Domain Rules/Services** | #3 | `feature/extract-move-validation-rules` | Regole validazione | `solitaire_rules.py` |
| | #4 | `feature/migrate-gameplay-logic-to-service` | Logica gameplay | `game_service.py` |
| **3. Infrastructure** | #5 | `feature/migrate-screen-reader-to-infrastructure` | Accessibilità TTS | `screen_reader.py` |
| | #6 | `feature/migrate-pygame-ui-to-infrastructure` | Menu PyGame | `menu.py` |
| **4. Application** | #7 | `feature/migrate-game-play-to-application` | Input handling | `input_handler.py`, `game_controller.py` |
| | #8 | `feature/add-timer-and-difficulty-management` | Timer/settings | `game_settings.py` |
| **5. Presentation** | #9 | `feature/extend-formatter-with-stats` | Statistiche | `game_formatter.py` |
| **6. Integration** | #10 | `feature/create-clean-arch-entry-point` | Entry point | `test.py` |
| | #11 | `feature/update-di-container-complete` | DI completo | `di_container.py` |
| **7. Testing/Docs** | #12 | `feature/add-integration-tests` | Test E2E | `tests/integration/` |
| | #13 | `feature/add-migration-documentation` | Documentazione | `docs/` |

***

### **Strategia Implementazione per Copilot Agent**

#### **Formato Issue/PR per ogni commit:**

```markdown
## Issue Template

**Title**: [FASE X - Commit Y] <Descrizione breve>

**Labels**: `migration`, `clean-architecture`, `fase-X`

**Description**:

### Obiettivo
<Copia da sezione "Obiettivo" del commit>

### File da Creare/Modificare
- [ ] `<path/to/file.py>` (NUOVO/AGGIORNARE)
- [ ] ...

### Implementazione
<Copia codice skeleton + checklist>

### Testing
<Copia checklist testing>

### Definition of Done
- [ ] Codice implementato con type hints completi
- [ ] Docstrings aggiunte
- [ ] Test unitari passano
- [ ] Nessun import da `scr/` nel codice `src/`
- [ ] Commit message segue template
- [ ] Feature parity verificata

### Riferimenti
- Migrato da: `scr/<file>` (SHA: <sha>)
- Issue correlate: #<num>
- Documentazione: docs/MIGRATION_GUIDE.md
```

***

## ✅ **COME USARE QUESTO PIANO**

### **Per te (Sviluppatore)**:
1. Crea **13 issue** su GitHub usando il template sopra
2. Assegna ogni issue a **Copilot Agent** (`@copilot`)
3. Segui l'ordine sequenziale (Commit #1 → #13)
4. Verifica ogni PR prima del merge

### **Per Copilot Agent**:
```
@copilot Implementa l'issue #<num> seguendo esattamente le specifiche nella descrizione.

Checklist obbligatoria:
- Copia il codice da scr/<file> come indicato (SHA specificato)
- Mantieni feature parity completa
- Aggiungi type hints e docstrings
- Nessun import scr/ nel nuovo codice src/
- Test unitari per logica critica
- Commit message come da template
```

***

## 🎯 **RISULTATO FINALE**

Al termine dei 13 commit:

✅ **`src/` completo** con Clean Architecture
✅ **`test.py` funzionante** come entry point
✅ **Feature parity 100%** con v1.3.3
✅ **`acs.py` intatto** (legacy ancora funzionante)
✅ **Test suite** per validazione
✅ **Documentazione completa**

***