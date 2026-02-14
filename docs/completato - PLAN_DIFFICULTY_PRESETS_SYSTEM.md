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
- ❌ Configurazioni illogiche possibili (es. "Livello 5 Maestro" con 1 carta pescata)
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

| Opzione | Livello 1<br>**Principiante** | Livello 2<br>**Facile** | Livello 3<br>**Normale** | Livello 4<br>**Esperto** | Livello 5<br>**Maestro** |
|---------|------|------|------|------|------|
| **Carte Pescate** | 🔓 **1-3**<br>*(default 1)* | 🔓 **1-3**<br>*(default 2)* | 🔒 **3** | 🔒 **3** | 🔒 **3** |
| **Timer** | 🔒 **OFF** | 🔓 **0-60 min** | 🔓 **0-60 min** | 🔒 **30 min** | 🔒 **15 min** |
| **Modalità Timer** | 🚫 *N/A* | 🔒 **PERMISSIVE** | 🔓 **PERM/STRICT** | 🔒 **PERMISSIVE** | 🔒 **STRICT** |
| **Riciclo Scarti** | 🔓 **Inv/Mes**<br>*(default Mes)* | 🔓 **Inv/Mes**<br>*(default Mes)* | 🔓 **Inv/Mes**<br>*(default Inv)* | 🔒 **Inversione** | 🔒 **Inversione** |
| **Sistema Punti** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔒 **ON** |
| **Suggerimenti** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔓 **ON/OFF** | 🔒 **OFF** | 🔒 **OFF** |

**Note Descrittive Preset**:
- **Livello 3 (Normale)**: Segue regole Vegas standard (3 carte, preferenza inversione)
- **Livello 4 (Esperto)**: Modalità Time Attack con limite 30 minuti
- **Livello 5 (Maestro)**: Modalità Tournament strict (15 min, tutte opzioni bloccate)

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
4. TTS: "Difficoltà Livello 4, Esperto. Timer bloccato su 30 minuti. Suggerimenti disattivati."

**File Coinvolti**:
- `src/application/options_controller.py` - MODIFIED ⚙️ (metodo `_modify_difficulty()`)

---

### 3. Blocco Modifica Opzioni Locked

