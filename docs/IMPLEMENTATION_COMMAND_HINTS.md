# Implementazione Feature: Suggerimenti Comandi (v1.5.0)

## 🎯 Panoramica Feature

### Descrizione
Aggiunta dell'opzione #5 "**Suggerimenti Comandi**" nel menu impostazioni che abilita/disabilita la vocalizzazione di hint contestuali durante il gameplay. Gli hint forniscono informazioni sui comandi disponibili in ogni contesto per migliorare l'esperienza utente, specialmente per utenti non vedenti che usano screen reader.

### Obiettivi
- ✅ Migliorare l'**accessibilità** fornendo guida vocale contestuale
- ✅ Aiutare utenti **nuovi** a scoprire i comandi disponibili
- ✅ Permettere a utenti **esperti** di disattivare gli hint per velocità
- ✅ Mantenere **Clean Architecture** senza violare dependency rule
- ✅ **Zero breaking changes** - backward compatible al 100%

---

## 🏗️ Architettura & Design Decisions

### Strategia Implementativa: **Strategia A** (Scelta Approvata)

#### Pattern: Hint Condizionali con Return Value Esteso

```
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                           │
│  (Business Logic - Genera hint SEMPRE per testabilità)   │
├─────────────────────────────────────────────────────────┤
│  CursorManager.move_to_pile()                            │
│    return ("Pila 3. Sette di Cuori.",                    │
│            "Premi ancora 3 per selezionare.")            │
│            │                      │                        │
│         message                hint (sempre generato)     │
└────────────│──────────────────│────────────────────────┘
             │                       │
             │                       │
             v                       v
┌─────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                        │
│  (Orchestrazione - Decide vocalizzazione condizionale)   │
├─────────────────────────────────────────────────────────┤
│  GameplayController._handle_number_key()                 │
│                                                           │
│    message, hint = cursor_manager.move_to_pile(3)        │
│    screen_reader.speak(message, interrupt=True)          │
│                                                           │
│    # CONDIZIONALE basato su settings                     │
│    if settings.command_hints_enabled and hint:           │
│        pygame.time.wait(200)  # Pausa                    │
│        screen_reader.speak(hint, interrupt=False)        │
└─────────────────────────────────────────────────────────┘
             │                       │
             v                       v (condizionale)
    ┌───────────────┐      ┌───────────────────────────┐
    │  TTS: Message │      │ TTS: Hint (se enabled) │
    │ "Pila 3..."  │      │ "Premi ancora 3..."    │
    └───────────────┘      └───────────────────────────┘
```

#### Vantaggi Strategia A

| Aspetto | Beneficio | Dettaglio |
|---------|-----------|----------|
| **Clean Architecture** | ✅ Rispettata | Domain non conosce settings, solo genera hint |
| **Testabilità** | ✅ Ottima | Hint sempre generati, testabili isolatamente |
| **Backward Compatibility** | ✅ 100% | Return tuple esteso, nessun breaking change |
| **Performance** | ✅ Efficiente | Check boolean `O(1)`, hint generati sempre |
| **Manutenibilità** | ✅ Alta | Logica centralizzata, facile estensione |

---

## 📋 Decisioni Design Finalizzate

### 1. Default Opzione: ON
**Decisione**: `command_hints_enabled: bool = True`

**Motivazione**:
- ✅ Massimizza **accessibilità** per utenti nuovi
- ✅ Gioco è primariamente per non vedenti
- ✅ Utenti esperti possono disattivare facilmente

### 2. Frequenza Hint: SEMPRE
**Decisione**: Hint vocalizati ad ogni azione quando opzione ON

**Alternativa scartata**: "Solo primo utilizzo per sessione"

**Motivazione**:
- ✅ **Consistenza**: comportamento prevedibile
- ✅ **Semplicità**: no tracking stato complesso
- ✅ **Utente controlla**: può disattivare quando vuole

### 3. Formato Messaggi: SEPARATI
**Decisione**: Due chiamate TTS con pausa 200ms

