---
name: project-reset
description: >
  Skill per resettare il profilo progetto (`.github/project-profile.md`) in
  modo sicuro e guidato. Effettua backup, applica l'azione scelta (elimina
  file o imposta `initialized: false`) e fornisce istruzioni per rilanciare
  il setup tramite `#project-setup`.
---

# Skill: Project Reset

## Scopo

Fornire un'operazione guidata, ripetibile e sicura per resettare lo stato
del profilo progetto. Questa skill NON esegue commit o push: delega le
operazioni git ad `Agent-Git` quando necessario.

## Flusso operativo

1. Mostra avviso di rischio e richiedi conferma esplicita: "RESET PROFILO".
2. Esegui backup locale del file ` .github/project-profile.md` in
   `.github/backups/project-profile.<ts>.md` (timestamp consigliato).
3. Offri due opzioni all'utente:
   - `elimina`: elimina ` .github/project-profile.md` (cancella file)
   - `initialized=false`: modifica il frontmatter impostando `initialized: false`
4. Dopo l'azione, istruisci l'utente a eseguire `#project-setup` per rigenerare
   il profilo, oppure offri di chiamare `Agent-Welcome` per procedere.

## Vincoli e note di sicurezza

- Qualsiasi scrittura su `.github/**` deve avvenire con `framework_edit_mode: true`.
- Se `framework_edit_mode: false` interrompi e guida l'utente a `#framework-unlock`.
- Raccomandare il backup e non eseguire operazioni distruttive senza conferma.
- Non eseguire automaticamente commit/push: mostra i comandi `git` suggeriti e
  delega l'esecuzione ad `Agent-Git` quando l'utente conferma.

## Esempio di comandi proposti (non eseguiti automaticamente)

```bash
# Backup (esegui manualmente o tramite Agent-Git):
cp .github/project-profile.md .github/backups/project-profile-$(date +%s).md

# Eliminare il file (proposto):
rm .github/project-profile.md

# Oppure: impostare initialized: false nel frontmatter
# (editor guidato preferibile per evitare errori YAML)
```

---