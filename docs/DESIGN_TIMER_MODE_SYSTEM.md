# 🎨 DESIGN DOCUMENT
# Timer Mode & Time Outcome System

## 📌 Informazioni Generali

**Nome Feature**: Timer Mode & Time Outcome System  
**Versione Target**: v2.7.0  
**Stato**: Design Phase → Implementation Ready  
**Data Creazione**: 17 Febbraio 2026  
**Tipo**: Progettazione logico-concettuale validata su codebase v2.6.1

---

## 💡 Obiettivo della Modifica

Il sistema timer esistente definisce un limite temporale ma non influenza realmente lo stato della partita o le statistiche in modo strutturato.

**Questa modifica introduce**:
- La scadenza del tempo come **evento di gioco reale**
- Comportamento partita basato su **modalità timer** (STRICT/PERMISSIVE)
- Risultato registrato in modo **coerente** per statistiche e profili utente
- Il timer diventa **parte integrante dell'esito**, non solo informativo

---

## 🎯 Problema Attuale

### Stato Codice v2.6.1

**Nel sistema attuale** ([GameEngine](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/src/application/game_engine.py)):
- Timer è un valore configurabile (`max_time_game`)
- Scadenza **NON produce evento formalizzato**
- Commento esplicito: *"Timer countdown non ancora implementato"*
- Non esiste distinzione tra:
  - Partita conclusa entro tempo
  - Partita continuata oltre limite
  - Partita persa per tempo

**Impatto**:
- Statistiche inaffidabili (tempo non significativo)
- Confronto giocatori impossibile
- Timer non utilizzabile come parametro difficoltà reale

---

## 🧩 Concetti Fondamentali

### 1. Timer di Partita

Rappresenta il **tempo massimo previsto** per completare una partita.

**Stati**:
- **Disattivato**: `max_time_game <= 0`
- **Attivo**: Timer configurato e partita in corso
- **Scaduto**: `elapsed_time >= max_time_game` (evento unico)
- **Overtime**: Solo modalità PERMISSIVE, dopo scadenza

**Nota**: Il timer non è condizione di vittoria, ma può influenzare l'esito.

---

### 2. Modalità Timer

Determina il **comportamento del gioco quando il tempo scade**.

#### STRICT Mode
```
Tempo scaduto → Partita termina immediatamente
Esito: Sconfitta per tempo
```

**Caratteristiche**:
- Auto-stop alla scadenza
- Dialog finale con statistiche
- Nessun overtime possibile
- Comportamento competitivo/tournament

#### PERMISSIVE Mode
```
Tempo scaduto → Partita continua
Esito: Vittoria possibile, overtime tracciato
```

**Caratteristiche**:
- Continua gameplay dopo scadenza
- Overtime registrato come info statistica
- Malus scoring: -100pt/min (già implementato in v2.0)
- Comportamento learning/casual

**Implementazione Esistente**: `GameSettings.timer_strict_mode` (v1.5.2.2)
```python
self.timer_strict_mode = True  # STRICT (default)
self.timer_strict_mode = False # PERMISSIVE
```

---

### 3. Evento "Tempo Scaduto"

**Evento logico** che avviene quando:
```
elapsed_time >= max_time_game
```

**Caratteristiche**:
- Avviene **una sola volta** per partita
- Non può essere annullato
- Cambia stato timer: `Attivo` → `Scaduto`
- Trigger annuncio TTS (single-fire, no spam)

**Implementazione Necessaria**:
- Tick periodico (wx.Timer 1000ms)
- Flag `timer_expired: bool` in GameService
- Metodo `check_timer_expiry() -> bool`

---

### 4. Overtime

**Periodo di gioco successivo** alla scadenza del timer.

**Condizioni**:
- Esiste **solo in modalità PERMISSIVE**
- Inizia al momento della scadenza
- Termina con fine partita normale

**Dati Tracciati**:
```python
overtime_start: Optional[float] = None  # Timestamp inizio overtime
overtime_duration: float  # Calcolato: end_time - overtime_start
```

