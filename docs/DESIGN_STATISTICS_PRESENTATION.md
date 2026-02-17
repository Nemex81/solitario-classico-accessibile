# 🎨 DESIGN DOCUMENT
# Statistics Presentation & UI/UX Layer

## 📌 Informazioni Generali

**Nome Feature**: Statistics Presentation & UI/UX Layer  
**Versione Target**: v3.0.0  
**Stato**: Design Phase  
**Data Creazione**: 17 Febbraio 2026  
**Tipo**: Progettazione UI/UX e accessibilità per sistema statistiche

---

## 🔗 Relazione con Altri Design Document

### 📚 Documenti Prerequisiti (LEGGERE PRIMA)

Questo documento è **complementare** e assume familiarità con:

1. **[Timer Mode & Time Outcome System](DESIGN_TIMER_MODE_SYSTEM.md)** (v2.7.0)
   - Definisce `EndReason` enum (VICTORY, ABANDON_*, TIMEOUT_STRICT, VICTORY_OVERTIME)
   - Specifica timer state tracking (`timer_expired`, `overtime_duration`)
   - Stabilisce regole STRICT/PERMISSIVE

2. **[Profile & Statistics System](DESIGN_PROFILE_STATISTICS_SYSTEM.md)** (v3.0.0)
   - Definisce data model (`UserProfile`, `SessionOutcome`, aggregati)
   - Specifica persistenza JSON (storage strategy)
   - Descrive scenari backend (CRUD profili, session recording)

### 🎯 Scope di Questo Documento

Copre **esclusivamente**:
- **Regole di conteggio** (victory/defeat definitions, record eligibility)
- **UI/UX specifications** (dialog layout, menu structure)
- **TTS formatting** (come trasformare dati in stringhe accessibili)
- **Accessibilità NVDA** (focus management, keyboard navigation)
- **Integration points** (quando chiamare cosa nel flusso gameplay)

**NON copre**:
- Data model (già in Profile System doc)
- Storage implementation (già in Profile System doc)
- Timer logic (già in Timer System doc)

---

## 💡 Obiettivo del Documento

Il sistema profili e timer producono **dati strutturati** (`SessionOutcome`, aggregati), ma servono **regole chiare** per:
- Determinare cosa conta come vittoria/sconfitta
- Presentare statistiche in modo accessibile (TTS friendly)
- Gestire navigazione keyboard-only (NVDA compatible)
- Integrare presentazione dati con gameplay flow

**Questo documento definisce il layer di presentazione**, lasciando backend/storage ai documenti esistenti.

---

## 📋 SEZIONE 1: Regole di Conteggio

### 1.1 EndReason: Tassonomia Completa

**Dal Timer System Design** (riferimento autorevole):

```python
class EndReason(Enum):
    # Vittorie
    VICTORY = "victory"                          # Vittoria entro tempo (o timer off)
    VICTORY_OVERTIME = "victory_overtime"        # Vittoria oltre tempo (PERMISSIVE)
    
    # Abbandoni (fine-grained per analytics)
    ABANDON_NEW_GAME = "abandon_new_game"        # Nuova partita durante partita
    ABANDON_EXIT = "abandon_exit"                # ESC/menu con conferma
    ABANDON_APP_CLOSE = "abandon_app_close"      # Chiusura app implicita
    
    # Sconfitte timer
    TIMEOUT_STRICT = "timeout_strict"            # Timer scaduto (STRICT mode)
```

### 1.2 Macro-Categorie (Derivate per Stats/UX)

**Non sono enum**, ma helper functions per aggregazione:

```python
def is_victory(reason: EndReason) -> bool:
    """Qualsiasi vittoria (entro tempo o overtime)."""
    return reason in (VICTORY, VICTORY_OVERTIME)

def is_defeat(reason: EndReason) -> bool:
    """Qualsiasi esito non vittoria."""
    return reason in (
        ABANDON_NEW_GAME,
        ABANDON_EXIT,
        ABANDON_APP_CLOSE,
        TIMEOUT_STRICT
    )

def is_voluntary_abandon(reason: EndReason) -> bool:
    """Abbandono con conferma esplicita utente."""
    return reason in (ABANDON_NEW_GAME, ABANDON_EXIT)

def is_interrupted_abandon(reason: EndReason) -> bool:
    """Abbandono senza conferma (crash/chiusura app)."""
    return reason == ABANDON_APP_CLOSE
```

### 1.3 Conteggio Statistiche Profilo

#### Vittorie e Sconfitte

