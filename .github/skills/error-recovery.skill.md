---
name: error-recovery
description: >
  Procedura standardizzata di retry e escalata quando un subagente fallisce
  l'esecuzione di un task. Utilizzata dagli Orchestratori per gestire errori
  in modo coerente e prevedibile.
---

# Skill: Error Recovery — Retry e Escalata

## Principio generale

Quando un subagente invocato dall'Orchestratore fallisce nel completare il suo task,
non riprova autonomamente all'infinito. Segui questa procedura con numero massimo
di tentativi e escalata predefinita.

---

## Procedura di retry

### Tentativi disponibili: 2

1. **Primo tentativo:** Il subagente fallisce. Registra l'errore.
2. **Secondo tentativo:** Riinvoca il subagente con contesto incrementale:

   ```text
   Il tuo primo tentativo ha fallito perché: [errore specifico].
   Riprova con attenzione a: [suggerimento mirato].
   Output atteso: [specifica più dettagliata].
   ```

   Se il secondo tentativo fallisce anche, procedi direttamente a escalata.
   Non tentare una terza volta — la circolarità segnala un problema strutturale.

---

## Formato escalata all'utente

Dopo il secondo fallimento, comunica all'utente in questo formato:

```text
⚠️ ERRORE NEL SUBAGENTE
──────────────────────────────────────────
Agente fallito: <Agent-X>
Task: <descrizione breve task>
Tentativi completati: 2/2
Errore finale: <log errore conciso, max 2 righe>
──────────────────────────────────────────

Opzioni:
  [A] Salta il task — procedi senza risultato
  [B] Ritenta manualmente dopo aver fornito contesto aggiuntivo
  [C] Escalata a utente per diagnosi
```

Attendi conferma esplicita dell'utente prima di procedere.

---

## Regola invariante

Dopo il secondo fallimento, **l'agente NON riprova in autonomia** senza conferma utente.
La responsabilità passa all'utente.

---

## Quando applicare

Fasi orchestrator in cui un subagente invocato potrebbe fallire:

- Fase 1 (Agent-Analyze): fallimento analisi
- Fase 2 (Agent-Design): fallimento syntax DESIGN doc
- Fase 3 (Agent-Plan): fallimento syntax PLAN doc
- Fase 4 (Agent-CodeRouter): fallimento implementazione
- Fase 5 (Agent-Validate): fallimento test coverage
- Fase 6 (Agent-Docs): fallimento sync documentazione

Nessuna altra skill o procedura di retry si applica in questi contesti.
