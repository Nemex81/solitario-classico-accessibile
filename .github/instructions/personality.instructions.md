---
applyTo: ".github/**"
---

# Personality — Postura Conversazionale

## Regola generale

Prima di produrre output conversazionale in un componente del framework,
risolvi il valore di personality seguendo la cascata definita in:
→ `.github/skills/personality.skill.md`

## Sorgenti del valore

- Valore globale: campo `personality` in `.github/project-profile.md`
- Override di sessione: richiesta verbale esplicita dell'utente nella
  chat corrente; non richiede scrittura su file
- Override agente: dichiarazione `Personalita` del file agente attivo

## Vincoli

- Non ridefinire i profili in questa instruction: usa la skill
- Non duplicare la logica della cascata oltre il minimo necessario
- Personality e verbosity sono assi ortogonali e indipendenti
- In caso di conflitto prevalgono policy, guardie e regole obbligatorie