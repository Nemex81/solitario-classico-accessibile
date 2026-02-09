# 🐛 BUG TRACKING - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Data**: Febbraio 2026  

---

## 📊 SOMMARIO BUG

| ID | Titolo | Stato | Priorità | Files Coinvolti | Commits |
|----|--------|-------|----------|-----------------|----------|
| #1 | Deck Type Non Applicato | ✅ FIXED | 🔴 Alta | game_engine.py, test.py, gameplay_controller.py | 3 |
| #2 | Validazione Seme Assi Mancante | ✅ FIXED | 🔴 Alta | pile.py, table.py, solitaire_rules.py | 3+1 hotfix |
| #3 | Settings Non Consultate in new_game() | 🔧 IN PROGRESS | 🔴 CRITICA | game_engine.py, game_service.py | TBD |

**Legenda Stati**:
- 🔧 IN PROGRESS: Implementazione in corso
- ✅ FIXED: Risolto e committato
- 🧪 TESTING: In fase di test
- ✅ VERIFIED: Testato e confermato funzionante

---

## 🐛 BUG #1: Deck Type Non Applicato da Settings

### **Scoperta**
Data: 09/02/2026 01:00 AM CET  
Severità: 🔴 Alta  

### **Descrizione Problema**
Il tipo di mazzo (French vs Neapolitan) selezionato nelle opzioni NON viene applicato quando si crea una nuova partita. L'engine usa sempre il mazzo French di default, ignorando completamente `GameSettings.deck_type`.

### **Comportamento Atteso**
1. Utente apre Opzioni (O)
2. Cambia "Tipo mazzo" a "Napoletane"
3. Salva (S)
4. Nuova partita (N)
5. **Partita usa 40 carte napoletane** ✅

### **Comportamento Reale**
1. Utente apre Opzioni (O)
2. Cambia "Tipo mazzo" a "Napoletane"
3. Salva (S)
4. Nuova partita (N)
5. **Partita usa 52 carte francesi** ❌

### **Root Cause**
Il metodo `GameEngine.create()` non accettava parametro `settings`, quindi creava sempre `FrenchDeck()` hardcoded.

```python
# PRIMA (BUG):
@classmethod
def create(cls, audio_enabled: bool = True, ...):
    deck = FrenchDeck()  # ❌ Sempre French!
    table = GameTable(deck)
    # ...
```

### **Soluzione Implementata**
1. ✅ Aggiunto parametro `settings: Optional[GameSettings] = None` a `GameEngine.create()`
2. ✅ Logica condizionale per deck type:
   ```python
   if settings and settings.deck_type == "neapolitan":
       deck = NeapolitanDeck()
   else:
       deck = FrenchDeck()  # Default
   ```
3. ✅ Passaggio settings da `test.py` all'engine
4. ✅ Passaggio settings a `GamePlayController`

### **Files Modificati**
- `src/application/game_engine.py` (commit `c2dd2ea`)
- `test.py` (commit `036d630`)
- `src/application/gameplay_controller.py` (commit `856e298`)

### **Status**: ✅ FIXED (3 commits)

---

## 🐛 BUG #2: Validazione Seme Assi Mancante

### **Scoperta**
Data: 09/02/2026 01:00 AM CET  
Severità: 🔴 Alta  

### **Descrizione Problema**
Le pile fondazione (semi) accettavano **qualsiasi asso** quando vuote, anche se il seme non corrispondeva. Ad esempio:
- Asso di Cuori accettato su "Pila semi Quadri" ❌
- Asso di Denari accettato su "Pila semi Coppe" ❌

Questo viola le regole del solitario classico, dove ogni fondazione è dedicata a un seme specifico.

### **Comportamento Atteso**
1. Foundation "Pila semi Cuori" accetta SOLO Asso di Cuori
2. Foundation "Pila semi Quadri" accetta SOLO Asso di Quadri
3. Altri assi vengono rifiutati con messaggio errore ✅

### **Comportamento Reale**
1. Foundation "Pila semi Cuori" accetta QUALSIASI asso ❌
2. Nessuna validazione del seme ❌

### **Root Cause**
Le pile fondazione non avevano un attributo `assigned_suit` e la validazione in `SolitaireRules.can_place_on_foundation()` controllava solo:
```python
# PRIMA (BUG):
if target_pile.is_empty():
    return card.get_value == 1  # ❌ Solo valore, non seme!
```

### **Soluzione Implementata**

#### **Parte 1: Modello Pile** (commit `5bfd031`)
✅ Aggiunto attributo `assigned_suit: Optional[str]` a `Pile.__init__()`
```python
class Pile:
    def __init__(self, name: str, pile_type: str, assigned_suit: Optional[str] = None):
        self.assigned_suit = assigned_suit  # NEW
```

