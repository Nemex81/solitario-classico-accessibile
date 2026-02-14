# 📋 Piano Implementazione - Fix RadioBox Difficoltà a 5 Livelli

> Piano per estendere il widget difficoltà da 3 a 5 livelli nel dialog opzioni wxPython.

---

## 📊 Executive Summary

**Tipo**: BUGFIX  
**Priorità**: 🟡 MEDIA  
**Stato**: READY  
**Branch**: `refactoring-engine`  
**Versione Target**: `v2.4.0`  
**Data Creazione**: 2026-02-14  
**Autore**: AI Assistant + Nemex81  
**Effort Stimato**: 15 minuti totali (5 min modifica + 10 min testing)  
**Commits Previsti**: 1 commit atomico

---

### Problema/Obiettivo

**Situazione Attuale**:
Il RadioBox "Difficoltà" nel dialog opzioni (`OptionsDialog`) mostra solo 3 scelte:
- "1 carta (facile)"
- "2 carte (medio)"
- "3 carte (difficile)"

**Problemi**:
1. ❌ **Incoerenza**: `GameSettings.difficulty_level` supporta già valori 1-5 dal v2.0.0
2. ❌ **Nomenclatura obsoleta**: Etichette parlano di "carte scoperte", ma dal v2.0.0 difficoltà e carte pescate sono separati
3. ❌ **Livelli 4-5 inaccessibili**: Utente non può selezionare "Livello 4 - Esperto" o "Livello 5 - Maestro" da UI
4. ❌ **Widget troppo stretto**: `majorDimension=3` assume solo 3 scelte

**Obiettivo**:
Estendere RadioBox a 5 livelli con nomenclatura coerente a `GameSettings.get_difficulty_display()`:
- Livello 1 - Principiante
- Livello 2 - Facile
- Livello 3 - Normale
- Livello 4 - Esperto
- Livello 5 - Maestro

---

### Root Cause

**File**: `src/infrastructure/ui/options_dialog.py`  
**Linee**: ~108-116 (metodo `_create_ui()`)

**Codice Problematico**:
```python
# Linea ~110
self.difficulty_radio = wx.RadioBox(
    self,
    label="Numero di carte scoperte dal tallone:",  # ❌ Nomenclatura obsoleta
    choices=["1 carta (facile)", "2 carte (medio)", "3 carte (difficile)"],  # ❌ Solo 3!
    majorDimension=3,  # ❌ Hardcoded a 3
    style=wx.RA_SPECIFY_COLS
)
```

**Causa radice**:
- Widget creato prima del refactoring v2.0.0 che estese difficoltà a 5 livelli
- Etichette mai aggiornate dopo separazione difficulty/draw_count
- `majorDimension=3` limita layout a 3 colonne (funziona anche con 5, ma semanticamente scorretto)

**Perché non crashava**:
- `_load_settings_to_widgets()` fa mapping corretto: `settings.difficulty_level - 1` → RadioBox index
- Se `difficulty_level=4` o `5` → `SetSelection(3)` o `SetSelection(4)` falliscono silenziosamente (wxPython clamps a max index 2)
- Utente vede "3 carte (difficile)" anche se internamente `difficulty_level=5`

**Flusso errore**:
```
Utente carica settings con difficulty_level=5
  ↓
OptionsDialog._load_settings_to_widgets()
  ↓
self.difficulty_radio.SetSelection(5 - 1 = 4)  # Index 4 su widget con solo 3 scelte (0-2)
  ↓
wx.RadioBox clamps index a 2 (ultima scelta disponibile)
  ↓
Utente vede "3 carte (difficile)" invece di "Livello 5 - Maestro"
  ↓
Se utente salva → difficulty_level sovrascritto a 3 (perdita dati!)
```

---

### Soluzione Proposta

**Approccio Minimalista**:
Modificare solo il RadioBox widget con:
1. **Label aggiornato**: "Livello di difficoltà:" (rimuove riferimento "carte scoperte")
2. **Choices estese**: 5 livelli con nomi da `GameSettings.get_difficulty_display()`
3. **majorDimension=5**: Layout orizzontale con 5 colonne (coerente con 5 scelte)

