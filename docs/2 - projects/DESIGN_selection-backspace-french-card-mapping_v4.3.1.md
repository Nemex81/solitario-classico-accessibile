---
type: design
feature: selection-backspace-french-card-mapping
version: v4.3.1
status: REVIEWED
agent: Agent-Design
date: 2026-04-10
---

# DESIGN: Selection Backspace French Card Mapping v4.3.1

## 1. Idea in 3 righe

I pathway gameplay hanno tre incoerenze funzionali che impattano accessibilita e prevedibilita: il tasto di annullamento selezione usa ancora Delete invece di Backspace, una nuova selezione viene spesso bloccata invece di sostituire quella attiva con feedback utile, e il mapping delle carte francesi deve restare allineato agli asset numerici senza contaminare il branch napoletano. La proposta unifica il comando di cancellazione intorno a Backspace, introduce una semantica esplicita di selection replacement con annuncio vocale descrittivo, e concentra la normalizzazione dei rank francesi nel layer infrastructure dedicato alle immagini. Il risultato atteso e un gameplay piu coerente per tastiera e NVDA, con regressione controllata sul rendering dei due mazzi.

---

## 2. Comportamento Utente Atteso

### 2.1 Gameplay da tastiera

- Durante la partita, Backspace annulla la selezione corrente in tutti i pathway gameplay che oggi dipendono da CANCEL_SELECTION.
- Delete non deve piu essere il tasto documentato o il binding primario del flusso partita.
- I messaggi di help, hint e feedback vocale devono nominare Backspace in modo coerente con il binding reale.

### 2.2 Sostituzione selezione

- Se l'utente ha gia una selezione attiva e seleziona un'altra carta o sequenza valida, il sistema non deve rispondere con un blocco generico.
- La selezione esistente deve essere sostituita in modo atomico con la nuova.
- L'annuncio vocale deve descrivere l'evento completo, per esempio: selezione precedente annullata, nuova selezione composta da N carte, elenco o carta target.
- La stessa semantica deve valere sia per la selezione da tableau sia per la selezione dalla pila scarti, evitando differenze arbitrarie tra pathway manuali e pathway di auto-selection gia presenti.

### 2.3 Rendering carte francesi

- Quando il mazzo attivo e francese, i rank emessi dal dominio come Asso, Jack, Regina e Re devono risolversi sugli asset numerici 1, 11, 12 e 13 presenti in assets/img/carte_francesi.
- Quando il mazzo attivo e napoletano, il mapping esistente sequenziale deve restare invariato e isolato.
- In caso di asset francese mancante, il fallback visuale o testuale gia previsto deve continuare a funzionare senza crash.

---

## 3. Attori e Concetti

### Attori software coinvolti

- src/application/input_handler.py: punto di verita dei binding tastiera gameplay e degli AudioEvent associati ai comandi semantici.
- src/domain/services/selection_manager.py: stato della selezione e feedback di dominio oggi ancora orientato al blocco se esiste una selezione attiva.
- src/application/game_engine.py: orchestration dei pathway di selezione manuale, selezione da scarti e jump-to-pile con auto-selection gia capace di cancellazione preventiva.
- src/presentation/game_formatter.py: help e testo guida annunciato all'utente, da riallineare al nuovo tasto e alla nuova semantica.
- src/infrastructure/ui/card_image_cache.py: boundary corretto per tradurre rank e suit del dominio nei filename degli asset visuali.
- src/infrastructure/ui/gameplay_panel.py: superficie di integrazione che consuma CardImageCache e rende osservabile la regressione o il successo del fix immagini.

### Concetti chiave

- Comando semantico stabile: CANCEL_SELECTION resta il comando applicativo, cambia il tasto fisico che lo attiva.
- Selection replacement: la nuova selezione e un rimpiazzo esplicito della precedente, non un errore di stato.
- Voice-first feedback: il messaggio deve spiegare sia la cancellazione implicita sia il nuovo target selezionato.
- Mapping isolato per deck type: il branch francese normalizza rank legacy verso filename numerici; il branch napoletano continua a usare la propria risoluzione dedicata.

---

## 4. Flussi Concettuali

### 4.1 Flusso attuale da correggere

```text
Backspace premuto
  -> nessun binding gameplay primario

Selezione gia attiva + nuova selezione manuale
  -> SelectionManager ritorna messaggio di blocco
  -> l'utente deve annullare manualmente prima di riprovare

Richiesta bitmap carta francese
  -> CardImageCache riceve rank dominio
  -> la correzione dipende dalla normalizzazione dei rank legacy
  -> se la normalizzazione non copre tutti i casi, l'asset non viene trovato
```

### 4.2 Flusso proposto

