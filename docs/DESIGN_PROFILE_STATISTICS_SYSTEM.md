# 🎨 DESIGN DOCUMENT
# Profile & Statistics System

## 📌 Informazioni Generali

**Nome Feature**: Profile & Statistics System  
**Versione Target**: v3.0.0  
**Stato**: Design Phase  
**Data Creazione**: 17 Febbraio 2026  
**Tipo**: Progettazione logico-concettuale per sistema profili multi-utente

---

## 💡 Obiettivo della Modifica

Il gioco attualmente **non traccia progressi utente** in modo strutturato:
- Nessuna distinzione tra giocatori diversi
- Statistiche volatili (perse a chiusura app)
- Impossibile confrontare performance nel tempo
- Nessuno storico partite consultabile

**Questa modifica introduce**:
- **Sistema profili** multi-utente (famiglia/amici su stesso PC)
- **Statistiche aggregate** persistenti (winrate, record, medie)
- **Storico partite** dettagliato con replay informazioni
- **Modalità ospite** per sessioni temporanee
- **Integrazione seamless** con timer system (v2.7.0) e scoring (v2.0)

---

## 🎯 Problema Attuale

### Stato Codice v2.6.1

**Limiti esistenti**:
- `GameEngine` genera `FinalScore` ma **non lo salva** ([scoring_service.py](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/src/domain/services/scoring_service.py))
- `ScoreStorage` esiste ma salva solo **"last game"** in JSON temporaneo
- Nessun concetto di "utente" o "sessione di gioco"
- Timer system (v2.7.0 design) produce `EndReason` senza storage definito

**Impatto**:
- Dati preziosi persi (ogni partita sovrascrive la precedente)
- Impossibile rispondere a "Quante partite ho vinto?"
- Impossibile tracking progressi (miglioramento skill)
- Nessuna motivazione long-term (achievement, record)

---

## 🧩 Concetti Fondamentali

### 1. Profilo Utente

Rappresenta un **giocatore individuale** con identità persistente.

```python
@dataclass
class UserProfile:
    # Identità
    profile_id: str           # UUID unico
    profile_name: str         # "Luca", "Ospite", "Mamma"
    created_at: datetime      # Data creazione
    last_played: datetime     # Ultimo accesso
    is_default: bool          # Auto-selezionato all'avvio
    is_guest: bool            # Profilo ospite (speciale)
    
    # Preferenze (future, placeholder)
    preferred_difficulty: int = 3
    preferred_deck: str = "french"
```

**Caratteristiche**:
- **Multi-utente**: Supporta famiglia/amici su stesso PC
- **Persistente**: Dati salvati tra sessioni app
- **Identificabile**: UUID previene conflitti nomi
- **Selezionabile**: Profilo attivo determina dove salvare partite

---

### 2. Session Outcome (Unità Atomica)

Snapshot **completo** di una partita terminata. È l'unità minima che alimenta:
- Storico partite dettagliato
- Aggregati statistici profilo
- Record personali

```python
@dataclass
class SessionOutcome:
    # ========================================
    # IDENTIFICAZIONE
    # ========================================
    session_id: str           # UUID unico partita
    profile_id: str           # A quale profilo appartiene
    timestamp: datetime       # Quando è finita (ISO 8601)
    
    # ========================================
    # ESITO PARTITA (da Timer System v2.7.0)
    # ========================================
    end_reason: EndReason     # victory | abandon_* | timeout | overtime
    is_victory: bool          # Shortcut per query aggregate
    
    # ========================================
    # TEMPO (da Timer System v2.7.0)
    # ========================================
    elapsed_time: float       # Secondi totali partita
    timer_enabled: bool       # Timer era attivo?
    timer_limit: int          # Limite configurato (secondi, 0=off)
    timer_mode: str           # "STRICT" | "PERMISSIVE" | "OFF"
    timer_expired: bool       # Scadenza avvenuta?
    overtime_duration: float  # Secondi oltre limite (0 se non overtime)
    
    # ========================================
    # SCORING (da Scoring System v2.0)
    # ========================================
    scoring_enabled: bool     # Sistema punti attivo?
    final_score: int          # Punteggio finale totale
    base_score: int           # Punteggio base (mosse/tempo)
    difficulty_multiplier: float  # Moltiplicatore difficoltà
    deck_bonus: int           # Bonus tipo mazzo
    quality_multiplier: float # Qualità vittoria (1.0-2.0)
    
    # ========================================
    # CONFIGURAZIONE PARTITA
    # ========================================
    difficulty_level: int     # 1-5
    deck_type: str            # "french" | "neapolitan"
    draw_count: int           # 1-3 carte pescate
    shuffle_mode: str         # "invert" | "random"
    
    # ========================================
    # GAMEPLAY STATS (da GameService)
    # ========================================
    move_count: int           # Mosse totali
    draw_count_actions: int   # Azioni pescata
    recycle_count: int        # Ricicli tallone
    foundation_cards: List[int]  # [13,13,10,8] = carte per seme
    completed_suits: int      # 0-4 semi completati
    
    # ========================================
    # METADATA (opzionali v3.1+)
    # ========================================
    game_version: str = "2.6.1"  # Versione app
    notes: str = ""           # Note utente (future)
```