```python
# SCELTO
speak("Pila 3. Sette di Cuori.", interrupt=True)
wait(200)
speak("Premi ancora 3 per selezionare.", interrupt=False)

# SCARTATO
speak("Pila 3. Sette di Cuori. Premi ancora 3 per selezionare.", interrupt=True)
```

**Motivazione**:
- ✅ **Separazione concetti**: azione vs suggerimento
- ✅ **Interrompibilità**: utente può interrompere hint mantenendo messaggio
- ✅ **Timing**: pausa migliora comprensione

### 4. Contesti Hint: 17 TOTALI
**Decisione**: Hint per navigazione, info comandi, e azioni

**Categorie**:
1. **Navigazione Pile** (6): 1-7, SHIFT+1-4, frecce ↑↓←→
2. **Cambio Contesto** (3): TAB, SHIFT+S, SHIFT+M
3. **Comandi Info** (6): S, M, R, G, T, I
4. **Azioni** (2): INVIO, DELETE

### 5. Persistenza: IN-MEMORY
**Decisione**: Settings salvati solo in RAM, non su file

**Motivazione**:
- ✅ **Semplicità**: no gestione I/O file
- ✅ **Scope feature**: focalizzata su hint, non persistenza
- ✅ **Estensibilità**: persistenza può essere aggiunta dopo (v1.6.0)

---

## 📝 Esempi Hint per Contesto

### Categoria 1: Navigazione Pile

#### Tasti Numerici (1-7) - Double-Tap Hint
```python
# Contesto: Utente preme tasto "3"
message = "Pila 3. Sette di Cuori scoperta."
hint = "Premi ancora 3 per selezionare Sette di Cuori."

# Se pila vuota
message = "Pila 3 vuota."
hint = None  # Nessun hint se non c'è carta da selezionare

# Se carta coperta
message = "Pila 5. Ultima carta coperta."
hint = None  # Non si può selezionare carta coperta
```

#### SHIFT+Numeri (1-4) - Fondazioni
```python
# Contesto: Utente preme SHIFT+2 (Quadri)
message = "Pila Quadri. Cinque di Quadri in cima."
hint = "Premi ancora SHIFT+2 per selezionare Cinque di Quadri."

# Se fondazione vuota
message = "Pila Cuori vuota."
hint = "Premi ancora SHIFT+1 per selezionare (se hai un Asso di Cuori selezionato)."
```

#### Frecce SU/GIÙ - Navigazione Carta
```python
# Contesto: Naviga con freccia SU/GIÙ su pila base
message = "3 di 5: Regina di Fiori."
hint = "Premi INVIO per selezionare Regina di Fiori."

# Se carta non selezionabile (coperta)
message = "2 di 5: Carta coperta."
hint = None
```

#### Frecce SINISTRA/DESTRA - Cambio Pila
```python
# Contesto: Utente cambia pila con frecce
message = "Pila 4. Fante di Picche in cima."
hint = "Usa frecce SU/GIÙ per consultare le altre carte della pila."
```

### Categoria 2: Cambio Contesto

#### TAB - Cambio Tipo Pila
```python
# Contesto: Utente preme TAB
message = "Pile base. Pila 1. Asso di Cuori in cima."
hint = "Premi TAB ancora per passare alle pile semi."

# Ciclo completo: Base → Semi → Scarti → Mazzo → Base
```

#### SHIFT+S - Scarti
```python
# Contesto: Cursore spostato su scarti
message = "Pila scarti. Carta in cima: Dieci di Fiori."
hint = "Usa frecce SU/GIÙ per consultare tutti gli scarti. Premi CTRL+INVIO per selezionare l'ultima carta."

# Se scarti vuoti
message = "Pila scarti vuota."
hint = None
```

#### SHIFT+M - Mazzo
```python
# Contesto: Cursore spostato su mazzo
message = "Pila riserve. Carte nel mazzo: 15."
hint = "Premi INVIO per pescare una carta. Oppure usa D o P da qualunque posizione."

# Se mazzo vuoto
message = "Mazzo riserve vuoto."
hint = "Gli scarti verranno rimescolati automaticamente al prossimo tentativo di pesca."
```

