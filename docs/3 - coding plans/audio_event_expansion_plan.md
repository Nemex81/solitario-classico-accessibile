# Piano Espansione Sistema Audio - Parità con Vecchia Versione

**Data:** 2026-02-24  
**Branch:** `supporto-audio-centralizzato`  
**Obiettivo:** Riprodurre gli stessi effetti sonori associati agli stessi eventi della vecchia versione pygame nel nuovo sistema wx.

---

## 1. Executive Summary

La vecchia versione aveva **25+ eventi audio distinti** con feedback granulare per ogni azione utente. La versione moderna attuale ha solo **12 eventi mappati**. Questo piano colma il gap aggiungendo:

- **15 nuovi AudioEvent** a `audio_events.py`
- **Configurazione completa** in `audio_config.json` con tutti i mapping semantici
- **Punti di inserimento** nel codice wx per chiamare gli eventi giusti

### Mappatura Semantica Dedotta

Basandoci sui nomi dei file rinominati durante la conversione ogg→wav, abbiamo dedotto la seguente corrispondenza:

```
Vecchio File → Evento → Nuovo File
─────────────────────────────────────────────────────────────
# Navigazione
sound58.ogg → movecursor menu → navigate.wav ✓ (già mappato)
sound62.ogg → scorri frame → navigate_alt.wav
sound61.ogg → scorri pile → focus_change.wav
sound33.ogg → anteprima pile → notification.wav

# Conferme/Azioni
sound1.ogg → confirm → select.wav ✓ (già mappato)
sound29.ogg → abort/cancel → cancel.wav ✓ (già mappato)
sound2.ogg → toggle si/no → button_hover.wav
sound3.ogg → confirm yes/no → confirm.wav
sound101.ogg → question quit → error.wav

# Gameplay Core
sound84.ogg → scorri carte → card_move.wav ✓ (già mappato)
sound11.ogg → pescata → stock_draw.wav ✓ (già mappato)
sound7.ogg → spostamento fallito → invalid_move.wav ✓ (già mappato)
speed.ogg → spostamento singolo → tableau_drop.wav
solve.ogg → spostamento multiplo → foundation_drop.wav
sound59.ogg → carte esaurite → boundary_hit.wav

# Gestione Partita
shuffle-cards-1.ogg → new game → card_shuffle.wav
arteries.ogg → distribuzione carte → card_shuffle.wav (riuso)
shuffle-cards-2.ogg → rimischia scarti → card_shuffle_alt.wav
level.ogg → vittoria → victory.wav ✓ (già mappato)

# Settings (riuso intelligente)
sound36.ogg → save settings → select.wav
sound55.ogg → change level → focus_change.wav
sound53.ogg → change volume → focus_change.wav
sound111.ogg → change music → focus_change.wav
sound102.ogg → switch on → button_click.wav
sound103.ogg → switch off → button_hover.wav

# Voice
welcome-it.ogg → benvenuto IT → welcome_italian.wav ✓
welcome-eng.ogg → benvenuto EN → welcome_english.wav ✓

# Menu UI
(nuovi) → apri/chiudi menu → menu_open.wav / menu_close.wav
(nuovi) → click pulsante → button_click.wav
```

---

## 2. Modifiche a `audio_events.py`

### File: `src/infrastructure/audio/audio_events.py`

**Aggiungi questi eventi alla classe `AudioEventType`:**