**Design Rationale**:
- **Completo**: Ogni campo necessario per ricostruire contesto partita
- **Immutabile**: Una volta salvato, non si modifica (audit trail)
- **Integrabile**: Compatibile con timer system + scoring system
- **Estensibile**: Campo `notes` e `game_version` per future features

---

### 3. Statistiche Aggregate

Dati **calcolati** da SessionOutcome, salvati nel profilo per query veloci.

#### A) Statistiche Globali (Tutte le Partite)

```python
@dataclass
class GlobalStats:
    # Contatori base
    total_games: int = 0
    total_victories: int = 0
    total_defeats: int = 0        # abandons + timeouts
    
    # Ratios
    winrate: float = 0.0          # victories / total_games
    
    # Tempo
    total_playtime: float = 0.0   # Secondi totali
    average_game_time: float = 0.0
    fastest_victory: float = float('inf')  # Record tempo minimo
    slowest_victory: float = 0.0           # Tempo massimo
    
    # Record
    highest_score: int = 0        # Punteggio massimo
    longest_streak: int = 0       # Vittorie consecutive
    current_streak: int = 0       # Streak attuale
```

#### B) Statistiche Timer (Solo Partite con Timer)

```python
@dataclass
class TimerStats:
    games_with_timer: int = 0
    
    # Breakdown per esito
    victories_within_time: int = 0   # EndReason.VICTORY (no overtime)
    victories_overtime: int = 0      # EndReason.VICTORY_OVERTIME
    defeats_timeout: int = 0         # EndReason.TIMEOUT_STRICT
    
    # Overtime analytics
    total_overtime: float = 0.0      # Secondi totali overtime
    average_overtime: float = 0.0    # Media quando presente
    max_overtime: float = 0.0        # Peggiore overtime
    
    # Performance
    average_time_vs_limit: float = 0.0  # Efficienza tempo
```

#### C) Statistiche per Difficoltà (Breakdown 1-5)

```python
@dataclass
class DifficultyStats:
    games_by_level: Dict[int, int]      # {1: 10, 2: 5, ...}
    victories_by_level: Dict[int, int]
    winrate_by_level: Dict[int, float]
    average_score_by_level: Dict[int, float]
```

#### D) Statistiche Scoring (Solo se Scoring Enabled)

```python
@dataclass
class ScoringStats:
    games_with_scoring: int = 0
    
    total_score: int = 0              # Somma tutti i punteggi
    average_score: float = 0.0
    highest_score: int = 0
    lowest_score: int = 0             # Solo vittorie
    
    # Quality distribution
    perfect_games: int = 0            # quality_multiplier >= 1.8
    good_games: int = 0               # quality >= 1.4
    average_games: int = 0            # quality < 1.4
```

**Nota**: Aggregati **precalcolati** e salvati in profilo per performance. Aggiornati incrementalmente ad ogni partita.

---

### 4. Persistenza: Strategia Ibrida JSON

**Scelta architetturale**: **JSON files** (non SQLite) per:
- Semplicità implementazione (~1 ora agent vs 2-3 ore SQLite)
- Human-readable (debug facile)
- Zero dipendenze esterne
- Compatibile con storage esistente (ScoreStorage pattern)

#### Struttura Directory

```
data/
├─ profiles/
│  ├─ profiles_index.json        # Lista profili + metadati
│  ├─ profile_<uuid>.json        # Aggregati + ultimi 50 outcome
│  └─ sessions_<uuid>.json       # Storico completo (append-only)
│
└─ backups/                       # Backup automatici (future)
   └─ profiles_YYYYMMDD.zip
```