```python
# Profile stats aggregation
victories = count(is_victory)           # VICTORY + VICTORY_OVERTIME
defeats = count(is_defeat)              # Tutti gli abbandoni + TIMEOUT_STRICT
winrate = victories / (victories + defeats)
```

#### Breakdown Sconfitte

```python
# Detailed defeat analysis
voluntary_abandons = count(is_voluntary_abandon)    # NEW_GAME + EXIT
interrupted_abandons = count(is_interrupted_abandon) # APP_CLOSE
timeout_defeats = count(TIMEOUT_STRICT)

# Validation invariant
assert defeats == (voluntary_abandons + interrupted_abandons + timeout_defeats)
```

### 1.4 Record Eligibility Rules

**Record Tempo** (vittoria più veloce):
```python
# Solo vittorie "pure" (no overtime)
record_time = min(elapsed_time WHERE end_reason == VICTORY)
```

**Record Punteggio** (punteggio massimo):
```python
# Vittorie entro tempo + overtime (esclude abbandoni)
record_score = max(final_score WHERE is_victory(end_reason))
```

**Record Streak** (vittorie consecutive):
```python
# Qualsiasi sconfitta interrompe streak (inclusi abbandoni)
streak_interrupted_by = is_defeat(end_reason)
```

### 1.5 Regole Timer (dal Timer Design)

**Vittoria entro tempo**:
```python
end_reason == VICTORY AND elapsed_time <= timer_limit
```

**Vittoria overtime**:
```python
end_reason == VICTORY_OVERTIME AND overtime_duration > 0
```

**Sconfitta timeout**:
```python
end_reason == TIMEOUT_STRICT  # Solo STRICT mode
```

---

## 📊 SEZIONE 2: Livello 1 - Partita Corrente

### 2.1 Statistiche On-Demand (Durante Gameplay)

**Trigger**: Tasto **I** (Info) durante partita

#### Dialog Info Partita

```
=== INFO PARTITA CORRENTE ===

TEMPO
Trascorso: 3 minuti e 42 secondi
[SE TIMER ATTIVO]
  Timer: 15:00 limite
  Rimanente: 11 minuti e 18 secondi
  [SE OVERTIME]
    Overtime: +2 minuti e 15 secondi

PROGRESSO
Mosse: 87
Pescate: 12 azioni
Ricicli tallone: 2

FONDAZIONI
Carte totali: 18 / 52 (34%)
Semi completati: 0 / 4
  Cuori: 7 carte
  Quadri: 5 carte
  Fiori: 4 carte
  Picche: 2 carte

[SE SCORING ENABLED]
PUNTEGGIO PROVVISORIO
Punteggio: 450 punti
(Il punteggio finale sarà calcolato a fine partita)

[ESC - Chiudi Info]
```

**TTS Announcement** (apertura dialog):
```
"Info partita corrente. Tempo trascorso: 3 minuti e 42 secondi. Mosse: 87. Carte in fondazione: 18 su 52."
```

#### Formatter Method (Conceptual)

```python
def format_current_game_info(
    elapsed_time: float,
    timer_config: dict,
    move_count: int,
    foundation_cards: int,
    total_cards: int,
    provisional_score: int,
    scoring_enabled: bool
) -> str:
    """
    Formatta info partita corrente per TTS.
    
    Returns:
        Stringa multi-line accessibile NVDA.
    """
    # ... implementation in actual code ...
```

---

### 2.2 Dialog Vittoria

**Trigger**: `GameEngine.end_game(EndReason.VICTORY)` o `EndReason.VICTORY_OVERTIME`

#### Layout Dialog (Essenziale)

```
═════════════════════════════════════════════
           VITTORIA!
═════════════════════════════════════════════

Tempo: 5 minuti e 23 secondi
Mosse: 87
Ricicli tallone: 2

[SE TIMER ATTIVO - VICTORY]
✓ Completato entro il limite (15:00)

[SE TIMER ATTIVO - VICTORY_OVERTIME]
⚠ Overtime: +2 minuti e 15 secondi
  Penalità punteggio: -225 punti

[SE SCORING ENABLED]
Punteggio: 1,250 punti
Qualità vittoria: Eccellente (x1.8)

[STATISTICHE PROFILO - Aggiornate]
Vittorie totali: 29
Winrate: 67.4%

[SE RECORD PERSONALE]
🏆 NUOVO RECORD: Vittoria più veloce!
  Precedente: 5min 45sec

─────────────────────────────────────────────
INVIO - Nuova Partita
D - Dettagli Completi
ESC - Menu Principale
```

