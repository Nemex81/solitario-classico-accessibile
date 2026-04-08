---
feature: gameplay-visual-ui
type: design
agent: Agent-Design
status: REVIEWED
version: v4.0.0
date: 2026-04-08
---

# DESIGN: Gameplay Visual UI

## 1. Idea in 3 righe

Trasformare la finestra di gameplay da interfaccia puramente audio/testuale a board visiva completa con rendering carte, layout solitaire classico (7 tableau, 4 foundation, stock, waste) e cursore grafico. L'interfaccia opera in dual-mode: modalita visiva per giocatori vedenti e ipovedenti (carte disegnate, highlight cursore, temi alto contrasto) e modalita audio-only per giocatori non vedenti (comportamento attuale preservato integralmente). L'accessibilita NVDA resta garantita in entrambe le modalita tramite due canali paralleli: TTS SAPI5 diretto per il feedback gameplay e accessible descriptions wx per la navigazione widget.

---

## 2. Attori e Concetti

### Attori umani

- Giocatore vedente: interagisce tramite tastiera, percepisce il board visivo con carte, colori e animazioni
- Giocatore ipovedente: interagisce tramite tastiera, beneficia di temi alto contrasto, font grande, bordi spessi e cursore lampeggiante
- Giocatore non vedente: interagisce tramite tastiera, riceve feedback esclusivamente via TTS SAPI5 e NVDA; la modalita audio-only e il default

### Attori software (esistenti)

- GameplayPanel (src/infrastructure/ui/gameplay_panel.py): panel wx che cattura input tastiera e ospita il board visivo; da ristrutturare
- GamePlayController (src/application/gameplay_controller.py): entry point comandi tastiera, orchestra logica di gioco e feedback TTS
- GameEngine (src/application/game_engine.py): facade del domain, espone stato di gioco (table, cursor, selection)
- ScreenReader (src/infrastructure/audio/screen_reader.py): canale TTS SAPI5 diretto
- BasicPanel (src/infrastructure/ui/basic_panel.py): base class con sizer, EVT_CHAR_HOOK e announce()

### Attori software (nuovi da introdurre)

- CardRenderer: componente presentation-layer responsabile del disegno di una singola carta (fronte con rank/suit/colore, dorso uniforme) tramite wx.DC
- BoardLayoutManager: componente presentation-layer che calcola la posizione e dimensione di ogni pila e carta in base alla dimensione del panel; gestisce il layout responsive
- BoardState DTO: oggetto leggero di trasferimento dati tra application e presentation che descrive lo stato corrente del board (pile, carte visibili, posizione cursore, selezione attiva) senza esporre il domain model

### Concetti chiave

- Card rendering: disegno di una carta come rettangolo con rank (testo), suit (simbolo Unicode), colore seme (rosso/nero) e dorso uniforme per carte coperte
- Pile layout: disposizione spaziale delle 13 pile sul board; le pile tableau hanno fan-down verticale (carte sovrapposte parzialmente visibili), le foundation e stock/waste mostrano solo la carta in cima
- Cursor highlight: indicatore visivo della posizione corrente del cursore di navigazione; bordo luminoso attorno alla carta o pila selezionata dal cursore
- Selection feedback: indicazione visiva della carta o gruppo di carte selezionate per lo spostamento; bordo colorato distinto dal cursor highlight
- Dual-mode UI: capacita del GameplayPanel di operare in due modalita (visual e audio_only) con switch runtime senza perdita di stato
- Dirty-rect invalidation: tecnica di rendering che ridisegna solo la regione del board effettivamente modificata dall'ultima azione, invece dell'intero panel
- Screen reader info-zone: widget wx.StaticText posizionato off-screen visivamente ma raggiungibile da NVDA, che riflette lo stato testuale completo della posizione corrente

---

## 3. Flussi Concettuali

### 3.1 Flusso di rendering (board refresh)

```
Utente preme tasto
  |
  v
GameplayPanel.on_key_down()
  |
  v
GamePlayController.handle_wx_key_event()
  |
  v
GameEngine modifica domain state
  |
  v
Controller invoca callback on_board_changed(board_state)
  |
  v
GameplayPanel riceve BoardState DTO
  |
  v
GameplayPanel calcola dirty-rect (pile modificate)
  |
  v
GameplayPanel.Refresh(rect=dirty_region)
  |
  v
EVT_PAINT handler ridisegna solo regione invalidata
  |
  v
BoardLayoutManager fornisce coordinate
  |
  v
CardRenderer disegna carte nella regione
```

