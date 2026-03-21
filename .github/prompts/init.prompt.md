---
name: Init Task
description: >
  Avvia un nuovo task nel framework. Analizza la descrizione
  e suggerisce l'agente appropriato tra i 7 disponibili.
---

Analizza questa descrizione di task e suggerisci l'agente appropriato:

**Task**: ${input:Descrivi il task (es: aggiungi feedback audio alla schermata di fine partita)}

Esegui il seguente processo:
1. Identifica le keyword nella descrizione
2. Mappa alle categorie agente: Analyze/Design/Plan/Code/Validate/Docs/Release
3. Suggerisci l'agente con motivazione in 1 riga
4. Chiedi conferma: "Procedo con Agent-X? (yes / Agent-Y per override)"

Se la descrizione e ambigua, elenca i 2 agenti piu probabili e chiedi
quale preferisce l'utente.
