📋 TODO – [Feature/Fix Name] (vX.Y.Z)
Branch: [nome-branch]
Tipo: [FEATURE | FIX | REFACTOR | ENHANCEMENT]
Priorità: [HIGH | MEDIUM | LOW]
Stato: [READY | IN PROGRESS | DONE | BLOCKED]

---

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`docs/[NOME_FILE_PIANO_COMPLETO].md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici, architettura, edge case della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta checkbox completate per la fase
6. **Acquisisci info sommarie** → Rivedi stato globale prima di proseguire
7. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni fase**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/M]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

**Esempio workflow reale:**
```
Fase 1: Domain Model
→ Implementa + Commit + Aggiorna TODO ✅

Fase 2: Domain Service  
→ Rileggi piano completo sezione Fase 2
→ Implementa + Commit + Aggiorna TODO ✅

Fase 3: Application Controller
→ Rileggi piano completo sezione Fase 3
→ Implementa + Commit + Aggiorna TODO ✅

... e così via per tutte le fasi
```

---

🎯 Obiettivo Implementazione

Breve descrizione in 3–5 righe:

- Cosa viene introdotto/modificato
- Perché viene fatto
- Impatto principale sul sistema

---

📂 File Coinvolti

- `path/to/file1.py` → CREATE / MODIFY / DELETE
- `path/to/file2.py` → MODIFY
- `tests/unit/test_feature.py` → CREATE
- `README.md` → UPDATE
- `CHANGELOG.md` → UPDATE

---

🛠 Checklist Implementazione

**Logica / Dominio**
- [ ] Modifica modello / entità
- [ ] Aggiornamento servizi / use case
- [ ] Gestione edge case previsti

**Application / Controller**
- [ ] Nuovi metodi aggiunti
- [ ] Metodi esistenti aggiornati
- [ ] Nessuna violazione Clean Architecture

**Infrastructure (se applicabile)**
- [ ] Persistenza aggiornata
- [ ] Eventi / handler modificati

**Presentation / Accessibilità**
- [ ] Messaggi TTS in italiano chiaro
- [ ] Nessuna informazione solo visiva
- [ ] Comandi accessibili via tastiera

**Testing**
- [ ] Unit test creati / aggiornati
- [ ] Tutti i test esistenti passano
- [ ] Nessuna regressione rilevata

---

✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le checklist sopra sono spuntate
- [ ] Tutti i test passano
- [ ] Nessuna regressione funzionale
- [ ] Versione aggiornata coerentemente (SemVer)

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `README.md` se la feature è visibile all'utente
- [ ] Aggiornare `CHANGELOG.md` con entry dettagliata
- [ ] Incrementare versione in modo coerente:
  - **PATCH** → bug fix
  - **MINOR** → nuova feature retrocompatibile
  - **MAJOR** → breaking change
- [ ] Commit con messaggio convenzionale
- [ ] Push su branch corretto

---

📌 Note

Eventuali note rapide operative (non sostituiscono il piano completo).

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo resta come fonte di verità tecnica. Questo è il cruscotto operativo.