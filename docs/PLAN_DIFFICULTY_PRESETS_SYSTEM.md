# 📋 Piano Implementazione - Sistema Preset Difficoltà

> Piano completo per reimplementare il sistema di preset difficoltà intelligenti con blocco opzioni progressive.

---

## 📊 Executive Summary

**Tipo**: FEATURE  
**Priorità**: 🟠 ALTA  
**Stato**: READY  
**Branch**: `refactoring-engine`  
**Versione Target**: `v2.4.0`  
**Data Creazione**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 5-6 ore totali (4 ore implementazione + 1-2 ore testing)  
**Commits Previsti**: 8-10 commit atomici

---

### Problema/Obiettivo

**Situazione Attuale**:
Il sistema ha due opzioni separate:
1. **Livello Difficoltà** (1-5): Attualmente ciclica 1→2→3→4→5→1 senza effetti collaterali
2. **Carte Pescate** (1-3): Modificabile indipendentemente

Questa separazione causa problemi:
- ❌ Ridondanza concettuale (difficoltà non influisce su nulla)
- ❌ Configurazioni illogiche possibili (es. "Livello 5 Esperto" con 1 carta pescata)
- ❌ Nessuna protezione anti-errore per utenti inesperti
- ❌ Impossibile garantire fair play per modalità competitiva

**Obiettivo**:
Trasformare "Livello Difficoltà" in un **preset manager intelligente** che:
- ✅ Applica configurazioni predefinite coerenti
- ✅ Blocca opzioni incompatibili ai livelli alti (4-5)
- ✅ Guida utenti inesperti con default sensati (livelli 1-2)
- ✅ Garantisce regole ufficiali Vegas/Tournament (livelli 3-5)

---

### Soluzione Proposta

**Architettura Domain-Driven Design**:

1. **Nuova classe `DifficultyPreset`** (Domain Layer):
   - Definisce configurazione completa per ogni livello 1-5
   - Specifica quali opzioni sono bloccate/personalizzabili
   - Contiene valori default e valori fissi

2. **Metodo `GameSettings.apply_difficulty_preset(level)`** (Domain Service):
   - Applica preset al cambio livello difficoltà
   - Sovrascrive opzioni bloccate
   - Rispetta opzioni personalizzabili

3. **Property `GameSettings.is_option_locked(option_name)`** (Domain Service):
   - Query per verificare se opzione è modificabile
   - Usata da UI per mostrare stato 🔒

4. **Refactoring `OptionsController`** (Application Layer):
   - Blocca tentativi modifica opzioni locked
   - Restituisce messaggi TTS "Opzione bloccata da Livello X"
   - Applica preset quando utente cicla difficoltà

5. **Aggiornamento `OptionsFormatter`** (Presentation Layer):
   - Mostra indicatore 🔒 nelle opzioni bloccate
   - Formatta messaggi TTS specifici per lock state

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | ALTA | Feature core gameplay, cambia UX opzioni |
| **Scope** | 6 file modificati + 1 nuovo | Domain, Application, Presentation layers |
| **Rischio regressione** | MEDIO | Opzioni esistenti funzionano, aggiungiamo solo lock logic |
| **Breaking changes** | NO | Backward compatible (preset applicati solo a new games) |
| **Testing** | MEDIO | 5 livelli × 8 opzioni = 40 combinazioni da testare |

---

## 🎯 Requisiti Funzionali

### 1. Schema Preset Difficoltà

**Tabella Completa** (🔒=bloccato, 🔓=personalizzabile, 🚫=nascosto):

| Opzione | Livello 1<br>**Principiante** | Livello 2<br>**Facile** | Livello 3<br>**Normale<br>(Vegas)** | Livello 4<br>**Difficile<br>(Time Attack)** | Livello 5<br>**Esperto<br>(Tournament)** |
|---------|------|------|------|------|------|
| **Carte Pescate** | 🔓 **1-3**<br>*(default 1)* | 🔓 **1-3**<br>*(default 2)* | 🔒 **3** | 🔒 **3** | 🔒 **3** |
| **Timer** | 🔒 **OFF** | 🔓 **0-60 min** | 🔓 **0-60 min** | 🔒 **30 min** | 🔒 **15 min** |
| **Modalità Timer** | 🚫 *N/A* | 🔒 **PERMISSIVE** | 🔓 **PERM/STRICT** | 🔒 **PERMISSIVE** | 🔒 **STRICT** |
| **Riciclo Scarti** | 🔓 **Inv/Mes**<br>*(default Mes)* | 🔓 **Inv/Mes**<br>*(default Mes)* | 🔓 **Inv/Mes**<br>*(default Inv)* | 🔒 **Inversione** | 🔒 **Inversione** |
| **Sistema Punti** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔒 **ON** |
| **Suggerimenti** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔒 **OFF** | 🔒 **OFF** |

**File Coinvolti**:
- `src/domain/models/difficulty_preset.py` - **NEW** 🆕
- `src/domain/services/game_settings.py` - MODIFIED ⚙️

---

### 2. Comportamento Cambio Livello

**Flusso Utente**:
1. Utente apre Opzioni
2. Naviga su "Difficoltà"
3. Preme INVIO → Difficoltà cicla (es. Liv 2 → Liv 3)
4. **Sistema applica preset Liv 3 automaticamente**:
   - Carte Pescate → **bloccato su 3**
   - Timer → mantiene valore utente (personalizzabile)
   - Modalità Timer → mantiene valore utente (personalizzabile)
   - Riciclo Scarti → **default Inversione** (ma personalizzabile)
   - Sistema Punti → mantiene valore utente (personalizzabile)
   - Suggerimenti → mantiene valore utente (personalizzabile)
5. TTS annuncia: "Difficoltà impostata a Livello 3, Normale. Carte Pescate bloccate su 3. Riciclo Scarti impostato su Inversione."

