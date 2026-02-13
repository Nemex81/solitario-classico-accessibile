# 🎯 Piano di Refactoring: GameplayPanel, Opzioni wx e Gestione ESC

**Branch target**: `copilot/remove-pygame-migrate-wxpython`  
**Scope**: Separazione chiara tra
- pannello gameplay wx
- finestra opzioni wx
- vecchio sistema "menu virtuale" a sola tastiera

**Obiettivo**: Eliminare le ambiguità tra pannelli wx e menu virtuali, rendere il flusso:

1. Menu principale (pannello wx con pulsanti)  
2. Gameplay (pannello wx dedicato, partita visibile, tasti mappati al GamePlayController)  
3. Opzioni (finestra/dialog wx separata, con navigazione via frecce sui controlli attuali)  
4. ESC e pulsante "Chiudi" gestiti in modo consistente in tutti i contesti

Copilot deve implementare questo piano in **più commit incrementali**, ciascuno piccolo, coerente e facilmente revisionabile.

---

## 1. Stato Attuale (Sintesi Problemi)

### 1.1 Comportamento utente osservato

- INVIO su "Gioca al solitario classico" nel `MenuPanel` NON porta a un'esperienza di gameplay chiara, ma di fatto l'utente finisce in un contesto che **si comporta** come un menu virtuale delle opzioni invece che come tavolo di gioco.
- ESC non si comporta più come nei rami precedenti: non sempre abbandona la partita o torna al menu.
- Il pulsante fisico "Chiudi" della finestra non ha un comportamento consistente con il resto dell'app.

### 1.2 Architettura attuale rilevante

- `SolitarioFrame`:
  - Single-frame con `panel_container` e sizer configurato (FIX 1 già applicato).
  - Gestisce `EVT_CLOSE` e richiama `SolitarioController._on_frame_close()` → `quit_app()`.
- `ViewManager`:
  - Gestisce registrazione e swap di pannelli (`menu`, `gameplay`) via `show_panel('menu'|'gameplay')`.
- `MenuPanel`:
  - Pannello wx con `wx.Button`:
    - "Gioca al solitario classico" → `controller.start_gameplay()`
    - "Opzioni di gioco" → `controller.show_options()`
    - "Esci dal gioco" → `controller.show_exit_dialog()`
- `SolitarioController`:
  - `start_gameplay()`:
    - `view_manager.show_panel('gameplay')`
    - `engine.reset_game()`, `engine.new_game()`
  - `show_options()`:
    - Chiama `self.gameplay_controller.options_controller.open_window()` (logica opzioni attuale, in stile menu virtuale, non un vero dialog wx autonomo).
  - `confirm_abandon_game()` / `show_abandon_game_dialog()` / `show_new_game_dialog()` già esistono e gestiscono la logica di conferma partita.
- `GameplayPanel`:
  - Esiste come pannello registrato nel `ViewManager`, ma NON ha ancora una gestione completa degli eventi di tastiera wx.
- `GamePlayController`:
  - Gestisce oltre 60 comandi tastiera, ancora modellati con pygame (es. `pygame.key.get_mods()`), ma concettualmente già separati in callback logici (_cursor_up, _draw_cards, ecc.).
  - Gestisce anche la "finestra opzioni" tramite `OptionsWindowController`, ma come concetto virtuale, non come dialog wx nativo.
- `WxVirtualMenu`:
  - Menu virtuale basato solo su tasti e TTS, pensato per l'era pygame.
  - Ancora presente, potenzialmente confondente rispetto alla nuova UI wx con pannelli.

### 1.3 Root Cause dei problemi attuali

1. Gameplay e opzioni condividono ancora lo stesso "mondo di input" logico (GamePlayController + OptionsWindowController), senza una separazione chiara di contesto.
2. `GameplayPanel` non intercetta direttamente i tasti per inoltrarli a un entry point wx-specifico (tipo `handle_wx_key_event`).
3. `show_options()` apre la logica opzioni "virtuale" nel contesto del gameplay, invece di mostrare una finestra wx separata.
4. ESC non è instradato esplicitamente nei diversi contesti (menu, gameplay, opzioni), quindi l'effetto dipende da chi per primo consuma il tasto, se qualcuno lo consuma.

