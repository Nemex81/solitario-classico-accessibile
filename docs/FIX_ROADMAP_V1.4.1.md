# 🛠️ FIX ROADMAP v1.4.1 - Implementazione Logica Gioco Completa

**Branch**: `refactoring-engine`  
**Base Version**: v1.4.0 (Clean Architecture implementata)  
**Target Version**: v1.4.1 (Feature parity 100% con legacy)  
**Data Creazione**: 8 Febbraio 2026

---

## 📊 STATO ATTUALE vs ATTESO

### ✅ Cosa Funziona (v1.4.0)
- ✅ Architettura Clean completa (Domain/Application/Infrastructure/Presentation)
- ✅ Game engine funzionante
- ✅ Tutti i 60+ comandi tastiera mappati
- ✅ TTS e screen reader integrati
- ✅ Menu principale base
- ✅ Nessun crash improvviso

### ❌ Cosa Manca (Feature Gap)
- ❌ **Menu secondario** "Gioca al solitario" (Nuova partita/Opzioni/Chiudi)
- ❌ **Finestra opzioni virtuali** (gestione settings interattiva)
- ❌ **Feedback vocali dettagliati** (pesca, mosse, rimescolamenti)

---

## 🎯 FIX #1: MENU SECONDARIO (Priorità: ALTA)

### Problema Attuale
```
Menu Principale
├─ [ENTER] su "Gioca al solitario" → Avvia partita DIRETTAMENTE ❌
└─ Esci
```

**Comportamento errato**: L'utente viene catapultato in partita senza possibilità di configurare le opzioni.

### Comportamento Atteso
```
Menu Principale
├─ [ENTER] su "Gioca al solitario" → Menu Secondario ✅
│   └─ Menu Solitario Classico
│       ├─ Nuova partita (tasto rapido: N)
│       ├─ Opzioni (tasto rapido: O) → Finestra virtuale opzioni
│       └─ Chiudi (tasto ESC o C) → Torna al menu principale
└─ Esci
```

### Riferimenti Legacy
**File**: `scr/game_play.py` (linee 129-141)

```python
def n_press(self):
    # avviamo una nuova partita richiedendo il livello di difficoltà.
    if self.engine.is_game_running:
        self.create_yes_or_no_box("Sei sicuro di voler avviare una nuova partita?", "Partita in corso rilevata")
        if not self.answare:
            return

    self.engine.nuova_partita()

def o_press(self):
    string = self.engine.change_game_settings()
    if string:
        self.vocalizza(string)
```

### Implementazione Clean Architecture

#### 1. Aggiornare `VirtualMenu` per supportare sottomenu
**File**: `src/infrastructure/ui/menu.py`

**Modifiche**:
- Aggiungere attributo `parent_menu: Optional[VirtualMenu]` per gerarchie
- Aggiungere metodo `open_submenu(submenu: VirtualMenu)`
- Aggiungere metodo `close_submenu()` per tornare al parent
- Gestire chiave ESC per chiudere sottomenu

#### 2. Creare sottomenu in `test.py`
**File**: `test.py` (metodo `__init__`)

```python
# Menu secondario "Gioca al solitario"
self.game_submenu = VirtualMenu(
    items=[
        "Nuova partita",
        "Opzioni",
        "Chiudi"
    ],
    callback=self.handle_game_submenu_selection,
    screen=self.screen,
    screen_reader=self.screen_reader,
    parent_menu=self.menu  # Collega al menu principale
)

# Aggiorna callback menu principale
def handle_menu_selection(self, selected_item: int) -> None:
    if selected_item == 0:
        # Apri sottomenu invece di avviare partita
        self.menu.open_submenu(self.game_submenu)
    elif selected_item == 1:
        self.quit_app()

# Nuovo callback per sottomenu
def handle_game_submenu_selection(self, selected_item: int) -> None:
    if selected_item == 0:
        # Nuova partita
        self.start_game()
    elif selected_item == 1:
        # Apri opzioni (vedi FIX #2)
        self.open_options()
    elif selected_item == 2:
        # Chiudi sottomenu
        self.game_submenu.close()
```

### Output Vocale Atteso
```
[User preme ENTER su "Gioca al solitario"]
→ TTS: "Sottomenu aperto: Gioca al solitario. 3 voci. Voce corrente: 1 di 3, Nuova partita."

[User preme FRECCIA GIÙ]
→ TTS: "2 di 3: Opzioni"

[User preme O]
→ TTS: "Apertura opzioni..."
```