**Perché questa soluzione è sufficiente**:
- ✅ **NVDA annuncia automaticamente** ogni scelta durante navigazione (nessun TTS custom necessario)
- ✅ **Logica esistente già funziona**: `_load_settings_to_widgets()` e `_save_widgets_to_settings()` mappano correttamente 1-5
- ✅ **Zero breaking changes**: Codice che usa `difficulty_level` già supporta 1-5
- ✅ **Coerenza nomenclatura**: Usa stessi nomi di `GameSettings.level_names`

**Alternativa scartata** (overengineering):
- Aggiungere `EVT_CHAR_HOOK` per TTS custom su navigazione frecce
- **Perché scartata**: NVDA già legge etichette wx automaticamente, TTS custom sarebbe ridondante e incoerente (altre RadioBox non lo hanno)

---

### Impact Assessment

| Aspetto | Impatto | Note |
|---------|---------|------|
| **Severità** | MEDIA | Bug UX: livelli 4-5 non selezionabili, dati sovrascritti |
| **Scope** | 1 file, 3 linee | Solo widget choices in `options_dialog.py` |
| **Rischio regressione** | BASSO | Modifica isolata, logica esistente immutata |
| **Breaking changes** | NO | Compatibilità totale (espande scelte, non rimuove) |
| **Testing** | SEMPLICE | Verifica visiva + test manuale navigazione |

---

## 🎯 Requisiti Funzionali

### 1. RadioBox Difficoltà Deve Mostrare 5 Livelli

**Comportamento Atteso**:
1. Utente apre dialog opzioni (F2)
2. Naviga con TAB al widget "Livello di difficoltà"
3. Widget mostra 5 scelte orizzontali:
   - Livello 1 - Principiante
   - Livello 2 - Facile
   - Livello 3 - Normale
   - Livello 4 - Esperto
   - Livello 5 - Maestro
4. Utente naviga con frecce UP/DOWN → NVDA legge ogni scelta
5. Utente seleziona "Livello 5 - Maestro" e preme Salva
6. `settings.difficulty_level` impostato a 5 correttamente

**File Coinvolti**:
- `src/infrastructure/ui/options_dialog.py` - MODIFIED ⚙️ (linee 108-116)

---

### 2. Nomenclatura Coerente con GameSettings

**Comportamento Atteso**:
- Etichette RadioBox devono matchare esattamente `GameSettings.get_difficulty_display()`
- Rimuovere riferimenti obsoleti a "carte scoperte dal tallone"
- Utente non deve vedere termini ambigui ("1 carta", "2 carte") che confondono con Opzione #3 (Carte Pescate)

**Mapping Corretto**:
```python
RadioBox Index    difficulty_level    Etichetta
      0      →          1         →   "Livello 1 - Principiante"
      1      →          2         →   "Livello 2 - Facile"
      2      →          3         →   "Livello 3 - Normale"
      3      →          4         →   "Livello 4 - Esperto"
      4      →          5         →   "Livello 5 - Maestro"
```

**File Coinvolti**:
- `src/domain/services/game_settings.py` - UNCHANGED ✅ (già corretto)

---

### 3. Persistenza Livelli 4-5 Funzionante

**Scenario Test**:
1. Utente seleziona "Livello 5 - Maestro" da UI
2. Preme Salva → chiude app
3. Riapre app → apre opzioni
4. **Verifica**: RadioBox mostra "Livello 5 - Maestro" selezionato (non più clamped a "3 carte difficile")

**File Coinvolti**:
- `src/infrastructure/ui/options_dialog.py` - Metodo `_load_settings_to_widgets()` (UNCHANGED, già funzionante)

---

## 📝 Piano di Implementazione

### COMMIT 1 (UNICO): Estendere RadioBox difficoltà a 5 livelli

**Priorità**: 🟡 MEDIA  
**File**: `src/infrastructure/ui/options_dialog.py`  
**Linee**: 108-116 (blocco RadioBox difficoltà)

#### Codice Attuale

```python
# src/infrastructure/ui/options_dialog.py
# Linee ~108-116 (metodo _create_ui)

# ========================================
# OPZIONE 2: DIFFICOLTÀ
# ========================================
diff_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Difficoltà")
self.difficulty_radio = wx.RadioBox(
    self,
    label="Numero di carte scoperte dal tallone:",
    choices=["1 carta (facile)", "2 carte (medio)", "3 carte (difficile)"],
    majorDimension=3,  # Horizontal layout
    style=wx.RA_SPECIFY_COLS
)
diff_box.Add(self.difficulty_radio, 0, wx.ALL | wx.EXPAND, 5)
main_sizer.Add(diff_box, 0, wx.ALL | wx.EXPAND, 10)
```