---

## 2. Obiettivi di Design

### 2.1 Obiettivi funzionali

1. **INVIO su "Gioca"**: mostra `GameplayPanel` e avvia una partita; l'utente non deve percepire la navigazione come un menu virtuale, ma come un contesto di gioco.
2. **Opzioni**: devono aprirsi come finestra/sezione separata, con navigazione tramite frecce sui controlli attuali, ma chiaramente distinta dal gameplay.
3. **ESC**:
   - Nel **MenuPanel**: opzionale, ma se gestito deve essere coerente (es. ESC = torna alla conferma uscita oppure ignorato).
   - Nel **GameplayPanel**: ESC deve aprire una conferma abbandono (`show_abandon_game_dialog()`), con supporto per doppio ESC (abbandono diretto) se richiesto.
   - Nelle **Opzioni**: ESC deve chiudere/annullare lo stato opzioni in modo pulito (usando `OptionsWindowController`).
4. **Pulsante "Chiudi"**: deve chiudere l'applicazione in modo coerente con `show_exit_dialog()` / `quit_app()`.

### 2.2 Obiettivi architetturali

1. Separare i ruoli:
   - `MenuPanel` → solo menu principale grafico.
   - `GameplayPanel` → contesto di gioco, inoltra tasti a GamePlayController.
   - Nuova entità **OptionsDialog** (o pannello opzioni) → contesto opzioni, inoltra tasti a OptionsWindowController.
2. Introdurre un entry point unico per i tasti wx nel `GamePlayController`:
   - `handle_wx_key_event(event: wx.KeyEvent) -> bool`
   - Gestisce mappa da codici wx ai metodi esistenti (cursor, selection, draw, ecc.).
3. Ridurre dipendenza dal vecchio `WxVirtualMenu` per i flussi principali (menu, gameplay, opzioni).

---

## 3. Piano Implementativo per Copilot (Commit Incrementali)

> Copilot: implementa i seguenti step in ordine, con **un commit per step** (o al massimo due per step più complessi). Non mescolare modifiche tra step.

### STEP 1 – Potenziare `GameplayPanel` per gestire i tasti wx

**File coinvolti**:
- `src/infrastructure/ui/gameplay_panel.py`
- (eventualmente) `src/infrastructure/ui/basic_panel.py`
- `src/application/gameplay_controller.py`

**Obiettivo**: Fare in modo che, quando il pannello `gameplay` è visibile, tutti i tasti rilevanti (frecce, spazio, invio, ecc.) siano inoltrati al `GamePlayController` tramite un metodo wx-specifico.

#### 3.1.1 Aggiungere entry point wx in `GamePlayController`

In `GamePlayController` (stesso file dove sono definiti `_cursor_up`, `_draw_cards`, ecc.):

1. Aggiungi un metodo pubblico:

```python
import wx  # in testa al file, se non presente

class GamePlayController:
    # ... codice esistente ...

    def handle_wx_key_event(self, event: 'wx.KeyEvent') -> bool:
        """Gestisce un wx.KeyEvent mappandolo ai comandi gameplay.

        Ritorna True se il tasto è stato gestito, False altrimenti.
        Non chiama event.Skip(): il chiamante decide se propagare.
        """
        key_code = event.GetKeyCode()

        # Esempio: frecce e invio
        if key_code == wx.WXK_UP:
            self._cursor_up()
            return True
        if key_code == wx.WXK_DOWN:
            self._cursor_down()
            return True
        if key_code == wx.WXK_LEFT:
            self._cursor_left()
            return True
        if key_code == wx.WXK_RIGHT:
            self._cursor_right()
            return True

        # INVIO / SPAZIO / CANC ecc. da mappare progressivamente
        # TODO: mappare tutti i tasti esistenti del callback_dict originale

        return False
```

