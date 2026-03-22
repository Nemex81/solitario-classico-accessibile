---
name: file-deletion-guard
description: >
  Procedura obbligatoria di guardia per qualsiasi operazione che
  elimina file o directory. Si applica a tutti gli agenti in tutti
  i contesti, inclusi merge con conflitti.
used_by:
  - Agent-Git
  - Agent-Code
  - Agent-FrameworkDocs
---

# file-deletion-guard — Skill

Scopo: garantire che nessun file venga eliminato senza esplicita
conferma dell'utente.

---

## Operazioni coperte

Questa skill si attiva SEMPRE prima di eseguire qualsiasi operazione
che comporti eliminazione di file, diretta o indiretta:

- Eliminazione di file (`git rm`, `os.remove`, `delete_file`, ecc.)
- `git clean` in qualsiasi forma
- Risoluzione di conflitti di merge che implica la rimozione di file
- Qualsiasi refactoring che rimuova file dal repository

---

## Procedura obbligatoria

Prima di procedere con qualsiasi operazione coperta:

1. Interrompi l'operazione corrente.
2. Mostra il blocco di conferma seguente:

   FILE IN ATTESA DI ELIMINAZIONE
   ──────────────────────────────────────────
   - <path/file1>
     Motivo : <motivazione tecnica esplicita>

   - <path/file2>
     Motivo : <motivazione tecnica esplicita>
   ──────────────────────────────────────────
   Scrivi ELIMINA (maiuscolo) per confermare TUTTE le eliminazioni.
   Scrivi ANNULLA per annullare TUTTE le operazioni.
   Per eliminazioni selettive: elenca i path da confermare.

3. Attendi risposta esplicita dell'utente.
4. In assenza di risposta o risposta diversa da ELIMINA: annulla tutto
   e notifica: "Operazione annullata. Nessun file eliminato."

---

## Regola invariante

Questa procedura NON può essere saltata, abbreviata o delegata.
Non esistono eccezioni automatiche, nemmeno durante merge,
refactoring o risoluzione conflitti.
