---
type: prompt
name: scf-check-updates
description: Controlla aggiornamenti dei pacchetti SCF installati senza modificare il workspace.
---

Obiettivo: verificare se i pacchetti SCF installati hanno aggiornamenti disponibili.

Istruzioni operative:
1. Esegui `scf_update_packages()`.
2. Non modificare file o stato del workspace.
3. Mostra il piano di update calcolato dal tool, senza applicarlo.
4. Mostra un report chiaro con questi gruppi:
   - `up_to_date`
   - `update_available`
   - `not_in_registry`
   - `blocked_*` o `metadata_unavailable` se presenti
5. Se non ci sono pacchetti installati, dillo in modo esplicito.

Formato risposta:
- Sintesi iniziale (quanti pacchetti analizzati, quanti aggiornamenti disponibili).
- Elenco per stato.
- Sezione `Piano di update` con ordine previsto e dipendenze intra-plan.
- Sezione `Blocchi` se il tool restituisce impedimenti all'applicazione.
- Prossimo passo suggerito: usare `/scf-update` per applicare gli aggiornamenti.