2. NON copiare tutti i tasti in un colpo solo. In questo step mappa solo:
   - Frecce (navigazione cursore)
   - INVIO (selezione) → `_select_card()`
   - SPAZIO (sposta carte) → `_move_cards()`
   - D / P (pesca carte) → `_draw_cards()`

   Il resto può essere aggiunto in step futuri.

#### 3.1.2 Collegare `GameplayPanel` a `GamePlayController`

Nel file `gameplay_panel.py`:

1. Assicurati che il pannello abbia un riferimento al controller principale (`SolitarioController`) e tramite lui al `gameplay_controller`.
2. Override di `on_key_down(self, event: wx.KeyEvent)` (eredita da `BasicPanel`):

```python
class GameplayPanel(BasicPanel):
    # ... init_ui_elements, ecc. ...

    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Instrada i tasti al GamePlayController gameplay.

        Se il controller gestisce il tasto, non chiama event.Skip().
        Altrimenti, propaga l'evento.
        """
        # Recupera controller app (SolitarioController)
        controller = self.controller
        if controller and controller.gameplay_controller:
            handled = controller.gameplay_controller.handle_wx_key_event(event)
            if handled:
                return  # tasto consumato

        # Non gestito dal gameplay: propaga
        event.Skip()
```

3. Verificare che `BasicPanel` stia ancora facendo `Bind(wx.EVT_CHAR_HOOK, self.on_key_down)` (già presente). In caso contrario, aggiungerlo.

**Commit suggerito**:

> `feat(ui): route wx key events from GameplayPanel to GamePlayController`

---

### STEP 2 – Gestione ESC nel GameplayPanel

**File coinvolti**:
- `src/infrastructure/ui/gameplay_panel.py`
- `test.py` (per usare `show_abandon_game_dialog()` / `confirm_abandon_game()` già presenti)

**Obiettivo**: Ripristinare un comportamento chiaro di ESC durante il gameplay.

#### 3.2.1 Logica ESC nel controller

In `GamePlayController.handle_wx_key_event` aggiungi gestione esplicita per ESC:

```python
if key_code == wx.WXK_ESCAPE:
    # Delegate decision to application controller (abbandono, menu, ecc.)
    # Non gestire qui direttamente: ritorna False per farlo gestire da GameplayPanel
    return False
```

Questo permette al pannello di decidere cosa fare con ESC (conferma abbandono, ecc.).

#### 3.2.2 ESC nel `GameplayPanel`

In `GameplayPanel.on_key_down`:

```python
    def on_key_down(self, event: wx.KeyEvent) -> None:
        key_code = event.GetKeyCode()

        # Gestione ESC locale (abbandono partita / ritorno a menu)
        if key_code == wx.WXK_ESCAPE:
            if self.controller:
                # Usa show_abandon_game_dialog() per conferma
                self.controller.show_abandon_game_dialog()
            return

        # Altri tasti → GameplayController
        controller = self.controller
        if controller and controller.gameplay_controller:
            handled = controller.gameplay_controller.handle_wx_key_event(event)
            if handled:
                return

        event.Skip()
```

Più avanti, se vuoi supportare doppio ESC, potremo usare `confirm_abandon_game(skip_dialog=True)` e un timestamp nel controller, ma NON in questo step.

**Commit suggerito**:

> `feat(ui): handle ESC in GameplayPanel using controller abandon dialog`

---

### STEP 3 – Introduzione di una OptionsDialog wx

**File coinvolti**:
- Nuovo: `src/infrastructure/ui/options_dialog.py`
- `test.py` (usa il nuovo dialog in `show_options()`)
- Eventualmente: `OptionsWindowController` (già esistente)

**Obiettivo**: Spostare la logica opzioni in una finestra wx dedicata, separata dal gameplay.

#### 3.3.1 Creare `OptionsDialog`

Nuovo file: `src/infrastructure/ui/options_dialog.py`

Struttura proposta:

