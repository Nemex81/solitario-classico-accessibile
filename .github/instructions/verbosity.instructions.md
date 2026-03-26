---
applyTo: ".github/**"
---

# Verbosity — Output Conversazionale

## Regola generale

Prima di produrre output conversazionale in un componente del framework,
risolvi il livello di verbosita seguendo la cascata definita in:
→ `.github/skills/verbosity.skill.md`

## Sorgenti del valore

- Valore globale: campo `verbosity` in `.github/project-profile.md`
- Override di sessione: richiesta verbale esplicita dell'utente nella
  chat corrente; non richiede scrittura su file
- Override agente: dichiarazione `Verbosita` del file agente attivo

## Vincoli

- Non ridefinire i profili in questa instruction: usa la skill
- Non duplicare la logica della cascata oltre il minimo necessario
- In caso di conflitto prevalgono policy, guardie e regole obbligatorie