### 3.2 Flusso navigazione visiva (cursore)

```
Utente preme freccia (sx/dx/su/giu)
  |
  v
Controller aggiorna CursorManager (pile_idx, card_idx)
  |
  v
on_board_changed emette BoardState con nuova posizione cursore
  |
  v
[Canale visivo] Panel evidenzia nuova pila/carta con bordo luminoso
  |                 Vecchia posizione cursore: bordo rimosso (dirty-rect)
  |
  v
[Canale audio] TTS annuncia carta/pila corrente (comportamento invariato)
  |
  v
[Canale NVDA] info-zone aggiornata con descrizione testuale posizione
```

### 3.3 Flusso selezione e spostamento carte

```
Utente preme Invio (seleziona) su carta scoperta
  |
  v
Controller attiva SelectionManager
  |
  v
BoardState emesso con selection_active=True, selected_cards=[...]
  |
  v
[Visivo] Carte selezionate: bordo colorato distinto (es. blu)
[Audio] TTS conferma selezione
  |
  v
Utente naviga fino a pila destinazione e preme Invio
  |
  v
Controller esegue spostamento via GameEngine
  |
  v
BoardState emesso con pile sorgente/destinazione modificate
  |
  v
[Visivo] Dirty-rect su pile sorgente + destinazione, ridisegno
[Audio] TTS conferma spostamento + suono
```

### 3.4 Flusso pesca dal mazzo (stock)

```
Utente preme tasto pesca (M o tasto dedicato) con cursore su stock
  |
  v
Controller invoca GameEngine.draw_from_stock()
  |
  v
Carta spostata da stock a waste nel domain
  |
  v
BoardState emesso con stock e waste aggiornati
  |
  v
[Visivo] Dirty-rect su zona stock + waste, carta appare scoperta su waste
[Audio] Suono flip + TTS annuncia carta pescata
```

### 3.5 Flusso vittoria

```
GameEngine rileva tutte le foundation complete (13 carte ciascuna)
  |
  v
Callback on_game_ended(victory=True)
  |
  v
[Visivo] Dialog celebrativo wx con statistiche partita
[Audio] Suono vittoria + TTS annuncio completo
  |
  v
Utente conferma, torna al menu
```

---

## 4. Decisioni Architetturali

### 4A. Strategia di rendering

Approccio ibrido: un wx.Panel custom con handler EVT_PAINT e AutoBufferedPaintDC per il disegno delle carte. Il double-buffering tramite AutoBufferedPaintDC elimina il flickering.

Le carte sono rettangoli disegnati con wx.DC:
- Carta scoperta: sfondo bianco, rank (testo), simbolo seme Unicode (cuori, quadri, fiori, picche), colore testo rosso o nero secondo il seme
- Carta coperta: rettangolo con pattern dorso uniforme (colore pieno con bordo)
- Bordi arrotondati dove supportato dal DC

Il rendering usa dirty-rect invalidation: ogni azione di gioco identifica quali pile sono state modificate e chiama Refresh(rect=regione_pila) invece di ridisegnare l'intero board.

Il layer accessibilita e separato e parallelo: un wx.StaticText nascosto off-screen (posizione -10000, -10000 px) viene aggiornato con la descrizione testuale dello stato corrente. NVDA lo legge quando il focus e sul panel. Questo evita il problema di PaintDC non accessibile a screen reader.

Motivazione: wx.DC e l'unico approccio che permette rendering custom di carte con posizionamento libero (fan-down tableau) senza dipendenze esterne come OpenGL o Cairo. Il layer accessibilita parallelo mantiene piena compatibilita NVDA senza compromessi sul rendering visivo.

### 4B. Layout del board

Disposizione a due zone:

```
+-------------------------------------------------------+
|  [STOCK]  [WASTE]          [FND-0] [FND-1] [FND-2] [FND-3] |
|                                                         |
|  [TAB-0] [TAB-1] [TAB-2] [TAB-3] [TAB-4] [TAB-5] [TAB-6]  |
|    |       |       |       |       |       |       |         |
|    v       v       v       v       v       v       v         |
|  (fan)   (fan)   (fan)   (fan)   (fan)   (fan)   (fan)      |
+-------------------------------------------------------+
```