```python
class AudioEventType:
    """Costanti stringa per i tipi di evento audio.
    Organizzati per bus/categoria.
    I controller usano queste costanti per creare istanze AudioEvent.
    """
    # Gameplay bus - azioni sulle carte
    CARD_MOVE = "card_move"  # ✓ esistente
    CARD_SELECT = "card_select"  # ✓ esistente
    CARD_DROP = "card_drop"  # ✓ esistente
    CARD_FLIP = "card_flip"  # NUOVO: carta scoperta
    CARD_SHUFFLE = "card_shuffle"  # NUOVO: mischia mazzo (new game)
    CARD_SHUFFLE_WASTE = "card_shuffle_waste"  # NUOVO: rimischia scarti
    FOUNDATION_DROP = "foundation_drop"  # ✓ esistente
    INVALID_MOVE = "invalid_move"  # ✓ esistente
    TABLEAU_BUMPER = "tableau_bumper"  # ✓ esistente
    TABLEAU_DROP = "tableau_drop"  # NUOVO: drop su pila gioco (spostamento singolo)
    STOCK_DRAW = "stock_draw"  # ✓ esistente
    WASTE_DROP = "waste_drop"  # ✓ esistente
    CARDS_EXHAUSTED = "cards_exhausted"  # NUOVO: carte mazzo/scarti esaurite
    MULTI_CARD_MOVE = "multi_card_move"  # NUOVO: spostamento multiplo
    
    # UI bus - navigazione
    UI_NAVIGATE = "ui_navigate"  # ✓ esistente (cursore menu)
    UI_NAVIGATE_FRAME = "ui_navigate_frame"  # NUOVO: cambio sezione (frame)
    UI_NAVIGATE_PILE = "ui_navigate_pile"  # NUOVO: scorrimento pile orizzontale
    UI_SELECT = "ui_select"  # ✓ esistente
    UI_CANCEL = "ui_cancel"  # ✓ esistente
    UI_CONFIRM = "ui_confirm"  # NUOVO: conferma generica
    UI_TOGGLE = "ui_toggle"  # NUOVO: toggle opzioni si/no
    UI_FOCUS_CHANGE = "ui_focus_change"  # NUOVO: cambio focus generico
    UI_BOUNDARY_HIT = "ui_boundary_hit"  # NUOVO: limite raggiunto
    UI_NOTIFICATION = "ui_notification"  # NUOVO: notifica/anteprima info
    UI_ERROR = "ui_error"  # NUOVO: errore/alert
    
    # UI bus - menu e pulsanti
    UI_MENU_OPEN = "ui_menu_open"  # NUOVO: apertura menu
    UI_MENU_CLOSE = "ui_menu_close"  # NUOVO: chiusura menu
    UI_BUTTON_CLICK = "ui_button_click"  # NUOVO: click pulsante
    UI_BUTTON_HOVER = "ui_button_hover"  # NUOVO: hover pulsante
    MIXER_OPENED = "mixer_opened"  # ✓ esistente
    
    # Settings bus (nuovi eventi)
    SETTING_SAVED = "setting_saved"  # NUOVO: impostazioni salvate
    SETTING_CHANGED = "setting_changed"  # NUOVO: cambio impostazione generica
    SETTING_LEVEL_CHANGED = "setting_level_changed"  # NUOVO: cambio difficoltà
    SETTING_VOLUME_CHANGED = "setting_volume_changed"  # NUOVO: cambio volume
    SETTING_MUSIC_CHANGED = "setting_music_changed"  # NUOVO: cambio brano
    SETTING_SWITCH_ON = "setting_switch_on"  # NUOVO: interruttore ON
    SETTING_SWITCH_OFF = "setting_switch_off"  # NUOVO: interruttore OFF
    
    # Ambient bus
    AMBIENT_LOOP = "ambient_loop"  # ✓ esistente
    
    # Music bus
    MUSIC_LOOP = "music_loop"  # ✓ esistente
    
    # Voice bus
    GAME_WON = "game_won"  # ✓ esistente
    WELCOME_MESSAGE = "welcome_message"  # NUOVO: benvenuto (localizzato)
    
    # Timer events
    TIMER_WARNING = "timer_warning"  # ✓ esistente
    TIMER_EXPIRED = "timer_expired"  # ✓ esistente
```

**Conteggio:** +21 nuovi eventi audio

---

## 3. Modifiche a `audio_config.json`

### File: `config/audio_config.json`

**Sostituisci la sezione `event_sounds` con questa configurazione completa:**