```text
Backspace premuto
  -> InputHandler emette GameCommand.CANCEL_SELECTION
  -> pathway gameplay annulla la selezione
  -> NVDA annuncia conferma coerente con il nuovo tasto documentato

Selezione gia attiva + nuova selezione manuale
  -> GameEngine rileva selezione esistente
  -> cancella la selezione attiva in modo controllato
  -> prova la nuova selezione
  -> costruisce un unico messaggio descrittivo
  -> NVDA annuncia il risultato completo

Richiesta bitmap carta francese
  -> CardImageCache riconosce deck_type=french
  -> normalizza rank legacy in numero file
  -> carica assets/img/carte_francesi/{rank_num}-{suit}.jpg
  -> deck_type=neapolitan continua sul loader dedicato senza shared mapping improprio
```

### 4.3 Nota di coerenza architetturale

Il replacement della selezione non deve introdurre logica di UI nel dominio. Il dominio puo esporre primitive piu neutrali per clear e select, ma la composizione del messaggio contestuale e la decisione di sostituzione appartengono al layer application, che conosce il pathway utente e il timing dell'annuncio vocale.

---

## 5. Punti di Estensione nel Codice

### 5.1 Binding tastiera e feedback input

- src/application/input_handler.py
  - aggiornare _initialize_bindings() per mappare Backspace a CANCEL_SELECTION;
  - riallineare docstring e commenti del comando;
  - mantenere invariato il contratto GameCommand per evitare ripple inutile.

### 5.2 Semantica di selezione

- src/domain/services/selection_manager.py
  - ridurre il coupling tra stato interno e messaggio di blocco;
  - valutare una primitiva esplicita per clear senza testo prescrittivo oppure una variante di select che non imponga il blocco applicativo.
- src/application/game_engine.py
  - usare un pathway comune per tableau e waste che gestisca replacement, nuova selezione e composizione del messaggio finale;
  - riallineare il comportamento manuale con jump_to_pile(), dove una cancellazione preventiva esiste gia ma va resa piu descrittiva e uniforme.

### 5.3 Help e annunci

- src/presentation/game_formatter.py
  - aggiornare help summary e help detailed da CANC a Backspace;
  - evitare disallineamento tra testo guida, binding reale e annunci runtime.

### 5.4 Mapping immagini francesi

- src/infrastructure/ui/card_image_cache.py
  - mantenere la normalizzazione dei rank francesi in un solo punto;
  - validare esplicitamente gli alias legacy Asso, Jack, Regina, Re contro i filename numerici osservabili nella cartella assets/img/carte_francesi;
  - non condividere questa normalizzazione con _load_source_napoletane().
- src/infrastructure/ui/gameplay_panel.py
  - usare questo pannello come smoke surface per verificare che il fix del mapping produca bitmap corrette nel rendering effettivo.

---

## 6. Strategia Accessibilita NVDA

- Annuncio unificato: ogni replacement deve produrre una sola frase utile, non due messaggi concorrenti che si interrompono a vicenda.
- Ordine del contenuto: prima la cancellazione implicita della vecchia selezione, poi la nuova selezione, poi eventuale dettaglio carta target.
- Lessico operativo stabile: Backspace deve comparire in help, hint e messaggi d'errore o conferma in modo consistente.
- Interrupt controllato: i pathway gameplay che gia usano speak con interrupt devono evitare doppia emissione ravvicinata dello stesso evento semantico.
- Nessun silenzio ambiguo: sostituire il blocco con un annuncio descrittivo evita il caso in cui l'utente non capisca se la nuova selezione sia fallita o sia stata ignorata.
- Compatibilita cognitiva: i messaggi devono restare brevi sul caso nominale, ma sufficientemente descrittivi nel caso replacement, dove il contesto cambia senza input esplicito di annullamento.

---

## 7. Strategia Per Verificare e Correggere il Mapping Francese Senza Rompere il Napoletano

### 7.1 Principio di isolamento

- Il mapping francese va corretto solo nel branch french di CardImageCache.
- Il loader napoletano deve restare separato, con le proprie regole sequenziali e il proprio dorso.
- Nessuna funzione comune deve introdurre conversioni che cambiano i rank napoletani o i filename del mazzo italiano.

### 7.2 Matrice minima di verifica francese

- Asso di cuori -> 1-cuori.jpg
- Jack di picche -> 11-picche.jpg
- Regina di fiori -> 12-fiori.jpg
- Re di quadri -> 13-quadri.jpg
- Rank numerico puro, per esempio 7 di fiori -> 7-fiori.jpg

### 7.3 Matrice minima di non regressione napoletana

- Asso di bastoni continua a risolversi nel loader napoletano dedicato.
- Re di bastoni continua a usare la numerazione sequenziale napoletana gia supportata.
- Il dorso 41_Carte_Napoletane_retro.jpg continua a essere caricato solo per deck_type=neapolitan.

### 7.4 Criterio di implementazione

- Centralizzare gli alias legacy francesi in una mappa o normalizer privata dedicata.
- Non basarsi su assunzioni di naming prese dal dominio francese, ma sui filename reali presenti nella cartella asset.
- Se emergono discrepanze future negli asset francesi, aggiungere alias nel normalizer invece di piegare il dominio o il renderer.