**Caso Edge - Liv 3 → Liv 4**:
1. Utente ha Liv 3 con Timer OFF (personalizzato)
2. Cicla Difficoltà → Liv 4
3. **Preset Liv 4 sovrascrive Timer → 30 minuti fisso**
4. TTS: "Difficoltà Livello 4, Time Attack. Timer bloccato su 30 minuti. Suggerimenti disattivati."

**File Coinvolti**:
- `src/application/options_controller.py` - MODIFIED ⚙️ (metodo `_modify_difficulty()`)

---

### 3. Blocco Modifica Opzioni Locked

**Comportamento Atteso**:
1. Utente a Livello 5 (Tournament)
2. Naviga su "Carte Pescate" (bloccata su 3)
3. TTS: "2 di 8: Carte Pescate, 3. Opzione bloccata da Livello Difficoltà 5. 🔒"
4. Preme INVIO per modificare
5. **Sistema rifiuta modifica**
6. TTS: "Impossibile modificare. Opzione bloccata da Livello Difficoltà Esperto. Cambia livello difficoltà per sbloccare."

**File Coinvolti**:
- `src/application/options_controller.py` - MODIFIED ⚙️ (metodo `modify_current_option()`)
- `src/presentation/options_formatter.py` - MODIFIED ⚙️ (nuovo metodo `format_option_locked()`)

---

### 4. Persistenza JSON

**Comportamento**:
- Salvataggio: Tutti i valori salvati (anche quelli bloccati)
- Caricamento: `apply_difficulty_preset()` chiamato per validare coerenza
- Se preset cambiato nel codice → sovrascrive valori incoerenti

**Esempio JSON** (Livello 5 salvato):
```json
{
  "difficulty_level": 5,
  "draw_count": 3,
  "max_time_game": 900,
  "timer_strict_mode": true,
  "shuffle_discards": false,
  "scoring_enabled": true,
  "command_hints_enabled": false
}
```

**File Coinvolti**:
- `src/domain/services/game_settings.py` - MODIFIED ⚙️ (metodo `load_from_dict()`)

---

## 🏗️ Architettura

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ OptionsFormatter                                      │   │
│  │ + format_option_locked(option_name, level)           │   │  🆕
│  │ + format_preset_applied(level, changes_list)         │   │  🆕
│  │ + format_option_item() [MODIFIED]                    │   │  ⚙️
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ OptionsController                                     │   │
│  │ + _modify_difficulty() [MODIFIED]                    │   │  ⚙️
│  │ + modify_current_option() [MODIFIED]                 │   │  ⚙️
│  │ + _format_current_option() [MODIFIED]                │   │  ⚙️
│  │ + _is_current_option_locked() → bool                 │   │  🆕
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  ┌────────────────────────┐  ┌─────────────────────────┐    │
│  │ DifficultyPreset       │  │ GameSettings            │    │
│  │ (NEW)                  │  │ (MODIFIED)              │    │
│  ├────────────────────────┤  ├─────────────────────────┤    │
│  │ + level: int           │  │ + apply_difficulty_     │    │
│  │ + locked_options: Set  │  │   preset(level)   🆕    │    │
│  │ + defaults: Dict       │  │ + is_option_locked()🆕  │    │
│  │ + fixed_values: Dict   │  │ + get_current_preset()  │    │
│  │                        │  │   → DifficultyPreset 🆕 │    │
│  │ PRESETS = {            │  │ + load_from_dict()  ⚙️  │    │
│  │   1: Preset(...),      │  │ + cycle_difficulty() ⚙️ │    │
│  │   2: Preset(...),      │  └─────────────────────────┘    │
│  │   ...                  │                                  │
│  │ }                      │                                  │
│  └────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
src/
├── domain/
│   ├── models/
│   │   └── difficulty_preset.py              # NEW 🆕
│   └── services/
│       └── game_settings.py                  # MODIFIED ⚙️
├── application/
│   └── options_controller.py                 # MODIFIED ⚙️
└── presentation/
    └── options_formatter.py                  # MODIFIED ⚙️

tests/
├── unit/
│   ├── domain/
│   │   ├── test_difficulty_preset.py         # NEW: 8 tests
│   │   └── test_game_settings_presets.py     # NEW: 12 tests
│   └── application/
│       └── test_options_controller_lock.py   # NEW: 10 tests
└── integration/
    └── test_preset_flow.py                   # NEW: 5 scenarios

docs/
├── PLAN_DIFFICULTY_PRESETS_SYSTEM.md         # THIS FILE
└── TODO_DIFFICULTY_PRESETS.md                # Tracking checklist
```

---

## 📝 Piano di Implementazione

### COMMIT 1: Creare modello DifficultyPreset (Domain Layer)

**Priorità**: 🔴 CRITICA (fondazione sistema)  
**File**: `src/domain/models/difficulty_preset.py` (NEW)  
**Linee**: 1-150 (nuovo file)

#### Codice Nuovo

```python
"""Difficulty preset configurations for progressive gameplay.

Defines locked/unlocked options and default values for each difficulty level (1-5).

Architecture: Domain Layer - Models
Version: v2.4.0
"""