```json
{
  "version": "1.0",
  "active_sound_pack": "default",
  "bus_volumes": {
    "gameplay": 80,
    "ui": 70,
    "ambient": 40,
    "music": 30,
    "voice": 90
  },
  "bus_muted": {
    "gameplay": false,
    "ui": false,
    "ambient": false,
    "music": false,
    "voice": false
  },
  "mixer_params": {
    "frequency": 44100,
    "size": -16,
    "channels": 2,
    "buffer": 512
  },
  "event_sounds": {
    "CARD_MOVE": "gameplay/card_move.wav",
    "CARD_SELECT": "gameplay/card_place.wav",
    "CARD_FLIP": "gameplay/card_flip.wav",
    "CARD_SHUFFLE": "gameplay/card_shuffle.wav",
    "CARD_SHUFFLE_WASTE": "gameplay/card_shuffle_alt.wav",
    "FOUNDATION_DROP": "gameplay/foundation_drop.wav",
    "INVALID_MOVE": "gameplay/invalid_move.wav",
    "TABLEAU_BUMPER": "gameplay/invalid_move.wav",
    "TABLEAU_DROP": "gameplay/tableau_drop.wav",
    "STOCK_DRAW": "gameplay/stock_draw.wav",
    "CARDS_EXHAUSTED": "ui/boundary_hit.wav",
    "MULTI_CARD_MOVE": "gameplay/foundation_drop.wav",
    
    "UI_NAVIGATE": "ui/navigate.wav",
    "UI_NAVIGATE_FRAME": "ui/navigate_alt.wav",
    "UI_NAVIGATE_PILE": "ui/focus_change.wav",
    "UI_SELECT": "ui/select.wav",
    "UI_CANCEL": "ui/cancel.wav",
    "UI_CONFIRM": "ui/confirm.wav",
    "UI_TOGGLE": "ui/button_hover.wav",
    "UI_FOCUS_CHANGE": "ui/focus_change.wav",
    "UI_BOUNDARY_HIT": "ui/boundary_hit.wav",
    "UI_NOTIFICATION": "ui/notification.wav",
    "UI_ERROR": "ui/error.wav",
    
    "UI_MENU_OPEN": "ui/menu_open.wav",
    "UI_MENU_CLOSE": "ui/menu_close.wav",
    "UI_BUTTON_CLICK": "ui/button_click.wav",
    "UI_BUTTON_HOVER": "ui/button_hover.wav",
    "MIXER_OPENED": "ui/menu_open.wav",
    
    "SETTING_SAVED": "ui/select.wav",
    "SETTING_CHANGED": "ui/focus_change.wav",
    "SETTING_LEVEL_CHANGED": "ui/focus_change.wav",
    "SETTING_VOLUME_CHANGED": "ui/focus_change.wav",
    "SETTING_MUSIC_CHANGED": "ui/focus_change.wav",
    "SETTING_SWITCH_ON": "ui/button_click.wav",
    "SETTING_SWITCH_OFF": "ui/button_hover.wav",
    
    "GAME_WON": "voice/victory.wav",
    "WELCOME_MESSAGE": "voice/welcome_italian.wav",
    
    "TIMER_WARNING": "ui/navigate.wav",
    "TIMER_EXPIRED": "ui/cancel.wav"
  },
  "preload_all_event_sounds": true,
  "enabled_events": {
    "ui_navigate": true,
    "ui_navigate_frame": true,
    "ui_navigate_pile": true,
    "ui_select": true,
    "ui_cancel": true,
    "ui_confirm": true,
    "ui_toggle": true,
    "ui_focus_change": true,
    "ui_boundary_hit": true,
    "ui_notification": true,
    "ui_error": true,
    "ui_menu_open": true,
    "ui_menu_close": true,
    "ui_button_click": true,
    "ui_button_hover": true,
    "card_move": true,
    "card_flip": true,
    "card_shuffle": true,
    "card_shuffle_waste": true,
    "tableau_drop": true,
    "cards_exhausted": true,
    "multi_card_move": true,
    "game_won": true,
    "welcome_message": true,
    "timer_warning": true,
    "timer_expired": true,
    "ambient_loop": true,
    "mixer_opened": true,
    "setting_saved": true,
    "setting_changed": true,
    "setting_level_changed": true,
    "setting_volume_changed": true,
    "setting_music_changed": true,
    "setting_switch_on": true,
    "setting_switch_off": true
  }
}
```

---

## 4. Punti di Inserimento nel Codice WX

### 4.1 Navigazione Menu e UI

**File:** `src/presentation/wx_ui/main_window.py` o equivalente gestore eventi tastiera

#### Evento: Scorrimento Menu (↑/↓)

**Vecchia versione:**  
```python
def PlayWalkMenu(self):
    suono = self.lksounds["effect"]["movecursor"]
    self.PlayEff(suono)  # sound58.ogg
```

**Nuova versione:**  
```python
def on_arrow_up(self, event):
    # ... logica navigazione ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NAVIGATE
    ))
    
def on_arrow_down(self, event):
    # ... logica navigazione ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NAVIGATE
    ))
```

#### Evento: Cambio Frame/Sezione (Tab)

**Vecchia versione:**  
```python
def PlayMoveFrame(self):
    suono = self.lksounds["effect"]["scorri frame"]
    self.PlayEff(suono)  # sound62.ogg
```

