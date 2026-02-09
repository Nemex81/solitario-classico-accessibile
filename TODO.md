# ✅ TODO - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Focus**: Bug Fix Release  

---

## 🐛 BUG #3: Settings Integration in new_game()

**Priorità**: 🔴 CRITICA  
**Status**: 🔧 IN PROGRESS  
**File**: `src/application/game_engine.py`  

---

### 📝 TASK BREAKDOWN

#### **FASE 1: Engine Initialization** (1/6)

**File**: `src/application/game_engine.py`

- [ ] **Task 1.1**: Modificare `__init__()` signature
  ```python
  def __init__(
      self,
      table: GameTable,
      service: GameService,
      rules: SolitaireRules,
      cursor: CursorManager,
      selection: SelectionManager,
      screen_reader: Optional[ScreenReader] = None,
      settings: Optional[GameSettings] = None  # NEW
  ):
  ```

- [ ] **Task 1.2**: Salvare settings come attributo
  ```python
  self.settings = settings
  ```

- [ ] **Task 1.3**: Inizializzare attributi configurabili
  ```python
  self.draw_count = 1  # Default, sarà aggiornato da settings
  self.shuffle_on_recycle = False  # Default
  ```

---

#### **FASE 2: Factory Method Update** (2/6)

**File**: `src/application/game_engine.py`

- [ ] **Task 2.1**: Modificare `create()` per passare settings
  ```python
  @classmethod
  def create(cls, audio_enabled=True, tts_engine="auto", verbose=1, 
             settings: Optional[GameSettings] = None):
      # ... crea componenti ...
      return cls(table, service, rules, cursor, selection, 
                 screen_reader, settings)  # ✅ Passa settings
  ```

- [ ] **Task 2.2**: Verificare che test.py passa settings correttamente
  ```python
  # In test.py:
  self.engine = GameEngine.create(
      audio_enabled=True,
      tts_engine="auto",
      verbose=1,
      settings=self.settings  # ✅ Già presente (Bug #1)
  )
  ```

---

#### **FASE 3: Deck Recreation Logic** (3/6) ⭐ **CRITICO**

**File**: `src/application/game_engine.py` > `new_game()`

- [ ] **Task 3.1**: Implementare controllo deck type change
  ```python
  def new_game(self):
      # ✅ NUOVO: Controlla se deck type è cambiato
      if self.settings:
          current_is_neapolitan = self.table.mazzo.is_neapolitan_deck()
          should_be_neapolitan = (self.settings.deck_type == "neapolitan")
          
          if current_is_neapolitan != should_be_neapolitan:
              self._recreate_deck_and_table(should_be_neapolitan)
  ```

- [ ] **Task 3.2**: Implementare metodo helper `_recreate_deck_and_table()`
  ```python
  def _recreate_deck_and_table(self, use_neapolitan: bool) -> None:
      """Ricrea deck e table quando l'utente cambia tipo di mazzo."""
      # Crea nuovo deck
      if use_neapolitan:
          new_deck = NeapolitanDeck()
      else:
          new_deck = FrenchDeck()
      
      new_deck.crea()
      new_deck.mischia()
      
      # Ricrea table
      self.table = GameTable(new_deck)
      
      # Aggiorna rules (deck-dependent)
      self.rules = SolitaireRules(new_deck)
      
      # Aggiorna service references
      self.service.table = self.table
      self.service.rules = self.rules
      
      # Aggiorna cursor reference
      self.cursor.table = self.table
      
      # TTS feedback
      if self.screen_reader:
          deck_name = "napoletane" if use_neapolitan else "francesi"
          self.screen_reader.tts.speak(
              f"Tipo di mazzo cambiato: carte {deck_name}.",
              interrupt=True
          )
  ```

- [ ] **Task 3.3**: Testare switch French → Neapolitan
  - Avvia partita con French
  - Cambia opzioni a Neapolitan
  - Nuova partita
  - Verifica: 40 carte distribuite (28 tavolo + 12 mazzo)

- [ ] **Task 3.4**: Testare switch Neapolitan → French
  - Avvia partita con Neapolitan
  - Cambia opzioni a French
  - Nuova partita
  - Verifica: 52 carte distribuite (28 tavolo + 24 mazzo)

---

#### **FASE 4: Timer Settings Application** (4/6)