---

## 🎯 FIX #2: FINESTRA OPZIONI VIRTUALI (Priorità: ALTA)

### Problema Attuale
**Mancante completamente**: Non esiste gestione interattiva delle opzioni.

### Comportamento Atteso
Quando l'utente preme **O** (da menu o durante partita):
1. Entra in "modalità opzioni" (flag `change_settings = True`)
2. Tutti i tasti F1-F5 modificano le impostazioni
3. Ogni modifica vocalizza lo stato corrente
4. Premendo **O** o **ESC** esce dalle opzioni

### Comandi Opzioni (come in Legacy)

| Tasto | Azione | Feedback Vocale |
|-------|--------|-----------------|
| **F1** | Cambia mazzo | "Tipo di mazzo impostato a: carte napoletane." |
| **F2** | Cambia difficoltà (1→2→3→1) | "Livello di difficoltà impostato a: 2." |
| **F3** | Decrementa timer (-5 min) | "Timer impostato a: 15 minuti." |
| **F4** | Incrementa timer (+5 min) | "Timer impostato a: 25 minuti." |
| **F5** | Toggle shuffle mode | "Modalità riciclo scarti: MESCOLATA CASUALE." |
| **CTRL+F3** | Disabilita timer | "Il timer è stato disattivato!" |
| **O/ESC** | Chiudi opzioni | "Impostazioni di gioco chiuse." |

### Riferimenti Legacy
**File**: `scr/game_engine.py` (linee 345-366)

```python
def change_game_settings(self):
    """ cambiamo le impostazioni del gioco """
    
    if self.is_game_running:
        return "Non puoi modificare le impostazioni di gioco durante una partita!  \n"
    
    elif not self.is_game_running and self.change_settings:
        self.change_settings = False
        return "impostazioni di gioco chiuse.  \n"
    
    elif not self.is_game_running and not self.change_settings:
        self.change_settings = True
        return "impostazioni di gioco aperte.  \n"
```

**Validazioni importanti**:
```python
def change_deck_type(self):
    if self.is_game_running:
        return "Non puoi modificare il tipo di mazzo durante una partita!  \n"
    # ... modifica mazzo
```

### Implementazione Clean Architecture

#### 1. Aggiungere flag al `GameEngine`
**File**: `src/application/game_engine.py`

```python
class GameEngine:
    def __init__(self, ...):
        # ... existing code ...
        self._options_open: bool = False  # Flag finestra opzioni
    
    def open_options(self) -> str:
        """Apre la finestra virtuale opzioni."""
        if self.is_game_running():
            return "Non puoi modificare le impostazioni durante una partita!  \n"
        
        self._options_open = True
        return "Impostazioni di gioco aperte.  \n"
    
    def close_options(self) -> str:
        """Chiude la finestra virtuale opzioni."""
        self._options_open = False
        return "Impostazioni di gioco chiuse.  \n"
    
    def is_options_open(self) -> bool:
        """Verifica se la finestra opzioni è aperta."""
        return self._options_open
```

#### 2. Aggiornare `GameSettings` per validazioni
**File**: `src/application/game_settings.py`

```python
def change_deck_type(self, is_game_running: bool) -> Tuple[bool, str]:
    """Cambia tipo di mazzo con validazione.
    
    Returns:
        (success, message): Tupla con esito e messaggio vocale
    """
    if is_game_running:
        return (False, "Non puoi modificare il tipo di mazzo durante una partita!")
    
    # Cambia mazzo
    new_type = "neapolitan" if self.deck_type == "french" else "french"
    self.deck_type = new_type
    
    deck_names = {"french": "carte francesi", "neapolitan": "carte napoletane"}
    return (True, f"Tipo di mazzo impostato a: {deck_names[new_type]}.")
```

#### 3. Gestire comandi opzioni in `GamePlayController`
**File**: `src/application/gameplay_controller.py`