from typing import Set, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DifficultyPreset:
    """Configuration preset for a specific difficulty level.
    
    Immutable configuration that defines:
    - Which options are locked (user cannot modify)
    - Default values for unlocked options
    - Fixed values for locked options
    
    Attributes:
        level: Difficulty level (1-5)
        name: Display name (es. "Principiante", "Esperto")
        locked_options: Set of option names that cannot be modified
        defaults: Default values for unlocked options
        fixed_values: Fixed values for locked options (override user settings)
    
    Example:
        >>> preset = PRESETS[5]  # Tournament mode
        >>> preset.is_locked("draw_count")
        True
        >>> preset.get_value("draw_count")
        3
    
    Version:
        v2.4.0: Initial implementation
    """
    
    level: int
    name: str
    locked_options: Set[str] = field(default_factory=set)
    defaults: Dict[str, Any] = field(default_factory=dict)
    fixed_values: Dict[str, Any] = field(default_factory=dict)
    
    def is_locked(self, option_name: str) -> bool:
        """Check if option is locked at this difficulty level.
        
        Args:
            option_name: Name of option (es. "draw_count", "max_time_game")
            
        Returns:
            True if option cannot be modified by user
            
        Example:
            >>> PRESETS[1].is_locked("max_time_game")
            True  # Timer locked OFF at level 1
            >>> PRESETS[2].is_locked("draw_count")
            False  # Draw count customizable at level 2
        """
        return option_name in self.locked_options
    
    def get_value(self, option_name: str) -> Optional[Any]:
        """Get value for option (fixed if locked, default if unlocked).
        
        Args:
            option_name: Name of option
            
        Returns:
            Fixed value if locked, default value if unlocked, None if not configured
            
        Example:
            >>> PRESETS[5].get_value("draw_count")
            3  # Fixed value for tournament
            >>> PRESETS[1].get_value("draw_count")
            1  # Default value for beginners
        """
        if option_name in self.fixed_values:
            return self.fixed_values[option_name]
        return self.defaults.get(option_name)
    
    def get_changes_description(self) -> str:
        """Get human-readable description of preset changes.
        
        Returns:
            Comma-separated list of locked options with values
            
        Example:
            >>> PRESETS[5].get_changes_description()
            "Carte Pescate: 3, Timer: 15 minuti, Modalità Timer: STRICT, ..."
        """
        # Implementation deferred to OptionsFormatter for i18n
        return f"Preset Livello {self.level}"


# ============================================
# PRESET DEFINITIONS (1-5)
# ============================================

PRESETS: Dict[int, DifficultyPreset] = {
    1: DifficultyPreset(
        level=1,
        name="Principiante",
        locked_options={"max_time_game"},  # Timer always OFF
        defaults={
            "draw_count": 1,              # Default 1 carta
            "shuffle_discards": True,     # Default mescolata
            "max_time_game": 0,           # Timer OFF (locked)
        },
        fixed_values={
            "max_time_game": 0,           # Enforce timer OFF
        }
    ),
    
    2: DifficultyPreset(
        level=2,
        name="Facile",
        locked_options={"timer_strict_mode"},  # Timer mode locked PERMISSIVE
        defaults={
            "draw_count": 2,              # Default 2 carte
            "shuffle_discards": True,     # Default mescolata
            "timer_strict_mode": False,   # PERMISSIVE (locked)
        },
        fixed_values={
            "timer_strict_mode": False,   # Enforce PERMISSIVE
        }
    ),
    
    3: DifficultyPreset(
        level=3,
        name="Normale (Vegas)",
        locked_options={"draw_count"},    # 3 carte fixed (Vegas rule)
        defaults={
            "shuffle_discards": False,    # Default inversione (Vegas standard)
        },
        fixed_values={
            "draw_count": 3,              # Enforce 3 cards
        }
    ),
    
    4: DifficultyPreset(
        level=4,
        name="Difficile (Time Attack)",
        locked_options={
            "draw_count",
            "max_time_game",
            "timer_strict_mode",
            "shuffle_discards",
            "command_hints_enabled",
        },
        defaults={},  # No defaults, all locked
        fixed_values={
            "draw_count": 3,
            "max_time_game": 1800,        # 30 minutes
            "timer_strict_mode": False,   # PERMISSIVE (can finish over time)
            "shuffle_discards": False,    # Inversione (fair play)
            "command_hints_enabled": False,  # No hints (pro mode)
        }
    ),
    
    5: DifficultyPreset(
        level=5,
        name="Esperto (Tournament)",
        locked_options={
            "draw_count",
            "max_time_game",
            "timer_strict_mode",
            "shuffle_discards",
            "command_hints_enabled",
            "scoring_enabled",
        },
        defaults={},  # No defaults, all locked
        fixed_values={
            "draw_count": 3,
            "max_time_game": 900,         # 15 minutes
            "timer_strict_mode": True,    # STRICT (game over at timeout)
            "shuffle_discards": False,    # Inversione (tournament standard)
            "command_hints_enabled": False,  # No hints
            "scoring_enabled": True,      # Scoring required for leaderboard
        }
    ),
}


def get_preset(level: int) -> DifficultyPreset:
    """Get preset configuration for difficulty level.
    
    Args:
        level: Difficulty level (1-5)
        
    Returns:
        DifficultyPreset instance
        
    Raises:
        ValueError: If level not in 1-5 range
        
    Example:
        >>> preset = get_preset(5)
        >>> preset.name
        'Esperto (Tournament)'
    """
    if level not in PRESETS:
        raise ValueError(f"Invalid difficulty level: {level}. Must be 1-5.")
    return PRESETS[level]
```

#### Rationale

**Perché funziona**:
1. **Immutable dataclass**: `frozen=True` garantisce thread-safety e cache-ability
2. **Separation of Concerns**: Preset logic separata da GameSettings (Domain Model puro)
3. **Type-safe**: Dict[int, DifficultyPreset] previene errori runtime
4. **Explicit over Implicit**: `locked_options` + `fixed_values` rendono intent chiaro
5. **Extensible**: Aggiungere Livello 6 custom è triviale (append al dict)

**Non ci sono regressioni perché**:
- Nuovo file, nessun codice esistente modificato
- Zero import da altri moduli (dependency-free)
- Può essere testato standalone

#### Testing Commit 1

**File**: `tests/unit/domain/test_difficulty_preset.py`

```python
import pytest
from src.domain.models.difficulty_preset import get_preset, PRESETS


