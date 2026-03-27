---
applyTo: ".github/**"
---

# Instruction: Project Reset

Questa instruction descrive il comportamento atteso quando un agente o una
skill devono resettare il profilo progetto (`.github/project-profile.md`).

## Regole operative

- Prima di ogni operazione, verifica `framework_edit_mode` in
  `.github/project-profile.md`.
  - Se `false`: interrompi e indirizza l'utente a `#framework-unlock`.
  - Se `true`: procedi solo entro il perimetro dichiarato.

- Usa la skill `project-reset` per eseguire il flusso di reset guidato.
- Esegui sempre un backup del file prima di cancellare o modificare il
  frontmatter.
- Non eseguire commit/push automaticamente: proponi i comandi git o delega
  ad `Agent-Git` per l'esecuzione (con conferme richieste da Agent-Git).

## Messaggi e conferme

- Richiedi conferma esplicita dell'utente con la frase "RESET PROFILO"
  prima di procedere con azioni distruttive.
- Registra sempre l'azione nel `.github/FRAMEWORK_CHANGELOG.md` come voce
  di audit (mostra al terminare la procedura la voce proposta).

## Esempio di integrazione

Agent-Welcome può offrire l'opzione "Reset profilo progetto" che, dopo
aver raccolto conferme e aver eseguito il backup, chiama `project-reset`.

---