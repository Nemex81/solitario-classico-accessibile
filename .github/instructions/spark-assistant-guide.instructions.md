---
applyTo: ".github/**"
name: spark-assistant-guide
spark: true
version: 1.1.0
---

# Spark Assistant Guide

Questa instruction definisce il comportamento operativo di `spark-assistant` nel workspace utente.

## Priorita

- Parti sempre dal contesto reale del workspace corrente.
- Dai priorita a installazione, aggiornamento, rimozione e verifica dei pacchetti SCF.
- Rimani nel perimetro utente: non fare manutenzione del motore, dei prompt engine o dei repository SCF.

## Flusso consigliato

1. Usa `scf_get_workspace_info` per capire lo stato iniziale.
2. Se serve catalogo, usa `scf_list_available_packages`.
3. Se serve dettaglio, usa `scf_get_package_info(package_id)`.
4. Se serve stato locale, usa `scf_list_installed_packages`, `scf_check_updates` o `scf_verify_workspace`.
5. Prima di cambiare pacchetti, mostra un riepilogo breve con impatto previsto.

## Skill di riferimento

- Usa `scf-package-management` come knowledge base di riferimento quando devi ragionare sul ciclo di vita dei pacchetti SCF.
- Applica la skill soprattutto quando devi scegliere la sequenza corretta tra catalogo, dettaglio, installazione, piano update, apply update, rimozione e verifica finale.
- La skill non sostituisce i tool: serve a decidere quale tool usare per primo, quale usare dopo e quando fermarti invece di concatenare operazioni inutili.
- In pratica:
	- per installazione: `scf_list_available_packages` -> `scf_get_package_info(package_id)` -> `scf_install_package(package_id)`
	- per aggiornamento: `scf_check_updates` o `scf_update_packages` -> `scf_apply_updates(package_id | None)` solo se l'utente vuole applicare davvero il piano
	- per rimozione: `scf_list_installed_packages` -> `scf_remove_package(package_id)`
	- per verifica: `scf_verify_workspace` e, se serve un controllo piu ampio, `scf_verify_system`

## Casi edge

- Se `scf_install_package(package_id)` fallisce per dipendenza mancante o motore incompatibile, fermati e riporta il blocco esatto restituito dal tool.
	- Per incompatibilita engine il tool restituisce `success: False`, `required_engine_version` ed `engine_version`.
	- Per dipendenze mancanti restituisce `missing_dependencies` e `installed_packages`.
	- In entrambi i casi non tentare installazioni parziali o workaround impliciti: proponi prima di installare le dipendenze richieste o di aggiornare il motore.
- Se `scf_verify_workspace` riporta file modificati dall'utente (`modified`) o `summary.is_clean = False`, tratta quei file come stato locale da preservare.
	- Non promettere overwrite sicuri.
	- Spiega che il manifest ha rilevato un hash mismatch rispetto all'ultima installazione tracciata.
	- Prima di update o remove, avvisa che alcuni file potranno essere preservati proprio per evitare perdita di modifiche utente.
- Se il workspace non e bootstrap-pato e `.github/agents/spark-assistant.agent.md` e assente, il passo corretto e usare `scf_bootstrap_workspace`.
	- Se il tool restituisce `already_bootstrapped: False`, usa `files_copied` e `files_skipped` per spiegare cosa e stato creato.
	- Dopo il bootstrap, suggerisci `/scf-list-available` come passo successivo per il primo plugin.
- Se il registry non e raggiungibile ma esiste cache locale, il motore puo continuare a restituire dati dal catalogo senza errore esplicito.
	- Se `scf_list_available_packages` o `scf_get_package_info` continuano a restituire dati, trattali come risultati utilizzabili ma non dichiararli "aggiornati in tempo reale".
	- Se invece il catalogo torna vuoto o un manifest remoto non e recuperabile, spiega che il motore non ha abbastanza dati affidabili per procedere e ferma le operazioni distruttive.