**TTS Announcement** (apertura dialog):
```
"Vittoria! Completato in 5 minuti e 23 secondi con 87 mosse. Punteggio: 1250 punti. Vittorie totali: 29. Winrate: 67 percento."
[SE RECORD]
"Nuovo record personale: vittoria più veloce!"
```

#### Dialog Dettagli (Tasto D)

```
=== DETTAGLI VITTORIA ===

BREAKDOWN PUNTEGGIO
Punteggio base: 800
Moltiplicatore difficoltà: x1.5 (Livello 3)
Bonus mazzo: +50 (Carte Francesi)
Qualità vittoria: x1.8 (Eccellente)
  - Mosse efficienti: +30%
  - Tempo rapido: +25%
  - Ricicli minimi: +20%
Punteggio finale: 1,250

[SE TIMER OVERTIME]
Penalità overtime: -225
  2min 15sec oltre limite × 100pt/min

CONFRONTO CON MEDIE PERSONALI
Tempo partita: 5:23 (media: 6:45) ↓ 22% più veloce
Mosse: 87 (media: 92) ↓ 5% più efficiente
Punteggio: 1,250 (media: 850) ↑ 47% superiore

RECORD PERSONALI
🏆 Tempo: 5:23 (NUOVO RECORD)
🏆 Punteggio: 1,450 (non battuto)
🏆 Streak: 4 vittorie consecutive (in corso)

[Pagina 1/1]
ESC - Torna a Dialog Vittoria
```

---

### 2.3 Dialog Abbandono

**Trigger**: `GameEngine.end_game(EndReason.ABANDON_*)` o `EndReason.TIMEOUT_STRICT`

#### Layout Dialog (Minimale)

```
═════════════════════════════════════════════
      PARTITA ABBANDONATA
═════════════════════════════════════════════

Tempo giocato: 3 minuti e 12 secondi
Mosse effettuate: 42
Progressione: 18 carte in fondazione (34%)

[SE TIMEOUT_STRICT]
⚠ Motivo: Tempo scaduto (Timer STRICT)

[SE ABANDON_EXIT]
Motivo: Abbandono volontario

[SE ABANDON_NEW_GAME]
Motivo: Nuova partita avviata

[SE ABANDON_APP_CLOSE]
Motivo: Chiusura app durante partita

ESITO
Registrata come: Sconfitta
Influisce su: Winrate, Streak (interrotto)
Non influisce su: Record tempo/punteggio

[STATISTICHE PROFILO - Aggiornate]
Sconfitte totali: 15
Winrate: 65.9%
Streak corrente: 0 (interrotto)

─────────────────────────────────────────────
INVIO - Nuova Partita
ESC - Menu Principale
```

**TTS Announcement**:
```
[SE TIMEOUT_STRICT]
"Partita terminata. Tempo scaduto. Registrata come sconfitta."

[SE ABANDON_EXIT]
"Partita abbandonata. Registrata come sconfitta. Winrate: 65 percento."
```

---

### 2.4 "Ultima Partita" (Persistenza Temporanea)

**Caso d'uso**: Utente chiude dialog vittoria (ESC) e vuole rivedere risultati.

#### Menu Principale (Opzione Nuova)

```
=== MENU PRINCIPALE ===

N - Nuova Partita
U - Ultima Partita (risultati)  [NUOVO]
O - Opzioni
P - Gestione Profili
G - Gioca come Ospite
E - Esci

Profilo attivo: Luca (29 vittorie)
```

#### Dialog "Ultima Partita"

```
=== ULTIMA PARTITA ===

Data: 17 Febbraio 2026, 12:15
Esito: Vittoria

Tempo: 5 minuti e 23 secondi
Mosse: 87
Punteggio: 1,250 punti

Difficoltà: Livello 3
Mazzo: Carte Francesi
Timer: Attivo (15:00 limite)

[ESC - Torna al Menu]
```

**Storage**: Salvato in memoria (`GameEngine.last_session_outcome`) fino a nuova partita.

---

## 📈 SEZIONE 3: Livello 2 - Profilo Utente

### 3.1 Menu Gestione Profili (Esteso)

**Dal Profile System Design**, con aggiunte per statistiche:

```
=== GESTIONE PROFILI ===

1. Cambia Profilo
2. Crea Nuovo Profilo
3. Rinomina Profilo Corrente
4. Elimina Profilo
5. Statistiche Dettagliate  [FOCUS QUESTA SEZIONE]
6. Imposta come Predefinito
7. Reset Statistiche         [NUOVO]

ESC - Torna al Menu Principale
```