**Comportamento Atteso**:
1. Utente a Livello 5 (Maestro)
2. Naviga su "Carte Pescate" (bloccata su 3)
3. TTS: "2 di 8: Carte Pescate, 3. Opzione bloccata da Livello Difficoltà 5. 🔒"
4. Preme INVIO per modificare
5. **Sistema rifiuta modifica**
6. TTS: "Impossibile modificare. Opzione bloccata da Livello Difficoltà Maestro. Cambia livello difficoltà per sbloccare."

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
│  ┌────────────────────────────────────────────────────────┐   │
│  │ OptionsFormatter                                      │   │
│  │ + format_option_locked(option_name, level)           │   │  🆕
│  │ + format_preset_applied(level, changes_list)         │   │  🆕
│  │ + format_option_item() [MODIFIED]                    │   │  ⚙️
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ OptionsController                                     │   │
│  │ + _modify_difficulty() [MODIFIED]                    │   │  ⚙️
│  │ + modify_current_option() [MODIFIED]                 │   │  ⚙️
│  │ + _format_current_option() [MODIFIED]                │   │  ⚙️
│  │ + _is_current_option_locked() → bool                 │   │  🆕
│  └────────────────────────────────────────────────────────┘   │
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
├── PLAN_FIX_DIFFICULTY_RADIOBOX_5_LEVELS.md  # PREREQUISITE
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
        name: Display name (es. "Principiante", "Maestro")
        locked_options: Set of option names that cannot be modified
        defaults: Default values for unlocked options
        fixed_values: Fixed values for locked options (override user settings)
    
    Example:
        >>> preset = PRESETS[5]  # Maestro (Tournament mode)
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
        name="Normale",
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
        name="Esperto",
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
            "max_time_game": 1800,        # 30 minutes (Time Attack)
            "timer_strict_mode": False,   # PERMISSIVE (can finish over time)
            "shuffle_discards": False,    # Inversione (fair play)
            "command_hints_enabled": False,  # No hints (pro mode)
        }
    ),
    
    5: DifficultyPreset(
        level=5,
        name="Maestro",
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
            "max_time_game": 900,         # 15 minutes (Tournament strict)
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
        
    Example:
        >>> preset = get_preset(5)
        >>> preset.name
        'Maestro'
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
    
    def test_level_names_match_unified_nomenclature(self):
        """Preset names must match unified nomenclature."""
        expected_names = {
            1: "Principiante",
            2: "Facile",
            3: "Normale",
            4: "Esperto",
            5: "Maestro"
        }
        for level, expected_name in expected_names.items():
            assert PRESETS[level].name == expected_name
```

**Commit Message**:
```
feat(domain): add DifficultyPreset model with 5-level configuration

Introduce immutable preset configurations for difficulty levels 1-5:
- Level 1 (Principiante): Timer locked OFF, 1 card default
- Level 2 (Facile): Timer mode locked PERMISSIVE, 2 cards default
- Level 3 (Normale): 3 cards locked, inversione default (Vegas rules)
- Level 4 (Esperto): 30min timer, all competitive options locked (Time Attack)
- Level 5 (Maestro): 15min STRICT timer, all options locked (Tournament)

Features:
- is_locked(option_name) → bool: Check if option modifiable
- get_value(option_name) → Any: Get fixed/default value
- Immutable dataclass (frozen=True) for thread-safety
- Type-safe Dict[int, DifficultyPreset] registry

Nomenclature: Unified with PLAN_FIX_DIFFICULTY_RADIOBOX_5_LEVELS.md

Impact:
- NEW: src/domain/models/difficulty_preset.py
- NEW: tests/unit/domain/test_difficulty_preset.py (8 tests)
- Zero modifications to existing code (new module)

Version: v2.4.0
```

---

### COMMIT 2-8: [Implementation Details]

[Resto del piano implementazione invariato - vedi piano completo]

**COMMIT 2**: Aggiungere apply_difficulty_preset() a GameSettings  
**COMMIT 3**: Bloccare modifiche opzioni locked in OptionsController  
**COMMIT 4**: Aggiungere metodi formatter in OptionsFormatter  
**COMMIT 5**: Modificare load_from_dict() per applicare preset al caricamento  
**COMMIT 6**: Aggiungere Integration Tests (5 scenari end-to-end)  
**COMMIT 7**: Aggiornare CHANGELOG.md con v2.4.0  
**COMMIT 8**: Aggiornare README.md con nuovo sistema

[Dettagli commit 2-8 rimangono invariati dal piano originale]

---

## 🧪 Testing Strategy

[Sezione testing invariata - 30 unit test + 5 integration test]

---

## ✅ Common Pitfalls to Avoid

[Sezione pitfalls invariata]

---

## 📚 References

### Internal Architecture Docs
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `docs/PLAN_FIX_DIFFICULTY_RADIOBOX_5_LEVELS.md` - **PREREQUISITE** (RadioBox 5 levels)
- `docs/PLAN_FIX_TIMER_OPTION_COMBOBOX_ONLY.md` - Esempio piano simile

### Related Code Files
- `src/domain/services/game_settings.py` - Settings service (da modificare)
- `src/application/options_controller.py` - Controller opzioni (da modificare)
- `src/presentation/options_formatter.py` - TTS formatter (da modificare)

---

## 📝 Note Operative per Copilot

[Sezione istruzioni operative invariata]

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **Sistema Preset Funzionante**: Livelli 1-5 con lock progressivi  
✅ **UX Coerente**: Utenti guidati, pro player protetti da cheat  
✅ **Tournament Ready**: Livello 5 (Maestro) garantisce fair play per leaderboard  
✅ **Backward Compatible**: Giochi esistenti funzionano senza modifiche  
✅ **Well Tested**: 35+ test (unit + integration)  
✅ **Documented**: CHANGELOG + README aggiornati  
✅ **Nomenclatura Unificata**: Coerente con RadioBox e GameSettings

**Metriche Successo**:
- Coverage: 95%+ per nuovo codice
- Performance: <1ms per apply_preset()
- User feedback: TTS chiaro "Opzione bloccata da Livello X"
- NVDA: Annuncia correttamente stato locked
- Nomenclatura: Zero discrepanze tra UI, domain, presentation

---

## 📊 Progress Tracking

| Fase | Status | Commit | Data | Note |
|------|--------|--------|------|------|
| PREREQ: RadioBox 5 livelli | [ ] | - | - | Fix UI prerequisito |
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

**Version**: v1.1 (Nomenclatura Corretta)  
**Creato**: 2026-02-14  
**Aggiornato**: 2026-02-14 (Allineamento nomenclatura)  
**Autore**: AI Assistant (Perplexity) + Nemex81  
**Basato su**: Discussione design 2026-02-14 ore 17:40-18:00 CET  
**Target Release**: v2.4.0 (MINOR - nuova feature backward compatible)

---

## 🎯 Quick Start per Implementazione

**Per iniziare subito**:
1. **PREREQUISITO**: Implementa PLAN_FIX_DIFFICULTY_RADIOBOX_5_LEVELS.md (15 min)
2. Leggi "Executive Summary" + "Schema Preset" (requisito 1)
3. Segui commit 1-3 in sequenza (core logic)
4. Esegui test dopo ogni commit
5. Commit 4-8 sono completamenti (formatter, docs)

**Tempo stimato per core (commit 1-3)**: 3-4 ore  
**Tempo totale con docs**: 5-6 ore

**Happy Coding! 🚀**