**Nuova versione:**  
```python
def on_tab_press(self, event):
    # ... logica cambio frame ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NAVIGATE_FRAME
    ))
```

#### Evento: Scorrimento Pile Orizzontale (←/→)

**Vecchia versione:**  
```python
def PlayScorriPile(self):
    suono = self.lksounds["effect"]["scorri pile"]
    self.PlayEff(suono)  # sound61.ogg
```

**Nuova versione:**  
```python
def on_left_arrow(self, event):
    # ... logica cambio pila ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NAVIGATE_PILE,
        source_pile=self.current_pile_index
    ))
    
def on_right_arrow(self, event):
    # ... logica cambio pila ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NAVIGATE_PILE,
        source_pile=self.current_pile_index
    ))
```

#### Evento: Anteprima Tutte le Pile (tasto 'A')

**Vecchia versione:**  
```python
def PlayAnteprimaPileGioco(self):
    suono = self.lksounds["effect"]["anteprima pile"]
    self.PlayEff(suono)  # sound33.ogg
```

**Nuova versione:**  
```python
def on_key_a_press(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_NOTIFICATION
    ))
    # ... lettura anteprima pile ...
```

#### Evento: Conferma Selezione (Enter)

**Vecchia versione:**  
```python
def PlayConfirmSelect(self):
    suono = self.lksounds["effect"]["confirm"]
    self.PlayEff(suono)  # sound1.ogg
```

**Nuova versione:**  
```python
def on_enter_press(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_SELECT
    ))
    # ... azione confermata ...
```

#### Evento: Annullamento (Esc)

**Vecchia versione:**  
```python
def PlayAbortQuitGame(self):
    suono = self.lksounds["effect"]["abort quitgame"]
    self.PlayEff(suono)  # sound29.ogg
```

**Nuova versione:**  
```python
def on_escape_press(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_CANCEL
    ))
    # ... azione annullata ...
```

---

### 4.2 Finestre di Dialogo Yes/No

**File:** Gestore finestre di conferma (es. quit game, new game)

#### Evento: Toggle Si/No (↑/↓)

**Vecchia versione:**  
```python
def PlaySelect_YN(self):
    suono = self.lksounds["effect"]["move yn"]
    self.PlayEff(suono)  # sound2.ogg
```

**Nuova versione:**  
```python
def on_yes_no_toggle(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_TOGGLE
    ))
    # ... cambio selezione Si/No ...
```

#### Evento: Conferma Yes/No (Enter)

**Vecchia versione:**  
```python
def PlayConfirm_YN(self):
    suono = self.lksounds["effect"]["confirm yn"]
    self.PlayEff(suono)  # sound3.ogg
```

**Nuova versione:**  
```python
def on_yes_no_confirm(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_CONFIRM
    ))
    # ... conferma scelta ...
```

#### Evento: Richiesta Conferma Abbandono

**Vecchia versione:**  
```python
def PlayQuestionQuitGame(self):
    suono = self.lksounds["effect"]["question quitgame"]
    self.PlayEff(suono)  # sound101.ogg
```

**Nuova versione:**  
```python
def show_quit_confirmation_dialog(self):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_ERROR  # alert/warning sonoro
    ))
    # ... mostra dialogo conferma ...
```

---

### 4.3 Gameplay - Gestione Carte

**File:** Controller logica di gioco (es. `GameController` o gestore mosse)

#### Evento: Spostamento Carte Multiplo

**Vecchia versione:**  
```python
def PlaySoundSpostamento(self):
    if self.typemove == 1:  # multiplo
        suono = self.lksounds["effect"]["spostamento2"]
        self.PlayEff(suono)  # solve.ogg
```

**Nuova versione:**  
```python
def execute_multi_card_move(self, source_pile, dest_pile, card_count):
    # ... logica spostamento ...
    if card_count > 1:
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.MULTI_CARD_MOVE,
            source_pile=source_pile,
            destination_pile=dest_pile
        ))
    else:
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.TABLEAU_DROP,
            source_pile=source_pile,
            destination_pile=dest_pile
        ))
```

#### Evento: Carte Esaurite (Mazzo + Scarti Vuoti)

**Vecchia versione:**  
```python
def PlayCarteFinite(self):
    suono = self.lksounds["effect"]["scarti finiti"]
    self.PlayEff(suono)  # sound59.ogg
```

