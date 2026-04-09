"""OptionsDialog - wxPython modal dialog for game options with native widgets.

This module provides a wxPython-based options dialog with native wx widgets
(RadioBox, CheckBox, ComboBox) for all 9 game options. Replaces virtual audio-only
navigation with standard wx TAB navigation and visual controls.

Version: v1.9.0 - Added 9th option (score warning level)
Pattern: Modal dialog with native wx controls + event binding
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Features (v1.8.0):
- Native wx.RadioBox for multi-choice options (deck type, difficulty, etc.)
- Native wx.CheckBox for boolean options (timer enable, hints, scoring)
- Native wx.ComboBox for timer duration selection
- Standard TAB navigation between widgets
- Arrow keys to change values within RadioBox/ComboBox
- SPACE to toggle CheckBox
- Salva/Annulla buttons (ALT+S/ALT+A mnemonics)
- Smart ESC with save confirmation if modifications present
- Automatic NVDA screen reader support (no custom TTS needed)

Usage (v1.8.0):
    >>> from src.application.options_controller import OptionsWindowController
    >>> from src.infrastructure.accessibility.screen_reader import ScreenReader
    >>> controller = OptionsWindowController(settings)
    >>> controller.open_window()  # Initialize state + snapshot
    >>> dlg = OptionsDialog(parent=frame, controller=controller, screen_reader=sr)
    >>> result = dlg.ShowModal()  # wx.ID_OK (saved) or wx.ID_CANCEL (discarded)
    >>> dlg.Destroy()
"""

import wx
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.infrastructure.accessibility.screen_reader import ScreenReader

from src.application.options_controller import OptionsWindowController