---

### 3.2 Statistiche Dettagliate (Opzione 5)

**Trigger**: Menu Gestione Profili → Opzione 5

#### Pagina 1: Statistiche Globali

```
════════════════════════════════════════════════════════
    STATISTICHE PROFILO: Luca
════════════════════════════════════════════════════════

PERFORMANCE GLOBALE
Partite totali: 42
Vittorie: 28 (66.7%)
Sconfitte: 14 (33.3%)
  • Abbandoni volontari: 7
  • Interruzioni: 0
  • Timeout: 7

STREAK
Streak corrente: 3 vittorie
Streak massimo: 8 vittorie consecutive

TEMPO
Tempo totale giocato: 3h 25min
Tempo medio per partita: 4min 52sec
Tempo medio per vittoria: 5min 10sec

RECORD PERSONALI
🏆 Vittoria più veloce: 4min 5sec
🏆 Vittoria più lenta: 12min 30sec
🏆 Punteggio massimo: 1,450 punti

ULTIMI 7 GIORNI
Partite: 12
Vittorie: 8 (66.7%)
Tempo medio: 5min 20sec

────────────────────────────────────────────────────────
Pagina 1/3
Frecce SU/GIÙ - Scroll
PAGE DOWN - Pagina successiva
ESC - Torna a Gestione Profili
```

**TTS Announcement** (apertura):
```
"Statistiche profilo Luca. Pagina 1 di 3. Performance globale. Partite totali: 42. Vittorie: 28. Winrate: 66 percento."
```

---

#### Pagina 2: Performance Timer

```
════════════════════════════════════════════════════════
    STATISTICHE PROFILO: Luca
════════════════════════════════════════════════════════

PERFORMANCE TIMER
Partite con timer attivo: 30 (71% del totale)

VITTORIE TIMER
Vittorie entro tempo: 18 (60%)
Vittorie overtime: 5 (16.7%)
Sconfitte timeout: 7 (23.3%)

OVERTIME ANALYTICS
Overtime medio: 2min 45sec
Overtime massimo: 8min 12sec
Overtime minimo: 45sec

EFFICIENZA TEMPO
Tempo medio vs limite: 85%
  (Media: 12min 45sec su limite 15min)

BREAKDOWN PER MODALITÀ
STRICT mode:
  Partite: 15
  Vittorie: 8 (53.3%)
  Timeout: 7

PERMISSIVE mode:
  Partite: 15
  Vittorie: 15 (100%)
  Overtime: 5 partite

────────────────────────────────────────────────────────
Pagina 2/3
PAGE UP/DOWN - Cambia pagina
ESC - Torna a Gestione Profili
```

---

#### Pagina 3: Performance Scoring & Difficoltà

```
════════════════════════════════════════════════════════
    STATISTICHE PROFILO: Luca
════════════════════════════════════════════════════════

PERFORMANCE SCORING
Punteggio totale accumulato: 23,450
Punteggio medio: 837
Record personale: 1,450

DISTRIBUZIONE QUALITÀ VITTORIE
Perfette (quality ≥1.8): 5 (17.9%)
Buone (quality 1.4-1.7): 12 (42.9%)
Medie (quality <1.4): 11 (39.2%)

PERFORMANCE PER DIFFICOLTÀ
Livello 1 (Principiante):
  Partite: 5 | Vittorie: 5 (100%)
  Tempo medio: 6min 20sec
  Punteggio medio: 650

Livello 2 (Facile):
  Partite: 10 | Vittorie: 8 (80%)
  Tempo medio: 5min 15sec
  Punteggio medio: 780

Livello 3 (Normale):
  Partite: 20 | Vittorie: 12 (60%)
  Tempo medio: 4min 50sec
  Punteggio medio: 920

Livello 4 (Esperto):
  Partite: 5 | Vittorie: 2 (40%)
  Tempo medio: 8min 30sec
  Punteggio medio: 1,100

Livello 5 (Maestro):
  Partite: 2 | Vittorie: 1 (50%)
  Tempo medio: 12min 15sec
  Punteggio medio: 1,350

────────────────────────────────────────────────────────
Pagina 3/3
PAGE UP - Pagina precedente
ESC - Torna a Gestione Profili
```

---

### 3.3 Formatter Methods (Conceptual)

