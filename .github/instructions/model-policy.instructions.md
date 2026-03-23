---
applyTo: ".github/**"
---

# Model Policy — Framework Copilot

Questa istruzione è attiva automaticamente su tutti i file `.github/`.
Consultala quando ti viene chiesto quale modello usare per un dato agente
o tipo di task, o quando devi valutare la coerenza di una configurazione.

## Assegnazioni agenti

Nota: il fallback è espresso come secondo elemento dell'array `model`
nel frontmatter degli agenti, non come chiave separata.

| Agente | model (array ordinato) |
|--------|-------------------------|
| Agent-Orchestrator | ['GPT-5.4 (copilot)', 'Claude Opus 4.6 (copilot)'] |
| Agent-Analyze | ['Claude Sonnet 4.6 (copilot)', 'GPT-5.4 (copilot)'] |
| Agent-Design | ['Claude Opus 4.6 (copilot)', 'GPT-5.4 (copilot)'] |
| Agent-Plan | ['Claude Sonnet 4.6 (copilot)', 'GPT-5.4 (copilot)'] |
| Agent-Code | ['Claude Sonnet 4.6 (copilot)', 'GPT-5.3-Codex (copilot)'] |
| Agent-Validate | ['GPT-5.3-Codex (copilot)', 'Claude Sonnet 4.6 (copilot)'] |
| Agent-Docs | ['GPT-5 mini (copilot)', 'Raptor mini (copilot)'] |
| Agent-Release | ['GPT-5 mini (copilot)', 'Raptor mini (copilot)'] |
| Agent-FrameworkDocs | ['Claude Sonnet 4.6 (copilot)', 'GPT-5 mini (copilot)'] |
| Agent-Git | ['GPT-5 mini (copilot)', 'Raptor mini (copilot)'] |

## Criteri di selezione per tipo di task

- **Reasoning architetturale e decisioni E2E**: gpt-5.4 o claude-opus-4.6
- **Analisi codebase, design e planning strutturato**: claude-sonnet-4.6
- **Coding generale e review**: claude-sonnet-4.6
- **Task agentic puro, test, coverage, refactor pipeline**: gpt-5.3-codex
- **Task meccanici, formali, ripetitivi**: gpt-5-mini o raptor-mini
- **Contenere il consumo premium**: gpt-5-mini (0x), raptor-mini (0x),
  gpt-5.4 (1x), claude-sonnet-4.6 (1x), claude-opus-4.6 (3x)

## Modelli da evitare come base per nuove regole

I seguenti modelli sono in deprecazione o legacy:
gpt-4o, gpt-4.1, gpt-5.1, gpt-5.1-codex, gpt-5.1-codex-mini,
gpt-5.1-codex-max, gemini-3-pro

## Fallback ufficiali per modelli deprecati

- gpt-4o → gpt-5-mini
- gpt-4.1 → gpt-5-mini
- gemini-3-pro → gemini-3.1-pro
- gpt-5.1* → gpt-5.3-codex
- claude-sonnet-4 → claude-sonnet-4.6
- claude-opus-4.5 → claude-opus-4.6
