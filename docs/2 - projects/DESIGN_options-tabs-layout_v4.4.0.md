---
type: design
feature: options-tabs-layout
version: v4.4.0
status: REVIEWED
agent: Agent-Design
date: 2026-04-09
---

# DESIGN: Options Tabs Layout v4.4.0

## 1. Idea in 3 righe

La finestra opzioni attuale accumula 11 controlli in un solo flusso verticale, con carico cognitivo alto e nessuna separazione semantica tra gameplay, accessibilità, audio e preferenze visive. La soluzione introduce un `wx.Notebook` con tab logiche e accessibili, mantiene i pulsanti Salva/Annulla fuori dalle pagine e conserva il binding live verso `GameSettings` senza cambiare il contratto del controller. In parallelo correggiamo due incoerenze emerse nell’analisi: snapshot incompleto del controller (`draw_count`) e widget tema visivo non omogeneo per NVDA.

---

## 2. Attori e Concetti

### Attori software coinvolti

- `OptionsDialog` in `src/infrastructure/ui/options_dialog.py`: dialogo wx principale da rifattorizzare in layout a tab.
- `OptionsWindowController` in `src/application/options_controller.py`: gestisce snapshot, dirty state e rollback; resta separato dal layout ma necessita del fix snapshot su `draw_count`.
- `GameSettings` in `src/domain/services/game_settings.py`: sorgente di verità dei valori, nessun cambiamento strutturale richiesto.
- `OptionsFormatter` in `src/presentation/options_formatter.py`: testo TTS legacy; va riallineato ai comandi reali del dialogo wx.
- `TimerComboBox` in `src/infrastructure/ui/widgets/timer_combobox.py`: controllo custom già compatibile con NVDA, da riusare nel tab Gameplay.

### Categorie UX introdotte

- Generale: tipo mazzo, difficoltà.
- Gameplay: carte pescate, timer, modalità timer, riciclo scarti.
- Audio e Accessibilità: suggerimenti comandi, sistema punti, avvisi soglie punteggio.
- Visuale: modalità display, tema visivo.

### Concetti chiave

- `wx.Notebook` come contenitore di alto livello per ridurre lunghezza verticale e migliorare scanning.
- Focus iniziale e cambio tab guidati per NVDA: ogni pagina espone il primo controllo logico e riceve focus esplicito al cambio scheda.
- Ordine TAB locale a ogni pannello, con pulsanti finali sempre esterni al notebook.
- Live update invariato: il dialogo continua a salvare nei `GameSettings` a ogni modifica e usa lo snapshot del controller solo per rollback.

---

## 3. Flussi Concettuali

### 3.1 Flusso attuale

`OptionsDialog._create_ui()` crea un unico `wx.BoxSizer` verticale con tutti i gruppi in sequenza. L’utente deve attraversare ogni controllo per raggiungere una sezione successiva, e la gerarchia concettuale è implicita solo nei `StaticBoxSizer`.

### 3.2 Flusso proposto

`OptionsDialog._create_ui()` crea:

1. un `wx.Notebook`;
2. quattro `wx.Panel` interni (`Generale`, `Gameplay`, `Audio e Accessibilità`, `Visuale`);
3. un sizer verticale per ogni pagina con i soli controlli della categoria;
4. una mappa `tab -> first_focus_widget` usata da `EVT_NOTEBOOK_PAGE_CHANGED`;
5. pulsanti `Salva` e `Annulla` nel contenitore principale del dialogo, fuori dal notebook.

Il binding degli eventi resta centralizzato e il salvataggio widget -> settings non cambia semanticamente.

---

## 4. Decisioni Architetturali

### 4.1 Notebook con 4 tab invece di colonne multiple

Decisione: usare `wx.Notebook`, non layout a due colonne.

Motivazione: i tab riducono meglio il rumore cognitivo, si leggono bene con NVDA e rendono la UI più simile a un pannello impostazioni moderno.

### 4.2 Tema visivo convertito da `wx.Choice` a `wx.RadioBox`

Decisione: sostituire `visual_theme_choice` con `visual_theme_radio`.

Motivazione: con 3 sole opzioni il `RadioBox` è più consistente con gli altri controlli e più prevedibile per NVDA.

### 4.3 Fix snapshot controller senza redesign del controller

Decisione: aggiungere `draw_count` allo snapshot del controller e riallineare l’help TTS, senza introdurre conoscenza dei tab in `OptionsWindowController`.

Motivazione: il layout deve restare responsabilità del dialogo; il controller continua a gestire solo stato e rollback.

### 4.4 Accessibilità come vincolo di primo livello

Decisione: ad ogni cambio pagina chiamare `SetFocus()` sul primo controllo logico; mantenere nomi tab espliciti in italiano; non nascondere i controlli locked.

Motivazione: NVDA annuncia correttamente i tab ma beneficia di focus esplicito sul contenuto attivo.

---

## 5. Vincoli

- Nessuna modifica a `.github/**`.
- Nessun commit automatico.
- Compatibilità con Windows + NVDA prioritaria.
- Preservare `audio_manager`, `screen_reader`, save/cancel e live update già esistenti.
- Non rompere i test esistenti del controller; aggiungere smoke test UI mirati sul notebook.

---

## 6. File previsti

- `src/infrastructure/ui/options_dialog.py`
- `src/application/options_controller.py`
- `src/presentation/options_formatter.py`
- `tests/unit/presentation/test_options_dialog_audio.py`
- nuovo file test UI notebook se utile

---

## 7. Esito atteso

La finestra opzioni risulta organizzata per dominio funzionale, con meno scrolling mentale, migliore orientamento da tastiera e screen reader, e comportamento invariato su save/cancel/rollback.