**Nuova versione:**  
```python
def on_stock_draw_attempt(self):
    if self.is_stock_empty() and self.is_waste_empty():
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.CARDS_EXHAUSTED
        ))
        # ... feedback utente ...
        return
    # ... procedi con pescata ...
```

#### Evento: Rimischia Scarti nel Mazzo

**Vecchia versione:**  
```python
def PlayRistoraMazzo(self):
    suono = self.lksounds["effect"]["ristora mazzo"]
    self.PlayEff(suono)  # shuffle-cards-2.ogg
```

**Nuova versione:**  
```python
def recycle_waste_to_stock(self):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.CARD_SHUFFLE_WASTE
    ))
    # ... logica rimescolamento ...
```

#### Evento: Carta Scoperta

**Nuova implementazione:**  
```python
def flip_card_face_up(self, pile_index, card_index):
    # ... logica scoprire carta ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.CARD_FLIP,
        source_pile=pile_index
    ))
```

---

### 4.4 Gestione Partita

**File:** Controller ciclo vita partita (es. `GameLifecycleController`)

#### Evento: Nuova Partita (Mischia Carte)

**Vecchia versione:**  
```python
def PlayNewGame(self):
    suono = self.lksounds["effect"]["new game"]
    self.PlayEff(suono)  # shuffle-cards-1.ogg
```

**Nuova versione:**  
```python
def start_new_game(self):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.CARD_SHUFFLE
    ))
    # ... inizializzazione partita ...
```

#### Evento: Distribuzione Carte (Mazziere)

**Vecchia versione:**  
```python
def PlayMazziere(self):
    suono = self.lksounds["effect"]["mazziere"]
    self.PlayEff(suono)  # arteries.ogg
```

**Nuova versione:**  
```python
def deal_initial_cards(self):
    # Riuso del suono shuffle
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.CARD_SHUFFLE
    ))
    # ... distribuzione carte nelle pile ...
```

#### Evento: Messaggio Benvenuto

**Vecchia versione:**  
```python
def PlayWelcome(self):
    if self.lang == "it":
        welcome = self.lksounds["welcome"]["it"] 
    elif self.lang == "eng":
        welcome = self.lksounds["welcome"]["eng"] 
    self.PlayEff(welcome)
```

**Nuova versione:**  
```python
def show_welcome_screen(self):
    # File mappato in config: welcome_italian.wav o welcome_english.wav
    # La localizzazione sarà gestita a livello di config o context
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.WELCOME_MESSAGE,
        context={"language": self.current_language}
    ))
```

**Nota:** Per supportare la localizzazione dinamica del messaggio di benvenuto, sarà necessario estendere `AudioManager` per gestire varianti linguistiche. Alternativa temporanea: mappare sempre su `welcome_italian.wav` e cambiare manualmente il file nella config.

---

### 4.5 Settings e Configurazione

**File:** Controller impostazioni (es. `SettingsController` o pannello settings)

#### Evento: Salvataggio Impostazioni

**Vecchia versione:**  
```python
def PlaySaveSettings(self):
    suono = self.lksounds["effect"]["save settings"]
    self.PlayEff(suono)  # sound36.ogg
```

**Nuova versione:**  
```python
def save_settings(self):
    # ... salvataggio su file ...
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.SETTING_SAVED
    ))
```

#### Evento: Cambio Difficoltà

**Vecchia versione:**  
```python
def PlayChangeLevel(self):
    suono = self.lksounds["effect"]["change level"]
    self.PlayEff(suono)  # sound55.ogg
```

**Nuova versione:**  
```python
def on_difficulty_changed(self, new_level):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.SETTING_LEVEL_CHANGED
    ))
```

#### Evento: Cambio Volume

**Vecchia versione:**  
```python
def PlayChangeVolume(self):
    suono = self.lksounds["effect"]["change volume"]
    self.PlayEff(suono)  # sound53.ogg
```

**Nuova versione:**  
```python
def on_volume_changed(self, bus_name, new_volume):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.SETTING_VOLUME_CHANGED
    ))
```

#### Evento: Cambio Brano Musicale

**Vecchia versione:**  
```python
def PlayChangeMusic(self):
    suono = self.lksounds["effect"]["change music"]
    self.PlayEff(suono)  # sound111.ogg
```

**Nuova versione:**  
```python
def on_music_track_changed(self):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.SETTING_MUSIC_CHANGED
    ))
```

#### Evento: Switch ON/OFF

