# 📋 TODO — Sistema Logging Categorizzato (v3.2.0)

Branch: `sistema-log-categorizzati`  
Tipo: `FEATURE`  
Priorità: `MEDIUM`  
Stato: `DONE`

---

## 📖 Riferimento Documentazione

Prima di iniziare qualsiasi fase, consultare obbligatoriamente entrambi i file:

- **Design (logica e flussi)**: [docs/2 - projects/DESIGN_categorized_logging.md](2%20-%20projects/DESIGN_categorized_logging.md)
- **Piano tecnico (codifica step-by-step)**: [docs/3 - coding plans/PLAN_categorized_logging.md](3%20-%20coding%20plans/PLAN_categorized_logging.md)

Questo file TODO è il cruscotto operativo. I due file sopra sono la fonte di verità tecnica.

---

## 🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi sezione pertinente in `PLAN_categorized_logging.md`
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta checkbox completate per la fase
6. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni fase**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/5]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

---

## 🎯 Obiettivo Implementazione

Sostituire il sistema di logging monolitico (`solitario.log`) con un sistema multi-file categorizzato in stile Paradox Interactive. Ogni tipo di evento scrive in un file dedicato (`game_logic.log`, `ui_events.log`, `errors.log`, `timer.log`), mantenendo l'API pubblica **completamente invariata**. Zero modifiche a `acs_wx.py` e alla suite di test esistenti. Strategia: Low-Risk Multi-Handler su named loggers Python già esistenti.

---

## 📂 File Coinvolti

- `src/infrastructure/logging/categorized_logger.py` → **CREATE** (~130 righe)
- `src/infrastructure/logging/logger_setup.py` → **MODIFY** (thin wrapper + re-export)
- `src/infrastructure/logging/__init__.py` → **MODIFY** (+2 righe export)
- `src/infrastructure/logging/game_logger.py` → **MODIFY** (5 righe: timer logger + fix keyboard)
- `CHANGELOG.md` → **UPDATE** (entry `[Unreleased]`)

---

## 🛠 Checklist Implementazione

### Fase 1 — Crea `categorized_logger.py` (file nuovo)
> Ref: PLAN Step 1 | Crea `src/infrastructure/logging/categorized_logger.py`

- [x] Costanti `LOGS_DIR`, `LOG_FILE`, `CATEGORIES`, `LOG_FORMAT`, `LOG_DATE_FORMAT` definite
- [x] Funzione `setup_categorized_logging(logs_dir, level, console_output)` implementata
- [x] Handler `RotatingFileHandler` creato per ogni categoria (5MB, backupCount=3, UTF-8)
- [x] `propagate = False` impostato su ogni named logger (evita duplicazioni)
- [x] Root logger configurato su `solitario.log` per library logs (wx, PIL, urllib3)
- [x] Guard anti-doppia-registrazione (`if logger.handlers: continue`) presente
- [x] Console handler opzionale (`console_output=True`) funzionante
- [x] Librerie esterne mute a WARNING (`PIL`, `urllib3`, `wx`)

### Fase 2 — Modifica `logger_setup.py` (thin wrapper)
> Ref: PLAN Step 2 | Sostituisce contenuto con re-export per backward compatibility

- [x] Import da `categorized_logger` (setup_categorized_logging, LOGS_DIR, LOG_FILE)
- [x] `setup_logging()` è thin wrapper su `setup_categorized_logging()`
- [x] `get_logger(name)` mantenuto invariato
- [x] Docstring aggiornata con nota DEPRECATED + versione v3.2.0

### Fase 3 — Modifica `__init__.py` (aggiungi export)
> Ref: PLAN Step 3 | Aggiunge 2 righe export

- [x] `setup_categorized_logging` esportato
- [x] `LOGS_DIR` e `LOG_FILE` esportati
- [x] `__all__` aggiornato

### Fase 4 — Modifica `game_logger.py` (5 righe)
> Ref: PLAN Step 4 | _timer_logger + fix keyboard_command

- [x] `_timer_logger = logging.getLogger('timer')` aggiunto dopo `_error_logger`
- [x] `timer_started()` usa `_timer_logger.info()`
- [x] `timer_expired()` usa `_timer_logger.warning()`
- [x] `timer_paused()` usa `_timer_logger.debug()`
- [x] `keyboard_command()` usa `_ui_logger.debug()` (fix incongruenza esistente)

### Fase 5 — Verifica e aggiornamento docs
> Ref: PLAN Step 6–7

- [x] Patch target `_timer_logger` verificato — nessun test patch `_game_logger` per funzioni timer (i match erano proprietà di sessione, non logger)
- [x] `CHANGELOG.md` aggiornato con entry `[Unreleased] - Added`
- [ ] `pytest tests/unit/infrastructure/logging/ -v` → tutti pass (da eseguire localmente)
- [ ] `pytest tests/ -v` completo → nessuna regressione (da eseguire localmente)
- [ ] Avvio manuale app → 5 file in `logs/` (da verificare localmente)

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [x] Tutti gli step 1–5 completati e modifiche applicate
- [x] `CHANGELOG.md` aggiornato
- [ ] Avvio manuale app → 5 file presenti in `logs/` (game_logic, ui_events, errors, timer, solitario)
- [ ] Nessun contenuto duplicato tra file log
- [ ] Tutti i test esistenti passano senza modifiche

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [x] Aggiornare `CHANGELOG.md` con entry dettagliata (sezione `[Unreleased] - Added`)
- [ ] Versione: **MINOR** (v3.1.x → v3.2.0) — nuova feature retrocompatibile
- [ ] Push su branch `sistema-log-categorizzati`
- [ ] Aprire PR verso `main` con descrizione feature

---

## 📌 Note Operative

- `backupCount` passa da **5** (legacy in `logger_setup.py`) a **3** (allineato al design)
- Il formato log cambia da `%(asctime)s - %(levelname)s - %(name)s - %(message)s` a `%(asctime)s [%(levelname)s] %(message)s` (più leggibile con NVDA)
- `LOGS_DIR.mkdir(exist_ok=True)` si sposta da `logger_setup.py` (esecuzione a import-time) a dentro `setup_categorized_logging()` (esecuzione esplicita)
- Le categorie `profile`, `scoring`, `storage` sono commentate in `CATEGORIES` — pronte per attivazione futura senza altre modifiche

---

**Fine.**

Cruscotto operativo aggiornato al: 2026-02-21 (codifica completata, in attesa verifica locale)  
Fonte di verità: `PLAN_categorized_logging.md` + `DESIGN_categorized_logging.md`
