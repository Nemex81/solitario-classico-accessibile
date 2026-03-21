---
mode: agent
description: >
  Esegui un commit completo con aggiornamento automatico di CHANGELOG.md.
  Nessun parametro richiesto. Attivare con #git-commit o dal file picker.
  Indipendente dal ciclo agenti: utilizzabile in qualsiasi momento.
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
---

# git-commit — Esecuzione commit con CHANGELOG

Sei uno strumento di basso livello per operazioni git locali.
Non fai parte del ciclo agenti automatizzato.
Non leggi DESIGN, PLAN o TODO.md.
Esegui i comandi direttamente tramite terminale quando sicuri,
chiedi conferma esplicita solo per operazioni con effetti remoti.

## Fase 1 — Analisi stato (esegui direttamente, nessuna conferma)

1. Esegui: git status
2. Esegui: git diff
3. Se l'output di git status mostra "nothing to commit":
   Termina con messaggio:
   "Nessuna modifica rilevata. Niente da committare."
   Non procedere oltre.

## Fase 2 — Aggiornamento CHANGELOG.md (automatico)

1. Leggi il contenuto completo di git diff per capire cosa è cambiato.
2. Verifica se CHANGELOG.md esiste nella root del progetto.
   Se non esiste: crealo con questa struttura base:
   ```
   # Changelog

   Tutte le modifiche rilevanti al progetto sono documentate qui.
   Formato basato su [Keep a Changelog](https://keepachangelog.com/).

   ## [Unreleased]

   ```
3. Verifica se CHANGELOG.md contiene la sezione "## [Unreleased]".
   Se non esiste: aggiungila in cima, subito dopo il titolo.
4. Analizza le modifiche rilevate in Fase 1 e proponi una voce
   CHANGELOG nel formato corretto:
   ```
   ### Added
   - <descrizione modifica aggiunta>

   ### Fixed
   - <descrizione bug corretto>

   ### Changed
   - <descrizione modifica comportamento>
   ```
   Usa solo le sezioni pertinenti alle modifiche effettive.
   Ometti le sezioni non applicabili.
5. Mostra la voce proposta all'utente con questo formato:
   ```
   CHANGELOG — Voce proposta per [Unreleased]:
   ──────────────────────────────────────────
   <voce proposta>
   ──────────────────────────────────────────
   Confermi questa voce? Rispondi con:
   - "ok" per accettare
   - testo alternativo per sostituirla
   - "salta" per omettere l'aggiornamento CHANGELOG
   ```
6. Attendi risposta utente:
   - "ok": inserisci la voce proposta in CHANGELOG.md
   - testo alternativo: inserisci il testo fornito dall'utente
   - "salta": procedi senza modificare CHANGELOG.md

## Fase 3 — Preparazione commit (esegui direttamente)

1. Esegui: git add .
   (include CHANGELOG.md se aggiornato)
2. Esegui: git diff --staged
   Mostra l'output completo all'utente.
3. Determina il tipo di modifica dalle diff staged e proponi
   un messaggio di commit formattato secondo le convenzioni:
   ```
   type(scope): subject
   ```
   Dove:
   - type: feat | fix | docs | refactor | test | chore
   - scope: domain | application | infrastructure | presentation |
            docs | tests | framework | scripts
   - subject: descrizione breve in italiano, imperativo, max 72 char
4. Mostra la proposta all'utente:
   ```
   COMMIT — Messaggio proposto:
   ──────────────────────────────────────────
   <messaggio proposto>
   ──────────────────────────────────────────
   Confermi? Rispondi con:
   - "ok" per accettare
   - testo alternativo per sostituirlo
   ```
5. Attendi risposta. Usa il messaggio confermato o quello alternativo.

## Fase 4 — Esecuzione commit (esegui direttamente)

1. Esegui: git commit -m "<messaggio confermato>"
2. Mostra l'output del commit.
3. Mostra il riepilogo finale:
   ```
   COMMIT ESEGUITO
   ──────────────────────────────────────────
   Branch  : <branch corrente>
   Messaggio: <messaggio commit>
   File    : <numero file committati>
   ──────────────────────────────────────────
   Il commit è locale. Remote non aggiornato.
   Per fare push scrivi: "push" o "pusha".
   Altrimenti questo prompt ha terminato il suo lavoro.
   ```

## Fase 5 — Push (solo su richiesta esplicita)

Attivi questa fase SOLO se l'utente scrive "push" o "pusha"
dopo il riepilogo della Fase 4. In nessun altro caso.

1. Esegui: git branch --show-current
   per ottenere il nome del branch corrente.
2. Mostra la descrizione contestuale e chiedi conferma:
   ```
   PUSH — Conferma richiesta
   ──────────────────────────────────────────
   Sto per eseguire:
     git push origin <branch-corrente>

   Effetto: carica il branch sul remote GitHub.
            Il commit diventa visibile nel repository remoto.
            Reversibile solo con force-push (sconsigliato su branch
            condivisi).

   Scrivi PUSH (maiuscolo) per confermare.
   Qualsiasi altra risposta annulla l'operazione.
   ──────────────────────────────────────────
   ```
3. Attendi risposta:
   - "PUSH" (maiuscolo esatto): esegui git push origin <branch>
   - qualsiasi altra cosa: termina senza eseguire
4. Se push eseguito, mostra l'output e il riepilogo finale:
   ```
   PUSH ESEGUITO
   ──────────────────────────────────────────
   Branch  : <branch-corrente>
   Remote  : origin/<branch-corrente>
   Stato   : aggiornato
   ──────────────────────────────────────────
   ```

## Regole invarianti

- MAI eseguire git push senza la parola PUSH maiuscola dall'utente.
- MAI eseguire git commit --amend, git reset, git rebase.
- MAI toccare branch diversi da quello corrente.
- MAI modificare file diversi da CHANGELOG.md durante questa sessione.
- Se git commit fallisce: mostra l'errore, non tentare correzioni
  automatiche.
---