---

## 8. Decisioni Architetturali

### 8.1 Backspace come nuovo binding primario

Decisione: spostare il binding gameplay di CANCEL_SELECTION da Delete a Backspace senza rinominare il comando semantico.

Motivazione: il cambiamento richiesto e di ergonomia e accessibilita, non di semantica applicativa. Conservare CANCEL_SELECTION evita refactor laterali inutili.

### 8.2 Replacement orchestrato nel layer application

Decisione: la sostituzione di selezione deve essere decisa nel game engine o in un pathway applicativo equivalente, non hardcodata come policy testuale nel dominio.

Motivazione: il layer application possiede il contesto del flusso utente, della voce NVDA e dei diversi pathway di selezione. Il dominio deve rimanere concentrato sullo stato della selezione.

### 8.3 Normalizzazione rank francesi confinata in infrastructure

Decisione: il mapping Asso/Jack/Regina/Re -> 1/11/12/13 resta nel componente che traduce il modello dominio in nomi file asset.

Motivazione: e un problema di boundary con il filesystem, non di dominio. Portarlo altrove aumenterebbe il rischio di duplicazioni e regressioni.

### 8.4 Uniformita tra selezione manuale e auto-selection

Decisione: i pathway manuali devono convergere semanticamente verso il comportamento gia introdotto in jump_to_pile(), ma con messaggi piu robusti e riusabili.

Motivazione: due meccaniche diverse per la stessa azione mentale dell'utente producono confusione, soprattutto con screen reader.

---

## 9. Rischi e Vincoli

- Rischio di regressione input: alcune abitudini utente o test possono ancora usare Delete; serve una decisione esplicita se mantenerlo come alias temporaneo o rimuoverlo del tutto.
- Rischio di doppio annuncio NVDA: se il clear della vecchia selezione e la nuova select parlano separatamente, il messaggio diventa rumoroso o troncato.
- Rischio di regressione dominio: spostare troppo comportamento in SelectionManager puo reintrodurre accoppiamento tra stato e UX testuale.
- Rischio di regressione visuale francese: una normalizzazione incompleta puo rompere solo alcune figure, rendendo il bug intermittente.
- Rischio di contaminazione tra mazzi: una funzione condivisa troppo aggressiva puo alterare il naming napoletano, che segue regole diverse.
- Vincolo architetturale: Presentation non deve incorporare business logic di selezione; Infrastructure non deve conoscere decisioni di gameplay oltre la traduzione verso asset.

---

## 10. Test Strategy

### 10.1 Test unitari input e help

- Aggiornare tests/unit/application/test_input_handler_audio.py per verificare che Backspace attivi CANCEL_SELECTION e che il feedback audio resti associato al comando corretto.
- Aggiungere o aggiornare test sui formatter per assicurare che l'help gameplay annunci Backspace e non Delete.

### 10.2 Test unitari selection replacement

- Estendere tests/domain/services/test_selection_manager.py solo per le primitive di stato, evitando di spostare in dominio asserzioni troppo UI-centriche.
- Aggiungere test application sul pathway di selezione in game engine per coprire:
  - selezione semplice senza selezione preesistente;
  - replacement da tableau a tableau;
  - replacement da scarti a tableau o viceversa;
  - annuncio descrittivo unico prodotto dopo replacement.

### 10.3 Test integrazione gameplay con NVDA semantics

- Verificare che jump_to_pile() e la selezione manuale convergano sullo stesso modello di feedback.
- Coprire il caso in cui una selezione preesistente venga rimpiazzata senza blocco e senza perdita della nuova selezione.

### 10.4 Test unitari mapping immagini

- Estendere tests/unit/test_card_image_cache.py con casi espliciti per i rank legacy francesi Asso, Jack, Regina e Re.
- Conservare i test gia esistenti sul branch napoletano come guard rail di non regressione.
- Usare fixture filesystem temporanee per rendere esplicito il contratto filename -> bitmap senza dipendere dagli asset reali del repository.

### 10.5 Smoke test manuale finale

- Avvio partita con mazzo francese: selezione, replacement, annuncio NVDA, rendering di Asso e figure.
- Avvio partita con mazzo napoletano: rendering delle carte e del dorso, nessuna regressione nel caricamento bitmap.
- Verifica help in partita: il tasto annunciato per annullare deve essere Backspace.

---

## 11. Esito Atteso

Il gameplay diventa piu coerente per utenti tastiera e screen reader: Backspace sostituisce Delete nel percorso reale e documentato, una nuova selezione non viene piu rifiutata quando esiste gia una selezione attiva ma la rimpiazza con annuncio comprensibile, e il mapping delle carte francesi resta corretto rispetto agli asset visuali senza introdurre regressioni nel branch napoletano.
