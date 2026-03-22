versione: v1.5.0
parole_chiave:
  - RELEASE

descrizione: |
  Prompt per l'operazione di release del framework. Obiettivo: consolidare la
  sezione `[Unreleased]` presente in `.github/FRAMEWORK_CHANGELOG.md` in una
  nuova voce di release `v1.5.0` datata oggi (22 marzo 2026). Questo prompt è
  pensato per l'agente `Agent-Release` o per l'operatore umano che esegue la
  release.

istruzioni: |
  1. Apri `.github/FRAMEWORK_CHANGELOG.md` e individua la sezione `## [Unreleased]`.
  2. Se la sezione contiene contenuti, sposta tutto il contenuto sotto una nuova
     intestazione `## [v1.5.0] - 2026-03-22` mantenendo la formattazione delle
     sottosezioni (Added, Changed, Fixed, ecc.). Rimuovi la sezione `[Unreleased]`
     oppure lascia una intestazione vuota se preferito dal maintainer.
  3. Aggiorna i metadati rilevanti in `.github/AGENTS.md` e `.github/copilot-instructions.md`
     sostituendo eventuali riferimenti a `v1.5.0` precedenti o a `[Unreleased]` con
     la nuova versione quando applicabile.
  4. Non eseguire operazioni git automaticamente: lascia i cambiamenti pronti per
     la review e commit da parte del maintainer. Includi nel messaggio di commit
     la riga `chore(framework): release v1.5.0` (conventional-commit).

note_operatore: |
  - Verifica che il contenuto spostato non introduca duplicati o conflitti di
    formattazione nel changelog.
  - Se sono presenti voci collegate nelle note di rilascio del progetto, ricordarsi
    di aggiornare anche gli altri file di documentazione se necessario.

output_atteso: |
  - `.github/FRAMEWORK_CHANGELOG.md` con una nuova sezione `## [v1.5.0] - 2026-03-22`
    contenente il contenuto precedentemente sotto `[Unreleased]`.
  - Modifiche preparate in `.github/AGENTS.md` e `.github/copilot-instructions.md`
    se applicabili.
---
mode: agent
description: Consolida [Unreleased] in una versione rilasciata del framework.
---

# Framework Release

Sei Agent-FrameworkDocs. Prepara il rilascio di una nuova versione del framework.

Esegui in sequenza:

1. Leggi `.github/FRAMEWORK_CHANGELOG.md` — contenuto sezione [Unreleased]
2. Leggi `.github/AGENTS.md` — versione corrente
3. Verifica prerequisiti bloccanti:
   - [Unreleased] non è vuoto (almeno una voce presente)
   - Nessun task di framework in corso non completato
   Se un prerequisito fallisce: mostra errore e interrompi.
4. Raccogli la versione target: ${input:Versione da rilasciare (es. v1.4.0)}
5. Mostra piano completo PRIMA di scrivere:
   - Voci [Unreleased] che diventano la nuova versione
   - Nuova intestazione: `## [X.Y.Z] — YYYY-MM-DD`
   - Aggiornamenti proposti in AGENTS.md (versione + data)
   - Aggiornamenti proposti in copilot-instructions.md (versione)
   - Comandi git proposti (NON eseguiti):
     git add .github/
     git commit -m "chore(framework): release vX.Y.Z"
     git tag framework-vX.Y.Z
6. Attendi conferma esplicita con parola chiave RELEASE
7. Scrivi le modifiche ai file
8. Mostra report finale