```python
def handle_keyboard_events(self, event):
    """Gestisce eventi tastiera con modalità opzioni."""
    
    if event.type == pygame.KEYDOWN:
        # Modalità OPZIONI: intercetta F1-F5
        if self.engine.is_options_open():
            if event.key == pygame.K_F1:
                msg = self._handle_change_deck()
                self.screen_reader.tts.speak(msg, interrupt=True)
                return
            elif event.key == pygame.K_F2:
                msg = self._handle_change_difficulty()
                self.screen_reader.tts.speak(msg, interrupt=True)
                return
            # ... altri tasti F3-F5
            
            elif event.key == pygame.K_o or event.key == pygame.K_ESCAPE:
                msg = self.engine.close_options()
                self.screen_reader.tts.speak(msg, interrupt=True)
                return
        
        # Modalità NORMALE: comandi gioco standard
        else:
            # ... gestione comandi esistenti
            pass
```

### Output Vocale Atteso
```
[User preme O nel menu]
→ TTS: "Impostazioni di gioco aperte."

[User preme F1]
→ TTS: "Tipo di mazzo impostato a: carte napoletane."

[User preme F2]
→ TTS: "Livello di difficoltà impostato a: 2."

[User preme F4]
→ TTS: "Timer impostato a: 25 minuti."

[User preme O]
→ TTS: "Impostazioni di gioco chiuse."
```

---

## 🎯 FIX #3: FEEDBACK VOCALI DETTAGLIATI (Priorità: MEDIA)

### Problema Attuale
**Output generico**: "Hai pescato carta", "Mossa eseguita" senza dettagli.

### Comportamento Atteso
**Output dettagliato** come in legacy con:
- Nomi esatti delle carte
- Pile di origine/destinazione
- Carte scoperte dopo spostamenti
- Messaggi per rimescolamenti

---

### 3.1 PESCA CARTE - Feedback Dettagliato

#### Riferimento Legacy
**File**: `scr/game_engine.py` (linee 758-762)

```python
def _genera_messaggio_carte_pescate(self, lista_carte):
    """Genera il messaggio vocale per le carte pescate."""
    msg = "hai pescato: "
    for c in lista_carte:
        msg += "%s,  \n" % c.get_name
    return msg
```

**Output esempio**:
```
"Hai pescato: 7 di Cuori, Regina di Quadri, 3 di Fiori."
```

#### Implementazione Clean Architecture
**File**: `src/presentation/game_formatter.py`

```python
@staticmethod
def format_drawn_cards(cards: List[Card]) -> str:
    """Formatta il messaggio di pesca dettagliato.
    
    Args:
        cards: Lista di carte pescate
        
    Returns:
        Messaggio vocale formattato
        
    Example:
        >>> cards = [Card("7", "hearts"), Card("Q", "diamonds")]
        >>> GameFormatter.format_drawn_cards(cards)
        "Hai pescato: 7 di Cuori, Regina di Quadri."
    """
    if not cards:
        return "Nessuna carta pescata."
    
    msg = "Hai pescato: "
    card_names = [card.get_display_name() for card in cards]
    msg += ", ".join(card_names) + "."
    
    return msg
```

---

### 3.2 REPORT MOSSE - Feedback Completo

#### Riferimento Legacy
**File**: `scr/game_engine.py` (linee 526-556)

```python
def get_report_mossa(self):
    """ vocalizziamo il report della mossa """
    
    string = ""
    tot_cards = 0
    if self.selected_card:
        tot_cards = len(self.selected_card)
        string += "sposti:  \n"
        if tot_cards > 2:
            string += f"{self.selected_card[0].get_name} e altre {tot_cards - 1} carte.  \n"
        else:
            for carta in self.selected_card:
                string += f"{carta.get_name}.  \n"

    if self.origin_pile:
        string += f"da: {self.origin_pile.nome},  \n"

    if self.dest_pile:
        string += f"a: {self.dest_pile.nome},  \n"
        
        # Verifica che ci siano abbastanza carte e che l'indice sia valido
        if tot_cards > 0 and len(self.dest_pile.carte) > tot_cards:
            id = len(self.dest_pile.carte) - tot_cards - 1
            
            # Verifica bounds dell'indice
            if 0 <= id < len(self.dest_pile.carte):
                carta_sotto = self.dest_pile.carte[id]
                
                # Mostra la carta sotto SOLO se NON è un Re E NON è la carta selezionata stessa
                if carta_sotto.get_value != 13 and carta_sotto != self.selected_card[0]:
                    string += f"sopra alla carta: {carta_sotto.get_name}.  \n"

    # Verifica che origin_pile non sia None prima di controllare se è vuota
    if self.origin_pile and not self.origin_pile.is_empty_pile():
        string += f"hai scoperto : {self.origin_pile.carte[-1].get_name} in:  {self.origin_pile.nome}.  \n"
    
    return string
```