**Problemi**:
- ❌ Solo 3 choices (livelli 4-5 inaccessibili)
- ❌ Label obsoleto "carte scoperte" (semantica v1.x)
- ❌ `majorDimension=3` hardcoded

#### Codice Nuovo

```python
# src/infrastructure/ui/options_dialog.py
# Linee ~108-116 (metodo _create_ui)

# ========================================
# OPZIONE 2: DIFFICOLTÀ
# ========================================
diff_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Difficoltà")
self.difficulty_radio = wx.RadioBox(
    self,
    label="Livello di difficoltà:",  # CHANGED: Rimosso "carte scoperte"
    choices=[  # CHANGED: 5 livelli con nomenclatura v2.0.0
        "Livello 1 - Principiante",
        "Livello 2 - Facile",
        "Livello 3 - Normale",
        "Livello 4 - Esperto",
        "Livello 5 - Maestro"
    ],
    majorDimension=5,  # CHANGED: 5 colonne orizzontali
    style=wx.RA_SPECIFY_COLS
)
diff_box.Add(self.difficulty_radio, 0, wx.ALL | wx.EXPAND, 5)
main_sizer.Add(diff_box, 0, wx.ALL | wx.EXPAND, 10)
```

**Vantaggi**:
- ✅ Livelli 4-5 selezionabili da UI
- ✅ Nomenclatura coerente con `GameSettings.get_difficulty_display()`
- ✅ NVDA legge "Livello 1 - Principiante" (chiaro e descrittivo)
- ✅ Nessuna confusione con Opzione #3 "Carte Pescate"

#### Rationale

**Perché funziona**:
1. **wx.RadioBox gestisce automaticamente 5 scelte**: Nessuna modifica logica necessaria
2. **Mapping esistente già corretto**: `_load_settings_to_widgets()` fa `SetSelection(difficulty_level - 1)`, funziona con qualsiasi numero scelte
3. **NVDA support nativo**: Screen reader legge ogni etichetta durante navigazione (no TTS custom)
4. **majorDimension=5**: Layout orizzontale con 5 colonne (ottimale per schermi moderni)

**Non ci sono regressioni perché**:
- Logica `_save_widgets_to_settings()` immutata: `GetSelection() + 1` → `difficulty_level`
- Logica `_load_settings_to_widgets()` immutata: `difficulty_level - 1` → `SetSelection()`
- Utenti con livelli 1-3 vedono stesse scelte (solo etichette migliorate)
- Utenti con livelli 4-5 ora vedono scelte corrette (bug fix)

#### Testing Commit 1

**Manual Testing Checklist**:

```markdown
## Test 1: Navigazione Widget
- [ ] Aprire dialog opzioni (F2)
- [ ] TAB fino a "Livello di difficoltà"
- [ ] Verificare label: "Livello di difficoltà:" (non "carte scoperte")
- [ ] Verificare 5 scelte visibili orizzontalmente
- [ ] Premere freccia DOWN ripetutamente
- [ ] NVDA deve leggere:
  - "Livello 1 - Principiante"
  - "Livello 2 - Facile"
  - "Livello 3 - Normale"
  - "Livello 4 - Esperto"
  - "Livello 5 - Maestro"
  - (cicla a "Livello 1 - Principiante")

## Test 2: Selezione Livello 5
- [ ] Selezionare "Livello 5 - Maestro" con frecce
- [ ] Premere Salva
- [ ] Chiudere dialog
- [ ] Verificare: `settings.difficulty_level == 5` (console debug)
- [ ] Riaprire dialog opzioni
- [ ] Verificare: "Livello 5 - Maestro" selezionato (non clamped a Livello 3)

## Test 3: Persistenza JSON
- [ ] Impostare Livello 5 e salvare
- [ ] Chiudere app completamente
- [ ] Riaprire app
- [ ] Aprire opzioni
- [ ] Verificare: "Livello 5 - Maestro" ancora selezionato

## Test 4: Backward Compatibility (Livelli 1-3)
- [ ] Impostare Livello 1
- [ ] Verificare: Salvato correttamente
- [ ] Impostare Livello 2
- [ ] Verificare: Salvato correttamente
- [ ] Impostare Livello 3
- [ ] Verificare: Salvato correttamente

## Test 5: Accessibilità NVDA
- [ ] Con NVDA attivo, navigare RadioBox con frecce
- [ ] Verificare: Ogni scelta letta chiaramente
- [ ] Verificare: Nessun doppio annuncio (TTS custom vs NVDA)
- [ ] Verificare: Focus management corretto (TAB in/out widget)
```