#### File: `profiles_index.json`

Lista profili per selezione rapida all'avvio.

```json
{
  "version": "3.0.0",
  "default_profile_id": "uuid-123",
  "profiles": [
    {
      "profile_id": "uuid-123",
      "profile_name": "Luca",
      "is_default": true,
      "is_guest": false,
      "created_at": "2026-02-17T09:00:00Z",
      "last_played": "2026-02-17T09:15:00Z",
      "total_games": 42,
      "total_victories": 28,
      "winrate": 0.67
    },
    {
      "profile_id": "guest",
      "profile_name": "Ospite",
      "is_default": false,
      "is_guest": true,
      "created_at": "2026-02-01T10:00:00Z",
      "last_played": "2026-02-15T14:30:00Z",
      "total_games": 5,
      "total_victories": 2,
      "winrate": 0.40
    }
  ]
}
```

**Funzioni**:
- Caricamento rapido lista profili (no scan directory)
- Default profile per auto-select all'avvio
- Summary stats per UI (no need to load full profile)

#### File: `profile_<uuid>.json`

Dati completi profilo + aggregati + **ultimi 50 outcome** (cache query veloci).

```json
{
  "profile_id": "uuid-123",
  "profile_name": "Luca",
  "created_at": "2026-02-17T09:00:00Z",
  "last_played": "2026-02-17T09:15:00Z",
  "is_default": true,
  "is_guest": false,
  
  "global_stats": {
    "total_games": 42,
    "total_victories": 28,
    "winrate": 0.67,
    "fastest_victory": 245.3,
    "highest_score": 1250
  },
  
  "timer_stats": {
    "games_with_timer": 30,
    "victories_within_time": 18,
    "victories_overtime": 5,
    "defeats_timeout": 7
  },
  
  "difficulty_stats": {
    "games_by_level": {"1": 5, "2": 10, "3": 20, "4": 5, "5": 2},
    "winrate_by_level": {"1": 1.0, "2": 0.8, "3": 0.6, "4": 0.4, "5": 0.5}
  },
  
  "recent_sessions": [
    {"session_id": "sess-001", "timestamp": "...", "is_victory": true, ...},
    {"session_id": "sess-002", "timestamp": "...", "is_victory": false, ...}
  ]
}
```

**Note**:
- `recent_sessions`: Ultimi 50 outcome per query veloci ("ultime partite")
- Aggregati precalcolati per performance UI
- Storico completo in file separato (scaling)

#### File: `sessions_<uuid>.json`

Storico **completo** partite (append-only, crescita illimitata).

```json
{
  "profile_id": "uuid-123",
  "version": "3.0.0",
  "sessions": [
    {
      "session_id": "sess-001",
      "timestamp": "2026-02-17T09:00:00Z",
      "end_reason": "victory",
      "is_victory": true,
      "elapsed_time": 312.5,
      "final_score": 850,
      "difficulty_level": 3,
      ...
    },
    {...}
  ]
}
```

**Caratteristiche**:
- **Write-only append**: Nuove partite aggiunte in coda
- **Immutabile**: Nessuna modifica a session esistenti (audit trail)
- **Compressione futura**: v3.1+ può comprimere vecchi dati

---

### 5. Profilo Ospite (Guest Mode)

**Caso d'uso**: Amico/familiare gioca senza creare profilo permanente.

#### Caratteristiche Speciali

```python
GUEST_PROFILE = UserProfile(
    profile_id="guest",           # ID fisso (non UUID)
    profile_name="Ospite",
    is_guest=True,                # Flag speciale
    is_default=False,             # Mai auto-select
    created_at=<install_date>
)
```

**Comportamento**:
- **Non eliminabile**: Sempre presente in profiles_index
- **Statistiche separate**: Non inquina profili "veri"
- **Conversione opzionale**: "Vuoi salvare come nuovo profilo?" (future v3.1)
- **Reset permesso**: "Cancella statistiche ospite" disponibile

#### Flusso UI Modalità Ospite

```
1. Menu: "Gioca come Ospite"
2. App seleziona GUEST_PROFILE come attivo
3. TTS: "Modalità ospite attiva. Le statistiche non saranno salvate permanentemente."
4. Partite salvate in sessions_guest.json
5. Fine sessione: ritorna a profilo default
```

---

## 🔄 Stati e Transizioni

### Ciclo Vita Profilo