#### **Parte 2: Assegnazione Semi** (commit `b7c60b7` + hotfix `79f91a6`)
✅ Foundation piles creati con semi fissi da `deck.SUITES`:
```python
deck_suits = deck.SUITES  # ["cuori", "quadri", "fiori", "picche"]
self.pile_semi = [
    Pile(
        name=f"Pila semi {suit.capitalize()}",  # Display
        pile_type="semi",
        assigned_suit=suit  # Validation (lowercase)
    )
    for suit in deck_suits
]
```

**HOTFIX**: Corretto `deck.SEMI` → `deck.SUITES` (AttributeError)

#### **Parte 3: Validazione Regole** (commit `42618c8`)
✅ Controllo seme in `can_place_on_foundation()`:
```python
if target_pile.is_empty():
    is_ace = card.get_value == 1
    
    # NEW: Validate suit
    if hasattr(target_pile, 'assigned_suit') and target_pile.assigned_suit:
        correct_suit = card.get_suit == target_pile.assigned_suit
        return is_ace and correct_suit  # ✅ Entrambe le condizioni!
    
    return is_ace  # Backward compat
```

### **Files Modificati**
- `src/domain/models/pile.py` (commit `5bfd031`)
- `src/domain/models/table.py` (commit `b7c60b7`, hotfix `79f91a6`)
- `src/domain/rules/solitaire_rules.py` (commit `42618c8`)

### **Status**: ✅ FIXED (3 commits + 1 hotfix)

---

## 🐛 BUG #3: Settings Non Consultate in new_game()

### **Scoperta**
Data: 09/02/2026 01:30 AM CET  
Severità: 🔴 **CRITICA** (blocca tutte le impostazioni!)  
Rilasciato in: Testing v1.4.2.1  

### **Descrizione Problema**
**TUTTE le impostazioni di gioco** vengono ignorate quando si avvia una nuova partita. Il metodo `GameEngine.new_game()` non consulta mai `GameSettings`, causando:

