---
type: todo
feature: "[feature-slug]"
version: "vX.Y.Z"
status: READY
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

TODO - [Feature/Fix Name] (vX.Y.Z)
Branch: [nome-branch]
Tipo: [FEATURE | FIX | REFACTOR | ENHANCEMENT]
Priorita: [HIGH | MEDIUM | LOW]
Stato: [READY | IN PROGRESS | DONE | BLOCKED]

---

📖 Riferimento Documentazione
Consulta sempre il piano completo:
`docs/[NOME_FILE_PIANO_COMPLETO].md` – contiene analisi, architettura e dettagli.

Questo TODO è un cruscotto operativo: aggiornalo dopo ogni fase. Le regole
(documenti, workflow, commit, versioning) sono in `.github/copilot-instructions.md`.

---

🤖 Istruzioni per Copilot Agent

Segui il TODO Gate: lavora fase per fase, esegui un commit atomico e spunta la
corrispondente checkbox. Rileggi il piano prima di ogni passo.

⚠️ Promemoria veloce:
- Un commit per fase logica, messaggio conventional.
- Dopo ogni commit aggiorna questo TODO.
- Non implementare tutto in un unico colpo.

---

🎯 Obiettivo Implementazione

Breve descrizione (3–5 righe) di cosa, perché e impatto della modifica.

---

📂 File Coinvolti

- `path/to/file1.py` → CREATE / MODIFY / DELETE
- `path/to/file2.py` → MODIFY
- `tests/unit/test_feature.py` → CREATE
- `README.md` → UPDATE
- `CHANGELOG.md` → UPDATE

---

🛠 Checklist Implementazione (segna il necessario)

- Logica / Dominio: modello, servizi, edge case
- Application: controller, metodi
- Infrastructure: storage, eventi
- Presentation / Accessibilità
- Testing: unit/integrazione, nessuna regressione

---

✅ Criteri di Completamento

- Checklist spuntate, test verdi, nessuna regressione.
- Versioning e documenti aggiornati (README, CHANGELOG).

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

Aggiorna README/CHANGELOG, incrementa versione (seguendo la policy),
commit e push come da prassi.

---

📌 Note

Eventuali note rapide operative (non sostituiscono il piano completo).

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo resta come fonte di verità tecnica. Questo è il cruscotto operativo.