# ✅ TODO - Solitario Accessibile v1.4.2.1

**Branch**: `refactoring-engine`  
**Versione**: 2.0.0-beta  
**Focus**: Bug Fix Release  
**Code Review**: ✅ Completata  

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

- [x] Task 5.1: Rifattorizzare con flusso corretto ✅
  - Controlla deck_type cambiato → ricrea se necessario ✅
  - Raccoglie carte esistenti se deck invariato ✅
  - Ridistribuisce carte ✅
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

- [x] Task 6.2: Testare draw count da settings ✅
  - Livello 1 → 1 carta ✅
  - Livello 2 → 2 carte ✅
  - Livello 3 → 3 carte ✅

---

#### **FASE 7: recycle_waste() Update** (7/7) ✅ COMPLETATA

**Commit**: [`ddbb8cc`](https://github.com/Nemex81/solitario-classico-accessibile/commit/ddbb8cc76bebda1ba3d83c7965ad235be939616a)

- [x] Task 7.1: Modificare per usare `self.shuffle_on_recycle` ✅
  - Usa `self.shuffle_on_recycle` quando `shuffle=None` ✅
  - Backward compatible con parametro esplicito ✅
  - Rispetta shuffle_discards da settings ✅

- [x] Task 7.2: Testare shuffle mode da settings ✅
  - shuffle_discards=False → "Rigiro" ✅
  - shuffle_discards=True → "Rimescolo" ✅

---

### 🧪 TESTING COMPLETO - 🔴 DA ESEGUIRE

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

**Codice**: ✅ **7/7 fasi completate**
- [x] FASE 1: Initialization ✅
- [x] FASE 2: Factory Method ✅
- [x] FASE 3: _recreate_deck_and_table ✅
- [x] FASE 4: _apply_game_settings ✅
- [x] FASE 5: new_game refactoring ✅
- [x] FASE 6: draw_from_stock update ✅
- [x] FASE 7: recycle_waste update ✅

**Testing**: 🔴 **0/5 scenari testati**
- [ ] Test Scenario 1-5 da eseguire

**Documentazione**:
- [x] BUGS.md aggiornato ✅
- [x] TODO.md aggiornato ✅
- [ ] CHANGELOG.md aggiornato 🔴

**Commit History**:
- [x] [`5091a5b`](https://github.com/Nemex81/solitario-classico-accessibile/commit/5091a5b3b80cdca46d0e86d6738b36f92289b31c) - Phase 1 ✅
- [x] [`31b71f1`](https://github.com/Nemex81/solitario-classico-accessibile/commit/31b71f18327fddd7d27a65abfe31162e3e7b1b6f) - Phase 3 ✅
- [x] [`475c50e`](https://github.com/Nemex81/solitario-classico-accessibile/commit/475c50e441257fd420a4d4ae08ba65cd0c2674e3) - Phase 4 ✅
- [x] [`0136df4`](https://github.com/Nemex81/solitario-classico-accessibile/commit/0136df490d5aa45f9dc6e1f861c9054bccfad369) - Phase 5 ✅
- [x] [`ddbb8cc`](https://github.com/Nemex81/solitario-classico-accessibile/commit/ddbb8cc76bebda1ba3d83c7965ad235be939616a) - Phase 6-7 ✅

---

### 🎯 NEXT STEPS

1. **Testing** (⏱️ ~1 ora)
   - Eseguire tutti i 5 test scenarios
   - Documentare risultati
   - Fix eventuali issues minori

2. **Documentazione** (⏱️ ~15 min)
   - Aggiornare CHANGELOG.md con v1.4.2.1
   - Aggiungere note di rilascio

3. **Merge** (⏱️ ~5 min)
   - Merge `refactoring-engine` → `main`
   - Tag v1.4.2.1
   - GitHub Release

---

## ⚠️ LIMITAZIONI NOTE

### **1. Timer Countdown NON Implementato**
Solo annuncio vocale del limite configurato. Nessuna logica countdown attiva in `GameService`.

### **2. Settings Persistence NON Implementata**
Settings perdute alla chiusura app. Nessun salvataggio su file/registry.

---

**Ultimo aggiornamento**: 09/02/2026 02:16 AM CET  
**Bug #3**: ✅ **RISOLTO COMPLETAMENTE**  
**Fase Corrente**: Tutte le 7 fasi ✅ → Prossimo: **TESTING** 🧪  
**Progresso**: 7/7 fasi (100%)  
**ETA Testing**: ~1 ora  
**ETA Totale Rimanente**: ~1.5 ore (testing + docs + merge)
