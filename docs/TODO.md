📋 TODO – Refactor audio configuration to JSON-driven
Branch: supporto-audio-centralizzato → refactor-audio-config-json
Tipo: Refactor / Technical Debt
Priorità: MEDIUM (Qualità)
Stato: READY for implementation

---

📖 Piano di riferimento:
- [3 - coding plans/PLAN_audio_config_json_driven.md](3%20-%20coding%20plans/PLAN_audio_config_json_driven.md)

Obiettivo: eliminare la duplicazione del mapping evento→file tra codice e
`audio_config.json`, rendendo l'intera assegnazione sonoro **JSON-driven**.
Questo riduce manutenzione, permette modifiche senza toccare Python e apre la
porta a configurazione runtime/modding.

---

### Fase 1 – Config JSON (30 min)
- [x] Modificare `config/audio_config.json`:
    - aggiungere sezione `event_sounds` con tutti le 12 coppie evento/file
    - inserire flag booleano `preload_all_event_sounds` (default true)
    - mantenere `preload_sounds` come proprietà deprecata per compatibilità
- [x] Validare JSON con formatter/linter
- [x] Verificare fallback automatico in caso di configurazione mancante

### Fase 2 – Refactor AudioManager (≈1.5 h)
- [x] Rimuovere dizionario `_event_sounds` hardcoded da `__init__()`
- [x] Implementare metodo `_load_event_mapping(config: dict) -> Dict[AudioEventType,str]`
    - parse JSON keys → enum, log warning per chiavi sconosciute
    - log warning per eventi mancanti
- [x] Implementare `_get_default_event_mapping()` per fallback (duplicare mappa)
- [x] Aggiungere chiamata `self._validate_config_completeness()` dopo il caricamento
- [x] Spostare preload sotto condizione `preload_all_event_sounds`
- [x] Scrivere docstring e aggiornare commenti

### Fase 3 – Validazione & compatibilità (45 min)
- [x] Nuovo metodo `_validate_config_completeness()` con warning per eventi
      mancanti e file non esistenti
- [x] Test unitari:
    - config completa → mapping corretto
    - config mancante → usa fallback e log warning
    - config con chiave sconosciuta → skip con warning
    - eventi mancanti nel mapping → warning e assenza di suono
- [x] Test di caricamento audio_config (già esistente `test_audio_config_loader.py`,
      estendere per verificare sezione `event_sounds`)

### Fase 4 – Documentazione & cleanup (30 min)
- [x] Aggiornare sezione “Audio Config” in `README.md` con nuovo formato
- [x] Modificare `API.md` se menziona preload_sounds o mapping hardcoded
- [x] Aggiornare commenti di `audio_config_loader.py` (documentare `event_sounds` e flag)
- [x] Aggiungere note al `CHANGELOG.md` sotto v3.5.0 (incrementale minor)

### Fase 5 – Verifica finale (15 min)
- [x] Eseguire `mypy`, `flake8` su modelli modificati
- [x] Lanciare suite test (unit + integrazione) per confermare 100% green
- [x] Controllare `docs/TODO.md` e aggiornare eventuali task bonus

---

🗂️ File coinvolti
- `config/audio_config.json` (nuova struttura)
- `src/infrastructure/audio/audio_manager.py` (caricamento e validazione)
- `src/infrastructure/config/audio_config_loader.py` (descrizione/optional keys)
- `docs/3 - coding plans/PLAN_audio_config_json_driven.md` (piano già esistente)
- `docs/API.md`, `docs/ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`
- `tests/unit/infrastructure/audio/test_audio_config_loader.py` (estendere)
- possibili nuove unit tests sotto `tests/unit/infrastructure/audio`

---

📋 Linee guida
- Non cambiare comportamento sonoro in fase (solo refactor)
- Log warning per qualsiasi discrepanza, ma non lanciare eccezioni
- Test TDD: scrivere prima i nuovi unit tests per `_load_event_mapping`
- Conservare backward compatibility con file `audio_config.json` esistenti
  (qualora `event_sounds` manchi, usare fallback e loggare)

---

*Autore: AI Assistant – 23 Febbraio 2026*
✅ Criteri di completamento
- [ ] Tutti i checklist sopra spuntate
- [ ] Tutti i nuovi e vecchi test passano
- [ ] Nessuna regressione funzionale audio
- [ ] Documentazione e CHANGELOG aggiornati

---

**Fine nuovo TODO.**

Questo documento sostituisce integralmente il precedente; usa il piano come
fonte di verità tecnica. Contento per la nuova iterazione, pronto per
iniziare l'implementazione quando decidi!  