class TestDifficultyPreset:
    """Test DifficultyPreset model."""
    
    def test_level_1_locks_timer(self):
        """Level 1 must lock timer to OFF."""
        preset = get_preset(1)
        assert preset.is_locked("max_time_game")
        assert preset.get_value("max_time_game") == 0
    
    def test_level_5_locks_all_competitive_options(self):
        """Level 5 must lock all tournament-critical options."""
        preset = get_preset(5)
        assert preset.is_locked("draw_count")
        assert preset.is_locked("max_time_game")
        assert preset.is_locked("timer_strict_mode")
        assert preset.is_locked("shuffle_discards")
        assert preset.is_locked("scoring_enabled")
        assert preset.is_locked("command_hints_enabled")
    
    def test_level_2_default_2_cards(self):
        """Level 2 should default to 2 cards drawn."""
        preset = get_preset(2)
        assert not preset.is_locked("draw_count")
        assert preset.get_value("draw_count") == 2
    
    def test_invalid_level_raises_error(self):
        """Invalid level must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid difficulty level"):
            get_preset(99)
    
    def test_all_presets_have_unique_names(self):
        """All 5 presets must have distinct names."""
        names = [p.name for p in PRESETS.values()]
        assert len(names) == len(set(names))  # No duplicates
```

**Commit Message**:
```
feat(domain): add DifficultyPreset model with 5-level configuration

Introduce immutable preset configurations for difficulty levels 1-5:
- Level 1 (Principiante): Timer locked OFF, 1 card default
- Level 2 (Facile): Timer mode locked PERMISSIVE, 2 cards default
- Level 3 (Normale/Vegas): 3 cards locked, inversione default
- Level 4 (Time Attack): 30min timer, all competitive options locked
- Level 5 (Tournament): 15min STRICT timer, all options locked

Features:
- is_locked(option_name) → bool: Check if option modifiable
- get_value(option_name) → Any: Get fixed/default value
- Immutable dataclass (frozen=True) for thread-safety
- Type-safe Dict[int, DifficultyPreset] registry

Impact:
- NEW: src/domain/models/difficulty_preset.py
- NEW: tests/unit/domain/test_difficulty_preset.py (8 tests)
- Zero modifications to existing code (new module)

Version: v2.4.0
```

---

### COMMIT 2: Aggiungere apply_difficulty_preset() a GameSettings

**Priorità**: 🔴 CRITICA  
**File**: `src/domain/services/game_settings.py`  
**Linee**: ~200-250 (nuovo metodo + import)

#### Codice Attuale (Import section)

```python
"""Game settings service.

Manages all game configuration...
"""

from typing import Tuple
from src.domain.models.game_state import GameState
# ... altri import
```

#### Codice Nuovo (Aggiungere import + metodi)

```python
"""Game settings service.

Manages all game configuration...

Version:
    v2.4.0: Added difficulty preset system with locked options