```python
import wx
from typing import Optional

from src.application.options_controller import OptionsWindowController


class OptionsDialog(wx.Dialog):
    """Finestra opzioni modale basata su OptionsWindowController.

    Gestisce i tasti freccia, invio, ESC e mappa il tutto
    ai metodi dell'OptionsWindowController esistente.
    """

    def __init__(self, parent: wx.Window, controller: OptionsWindowController):
        super().__init__(parent, title="Opzioni di gioco", size=(500, 400))

        self.options_controller = controller

        # Layout minimale (può contenere solo un testo descrittivo)
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Finestra opzioni. Usa frecce e invio per modificare.")
        sizer.Add(label, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(sizer)

        # Bind tasti
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

    def on_key_down(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()

        # Esempio iniziale: ESC chiude, frecce/INVIO demandati all'OptionsWindowController
        if key == wx.WXK_ESCAPE:
            # Usa il controller per annullare / chiudere
            msg = self.options_controller.cancel_close()
            # Se serve, vocalizza via screen reader (già gestito altrove)
            self.EndModal(wx.ID_CANCEL)
            return

        # TODO: mappare UP/DOWN/ENTER/1-5/T/+/- verso options_controller

        event.Skip()
```

In questo step creare solo lo scheletro, mappando almeno ESC in modo pulito.

#### 3.3.2 Collegare `show_options()` al nuovo dialog

Nel `SolitarioController.show_options()` in `test.py`:

1. Importa `OptionsDialog`:

```python
from src.infrastructure.ui.options_dialog import OptionsDialog
```

2. Modifica `show_options` per usare la dialog:

```python
def show_options(self) -> None:
    """Show options window (called from MenuView)."""
    print("\n" + "="*60)
    print("APERTURA FINESTRA OPZIONI")
    print("="*60)

    self.is_options_mode = True

    # Usa OptionsDialog con l'OptionsWindowController esistente
    dlg = OptionsDialog(parent=self.frame, controller=self.gameplay_controller.options_controller)
    dlg.ShowModal()
    dlg.Destroy()

    self.is_options_mode = False

    print("Finestra opzioni chiusa.")
    print("="*60)
```

3. NON toccare ancora il comportamento interno di `OptionsWindowController` (open_window, ecc.). Verrà adattato nello step successivo.

**Commit suggerito**:

> `feat(ui): introduce OptionsDialog wx wrapper for options controller`

---

### STEP 4 – Allineare OptionsWindowController al nuovo dialog

**File coinvolti**:
- `src/application/options_controller.py`
- `src/application/gameplay_controller.py` (eventuali riferimenti)
- `src/infrastructure/ui/options_dialog.py`

**Obiettivo**: Far sì che OptionsWindowController lavori in armonia con un dialog wx, senza dipendere da stato "virtuale" ambiguo.

#### 3.4.1 Revisione metodi di OptionsWindowController

Analizzare i metodi esistenti (es: `open_window`, `close_window`, `save_and_close`, `discard_and_close`, `cancel_close`, `navigate_up/down`, `modify_current_option`, `jump_to_option`, `increment_timer`, `decrement_timer`, `toggle_timer`, `read_all_settings`, `show_help`).

Obiettivo in questo step:

- Mantenere le firme e la logica, ma:
  - Rimuovere/ignorare eventuali assunzioni sul fatto che esista un "virtual window" non wx.
  - Esporre metodi che il dialog può chiamare direttamente quando riceve i tasti.

In `OptionsDialog.on_key_down`, mappare in modo esplicito:

```python
if key == wx.WXK_UP:
    msg = self.options_controller.navigate_up()
elif key == wx.WXK_DOWN:
    msg = self.options_controller.navigate_down()
elif key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
    msg = self.options_controller.modify_current_option()
elif key == wx.WXK_ESCAPE:
    msg = self.options_controller.cancel_close()
    self.EndModal(wx.ID_CANCEL)
    return
# 1-5 → jump_to_option
# + / - → increment/decrement_timer
# T → toggle_timer
```

Per ogni azione, se `msg` è non vuoto, delegare al `ScreenReader` già disponibile nel `GamePlayController` (in una fase successiva). Per ora il dialog può limitarsi a ignorare l'audio o stampare su console.

**Commit suggerito**:

> `refactor(options): adapt OptionsWindowController to be driven by OptionsDialog`

---

### STEP 5 – Pulizia e riduzione dipendenza da WxVirtualMenu