**Utilità**:
- Distinguere vittorie entro tempo da vittorie overtime
- Raccogliere dati statistici significativi
- Supportare classifiche per categoria

---

### 5. Esito Partita (Time-Aware)

L'esito finale deve includere la **causa di terminazione**.

#### End Reason Enum

```python
class EndReason(Enum):
    VICTORY = "victory"                    # Vittoria entro tempo
    VICTORY_OVERTIME = "victory_overtime"  # Vittoria oltre tempo (PERMISSIVE)
    ABANDON_NEW_GAME = "abandon_new_game"  # Abbandono via new game
    ABANDON_EXIT = "abandon_exit"          # Abbandono via ESC/menu
    ABANDON_APP_CLOSE = "abandon_app_close"  # Chiusura app implicita
    TIMEOUT_STRICT = "timeout_strict"      # Sconfitta per tempo (STRICT)
```

**Mapping Aggregati**:
- **Sconfitte**: `ABANDON_*` + `TIMEOUT_STRICT`
- **Vittorie**: `VICTORY` + `VICTORY_OVERTIME`
- **Abbandoni**: `ABANDON_*`
- **Timeout**: `TIMEOUT_STRICT` + `VICTORY_OVERTIME` (overtime flag)

---

## 🔄 Stati del Sistema

### Diagramma Transizioni

```
Timer Disattivato (max_time_game <= 0)
        ↓
        [Attivazione timer]
        ↓
Timer Attivo (elapsed < max_time_game)
        ↓
        [elapsed >= max_time_game]
        ↓
Timer Scaduto (evento unico, annuncio TTS)
        ↓
        ├─ [STRICT] → Fine Partita (Sconfitta)
        │
        └─ [PERMISSIVE] → Overtime
                          ↓
                          [Vittoria/Abbandono] → Fine Partita
```

### Tabella Stati

| Stato | Condizione | Azioni | Transizione |
|---|---|---|---|
| **Disattivato** | `max_time_game <= 0` | Nessun controllo tempo | → Attivo (config) |
| **Attivo** | `elapsed < limit` | Tick check 1000ms | → Scaduto (limit) |
| **Scaduto** | `elapsed >= limit` | TTS announce (1x), flag `timer_expired=True` | → Overtime o Fine |
| **Overtime** | Solo PERMISSIVE | Continua gameplay, tracking durata | → Fine (vittoria/abbandono) |

---

## 🎬 Scenari di Utilizzo

### Scenario A — Timer STRICT (Tournament)

```
1. Partita in corso, timer 15 minuti
2. Tempo raggiunge 15:00
3. Sistema rileva scadenza (tick check)
4. TTS: "Tempo scaduto!"
5. Partita termina immediatamente
6. Dialog finale: EndReason.TIMEOUT_STRICT
7. Statistiche registrate (no overtime)
```

**Contesto**: Livello 5 - Maestro (Tournament Mode)

---

### Scenario B — Timer PERMISSIVE (Learning)

```
1. Partita in corso, timer 30 minuti
2. Tempo raggiunge 30:00
3. Sistema rileva scadenza (tick check)
4. TTS: "Tempo scaduto! Il gioco continua con penalità."
5. overtime_start = current_time
6. Utente continua a giocare (mosse valide)
7. Vittoria dopo 3 minuti overtime
8. EndReason.VICTORY_OVERTIME, overtime_duration = 180s
9. Scoring: malus -300pt (3 min × 100pt)
```

**Contesto**: Livello 2 - Facile (casual play)

---

### Scenario C — Timer Disattivato

```
1. max_time_game = -1
2. Sistema ignora completamente dimensione temporale
3. Nessun tick check, nessuna scadenza
4. Vittoria: EndReason.VICTORY (classico)
5. Nessuna statistica timer generata
```

**Contesto**: Livello 1 - Principiante (free play)

---

### Scenario D — Abbandono con Timer Attivo

```
1. Partita in corso, timer 20 minuti
2. Elapsed: 12 minuti (entro limite)
3. Utente preme ESC → Conferma abbandono
4. EndReason.ABANDON_EXIT
5. Statistiche: elapsed_time = 720s, overtime = 0
6. Session cleanup (game_active = false)
```