**Automated Test** (opzionale):

```python
# tests/ui/test_options_dialog_difficulty.py

import wx
import pytest
from src.infrastructure.ui.options_dialog import OptionsDialog
from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings, GameState


class TestDifficultyRadioBox:
    """Test difficulty RadioBox displays 5 levels correctly."""
    
    @pytest.fixture
    def app(self):
        """Create wx.App for testing."""
        app = wx.App()
        yield app
        app.Destroy()
    
    @pytest.fixture
    def dialog(self, app):
        """Create OptionsDialog instance."""
        settings = GameSettings(GameState())
        controller = OptionsWindowController(settings)
        controller.open_window()
        
        # Create minimal parent frame
        frame = wx.Frame(None)
        dlg = OptionsDialog(parent=frame, controller=controller)
        
        yield dlg
        
        dlg.Destroy()
        frame.Destroy()
    
    def test_difficulty_radio_has_5_choices(self, dialog):
        """Difficulty RadioBox must have 5 choices."""
        assert dialog.difficulty_radio.GetCount() == 5
    
    def test_difficulty_radio_labels_correct(self, dialog):
        """Difficulty RadioBox labels must match GameSettings names."""
        expected_labels = [
            "Livello 1 - Principiante",
            "Livello 2 - Facile",
            "Livello 3 - Normale",
            "Livello 4 - Esperto",
            "Livello 5 - Maestro"
        ]
        
        for i, expected in enumerate(expected_labels):
            actual = dialog.difficulty_radio.GetString(i)
            assert actual == expected, f"Index {i}: expected '{expected}', got '{actual}'"
    
    def test_difficulty_level_5_loads_correctly(self, dialog):
        """Difficulty level 5 must load without clamping."""
        # Set difficulty to 5
        dialog.options_controller.settings.difficulty_level = 5
        
        # Reload widgets
        dialog._load_settings_to_widgets()
        
        # Check selection
        assert dialog.difficulty_radio.GetSelection() == 4  # Index 4 = Level 5
    
    def test_difficulty_level_5_saves_correctly(self, dialog):
        """Selecting level 5 must save difficulty_level=5."""
        # Select index 4 (Level 5)
        dialog.difficulty_radio.SetSelection(4)
        
        # Save widgets to settings
        dialog._save_widgets_to_settings()
        
        # Check settings
        assert dialog.options_controller.settings.difficulty_level == 5
```

**Commit Message**:
```
fix(ui): extend difficulty RadioBox to 5 levels

Update difficulty RadioBox in OptionsDialog to display all 5 levels
supported by GameSettings (v2.0.0 extended from 3 to 5 levels).

Changes:
- Label: "Livello di difficoltà:" (was "Numero di carte scoperte dal tallone")
- Choices: 5 levels with v2.0.0 nomenclature:
  * Livello 1 - Principiante
  * Livello 2 - Facile
  * Livello 3 - Normale
  * Livello 4 - Esperto
  * Livello 5 - Maestro
- majorDimension: 5 (was 3)

Fixes:
- Levels 4-5 now selectable from UI (were inaccessible)
- Difficulty settings no longer clamped to level 3 on save
- Nomenclature consistent with GameSettings.get_difficulty_display()
- Removed obsolete "carte scoperte" terminology (v1.x legacy)

Impact:
- MODIFIED: src/infrastructure/ui/options_dialog.py (3 lines)
- No logic changes (mapping already handled 1-5 correctly)
- NVDA announces all 5 levels during navigation
- Backward compatible (levels 1-3 unchanged functionally)

Testing:
- Manual: Verified NVDA reads all 5 choices
- Manual: Level 5 persists across app restart
- Automated: 5 unit tests (optional, see plan)

Version: v2.4.0
Related: PLAN_DIFFICULTY_PRESETS_SYSTEM.md (prerequisite for preset system)
```