- Zona superiore: stock a sinistra, waste accanto, 4 foundation allineate a destra
- Zona inferiore: 7 colonne tableau con fan-down verticale (ogni carta successiva e spostata verso il basso, mostrando parte della carta precedente)
- Carte coperte nel tableau mostrano solo il dorso con offset verticale ridotto
- Carte scoperte nel tableau mostrano rank e suit con offset verticale maggiore

BoardLayoutManager calcola:
- Dimensione base carta: proporzionale alla larghezza del panel (larghezza_panel / 9 circa per avere margini)
- Aspect ratio carta costante: 2.5:3.5 (standard)
- Offset fan-down: coperta = 1/5 altezza carta, scoperta = 1/3 altezza carta
- Margini tra pile: proporzionali alla dimensione carta
- Ricalcolo completo su EVT_SIZE del panel

Motivazione: il layout a due zone replica il solitaire Klondike classico. Il calcolo responsive garantisce che il board sia leggibile a qualsiasi dimensione finestra. L'offset differenziato coperta/scoperta permette di distinguere visivamente le due categorie.

### 4C. Accessibilita dual-mode

Il GameplayPanel espone una proprieta display_mode con due valori:
- "audio_only": comportamento attuale preservato integralmente; nessun rendering visivo, solo TTS e suoni
- "visual": rendering completo delle carte + TTS attivo + info-zone NVDA

Regole della dual-mode:
- Il default e "audio_only" (backward compatibility assoluta)
- Toggle con shortcut F3 ("Alterna modalita visiva")
- La navigazione tastiera e IDENTICA in entrambe le modalita: nessun tasto cambia comportamento
- Il cambio modalita non interrompe la partita in corso
- La preferenza viene salvata nel profilo utente per persistenza tra sessioni

Canali di informazione paralleli:
- Canale TTS diretto (SAPI5 via ScreenReader): domina durante il gameplay in ENTRAMBE le modalita; ogni azione annuncia il risultato vocalmente
- Canale NVDA automatico: legge l'info-zone (wx.StaticText off-screen) e l'accessible name del panel; attivo in modalita visual, irrilevante in audio_only
- Canale visivo: rendering carte, highlight cursore, feedback selezione; attivo solo in modalita visual

Info-zone NVDA (wx.StaticText off-screen):
- Posizione: (-10000, -10000) — fuori schermo ma nel tree wx, raggiungibile da NVDA
- Contenuto aggiornato ad ogni azione: "Pila tableau 3, carta: 7 di cuori scoperta, 2 carte coperte sotto. Selezione attiva: 10 di picche"
- L'accessible name del GameplayPanel viene aggiornato dinamicamente: "Board solitario - Cursore su tableau 3"

Gestione tasti e focus:
- Il GameplayPanel resta l'UNICO widget focusabile nella finestra gameplay
- Nessun widget figlio accetta focus (info-zone ha stile wx.NO_BORDER e non cattura eventi)
- EVT_CHAR_HOOK resta sul panel, tutti i tasti dispatched a GamePlayController come prima
- TAB resta riservato a cursor_tab (navigazione tra pile) come nel comportamento attuale

Motivazione: il dual-mode garantisce zero regressione per gli utenti non vedenti (il default e audio_only) e abilita il rendering visivo come funzionalita aggiuntiva. L'info-zone off-screen e un pattern standard wxPython per fornire contenuto a screen reader senza impatto visivo.

### 4D. Canale di update (observer pattern)

Stato attuale: il GamePlayController aggiorna il domain tramite GameEngine ma NON notifica il GameplayPanel. Non esiste canale di ritorno.

Soluzione: introdurre un callback on_board_changed nel GamePlayController (non nel GameEngine, per rispettare la Clean Architecture: il presentation layer non deve dipendere dal domain).

Flusso:
1. GameplayPanel registra una callback set_on_board_changed(callback) sul controller
2. Dopo ogni azione che modifica lo stato del board, il controller:
   - Costruisce un BoardState DTO leggero leggendo lo stato da GameEngine
   - Invoca la callback passando il BoardState