**Output esempio**:
```
Sposti: Asso di Cuori.
Da: Pila base 1.
A: Pila semi Cuori.
Sopra alla carta: Re di Cuori.
Hai scoperto: 5 di Picche in: Pila base 1.
```

#### Implementazione Clean Architecture
**File**: `src/presentation/game_formatter.py`

```python
@staticmethod
def format_move_report(
    moved_cards: List[Card],
    origin_pile: Pile,
    dest_pile: Pile,
    card_under: Optional[Card] = None,
    revealed_card: Optional[Card] = None
) -> str:
    """Formatta il report dettagliato di una mossa.
    
    Args:
        moved_cards: Carte spostate
        origin_pile: Pila di origine
        dest_pile: Pila di destinazione
        card_under: Carta sotto cui si posiziona (opzionale)
        revealed_card: Carta scoperta nella pila origine (opzionale)
        
    Returns:
        Messaggio vocale completo della mossa
    """
    if not moved_cards:
        return "Nessuna carta spostata."
    
    msg = "Sposti: "
    
    # Formato carte: se >2 mostra solo prima + conteggio
    tot_cards = len(moved_cards)
    if tot_cards > 2:
        msg += f"{moved_cards[0].get_display_name()} e altre {tot_cards - 1} carte.\n"
    else:
        card_names = [card.get_display_name() for card in moved_cards]
        msg += ", ".join(card_names) + ".\n"
    
    # Origine e destinazione
    msg += f"Da: {origin_pile.name}.\n"
    msg += f"A: {dest_pile.name}.\n"
    
    # Carta sotto (se non Re)
    if card_under and card_under.rank != "K":
        msg += f"Sopra alla carta: {card_under.get_display_name()}.\n"
    
    # Carta scoperta
    if revealed_card:
        msg += f"Hai scoperto: {revealed_card.get_display_name()} in: {origin_pile.name}.\n"
    
    return msg
```

---

### 3.3 RIMESCOLAMENTO - Feedback con Auto-Pesca

#### Riferimento Legacy
**File**: `scr/game_engine.py` (linee 779-803)

```python
def _esegui_rimescolamento_e_pescata(self):
    """Rimescola gli scarti nel mazzo e pesca automaticamente."""
    self.tavolo.riordina_scarti(self.shuffle_discards)
    self.conta_rimischiate += 1
    
    # Prepara messaggio rimescolamento
    if self.shuffle_discards:
        msg_rimescola = "Rimescolo gli scarti in modo casuale nel mazzo riserve!  \n"
    else:
        msg_rimescola = "Rimescolo gli scarti in mazzo riserve!  \n"
    
    # Auto-draw: tenta pescata automatica dopo rimescolamento
    livello = int(self.difficulty_level)
    pescata_ok = self.tavolo.pescata(livello)
    
    if not pescata_ok:
        # Mazzo ancora vuoto dopo rimescolamento (edge case)
        return msg_rimescola + "Attenzione: mazzo vuoto, nessuna carta da pescare!  \n"
    
    # Pescata riuscita: ottieni carte e genera messaggio completo
    carte_pescate = self.execute_draw()
    msg_pescata = self._genera_messaggio_carte_pescate(carte_pescate)
    
    return msg_rimescola + "Pescata automatica: " + msg_pescata
```

**Output esempio**:
```
Rimescolo gli scarti in modo casuale nel mazzo riserve!
Pescata automatica: Hai pescato: 9 di Quadri, Asso di Fiori.
```

#### Implementazione Clean Architecture
**File**: `src/presentation/game_formatter.py`

```python
@staticmethod
def format_reshuffle_message(
    shuffle_mode: str,
    auto_drawn_cards: Optional[List[Card]] = None
) -> str:
    """Formatta il messaggio di rimescolamento con eventuale auto-pesca.
    
    Args:
        shuffle_mode: "shuffle" (casuale) o "reverse" (inversione)
        auto_drawn_cards: Carte pescate automaticamente dopo rimescolamento
        
    Returns:
        Messaggio vocale completo
    """
    if shuffle_mode == "shuffle":
        msg = "Rimescolo gli scarti in modo casuale nel mazzo riserve!\n"
    else:
        msg = "Rimescolo gli scarti in mazzo riserve!\n"
    
    # Auto-pesca
    if auto_drawn_cards:
        msg += "Pescata automatica: "
        msg += GameFormatter.format_drawn_cards(auto_drawn_cards)
    else:
        msg += "Attenzione: mazzo vuoto, nessuna carta da pescare!"
    
    return msg
```