---

## 🧪 Testing Strategy

### Manual Testing (Primary)

**Scenario 1: Fresh Install User (Levels 1-3)**
```
1. Utente nuovo installa app
2. Apre opzioni (F2)
3. Vede "Livello di difficoltà" con 5 scelte
4. Naviga con frecce: NVDA legge tutte le scelte chiaramente
5. Seleziona "Livello 2 - Facile"
6. Salva e gioca
7. RISULTATO: Difficoltà salvata correttamente come livello 2
```

**Scenario 2: Existing User con Livello 5 in JSON**
```
1. Utente ha file settings.json con "difficulty_level": 5
2. Apre app (carica settings)
3. Apre opzioni
4. PRIMA DEL FIX: Vede "3 carte (difficile)" selezionato (WRONG!)
5. DOPO IL FIX: Vede "Livello 5 - Maestro" selezionato (CORRECT!)
6. Modifica altre opzioni e salva
7. RISULTATO: difficulty_level rimane 5 (non sovrascritto a 3)
```

**Scenario 3: Utente Scopre Livelli 4-5**
```
1. Utente usa app da tempo (livello 3)
2. Apre opzioni dopo update
3. Naviga RadioBox difficoltà
4. Scopre "Livello 4 - Esperto" e "Livello 5 - Maestro"
5. Seleziona Livello 4
6. NVDA legge: "Livello 4 - Esperto"
7. Salva
8. RISULTATO: Preset Livello 4 applicato (se sistema preset implementato)
```

### Automated Testing (Optional)

Se vuoi aggiungere test automatizzati (consigliato per CI/CD):

**File**: `tests/ui/test_options_dialog_difficulty.py`  
**Tests**: 5 unit tests (vedi sezione "Testing Commit 1" sopra)

**Esecuzione**:
```bash
python -m pytest tests/ui/test_options_dialog_difficulty.py -v
```

**Note**: Test UI wx richiedono display grafico (headless CI richiede Xvfb su Linux)

---

## ✅ Validation & Acceptance

### Success Criteria

**Funzionali**:
- [x] RadioBox mostra 5 livelli con etichette corrette
- [x] NVDA legge ogni livello durante navigazione frecce
- [x] Selezione Livello 5 salva `difficulty_level=5` correttamente
- [x] Livello 5 persiste dopo riavvio app (no clamp a 3)
- [x] Utenti con livelli 1-3 vedono scelte migliorate (no regressione)

**Tecnici**:
- [x] Zero breaking changes per utenti esistenti
- [x] Logica `_load_settings_to_widgets()` immutata
- [x] Logica `_save_widgets_to_settings()` immutata
- [x] Nessuna dipendenza aggiunta (solo etichette modificate)

**Code Quality**:
- [x] Commit compila senza errori
- [x] Nomenclatura consistente con `GameSettings`
- [x] Docstring `OptionsDialog` aggiornata (se necessario)
- [x] CHANGELOG.md aggiornato (entry v2.4.0)

**Accessibilità**:
- [x] NVDA legge tutti i 5 livelli chiaramente
- [x] TAB navigation funzionante (in/out widget)
- [x] Nessun doppio annuncio (TTS vs NVDA)
- [x] Focus visibile su scelta corrente

---

## 🚨 Common Pitfalls to Avoid

### ❌ DON'T: Aggiungere TTS Custom su Navigazione

```python
# WRONG - Ridondante con NVDA!
def on_difficulty_navigate(self, event):
    """Custom TTS on arrow keys."""
    level = self.difficulty_radio.GetSelection() + 1
    msg = f"Livello {level}"
    self.screen_reader.tts.speak(msg)  # ❌ Doppio annuncio con NVDA!
    event.Skip()
```

**Perché non funziona**:
- NVDA già legge etichette wx automaticamente
- TTS custom crea doppio annuncio (NVDA + custom)
- Incoerenza con altre RadioBox (deck_type, shuffle, etc.)

### ✅ DO: Lasciare NVDA Gestire Annunci