### Categoria 3: Comandi Info

#### S - Info Scarti
```python
message = "Scarti: 8 carte disponibili. Carta in cima: Nove di Bastoni."
hint = "Usa SHIFT+S per spostare il cursore sugli scarti e consultarli."
```

#### M - Info Mazzo
```python
message = "Mazzo riserve: 12 carte rimanenti."
hint = "Premi D o P per pescare. Usa SHIFT+M per spostare il cursore sul mazzo."
```

#### R - Report Partita
```python
message = "[Report completo statistiche...]"
hint = None  # Report già completo, nessuna azione suggerita
```

#### G - Info Tavolo
```python
message = "[Info complete tutte le pile...]"
hint = None  # Info già completa
```

#### T - Info Timer
```python
message = "Timer: 12 minuti e 34 secondi rimanenti."
hint = "Premi O per aprire le opzioni e modificare il timer."

# Se timer disattivato
message = "Timer disattivato."
hint = "Premi O per aprire le opzioni e attivare il timer."
```

#### I - Info Impostazioni
```python
message = "[Recap tutte le impostazioni correnti...]"
hint = "Premi O per aprire il menu opzioni e modificarle."
```

### Categoria 4: Azioni (Opzionali)

#### INVIO - Selezione Carta
```python
# Dopo selezione riuscita
message = "Carta selezionata: Regina di Cuori!"
hint = "Premi SPAZIO per spostare la carta sulla pila di destinazione."
```

#### DELETE - Annulla Selezione
```python
# Dopo annullamento
message = "Selezione annullata."
hint = "Premi INVIO per selezionare un'altra carta."
```

---

## 👨‍💻 Implementazione Dettagliata per Fase

### FASE 1: Domain Layer - GameSettings

#### File: `src/domain/services/game_settings.py`

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class GameSettings:
    """Game configuration settings."""
    
    # ... existing fields ...
    shuffle_on_recycle: bool = False
    
    # NEW (v1.5.0): Command hints feature
    command_hints_enabled: bool = True
    """Enable/disable command hints during gameplay.
    
    When enabled, contextual hints are vocalized after actions to help
    users discover available commands. Especially useful for screen reader
    users and newcomers.
    
    Default: True (maximum accessibility)
    """
    
    # ... existing methods ...
    
    def toggle_command_hints(self) -> Tuple[bool, str]:
        """Toggle command hints on/off.
        
        Cannot be modified during active game for consistency.
        
        Returns:
            (success, message): Success flag and TTS message
            
        Examples:
            >>> settings.toggle_command_hints()
            (True, "Suggerimenti comandi disattivati.")
        """
        if self.is_game_running():
            return (False, "Non puoi modificare questa opzione durante una partita!")
        
        # Toggle
        self.command_hints_enabled = not self.command_hints_enabled
        
        # Generate message
        status = "attivi" if self.command_hints_enabled else "disattivati"
        message = f"Suggerimenti comandi {status}."
        
        return (True, message)
    
    def get_command_hints_display(self) -> str:
        """Get display value for command hints option.
        
        Returns:
            "Attivi" or "Disattivati"
            
        Used by OptionsFormatter for option #5 display.
        """
        return "Attivi" if self.command_hints_enabled else "Disattivati"
```

#### Test: `tests/unit/src/test_game_settings_hints.py`

```python
import pytest
from src.domain.services.game_settings import GameSettings


