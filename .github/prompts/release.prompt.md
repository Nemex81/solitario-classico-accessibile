---
name: Release
description: >
  Avvia Agent-Release per versioning, build e coordinamento release.
---

Avvia Agent-Release per la versione ${input:Versione da rilasciare (es: v3.6.0)}.

Prerequisiti da verificare PRIMA di procedere:
1. Leggi CHANGELOG.md -- la sezione [UNRELEASED] e presente e completa?
2. Verifica che tutti i PLAN attivi abbiano status READY o siano completati
3. Verifica che docs/TODO.md non abbia fasi [ ] non completate

Se un prerequisito non e soddisfatto: blocca e comunica cosa manca.
Se tutti OK: segui il Workflow Release in .github/agents/Agent-Release.md.
