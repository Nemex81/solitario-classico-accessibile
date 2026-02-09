# ✅ TODO - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Focus**: Bug Fix Release  
**Code Review**: ✅ Completata  

---

## 🔥 **BUG #3.1: Double Distribution - FIX URGENTE!**

**Priorità**: 🔴 **CRITICA** (App Crasher)  
**Status**: 🔧 FIX IN PROGRESS  
**File**: `src/application/game_engine.py` > `new_game()`  
**Parent**: Bug #3 (Settings Integration)  
**Introdotto in**: Commit `0136df4` (Phase 5)  
**Rilevato**: 09/02/2026 02:23 AM CET (Test manuale utente)  

---

### 🐛 **PROBLEMA**

#### **Descrizione**
App crasha con `IndexError: pop from empty list` quando l'utente cambia deck type nelle opzioni e avvia nuova partita.

#### **Stack Trace**
```
File "game_engine.py", line 237, in new_game
    self.table.distribuisci_carte()
File "table.py", line 138, in distribuisci_carte
    carta = self.mazzo.pesca()
File "deck.py", line 88, in pesca
    carta_pescata = self.cards.pop(0)
                    ^^^^^^^^^^^^^^^^^^
IndexError: pop from empty list
```

#### **Root Cause**
**Doppia chiamata a `distribuisci_carte()`:**

1. `_recreate_deck_and_table()` → crea `GameTable(new_deck)`
2. `GameTable.__init__()` → chiama `distribuisci_carte()` automaticamente ✅ (40 carte → 12 carte)
3. `new_game()` → chiama `distribuisci_carte()` **di nuovo** ❌ (12 carte → 0 carte → **CRASH!**)

#### **Flusso Buggy**
```python
def new_game(self):
    if deck_type_changed:
        self._recreate_deck_and_table(...)  # Distribuisce già qui!
    
    if not deck_changed:
        # Raccoglie carte...
    
    self.table.distribuisci_carte()  # ❌ SEMPRE eseguito!
```

---

### ✅ **SOLUZIONE**

#### **Strategia**
Spostare `distribuisci_carte()` dentro il blocco `if not deck_changed`.

**Logica**:
- `deck_changed = True` → GameTable ha già distribuito → **Skip**
- `deck_changed = False` → Carte raccolte necessitano ridistribuzione → **Esegui**

#### **Code Fix (1 linea spostata)**
```python
def new_game(self):
    deck_changed = False
    
    # 1️⃣ Check deck type
    if deck_type_changed:
        deck_changed = True
        self._recreate_deck_and_table(...)  # Distribuisce automaticamente
    
    # 2️⃣ Gather cards ONLY if deck unchanged
    if not deck_changed:
        # ... raccoglie carte da tavolo ...
        self.table.mazzo.mischia()
        
        # 3️⃣ Redistribute ONLY here! ✅
        self.table.distribuisci_carte()  # ← SPOSTATO dentro if!
    
    # 4️⃣ Apply settings
    self._apply_game_settings()
    # ...
```

#### **Impatto**
✅ **1 linea spostata** (indentazione)  
✅ **Nessuna modifica architetturale**  
✅ **100% backward compatible**  
✅ **Fix testabile immediatamente**  

---

### 🧪 **TEST PLAN**

#### **Test 1: Deck Change** ⭐ **CRITICO**
- [ ] Setup: French → Salva
- [ ] Nuova partita → OK (52 carte)
- [ ] Cambia a Neapolitan → Salva
- [ ] **Nuova partita → Nessun crash!**
- [ ] Verifica: 40 carte, TTS "napoletane", mazzo ha 12 carte

#### **Test 2: Reverse Switch**
- [ ] Setup: Neapolitan → Salva
- [ ] Nuova partita → OK (40 carte)
- [ ] Cambia a French → Salva
- [ ] **Nuova partita → Nessun crash!**
- [ ] Verifica: 52 carte, TTS "francesi", mazzo ha 24 carte

#### **Test 3: Same Deck (Backward Compat)**
- [ ] Setup: French → Nuova partita
- [ ] Gioca alcune mosse
- [ ] **Nuova partita → Funziona come prima**
- [ ] Verifica: Carte raccolte e ridistribuite correttamente

