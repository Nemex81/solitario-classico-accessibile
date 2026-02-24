📋 TODO – Espansione eventi audio (parità vecchia versione)
Branch: supporto-audio-centralizzato
Tipo: Feature / Audio
Priorità: HIGH (Copertura sonoro)
Stato: READY for implementation

---

📖 Piano di riferimento:
- [3 - coding plans/audio_event_expansion_plan.md](3%20-%20coding%20plans/audio_event_expansion_plan.md)

Obiettivo: portare la versione wx dell'applicazione alla stessa ricchezza
sonora della vecchia release pygame. Aggiungere 21 eventi mancanti, aggiornare
`audio_config.json` e inserire chiamate `AudioEvent` in tutti i punti di UI e
gameplay identificati dal piano.

---

### Fase 1 – Definizione eventi (15 min)
- [x] Aggiungere 21 costanti mancanti in `src/infrastructure/audio/audio_events.py`
- [x] Assicurarsi che il modulo esporti tutte le costanti nuove (aggiungere in `__all__` se presente)
- [x] Scrivere test unitari base (`test_audio_events.py`) che verificano l'esistenza di ogni nuovo valore

### Fase 2 – Configurazione completa (30 min)
- [x] Sostituire/aggiornare la sezione `event_sounds` in `config/audio_config.json` con la mappatura completa riportata nel piano
- [x] Aggiungere i relativi flag sotto `enabled_events` come mostrato nel piano
- [x] Verificare che il loader supporti tutte le nuove chiavi (unit test già esistenti)
- [x] Aggiungere test per validare la configurazione estesa e `preload_all_event_sounds`

### Fase 3 – Inserimenti nel codice (2‑3 h)
_Suddividere per area per mantenere commit atomici_:
1. UI navigazione e dialoghi (menu, frame, anteprima pile, conferme, abort)
2. Gameplay core (movimenti carte singolo/multiplo, carte esaurite, flip, rimescola)
3. Gestione partita (nuova partita/mischia, distribuzione, benvenuto localizzato)
4. Impostazioni (salvataggio, livelli, volume, musica, switch)
5. Menu e pulsanti (apertura/chiusura, click, hover)
6. Verifica che eventi già esistenti non siano rotti

Per ciascuna sottosezione:
- aggiornare controller/handler wx con chiamate `audio_manager.play_event(...)`
- aggiungere unit test che simulano l'evento e controllano che `AudioManager`
  riceva la richiesta corrispondente

### Fase 4 – Testing e regressione (1 h)
- [x] Tests generali per ogni nuovo evento (46 test audio passano)
- [x] Esecuzione completa suite audio: 46 passed
- [x] Verificare che non ci siano errori o warning inattesi

### Fase 5 – Documentazione & cleanup (30 min)
- [ ] Aggiornare `README.md` (nessuna sezione eventi — non richiede modifiche)
- [x] Aggiornare sezione in `API.md` per i nuovi eventi sonori (v3.5.0+)
- [ ] Aggiornare `docs/ARCHITECTURE.md` (facoltativo)
- [x] Integrare nota nel `CHANGELOG.md` per la versione successiva

### Fase 6 – Verifica finale (15 min)
- [x] `mypy` su file modificati (no nuovi errori introdotti)
- [x] 46 test audio tutti verdi, 77 failing pre-esistenti non aggravati
- [x] Aggiornare `docs/TODO.md` spuntando le caselle

---

🗂️ File principali toccati:
- `src/infrastructure/audio/audio_events.py`
- `config/audio_config.json`
- controllers wx (`presentation/wx_ui/*`, `controllers/*`)
- `tests/unit/infrastructure/audio/test_audio_events.py`
- `tests/unit/*` per controller modificati
- `docs/` per aggiornamenti

---

*Autore: AI Assistant – 24 Febbraio 2026*
✅ Criteri di completamento:
- Tutte le checkbox delle fasi completate
- Tutti i test (vecchi e nuovi) passano senza regressioni
- Documentazione e CHANGELOG aggiornati

---

**NOTE:** Il piano di riferimento è la fonte di verità. Ogni modifica deve
riferirsi esplicitamente agli esempi di codice indicati nel piano. Procedere per
commit atomici per ognuna delle sotto‐aree della Fase 3.  