3. GameplayPanel riceve il BoardState e aggiorna la vista

BoardState DTO (application layer, perche intermedia tra domain e presentation):
- piles: lista di 13 pile, ciascuna con lista di CardView(rank, suit, face_up)
- cursor_pile_idx: int
- cursor_card_idx: int
- selection_active: bool
- selected_pile_idx: int o None
- selected_cards: lista di CardView o None
- game_over: bool

CardView e un NamedTuple o dataclass leggero, distinto dalla Card di dominio. Contiene solo le informazioni necessarie al rendering: rank (str), suit (str), face_up (bool), suit_color (str).

Questo rispetta la Clean Architecture: il presentation non importa domain.Card, ma usa CardView definito nell'application layer come DTO di confine.

Motivazione: l'observer callback e il pattern piu leggero per introdurre il canale di update senza refactoring invasivo. Un event bus completo sarebbe over-engineering a questo stadio.

### 4E. Gestione tasti (zero breaking changes)

Principio: il rendering visivo e PASSIVO. Reagisce ai cambiamenti di stato (via on_board_changed) ma non cattura ne intercetta tasti propri.

Regole:
- Tutti i 60+ comandi tastiera nel GamePlayController restano invariati
- L'unica aggiunta e il toggle F3 per il cambio display_mode, gestito direttamente nel GameplayPanel prima del dispatch al controller
- ESC, TAB, frecce, numeri, H, M, S e tutti gli altri tasti continuano a funzionare identicamente
- Nessun widget figlio e focusabile: impossibile che il focus si sposti accidentalmente
- event.Skip() NON viene chiamato dopo la gestione tasti gameplay (comportamento attuale preservato): questo impedisce che wx propaghi i tasti a widget nativi

Motivazione: la gestione tasti e il componente piu sensibile per accessibilita. Qualsiasi modifica rischierebbe regressione. Il rendering visivo e un layer aggiuntivo che osserva senza interferire.

### 4F. Dimensione finestra

Modifiche al SolitarioFrame:
- Minimum size portato a 900x650 px (da 600x450)
- Il frame supporta ridimensionamento (rimuovere eventuale wx.RESIZE_BORDER se disabilitato)
- Su EVT_SIZE: BoardLayoutManager ricalcola posizioni e dimensioni carte
- Le carte mantengono aspect ratio costante (2.5:3.5) a qualsiasi dimensione
- Il limite inferiore 900x650 garantisce leggibilita minima con 13 pile

Motivazione: 600x450 e insufficiente per disporre 7 colonne tableau + stock/waste + 4 foundation con carte leggibili. 900x650 e il minimo per un layout confortevole; il responsive permette finestre piu grandi.

### 4G. Rimozione pygame.time.wait (prerequisito)

Stato attuale: GamePlayController._vocalizza() usa pygame.time.wait(100) e pygame.time.wait(200) per creare pause tra annunci TTS. Questo blocca il thread UI e congelera il rendering visivo.

Soluzione propedeutica (da implementare PRIMA del rendering visivo):
- Sostituire pygame.time.wait() con wx.CallLater(ms, callback) per pause non bloccanti
- In alternativa: usare un timer wx.Timer per sequenze di annunci TTS con delay
- Rimuovere l'import di pygame dal layer Application (violazione Clean Architecture gia identificata)

Questo intervento e un PREREQUISITO: va pianificato come fase zero nel PLAN, prima di qualsiasi lavoro sul rendering.

Motivazione: un thread UI bloccato impedisce il ridisegno della finestra. Senza questa correzione, il rendering visivo sarebbe inutilizzabile: la finestra si congelerebbe ad ogni azione vocale.

### 4H. Temi alto contrasto e ipovedenti

Tre temi disponibili:
- Standard: sfondo verde tavolo, carte bianche, testo nero/rosso, bordi grigi
- Alto Contrasto: sfondo nero, carte bianche con bordi spessi bianchi, testo nero/rosso intenso, cursore giallo fluorescente
- Grande: come Standard ma con carte e font 150% della dimensione base

Dettagli per ipovedenti:
- Font rank/suit: scalabile, minimo 14pt in modalita Standard, 21pt in Grande
- Bordi carta: 2px Standard, 3px Alto Contrasto
- Simboli seme Unicode grandi e centrati nella carta
- Cursore: bordo 3px colore contrastante + effetto blink (alternanza colore ogni 500ms tramite wx.Timer)
- Selezione: bordo colore distinto dal cursore (es. cursore = giallo, selezione = ciano)