---

### Scenario E — Chiusura App Implicita

```
1. Partita in corso (session: game_active=true)
2. Utente chiude app senza ESC/menu
3. SessionStorage: closed_cleanly = false
4. Avvio successivo: check_orphaned_session()
5. Rileva partita orfana, registra sconfitta
6. EndReason.ABANDON_APP_CLOSE
7. Session cleanup
```

---

## 👤 Impatto su Statistiche e Profili Utente

### Dati Logici per Aggregazione

Ogni partita deve produrre:

```python
{
    "end_reason": EndReason,           # Causa terminazione
    "timer_enabled": bool,             # Timer attivo sì/no
    "timer_limit": int,                # Limite timer (secondi)
    "timer_mode": str,                 # "STRICT" | "PERMISSIVE"
    "timer_expired": bool,             # Scadenza avvenuta
    "overtime_duration": float,        # Secondi oltre limite
    "elapsed_time": float,             # Tempo totale partita
    "is_victory": bool,                # Vittoria sì/no
    "final_score": int,                # Punteggio finale
}
```

### Statistiche Derivabili (Profili Futuri)

Con questi dati è possibile calcolare:

**Performance Timer**:
- % vittorie entro tempo vs overtime
- Tempo medio vittoria per categoria timer
- Tasso abbandono per timeout (STRICT)

**Confronto Difficoltà**:
- Performance STRICT vs PERMISSIVE
- Vittorie per livello difficoltà + timer
- Evoluzione skill (riduzione overtime nel tempo)

**Classifiche**:
- Leaderboard per tempo completamento
- Leaderboard per vittorie zero-overtime
- Tournament ranking (STRICT only)

---

## 🎧 Considerazioni di Accessibilità

### Principi Rispettati

1. **Annunci TTS Non Ripetuti**
   - Scadenza annunciata **una sola volta**
   - Flag `timer_expired` previene spam

2. **Nessuna Interruzione Aggressiva**
   - PERMISSIVE consente completamento partita
   - STRICT mostra dialog chiaro (no panic)

3. **Comunicazione Chiara**
   - Formatter dedicati (ScoreFormatter/GameFormatter)
   - Messaggi italiani screen-reader friendly

4. **Nessuno Spam Gameplay**
   - Tick check silenzioso (no TTS ogni secondo)
   - Countdown solo su richiesta (tasto T)

### Annunci TTS

**Scadenza Timer**:
```
"Tempo scaduto!" [STRICT + PERMISSIVE]
"Il gioco continua con penalità." [PERMISSIVE only]
```

**Overtime Warning** (opzionale, PERMISSIVE):
```
"Hai superato il tempo limite di X minuti."
[Solo al momento scadenza, no ripetizioni]
```

---

## ⚖️ Decisioni di Design

### ✅ Decisioni Confermate

1. **Scadenza = Evento Unico**
   - Flag `timer_expired` = True (irreversibile)
   - Annuncio TTS single-fire

2. **STRICT Termina Immediatamente**
   - `end_game(EndReason.TIMEOUT_STRICT)`
   - No overtime tracking

3. **PERMISSIVE Continua Gameplay**
   - Overtime tracking attivo
   - Scoring malus già implementato (v2.0)

4. **End Reason Obbligatorio**
   - Sostituisce `is_victory: bool` (troppo semplice)
   - Signature: `end_game(end_reason: EndReason)`

5. **Session Integrity**
   - Rilevamento chiusure implicite
   - Orphaned game cleanup all'avvio

### 🔮 Decisioni Rimandate (Future)

1. **Overtime Scoring Impact**
   - Attuale: -100pt/min malus
   - Futuro: Configurabile per livello difficoltà?

2. **Differenziazione UI Overtime**
   - Attuale: Solo dato statistico
   - Futuro: Badge/icona vittoria-overtime?

3. **Pre-Warning Timer**
   - Attuale: Solo annuncio scadenza
   - Futuro: Warning a 5/2/1 minuti rimanenti?