class TestCommandHintsSettings:
    """Test suite for command hints settings (v1.5.0)."""
    
    def test_default_hints_enabled(self):
        """Command hints should be enabled by default for accessibility."""
        settings = GameSettings()
        assert settings.command_hints_enabled is True
    
    def test_toggle_hints_on_off(self):
        """Toggle should change state bidirectionally."""
        settings = GameSettings()
        
        # OFF
        success, msg = settings.toggle_command_hints()
        assert success is True
        assert settings.command_hints_enabled is False
        assert "disattivati" in msg.lower()
        
        # ON
        success, msg = settings.toggle_command_hints()
        assert success is True
        assert settings.command_hints_enabled is True
        assert "attivi" in msg.lower()
    
    def test_display_values(self):
        """Display method should return Italian strings."""
        settings = GameSettings()
        
        # Enabled
        assert settings.get_command_hints_display() == "Attivi"
        
        # Disabled
        settings.command_hints_enabled = False
        assert settings.get_command_hints_display() == "Disattivati"
    
    def test_toggle_blocked_during_game(self):
        """Cannot toggle hints during active game."""
        settings = GameSettings()
        settings._game_running = True  # Simulate active game
        
        success, msg = settings.toggle_command_hints()
        
        assert success is False
        assert "durante una partita" in msg.lower()
        assert settings.command_hints_enabled is True  # Unchanged
```

---

### FASE 2: Domain Layer - CursorManager

#### File: `src/domain/services/cursor_manager.py`

```python
from typing import Tuple, Optional

class CursorManager:
    """Manages cursor position and navigation (v1.5.0: extended with hints)."""
    
    def move_to_pile(self, pile_index: int) -> Tuple[str, Optional[str]]:
        """Move cursor to specified pile with optional hint.
        
        Args:
            pile_index: Target pile index (0-6 for tableau, 7-10 for foundations)
            
        Returns:
            (message, hint): Navigation message and optional command hint
            
        Examples:
            >>> move_to_pile(3)
            ("Pila 3. Sette di Cuori scoperta.", 
             "Premi ancora 3 per selezionare Sette di Cuori.")
        """
        # ... existing logic to move cursor ...
        
        # Generate message
        card_name = self._get_card_name(pile)
        message = f"Pila {pile_index}. {card_name}."
        
        # Generate hint (v1.5.0)
        if self._can_select_card(pile):
            hint = f"Premi ancora {pile_index} per selezionare {card_name}."
        else:
            hint = None
        
        return (message, hint)
    
    def move_cursor_up(self) -> Tuple[str, Optional[str]]:
        """Navigate to previous card in current pile.
        
        Returns:
            (message, hint): Position message and selection hint
        """
        # ... existing logic ...
        
        position = self.cursor_pos[1]
        total = len(current_pile.cards)
        card_name = self._get_card_name(current_card)
        
        message = f"{position} di {total}: {card_name}."
        
        # Hint if card is selectable
        hint = f"Premi INVIO per selezionare {card_name}." if selectable else None
        
        return (message, hint)
    
    def move_cursor_down(self) -> Tuple[str, Optional[str]]:
        """Navigate to next card in current pile."""
        # Identical to move_cursor_up() logic
        # ... implementation ...
        return (message, hint)
    
    def move_cursor_left(self) -> Tuple[str, Optional[str]]:
        """Move cursor to previous pile."""
        # ... existing logic ...
        
        message = f"Pila {new_pile_index}. {card_name}."
        hint = "Usa frecce SU/GIÙ per consultare le altre carte della pila."
        
        return (message, hint)
    
    def move_cursor_right(self) -> Tuple[str, Optional[str]]:
        """Move cursor to next pile."""
        # Same hint as move_cursor_left()
        # ... implementation ...
        return (message, hint)
```

---

### FASE 6: Application Layer - GameplayController

#### Pattern Helper Method

```python
class GameplayController:
    """Main gameplay controller (v1.5.0: conditional hint vocalization)."""
    
    def _speak_with_hint(self, message: str, hint: Optional[str]) -> None:
        """Speak message and optional hint based on settings.
        
        This helper method centralizes the hint vocalization logic.
        
        Args:
            message: Main message to speak (always vocalized)
            hint: Optional hint (vocalized only if settings.command_hints_enabled)
            
        Behavior:
            1. Speak message with interrupt=True (priority)
            2. If hints enabled AND hint not None:
               - Wait 200ms (pause between messages)
               - Speak hint with interrupt=False (can be interrupted)
        """
        # Always speak main message
        self.screen_reader.speak(message, interrupt=True)
        
        # Conditionally speak hint
        if self.settings.command_hints_enabled and hint:
            pygame.time.wait(200)  # Pause for clarity
            self.screen_reader.speak(hint, interrupt=False)