```python
class StatsFormatter:
    """Formatter per statistiche profilo TTS-friendly."""
    
    def format_global_stats(self, stats: GlobalStats) -> str:
        """Pagina 1: Statistiche globali."""
        # Multi-line string con layout accessibile
        pass
    
    def format_timer_stats(self, stats: TimerStats) -> str:
        """Pagina 2: Performance timer."""
        pass
    
    def format_scoring_difficulty_stats(
        self,
        scoring_stats: ScoringStats,
        difficulty_stats: DifficultyStats
    ) -> str:
        """Pagina 3: Scoring + difficoltà."""
        pass
    
    def format_victory_dialog(
        self,
        outcome: SessionOutcome,
        profile_summary: dict
    ) -> str:
        """Dialog vittoria essenziale."""
        pass
    
    def format_abandon_dialog(
        self,
        outcome: SessionOutcome,
        profile_summary: dict
    ) -> str:
        """Dialog abbandono."""
        pass
```

---

## 🏆 SEZIONE 4: Livello 3 - Globale + Record

### 4.1 Menu Leaderboard (Nuovo)

**Menu Principale** (opzione aggiunta):

```
=== MENU PRINCIPALE ===

N - Nuova Partita
U - Ultima Partita
O - Opzioni
P - Gestione Profili
L - Leaderboard Globale  [NUOVO]
G - Gioca come Ospite
E - Esci
```

---

### 4.2 Leaderboard Principale

**Trigger**: Menu Principale → L

```
════════════════════════════════════════════════════════
       LEADERBOARD GLOBALE
════════════════════════════════════════════════════════

1. WINRATE (min 20 partite)
   1° Papà      78.5% (33 vittorie / 42 partite)
   2° Luca      66.7% (28 vittorie / 42 partite) ← TU
   3° Mamma     53.3% (8 vittorie / 15 partite)

2. VITTORIE TOTALI
   1° Papà      33 vittorie
   2° Luca      28 vittorie ← TU
   3° Mamma     8 vittorie

3. RECORD TEMPO (vittoria più veloce)
   1° Luca      4min 5sec ← TU
   2° Papà      4min 23sec
   3° Mamma     6min 12sec

4. RECORD PUNTEGGIO
   1° Papà      1,680 punti
   2° Luca      1,450 punti ← TU
   3° Mamma     920 punti

5. STREAK MASSIMO
   1° Papà      23 vittorie consecutive
   2° Luca      8 vittorie consecutive ← TU
   3° Mamma     3 vittorie consecutive

────────────────────────────────────────────────────────
Frecce SU/GIÙ - Scroll
F - Filtra per Difficoltà
T - Filtra per Timer Mode
ESC - Torna al Menu Principale
```

**TTS Announcement**:
```
"Leaderboard globale. 5 classifiche disponibili. Winrate: secondo posto con 66 percento. Record tempo: primo posto con 4 minuti e 5 secondi."
```