```
App Start
   ↓
Carica profiles_index.json
   ↓
   ├─ Nessun profilo? → Prima Esecuzione
   │     ↓
   │  Dialog "Crea Profilo"
   │     ↓
   │  Profilo creato (is_default=True)
   │
   └─ Profili esistenti? → Selezione
         ↓
      Carica default_profile_id
         ↓
      Menu Principale (profilo attivo visualizzato)
```

### Ciclo Vita Sessione

```
New Game Start
   ↓
Crea SessionOutcome (campi iniziali)
   ↓
Gameplay (tracking mosse/tempo)
   ↓
Game End (vittoria/abbandono/timeout)
   ↓
Finalizza SessionOutcome (tutti campi popolati)
   ↓
   ├─ Append a sessions_<uuid>.json
   ├─ Update profile_<uuid>.json (aggregati)
   └─ Update profiles_index.json (summary)
```

---

## 🎬 Scenari di Utilizzo

### Scenario A — Prima Esecuzione

```
1. Utente avvia app per prima volta
2. Sistema rileva: profiles_index.json non esiste
3. Dialog TTS: "Benvenuto! Crea il tuo profilo per iniziare."
4. Input: Nome profilo (default "Giocatore")
5. Sistema crea:
   - profiles_index.json con 1 profilo + ospite
   - profile_<uuid>.json (stats vuote)
   - sessions_<uuid>.json (array vuoto)
6. Profilo impostato come default
7. Continua a menu principale
```

---

### Scenario B — Avvio Normale

```
1. App carica profiles_index.json
2. Identifica default_profile_id
3. Carica profile_<uuid>.json in memoria
4. Menu principale mostra: "Profilo attivo: Luca"
5. TTS: "Benvenuto Luca. Hai 28 vittorie su 42 partite."
```

---

### Scenario C — Cambio Profilo

```
1. Menu: "Gestione Profili" → "Cambia Profilo"
2. Lista profili caricata da profiles_index.json
3. TTS: "Profili disponibili: 1. Luca (attivo). 2. Mamma. 3. Ospite."
4. Selezione: "2. Mamma"
5. Sistema:
   - Salva profilo corrente (flush aggregati)
   - Carica profile_mamma.json
   - Update profiles_index (last_played)
6. TTS: "Profilo cambiato a: Mamma."
7. Menu principale aggiornato
```

---

### Scenario D — Partita Completata (Vittoria)

```
1. Utente vince partita (EndReason.VICTORY)
2. GameEngine finalizza SessionOutcome:
   - session_id: generato UUID
   - profile_id: "uuid-123" (profilo attivo)
   - timestamp: "2026-02-17T09:15:00Z"
   - end_reason: EndReason.VICTORY
   - is_victory: True
   - elapsed_time: 312.5
   - final_score: 850
   - (tutti altri campi popolati)
3. ProfileService.record_session(outcome):
   - Append a sessions_uuid-123.json
   - Update global_stats (victories++, winrate recalc)
   - Update timer_stats se timer attivo
   - Update difficulty_stats per livello
   - Update recent_sessions (FIFO 50 elementi)
4. ProfileService.save():
   - Write profile_uuid-123.json
   - Update profiles_index.json (last_played, summary)
5. Dialog vittoria mostra statistiche aggiornate
```

---

### Scenario E — Partita Abbandonata

```
1. Utente preme ESC → Conferma abbandono
2. GameEngine finalizza SessionOutcome:
   - end_reason: EndReason.ABANDON_EXIT
   - is_victory: False
   - elapsed_time: 180.0 (abbandonata a 3 min)
3. ProfileService.record_session(outcome):
   - Append a sessions (anche abbandoni tracciati)
   - Update global_stats (defeats++)
   - Update current_streak = 0 (streak interrotta)
4. Nessun dialog vittoria (ritorno menu)
```

---

### Scenario F — Modalità Ospite

```
1. Menu: "Gioca come Ospite"
2. Sistema:
   - Salva profilo corrente (flush)
   - Carica GUEST_PROFILE
3. TTS: "Modalità ospite. Le statistiche saranno temporanee."
4. Partita giocata normalmente
5. SessionOutcome salvato con profile_id="guest"
6. Fine sessione:
   - Menu: "Torna a Profilo Principale"
   - Sistema ricarica default_profile_id
7. Statistiche ospite persistenti ma separate
```

---

## 👤 UI/UX: Menu Gestione Profili

### Menu Principale (Estensione)