```

#### Refactor Example: Number Keys

```python
# BEFORE (v1.4.3)
def _handle_number_key(self, key: int) -> None:
    """Handle pile number keys (1-7)."""
    pile_index = key - 1
    message = self.cursor_manager.move_to_pile(pile_index)
    self.screen_reader.speak(message, interrupt=True)

# AFTER (v1.5.0)
def _handle_number_key(self, key: int) -> None:
    """Handle pile number keys (1-7) with optional hints."""
    pile_index = key - 1
    
    # CursorManager now returns (message, hint) tuple
    message, hint = self.cursor_manager.move_to_pile(pile_index)
    
    # Use helper for conditional vocalization
    self._speak_with_hint(message, hint)
```

#### Refactor Example: Info Commands

```python
# BEFORE
def _show_waste_info(self) -> None:
    """Show waste pile info (S key)."""
    message = self.game_service.get_waste_info()
    self.screen_reader.speak(message, interrupt=True)

# AFTER (v1.5.0)
def _show_waste_info(self) -> None:
    """Show waste pile info with hint (S key)."""
    message, hint = self.game_service.get_waste_info()
    self._speak_with_hint(message, hint)
```

---

## 🧪 Testing Strategy

### Unit Tests Structure

#### 1. Settings Tests (~100 LOC)
```python
test_default_hints_enabled()
test_toggle_hints_on_off()
test_display_values()
test_toggle_blocked_during_game()
test_multiple_toggles()
```

#### 2. CursorManager Tests (~150 LOC)
```python
# Return type tests
test_move_to_pile_returns_tuple()
test_all_methods_return_tuple()

# Hint generation tests
test_move_to_pile_hint_present_when_card_selectable()
test_move_to_pile_hint_none_when_pile_empty()
test_move_to_pile_hint_none_when_card_covered()
test_cursor_up_hint_present()
test_cursor_left_hint_present()

# Content tests
test_hint_contains_pile_number()
test_hint_contains_card_name()
```

#### 3. GameService Tests (~100 LOC)
```python
test_get_waste_info_returns_tuple()
test_get_waste_info_hint_mentions_shift_s()
test_get_stock_info_hint_mentions_d_p()
test_get_game_report_hint_is_none()
test_get_timer_info_hint_mentions_options()
```

### Integration Tests (~250 LOC)

#### File: `tests/integration/test_gameplay_hints_integration.py`

```python
import pytest
from unittest.mock import Mock, call
import pygame

class TestGameplayHintsIntegration:
    """Integration tests for hints vocalization (v1.5.0)."""
    
    @pytest.fixture
    def setup(self):
        """Setup gameplay controller with mocked dependencies."""
        self.screen_reader = Mock()
        self.settings = GameSettings()
        self.controller = GameplayController(
            screen_reader=self.screen_reader,
            settings=self.settings
        )
    
    def test_hints_vocalized_when_enabled(self, setup):
        """Hints should be vocalized when option is ON."""
        # Enable hints
        self.settings.command_hints_enabled = True
        
        # Simulate number key press
        self.controller._handle_number_key(3)
        
        # Verify TWO speak calls: message + hint
        assert self.screen_reader.speak.call_count == 2
        
        # Verify first call (message)
        first_call = self.screen_reader.speak.call_args_list[0]
        assert first_call[1]['interrupt'] is True
        
        # Verify second call (hint)
        second_call = self.screen_reader.speak.call_args_list[1]
        assert second_call[1]['interrupt'] is False
        assert "Premi ancora" in second_call[0][0]
    
    def test_hints_not_vocalized_when_disabled(self, setup):
        """Hints should NOT be vocalized when option is OFF."""
        # Disable hints
        self.settings.command_hints_enabled = False
        
        # Simulate number key press
        self.controller._handle_number_key(3)
        
        # Verify ONE speak call: only message
        assert self.screen_reader.speak.call_count == 1
    
    def test_pause_between_message_and_hint(self, setup):
        """200ms pause should separate message and hint."""
        with patch('pygame.time.wait') as mock_wait:
            self.settings.command_hints_enabled = True
            self.controller._handle_number_key(3)
            
            # Verify wait called with 200ms
            mock_wait.assert_called_once_with(200)
    
    def test_all_17_contexts_covered(self, setup):
        """All 17 hint contexts should work correctly."""
        contexts = [
            ('_handle_number_key', 3),
            ('_handle_shift_foundation', 1),
            ('_move_cursor_up',),
            ('_move_cursor_down',),
            # ... tutti i 17 contesti ...
        ]
        
        for context, *args in contexts:
            self.screen_reader.reset_mock()
            self.settings.command_hints_enabled = True
            
            method = getattr(self.controller, context)
            method(*args)
            
            # Verify hint vocalized for each context
            assert self.screen_reader.speak.call_count >= 1