**Note**:
- Profilo Ospite **escluso** (policy dal Profile System Design)
- Profilo corrente evidenziato con `← TU`
- Calcolo **on-demand** (scan profiles all'apertura menu)

---

### 4.3 Filtri Leaderboard (Opzionali v3.1+)

**Tasto F**: Filtra per difficoltà

```
=== FILTRA PER DIFFICOLTÀ ===

Seleziona livello:
1. Livello 1 - Principiante
2. Livello 2 - Facile
3. Livello 3 - Normale
4. Livello 4 - Esperto
5. Livello 5 - Maestro
A. Tutti i livelli (default)

ESC - Annulla filtro
```

**Tasto T**: Filtra per timer mode

```
=== FILTRA PER TIMER MODE ===

1. Timer OFF
2. Timer STRICT
3. Timer PERMISSIVE
4. Tutti i timer (default)

ESC - Annulla filtro
```

---

### 4.4 Calcolo Leaderboard (On-Demand)

**Logic** (pseudo-code conceptual):

```python
def calculate_leaderboard(
    profiles: List[UserProfile],
    metric: str,
    filters: dict = None
) -> List[LeaderboardEntry]:
    """
    Calcola classifica per metrica specifica.
    
    Args:
        profiles: Tutti i profili (escluso guest)
        metric: "winrate" | "victories" | "fastest_time" | "highest_score" | "streak"
        filters: Opzionali (difficulty, timer_mode)
    
    Returns:
        Lista ordinata LeaderboardEntry (top 10)
    """
    # 1. Filter out guest profile
    valid_profiles = [p for p in profiles if not p.is_guest]
    
    # 2. Apply optional filters (difficulty, timer mode)
    if filters:
        # ... filter logic ...
        pass
    
    # 3. Extract metric from each profile
    entries = []
    for profile in valid_profiles:
        value = extract_metric(profile, metric)
        entries.append(LeaderboardEntry(
            profile_name=profile.profile_name,
            value=value
        ))
    
    # 4. Sort descending (higher is better)
    entries.sort(key=lambda e: e.value, reverse=True)
    
    # 5. Return top 10
    return entries[:10]
```

**Performance**: Con 10-20 profili, calcolo istantaneo (<50ms). Se profili >50, considerare cache (v3.1+).

---

## 🎧 SEZIONE 5: Accessibilità NVDA

### 5.1 Regola 1: Focus Iniziale + Annuncio

**Pattern**: Ogni dialog deve settare focus su elemento principale e annunciare contesto.

#### Dialog Gestione Profili

```python
# wxPython pseudo-code
class ProfileManagementDialog(wx.Dialog):
    def __init__(self):
        # ... UI setup ...
        self.profile_list = wx.ListCtrl(...)
        # Populate list
        self.profile_list.InsertItem(0, "Luca (predefinito)")
        self.profile_list.Select(0)
        
    def on_show(self):
        # Set focus su lista
        self.profile_list.SetFocus()
        # Accessible name per TTS
        self.SetTitle("Gestione profili")
        self.profile_list.SetName("Elenco profili. Selezionato: Luca, predefinito.")
```

**TTS Output atteso**:
```
[Dialog apre]
"Gestione profili. Elenco profili. Selezionato: Luca, predefinito."
```

---

### 5.2 Regola 2: Pulsanti Disabilitati Parlanti

**Pattern**: Pulsanti disabilitati devono spiegare perché (no silent disable).

#### Scenario: Profilo Ospite Selezionato

```python
def on_profile_selected(profile: UserProfile):
    if profile.is_guest:
        # Disable actions
        self.edit_button.Enable(False)
        self.delete_button.Enable(False)
        
        # Set help text (NVDA legge con NVDA+Tab)
        self.edit_button.SetHelpText(
            "Non disponibile: il profilo Ospite non può essere modificato."
        )
        self.delete_button.SetHelpText(
            "Non disponibile: il profilo Ospite non può essere eliminato."
        )
    else:
        # Enable + clear help
        self.edit_button.Enable(True)
        self.delete_button.Enable(True)
        self.edit_button.SetHelpText("")
        self.delete_button.SetHelpText("")
```

**TTS Output**:
```
[Tab su "Elimina profilo"]
"Elimina profilo. Pulsante. Non disponibile."
[NVDA+Tab per help]
"Non disponibile: il profilo Ospite non può essere eliminato."
```

---

### 5.3 Regola 3: Statistiche Multipage (Scroll Keyboard)

**Pattern**: TextCtrl multiline con scroll arrow keys + PageUp/Down.

```python
class DetailedStatsDialog(wx.Dialog):
    def __init__(self):
        # TextCtrl read-only multiline
        self.stats_text = wx.TextCtrl(
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )
        self.current_page = 1
        self.total_pages = 3
        
        # Load page 1
        self.load_page(1)
        
        # Bind keys
        self.stats_text.Bind(wx.EVT_KEY_DOWN, self.on_key)
    
    def on_key(self, event):
        key = event.GetKeyCode()
        
        if key == wx.WXK_UP:
            # Scroll su (1 riga) - NVDA legge automaticamente
            self.scroll_line(-1)
            
        elif key == wx.WXK_DOWN:
            # Scroll giù (1 riga)
            self.scroll_line(+1)
            
        elif key == wx.WXK_PAGEDOWN:
            # Pagina successiva
            if self.current_page < self.total_pages:
                self.load_page(self.current_page + 1)
                # Announce page change
                wx.Bell()  # Beep per feedback
                
        elif key == wx.WXK_PAGEUP:
            # Pagina precedente
            if self.current_page > 1:
                self.load_page(self.current_page - 1)
                wx.Bell()
    
    def load_page(self, page_num: int):
        # Carica contenuto pagina
        content = self.formatter.get_page_content(page_num)
        self.stats_text.SetValue(content)
        self.current_page = page_num
        
        # Update accessible name
        self.stats_text.SetName(f"Pagina {page_num} di {self.total_pages}")
```

**TTS Behavior**:
- **Freccia SU/GIÙ**: NVDA legge riga corrente automaticamente
- **PageDown**: Beep + annuncio "Pagina 2 di 3" + legge inizio pagina
- **Home/End**: Salta inizio/fine documento

---

### 5.4 Checklist Accessibilità NVDA

**Per ogni dialog**:

- [ ] Focus iniziale su elemento principale (non su label/groupbox)
- [ ] Accessible name settato (`SetName()` o `SetLabel()`)
- [ ] Pulsanti disabilitati con help text (`SetHelpText()`)
- [ ] Scroll keyboard supportato (arrow keys, PageUp/Down)
- [ ] ESC chiude dialog (sempre)
- [ ] Tab order logico (top-to-bottom, left-to-right)
- [ ] Nessun controllo decorativo nel tab order (skip invisible/disabled)
- [ ] Annunci TTS non ridondanti (no spam "dialog... pannello... groupbox...")

---

## 🔗 SEZIONE 6: Integration Points

### 6.1 Flow Partita Completa

```
User: "Nuova Partita"
    ↓
GameEngine.new_game()
    ↓
1. Crea SessionOutcome (campi iniziali)
2. Reset contatori GameService
3. Start timer (se enabled)
    ↓
Gameplay Loop
    ↓
[User: Tasto I]
    ↓
GameEngine.show_current_game_info()
    ↓
StatsFormatter.format_current_game_info()
    ↓
Dialog Info (Livello 1)
    ↓
[User: Vittoria o Abbandono]
    ↓
GameEngine.end_game(end_reason: EndReason)
    ↓
1. Finalizza SessionOutcome (tutti campi)
2. ProfileService.record_session(outcome)
    ↓
3. ProfileService.update_aggregates()
    - global_stats
    - timer_stats
    - difficulty_stats
    - scoring_stats
    ↓
4. ProfileService.save()  # Write JSON
    ↓
5. StatsFormatter.format_victory_dialog(outcome)
    OPPURE
   StatsFormatter.format_abandon_dialog(outcome)
    ↓
Dialog Vittoria/Abbandono (Livello 2)
    ↓
[User: ESC o INVIO]
    ↓
Ritorno Menu Principale
```

---

### 6.2 Hook Points in GameEngine

**Metodi da implementare/estendere**:

```python
class GameEngine:
    # Existing (da estendere)
    def end_game(self, end_reason: EndReason):  # NEW signature
        """Termina partita con motivo specifico."""
        # 1. Finalize SessionOutcome
        # 2. Call ProfileService.record_session()
        # 3. Show appropriate dialog (victory/abandon)
        pass
    
    # NEW methods
    def show_current_game_info(self):
        """Mostra dialog info partita corrente (Livello 1)."""
        pass
    
    def show_victory_dialog(self, outcome: SessionOutcome):
        """Dialog vittoria con stats aggiornate."""
        pass
    
    def show_abandon_dialog(self, outcome: SessionOutcome, reason: EndReason):
        """Dialog abbandono con policy chiara."""
        pass
    
    def show_last_game_summary(self):
        """Menu opzione "Ultima Partita"."""
        pass
```

---

### 6.3 Sequenze Critiche

#### Sequenza 1: Vittoria con Record

```
GameEngine.end_game(EndReason.VICTORY)
    ↓
SessionOutcome finalized
    ↓
ProfileService.record_session(outcome)
    ↓
ProfileService.check_personal_records(outcome)
    ↓ [Record battuto]
ProfileService.update_record("fastest_time", outcome.elapsed_time)
    ↓
StatsFormatter.format_victory_dialog(
    outcome,
    records_broken=["fastest_time"]
)
    ↓
Dialog Vittoria (con annuncio record)
```

#### Sequenza 2: Timeout STRICT

```
Timer tick check (GameEngine)
    ↓
elapsed_time >= timer_limit
    ↓
GameService.timer_expired = True
    ↓
GameEngine.end_game(EndReason.TIMEOUT_STRICT)
    ↓
SessionOutcome:
    end_reason = TIMEOUT_STRICT
    timer_expired = True
    overtime_duration = 0
    ↓
ProfileService.record_session(outcome)
    ↓
StatsFormatter.format_abandon_dialog(outcome)
    ↓
Dialog Abbandono ("Tempo scaduto")
```

#### Sequenza 3: Chiusura App (Session Tracking)

```
Partita in corso
    ↓
User chiude app (X / Alt+F4)
    ↓
GameEngine.on_close()
    ↓
SessionTracker.mark_session_dirty()  # Flag "non chiusa pulitamente"
    ↓
App termina

--- Avvio Successivo ---

App.startup()
    ↓
SessionTracker.check_orphaned_sessions()
    ↓ [Session dirty trovata]
SessionTracker.recover_orphaned_session()
    ↓
SessionOutcome ricostruito:
    end_reason = ABANDON_APP_CLOSE
    is_victory = False
    ↓
ProfileService.record_session(outcome)  # Retroattivo
    ↓
Log: "Sessione orfana recuperata e registrata come abbandono."
```

---

## ✅ SEZIONE 7: Checklist Implementazione

### Phase 1: Regole Conteggio (Foundation)

- [ ] EndReason enum implementato (5 valori)
- [ ] Helper functions (is_victory, is_defeat, is_voluntary_abandon)
- [ ] Record eligibility logic (fastest_time, highest_score)
- [ ] Streak calculation logic (interruption on defeat)

### Phase 2: Livello 1 - Partita Corrente

- [ ] Dialog Info Partita (tasto I)
- [ ] Dialog Vittoria (essenziale + tasto D per dettagli)
- [ ] Dialog Abbandono (policy chiara)
- [ ] "Ultima Partita" menu option + snapshot

### Phase 3: Livello 2 - Profilo

- [ ] Statistiche Dettagliate (3 pagine)
- [ ] Formatter methods (StatsFormatter class)
- [ ] Scroll keyboard (arrow keys, PageUp/Down)
- [ ] Timeline ultimi 7 giorni

### Phase 4: Livello 3 - Globale

- [ ] Menu Leaderboard
- [ ] Calcolo on-demand (scan profiles)
- [ ] Top 5 classifiche (winrate, victories, time, score, streak)
- [ ] Profilo corrente evidenziato
- [ ] Guest profile escluso

### Phase 5: Accessibilità NVDA

- [ ] Focus iniziale su tutti i dialog
- [ ] Pulsanti disabilitati con help text
- [ ] Accessible names settati
- [ ] TTS announcements non ridondanti
- [ ] ESC chiude tutti i dialog

### Phase 6: Integration

- [ ] GameEngine.end_game() esteso con EndReason
- [ ] ProfileService.record_session() hook
- [ ] SessionTracker per orphaned sessions
- [ ] Formatter integration in tutti i dialog

---

## 📊 Stima Implementazione

**Basato su performance GitHub Copilot Agent** (commit storici PR #64, #66):

| Fase | Componenti | Commit | Tempo | Test |
|---|---|---|---|---|
| **1. Regole Conteggio** | EndReason helpers, record logic | 1 | 8-12 min | 6-8 |
| **2. Livello 1 Dialog** | Info, Vittoria, Abbandono | 2-3 | 20-30 min | 10-12 |
| **3. Formatter Class** | StatsFormatter methods | 1-2 | 15-20 min | 8-10 |
| **4. Livello 2 Stats** | Pagine dettagliate + scroll | 2-3 | 25-35 min | 12-15 |
| **5. Livello 3 Leaderboard** | Menu + calcolo on-demand | 2 | 15-20 min | 8-10 |
| **6. Accessibilità NVDA** | Focus, help text, annunci | 1-2 | 10-15 min | 6-8 |
| **7. Integration Hooks** | GameEngine.end_game() esteso | 1-2 | 12-18 min | 10-12 |
| **TOTALE** | | **10-15** | **105-150 min** | **60-75** |

**Stima Realistica**: Copilot Agent completa presentazione layer in **1.5-2.5 ore**.

---

## ✅ Stato del Design

- [x] Regole conteggio formalizzate (victory/defeat/record)
- [x] 3 livelli UI specificati (partita/profilo/globale)
- [x] Dialog mockup dettagliati (layout text-based)
- [x] Formatter logic definita (conceptual methods)
- [x] Accessibilità NVDA regole complete (3 pattern core)
- [x] Integration points mappati (flow diagrams)
- [x] Cross-reference con Timer + Profile design

**Design completo e pronto per implementazione.**

---

## 📚 Riferimenti

- **Timer System Design**: [DESIGN_TIMER_MODE_SYSTEM.md](DESIGN_TIMER_MODE_SYSTEM.md)
- **Profile & Statistics System**: [DESIGN_PROFILE_STATISTICS_SYSTEM.md](DESIGN_PROFILE_STATISTICS_SYSTEM.md)
- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)
- **Versione Corrente**: v2.6.1 (16 Febbraio 2026)

---

**Documento creato**: 17 Febbraio 2026, 12:30 CET  
**Autore**: Luca (utente) + Perplexity AI (design/analisi)  
**Prossimo Step**: Implementation plan per backend (Profile System) + frontend (Presentation Layer)