class OptionsDialog(wx.Dialog):
    """Modal options dialog with native wx widgets for all 9 options.
    
    Provides a wxPython native dialog with visual controls for game options.
    Uses standard wx navigation (TAB between widgets, arrows within widgets).
    
    Features (v1.9.0):
    - 9 options with native wx widgets
    - RadioBox for multi-choice options (6 total)
    - CheckBox for boolean options (2 total)
    - ComboBox for timer duration
    - Salva/Annulla buttons
    - Smart ESC with save confirmation
    - Live settings update (changes immediately applied)
    - Rollback on cancel (restore original snapshot)
    - NVDA reads all widgets automatically
    
    Navigation:
    - TAB: Move between widgets
    - UP/DOWN: Change value in RadioBox/ComboBox
    - SPACE: Toggle CheckBox
    - ENTER: Activate focused button
    - ESC: Smart close (ask confirmation if modifications present)
    
    Example:
        >>> settings = GameSettings()
        >>> options_ctrl = OptionsWindowController(settings)
        >>> options_ctrl.open_window()  # Required: Init state
        >>> dlg = OptionsDialog(parent=main_frame, controller=options_ctrl)
        >>> result = dlg.ShowModal()
        >>> if result == wx.ID_OK:
        >>>     print("Settings saved")
        >>> elif result == wx.ID_CANCEL:
        >>>     print("Settings discarded")
        >>> dlg.Destroy()
    
    Note:
        Virtual navigation (arrows/numbers 1-8) removed in v1.8.0.
        Use standard wx TAB navigation instead.
    """
    
    def __init__(
        self,
        parent: wx.Window,
        controller: OptionsWindowController,
        screen_reader: Optional['ScreenReader'] = None,
        audio_manager=None,
        title: str = "Opzioni di gioco",
        size: tuple[int, int] = (760, 680)
    ):
        """Initialize OptionsDialog with native wx widgets.
        
        Args:
            parent: Parent window (typically main frame)
            controller: OptionsWindowController instance (must call open_window() before)
            screen_reader: ScreenReader for optional TTS feedback
            audio_manager: Optional AudioManager for sound effects (v3.5.0)
            title: Dialog title (default: "Opzioni di gioco")
            size: Dialog size in pixels (default: 600x700 for all widgets)
        
        Attributes:
            options_controller: Reference to OptionsWindowController
            screen_reader: Reference to ScreenReader for TTS
            audio_manager: Reference to AudioManager for audio events (v3.5.0)
            deck_type_radio: RadioBox for deck type (Francese/Napoletano)
            difficulty_radio: RadioBox for difficulty (5 levels)
            draw_count_radio: RadioBox for draw count (1/2/3)
            timer_combo: TimerComboBox for timer duration (0=disabled, 5-60 min)
            shuffle_radio: RadioBox for shuffle mode (Inversione/Mescolata)
            command_hints_check: CheckBox for command hints (ON/OFF)
            scoring_check: CheckBox for scoring system (ON/OFF)
            timer_strict_radio: RadioBox for timer strict mode (STRICT/PERMISSIVE)
            score_warning_radio: RadioBox for score warning level (4 levels)
            btn_save: Save button (ALT+S)
            btn_cancel: Cancel button (ALT+A)
        
        Note:
            Controller.open_window() must be called before creating dialog.
            This saves settings snapshot for change tracking and rollback.
        
        Version:
            v3.5.0: Added optional audio_manager parameter
        """
        super().__init__(
            parent=parent,
            title=title,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.options_controller = controller
        self.screen_reader = screen_reader
        self.audio_manager = audio_manager
        self._options_notebook: wx.Notebook | None = None
        self._tab_focus_targets: dict[int, wx.Window] = {}
        
        # Create native wx widgets UI
        self._create_ui()
        
        # Bind ESC key for smart close
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
        # Center dialog on parent
        self.Centre()
    
    def _create_ui(self) -> None:
        """Create the options UI grouped into accessible notebook tabs."""
        from src.infrastructure.ui.widgets.timer_combobox import TimerComboBox

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self)
        self._options_notebook = notebook

        general_page, general_sizer = self._create_notebook_page("Generale")
        gameplay_page, gameplay_sizer = self._create_notebook_page("Gameplay")
        audio_page, audio_sizer = self._create_notebook_page("Audio e Accessibilità")
        visual_page, visual_sizer = self._create_notebook_page("Visuale")

        self.deck_type_radio = wx.RadioBox(
            general_page,
            label="Seleziona il tipo di mazzo da usare:",
            choices=["Francese (52 carte)", "Napoletano (40 carte)"],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(general_sizer, general_page, "Tipo Mazzo", self.deck_type_radio)

        self.difficulty_radio = wx.RadioBox(
            general_page,
            label="Livello di difficoltà:",
            choices=[
                "Livello 1 - Principiante",
                "Livello 2 - Facile",
                "Livello 3 - Normale",
                "Livello 4 - Esperto",
                "Livello 5 - Maestro",
            ],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(general_sizer, general_page, "Difficoltà", self.difficulty_radio)

        self.draw_count_radio = wx.RadioBox(
            gameplay_page,
            label="Numero di carte pescate dal mazzo ad ogni click:",
            choices=["1 carta", "2 carte", "3 carte"],
            majorDimension=3,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(gameplay_sizer, gameplay_page, "Carte Pescate per Turno", self.draw_count_radio)

        timer_box = wx.StaticBoxSizer(wx.VERTICAL, gameplay_page, "Timer Partita")
        timer_label = wx.StaticText(
            gameplay_page,
            label="Seleziona durata timer (0 = disattivato):",
        )
        timer_box.Add(timer_label, 0, wx.ALL, 5)
        self.timer_combo = TimerComboBox(gameplay_page)
        timer_box.Add(self.timer_combo, 0, wx.ALL | wx.EXPAND, 5)
        gameplay_sizer.Add(timer_box, 0, wx.ALL | wx.EXPAND, 10)

        self.timer_strict_radio = wx.RadioBox(
            gameplay_page,
            label="Comportamento quando il timer scade:",
            choices=[
                "STRICT (sconfitta automatica)",
                "PERMISSIVE (penalità punti, partita continua)",
            ],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(gameplay_sizer, gameplay_page, "Modalità Timer", self.timer_strict_radio)

        self.shuffle_radio = wx.RadioBox(
            gameplay_page,
            label="Modalità di riciclo quando il tallone è vuoto:",
            choices=["Inversione (ribalta mazzo scarti)", "Mescolata (rimescola scarti)"],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(gameplay_sizer, gameplay_page, "Riciclo Scarti", self.shuffle_radio)

        self.command_hints_check = wx.CheckBox(
            audio_page,
            label="Suggerimenti comandi attivi (mostra aiuto per comandi disponibili)",
        )
        self._add_group(audio_sizer, audio_page, "Navigazione Assistita", self.command_hints_check)

        self.scoring_check = wx.CheckBox(
            audio_page,
            label="Sistema punti attivo (calcola punteggio durante partita)",
        )
        self._add_group(audio_sizer, audio_page, "Sistema Punti", self.scoring_check)

        self.score_warning_radio = wx.RadioBox(
            audio_page,
            label="Livello di verbosità degli avvisi TTS per penalità punteggio:",
            choices=[
                "DISABLED (nessun avviso)",
                "MINIMAL (solo primo avviso)",
                "BALANCED (avvisi soglie critiche)",
                "COMPLETE (tutti gli avvisi)",
            ],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(audio_sizer, audio_page, "Avvisi Soglie Punteggio", self.score_warning_radio)

        self.display_mode_radio = wx.RadioBox(
            visual_page,
            label="Scegli la modalità di visualizzazione del gioco:",
            choices=[
                "Solo Audio (solo TTS, nessuna grafica)",
                "Visiva (rendering grafico delle carte)",
            ],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(visual_sizer, visual_page, "Modalità Display", self.display_mode_radio)

        self.visual_theme_radio = wx.RadioBox(
            visual_page,
            label="Tema grafico (usato solo in modalità visiva):",
            choices=["Standard", "Alto Contrasto", "Grande"],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._add_group(visual_sizer, visual_page, "Tema Visivo", self.visual_theme_radio)

        notebook.AddPage(general_page, "Generale")
        notebook.AddPage(gameplay_page, "Gameplay")
        notebook.AddPage(audio_page, "Audio e Accessibilità")
        notebook.AddPage(visual_page, "Visuale")

        self._tab_focus_targets = {
            0: self.deck_type_radio,
            1: self.draw_count_radio,
            2: self.command_hints_check,
            3: self.display_mode_radio,
        }

        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 10)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_save = wx.Button(self, id=wx.ID_OK, label="&Salva modifiche")
        self.btn_save.SetToolTip("Salva le modifiche e chiudi la finestra opzioni (ALT+S)")
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="&Annulla modifiche")
        self.btn_cancel.SetToolTip("Annulla le modifiche e chiudi la finestra opzioni (ALT+A)")
        button_sizer.Add(self.btn_save, 0, wx.ALL, 5)
        button_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)

        self.SetSizer(main_sizer)
        self.Fit()

        self._load_settings_to_widgets()
        self._bind_widget_events()
        wx.CallAfter(self._set_initial_focus)

    def _create_notebook_page(self, name: str) -> tuple[wx.Panel, wx.BoxSizer]:
        """Create a notebook page with a vertical layout and accessible name."""
        if self._options_notebook is None:
            raise RuntimeError("Notebook non inizializzato")
        panel = wx.Panel(self._options_notebook)
        panel.SetName(name)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        return panel, sizer

    def _add_group(
        self,
        page_sizer: wx.BoxSizer,
        parent: wx.Window,
        title: str,
        control: wx.Window,
    ) -> None:
        """Add a control inside a labelled static box on the given page."""
        box = wx.StaticBoxSizer(wx.VERTICAL, parent, title)
        box.Add(control, 0, wx.ALL | wx.EXPAND, 5)
        page_sizer.Add(box, 0, wx.ALL | wx.EXPAND, 10)

    def _set_initial_focus(self) -> None:
        """Move focus to the first logical control of the selected notebook page."""
        target = self._tab_focus_targets.get(0)
        if target is not None:
            target.SetFocus()

    def on_notebook_page_changed(self, event: wx.BookCtrlEvent) -> None:
        """Keep focus navigation predictable for NVDA when a tab changes."""
        target = self._tab_focus_targets.get(event.GetSelection())
        if target is not None:
            wx.CallAfter(target.SetFocus)
        event.Skip()
    
    def _load_settings_to_widgets(self) -> None:
        """Load current settings from controller into widgets.
        
        Called after _create_ui() to populate widgets with values from
        GameSettings (via OptionsWindowController).
        
        Version: v2.4.2 - Added lock state update call
        
        Maps GameSettings values to wx widget selections:
        - deck_type: "french" -> 0, "neapolitan" -> 1
        - difficulty_level: 1/2/3/4/5 -> RadioBox selection 0/1/2/3/4
        - draw_count: 1/2/3 -> RadioBox selection 0/1/2
        - max_time_game: seconds -> TimerComboBox (minutes: 0=disabled, 5-60)
        - shuffle_discards: False -> 0 (Inversione), True -> 1 (Mescolata)
        - command_hints_enabled: boolean -> CheckBox
        - scoring_enabled: boolean -> CheckBox
        - timer_strict_mode: True -> 0 (STRICT), False -> 1 (PERMISSIVE)
        """
        settings = self.options_controller.settings
        
        # 1. Tipo Mazzo
        deck_selection = 0 if settings.deck_type == "french" else 1
        self.deck_type_radio.SetSelection(deck_selection)
        
        # 2. Difficoltà (1/2/3/4/5 -> 0/1/2/3/4)
        self.difficulty_radio.SetSelection(settings.difficulty_level - 1)
        
        # 3. Carte Pescate (1/2/3 -> 0/1/2)
        self.draw_count_radio.SetSelection(settings.draw_count - 1)
        
        # 4. Timer (usando TimerComboBox con set_minutes())
        minutes = settings.max_time_game // 60
        self.timer_combo.set_minutes(minutes)  # 0 = disabled, 5-60 = enabled
        
        # ComboBox SEMPRE abilitata (no Enable() call)
        
        # 5. Riciclo Scarti (False=Inversione, True=Mescolata)
        shuffle_selection = 1 if settings.shuffle_discards else 0
        self.shuffle_radio.SetSelection(shuffle_selection)
        
        # 6. Suggerimenti Comandi
        self.command_hints_check.SetValue(settings.command_hints_enabled)
        
        # 7. Sistema Punti
        self.scoring_check.SetValue(settings.scoring_enabled)
        
        # 8. Modalità Timer (True=STRICT, False=PERMISSIVE)
        strict_selection = 0 if settings.timer_strict_mode else 1
        self.timer_strict_radio.SetSelection(strict_selection)
        
        # 9. Avvisi Soglie Punteggio (DISABLED/MINIMAL/BALANCED/COMPLETE -> 0/1/2/3)
        from src.domain.models.scoring import ScoreWarningLevel
        warning_level_map = {
            ScoreWarningLevel.DISABLED: 0,
            ScoreWarningLevel.MINIMAL: 1,
            ScoreWarningLevel.BALANCED: 2,
            ScoreWarningLevel.COMPLETE: 3
        }
        warning_selection = warning_level_map.get(settings.score_warning_level, 2)  # Default: BALANCED
        self.score_warning_radio.SetSelection(warning_selection)

        # 10. Modalità Display ("audio_only" -> 0, "visual" -> 1)
        display_mode = getattr(settings, "display_mode", "audio_only")
        self.display_mode_radio.SetSelection(0 if display_mode == "audio_only" else 1)

        # 11. Tema Visivo ("standard"->0, "alto_contrasto"->1, "grande"->2)
        _theme_map = {"standard": 0, "alto_contrasto": 1, "grande": 2}
        visual_theme = getattr(settings, "visual_theme", "standard")
        self.visual_theme_radio.SetSelection(_theme_map.get(visual_theme, 0))

        # ✅ FIX BUG #67: Update widget lock states after loading
        # This ensures locked widgets are disabled when dialog opens
        self._update_widget_lock_states()
    
    def _bind_widget_events(self) -> None:
        """Bind widget events to detect changes and update settings.
        
        All widget changes:
        1. Call _save_widgets_to_settings() (live update)
        2. Mark controller as DIRTY (modifications present)
        3. Enable save confirmation on ESC
        
        Note:
            Settings are updated IMMEDIATELY (live mode).
            Original values saved in controller snapshot (for discard).
            All widgets use standard on_setting_changed() handler.
        """
        # RadioBox widgets
        self.deck_type_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
        self.difficulty_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
        self.draw_count_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
        self.shuffle_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
        self.timer_strict_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)
        self.score_warning_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)

        # RadioBox — display mode
        self.display_mode_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)

        # RadioBox — visual theme
        self.visual_theme_radio.Bind(wx.EVT_RADIOBOX, self.on_setting_changed)

        # CheckBox widgets
        self.command_hints_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        self.scoring_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        
        # ComboBox widget (TimerComboBox uses standard handler)
        self.timer_combo.Bind(wx.EVT_COMBOBOX, self.on_setting_changed)
        
        # Buttons
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_click)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel_click)
        if self._options_notebook is not None:
            self._options_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_page_changed)
    
    def on_setting_changed(self, event: wx.Event) -> None:
        """Handle any setting change from widgets.
        
        Special handling for difficulty change:
        - Apply preset values to settings
        - Refresh ALL widgets to show new preset values
        - Update widget lock states (disable/enable based on preset)
        
        🆕 v3.5.0: Plays SETTING_CHANGED sound effect.
        
        Version: v2.4.2 - Fixed preset application on difficulty change (Bug #67)
                 v3.5.0 - Added audio feedback
        
        Args:
            event: wx.Event from widget (EVT_RADIOBOX, EVT_CHECKBOX, EVT_COMBOBOX)
        
        Flow:
            1. Save current widget value to settings
            2. If difficulty changed:
               a. Get current preset
               b. Apply preset values (timer, draw_count, etc.)
               c. Refresh ALL widgets to show new values
               d. Update widget lock states (disable locked ones)
               e. TTS announcement (optional)
            3. Mark controller as DIRTY
        """
        # Update GameSettings from current widget values
        self._save_widgets_to_settings()
        
        # ✨ NUOVO v3.5.0: Play setting changed sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.SETTING_CHANGED
            ))
        
        # ✅ FIX BUG #67: Special handling for difficulty change
        if event.GetEventObject() == self.difficulty_radio:
            # Get current preset for new difficulty level
            preset = self.options_controller.settings.get_current_preset()
            
            # Apply preset values to settings (timer, draw_count, shuffle, etc.)
            preset.apply_to(self.options_controller.settings)
            
            # Refresh ALL widgets to show new preset values
            # This updates timer_combo, draw_count_radio, shuffle_radio, etc.
            self._load_settings_to_widgets()
            
            # Update widget lock states (disable locked widgets)
            self._update_widget_lock_states()
            
            # TTS announcement (optional - helps blind users understand changes)
            if self.screen_reader and self.screen_reader.tts:
                locked_count = len(preset.get_locked_options())
                self.screen_reader.tts.speak(
                    f"{preset.name} applicato. {locked_count} opzioni bloccate.",
                    interrupt=True
                )
        
        # Mark controller as dirty (modifications present)
        if self.options_controller.state == "OPEN_CLEAN":
            self.options_controller.state = "OPEN_DIRTY"
        
        # Propagate event
        event.Skip()
    
    def on_save_click(self, event: wx.CommandEvent) -> None:
        """Handle Save button click.
        
        Calls controller.save_and_close() which:
        1. Updates settings snapshot (modifications become permanent)
        2. Resets controller state to CLOSED
        3. Returns TTS confirmation message
        
        🆕 v3.5.0: Plays SETTING_SAVED sound effect.
        
        Args:
            event: wx.CommandEvent from btn_save
        
        Note:
            Settings already updated live via on_setting_changed().
            This just commits the snapshot.
        
        Version:
            v3.5.0: Added audio feedback
        """
        # ✨ NUOVO v3.5.0: Play setting saved sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.SETTING_SAVED
            ))
        
        msg = self.options_controller.save_and_close()
        
        # Vocalize confirmation (optional - buttons are visual)
        if self.screen_reader and self.screen_reader.tts:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        self._close_dialog(wx.ID_OK)
    
    def on_cancel_click(self, event: wx.CommandEvent) -> None:
        """Handle Cancel button click.
        
        Calls controller.discard_and_close() which:
        1. Restores original settings snapshot (undo modifications)
        2. Resets controller state to CLOSED
        3. Returns TTS confirmation message
        
        🆕 v3.5.0: Plays UI_CANCEL sound effect.
        
        Args:
            event: wx.CommandEvent from btn_cancel
        
        Note:
            Rollback restores ALL settings to values at dialog open time.
        
        Version:
            v3.5.0: Added audio feedback
        """
        # ✨ NUOVO v3.5.0: Play cancel sound
        if self.audio_manager:
            from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType
            self.audio_manager.play_event(AudioEvent(
                event_type=AudioEventType.UI_CANCEL
            ))
        
        msg = self.options_controller.discard_and_close()
        
        # Vocalize confirmation (optional - buttons are visual)
        if self.screen_reader and self.screen_reader.tts:
            self.screen_reader.tts.speak(msg, interrupt=True)
        
        self._close_dialog(wx.ID_CANCEL)

    def _close_dialog(self, exit_code: int) -> None:
        """Close the dialog safely in both modal runtime and direct unit tests."""
        if self.IsModal():
            self.EndModal(exit_code)
            return
        self.Hide()
    
    def _save_widgets_to_settings(self) -> None:
        """Save current widget values back to GameSettings.
        
        Called on every widget change (live update mode).
        Maps wx widget selections to GameSettings attributes.
        
        Mappings:
        - deck_type_radio: 0->"french", 1->"neapolitan"
        - difficulty_radio: 0/1/2/3/4 -> difficulty_level 1/2/3/4/5
        - draw_count_radio: 0/1/2 -> draw_count 1/2/3
        - timer_combo: minutes (0=disabled, 5-60) -> max_time_game seconds
        - shuffle_radio: 0->False (Inversione), 1->True (Mescolata)
        - command_hints_check: boolean -> command_hints_enabled
        - scoring_check: boolean -> scoring_enabled
        - timer_strict_radio: 0->True (STRICT), 1->False (PERMISSIVE)
        
        Note:
            This is "live update" mode - settings changed immediately.
            Original values preserved in controller snapshot for rollback.
        """
        settings = self.options_controller.settings
        
        # 1. Tipo Mazzo
        settings.deck_type = "french" if self.deck_type_radio.GetSelection() == 0 else "neapolitan"
        
        # 2. Difficoltà (0/1/2/3/4 -> 1/2/3/4/5)
        settings.difficulty_level = self.difficulty_radio.GetSelection() + 1
        
        # 3. Carte Pescate (0/1/2 -> 1/2/3)
        settings.draw_count = self.draw_count_radio.GetSelection() + 1
        
        # 4. Timer (usando TimerComboBox con get_selected_minutes())
        minutes = self.timer_combo.get_selected_minutes()  # 0 = disabled, 5-60 = enabled
        settings.max_time_game = minutes * 60  # Convert to seconds
        
        # 5. Riciclo Scarti (0->False, 1->True)
        settings.shuffle_discards = (self.shuffle_radio.GetSelection() == 1)
        
        # 6. Suggerimenti Comandi
        settings.command_hints_enabled = self.command_hints_check.GetValue()
        
        # 7. Sistema Punti
        settings.scoring_enabled = self.scoring_check.GetValue()
        
        # 8. Modalità Timer (0->True STRICT, 1->False PERMISSIVE)
        settings.timer_strict_mode = (self.timer_strict_radio.GetSelection() == 0)
        
        # 9. Avvisi Soglie Punteggio (0/1/2/3 -> DISABLED/MINIMAL/BALANCED/COMPLETE)
        from src.domain.models.scoring import ScoreWarningLevel
        warning_levels = [
            ScoreWarningLevel.DISABLED,
            ScoreWarningLevel.MINIMAL,
            ScoreWarningLevel.BALANCED,
            ScoreWarningLevel.COMPLETE
        ]
        settings.score_warning_level = warning_levels[self.score_warning_radio.GetSelection()]

        # 10. Modalità Display (0->"audio_only", 1->"visual")
        settings.display_mode = "audio_only" if self.display_mode_radio.GetSelection() == 0 else "visual"

        # 11. Tema Visivo (0->"standard", 1->"alto_contrasto", 2->"grande")
        _theme_choices = ["standard", "alto_contrasto", "grande"]
        theme_idx = self.visual_theme_radio.GetSelection()
        settings.visual_theme = _theme_choices[theme_idx] if 0 <= theme_idx < len(_theme_choices) else "standard"

    def _update_widget_lock_states(self) -> None:
        """Update widget enable/disable states based on current preset locks.
        
        Disables widgets that are locked by the current difficulty preset.
        This provides visual feedback that options cannot be modified.
        
        Locked widgets are grayed out and cannot be interacted with.
        
        Version: v2.4.2 - Added for preset lock enforcement (Bug #67)
        
        Mappings (option_name -> widget):
            draw_count          -> self.draw_count_radio
            max_time_game       -> self.timer_combo
            shuffle_discards    -> self.shuffle_radio
            command_hints_enabled -> self.command_hints_check
            scoring_enabled     -> self.scoring_check
            timer_strict_mode   -> self.timer_strict_radio
        
        Never locked:
            deck_type           -> self.deck_type_radio (always enabled)
            difficulty_level    -> self.difficulty_radio (always enabled)
        
        Example:
            >>> # Level 5 (Maestro) locks most options
            >>> preset = DifficultyPreset.get_preset(5)
            >>> self._update_widget_lock_states()
            >>> # draw_count_radio is now DISABLED (grayed out)
            >>> # timer_combo is now DISABLED (grayed out)
            >>> # User cannot modify these options
        """
        preset = self.options_controller.settings.get_current_preset()
        
        # Draw count (option: draw_count)
        is_draw_locked = preset.is_locked("draw_count")
        self.draw_count_radio.Enable(not is_draw_locked)
        
        # Timer duration (option: max_time_game)
        is_timer_locked = preset.is_locked("max_time_game")
        self.timer_combo.Enable(not is_timer_locked)
        
        # Shuffle mode (option: shuffle_discards)
        is_shuffle_locked = preset.is_locked("shuffle_discards")
        self.shuffle_radio.Enable(not is_shuffle_locked)
        
        # Command hints (option: command_hints_enabled)
        is_hints_locked = preset.is_locked("command_hints_enabled")
        self.command_hints_check.Enable(not is_hints_locked)
        
        # Scoring system (option: scoring_enabled)
        is_scoring_locked = preset.is_locked("scoring_enabled")
        self.scoring_check.Enable(not is_scoring_locked)
        
        # Timer strict mode (option: timer_strict_mode)
        is_strict_locked = preset.is_locked("timer_strict_mode")
        self.timer_strict_radio.Enable(not is_strict_locked)
        
        # Score warning level (option: score_warning_level)
        # Note: This option is NEVER locked by any preset (always user-configurable)
        self.score_warning_radio.Enable(True)  # Always enabled
        
        # Deck type and difficulty are NEVER locked
        # (always allow user to change these)
        self.deck_type_radio.Enable(True)
        self.difficulty_radio.Enable(True)
        self.display_mode_radio.Enable(True)
        self.visual_theme_radio.Enable(True)
    
    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Handle keyboard events for ESC key only.
        
        ESC behavior (v1.8.0 smart close):
        - If no modifications (OPEN_CLEAN): Close directly
        - If modifications present (OPEN_DIRTY): Show save confirmation dialog
          * Dialog options: Sì (save), No (discard), Annulla (cancel)
          * If user cancels: Stay open (don't close)
        
        Other keys: Propagated normally (TAB, arrows, SPACE handled by wx)
        
        Args:
            event: wx.KeyEvent from keyboard
        
        Note:
            Virtual navigation (arrows/numbers) removed in v1.8.0.
            Use standard wx navigation: TAB between widgets,
            arrows within RadioBox/ComboBox.
        """
        key_code = event.GetKeyCode()
        
        # ESC: Smart close with confirmation if dirty
        if key_code == wx.WXK_ESCAPE:
            # Call close_window() which handles DIRTY/CLEAN states
            msg = self.options_controller.close_window()
            
            # Check if dialog was actually closed
            # (controller sets state to CLOSED if user confirmed save/discard)
            if self.options_controller.state == "CLOSED":
                # Closing confirmed (saved or discarded)
                if self.screen_reader and self.screen_reader.tts:
                    self.screen_reader.tts.speak(msg, interrupt=True)
                
                # Determine exit code based on message content
                # ("salv" in msg means user chose to save)
                exit_code = wx.ID_OK if "salv" in msg.lower() else wx.ID_CANCEL
                self._close_dialog(exit_code)
            else:
                # Closing cancelled (user pressed Annulla in save dialog)
                # or fallback mode (no dialog_manager available)
                if self.screen_reader and self.screen_reader.tts:
                    self.screen_reader.tts.speak(msg, interrupt=True)
                # Stay open (don't call EndModal)
            
            return  # Event handled
        
        # All other keys: Propagate normally (TAB, arrows, SPACE, etc.)
        event.Skip()


# Module exports
__all__ = ['OptionsDialog']
