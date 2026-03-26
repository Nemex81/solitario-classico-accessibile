---
agent: agent
description: >
  Modifica il livello di verbosita comunicativa globale degli agenti
  aggiornando il campo verbosity in project-profile.md.
  Per override temporaneo di sessione non usare questo prompt:
  dichiara il livello desiderato direttamente in chat.
---

# Verbosity

Sei un prompt operativo dedicato alla modifica del solo campo `verbosity`
in `.github/project-profile.md`. Non estendi la tua competenza ad altri
campi del profilo progetto.

## Operazione supportata

`set-global`

## Sequenza obbligatoria

1. Leggi `.github/project-profile.md` e verifica `framework_edit_mode`.
2. Se `framework_edit_mode: false`, blocca l'operazione, mostra i file
   richiesti e indirizza l'utente a `#framework-unlock`.
3. Se `framework_edit_mode: true`, leggi e mostra il valore attuale di
   `verbosity`.
4. Chiedi il nuovo valore: `tutor` | `collaborator` | `nerd`.
5. Mostra il riepilogo nel formato seguente:

```text
VERBOSITY — Modifica globale
──────────────────────────────────────────
Valore attuale : <valore>
Nuovo valore   : <valore>
──────────────────────────────────────────
Confermi? [si / no]
```

6. Attendi conferma esplicita dell'utente.
7. Aggiorna solo il campo `verbosity` in `.github/project-profile.md`.
8. Comunica il completamento con il nuovo valore attivo.

Non registrare questa operazione in `.github/FRAMEWORK_CHANGELOG.md`.
Il changelog del framework traccia l'evoluzione del framework,
non le regolazioni operative dell'utente.
