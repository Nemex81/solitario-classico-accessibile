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