**Vecchia versione:**  
```python
def PlaySwitchOn(self):
    suono = self.lksounds["effect"]["switch on"]
    self.PlayEff(suono)  # sound102.ogg
    
def PlaySwitchOff(self):
    suono = self.lksounds["effect"]["switch off"]
    self.PlayEff(suono)  # sound103.ogg
```

**Nuova versione:**  
```python
def on_setting_toggle(self, setting_name, is_enabled):
    if is_enabled:
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.SETTING_SWITCH_ON
        ))
    else:
        self.audio_manager.play_event(AudioEvent(
            event_type=AudioEventType.SETTING_SWITCH_OFF
        ))
```

---

### 4.6 Menu e Pulsanti

**File:** Gestori UI per menu e controlli wx

#### Evento: Apertura/Chiusura Menu

**Nuova implementazione:**  
```python
def on_menu_opened(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_MENU_OPEN
    ))
    
def on_menu_closed(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_MENU_CLOSE
    ))
```

#### Evento: Click e Hover Pulsanti

**Nuova implementazione:**  
```python
def on_button_hover(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_BUTTON_HOVER
    ))
    
def on_button_clicked(self, event):
    self.audio_manager.play_event(AudioEvent(
        event_type=AudioEventType.UI_BUTTON_CLICK
    ))
```

---

## 5. Testing e Validazione

### 5.1 Checklist Test Audio Events

**Navigazione:**
- [ ] Frecce su/giù menu → `UI_NAVIGATE`
- [ ] Tab cambio frame → `UI_NAVIGATE_FRAME`
- [ ] Frecce sinistra/destra pile → `UI_NAVIGATE_PILE`
- [ ] Tasto 'A' anteprima pile → `UI_NOTIFICATION`
- [ ] Enter conferma → `UI_SELECT`
- [ ] Escape annulla → `UI_CANCEL`

**Dialoghi Yes/No:**
- [ ] Toggle Si/No → `UI_TOGGLE`
- [ ] Conferma scelta → `UI_CONFIRM`
- [ ] Richiesta conferma abbandono → `UI_ERROR`

**Gameplay:**
- [ ] Spostamento singolo carta → `TABLEAU_DROP`
- [ ] Spostamento multiplo carte → `MULTI_CARD_MOVE`
- [ ] Carte esaurite → `CARDS_EXHAUSTED`
- [ ] Rimischia scarti → `CARD_SHUFFLE_WASTE`
- [ ] Carta scoperta → `CARD_FLIP`

**Partita:**
- [ ] Nuova partita → `CARD_SHUFFLE`
- [ ] Benvenuto → `WELCOME_MESSAGE`
- [ ] Vittoria → `GAME_WON`

**Settings:**
- [ ] Salva impostazioni → `SETTING_SAVED`
- [ ] Cambio difficoltà → `SETTING_LEVEL_CHANGED`
- [ ] Cambio volume → `SETTING_VOLUME_CHANGED`
- [ ] Cambio musica → `SETTING_MUSIC_CHANGED`
- [ ] Switch ON → `SETTING_SWITCH_ON`
- [ ] Switch OFF → `SETTING_SWITCH_OFF`

**Menu/UI:**
- [ ] Apertura menu → `UI_MENU_OPEN`
- [ ] Chiusura menu → `UI_MENU_CLOSE`
- [ ] Click pulsante → `UI_BUTTON_CLICK`
- [ ] Hover pulsante → `UI_BUTTON_HOVER`

### 5.2 Test di Regressione

Verificare che gli eventi esistenti funzionino ancora correttamente:
- [ ] `CARD_MOVE` (già implementato)
- [ ] `STOCK_DRAW` (già implementato)
- [ ] `INVALID_MOVE` (già implementato)
- [ ] Tutti i test unitari audio esistenti passano

---

## 6. Note Implementative

### 6.1 Priorità di Implementazione

**Fase 1 (MUST HAVE):**
1. Aggiunta eventi a `audio_events.py`
2. Aggiornamento `audio_config.json`
3. Navigazione menu/UI (`UI_NAVIGATE_*`)
4. Gameplay core (spostamenti, scarti)
5. Gestione partita (new game, vittoria)

**Fase 2 (SHOULD HAVE):**
6. Dialoghi conferma Yes/No
7. Settings (salvataggio, cambio opzioni)
8. Menu e pulsanti