```
[Opzione esistente] N - Nuova Partita
[Opzione esistente] O - Opzioni
[Opzione esistente] E - Esci

[NUOVO] P - Gestione Profili
[NUOVO] G - Gioca come Ospite

[Info sempre visibile] Profilo attivo: Luca (28 vittorie)
```

### Submenu: Gestione Profili (P)

```
=== GESTIONE PROFILI ===

1. Cambia Profilo
2. Crea Nuovo Profilo
3. Rinomina Profilo Corrente
4. Elimina Profilo
5. Statistiche Dettagliate
6. Imposta come Predefinito

ESC - Torna al Menu Principale
```

#### Opzione 1: Cambia Profilo

```
=== CAMBIA PROFILO ===

Profili disponibili:
1. Luca (attivo) - 28 vittorie
2. Mamma - 15 vittorie
3. Papà - 42 vittorie
4. Ospite - 2 vittorie

Seleziona numero (1-4) o ESC per annullare:
```

#### Opzione 2: Crea Nuovo Profilo

```
=== CREA NUOVO PROFILO ===

Inserisci nome profilo:
[Input field]

Conferma (INVIO) o Annulla (ESC)

[Validation]
- Nome non vuoto
- Max 30 caratteri
- No duplicati
```

#### Opzione 5: Statistiche Dettagliate

```
=== STATISTICHE PROFILO: Luca ===

Globali:
- Partite totali: 42
- Vittorie: 28 (66.7%)
- Sconfitte: 14 (33.3%)
- Tempo totale: 3h 25min
- Tempo medio partita: 4min 52sec
- Vittoria più veloce: 4min 5sec
- Punteggio massimo: 1250
- Streak corrente: 3 vittorie

Per Difficoltà:
- Livello 1: 5 partite, 100% vittorie
- Livello 2: 10 partite, 80% vittorie
- Livello 3: 20 partite, 60% vittorie
- Livello 4: 5 partite, 40% vittorie
- Livello 5: 2 partite, 50% vittorie

Timer:
- Partite con timer: 30
- Vittorie entro tempo: 18 (60%)
- Vittorie overtime: 5 (16.7%)
- Sconfitte timeout: 7 (23.3%)

Pagina 1/2 - Frecce SU/GIÙ per navigare
ESC - Torna a Gestione Profili
```

---

## 🎧 Considerazioni Accessibilità

### Annunci TTS Profili

**All'avvio**:
```
"Benvenuto [Nome]. Hai [N] vittorie su [M] partite."
```

**Cambio profilo**:
```
"Profilo cambiato a: [Nome]."
```

**Modalità ospite**:
```
"Modalità ospite attiva. Le statistiche non saranno permanenti."
```

**Fine partita (con aggiornamenti)**:
```
[Esistente] "Vittoria! Completato in 5 minuti con 45 mosse. Punteggio: 850."
[NUOVO] "Vittorie totali: 29. Winrate: 67%."
```

### Navigazione Keyboard-Only

- **Gestione Profili**: Accessibile da menu (tasto P)
- **Cambio profilo**: Lista numerata (1-9 + frecce)
- **Statistiche**: Scrollable con frecce SU/GIÙ
- **Creazione profilo**: Input field standard wxPython

---

## ⚖️ Decisioni di Design

### ✅ Decisioni Confermate

1. **JSON Storage (non SQLite)**
   - Semplicità implementazione (~1 ora vs 2-3 ore)
   - Human-readable per debug
   - Compatibile con pattern esistente (ScoreStorage)

2. **Profilo Ospite Permanente**
   - ID fisso "guest" (non UUID)
   - Non eliminabile
   - Statistiche separate ma persistenti

3. **Aggregati Precalcolati**
   - Performance UI (no scan completo storico)
   - Update incrementale ad ogni partita
   - Stored in profile_<uuid>.json

4. **Recent Sessions Cache**
   - Ultimi 50 outcome in profile (FIFO)
   - Query veloci "ultime partite"
   - Storico completo in file separato

5. **SessionOutcome Immutabile**
   - Write-once (append-only)
   - Audit trail completo
   - No modifiche retroattive

### 🔮 Decisioni Rimandate (Future)

1. **Backup Automatici**
   - v3.1: Backup giornalieri in data/backups/
   - Compressione ZIP vecchi dati

2. **Conversione Ospite**
   - v3.1: "Salva ospite come nuovo profilo"
   - Migrazione sessions_guest.json → profile_new.json