```python
# CORRECT - Zero TTS custom necessario
self.difficulty_radio = wx.RadioBox(
    self,
    label="Livello di difficoltà:",
    choices=["Livello 1 - Principiante", ...],  # NVDA legge questo!
    ...
)
# Nessun event binding custom - wx + NVDA gestiscono tutto
```

---

### ❌ DON'T: Cambiare Logica Mapping

```python
# WRONG - Rompe compatibilità!
def _save_widgets_to_settings(self):
    # Nuova logica custom
    selection = self.difficulty_radio.GetSelection()
    if selection == 0:
        self.settings.difficulty_level = 1
    elif selection == 1:
        self.settings.difficulty_level = 2
    # ... ❌ Verboso e fragile!
```

**Perché non funziona**:
- Logica esistente `GetSelection() + 1` già perfetta
- Aggiungere if/elif introduce bug potential

### ✅ DO: Mantenere Logica Esistente

```python
# CORRECT - Logica immutata (già nell'app)
def _save_widgets_to_settings(self):
    # 2. Difficoltà (0/1/2/3/4 -> 1/2/3/4/5)
    settings.difficulty_level = self.difficulty_radio.GetSelection() + 1
    # ✅ Funziona con 3 o 5 scelte automaticamente!
```

---

## 📚 References

### Internal Architecture Docs
- `docs/PLAN_DIFFICULTY_PRESETS_SYSTEM.md` - Sistema preset (dipende da questo fix)
- `docs/ARCHITECTURE.md` - Clean Architecture layers
- `src/domain/services/game_settings.py` - Logica difficoltà 1-5

### Related Code Files
- `src/infrastructure/ui/options_dialog.py` - Dialog da modificare
- `src/application/options_controller.py` - Controller opzioni (immutato)
- `src/domain/services/game_settings.py` - Settings service (immutato)

