---
type: prompt
name: scf-install
description: Installa un pacchetto SCF con conferma esplicita prima di modificare file.
---

Obiettivo: installare un pacchetto SCF in modo sicuro e trasparente.

Regola obbligatoria:
- Non eseguire installazione finche l'utente non conferma in modo esplicito.

Istruzioni operative:
1. Se manca il nome pacchetto, chiedi `package_id`.
2. Esegui `scf_get_package_info(package_id)` per costruire il riepilogo.
3. Mostra anteprima con:
   - package id e versione
   - numero file da installare
   - categorie coinvolte
4. Chiedi conferma esplicita con domanda chiusa (es: "Confermi installazione? [si/no]").
5. Solo se l'utente conferma, esegui `scf_install_package(package_id)`.
6. Mostra esito con:
   - file installati
   - file preservati per modifica utente
   - eventuali errori

Se l'utente non conferma, interrompi senza modificare nulla.