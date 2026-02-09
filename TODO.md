# ✅ TODO - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Focus**: Bug Fix Release  
**Code Review**: ✅ Completata  

---

## 🐛 BUG #3: Settings Integration in new_game()

**Priorità**: 🔴 CRITICA  
**Status**: 🔧 IN PROGRESS - FASE 1 COMPLETATA ✅  
**File**: `src/application/game_engine.py`  

---

### 📝 TASK BREAKDOWN

#### **FASE 1: Engine Initialization** (1/7) ✅ COMPLETATA

**File**: `src/application/game_engine.py`  
**Commit**: [`5091a5b`](https://github.com/Nemex81/solitario-classico-accessibile/commit/5091a5b3b80cdca46d0e86d6738b36f92289b31c)

- [x] **Task 1.1**: Modificare `__init__()` signature ✅
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

- [x] **Task 1.2**: Salvare settings come attributo ✅
  ```python
  self.settings = settings
  ```

- [x] **Task 1.3**: Inizializzare attributi configurabili con defaults ✅
  ```python
  # Attributi modificabili da settings
  self.draw_count = 1  # Default: 1 carta
  self.shuffle_on_recycle = False  # Default: si girano (no shuffle)
  ```

---

#### **FASE 2: Factory Method Update** (2/7) ✅ GIÀ IMPLEMENTATA

**File**: `src/application/game_engine.py`  
**Commit**: Bug #1 fix + Phase 1

- [x] **Task 2.1**: Modificare `create()` per passare settings ✅
  ```python
  @classmethod
  def create(cls, audio_enabled=True, tts_engine="auto", verbose=1, 
             settings: Optional[GameSettings] = None):
      # ... crea componenti ...
      return cls(table, service, rules, cursor, selection, 
                 screen_reader, settings)  # ✅ Passa settings
  ```

- [x] **Task 2.2**: Verificare che test.py passa settings correttamente ✅
  - ✅ Già implementato in Bug #1 fix
  - Verificato: `self.engine = GameEngine.create(..., settings=self.settings)`

---

#### **FASE 3: Deck Recreation Helper** (3/7) ⭐ **NUOVO METODO** - PROSSIMO

**File**: `src/application/game_engine.py`

- [ ] **Task 3.1**: Implementare metodo `_recreate_deck_and_table()`
  ```python
  def _recreate_deck_and_table(self, use_neapolitan: bool) -> None:
      """Ricrea deck e table quando l'utente cambia tipo di mazzo.
      
      Questo metodo viene chiamato SOLO se deck_type è cambiato.
      Crea un nuovo deck (già mescolato), ricrea table, e aggiorna
      tutti i riferimenti in service/cursor.
      
      Args:
          use_neapolitan: True per Neapolitan, False per French
      """
      # 1. Crea nuovo deck
      if use_neapolitan:
          new_deck = NeapolitanDeck()
      else:
          new_deck = FrenchDeck()
      
      new_deck.crea()
      new_deck.mischia()
      
      # 2. Ricrea table con nuovo deck
      self.table = GameTable(new_deck)
      
      # 3. Aggiorna rules (deck-dependent per is_king, validation)
      self.rules = SolitaireRules(new_deck)
      
      # 4. Aggiorna service references
      self.service.table = self.table
      self.service.rules = self.rules
      
      # 5. Aggiorna cursor reference
      self.cursor.table = self.table
      
      # 6. TTS feedback
      if self.screen_reader:
          deck_name = "napoletane" if use_neapolitan else "francesi"
          self.screen_reader.tts.speak(
              f"Tipo di mazzo cambiato: carte {deck_name}.",
              interrupt=True
          )
  ```

---

#### **FASE 4: Settings Application Helper** (4/7) ⭐ **NUOVO METODO**

**File**: `src/application/game_engine.py`

- [ ] **Task 4.1**: Implementare metodo `_apply_game_settings()`
  ```python
  def _apply_game_settings(self) -> None:
      """Applica tutte le impostazioni di gioco da GameSettings.
      
      Configura:
      - Draw count da difficulty_level (1→1, 2→2, 3→3)
      - Shuffle mode da shuffle_discards
      - Annuncio timer (max_time_game)
      
      Note:
          Timer countdown NON implementato in GameService.
          Per ora solo annuncio vocale del limite configurato.
      """
      if not self.settings:
          return
      
      # 1️⃣ Draw count da difficulty
      # ⚠️ IMPORTANTE: Mapping corretto!
      #   Livello 1 = 1 carta
      #   Livello 2 = 2 carte (NON 3!)
      #   Livello 3 = 3 carte (NON 5!)
      if self.settings.difficulty_level == 1:
          self.draw_count = 1
      elif self.settings.difficulty_level == 2:
          self.draw_count = 2  # ✅ CORRETTO
      elif self.settings.difficulty_level == 3:
          self.draw_count = 3  # ✅ CORRETTO
      else:
          self.draw_count = 1  # Fallback per valori invalidi
      
      # 2️⃣ Shuffle mode
      # ⚠️ IMPORTANTE: Attributo corretto è shuffle_discards (non waste_shuffle!)
      self.shuffle_on_recycle = self.settings.shuffle_discards
      
      # 3️⃣ Timer warning (countdown non implementato)
      # max_time_game: -1 = OFF, 300-3600 = secondi (5-60 min)
      if self.settings.max_time_game > 0 and self.screen_reader:
          minutes = self.settings.max_time_game // 60
          self.screen_reader.tts.speak(
              f"Limite tempo configurato: {minutes} minuti. "
              f"Attenzione: Timer countdown non implementato.",
              interrupt=False
          )
      
      # 4️⃣ TTS riassunto settings
      if self.screen_reader:
          level_msg = f"Livello {self.settings.difficulty_level}: {self.draw_count} carta/e per pesca."
          shuffle_msg = "Scarti si mischiano." if self.shuffle_on_recycle else "Scarti si girano."
          self.screen_reader.tts.speak(
              f"{level_msg} {shuffle_msg}",
              interrupt=False
          )
  ```

---

#### **FASE 5: new_game() Refactoring** (5/7) ⭐ **CRITICO**

**File**: `src/application/game_engine.py` > `new_game()`

- [ ] **Task 5.1**: Rifattorizzare con flusso corretto
  ```python
  def new_game(self) -> None:
      """Start a new game con applicazione settings.
      
      Flusso corretto:
      1. Controlla se deck_type cambiato → ricrea deck SE necessario
      2. SE deck NON cambiato → raccogli carte esistenti
      3. Ridistribuisci carte (deck nuovo già mescolato, o vecchio raccolto)
      4. Applica altre settings (draw count, shuffle mode)
      5. Reset stato gioco e cursor/selection
      6. Avvia partita
      """
      deck_changed = False
      
      # 1️⃣ Controlla se deck type è cambiato
      if self.settings:
          current_is_neapolitan = self.table.mazzo.is_neapolitan_deck()
          should_be_neapolitan = (self.settings.deck_type == "neapolitan")
          
          if current_is_neapolitan != should_be_neapolitan:
              deck_changed = True
              self._recreate_deck_and_table(should_be_neapolitan)
      
      # 2️⃣ SE deck NON è cambiato: raccogli carte esistenti
      if not deck_changed:
          # Gather all cards from all piles
          all_cards = []
          for pile in self.table.pile_base:
              all_cards.extend(pile.get_all_cards())
              pile.clear()
          for pile in self.table.pile_semi:
              all_cards.extend(pile.get_all_cards())
              pile.clear()
          if self.table.pile_mazzo:
              all_cards.extend(self.table.pile_mazzo.get_all_cards())
              self.table.pile_mazzo.clear()
          if self.table.pile_scarti:
              all_cards.extend(self.table.pile_scarti.get_all_cards())
              self.table.pile_scarti.clear()
          
          # Put cards back in deck and shuffle
          self.table.mazzo.cards = all_cards
          self.table.mazzo.mischia()
      
      # 3️⃣ Ridistribuisci carte (nuovo deck già mescolato, o vecchio raccolto)
      self.table.distribuisci_carte()
      
      # 4️⃣ Applica altre settings (draw count, shuffle mode, timer)
      self._apply_game_settings()
      
      # 5️⃣ Reset stato gioco
      self.service.reset_game()
      
      # Reset cursor/selection
      self.cursor.pile_idx = 0
      self.cursor.card_idx = 0
      self.cursor.last_quick_pile = None
      self.selection.clear_selection()  # ✅ IMPORTANTE!
      
      # 6️⃣ Avvia partita (timer automatico)
      self.service.start_game()
      
      # 7️⃣ Annuncio TTS
      if self.screen_reader:
          self.screen_reader.tts.speak(
              "Nuova partita iniziata. Usa H per l'aiuto comandi.",
              interrupt=True
          )
  ```

---

#### **FASE 6: draw_from_stock() Update** (6/7)

**File**: `src/application/game_engine.py` > `draw_from_stock()`

- [ ] **Task 6.1**: Modificare per usare `self.draw_count`
  ```python
  def draw_from_stock(self, count: int = None) -> Tuple[bool, str]:
      """Draw cards from stock to waste.
      
      Args:
          count: Number of cards to draw (None = use self.draw_count)
      
      Returns:
          Tuple of (success, message)
      """
      # ✅ Se count non specificato, usa settings
      if count is None:
          count = getattr(self, 'draw_count', 1)  # Default 1
      
      success, generic_msg, cards = self.service.draw_cards(count)
      
      # Use detailed formatter
      if success and cards:
          message = GameFormatter.format_drawn_cards(cards)
      else:
          message = generic_msg
      
      if self.screen_reader:
          self.screen_reader.tts.speak(message, interrupt=True)
      
      return success, message
  ```

- [ ] **Task 6.2**: Testare draw count da settings
  - Livello 1 → 1 carta
  - Livello 2 → 2 carte ⚠️
  - Livello 3 → 3 carte ⚠️

---

#### **FASE 7: recycle_waste() Update** (7/7)

**File**: `src/application/game_engine.py` > `recycle_waste()`

- [ ] **Task 7.1**: Modificare per usare `self.shuffle_on_recycle`
  ```python
  def recycle_waste(self, shuffle: bool = None) -> Tuple[bool, str]:
      """Recycle waste pile back to stock.
      
      Args:
          shuffle: None = use settings, True = force shuffle, False = force invert
      
      Returns:
          Tuple of (success, message)
      """
      # ✅ Se shuffle non specificato, usa settings
      if shuffle is None:
          shuffle = getattr(self, 'shuffle_on_recycle', False)
      
      # Execute recycle
      success, generic_msg = self.service.recycle_waste(shuffle)
      
      if not success:
          if self.screen_reader:
              self.screen_reader.tts.speak(generic_msg, interrupt=False)
          return success, generic_msg
      
      # Auto-draw after reshuffle
      auto_success, auto_msg, auto_cards = self.service.draw_cards(1)
      
      # Format detailed message
      shuffle_mode = "shuffle" if shuffle else "reverse"
      message = GameFormatter.format_reshuffle_message(
          shuffle_mode=shuffle_mode,
          auto_drawn_cards=auto_cards if auto_success else None
      )
      
      if self.screen_reader:
          self.screen_reader.tts.speak(message, interrupt=False)
      
      return success, message
  ```

- [ ] **Task 7.2**: Testare shuffle mode da settings
  - shuffle_discards=False → "Rigiro gli scarti" (reverse)
  - shuffle_discards=True → "Rimescolo gli scarti" (shuffle)

---

### 🧪 TESTING COMPLETO

#### **Test Scenario 1: Tutte le Settings Insieme** ⭐ CRITICO
- [ ] **Setup**:
  - Mazzo: Napoletane
  - Timer: 600 secondi (10 minuti)
  - Livello: 2
  - Scarti: shuffle_discards = True
- [ ] **Azioni**:
  1. Avvia nuova partita (N)
  2. TTS annuncia tutte le impostazioni
  3. Pesca dal mazzo (D/P)
  4. Esaurisce mazzo e ricicla scarti
- [ ] **Verifiche**:
  - ✅ 40 carte distribuite (28 tavolo + 12 mazzo)
  - ✅ TTS dice "Tipo di mazzo cambiato: carte napoletane"
  - ✅ TTS dice "Livello 2: 2 carta/e per pesca" (NON 3!)
  - ✅ TTS dice "Scarti si mischiano"
  - ✅ TTS dice "Limite tempo configurato: 10 minuti" (con warning)
  - ✅ Pesca effettivamente 2 carte alla volta
  - ✅ Scarti effettivamente mischiano (non si girano)

#### **Test Scenario 2: Cambio Deck tra Partite** ⭐ CRITICO
- [ ] **Partita 1**: French (52 carte)
  - Nuova partita
  - Verifica: 52 carte (28+24)
  - Termina partita
- [ ] **Cambio Opzioni**: Napoletane
  - Apri opzioni (O)
  - Toggle mazzo (F1)
  - Salva (S)
- [ ] **Partita 2**: Neapolitan (40 carte)
  - Nuova partita
  - Verifica: 40 carte (28+12)
  - Verifica TTS: "carte napoletane"
  - Termina partita
- [ ] **Cambio Opzioni**: French
  - Toggle mazzo (F1)
  - Salva (S)
- [ ] **Partita 3**: French (52 carte)
  - Nuova partita
  - Verifica: 52 carte (28+24)
  - Verifica TTS: "carte francesi"

#### **Test Scenario 3: Difficulty Levels** ⚠️ MAPPING CORRETTO
- [ ] **Livello 1**: 1 carta
  - Imposta difficulty_level = 1
  - Nuova partita
  - Pesca (D)
  - Verifica: TTS annuncia 1 carta
  - Verifica: 1 carta effettivamente pescata
- [ ] **Livello 2**: 2 carte (NON 3!)
  - Imposta difficulty_level = 2
  - Nuova partita
  - Pesca (D)
  - Verifica: TTS dice "2 carta/e per pesca"
  - Verifica: 2 carte pescate
- [ ] **Livello 3**: 3 carte (NON 5!)
  - Imposta difficulty_level = 3
  - Nuova partita
  - Pesca (D)
  - Verifica: TTS dice "3 carta/e per pesca"
  - Verifica: 3 carte pescate

#### **Test Scenario 4: Shuffle Mode**
- [ ] **Shuffle OFF** (shuffle_discards = False):
  - Imposta shuffle_discards = False
  - Nuova partita
  - TTS: "Scarti si girano"
  - Pesca tutte le carte
  - Ricicla (R)
  - Verifica TTS: "Rigiro gli scarti nel mazzo"
- [ ] **Shuffle ON** (shuffle_discards = True):
  - Imposta shuffle_discards = True
  - Nuova partita
  - TTS: "Scarti si mischiano"
  - Pesca tutte le carte
  - Ricicla (R)
  - Verifica TTS: "Rimescolo gli scarti in modo casuale"

#### **Test Scenario 5: Backward Compatibility**
- [ ] **Engine senza settings**:
  ```python
  engine = GameEngine.create()  # No settings
  engine.new_game()
  ```
- [ ] **Verifiche**:
  - ✅ Nessun crash
  - ✅ Comportamento default: French, 1 carta, scarti girano
  - ✅ `draw_count` = 1
  - ✅ `shuffle_on_recycle` = False

---

### 📝 CHECKLIST FINALE

**Codice**:
- [x] Task 1.1-1.3 completati (Initialization) ✅
- [x] Task 2.1-2.2 completati (Factory Method) ✅
- [ ] Task 3.1 completato (_recreate_deck_and_table)
- [ ] Task 4.1 completato (_apply_game_settings)
- [ ] Task 5.1 completato (new_game refactoring)
- [ ] Task 6.1-6.2 completati (draw_from_stock)
- [ ] Task 7.1-7.2 completati (recycle_waste)
- [ ] Nessun warning o errore
- [ ] Docstrings aggiornati

**Testing**:
- [ ] Test Scenario 1 completo ✅ (All settings)
- [ ] Test Scenario 2 completo ✅ (Deck switch)
- [ ] Test Scenario 3 completo ✅ (Difficulty mapping)
- [ ] Test Scenario 4 completo ✅ (Shuffle mode)
- [ ] Test Scenario 5 completo ✅ (Backward compat)

**Documentazione**:
- [x] BUGS.md aggiornato (code review)
- [x] TODO.md aggiornato (task corretti)
- [ ] CHANGELOG.md aggiornato
- [ ] Docstrings metodi modificati

**Commit**:
- [x] Commit Fase 1 (5091a5b) ✅
- [ ] Commit Fase 3 (_recreate_deck_and_table)
- [ ] Commit Fase 4 (_apply_game_settings)
- [ ] Commit Fase 5 (new_game refactoring)
- [ ] Commit Fase 6 (draw_from_stock)
- [ ] Commit Fase 7 (recycle_waste)
- [ ] Branch push su GitHub

**Review**:
- [x] Code review completata
- [x] Attributi GameSettings corretti ✅
- [ ] Draw count mapping corretto (1, 2, 3)
- [ ] Nessuna regressione Bug #1 e #2
- [ ] UX non vedenti preservata

---

## ⚠️ LIMITAZIONI NOTE

### **1. Timer Countdown NON Implementato**
`GameService` **non ha logica** per:
- Controllare tempo trascorso vs max_time_game
- Terminare partita quando tempo scaduto
- Countdown display/audio

**Soluzione temporanea**: Solo annuncio vocale del limite configurato.

**Implementazione futura** richiederebbe:
```python
# In GameService
class GameService:
    def __init__(self, table, rules, max_time: int = -1):
        self.max_time = max_time  # -1 = OFF
    
    def check_timeout(self) -> bool:
        if self.max_time <= 0:
            return False
        return self.get_elapsed_time() >= self.max_time
```

### **2. Settings Persistence NON Implementata**
Settings **non vengono salvate su file**. Perdute a chiusura app.

**Implementazione futura** richiederebbe:
- File JSON/INI per settings
- Load da file in test.py initialization
- Save da OptionsWindow on exit

---

## 🚀 DEPLOYMENT

**Quando tutti i task sono completi**:

1. [ ] Review finale codice
2. [ ] Tutti i 5 test scenario passati
3. [ ] Update CHANGELOG.md con v1.4.2.1 notes
4. [ ] Squash commits se necessario (6 → 1-2)
5. [ ] Create Pull Request: `refactoring-engine` → `main`
6. [ ] Final testing su branch main
7. [ ] Tag release: `v1.4.2.1`
8. [ ] Update README con release notes

---

**Ultimo aggiornamento**: 09/02/2026 02:00 AM CET  
**Code Review**: ✅ Completata  
**Fase Corrente**: FASE 1 ✅ COMPLETATA → Prossima: FASE 3  
**ETA Rimanente**: ~2 ore sviluppo + 1 ora testing
