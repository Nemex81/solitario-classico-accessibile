---
type: prompt
name: scf-list-installed
description: Elenca i pacchetti SCF installati nel workspace attivo.
---

Obiettivo: mostrare cosa e gia installato localmente.

Istruzioni operative:
1. Esegui `scf_list_installed_packages()`.
2. Non modificare file o stato del workspace.
3. Mostra per ogni pacchetto:
   - `package`
   - `version`
   - `file_count`

Se non e installato nulla, rispondi chiaramente che il workspace non ha pacchetti SCF installati.