1. ❌ **Deck type** rimane sempre quello iniziale (fix Bug #1 parzialmente inefficace)
2. ❌ **Timer** usa sempre default (anche se utente ha impostato 10 minuti)
3. ❌ **Livello difficoltà** sempre livello 1 (ignora livello 2 o 3)
4. ❌ **Scarti mischiano** usa comportamento default (ignora configurazione)
5. ❌ **Draw count** sempre 1 carta (ignora se utente vuole pescarne 2 o 3)

### **Test Case Fallito**
```
Utente ha impostato:
- Mazzo: Napoletane ✓ (salvato)
- Timer: 10 minuti (600 secondi) ✓ (salvato)
- Livello: 2 ✓ (salvato)
- Scarti: Si mischiano ✓ (salvato)

Nuova partita avviata:
- Mazzo: FRANCESI ❌ (dovrebbe essere Napoletane)
- Timer: NESSUN LIMITE ❌ (dovrebbe avere 10 minuti)
- Livello: 1 ❌ (dovrebbe essere 2 con 2 carte pescate)
- Scarti: SI GIRANO ❌ (dovrebbe mischiarsi)
```

### **Root Cause Analysis**

#### **Problema 1: Deck Immutabile**
Il deck viene creato **una sola volta** in `GameEngine.create()` e **non viene mai ricreato** in `new_game()`.

```python
# GameEngine.create() - chiamato all'avvio app
@classmethod
def create(cls, settings: Optional[GameSettings] = None):
    # Deck creato QUI (una volta sola)
    if settings and settings.deck_type == "neapolitan":
        deck = NeapolitanDeck()
    else:
        deck = FrenchDeck()
    
    table = GameTable(deck)
    # Questo deck NON viene MAI sostituito!
    return cls(table, service, rules, ...)

# GameEngine.new_game() - chiamato ogni nuova partita
def new_game(self):
    self.service.reset_game()
    # ❌ USA SEMPRE LO STESSO DECK creato in create()!
    self.table.mazzo.mischia()  # Stesso deck
    self.table.distribuisci_carte()  # Stesso deck
    # ❌ NON controlla mai se settings.deck_type è cambiato!
```

**Flusso Attuale** (BUG):
```
1. App avvia → GameEngine.create(settings) → deck = FrenchDeck()
2. Utente cambia opzioni → settings.deck_type = "neapolitan"
3. Utente fa Nuova Partita → new_game()
4. new_game() usa ANCORA FrenchDeck ❌ (creato al punto 1)
```

#### **Problema 2: Settings Non Salvate**
`GameEngine.__init__()` **non salva il riferimento a settings**!

```python
def __init__(self, table, service, rules, cursor, selection, screen_reader):
    self.table = table
    self.service = service
    # ...
    # ❌ MANCA: self.settings = settings
```

Quindi anche se settings venisse passato, `new_game()` non potrebbe consultarlo!

#### **Problema 3: Timer Non Configurato**
```python
def new_game(self):
    self.service.reset_game()  # ❌ Resetta start_time = None
    self.service.start_game()  # ❌ Imposta start_time = now (nessun limite)
```

`GameService` **non ha timer_manager separato**! Il timer è solo:
- `start_time: Optional[float]` - timestamp inizio
- `get_elapsed_time()` - calcola tempo trascorso

**NON c'è modo di impostare un limite di tempo!** Questa funzionalità manca completamente.

### **Soluzione Dettagliata**

#### **Modifica 1: Salvare Settings in Engine**
```python
class GameEngine:
    def __init__(self, ..., settings: Optional[GameSettings] = None):
        # ...
        self.settings = settings  # ✅ Salva riferimento
        
        # Inizializza attributi configurabili con defaults
        self.draw_count = 1
        self.shuffle_on_recycle = False
```

#### **Modifica 2: Modificare create() per Passare Settings**
```python
@classmethod
def create(cls, audio_enabled=True, tts_engine="auto", verbose=1,
           settings: Optional[GameSettings] = None):
    # ... crea componenti ...
    return cls(table, service, rules, cursor, selection, 
               screen_reader, settings)  # ✅ Passa settings
```

#### **Modifica 3: Ricrea Deck in new_game() SE NECESSARIO**

**FLUSSO CORRETTO**:
```python
def new_game(self):
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
        
        # Rimetti carte nel deck e mescola
        self.table.mazzo.cards = all_cards
        self.table.mazzo.mischia()
    
    # 3️⃣ Ridistribuisci carte (nuovo deck già mescolato, o vecchio deck raccolto)
    self.table.distribuisci_carte()
    
    # 4️⃣ Applica altre settings (draw count, shuffle mode)
    self._apply_game_settings()
    
    # 5️⃣ Reset stato gioco
    self.service.reset_game()
    self.cursor.pile_idx = 0
    self.cursor.card_idx = 0
    self.cursor.last_quick_pile = None
    self.selection.clear_selection()
    
    # 6️⃣ Avvia partita (timer automatico)
    self.service.start_game()
    
    # 7️⃣ Annuncio TTS
    if self.screen_reader:
        self.screen_reader.tts.speak(
            "Nuova partita iniziata. Usa H per l'aiuto comandi.",
            interrupt=True
        )
```

#### **Modifica 4: Metodo Helper per Ricreazione Deck**
```python
def _recreate_deck_and_table(self, use_neapolitan: bool) -> None:
    """Ricrea deck e table quando l'utente cambia tipo di mazzo.
    
    Args:
        use_neapolitan: True per Neapolitan, False per French
    """
    # Crea nuovo deck
    if use_neapolitan:
        new_deck = NeapolitanDeck()
    else:
        new_deck = FrenchDeck()
    
    new_deck.crea()
    new_deck.mischia()
    
    # Ricrea table con nuovo deck
    self.table = GameTable(new_deck)
    
    # Aggiorna rules (deck-dependent per is_king, etc.)
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

#### **Modifica 5: Applicare Settings di Gioco**
```python
def _apply_game_settings(self) -> None:
    """Applica tutte le impostazioni di gioco da GameSettings.
    
    Configura:
    - Draw count da difficulty_level
    - Shuffle mode da shuffle_discards
    - Timer warning message (max_time_game)
    
    Note:
        Il timer countdown NON è implementato in GameService.
        Per ora annunciamo solo il limite configurato.
    """
    if not self.settings:
        return
    
    # 1️⃣ Draw count da difficulty
    # GameSettings.difficulty_level:
    #   1 = Draw 1 card
    #   2 = Draw 2 cards
    #   3 = Draw 3 cards
    if self.settings.difficulty_level == 1:
        self.draw_count = 1
    elif self.settings.difficulty_level == 2:
        self.draw_count = 2  # ✅ CORRETTO (non 3!)
    elif self.settings.difficulty_level == 3:
        self.draw_count = 3  # ✅ CORRETTO (non 5!)
    else:
        self.draw_count = 1  # Fallback
    
    # 2️⃣ Shuffle mode
    self.shuffle_on_recycle = self.settings.shuffle_discards
    
    # 3️⃣ Timer (solo annuncio, countdown non implementato)
    # GameSettings.max_time_game:
    #   -1 = Timer disabilitato
    #   300-3600 = Secondi (5-60 minuti)
    if self.settings.max_time_game > 0 and self.screen_reader:
        minutes = self.settings.max_time_game // 60
        self.screen_reader.tts.speak(
            f"Limite tempo configurato: {minutes} minuti. "
            f"(Timer countdown non implementato)",
            interrupt=False
        )
    
    # TTS riassunto settings
    if self.screen_reader:
        level_msg = f"Livello {self.settings.difficulty_level}: {self.draw_count} carta/e per pesca."
        shuffle_msg = "Scarti si mischiano." if self.shuffle_on_recycle else "Scarti si girano."
        self.screen_reader.tts.speak(
            f"{level_msg} {shuffle_msg}",
            interrupt=False
        )
```

#### **Modifica 6: Modificare draw_from_stock()**
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
        count = getattr(self, 'draw_count', 1)
    
    success, generic_msg, cards = self.service.draw_cards(count)
    
    # Usa formatter per messaggio dettagliato
    if success and cards:
        message = GameFormatter.format_drawn_cards(cards)
    else:
        message = generic_msg
    
    if self.screen_reader:
        self.screen_reader.tts.speak(message, interrupt=True)
    
    return success, message
```

#### **Modifica 7: Modificare recycle_waste()**
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
    
    # Esegui recycle
    success, generic_msg = self.service.recycle_waste(shuffle)
    
    if not success:
        if self.screen_reader:
            self.screen_reader.tts.speak(generic_msg, interrupt=False)
        return success, generic_msg
    
    # Auto-draw dopo reshuffle
    auto_success, auto_msg, auto_cards = self.service.draw_cards(1)
    
    # Messaggio dettagliato
    shuffle_mode = "shuffle" if shuffle else "reverse"
    message = GameFormatter.format_reshuffle_message(
        shuffle_mode=shuffle_mode,
        auto_drawn_cards=auto_cards if auto_success else None
    )
    
    if self.screen_reader:
        self.screen_reader.tts.speak(message, interrupt=False)
    
    return success, message
```

### **Files da Modificare**
1. `src/application/game_engine.py`
   - Modificare `__init__()` per salvare settings
   - Modificare `create()` per passare settings
   - Rifattorizzare `new_game()` con flusso corretto
   - Aggiungere `_recreate_deck_and_table()`
   - Aggiungere `_apply_game_settings()`
   - Modificare `draw_from_stock()`
   - Modificare `recycle_waste()`

2. `src/domain/services/game_service.py` (FUTURO)
   - Implementare timer countdown con max_time_game
   - Aggiungere check per tempo scaduto

### **Limitazioni Note**
1. **Timer Countdown NON Implementato**: `GameService` non ha logica per controllare tempo scaduto. Per ora solo annuncio vocale del limite.
2. **Persistenza Settings**: Non c'è salvataggio su file. Settings perduti a chiusura app.

### **Checklist Implementazione**
- [ ] Modificare `__init__()` per accettare e salvare settings
- [ ] Modificare `create()` per passare settings a `__init__()`
- [ ] Implementare `_recreate_deck_and_table()`
- [ ] Implementare `_apply_game_settings()`
- [ ] Rifattorizzare `new_game()` con flusso corretto
- [ ] Modificare `draw_from_stock()` per usare `self.draw_count`
- [ ] Modificare `recycle_waste()` per usare `self.shuffle_on_recycle`
- [ ] Test: Cambio deck French → Neapolitan tra partite
- [ ] Test: Livello 2 con 2 carte pescate (non 3!)
- [ ] Test: Scarti mischiano quando configurato
- [ ] Documentare limitazione timer countdown

### **Status**: 🔧 IN PROGRESS (documentazione corretta)

### **Priorità**: 🔴 CRITICA
Questo bug invalida completamente il sistema di opzioni. **Deve essere risolto prima del merge su main.**

---

## 📝 NOTE TECNICHE

### **GameSettings Attributi Reali**
```python
class GameSettings:
    deck_type: str           # "french" o "neapolitan"
    difficulty_level: int    # 1, 2, o 3
    max_time_game: int       # -1=OFF, o 300-3600 (secondi)
    shuffle_discards: bool   # True=shuffle, False=invert
```

### **Mapping Draw Count**
- Livello 1: **1 carta** ✅
- Livello 2: **2 carte** ✅ (non 3!)
- Livello 3: **3 carte** ✅ (non 5!)

### **GameService Timer**
- **NON esiste `timer_manager`**
- Solo `start_time: float` (timestamp)
- **Countdown non implementato**

### **Backward Compatibility**
Tutte le modifiche mantengono backward compatibility:
- `settings=None` usa comportamento default
- Metodi esistenti continuano a funzionare senza settings

### **Testing Requirements**
Per ogni bug fix:
1. ✅ Unit test per regole modificate
2. ✅ Integration test per flusso completo
3. ✅ Manual test con TTS per UX non vedenti

### **Commit Message Format**
```
fix(scope): Brief description

Detailed explanation.

- Change 1
- Change 2

Fixes #BUG-003
```

---

**Ultimo aggiornamento**: 09/02/2026 01:50 AM CET  
**Code Review**: Completata ✅  
**Autore**: Nemex81  
**Branch**: refactoring-engine
