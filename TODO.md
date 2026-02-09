# ✅ TODO - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Focus**: Bug Fix Release  
**Code Review**: ✅ Completata  

---

## 🐛 BUG #3: Settings Integration in new_game()

**Priorità**: 🔴 CRITICA  
**Status**: 🔧 IN PROGRESS - FASE 1-4 COMPLETATE ✅  
**File**: `src/application/game_engine.py`  

---

### 📝 TASK BREAKDOWN

#### **FASE 1: Engine Initialization** (1/7) ✅ COMPLETATA

**File**: `src/application/game_engine.py`  
**Commit**: [`5091a5b`](https://github.com/Nemex81/solitario-classico-accessibile/commit/5091a5b3b80cdca46d0e86d6738b36f92289b31c)

- [x] **Task 1.1**: Modificare `__init__()` signature ✅
- [x] **Task 1.2**: Salvare settings come attributo ✅
- [x] **Task 1.3**: Inizializzare attributi configurabili con defaults ✅

---

#### **FASE 2: Factory Method Update** (2/7) ✅ GIÀ IMPLEMENTATA

**File**: `src/application/game_engine.py`  
**Commit**: Bug #1 fix + Phase 1

- [x] **Task 2.1**: Modificare `create()` per passare settings ✅
- [x] **Task 2.2**: Verificare che test.py passa settings correttamente ✅

---

#### **FASE 3: Deck Recreation Helper** (3/7) ✅ COMPLETATA

**File**: `src/application/game_engine.py`  
**Commit**: [`31b71f1`](https://github.com/Nemex81/solitario-classico-accessibile/commit/31b71f18327fddd7d27a65abfe31162e3e7b1b6f)

- [x] **Task 3.1**: Implementare metodo `_recreate_deck_and_table()` ✅
  - Crea nuovo deck (French/Neapolitan)
  - Ricrea table con nuovo deck
  - Aggiorna rules (deck-dependent)
  - Aggiorna service e cursor references
  - TTS feedback cambio mazzo

---

#### **FASE 4: Settings Application Helper** (4/7) ✅ COMPLETATA

**File**: `src/application/game_engine.py`  
**Commit**: [`475c50e`](https://github.com/Nemex81/solitario-classico-accessibile/commit/475c50e441257fd420a4d4ae08ba65cd0c2674e3)

- [x] **Task 4.1**: Implementare metodo `_apply_game_settings()` ✅
  - Draw count da difficulty_level (1→1, 2→2, 3→3) ✅
  - Shuffle mode da shuffle_discards ✅
  - Timer warning announcement ✅
  - TTS riassunto settings ✅

---

#### **FASE 5: new_game() Refactoring** (5/7) ⭐ **PROSSIMA - CRITICA**

**File**: `src/application/game_engine.py` > `new_game()`  
**Status**: 🔴 DA IMPLEMENTARE

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
**Status**: ⏳ PENDING

- [ ] **Task 6.1**: Modificare per usare `self.draw_count`
  ```python
  def draw_from_stock(self, count: int = None) -> Tuple[bool, str]:
      """Draw cards from stock to waste.
      
      Args:
          count: Number of cards to draw (None = use self.draw_count)
      """
      # ✅ Se count non specificato, usa settings
      if count is None:
          count = getattr(self, 'draw_count', 1)
      
      success, generic_msg, cards = self.service.draw_cards(count)
      # ... rest of implementation ...
  ```

- [ ] **Task 6.2**: Testare draw count da settings (1, 2, 3)

---

#### **FASE 7: recycle_waste() Update** (7/7)

**File**: `src/application/game_engine.py` > `recycle_waste()`  
**Status**: ⏳ PENDING

- [ ] **Task 7.1**: Modificare per usare `self.shuffle_on_recycle`
  ```python
  def recycle_waste(self, shuffle: bool = None) -> Tuple[bool, str]:
      """Recycle waste pile back to stock.
      
      Args:
          shuffle: None = use settings, True/False = override
      """
      # ✅ Se shuffle non specificato, usa settings
      if shuffle is None:
          shuffle = getattr(self, 'shuffle_on_recycle', False)
      
      success, generic_msg = self.service.recycle_waste(shuffle)
      # ... rest of implementation ...
  ```

- [ ] **Task 7.2**: Testare shuffle mode da settings

---

### 🧪 TESTING COMPLETO

#### **Test Scenario 1: Tutte le Settings Insieme** ⭐ CRITICO
- [ ] **Setup**: Napoletane, Timer 600s, Livello 2, Shuffle ON
- [ ] **Verifiche**:
  - ✅ 40 carte distribuite
  - ✅ TTS annuncia "carte napoletane"
  - ✅ TTS annuncia "Livello 2: 2 carta/e"
  - ✅ TTS annuncia "Scarti si mischiano"
  - ✅ Pesca effettivamente 2 carte
  - ✅ Scarti mischiano

#### **Test Scenario 2: Cambio Deck tra Partite** ⭐ CRITICO
- [ ] Partita 1: French (52 carte)
- [ ] Cambio a Napoletane
- [ ] Partita 2: Neapolitan (40 carte)
- [ ] Cambio a French
- [ ] Partita 3: French (52 carte)

#### **Test Scenario 3: Difficulty Levels** ⚠️ MAPPING CORRETTO
- [ ] Livello 1 → 1 carta
- [ ] Livello 2 → 2 carte (NON 3!)
- [ ] Livello 3 → 3 carte (NON 5!)

#### **Test Scenario 4: Shuffle Mode**
- [ ] shuffle_discards=False → "Rigiro"
- [ ] shuffle_discards=True → "Rimescolo"

#### **Test Scenario 5: Backward Compatibility**
- [ ] Engine senza settings funziona
- [ ] Defaults corretti (French, 1 carta, no shuffle)

---

### 📝 CHECKLIST FINALE

**Codice**:
- [x] FASE 1: Initialization ✅
- [x] FASE 2: Factory Method ✅
- [x] FASE 3: _recreate_deck_and_table ✅
- [x] FASE 4: _apply_game_settings ✅
- [ ] FASE 5: new_game refactoring 🔴 PROSSIMA
- [ ] FASE 6: draw_from_stock update
- [ ] FASE 7: recycle_waste update

**Testing**:
- [ ] Test Scenario 1-5 completi

**Documentazione**:
- [x] BUGS.md aggiornato ✅
- [x] TODO.md aggiornato ✅
- [ ] CHANGELOG.md aggiornato

**Commit**:
- [x] Commit Fase 1 (5091a5b) ✅
- [x] Commit Fase 3 (31b71f1) ✅
- [x] Commit Fase 4 (475c50e) ✅
- [ ] Commit Fase 5 (new_game)
- [ ] Commit Fase 6 (draw)
- [ ] Commit Fase 7 (recycle)

---

## ⚠️ LIMITAZIONI NOTE

### **1. Timer Countdown NON Implementato**
Solo annuncio vocale. Nessuna logica countdown in `GameService`.

### **2. Settings Persistence NON Implementata**
Settings perdute a chiusura app. Nessun file config.

---

**Ultimo aggiornamento**: 09/02/2026 02:10 AM CET  
**Code Review**: ✅ Completata  
**Fase Corrente**: FASE 4 ✅ COMPLETATA → Prossima: FASE 5 🔴  
**Progresso**: 4/7 fasi (57%)  
**ETA Rimanente**: ~1.5 ore sviluppo + 1 ora testing
