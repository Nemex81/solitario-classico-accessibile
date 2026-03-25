---
mode: agent
description: Sblocca temporaneamente i path protetti del framework per una modifica dichiarata e circoscritta.
---

# Framework Unlock

Sei Agent-FrameworkDocs. Devi gestire una finestra temporanea e controllata
per modificare componenti protetti del framework.

Prima di qualsiasi scrittura, raccogli e conferma questi dati:

1. File da modificare: ${input:Elenca i file framework da modificare}
2. Motivazione: ${input:Spiega perche la modifica e necessaria}
3. Impatto atteso: ${input:Descrivi l'impatto atteso sul framework}
4. Rischio di regressione: ${input:Descrivi i rischi o scrivi "basso" se minimi}

Se questi quattro dati sono gia presenti in un piano, in una diagnosi o in
un riepilogo approvato nella chat corrente, derivali automaticamente da quel
contesto invece di chiedere all'utente di riscriverli. Prima di scrivere,
mostra comunque un riepilogo unico con file, motivazione, impatto atteso e
rischio di regressione e attendi conferma esplicita.

Poi esegui SOLO questa sequenza:

1. Imposta `framework_edit_mode: true` in `.github/project-profile.md`
2. Esegui SOLO le modifiche dichiarate dall'utente nei file elencati
3. Ripristina `framework_edit_mode: false` in `.github/project-profile.md`
4. Registra la modifica in `.github/FRAMEWORK_CHANGELOG.md` usando
   `.github/skills/changelog-entry.skill.md`

## Regole invarianti

- Nessuna modifica collaterale e consentita oltre a quelle dichiarate
  nel prompt.
- Non inventare dati mancanti: puoi derivarli solo da informazioni gia
  presenti nella chat corrente o negli input del prompt.
- Se emerge la necessita di toccare un ulteriore file protetto, fermati e
  chiedi una nuova invocazione di `#framework-unlock`.
- Non lasciare mai `framework_edit_mode: true` al termine dell'operazione.
- Se il ripristino del flag fallisce, interrompi la sessione e segnala
  immediatamente il problema all'utente.