Il tema si seleziona dalle opzioni di gioco (OptionsDialog esistente) e viene salvato nel profilo utente.

Motivazione: gli utenti ipovedenti necessitano di contrasto elevato, dimensioni ingrandite e feedback visivo forte (blink). I tre temi coprono lo spettro da visione normale a bassa visione severa.

---

## 5. Rischi e Vincoli

### Rischi dall'analisi e mitigazioni architetturali

1. ALTO - EVT_CHAR_HOOK cattura TAB bloccando navigazione widget
   - Mitigazione: nessun widget figlio e focusabile nel GameplayPanel. TAB resta riservato a cursor_tab. L'info-zone off-screen non cattura focus ne eventi. Il panel e l'unico focus owner: non esiste navigazione widget da bloccare. Questo rischio e annullato dal design.

2. ALTO - pygame.time.wait() congela UI visiva
   - Mitigazione: prerequisito obbligatorio (decisione 4G). pygame.time.wait() va sostituito con wx.CallLater() prima di qualsiasi lavoro sul rendering. Il PLAN deve schedulare questa fase come fase zero.

3. ALTO - PaintDC non accessibile a NVDA
   - Mitigazione: il canale accessibilita e completamente separato dal rendering (decisione 4C). Un wx.StaticText off-screen fornisce descrizione testuale dello stato board a NVDA. L'accessible name del panel e aggiornato dinamicamente. Il rendering PaintDC non ha alcun ruolo nel canale accessibilita.

4. MEDIO - Frame 600x450 troppo piccolo per 13 pile
   - Mitigazione: minimum size portato a 900x650 (decisione 4F). Layout responsive ricalcola su EVT_SIZE. Aspect ratio carte costante.

5. MEDIO - Performance rendering 52 carte con alpha blending
   - Mitigazione: dirty-rect invalidation (decisione 4A) assicura che solo le pile modificate vengano ridisegnate. AutoBufferedPaintDC elimina flickering. Non si usa alpha blending: le carte sono rettangoli opachi con bordi, senza trasparenze. Il costo di rendering per azione e O(carte nella pila modificata), non O(52).

6. MEDIO - Regressione accessibilita se focus si sposta su widget figli
   - Mitigazione: nessun widget figlio e focusabile (decisione 4E). L'info-zone usa stile non focusabile. Il panel mantiene il focus esclusivo in qualsiasi modalita. event.Skip() non viene chiamato per i tasti gameplay.

7. BASSO-MEDIO - Dipendenza pygame nel layer Application
   - Mitigazione: la rimozione di pygame.time.wait() (decisione 4G) elimina l'import pygame dal controller. Se rimangono altre dipendenze pygame nell'Application layer, vanno migrate all'Infrastructure layer. Questo va verificato nel PLAN.

### Vincoli di backward compatibility

- La modalita audio_only E IL DEFAULT. Un utente che non modifica alcuna impostazione deve avere esattamente lo stesso comportamento di prima: nessun rendering visivo, solo TTS e suoni.
- Tutti i 60+ comandi tastiera restano invariati: nessun tasto viene aggiunto, rimosso o ha comportamento modificato (l'unica eccezione e F3 per il toggle, che e un tasto nuovo senza conflitti).
- L'ordine degli annunci TTS non cambia: un giocatore non vedente non deve percepire alcuna differenza rispetto alla versione attuale.
- Le partite in corso non vengono invalidate dal cambio modalita: il toggle visual/audio_only e istantaneo e senza perdita di stato.
- Il profilo utente mantiene backward compatibility: se la chiave display_mode non esiste nel profilo, il default e "audio_only".

### Vincoli architetturali

- CardRenderer, BoardLayoutManager e BoardState rispettano la Clean Architecture: CardRenderer e BoardLayoutManager vivono nel presentation layer, BoardState e definito nell'application layer come DTO di confine.
- Il domain layer resta intatto: nessuna modifica a Card, Pile, GameTable, CursorManager, SelectionManager.
- Il DependencyContainer esistente viene esteso (non sostituito) per iniettare i nuovi componenti.