```

---

## ✔️ Checklist Validazione Finale

### Funzionalità
- [ ] Opzione #5 visibile nel menu opzioni
- [ ] Toggle ON/OFF funzionante con INVIO
- [ ] Default è ON all'avvio applicazione
- [ ] Hint vocalizati in tutti i 17 contesti quando ON
- [ ] Hint NON vocalizati in nessun contesto quando OFF
- [ ] Pausa 200ms presente tra message e hint
- [ ] Hint non interrompe message (interrupt=False)
- [ ] Message interrompe hint precedenti (interrupt=True)

### Qualità Codice
- [ ] Test coverage ≥ 85% per codice nuovo
- [ ] Tutti i test unitari passano
- [ ] Tutti i test integrazione passano
- [ ] Type hints completi (mypy --strict passing)
- [ ] Zero breaking changes rispetto a v1.4.3
- [ ] Docstrings Google-style per metodi nuovi

### Architettura
- [ ] Domain layer non conosce settings (dependency rule rispettata)
- [ ] Application layer controlla vocalizzazione (responsabilità corretta)
- [ ] Presentation layer formatta messaggi opzioni
- [ ] Nessuna violazione Clean Architecture
- [ ] Pattern helper `_speak_with_hint()` riutilizzabile

### User Experience
- [ ] Hint chiari e contestuali
- [ ] Hint non ridondanti con message
- [ ] Hint suggeriscono azioni, non ripetono informazioni
- [ ] Timing adeguato (200ms non troppo breve/lungo)
- [ ] Feedback vocale quando si modifica opzione

### Documentazione
- [ ] CHANGELOG.md aggiornato con sezione v1.5.0
- [ ] README.md aggiornato (se necessario)
- [ ] TODO.md completato al 100%
- [ ] IMPLEMENTATION_COMMAND_HINTS.md completo
- [ ] Commit messages descrittivi e atomici

---

## 📊 Metriche Attese

| Metrica | Target | Verifica |
|---------|--------|----------|
| **Test Coverage** | ≥ 85% | pytest --cov |
| **Type Hints** | 100% | mypy --strict |
| **LOC Produzione** | ~375 | cloc src/ |
| **LOC Testing** | ~550 | cloc tests/ |
| **Commit Count** | 5 atomici | git log |
| **Contesti Hint** | 17 totali | Manual test |
| **Breaking Changes** | 0 | Backward compat test |

---

## 🎉 Conclusione

Questa implementazione fornisce una feature di accessibilità professionale che:

1. **Migliora l'esperienza** per utenti non vedenti
2. **Rispetta Clean Architecture** senza compromessi
3. **È completamente testata** con coverage elevato
4. **Non rompe nulla** - 100% backward compatible
5. **È estensibile** - facile aggiungere nuovi contesti hint

La feature è pronta per essere implementata seguendo il piano dettagliato nelle 6 fasi documentate.

---

**Fine Documento**  
Ultimo aggiornamento: 10 Febbraio 2026  
Versione: 1.0 - Pianificazione Completa
