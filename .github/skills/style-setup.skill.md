---
name: style-setup
description: >
  Skill condivisa per la presentazione e selezione guidata dei
  parametri `verbosity` e `personality`. Definisce il formato di output
  per mostrare i valori correnti, le opzioni disponibili e il
  branching salta/personalizza. Usata da Agent-Welcome in OP-1
  per la personalizzazione opzionale, e da Agent-Helper in modalità
  informativa read-only. La sezione di scrittura è autorizzata
  solo per Agent-Welcome durante OP-1 o OP-2.
used_by:
  - Agent-Welcome
  - Agent-Helper
---

# Skill: Style Setup (verbosity & personality)

Scopo: fornire un contratto comune per la presentazione informativa
dei valori `verbosity` e `personality` e per la raccolta interattiva
e la scrittura controllata di questi campi in `.github/project-profile.md`.

---

## Sezione 1 — Presentazione informativa (usabile da tutti)

Regole:
- Leggere sempre i valori da `.github/project-profile.md` prima di mostrarli.
- Non mostrare valori hardcoded o presunti.
- Non modificare file in questa sezione.

Formato di output esatto (usare questo blocco):

  STILE COMUNICATIVO — Valori correnti
  ──────────────────────────────────────────
  verbosity   : <valore corrente>
    densità informativa e scaffolding delle risposte
    valori disponibili: tutor | collaborator | nerd

  personality : <valore corrente>
    postura operativa e stile relazionale degli agenti
    valori disponibili: mentor | pragmatico | reviewer | architect
  ──────────────────────────────────────────

Uso previsto:
- Invocare questa sezione quando si vuole mostrare i valori correnti
  senza effettuare scritture (es. `Agent-Helper`, help generico).

---

## Sezione 2 — Selezione e scrittura (solo Agent-Welcome in OP-1/OP-2)

Prerequisiti obbligatori:
- Questa sezione è autorizzata SOLO se invocata da `Agent-Welcome`
  durante OP-1 (quando `initialized: false`) o OP-2.
- Durante OP-1 la scrittura su `.github/project-profile.md` è
  autorizzata implicitamente da Agent-Welcome; in altri contesti
  NON eseguire questa sezione.

Sequenza procedurale:

1. Mostra il blocco informativo (Sezione 1) con i valori correnti.

2. Proponi la scelta con questo formato:

  PERSONALIZZAZIONE STILE — Opzionale
  ──────────────────────────────────────────
  Vuoi personalizzare lo stile comunicativo adesso?
  Rispondi "personalizza" per scegliere i valori
  oppure "salta" per mantenere i default.
  ──────────────────────────────────────────

3. Se l'utente risponde "salta":
- Non modificare nulla.
- Comunicare: "Mantengo i valori correnti."
- Restituire il controllo all'agente chiamante.

4. Se l'utente risponde "personalizza":
- Chiedi `verbosity` (una domanda alla volta, attendi risposta):
  "Scegli il livello di verbosity: tutor | collaborator | nerd"
- Chiedi `personality`:
  "Scegli la personality: mentor | pragmatico | reviewer | architect"
- Mostra riepilogo con conferma nel formato:

  STILE COMUNICATIVO — Riepilogo modifiche
  ──────────────────────────────────────────
  verbosity   : <valore precedente>  →  <nuovo valore>
  personality : <valore precedente>  →  <nuovo valore>
  ──────────────────────────────────────────
  Confermi? "ok" per applicare / "annulla" per tornare
  ──────────────────────────────────────────

- Attendi "ok" prima di scrivere qualsiasi file.
- Se "ok": aggiornare i campi `verbosity` e `personality`
  in `.github/project-profile.md` — solo questi due campi.
- Se "annulla": non modificare nulla e restituire controllo.
- Dopo la scrittura comunicare: "Stile aggiornato. verbosity: <X> | personality: <Y>"

Limiti della Sezione 2:
- Non modificare file fuori da `.github/project-profile.md`.
- Non sovrascrivere campi diversi da `verbosity` e `personality`.
- Non eseguire né suggerire comandi git.
- Non interferire con `framework-guard` o altre guardie; la skill
  documenta il prerequisito di invocazione (Agent-Welcome OP-1/OP-2).

---

## Note implementative
- Usare parsing YAML robusto per aggiornare solo i campi target.
- Validare i valori forniti contro le liste canoniche prima di scrivere.
