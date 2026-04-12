---
type: prompt
name: scf-status
description: Mostra una panoramica completa dello stato SCF del workspace attivo.
---

Obiettivo: mostrare lo stato SCF corrente in una vista unica.

Istruzioni operative:
1. Esegui `scf_get_workspace_info()`.
2. Esegui `scf_list_installed_packages()`.
3. Esegui `scf_update_packages()`.
4. Opzionale: se l'utente richiede una verifica di coerenza cross-component, esegui `scf_verify_system()` e riporta eventuali `issues` e `warnings`.
5. Non modificare file o stato del workspace.

Formato risposta:
- Sezione `Workspace`: root attiva, initialized, engine_version e installed_packages (elenco pacchetti installati con le rispettive versioni).
- Sezione `Asset SCF`: conteggi agent/skill/instruction/prompt.
- Sezione `Pacchetti installati`: package, versione, numero file.
- Sezione `Aggiornamenti`: up_to_date, update_available, not_in_registry e blocchi eventuali.
- Se il tool restituisce un piano di update valido, mostra anche l'ordine di applicazione previsto.
- Se non ci sono pacchetti installati, dillo esplicitamente.