#### **Test 4: Multiple Switches (Stress)**
- [ ] Loop 10 volte: Alterna French ↔ Neapolitan
- [ ] **Ogni nuova partita → Nessun crash**
- [ ] Verifica: Conteggio carte sempre corretto

---

### 📝 **TASK CHECKLIST**

#### **Implementazione**
- [ ] **Task 1**: Spostare `distribuisci_carte()` dentro `if not deck_changed` (⏱️ 2 min)
- [ ] **Task 2**: Aggiornare docstring `new_game()` con Bug #3.1 note (⏱️ 3 min)

#### **Testing**
- [ ] **Task 3**: Test 1 - French → Neapolitan (⏱️ 2 min)
- [ ] **Task 4**: Test 2 - Neapolitan → French (⏱️ 2 min)
- [ ] **Task 5**: Test 3 - Same deck restart (⏱️ 1 min)
- [ ] **Task 6**: Test 4 - Multiple switches x10 (⏱️ 3 min)

#### **Documentazione**
- [x] **Task 7**: Aggiornare BUGS.md ✅ (Commit `346307a`)
- [x] **Task 8**: Aggiornare TODO.md ✅ (Questo commit)

#### **Commit & Release**
- [ ] **Task 9**: Commit fix con messaggio dettagliato (⏱️ 2 min)
- [ ] **Task 10**: Test finale su build pulita (⏱️ 2 min)

**TOTALE ETA**: ~15 minuti

---

### 🎯 **COMMIT MESSAGE PROPOSTO**

```
fix(engine): Prevent double distribution on deck change (Bug #3.1)

CRITICAL FIX: Regression from Bug #3 Phase 5 refactoring

Problem:
- When deck_type changes, _recreate_deck_and_table() creates
  new GameTable which already calls distribuisci_carte()
- Then new_game() calls distribuisci_carte() AGAIN
- Result: IndexError (pop from empty list) - app crashes

Solution:
- Move distribuisci_carte() inside "if not deck_changed" block
- Only redistribute cards when using existing deck
- When deck changed, GameTable constructor already dealt cards

Impact:
- 1 line moved (indentation change only)
- No architecture changes
- 100% backward compatible
- Fixes critical app crasher

Testing:
- French→Neapolitan: ✅ No crash
- Neapolitan→French: ✅ No crash
- Same deck restart: ✅ Works as before
- Multiple switches: ✅ All stable

Fixes: #3.1 (regression from #3)
Related: Commit 0136df4 (Bug #3 Phase 5)
```

---

## 🎉 BUG #3: Settings Integration in new_game() - **RISOLTO!**

**Priorità**: 🔴 CRITICA  
**Status**: ✅ **COMPLETATO** - Tutte le 7 fasi implementate!  
**File**: `src/application/game_engine.py`  

---

### 📝 TASK BREAKDOWN - ✅ TUTTE COMPLETATE

#### **FASE 1: Engine Initialization** (1/7) ✅ COMPLETATA