3. **Achievement System**
   - v3.2: Badge per milestone (10/50/100 vittorie)
   - Unlock condizioni speciali (vittoria <5min, ecc.)

4. **Export/Import Profili**
   - v3.2: Condivisione profili tra PC
   - Format standard JSON per portabilità

5. **Cloud Sync**
   - v4.0: Sync profili tra dispositivi (opzionale)

---

## 🚧 Limiti del Documento

Questo documento:
- ❌ **Non definisce implementazione tecnica** (classi esatte, metodi)
- ❌ **Non definisce UI dettagliata** (wxPython widgets, layout)
- ❌ **Non definisce testing strategy** (unit test specifici)

Serve come **base logica** per:
- `IMPLEMENTATION_PROFILE_SYSTEM.md` (piano implementazione dettagliato)
- Developer handoff a GitHub Copilot Agent

---

## 🔗 Integrazione con Sistemi Esistenti

### Timer System v2.7.0 (Dependency)

**SessionOutcome dipende da Timer System**:
```python
# Campi popolati da Timer System
end_reason: EndReason           # Enum definito in timer design
timer_expired: bool
overtime_duration: float
```

**Sequenza implementazione consigliata**:
1. Profile System v3.0 (infrastruttura storage)
2. Timer System v2.7 (popola campi profilo)
3. Statistiche UI v3.1 (visualizza dati completi)

### Scoring System v2.0 (Integration)

**SessionOutcome usa FinalScore esistente**:
```python
# Campi da FinalScore (già implementato)
final_score: int
base_score: int
difficulty_multiplier: float
quality_multiplier: float
```

**Nessuna modifica necessaria** a ScoringService (già compatibile).

### GameService (Data Source)

**SessionOutcome legge da GameService**:
```python
# Campi già tracciati
move_count: int
draw_count: int
recycle_count: int
foundation_cards: List[int]
```

**Nessuna modifica necessaria** a GameService (già espone dati).

---

## 📊 Piano Implementazione Stimato

### GitHub Copilot Agent Performance

Basato su commit storici (PR #64, #66, v2.6.0):
- **Commit atomici**: 5-15 minuti per modifiche complesse
- **JSON storage**: Pattern già noto (ScoreStorage)
- **Test coverage**: 88-91% automatico

### Fasi Implementazione

| Fase | Modifiche | Commit | Tempo | Test |
|---|---|---|---|---|
| **1. Data Models** | `UserProfile`, `SessionOutcome`, Stats dataclasses | 1 | 10-15 min | 4-6 |
| **2. Storage Service** | `ProfileStorage`: JSON read/write/index | 1-2 | 15-25 min | 8-10 |
| **3. Profile Manager** | `ProfileService`: CRUD operations | 1-2 | 15-25 min | 10-12 |
| **4. Session Recording** | Integration GameEngine → ProfileService | 1 | 10-15 min | 6-8 |
| **5. Stats Aggregation** | Incremental update logic | 1 | 10-15 min | 8-10 |
| **6. UI Menu** | Gestione Profili submenu (wxPython) | 1-2 | 20-30 min | 4-6 |
| **7. Guest Mode** | Special profile logic | 1 | 8-12 min | 4-5 |
| **TOTALE** | | **8-11** | **88-137 min** | **44-57** |

**Stima Realistica**: Copilot Agent completa feature in **1.5-2.5 ore**.

---

## ✅ Stato del Design

- [x] Data model completo (UserProfile, SessionOutcome, Stats)
- [x] Persistenza strategia definita (JSON ibrido)
- [x] UI flows descritti (5 scenari)
- [x] Guest mode specificato
- [x] Integrazione con timer/scoring systems
- [x] Accessibilità TTS rispettata
- [x] Stime implementazione realistiche

**Design logicamente completo e pronto per implementazione.**

---

## 📚 Riferimenti

- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)
- **Versione Corrente**: v2.6.1 (16 Febbraio 2026)
- **Timer Design**: [DESIGN_TIMER_MODE_SYSTEM.md](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/docs/DESIGN_TIMER_MODE_SYSTEM.md)
- **Scoring System**: [FinalScore v2.0](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/src/domain/models/scoring.py)

---

**Documento creato**: 17 Febbraio 2026, 09:20 CET  
**Autore**: Luca (utente) + Perplexity AI (design/analisi)  
**Prossimo Step**: `IMPLEMENTATION_PROFILE_SYSTEM.md` (piano tecnico dettagliato)
