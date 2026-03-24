---
applyTo: "**"
---

# Gate Inizializzazione Progetto — Framework Copilot

## Condizione di attivazione

Questo gate si attiva quando `.github/project-profile.md`
contiene `initialized: false` oppure il file non esiste.

## Comportamento obbligatorio

INTERROMPI qualsiasi altra operazione e comunica
questo messaggio all'utente, senza modifiche:

---
Questo framework non è ancora configurato per il progetto
corrente.

Prima di procedere con qualsiasi operazione esegui
il setup iniziale:

  1. Scrivi  #project-setup  nella chat
  2. Seleziona  project-setup.prompt.md  dal file picker
  3. Segui il percorso guidato (circa 2 minuti)

Il setup configura il framework per il tuo stack tecnico
specifico e abilita tutti gli agenti per il tuo progetto.
---

## Eccezione

L'unico agente autorizzato a operare con
`initialized: false` è Agent-Welcome.
Quando il contesto attivo è Agent-Welcome,
questo gate è sospeso.

## Riferimento

Trigger globale in: `.github/copilot-instructions.md`
sezione "Contesto Progetto"