---

## 🚧 Limiti del Documento

Questo documento:
- ❌ **Non definisce implementazione tecnica** (codice, signature esatte)
- ❌ **Non definisce struttura dati completa** (attributi classe, JSON schema)
- ❌ **Non introduce nuovi moduli** (file paths, import statements)

Serve esclusivamente come **base logica** per la fase successiva:
- `IMPLEMENTATION_TIMER_MODE_SYSTEM.md` (piano implementazione dettagliato)

---

## 🔍 Validazione su Codebase v2.6.1

### Verifica Compatibilità

**Architettura Clean** ✅:
- Domain Layer: `GameService` (timer state, end reason)
- Application Layer: `GameEngine` (tick check, STRICT/PERMISSIVE logic)
- Infrastructure Layer: `SessionStorage` (persistence, cleanup)
- Presentation Layer: `ScoreFormatter` / `GameFormatter` (TTS announcements)

**Componenti Esistenti** ✅:
- `GameSettings.timer_strict_mode` → già implementato (v1.5.2.2)
- `GameService.start_time` / `elapsed_time` → già tracking tempo
- `GameEngine.end_game(is_victory)` → da estendere con `end_reason`
- `ScoringService._calculate_time_bonus()` → già gestisce overtime malus

**Zero Refactor Violenti** ✅:
- Estensione incrementale, no riscritture
- Backward compatible (wrapper deprecati per `is_victory`)
- Dependency Rule rispettata (no violazioni layer)

---

## 📊 Piano Implementazione Stimato

### GitHub Copilot Agent Performance

Basato su commit storici (PR #64, #66, v2.6.0):
- **Commit atomici**: 5-15 minuti per modifiche anche complesse
- **Test coverage**: 88-91% automatico
- **CHANGELOG**: Aggiornamento incluso
- **Log strutturati**: Integrazione automatica

### Fasi Implementazione

| Fase | Modifiche | Commit | Tempo | Test |
|---|---|---|---|---|
| **1. Timer State** | `GameService`: attrs + methods | 1 | 8-12 min | 3-4 |
| **2. End Reason** | `models/game_end.py`: enum | 1 | 3-5 min | 0 |
| **3. Tick Check** | `GameEngine`: wx.Timer periodico | 1 | 10-15 min | 5-6 |
| **4. Integration** | `end_game()` signature + calls | 1-2 | 12-18 min | 8-10 |
| **5. Session** | `SessionStorage`: persistence | 1 | 8-12 min | 4-5 |
| **6. TTS** | Formatters: announcements | 1 | 5-8 min | 2-3 |
| **TOTALE** | | **6-8** | **46-70 min** | **22-28** |

**Stima Realistica**: Copilot Agent completa feature in **45-70 minuti**.

---

## ✅ Stato del Design

- [x] Scenari definiti (5 scenari coperti)
- [x] Stati e transizioni chiari (4 stati formali)
- [x] Compatibile con scoring system v2.0
- [x] Compatibile con futuro sistema profili
- [x] Accessibilità TTS rispettata
- [x] Validato su codebase v2.6.1
- [x] Stime implementazione realistiche

**Design logicamente completo e pronto per implementazione.**

---

## 📚 Riferimenti

- **Codebase**: [refactoring-engine branch](https://github.com/Nemex81/solitario-classico-accessibile/tree/refactoring-engine)
- **Versione Corrente**: v2.6.1 (16 Febbraio 2026)
- **CHANGELOG**: [Keep a Changelog format](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/CHANGELOG.md)
- **ARCHITECTURE**: [Clean Architecture docs](https://github.com/Nemex81/solitario-classico-accessibile/blob/refactoring-engine/docs/ARCHITECTURE.md)

---

**Documento creato**: 17 Febbraio 2026, 01:30 CET  
**Autore**: Luca (utente) + Perplexity AI (analisi/validazione)  
**Prossimo Step**: `IMPLEMENTATION_TIMER_MODE_SYSTEM.md` (piano tecnico dettagliato)
