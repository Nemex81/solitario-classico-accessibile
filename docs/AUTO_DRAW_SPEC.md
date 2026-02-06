# Auto-Draw Feature - Technical Specification

## Obiettivo
Implementare la funzionalità di pescata automatica dopo il rimescolamento degli scarti nel mazzo.

## Comportamento Attuale (v1.2.0)
Quando il giocatore preme D/P per pescare:
1. Se il mazzo ha carte → pesca normalmente
2. Se il mazzo è vuoto → rimescola gli scarti e **STOP** (richiede un'altra pressione di D/P)

## Comportamento Desiderato (v1.2.1+)
Quando il giocatore preme D/P per pescare:
1. Se il mazzo ha carte → pesca normalmente
2. Se il mazzo è vuoto → rimescola gli scarti e **pesca automaticamente** una carta

## Requisiti Funzionali

### RF1: Pescata Automatica Post-Rimescolamento
- **Trigger**: Rimescolamento completato con successo
- **Azione**: Esegui immediatamente una pescata dal mazzo appena rimescolato
- **Output**: Messaggio vocale combinato che include:
  - Conferma rimescolamento
  - Carta/e pescate automaticamente

### RF2: Gestione Edge Cases
- **Caso 1**: Scarti vuoti → Nessun rimescolamento possibile (comportamento esistente OK)
- **Caso 2**: Dopo rimescolamento il mazzo è vuoto → Annuncio appropriato, no crash
- **Caso 3**: Difficoltà draw > 1 → Pesca tutte le carte richieste dalla difficoltà

### RF3: Annunci Vocali
Messaggio deve comunicare chiaramente:
- Tipo di rimescolamento eseguito (inversione/shuffle)
- Numero di carte riciclate
- Carta/e pescate automaticamente

Esempio: "Rimescolato 15 carte in modalità inversione. Pescata automatica: 7 di Cuori"

## Requisiti Non Funzionali

### RNF1: Backwards Compatibility
- Non modificare firma metodi pubblici esistenti
- Mantenere compatibilità con sistema undo/redo
- Non alterare statistiche di gioco (conta_rimischiate già incrementato)

### RNF2: Accessibilità
- Screen reader deve leggere un singolo messaggio fluido
- Evitare messaggi ripetitivi o confusionari
- Tempo di lettura ragionevole (< 5 secondi)

### RNF3: Testing
- Almeno 3 test specifici per auto-draw
- Test con mock per isolamento componenti
- Coverage >= 85% per codice nuovo/modificato

## Approcci di Implementazione Possibili

### Approccio A: Chiamata Sequenziale
- Dopo `riordina_scarti()`, verificare se mazzo ha carte
- Se sì, invocare logica di pescata esistente
- Combinare messaggi vocali

### Approccio B: Callback Pattern
- `riordina_scarti()` accetta callback opzionale
- Callback eseguito se rimescolamento ha successo
- Maggiore flessibilità ma più complesso

### Approccio C: State Machine
- Aggiungere stato "AUTO_DRAW_PENDING"
- Gestire transizione dopo rimescolamento
- Più robusto ma overhead architetturale

## Metriche di Successo
- [ ] Auto-draw funziona in 100% dei casi con scarti non vuoti
- [ ] Zero crash con edge cases
- [ ] Messaggio vocale chiaro e conciso
- [ ] Test passano al 100%
- [ ] Utente risparmia 1 pressione tasto per ciclo di rimescolamento

## Note di Implementazione
- Il metodo `pesca()` è il punto di ingresso principale
- Il metodo `execute_draw()` contiene logica di pescata da riutilizzare
- Il metodo `riordina_scarti()` in `game_table.py` gestisce il rimescolamento
- Pile di gioco: 11=scarti, 12=mazzo riserve
- Difficoltà determina numero carte da pescare (1-3)