**Fase 3 (NICE TO HAVE):**
9. Welcome message localizzato
10. Ottimizzazioni performance
11. Sound pack alternativi

### 6.2 Gestione Riuso File Audio

Diversi eventi condividono lo stesso file audio. Questo è intenzionale:
- `UI_FOCUS_CHANGE` / `SETTING_CHANGED` / `SETTING_LEVEL_CHANGED` → `focus_change.wav`
- `UI_SELECT` / `SETTING_SAVED` → `select.wav`
- `CARD_SHUFFLE` / distribuzione carte → `card_shuffle.wav`

Il riuso intelligente riduce la dimensione del progetto mantenendo feedback coerente.

### 6.3 Compatibilità con Sistema Esistente

- **Nessuna modifica breaking** ai metodi pubblici di `AudioManager`
- Gli eventi esistenti continuano a funzionare identicamente
- La configurazione è backward-compatible (basta commentare i nuovi eventi in `enabled_events` per disabilitarli)

### 6.4 Estensioni Future

**Localizzazione Welcome Message:**
Per gestire correttamente i messaggi di benvenuto multilingua:
1. Modificare `AudioManager.play_event()` per controllare `context["language"]`
2. Mappare dinamicamente su `welcome_italian.wav` o `welcome_english.wav`
3. Alternativa: creare eventi separati `WELCOME_MESSAGE_IT` / `WELCOME_MESSAGE_EN`

**Sound Pack Personalizzati:**
L'utente potrà creare cartelle `assets/sounds/custom_pack/` con gli stessi file, e cambiare `active_sound_pack` in config.

---

## 7. Checklist Implementazione Copilot

### Step 1: Modifica `audio_events.py`
```bash
# Apri file
open src/infrastructure/audio/audio_events.py

# Aggiungi i 21 nuovi eventi alla classe AudioEventType
# (copia dal punto 2 di questo documento)
```

### Step 2: Modifica `audio_config.json`
```bash
# Apri file
open config/audio_config.json

# Sostituisci la sezione event_sounds e enabled_events
# (copia dal punto 3 di questo documento)
```

### Step 3: Identifica Handler Eventi Tastiera
```bash
# Trova i metodi che gestiscono input utente
grep -r "def on_.*key" src/presentation/
grep -r "KeyDown" src/presentation/
grep -r "EVT_KEY" src/presentation/
```

### Step 4: Inserisci Chiamate Audio
- Cerca i punti identificati nel punto 4 di questo documento
- Aggiungi `self.audio_manager.play_event(AudioEvent(...))` nei punti appropriati
- Segui pattern:
  ```python
  # Prima della logica o subito dopo
  self.audio_manager.play_event(AudioEvent(
      event_type=AudioEventType.NOME_EVENTO,
      source_pile=opzionale,
      destination_pile=opzionale
  ))
  ```

### Step 5: Testing
```bash
# Esegui test unitari audio
pytest tests/infrastructure/audio/ -v

# Test manuale: avvia app e verifica ogni evento della checklist (punto 5)
python acs_wx.py
```

### Step 6: Commit
```bash
git add src/infrastructure/audio/audio_events.py
git add config/audio_config.json
git add src/presentation/  # (file modificati con chiamate audio)
git commit -m "feat(audio): espansione eventi audio per parità con vecchia versione

- Aggiunti 21 nuovi AudioEvent per feedback granulare
- Mappati tutti gli effetti sonori della versione pygame originale
- Implementati riuso intelligente file audio (focus_change, select, etc.)
- Mantenuta backward compatibility con sistema esistente

Ref: docs/3 - coding plans/audio_event_expansion_plan.md"
```

---

## 8. Risorse e Riferimenti

**File Modificati:**
- `src/infrastructure/audio/audio_events.py` (+21 eventi)
- `config/audio_config.json` (configurazione completa)
- `src/presentation/wx_ui/*.py` (handler eventi, da identificare)

**File Audio Utilizzati:**
- `assets/sounds/default/gameplay/*.wav` (9 file)
- `assets/sounds/default/ui/*.wav` (13 file)
- `assets/sounds/default/voice/*.wav` (6 file)

**Documentazione Correlata:**
- `docs/2 - technical specs/audio_system_architecture.md`
- Vecchia implementazione: `AccessibleClassicSolitair/pygame_interface.py`

**Conteggio Finale:**
- Eventi vecchia versione: ~25
- Eventi nuova versione (attuali): 12
- Nuovi eventi aggiunti: +21
- **Totale eventi nuova versione: 33** (parità raggiunta + estensioni)

