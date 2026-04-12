---
type: prompt
name: scf-list-available
description: Elenca i pacchetti SCF disponibili nel registry pubblico.
---

Obiettivo: mostrare i pacchetti disponibili senza modificare il workspace.

Istruzioni operative:
1. Esegui `scf_list_available_packages()`.
2. Non modificare file o stato del workspace.
3. Ordina i risultati per `id`.

Per ogni pacchetto mostra:
- `id`
- `description`
- `latest_version`
- `status`

Se il registry non e raggiungibile, mostra errore esplicito e nessuna azione successiva.