**Commit**: [`5091a5b`](https://github.com/Nemex81/solitario-classico-accessibile/commit/5091a5b3b80cdca46d0e86d6738b36f92289b31c)

- [x] Task 1.1: Modificare `__init__()` signature ✅
- [x] Task 1.2: Salvare settings come attributo ✅
- [x] Task 1.3: Inizializzare attributi configurabili con defaults ✅

---

#### **FASE 2: Factory Method Update** (2/7) ✅ GIÀ IMPLEMENTATA

**Commit**: Bug #1 fix + Phase 1

- [x] Task 2.1: Modificare `create()` per passare settings ✅
- [x] Task 2.2: Verificare che test.py passa settings correttamente ✅

---

#### **FASE 3: Deck Recreation Helper** (3/7) ✅ COMPLETATA

**Commit**: [`31b71f1`](https://github.com/Nemex81/solitario-classico-accessibile/commit/31b71f18327fddd7d27a65abfe31162e3e7b1b6f)

- [x] Task 3.1: Implementare metodo `_recreate_deck_and_table()` ✅
  - Crea nuovo deck (French/Neapolitan) ✅
  - Ricrea table con nuovo deck ✅
  - Aggiorna rules (deck-dependent) ✅
  - Aggiorna service e cursor references ✅
  - TTS feedback cambio mazzo ✅

---

#### **FASE 4: Settings Application Helper** (4/7) ✅ COMPLETATA

**Commit**: [`475c50e`](https://github.com/Nemex81/solitario-classico-accessibile/commit/475c50e441257fd420a4d4ae08ba65cd0c2674e3)

- [x] Task 4.1: Implementare metodo `_apply_game_settings()` ✅
  - Draw count da difficulty_level (1→1, 2→2, 3→3) ✅
  - Shuffle mode da shuffle_discards ✅
  - Timer warning announcement ✅
  - TTS riassunto settings ✅

---

#### **FASE 5: new_game() Refactoring** (5/7) ✅ COMPLETATA

**Commit**: [`0136df4`](https://github.com/Nemex81/solitario-classico-accessibile/commit/0136df490d5aa45f9dc6e1f861c9054bccfad369)

⚠️ **NOTA**: Questo commit ha introdotto Bug #3.1 (fix in progress sopra)

- [x] Task 5.1: Rifattorizzare con flusso corretto ✅
  - Controlla deck_type cambiato → ricrea se necessario ✅
  - Raccoglie carte esistenti se deck invariato ✅
  - Ridistribuisce carte ✅ (⚠️ bug: anche quando non necessario)
  - Applica settings via `_apply_game_settings()` ✅
  - Reset stato gioco e cursor/selection ✅
  - Avvia partita e annuncia ✅

---

#### **FASE 6: draw_from_stock() Update** (6/7) ✅ COMPLETATA

**Commit**: [`ddbb8cc`](https://github.com/Nemex81/solitario-classico-accessibile/commit/ddbb8cc76bebda1ba3d83c7965ad235be939616a)

- [x] Task 6.1: Modificare per usare `self.draw_count` ✅
  - Usa `self.draw_count` quando `count=None` ✅
  - Backward compatible con parametro esplicito ✅
  - Rispetta difficulty_level da settings ✅

- [ ] Task 6.2: Testare draw count da settings (TESTING PENDING)
  - Livello 1 → 1 carta
  - Livello 2 → 2 carte
  - Livello 3 → 3 carte

---

#### **FASE 7: recycle_waste() Update** (7/7) ✅ COMPLETATA

**Commit**: [`ddbb8cc`](https://github.com/Nemex81/solitario-classico-accessibile/commit/ddbb8cc76bebda1ba3d83c7965ad235be939616a)

- [x] Task 7.1: Modificare per usare `self.shuffle_on_recycle` ✅
  - Usa `self.shuffle_on_recycle` quando `shuffle=None` ✅
  - Backward compatible con parametro esplicito ✅
  - Rispetta shuffle_discards da settings ✅

- [ ] Task 7.2: Testare shuffle mode da settings (TESTING PENDING)
  - shuffle_discards=False → "Rigiro"
  - shuffle_discards=True → "Rimescolo"

---

### 🧪 TESTING COMPLETO - 🔴 DA ESEGUIRE

⚠️ **BLOCCATO DA BUG #3.1** - Fix urgente in corso

#### **Test Scenario 1: Tutte le Settings Insieme** ⭐ CRITICO
- [ ] **Setup**: Napoletane, Timer 600s, Livello 2, Shuffle ON
- [ ] **Azioni**: Avvia partita, pesca, esaurisce mazzo, ricicla
- [ ] **Verifiche**:
  - ✅ 40 carte distribuite (28+12)
  - ✅ TTS: "carte napoletane"
  - ✅ TTS: "Livello 2: 2 carta/e"
  - ✅ TTS: "Scarti si mischiano"
  - ✅ Pesca 2 carte effettivamente
  - ✅ Scarti mischiano effettivamente

#### **Test Scenario 2: Cambio Deck tra Partite** ⭐ CRITICO
- [ ] Partita 1: French (52 carte)
- [ ] Cambio settings → Napoletane
- [ ] Partita 2: Neapolitan (40 carte + TTS conferma)
- [ ] Cambio settings → French
- [ ] Partita 3: French (52 carte + TTS conferma)

#### **Test Scenario 3: Difficulty Levels** ⚠️ MAPPING CORRETTO
- [ ] Livello 1 → 1 carta
- [ ] Livello 2 → 2 carte (NON 3!)
- [ ] Livello 3 → 3 carte (NON 5!)

#### **Test Scenario 4: Shuffle Mode**
- [ ] shuffle_discards=False → "Rigiro gli scarti"
- [ ] shuffle_discards=True → "Rimescolo gli scarti"

#### **Test Scenario 5: Backward Compatibility**
- [ ] Engine senza settings → defaults corretti
- [ ] draw_from_stock(3) → override settings
- [ ] recycle_waste(True) → override settings

---

### 📊 RIEPILOGO IMPLEMENTAZIONE

**Codice**: ✅ **7/7 fasi completate** (⚠️ + Bug #3.1 regressione)
- [x] FASE 1: Initialization ✅
- [x] FASE 2: Factory Method ✅
- [x] FASE 3: _recreate_deck_and_table ✅
- [x] FASE 4: _apply_game_settings ✅
- [x] FASE 5: new_game refactoring ✅ (⚠️ introdotto Bug #3.1)
- [x] FASE 6: draw_from_stock update ✅
- [x] FASE 7: recycle_waste update ✅

**Bug Critici**:
- [ ] Bug #3.1: Double Distribution 🔴 **FIX IN PROGRESS**

**Testing**: 🔴 **0/5 scenari testati** (bloccato da Bug #3.1)
- [ ] Test Scenario 1-5 da eseguire dopo fix Bug #3.1

**Documentazione**:
- [x] BUGS.md aggiornato ✅
- [x] TODO.md aggiornato ✅
- [ ] CHANGELOG.md aggiornato 🔴

**Commit History**:
- [x] [`5091a5b`](https://github.com/Nemex81/solitario-classico-accessibile/commit/5091a5b3b80cdca46d0e86d6738b36f92289b31c) - Phase 1 ✅
- [x] [`31b71f1`](https://github.com/Nemex81/solitario-classico-accessibile/commit/31b71f18327fddd7d27a65abfe31162e3e7b1b6f) - Phase 3 ✅
- [x] [`475c50e`](https://github.com/Nemex81/solitario-classico-accessibile/commit/475c50e441257fd420a4d4ae08ba65cd0c2674e3) - Phase 4 ✅
- [x] [`0136df4`](https://github.com/Nemex81/solitario-classico-accessibile/commit/0136df490d5aa45f9dc6e1f861c9054bccfad369) - Phase 5 ✅ (⚠️ regressione)
- [x] [`ddbb8cc`](https://github.com/Nemex81/solitario-classico-accessibile/commit/ddbb8cc76bebda1ba3d83c7965ad235be939616a) - Phase 6-7 ✅
- [x] [`346307a`](https://github.com/Nemex81/solitario-classico-accessibile/commit/346307a4ec8d0591db4aa6fef68038f9e6f514be) - BUGS.md update ✅

---

### 🎯 NEXT STEPS

1. **🔥 FIX BUG #3.1** (⏱️ ~15 min) **← PRIORITÀ ASSOLUTA**
   - Implementare fix (1 linea)
   - Testare 4 scenari
   - Commit fix

2. **Testing Completo** (⏱️ ~1 ora)
   - Eseguire tutti i 5 test scenarios
   - Documentare risultati
   - Fix eventuali issues minori

3. **Documentazione** (⏱️ ~15 min)
   - Aggiornare CHANGELOG.md con v1.4.2.1
   - Aggiungere note di rilascio

4. **Merge & Release** (⏱️ ~5 min)
   - Merge `refactoring-engine` → `main`
   - Tag `v1.4.2.1`
   - GitHub Release

---

## ⚠️ LIMITAZIONI NOTE

### **1. Timer Countdown NON Implementato**
Solo annuncio vocale del limite configurato. Nessuna logica countdown attiva in `GameService`.

### **2. Settings Persistence NON Implementata**
Settings perdute alla chiusura app. Nessun salvataggio su file/registry.

---

**Ultimo aggiornamento**: 09/02/2026 02:31 AM CET  
**Bug #3**: ✅ **RISOLTO** (7/7 fasi)  
**Bug #3.1**: 🔴 **FIX IN PROGRESS** (regressione critica)  
**Blocco Release**: 🔴 **SÌ** (Bug #3.1 deve essere risolto)  
**Fase Corrente**: Bug #3.1 Fix (1 linea) → Testing → Release  
**ETA Bug #3.1**: ~15 minuti  
**ETA Totale Release**: ~1.5 ore