---

## Appendice: Tabella Comparativa Completa

| Evento Vecchio | File Vecchio | Evento Nuovo | File Nuovo | Bus | Status |
|----------------|--------------|--------------|------------|-----|--------|
| movecursor | sound58.ogg | UI_NAVIGATE | navigate.wav | ui | ✓ Esistente |
| scorri frame | sound62.ogg | UI_NAVIGATE_FRAME | navigate_alt.wav | ui | ✅ Nuovo |
| scorri pile | sound61.ogg | UI_NAVIGATE_PILE | focus_change.wav | ui | ✅ Nuovo |
| anteprima pile | sound33.ogg | UI_NOTIFICATION | notification.wav | ui | ✅ Nuovo |
| confirm | sound1.ogg | UI_SELECT | select.wav | ui | ✓ Esistente |
| abort/cancel | sound29.ogg | UI_CANCEL | cancel.wav | ui | ✓ Esistente |
| move yn | sound2.ogg | UI_TOGGLE | button_hover.wav | ui | ✅ Nuovo |
| confirm yn | sound3.ogg | UI_CONFIRM | confirm.wav | ui | ✅ Nuovo |
| question quit | sound101.ogg | UI_ERROR | error.wav | ui | ✅ Nuovo |
| scorri carte | sound84.ogg | CARD_MOVE | card_move.wav | gameplay | ✓ Esistente |
| draw1 | sound11.ogg | STOCK_DRAW | stock_draw.wav | gameplay | ✓ Esistente |
| spostamento fallito | sound7.ogg | INVALID_MOVE | invalid_move.wav | gameplay | ✓ Esistente |
| spostamento1 | speed.ogg | TABLEAU_DROP | tableau_drop.wav | gameplay | ✅ Nuovo |
| spostamento2 | solve.ogg | MULTI_CARD_MOVE | foundation_drop.wav | gameplay | ✅ Nuovo |
| scarti finiti | sound59.ogg | CARDS_EXHAUSTED | boundary_hit.wav | ui | ✅ Nuovo |
| new game | shuffle-cards-1.ogg | CARD_SHUFFLE | card_shuffle.wav | gameplay | ✅ Nuovo |
| mazziere | arteries.ogg | (riuso) CARD_SHUFFLE | card_shuffle.wav | gameplay | ✅ Riuso |
| ristora mazzo | shuffle-cards-2.ogg | CARD_SHUFFLE_WASTE | card_shuffle_alt.wav | gameplay | ✅ Nuovo |
| winner | level.ogg | GAME_WON | victory.wav | voice | ✓ Esistente |
| welcome-it | welcome-it.ogg | WELCOME_MESSAGE | welcome_italian.wav | voice | ✅ Nuovo |
| welcome-eng | welcome-eng.ogg | WELCOME_MESSAGE | welcome_english.wav | voice | ✅ Nuovo |
| save settings | sound36.ogg | SETTING_SAVED | select.wav | ui | ✅ Riuso |
| change level | sound55.ogg | SETTING_LEVEL_CHANGED | focus_change.wav | ui | ✅ Riuso |
| change volume | sound53.ogg | SETTING_VOLUME_CHANGED | focus_change.wav | ui | ✅ Riuso |
| change music | sound111.ogg | SETTING_MUSIC_CHANGED | focus_change.wav | ui | ✅ Riuso |
| switch on | sound102.ogg | SETTING_SWITCH_ON | button_click.wav | ui | ✅ Riuso |
| switch off | sound103.ogg | SETTING_SWITCH_OFF | button_hover.wav | ui | ✅ Riuso |
| - | - | UI_MENU_OPEN | menu_open.wav | ui | ✅ Nuovo |
| - | - | UI_MENU_CLOSE | menu_close.wav | ui | ✅ Nuovo |
| - | - | UI_BUTTON_CLICK | button_click.wav | ui | ✅ Nuovo |
| - | - | UI_BUTTON_HOVER | button_hover.wav | ui | ✅ Nuovo |
| - | - | CARD_FLIP | card_flip.wav | gameplay | ✅ Nuovo |

**Legenda:**
- ✓ Esistente: già implementato nel branch attuale
- ✅ Nuovo: da aggiungere con questo piano
- ✅ Riuso: nuovo evento che riusa file esistente

---

**Fine Piano Espansione Audio**