**File**: `src/application/game_engine.py` > `new_game()`

- [ ] **Task 4.1**: Applicare timer settings prima di start_game()
  ```python
  def new_game(self):
      # ... (dopo deck recreation)
      
      # ✅ Applica timer settings
      if self.settings:
          if self.settings.timer_enabled:
              # Abilita timer con durata da settings (in minuti)
              timer_seconds = self.settings.timer_duration * 60
              self.service.timer_manager.set_enabled(True)
              self.service.timer_manager.set_duration(timer_seconds)
              
              if self.screen_reader:
                  self.screen_reader.tts.speak(
                      f"Timer attivato: {self.settings.timer_duration} minuti.",
                      interrupt=False
                  )
          else:
              # Disabilita timer
              self.service.timer_manager.set_enabled(False)
      
      # Avvia partita (timer parte se abilitato)
      self.service.start_game()
  ```

- [ ] **Task 4.2**: Verificare metodi timer_manager esistenti
  - Controllare se `set_enabled()` esiste
  - Controllare se `set_duration()` esiste
  - Se mancanti, implementare in `TimerManager`

- [ ] **Task 4.3**: Testare timer 10 minuti
  - Imposta timer 10 min nelle opzioni
  - Nuova partita
  - Verifica TTS dice "Timer attivato: 10 minuti"
  - Verifica timer conta correttamente

- [ ] **Task 4.4**: Testare timer disabilitato
  - Disabilita timer nelle opzioni
  - Nuova partita
  - Verifica timer non parte

---

#### **FASE 5: Difficulty & Draw Count** (5/6)

**File**: `src/application/game_engine.py` > `new_game()`

- [ ] **Task 5.1**: Applicare difficulty settings per draw count
  ```python
  def new_game(self):
      # ... (dopo timer)
      
      # ✅ Applica livello difficoltà
      if self.settings:
          if self.settings.difficulty_level == 1:
              self.draw_count = 1  # Facile: 1 carta alla volta
          elif self.settings.difficulty_level == 2:
              self.draw_count = 3  # Medio: 3 carte
          elif self.settings.difficulty_level == 3:
              self.draw_count = 5  # Difficile: 5 carte
          
          if self.screen_reader:
              self.screen_reader.tts.speak(
                  f"Livello di difficoltà: {self.settings.difficulty_level}. "
                  f"Pesca: {self.draw_count} carta/e.",
                  interrupt=False
              )
  ```

- [ ] **Task 5.2**: Modificare `draw_from_stock()` per usare `self.draw_count`
  ```python
  def draw_from_stock(self, count: int = None) -> Tuple[bool, str]:
      # ✅ Se count non specificato, usa settings
      if count is None:
          count = self.draw_count if hasattr(self, 'draw_count') else 1
      
      success, generic_msg, cards = self.service.draw_cards(count)
      # ...
  ```

- [ ] **Task 5.3**: Testare livello 1 (1 carta)
  - Imposta livello 1
  - Nuova partita
  - Pesca dal mazzo (D/P)
  - Verifica: 1 carta pescata

- [ ] **Task 5.4**: Testare livello 2 (3 carte)
  - Imposta livello 2
  - Nuova partita
  - Pesca dal mazzo
  - Verifica: 3 carte pescate

- [ ] **Task 5.5**: Testare livello 3 (5 carte)
  - Imposta livello 3
  - Nuova partita
  - Pesca dal mazzo
  - Verifica: 5 carte pescate (se disponibili)

---

#### **FASE 6: Waste Shuffle Setting** (6/6)

**File**: `src/application/game_engine.py` > `recycle_waste()`

- [ ] **Task 6.1**: Modificare `recycle_waste()` per usare settings
  ```python
  def recycle_waste(self, shuffle: bool = None) -> Tuple[bool, str]:
      # ✅ Se shuffle non specificato, usa settings
      if shuffle is None and self.settings:
          shuffle = self.settings.waste_shuffle
      
      # Default se nessuna configurazione
      if shuffle is None:
          shuffle = False  # Default: si girano (non si mischiano)
      
      # Esegui recycle con shuffle configurato
      success, generic_msg = self.service.recycle_waste(shuffle)
      # ...
  ```

