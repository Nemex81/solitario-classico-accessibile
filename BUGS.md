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
5. ❌ **Draw count** sempre default (ignora se utente vuole pescarne 3)

### **Test Case Fallito**
```
Utente ha impostato:
- Mazzo: Napoletane ✓ (salvato)
- Timer: 10 minuti ✓ (salvato)
- Livello: 2 ✓ (salvato)
- Scarti: Si mischiano ✓ (salvato)

Nuova partita avviata:
- Mazzo: FRANCESI ❌ (dovrebbe essere Napoletane)
- Timer: DISABILITATO ❌ (dovrebbe essere 10 minuti)
- Livello: 1 ❌ (dovrebbe essere 2)
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

#### **Problema 3: Service Non Usa Settings**
```python
def new_game(self):
    self.service.reset_game()  # ❌ Non riceve settings
    self.service.start_game()  # ❌ Usa timer default
```

`GameService` non ha riferimento a settings, quindi non può:
- Configurare timer
- Configurare livello difficoltà
- Configurare draw count

### **Soluzione Dettagliata**

#### **Modifica 1: Salvare Settings in Engine**
```python
class GameEngine:
    def __init__(self, ..., settings: Optional[GameSettings] = None):
        # ...
        self.settings = settings  # ✅ Salva riferimento
```

#### **Modifica 2: Modificare create() per Passare Settings**
```python
@classmethod
def create(cls, settings: Optional[GameSettings] = None, ...):
    # ... crea deck, table, service ...
    return cls(table, service, rules, cursor, selection, screen_reader, settings)  # ✅ Passa settings
```

#### **Modifica 3: Ricrea Deck in new_game() se Necessario**
```python
def new_game(self):
    # ✅ CONTROLLA se deck type è cambiato
    if self.settings:
        current_is_neapolitan = self.table.mazzo.is_neapolitan_deck()
        should_be_neapolitan = (self.settings.deck_type == "neapolitan")
        
        if current_is_neapolitan != should_be_neapolitan:
            # ✅ RICREA DECK!
            if should_be_neapolitan:
                new_deck = NeapolitanDeck()
            else:
                new_deck = FrenchDeck()
            
            new_deck.crea()
            new_deck.mischia()
            
            # ✅ RICREA TABLE con nuovo deck
            self.table = GameTable(new_deck)
            
            # ✅ AGGIORNA RULES (deck-dependent)
            self.rules = SolitaireRules(new_deck)
            
            # ✅ AGGIORNA SERVICE
            self.service.table = self.table
            self.service.rules = self.rules
            
            # ✅ AGGIORNA CURSOR
            self.cursor.table = self.table
    
    # ... resto del metodo (raccolta carte, ridistribuzione)
```

#### **Modifica 4: Applicare Timer Settings**
```python
def new_game(self):
    # ... (dopo ricreazione deck)
    
    # ✅ Applica impostazioni timer
    if self.settings:
        if self.settings.timer_enabled:
            self.service.timer_manager.set_enabled(True)
            self.service.timer_manager.set_duration(self.settings.timer_duration * 60)
        else:
            self.service.timer_manager.set_enabled(False)
    
    # Avvia partita
    self.service.start_game()
```

#### **Modifica 5: Configurare Altre Settings**
```python
def new_game(self):
    # ... (dopo timer)
    
    if self.settings:
        # ✅ Livello difficoltà (influenza draw count)
        if self.settings.difficulty_level == 1:
            self.draw_count = 1  # Facile: 1 carta
        elif self.settings.difficulty_level == 2:
            self.draw_count = 3  # Medio: 3 carte
        else:
            self.draw_count = 5  # Difficile: 5 carte
        
        # ✅ Scarti mischiano (usato in recycle_waste)
        self.shuffle_on_recycle = self.settings.waste_shuffle
```

#### **Modifica 6: Usare Settings in recycle_waste()**
```python
def recycle_waste(self, shuffle: bool = None) -> Tuple[bool, str]:
    # ✅ Se shuffle non specificato, usa settings
    if shuffle is None and self.settings:
        shuffle = self.settings.waste_shuffle
    
    success, msg = self.service.recycle_waste(shuffle)
    # ...
```

### **Files da Modificare**
1. `src/application/game_engine.py`
   - Salvare `self.settings`
   - Modificare `create()` per passare settings
   - Rifattorizzare `new_game()` con controlli settings
   - Modificare `recycle_waste()` per usare settings

2. `src/domain/services/game_service.py` (opzionale)
   - Passare settings a service per configurazioni avanzate

### **Checklist Implementazione**
- [ ] Modificare `__init__()` per accettare e salvare settings
- [ ] Modificare `create()` per passare settings a `__init__()`
- [ ] Implementare logica ricreazione deck in `new_game()`
- [ ] Applicare timer settings in `new_game()`
- [ ] Applicare difficulty/draw count settings
- [ ] Modificare `recycle_waste()` per waste_shuffle setting
- [ ] Test: Cambio deck French → Neapolitan tra partite
- [ ] Test: Timer 10 minuti applicato
- [ ] Test: Livello 2 con 3 carte pescate
- [ ] Test: Scarti mischiano quando configurato

### **Status**: 🔧 IN PROGRESS

### **Priorità**: 🔴 CRITICA
Questo bug invalida completamente il sistema di opzioni. **Deve essere risolto prima del merge su main.**

---

## 📝 NOTE TECNICHE

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

Fixes #BUG-XXX
```

---

**Ultimo aggiornamento**: 09/02/2026 01:35 AM CET  
**Autore**: Nemex81  
**Branch**: refactoring-engine