**File coinvolti**:
- `src/infrastructure/ui/wx_menu.py`
- eventuali punti in cui viene ancora usato `WxVirtualMenu` per flussi principali

**Obiettivo**: Assicurarsi che il flusso principale menu → gameplay → opzioni non passi più per `WxVirtualMenu`, ma usi esclusivamente pannelli wx e dialog wx.

Azione concreta:

1. Cercare dove viene istanziato `WxVirtualMenu` nel branch `copilot/remove-pygame-migrate-wxpython`.
2. Se è ancora usato per il menu principale o le opzioni principali, sostituire l'uso con:
   - `MenuPanel` per il menu principale.
   - `OptionsDialog` per le opzioni.
3. Mantenere `WxVirtualMenu` solo se ancora necessario per menu secondari o modalità "solo tastiera" non coperte dai pannelli. In caso contrario, marcare come `DEPRECATED` nel docstring.

**Commit suggerito**:

> `refactor(ui): remove WxVirtualMenu from main menu/options flow`

---

## 4. Indicazioni Generali per Copilot

1. **Non cambiare** nomi pubblici già usati dal resto del codice (`start_gameplay`, `show_options`, `show_exit_dialog`, `show_abandon_game_dialog`, `confirm_abandon_game`, ecc.).
2. **Mantieni i commenti esistenti** e aggiungi commenti sintetici solo dove serve chiarire il nuovo flusso (es. "# Route wx key events to GamePlayController").
3. **Commits piccoli e coerenti**:
   - Ogni step descritto sopra deve essere un commit separato.
   - Nessun refactoring massivo trasversale nello stesso commit.
4. **Rispetto del comportamento esistente**:
   - Non modificare la logica di `GameEngine`, `GameSettings`, `GamePlayController` oltre alle parti esplicitamente indicate.
   - Non cambiare la firma dei metodi pubblici già usati dal resto dell'app.
5. **Testing manuale raccomandato dopo STEP 2 e STEP 3**:
   - STEP 2: `python test.py`
     - INVIO su "Gioca" → dovrebbe mostrare il pannello gameplay.
     - Frecce e tasti base dovrebbero muovere il cursore (nei limiti dei tasti mappati).
     - ESC in gameplay → dialog di abbandono partita.
   - STEP 3: `python test.py`
     - INVIO su "Opzioni" dal menu → si apre `OptionsDialog`.
     - ESC dentro il dialog → chiude le opzioni e torna al menu.

---

## 5. Messaggi di commit in serie (suggeriti)

1. `feat(ui): route wx key events from GameplayPanel to GamePlayController`
2. `feat(ui): handle ESC in GameplayPanel using controller abandon dialog`
3. `feat(ui): introduce OptionsDialog wx wrapper for options controller`
4. `refactor(options): adapt OptionsWindowController to be driven by OptionsDialog`
5. `refactor(ui): remove WxVirtualMenu from main menu/options flow`

---

## 6. Stato finale desiderato

Alla fine di questi step, il comportamento deve essere:

- Dal menu principale:
  - INVIO su "Gioca al solitario classico" → `start_gameplay()` → `GameplayPanel` visibile, partita avviata.
  - INVIO su "Opzioni di gioco" → `show_options()` → `OptionsDialog` modale, con navigazione frecce/INVIO.
  - INVIO su "Esci dal gioco" → `show_exit_dialog()` → conferma uscita.
- In gameplay:
  - Frecce / INVIO / SPAZIO / altri tasti gestiti da `GamePlayController.handle_wx_key_event` tramite `GameplayPanel.on_key_down`.
  - ESC → `show_abandon_game_dialog()` → conferma ritorno al menu.
- In opzioni:
  - Frecce / INVIO / numeri / T / +/- mappati a `OptionsWindowController`.
  - ESC → chiusura opzioni (con eventuale conferma tramite metodi del controller).
- Nessun passaggio del flusso principale dipende più da `WxVirtualMenu`.

Questo documento è pensato per essere la fonte unica di verità per Copilot durante l'implementazione incrementale delle modifiche.