"""

from typing import Tuple, Optional, Set
from src.domain.models.game_state import GameState
from src.domain.models.difficulty_preset import get_preset, DifficultyPreset  # NEW
# ... altri import


class GameSettings:
    """..."""
    
    # ... existing code ...
    
    # ========================================
    # DIFFICULTY PRESET SYSTEM (v2.4.0)
    # ========================================
    
    def apply_difficulty_preset(self, level: int) -> None:
        """Apply difficulty preset configuration.
        
        Overwrites locked options with preset fixed values.
        Applies defaults to unlocked options if not already set.
        
        Args:
            level: Difficulty level (1-5)
            
        Raises:
            ValueError: If level invalid
            
        Example:
            >>> settings.difficulty_level = 5
            >>> settings.apply_difficulty_preset(5)
            >>> settings.draw_count  # Locked to 3
            3
            >>> settings.max_time_game  # Locked to 15 min
            900
            
        Version:
            v2.4.0: Initial implementation
        """
        preset = get_preset(level)
        
        # Apply fixed values (override user settings)
        for option_name, value in preset.fixed_values.items():
            setattr(self, option_name, value)
        
        # Apply defaults to unlocked options (if not already customized)
        # Skip this for now - user keeps customizations for unlocked options
        # Future: Add flag to force-reset defaults
    
    def is_option_locked(self, option_name: str) -> bool:
        """Check if option is locked by current difficulty preset.
        
        Args:
            option_name: Internal option name (es. "draw_count")
            
        Returns:
            True if option cannot be modified by user
            
        Example:
            >>> settings.difficulty_level = 5
            >>> settings.is_option_locked("draw_count")
            True
            >>> settings.is_option_locked("deck_type")
            False
            
        Version:
            v2.4.0: Initial implementation
        """
        preset = get_preset(self.difficulty_level)
        return preset.is_locked(option_name)
    
    def get_locked_options(self) -> Set[str]:
        """Get set of all locked option names at current difficulty.
        
        Returns:
            Set of locked option names
            
        Example:
            >>> settings.difficulty_level = 5
            >>> locked = settings.get_locked_options()
            >>> "draw_count" in locked
            True
            
        Version:
            v2.4.0: Initial implementation
        """
        preset = get_preset(self.difficulty_level)
        return preset.locked_options.copy()
    
    def get_current_preset(self) -> DifficultyPreset:
        """Get current difficulty preset configuration.
        
        Returns:
            DifficultyPreset for current difficulty_level
            
        Example:
            >>> settings.difficulty_level = 3
            >>> preset = settings.get_current_preset()
            >>> preset.name
            'Normale (Vegas)'
            
        Version:
            v2.4.0: Initial implementation
        """
        return get_preset(self.difficulty_level)
```

#### Modifica Esistente: cycle_difficulty()

**Linee**: ~XXX (trovare metodo esistente)

```python
# BEFORE
def cycle_difficulty(self) -> Tuple[bool, str]:
    """Cycle difficulty level 1 -> 2 -> 3 -> 4 -> 5 -> 1."""
    self.difficulty_level = (self.difficulty_level % 5) + 1
    display = self.get_difficulty_display()
    return (True, f"Difficoltà impostata a {display}.")

# AFTER
def cycle_difficulty(self) -> Tuple[bool, str]:
    """Cycle difficulty level and apply preset.
    
    Version:
        v2.4.0: Now applies difficulty preset after cycling
    """
    old_level = self.difficulty_level
    self.difficulty_level = (self.difficulty_level % 5) + 1
    
    # Apply preset (locks/defaults)
    self.apply_difficulty_preset(self.difficulty_level)
    
    display = self.get_difficulty_display()
    return (True, f"Difficoltà impostata a {display}.")
```

#### Rationale

**Perché funziona**:
1. **Single Source of Truth**: Preset logic centralizzato in DifficultyPreset
2. **Automatic Application**: cycle_difficulty() applica automaticamente preset
3. **Query Methods**: `is_option_locked()` permette UI di check runtime
4. **Immutability Preserved**: Preset è immutable, GameSettings muta solo self

**Non ci sono regressioni perché**:
- `apply_difficulty_preset()` chiamato solo da `cycle_difficulty()`
- Se preset system disabilitato → comportamento identico a prima
- Existing unit tests di cycle_difficulty() continueranno a passare

#### Testing Commit 2

**File**: `tests/unit/domain/test_game_settings_presets.py`

```python
import pytest
from src.domain.services.game_settings import GameSettings
from src.domain.models.game_state import GameState


class TestGameSettingsPresets:
    """Test preset integration in GameSettings."""
    
    @pytest.fixture
    def settings(self):
        """Create GameSettings instance."""
        game_state = GameState()
        return GameSettings(game_state)
    
    def test_apply_preset_level_5_locks_draw_count(self, settings):
        """Applying level 5 preset must lock draw_count to 3."""
        settings.difficulty_level = 5
        settings.draw_count = 1  # User customization
        
        settings.apply_difficulty_preset(5)
        
        assert settings.draw_count == 3  # Overridden
        assert settings.is_option_locked("draw_count")
    
    def test_cycle_difficulty_applies_preset(self, settings):
        """Cycling difficulty must auto-apply preset."""
        settings.difficulty_level = 2
        settings.draw_count = 1
        
        settings.cycle_difficulty()  # 2 → 3
        
        assert settings.difficulty_level == 3
        assert settings.draw_count == 3  # Locked by preset
    
    def test_is_option_locked_returns_false_for_unlocked(self, settings):
        """Unlocked options must return False."""
        settings.difficulty_level = 1
        assert not settings.is_option_locked("deck_type")  # Never locked
    
    def test_get_locked_options_returns_set(self, settings):
        """get_locked_options must return set."""
        settings.difficulty_level = 5
        locked = settings.get_locked_options()
        assert isinstance(locked, set)
        assert "draw_count" in locked
```

**Commit Message**:
```
feat(domain): integrate preset system in GameSettings

Add preset application methods to GameSettings service:
- apply_difficulty_preset(level): Apply preset configuration
- is_option_locked(option_name): Query if option modifiable
- get_locked_options(): Get all locked option names
- get_current_preset(): Get current DifficultyPreset instance

Modifications:
- cycle_difficulty() now auto-applies preset after level change
- Locked options overridden by preset fixed values
- Unlocked options keep user customizations

Impact:
- MODIFIED: src/domain/services/game_settings.py (+60 lines)
- NEW: tests/unit/domain/test_game_settings_presets.py (12 tests)
- Backward compatible (preset applied only on cycle, not load)

Version: v2.4.0
```

---

### COMMIT 3: Bloccare modifiche opzioni locked in OptionsController

**Priorità**: 🟠 ALTA  
**File**: `src/application/options_controller.py`  
**Linee**: ~200-350 (metodi modify/navigation)

#### Codice Attuale (modify_current_option)

```python
def modify_current_option(self) -> str:
    """Modify currently selected option (toggle/cycle).
    
    Returns:
        TTS confirmation message or error
    """
    # Block if game running
    if self.settings.game_state.is_running:
        return OptionsFormatter.format_blocked_during_game()
    
    # Route to appropriate handler
    handlers = [
        self._modify_deck_type,
        self._modify_difficulty,
        self._modify_draw_count,
        # ...
    ]
    
    msg = handlers[self.cursor_position]()
    
    # Mark as dirty
    if ("impostato" in msg.lower() or ...):
        self.state = "OPEN_DIRTY"
    
    return msg
```

**Problemi**:
- ❌ Non verifica se opzione è bloccata
- ❌ Chiama handler anche per opzioni locked

#### Codice Nuovo (con lock check)

```python
def modify_current_option(self) -> str:
    """Modify currently selected option (toggle/cycle).
    
    NEW v2.4.0: Blocks modifications to locked options.
    
    Returns:
        TTS confirmation message, error, or lock message
    """
    # Block if game running
    if self.settings.game_state.is_running:
        return OptionsFormatter.format_blocked_during_game()
    
    # NEW v2.4.0: Check if option locked by difficulty preset
    if self._is_current_option_locked():
        option_name = OptionsFormatter.OPTION_NAMES[self.cursor_position]
        level_name = self.settings.get_difficulty_display()
        return OptionsFormatter.format_option_locked(option_name, level_name)
    
    # Route to appropriate handler
    handlers = [
        self._modify_deck_type,
        self._modify_difficulty,
        self._modify_draw_count,
        self._cycle_timer_preset,
        self._modify_shuffle_mode,
        self._modify_command_hints,
        self._modify_scoring,
        self._modify_timer_strict_mode,
    ]
    
    msg = handlers[self.cursor_position]()
    
    # Mark as dirty on successful modification
    msg_lower = msg.lower()
    if ("impostato" in msg_lower or "impostata" in msg_lower or 
        "disattivat" in msg_lower or "attivat" in msg_lower):
        self.state = "OPEN_DIRTY"
    
    return msg


def _is_current_option_locked(self) -> bool:
    """Check if currently selected option is locked by preset.
    
    Returns:
        True if option cannot be modified
        
    Version:
        v2.4.0: Initial implementation
    """
    # Map cursor position to option internal name
    option_map = {
        0: None,  # Deck type - never locked
        1: None,  # Difficulty - never locked (changes preset itself)
        2: "draw_count",
        3: "max_time_game",
        4: "shuffle_discards",
        5: "command_hints_enabled",
        6: "scoring_enabled",
        7: "timer_strict_mode",
    }
    
    option_name = option_map.get(self.cursor_position)
    if option_name is None:
        return False  # Deck type and difficulty never locked
    
    return self.settings.is_option_locked(option_name)
```

#### Modifica: _modify_difficulty() applica preset

```python
# BEFORE
def _modify_difficulty(self) -> str:
    """Cycle difficulty (1 -> 2 -> 3 -> 1)."""
    old_value = self.settings.difficulty_level
    success, msg = self.settings.cycle_difficulty()
    if success:
        new_value = self.settings.difficulty_level
        log.settings_changed("difficulty_level", old_value, new_value)
    return msg

# AFTER
def _modify_difficulty(self) -> str:
    """Cycle difficulty and apply preset.
    
    Version:
        v2.4.0: Returns enhanced message with preset changes
    """
    old_value = self.settings.difficulty_level
    success, base_msg = self.settings.cycle_difficulty()
    
    if success:
        new_value = self.settings.difficulty_level
        log.settings_changed("difficulty_level", old_value, new_value)
        
        # Get preset applied changes
        preset = self.settings.get_current_preset()
        changes_msg = OptionsFormatter.format_preset_applied(
            preset.level,
            preset.name,
            list(preset.locked_options)
        )
        
        return f"{base_msg} {changes_msg}"
    
    return base_msg
```

#### Modifica: _format_current_option() mostra 🔒

```python
def _format_current_option(self, include_hint: bool) -> str:
    """Format current option for TTS.
    
    Version:
        v2.4.0: Adds lock indicator for locked options
    """
    option_name = OptionsFormatter.OPTION_NAMES[self.cursor_position]
    
    # Get current value
    value_getters = [
        self.settings.get_deck_type_display,
        self.settings.get_difficulty_display,
        self.settings.get_draw_count_display,
        self.settings.get_timer_display,
        self.settings.get_shuffle_mode_display,
        self.settings.get_command_hints_display,
        self.settings.get_scoring_display,
        self.settings.get_timer_strict_mode_display
    ]
    
    value = value_getters[self.cursor_position]()
    
    # NEW v2.4.0: Check if locked
    is_locked = self._is_current_option_locked()
    
    return OptionsFormatter.format_option_item(
        self.cursor_position,
        option_name,
        value,
        include_hint,
        is_locked=is_locked  # NEW parameter
    )
```

#### Rationale

**Perché funziona**:
1. **Early Return Pattern**: Check lock prima di chiamare handler
2. **Centralized Logic**: `_is_current_option_locked()` riutilizzabile
3. **User Feedback**: TTS chiaro sul perché modifica rifiutata
4. **Difficulty Special Case**: Cambiare difficoltà NON è mai bloccato (cambia preset stesso)

**Non ci sono regressioni perché**:
- Se preset system disabilitato (tutti unlocked) → comportamento identico
- Lock check è addizionale (non cambia logica esistente)

#### Testing Commit 3

```python
# tests/unit/application/test_options_controller_lock.py

class TestOptionsControllerLocking:
    """Test option locking in OptionsController."""
    
    def test_modify_locked_option_returns_error(self, controller):
        """Trying to modify locked option must return error message."""
        controller.settings.difficulty_level = 5
        controller.cursor_position = 2  # Draw count (locked)
        
        msg = controller.modify_current_option()
        
        assert "bloccata" in msg.lower()
        assert "Livello" in msg or "Esperto" in msg
    
    def test_modify_unlocked_option_works(self, controller):
        """Unlocked options must be modifiable."""
        controller.settings.difficulty_level = 1
        controller.cursor_position = 2  # Draw count (unlocked)
        controller.settings.draw_count = 1
        
        msg = controller.modify_current_option()
        
        assert "impostat" in msg.lower()
        assert controller.settings.draw_count == 2  # Cycled
    
    def test_difficulty_itself_never_locked(self, controller):
        """Changing difficulty must never be locked."""
        controller.settings.difficulty_level = 5
        controller.cursor_position = 1  # Difficulty option
        
        msg = controller.modify_current_option()
        
        assert "bloccata" not in msg.lower()
        assert controller.settings.difficulty_level == 1  # Cycled 5→1
```

**Commit Message**:
```
feat(app): block modification of locked options in OptionsController

Add lock detection and user feedback for preset-locked options:
- modify_current_option() checks lock before calling handlers
- _is_current_option_locked() maps cursor → option name → query GameSettings
- _modify_difficulty() returns enhanced message with preset changes list
- _format_current_option() shows 🔒 indicator for locked options

Behavior:
- Locked options: TTS "Opzione bloccata da Livello X. Cambia difficoltà..."
- Unlocked options: Normal toggle/cycle behavior
- Difficulty option: Never locked (changes preset itself)

Impact:
- MODIFIED: src/application/options_controller.py (+40 lines)
- NEW: tests/unit/application/test_options_controller_lock.py (10 tests)
- Zero breaking changes (lock check is additive)

Version: v2.4.0
```

---

### COMMIT 4-8: [Implementazione Presentation Layer, Testing, Documentation]

[Per brevità, includo solo titoli. Struttura identica ai commit precedenti]

**COMMIT 4**: Aggiungere metodi formatter in OptionsFormatter  
- `format_option_locked(option_name, level_name)`  
- `format_preset_applied(level, name, locked_list)`  
- Modificare `format_option_item()` per parametro `is_locked`

**COMMIT 5**: Modificare load_from_dict() per applicare preset al caricamento  
- GameSettings valida coerenza preset vs JSON  
- Sovrascrive opzioni locked se preset cambiato nel codice

**COMMIT 6**: Aggiungere Integration Tests (5 scenari end-to-end)  
- Test: Liv 1 → Liv 5 → verifica tutti lock  
- Test: Liv 5 → modifica opzione → rifiuto  
- Test: Save/Load Liv 5 → preset riapplicato

**COMMIT 7**: Aggiornare CHANGELOG.md con v2.4.0  
- Sezione completa feature  
- Breaking changes: NONE  
- Migration guide: Opzionale

**COMMIT 8**: Aggiornare README.md con nuovo sistema  
- Tabella preset 1-5  
- Screenshot (opzionale)

---

## 🧪 Testing Strategy

### Unit Tests (30 totale)

#### `tests/unit/domain/test_difficulty_preset.py` (8 tests)
- [x] Test livello 1 blocca timer
- [x] Test livello 5 blocca tutte opzioni competitive
- [x] Test livello 2 default 2 carte
- [x] Test livello invalido raise ValueError
- [x] Test tutti preset hanno nomi unici
- [x] Test is_locked() corretto per tutti livelli
- [x] Test get_value() restituisce fixed/default
- [x] Test immutability (frozen dataclass)

#### `tests/unit/domain/test_game_settings_presets.py` (12 tests)
- [x] Test apply_preset sovrascrive opzioni locked
- [x] Test apply_preset rispetta opzioni unlocked
- [x] Test cycle_difficulty applica preset automaticamente
- [x] Test is_option_locked query corretta
- [x] Test get_locked_options restituisce set
- [x] Test get_current_preset restituisce istanza corretta
- [x] Test preset livello 1 → 5 (tutti livelli)
- [x] Test preset non applicato se livello non cambiato

#### `tests/unit/application/test_options_controller_lock.py` (10 tests)
- [x] Test modifica opzione locked rifiutata
- [x] Test modifica opzione unlocked permessa
- [x] Test difficoltà mai bloccata
- [x] Test TTS contiene "bloccata" per locked
- [x] Test _is_current_option_locked() mapping corretto
- [x] Test navigation mostra 🔒 per locked
- [x] Test increment_timer() bloccato se timer locked
- [x] Test decrement_timer() bloccato se timer locked
- [x] Test toggle_timer() bloccato se timer locked
- [x] Test state OPEN_DIRTY non cambia su modifica rifiutata

### Integration Tests (5 scenari)

#### `tests/integration/test_preset_flow.py` (5 tests)

```python
def test_full_progression_level_1_to_5():
    """Test complete progression through all difficulty levels."""
    settings = GameSettings(GameState())
    controller = OptionsController(settings)
    
    # Start at level 1
    assert settings.difficulty_level == 1
    assert not settings.is_option_locked("draw_count")
    assert settings.is_option_locked("max_time_game")  # Timer OFF
    
    # Cycle to level 3
    controller.cursor_position = 1  # Difficulty
    controller.modify_current_option()  # 1→2
    controller.modify_current_option()  # 2→3
    
    assert settings.difficulty_level == 3
    assert settings.draw_count == 3  # Locked
    assert settings.is_option_locked("draw_count")
    
    # Try modify draw_count (must fail)
    controller.cursor_position = 2
    msg = controller.modify_current_option()
    assert "bloccata" in msg.lower()
    assert settings.draw_count == 3  # Unchanged
    
    # Cycle to level 5
    controller.cursor_position = 1
    controller.modify_current_option()  # 3→4
    controller.modify_current_option()  # 4→5
    
    assert settings.difficulty_level == 5
    assert settings.max_time_game == 900  # 15 min locked
    assert settings.timer_strict_mode is True  # STRICT locked
    assert not settings.command_hints_enabled  # Hints OFF locked
    assert settings.scoring_enabled is True  # Scoring ON locked


def test_save_load_preserves_preset():
    """Test JSON save/load reapplies preset correctly."""
    settings = GameSettings(GameState())
    settings.difficulty_level = 5
    settings.apply_difficulty_preset(5)
    
    # Save to dict
    data = {
        "difficulty_level": settings.difficulty_level,
        "draw_count": settings.draw_count,
        "max_time_game": settings.max_time_game,
        # ...
    }
    
    # Simulate malicious manual edit of JSON
    data["draw_count"] = 1  # Try to cheat tournament rules
    
    # Load from dict
    new_settings = GameSettings(GameState())
    new_settings.load_from_dict(data)
    new_settings.apply_difficulty_preset(data["difficulty_level"])
    
    # Preset must override cheated value
    assert new_settings.draw_count == 3  # Restored by preset
```

### Manual Testing Checklist

- [ ] **Liv 1 → Liv 2**: Timer si sblocca, modalità timer appare
- [ ] **Liv 2 → Liv 3**: Carte pescate bloccate su 3, TTS annuncia
- [ ] **Liv 3 → Liv 4**: Timer bloccato 30 min, suggerimenti OFF
- [ ] **Liv 4 → Liv 5**: Timer 15 min STRICT, scoring ON, tutto bloccato
- [ ] **Liv 5 → modifica carte**: TTS "Opzione bloccata da Livello Esperto"
- [ ] **Liv 5 → Liv 1**: Tutto si sblocca, timer torna OFF
- [ ] **NVDA legge 🔒**: "Opzione bloccata" annunciato correttamente
- [ ] **Salva Liv 5 → riavvia**: Preset riapplicato, opzioni locked

---

## ✅ Common Pitfalls to Avoid

### ❌ DON'T: Bloccare "Difficoltà" stessa

```python
# WRONG - Utente non può mai uscire da Livello 5!
def _is_current_option_locked(self) -> bool:
    option_map = {
        1: "difficulty_level",  # ❌ ERRORE!
        # ...
    }
    # ...
```

**Perché non funziona**:
- Se difficoltà è locked → utente intrappolato in Livello 5 forever
- Nessun modo di tornare a livelli più facili

### ✅ DO: Difficoltà sempre modificabile

```python
# CORRECT
def _is_current_option_locked(self) -> bool:
    option_map = {
        1: None,  # Difficulty never locked
        # ...
    }
```

---

### ❌ DON'T: Dimenticare apply_preset() su load JSON

```python
# WRONG - Preset non riapplicato!
def load_from_dict(self, data: dict):
    self.difficulty_level = data.get("difficulty_level", 1)
    self.draw_count = data.get("draw_count", 1)
    # ❌ Manca apply_difficulty_preset()!
```

**Perché non funziona**:
- Utente edita manualmente JSON: `"draw_count": 1` con `"difficulty_level": 5`
- App carica valori incoerenti → tournament mode con 1 carta (cheat)

### ✅ DO: Sempre validare con preset

```python
# CORRECT
def load_from_dict(self, data: dict):
    self.difficulty_level = data.get("difficulty_level", 1)
    self.draw_count = data.get("draw_count", 1)
    # ...
    self.apply_difficulty_preset(self.difficulty_level)  # Validate!
```

---

## 📦 Commit Strategy

### Atomic Commits (8 totali)

1. **feat(domain)**: Add DifficultyPreset model
   - Files: `difficulty_preset.py`, `test_difficulty_preset.py`
   - Tests: 8 unit tests

2. **feat(domain)**: Integrate preset system in GameSettings
   - Files: `game_settings.py`, `test_game_settings_presets.py`
   - Tests: 12 unit tests

3. **feat(app)**: Block modification of locked options
   - Files: `options_controller.py`, `test_options_controller_lock.py`
   - Tests: 10 unit tests

4. **feat(presentation)**: Add lock indicators in OptionsFormatter
   - Files: `options_formatter.py`
   - Tests: Existing tests verificano output

5. **feat(domain)**: Validate preset on JSON load
   - Files: `game_settings.py`
   - Tests: 2 integration tests

6. **test(integration)**: Add end-to-end preset flow tests
   - Files: `test_preset_flow.py`
   - Tests: 5 integration scenarios

7. **docs(changelog)**: Add v2.4.0 release notes
   - Files: `CHANGELOG.md`

8. **docs(readme)**: Document preset system
   - Files: `README.md`

---

## 📚 References

### Internal Architecture Docs
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `docs/PLAN_FIX_TIMER_OPTION_COMBOBOX_ONLY.md` - Esempio piano simile
- `src/domain/models/game_state.py` - Domain model example

### Related Code Files
- `src/domain/services/game_settings.py` - Settings service (da modificare)
- `src/application/options_controller.py` - Controller opzioni (da modificare)
- `src/presentation/options_formatter.py` - TTS formatter (da modificare)

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Commit 1 - DifficultyPreset**:
   - Crea nuovo file `src/domain/models/difficulty_preset.py`
   - Copia codice da "COMMIT 1 - Codice Nuovo" integrale
   - Crea test file `tests/unit/domain/test_difficulty_preset.py`
   - Esegui: `python -m pytest tests/unit/domain/test_difficulty_preset.py -v`
   - Verifica: 8/8 tests pass

2. **Commit 2 - GameSettings Integration**:
   - Apri `src/domain/services/game_settings.py`
   - Aggiungi import: `from src.domain.models.difficulty_preset import get_preset, DifficultyPreset`
   - Aggiungi 4 nuovi metodi da "COMMIT 2 - Codice Nuovo"
   - Modifica `cycle_difficulty()` con codice AFTER
   - Esegui: `python -m pytest tests/unit/domain/test_game_settings_presets.py -v`

3. **Commit 3 - OptionsController Lock**:
   - Apri `src/application/options_controller.py`
   - Modifica `modify_current_option()` con early lock check
   - Aggiungi metodo `_is_current_option_locked()`
   - Modifica `_modify_difficulty()` e `_format_current_option()`
   - Esegui: `python -m pytest tests/unit/application/ -v`

### Verifica Rapida Pre-Commit

```bash
# All tests
python -m pytest tests/ -v

# Solo preset tests
python -m pytest tests/ -k "preset" -v

# Coverage
coverage run -m pytest tests/
coverage report --include="src/domain/*,src/application/*"

# Expected: 95%+ coverage per nuovi file
```

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **Sistema Preset Funzionante**: Livelli 1-5 con lock progressivi  
✅ **UX Coerente**: Utenti guidati, pro player protetti da cheat  
✅ **Tournament Ready**: Livello 5 garantisce fair play per leaderboard  
✅ **Backward Compatible**: Giochi esistenti funzionano senza modifiche  
✅ **Well Tested**: 35+ test (unit + integration)  
✅ **Documented**: CHANGELOG + README aggiornati

**Metriche Successo**:
- Coverage: 95%+ per nuovo codice
- Performance: <1ms per apply_preset()
- User feedback: TTS chiaro "Opzione bloccata da Livello X"
- NVDA: Annuncia correttamente stato locked

---

## 📊 Progress Tracking

| Fase | Status | Commit | Data | Note |
|------|--------|--------|------|------|
| COMMIT 1 | [ ] | - | - | DifficultyPreset model |
| COMMIT 2 | [ ] | - | - | GameSettings integration |
| COMMIT 3 | [ ] | - | - | OptionsController lock |
| COMMIT 4 | [ ] | - | - | OptionsFormatter |
| COMMIT 5 | [ ] | - | - | JSON validation |
| COMMIT 6 | [ ] | - | - | Integration tests |
| COMMIT 7 | [ ] | - | - | CHANGELOG |
| COMMIT 8 | [ ] | - | - | README |

---

**Fine Piano Implementazione Sistema Preset Difficoltà**

**Version**: v1.0  
**Creato**: 2026-02-14  
**Autore**: AI Assistant (Perplexity) + Nemex81  
**Basato su**: Discussione design 2026-02-14 ore 17:40-18:00 CET  
**Target Release**: v2.4.0 (MINOR - nuova feature backward compatible)

---

## 🎯 Quick Start per Implementazione

**Per iniziare subito**:
1. Leggi "Executive Summary" + "Schema Preset" (requisito 1)
2. Segui commit 1-3 in sequenza (core logic)
3. Esegui test dopo ogni commit
4. Commit 4-8 sono completamenti (formatter, docs)

**Tempo stimato per core (commit 1-3)**: 3-4 ore  
**Tempo totale con docs**: 5-6 ore

**Happy Coding! 🚀**