- [ ] **Task 6.2**: Salvare preferenza in `new_game()`
  ```python
  def new_game(self):
      # ... (dopo draw_count)
      
      # ✅ Salva preferenza scarti
      if self.settings:
          self.shuffle_on_recycle = self.settings.waste_shuffle
          
          if self.screen_reader:
              mode = "si mischiano" if self.shuffle_on_recycle else "si girano"
              self.screen_reader.tts.speak(
                  f"Scarti: {mode}.",
                  interrupt=False
              )
  ```

- [ ] **Task 6.3**: Testare scarti che si mischiano
  - Imposta "Scarti: Si mischiano"
  - Nuova partita
  - Pesca tutte le carte dal mazzo
  - Ricicla scarti
  - Verifica TTS dice "Rimescolo gli scarti in modo casuale"

- [ ] **Task 6.4**: Testare scarti che si girano
  - Imposta "Scarti: Si girano"
  - Nuova partita
  - Pesca tutte le carte
  - Ricicla scarti
  - Verifica TTS dice "Rigiro gli scarti nel mazzo"

---

### 🧪 TESTING COMPLETO

#### **Test Scenario 1: Tutte le Settings Insieme**
- [ ] Configura:
  - Mazzo: Napoletane
  - Timer: 10 minuti
  - Livello: 2 (3 carte)
  - Scarti: Si mischiano
- [ ] Salva e avvia nuova partita
- [ ] Verifica TTS annuncia TUTTE le impostazioni
- [ ] Verifica:
  - ✅ 40 carte distribuite (Napoletane)
  - ✅ Timer parte da 10:00
  - ✅ Pesca 3 carte alla volta
  - ✅ Scarti mischiano al riciclo

#### **Test Scenario 2: Cambio Settings tra Partite**
- [ ] Partita 1: French, no timer, livello 1
- [ ] Termina partita
- [ ] Cambia: Neapolitan, timer 5 min, livello 3
- [ ] Partita 2: Verifica tutti i cambiamenti applicati
- [ ] Termina partita
- [ ] Cambia: French, timer 15 min, livello 2
- [ ] Partita 3: Verifica tutti i cambiamenti applicati

#### **Test Scenario 3: Settings Persistence**
- [ ] Configura: Napoletane, timer 10 min, livello 2
- [ ] Salva
- [ ] Chiudi completamente l'app
- [ ] Riapri l'app
- [ ] Nuova partita
- [ ] Verifica: Settings ancora attive

#### **Test Scenario 4: Backward Compatibility**
- [ ] Crea engine senza settings: `GameEngine.create()`
- [ ] Verifica: Comportamento default (French, no timer, 1 carta)
- [ ] Verifica: Nessun crash o errore

---

### 📝 CHECKLIST FINALE

**Codice**:
- [ ] Tutte le modifiche implementate (Task 1.1 - 6.4)
- [ ] Nessun warning o errore
- [ ] Codice commentato dove necessario
- [ ] Docstrings aggiornati

**Testing**:
- [ ] Test Scenario 1 completo ✅
- [ ] Test Scenario 2 completo ✅
- [ ] Test Scenario 3 completo ✅
- [ ] Test Scenario 4 completo ✅

**Documentazione**:
- [x] BUGS.md aggiornato con Bug #3
- [x] TODO.md creato con checklist
- [ ] CHANGELOG.md aggiornato
- [ ] Docstrings metodi modificati

**Commit**:
- [ ] Commit atomici per ogni fase
- [ ] Commit messages seguono standard
- [ ] Branch aggiornato su GitHub

**Review**:
- [ ] Codice rivisto per best practices
- [ ] Nessuna regressione su Bug #1 e #2
- [ ] Performance accettabile
- [ ] UX non vedenti preservata

---

## 🚀 DEPLOYMENT

**Quando tutti i task sono completi**:

1. [ ] Squash commits se necessario
2. [ ] Update CHANGELOG.md con v1.4.2.1 notes
3. [ ] Create Pull Request: `refactoring-engine` → `main`
4. [ ] Final testing su branch main
5. [ ] Tag release: `v1.4.2.1`
6. [ ] Update README con note release

---

**Ultimo aggiornamento**: 09/02/2026 01:35 AM CET  
**Prossima milestone**: Bug #3 Implementation  
**ETA**: 1-2 ore sviluppo + 30 min testing