---

## 📋 PRIORITÀ IMPLEMENTAZIONE

### Fase 1: Menu + Opzioni (Commit #15)
1. ✅ Modificare `VirtualMenu` per supportare sottomenu
2. ✅ Creare menu secondario "Gioca al solitario"
3. ✅ Implementare finestra opzioni virtuali in `GameEngine`
4. ✅ Aggiungere validazioni in `GameSettings`
5. ✅ Gestire modalità opzioni in `GamePlayController`
6. ✅ Testing completo del flusso menu → opzioni → partita

### Fase 2: Feedback Vocali (Commit #16)
1. ✅ Implementare `format_drawn_cards()` in `GameFormatter`
2. ✅ Implementare `format_move_report()` in `GameFormatter`
3. ✅ Implementare `format_reshuffle_message()` in `GameFormatter`
4. ✅ Integrare formatter in `GamePlayController`
5. ✅ Testing completo feedback durante partita

### Fase 3: Testing Utenti (v1.4.1)
1. ✅ Testing menu completo (principale → secondario → opzioni)
2. ✅ Testing modifica settings (tutti i comandi F1-F5)
3. ✅ Testing feedback vocali durante partita
4. ✅ Validazione feature parity 100% con legacy

---

## 🎯 CRITERI DI SUCCESSO

### Menu Secondario ✅
- [ ] ENTER su "Gioca al solitario" apre sottomenu (non partita)
- [ ] Sottomenu ha 3 voci: Nuova partita / Opzioni / Chiudi
- [ ] Tasto rapido N avvia partita
- [ ] Tasto rapido O apre opzioni
- [ ] ESC chiude sottomenu e torna al principale

### Finestra Opzioni ✅
- [ ] Tasto O apre/chiude opzioni
- [ ] Flag `change_settings` gestito correttamente
- [ ] F1 cambia mazzo con validazione
- [ ] F2 cambia difficoltà (ciclo 1→2→3→1)
- [ ] F3 decrementa timer (-5 min)
- [ ] F4 incrementa timer (+5 min)
- [ ] F5 toggle shuffle mode
- [ ] CTRL+F3 disabilita timer
- [ ] Ogni modifica vocalizza stato corrente
- [ ] Opzioni bloccate durante partita in corso

### Feedback Vocali ✅
- [ ] Pesca carte: annuncia tutte le carte pescate per nome
- [ ] Spostamenti: annuncia carte/origine/destinazione/carta sotto/carta scoperta
- [ ] Rimescolamenti: annuncia modalità + auto-pesca
- [ ] Messaggi identici alla versione legacy
- [ ] Nessun output generico ("carta" → "7 di Cuori")

---

## 📖 FILE DA MODIFICARE

### Commit #15: Menu + Opzioni
1. `src/infrastructure/ui/menu.py` - Sottomenu support
2. `src/application/game_engine.py` - Flag opzioni
3. `src/application/game_settings.py` - Validazioni settings
4. `src/application/gameplay_controller.py` - Gestione modalità opzioni
5. `test.py` - Menu secondario e callback

### Commit #16: Feedback Vocali
1. `src/presentation/game_formatter.py` - Nuovi metodi format_*
2. `src/application/gameplay_controller.py` - Integrazione formatter
3. `src/domain/models/card.py` - Metodo `get_display_name()`

---

## 🚀 PROSSIMI STEP

1. ✅ **Creare FIX_CHECKLIST.md** per tracking rapido
2. ⏳ **Commit #15**: Implementazione menu + opzioni
3. ⏳ **Commit #16**: Implementazione feedback vocali
4. ⏳ **Testing utenti**: Validazione completa v1.4.1
5. ⏳ **CHANGELOG**: Aggiornamento versione v1.4.1
6. ⏳ **Release**: Tag v1.4.1 pronto per testing utenti reali

---

**Fine Roadmap v1.4.1**  
*Documentazione completa per implementazione fix logica gioco*
