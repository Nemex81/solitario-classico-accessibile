---
type: prompt
name: scf-update
description: Applica aggiornamenti pacchetti SCF con conferma esplicita e preservazione file utente.
---

Obiettivo: aggiornare pacchetti installati mantenendo sempre i file user-modified.

Regola obbligatoria:
- Non applicare aggiornamenti finche l'utente non conferma in modo esplicito.

Istruzioni operative:
1. Esegui `scf_update_packages()` per individuare update disponibili.
2. Se non ci sono update, informa l'utente e termina senza modifiche.
3. Mostra il piano pre-azione usando `plan.order` restituito dal tool.
4. Per ogni package pianificato mostra:
   - package
   - versione installata
   - versione target
   - dipendenze che verranno aggiornate prima del package, se presenti
   - nota di preservazione file utente modificati
5. Se il piano contiene blocchi, mostrali e non proporre applicazione finche non sono risolti.
6. Chiedi conferma esplicita (es: "Confermi applicazione aggiornamenti? [si/no]").
7. Solo se l'utente conferma, esegui `scf_apply_updates()`.
8. Mostra esito finale con:
   - pacchetti aggiornati
   - pacchetti falliti
   - ordine effettivamente applicato
   - dettagli installati/preservati/errori

Se l'utente non conferma, interrompi senza modificare nulla.