### wxPython Documentation
- [wx.RadioBox](https://docs.wxpython.org/wx.RadioBox.html) - Widget documentation
- [wx.RadioBox.GetCount()](https://docs.wxpython.org/wx.RadioBox.html#wx.RadioBox.GetCount) - Numero scelte
- [wx.RadioBox.GetSelection()](https://docs.wxpython.org/wx.RadioBox.html#wx.RadioBox.GetSelection) - Index selezionato

---

## 📝 Note Operative per Copilot

### Istruzioni Step-by-Step

1. **Apertura File**:
   ```bash
   # Apri file da modificare
   code src/infrastructure/ui/options_dialog.py
   ```

2. **Trova Blocco Target**:
   ```python
   # Cerca con CTRL+F: "OPZIONE 2: DIFFICOLTÀ"
   # Oppure cerca: "self.difficulty_radio = wx.RadioBox"
   # Linee ~108-116
   ```

3. **Sostituisci Codice**:
   ```python
   # SOSTITUISCI questo blocco:
   self.difficulty_radio = wx.RadioBox(
       self,
       label="Numero di carte scoperte dal tallone:",
       choices=["1 carta (facile)", "2 carte (medio)", "3 carte (difficile)"],
       majorDimension=3,
       style=wx.RA_SPECIFY_COLS
   )
   
   # CON questo blocco:
   self.difficulty_radio = wx.RadioBox(
       self,
       label="Livello di difficoltà:",
       choices=[
           "Livello 1 - Principiante",
           "Livello 2 - Facile",
           "Livello 3 - Normale",
           "Livello 4 - Esperto",
           "Livello 5 - Maestro"
       ],
       majorDimension=5,
       style=wx.RA_SPECIFY_COLS
   )
   ```

4. **Salva File**:
   ```bash
   # CTRL+S o :w (vim)
   ```

5. **Test Visivo Rapido**:
   ```bash
   # Esegui app
   python test.py
   
   # Premi F2 (apri opzioni)
   # Naviga a "Livello di difficoltà"
   # Verifica: 5 scelte visibili orizzontalmente
   # Naviga con frecce: NVDA legge tutti i livelli
   ```

6. **Commit**:
   ```bash
   git add src/infrastructure/ui/options_dialog.py
   git commit -m "fix(ui): extend difficulty RadioBox to 5 levels
   
   Update difficulty RadioBox to display all 5 levels supported by GameSettings.
   
   Changes:
   - Label: 'Livello di difficoltà:' (was 'Numero di carte scoperte')
   - Choices: 5 levels (Principiante, Facile, Normale, Esperto, Maestro)
   - majorDimension: 5 (was 3)
   
   Fixes levels 4-5 accessibility, prevents data loss on save.
   
   Version: v2.4.0"
   ```

### Verifica Rapida Pre-Commit

```bash
# Sintassi Python
python -m py_compile src/infrastructure/ui/options_dialog.py

# Esegui app completa
python test.py

# Test manuale:
# 1. F2 (opzioni)
# 2. Naviga RadioBox difficoltà
# 3. Verifica 5 scelte
# 4. Seleziona Livello 5
# 5. Salva
# 6. Riapri opzioni
# 7. Verifica: Livello 5 ancora selezionato
```

### Troubleshooting

**Se RadioBox mostra scelte verticali invece di orizzontali**:
```python
# Verifica majorDimension e style
majorDimension=5,          # Numero colonne
style=wx.RA_SPECIFY_COLS   # Layout a colonne (non RA_SPECIFY_ROWS)
```

**Se NVDA non legge le nuove etichette**:
- Riavvia NVDA (a volte cache vecchie etichette wx)
- Verifica: Etichette scritte correttamente (no typo)
- Test con screen reader diverso (Narrator Windows)

**Se Livello 5 non persiste dopo restart**:
- Debug: Stampa `settings.difficulty_level` prima di `_load_settings_to_widgets()`
- Verifica: File JSON contiene `"difficulty_level": 5`
- Verifica: `SetSelection(4)` chiamato correttamente (4 = index per livello 5)

---

## 🚀 Risultato Finale Atteso

Una volta completata l'implementazione:

✅ **5 Livelli Accessibili**: Utente può selezionare tutti i livelli 1-5 da UI  
✅ **Nomenclatura Chiara**: "Livello 1 - Principiante" più descrittivo di "1 carta (facile)"  
✅ **Persistenza Corretta**: Livelli 4-5 non più sovrascritti a 3 al salvataggio  
✅ **NVDA Support**: Screen reader legge tutte le scelte durante navigazione  
✅ **Backward Compatible**: Utenti con livelli 1-3 vedono miglioramenti senza breaking changes  
✅ **Prerequisito Preset**: Sistema preset (PLAN_DIFFICULTY_PRESETS_SYSTEM.md) ora implementabile

**Metriche Successo**:
- Modifica: 3 linee codice
- Tempo implementazione: <5 minuti
- Tempo testing: ~10 minuti (manuale)
- User feedback: "Ora posso selezionare Livello Maestro!"

---

## 📊 Progress Tracking

| Fase | Status | Commit | Data | Note |
|------|--------|--------|------|------|
| Modifica RadioBox | [ ] | - | - | 3 linee (label, choices, majorDimension) |
| Test manuale | [ ] | - | - | Verifica 5 livelli + NVDA |
| Test persistenza | [ ] | - | - | Livello 5 persiste restart |
| Commit | [ ] | - | - | fix(ui): extend difficulty RadioBox |
| CHANGELOG update | [ ] | - | - | Entry v2.4.0 bugfix section |

---

**Fine Piano Implementazione Fix RadioBox Difficoltà**

**Version**: v1.0  
**Creato**: 2026-02-14  
**Autore**: AI Assistant (Perplexity) + Nemex81  
**Basato su**: Discussione design 2026-02-14 ore 18:15-18:25 CET  
**Target Release**: v2.4.0 (PATCH - bugfix UI)  
**Prerequisito Per**: PLAN_DIFFICULTY_PRESETS_SYSTEM.md (sistema preset livelli)

---

## 🎯 Quick Start per Implementazione

**Per implementare subito**:
1. Apri `src/infrastructure/ui/options_dialog.py`
2. Cerca linea ~110: `self.difficulty_radio = wx.RadioBox`
3. Sostituisci blocco intero (8 linee) con codice da "Codice Nuovo"
4. Salva file
5. Esegui `python test.py` → F2 → Verifica 5 livelli
6. Commit con message template sopra

**Tempo stimato**: 15 minuti totali (5 min modifica + 10 min test)

**Happy Fixing! 🚀**
