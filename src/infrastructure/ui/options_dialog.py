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
        size: tuple = (600, 700)  # Increased for 8 widgets
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
        
        # Create native wx widgets UI
        self._create_ui()
        
        # Bind ESC key for smart close
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
        
        # Center dialog on parent
        self.Centre()
    
    def _create_ui(self) -> None:
        """Create native wx widgets for all game options.
        
        Layout (v1.9.0 - native widgets, ALL 9 options + buttons):
        - RadioBox for deck type (Francese/Napoletano)
        - RadioBox for difficulty (5 levels: Principiante to Maestro)
        - RadioBox for draw count (1/2/3 carte)
        - TimerComboBox for timer duration (0=disabled, 5-60 minutes)
        - RadioBox for shuffle mode (Inversione/Mescolata)
        - CheckBox for command hints (ON/OFF)
        - CheckBox for scoring system (ON/OFF)
        - RadioBox for timer strict mode (STRICT/PERMISSIVE)
        - RadioBox for score warning level (4 levels: DISABLED to COMPLETE)
        - Buttons: Salva / Annulla
        
        Navigation:
        - TAB to move between widgets (standard wx behavior)
        - UP/DOWN arrows to change value in RadioBox/ComboBox
        - SPACE to toggle CheckBox
        - ENTER to activate focused button
        
        Accessibility:
        - NVDA reads all widgets automatically (native support)
        - No custom TTS needed - wx handles screen reader communication
        - All widgets have descriptive labels for screen readers
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # ========================================
        # OPZIONE 1: TIPO MAZZO
        # ========================================
        deck_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Tipo Mazzo")
        self.deck_type_radio = wx.RadioBox(
            self,
            label="Seleziona il tipo di mazzo da usare:",
            choices=["Francese (52 carte)", "Napoletano (40 carte)"],
            majorDimension=1,  # Vertical layout
            style=wx.RA_SPECIFY_COLS
        )
        deck_box.Add(self.deck_type_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(deck_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 2: DIFFICOLTÀ
        # ========================================
        diff_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Difficoltà")
        self.difficulty_radio = wx.RadioBox(
            self,
            label="Livello di difficoltà:",
            choices=[
                "Livello 1 - Principiante",
                "Livello 2 - Facile",
                "Livello 3 - Normale",
                "Livello 4 - Esperto",
                "Livello 5 - Maestro"
            ],
            majorDimension=5,  # Horizontal layout with 5 columns
            style=wx.RA_SPECIFY_COLS
        )
        diff_box.Add(self.difficulty_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(diff_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 3: CARTE PESCATE
        # ========================================
        draw_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Carte Pescate per Turno")
        self.draw_count_radio = wx.RadioBox(
            self,
            label="Numero di carte pescate dal mazzo ad ogni click:",
            choices=["1 carta", "2 carte", "3 carte"],
            majorDimension=3,  # Horizontal layout
            style=wx.RA_SPECIFY_COLS
        )
        draw_box.Add(self.draw_count_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(draw_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 4: TIMER
        # ========================================
        timer_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Timer Partita")
        
        # Label esplicativa (sostituisce CheckBox)
        timer_label = wx.StaticText(
            self,
            label="Seleziona durata timer (0 = disattivato):"
        )
        timer_box.Add(timer_label, 0, wx.ALL, 5)
        
        # TimerComboBox SEMPRE ATTIVO con "0 minuti - Timer disattivato" come prima voce
        from src.infrastructure.ui.widgets.timer_combobox import TimerComboBox
        self.timer_combo = TimerComboBox(self)
        timer_box.Add(self.timer_combo, 0, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(timer_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 5: RICICLO SCARTI
        # ========================================
        shuffle_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Riciclo Scarti")
        self.shuffle_radio = wx.RadioBox(
            self,
            label="Modalità di riciclo quando il tallone è vuoto:",
            choices=["Inversione (ribalta mazzo scarti)", "Mescolata (rimescola scarti)"],
            majorDimension=1,  # Vertical layout
            style=wx.RA_SPECIFY_COLS
        )
        shuffle_box.Add(self.shuffle_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(shuffle_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 6: SUGGERIMENTI COMANDI
        # ========================================
        self.command_hints_check = wx.CheckBox(
            self,
            label="Suggerimenti comandi attivi (mostra aiuto per comandi disponibili)"
        )
        main_sizer.Add(self.command_hints_check, 0, wx.ALL, 10)
        
        # ========================================
        # OPZIONE 7: SISTEMA PUNTI
        # ========================================
        self.scoring_check = wx.CheckBox(
            self,
            label="Sistema punti attivo (calcola punteggio durante partita)"
        )
        main_sizer.Add(self.scoring_check, 0, wx.ALL, 10)
        
        # ========================================
        # OPZIONE 8: MODALITÀ TIMER
        # ========================================
        strict_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Modalità Timer")
        self.timer_strict_radio = wx.RadioBox(
            self,
            label="Comportamento quando il timer scade:",
            choices=[
                "STRICT (sconfitta automatica)",
                "PERMISSIVE (penalità punti, partita continua)"
            ],
            majorDimension=1,  # Vertical layout
            style=wx.RA_SPECIFY_COLS
        )
        strict_box.Add(self.timer_strict_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(strict_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # OPZIONE 9: AVVISI SOGLIE PUNTEGGIO
        # ========================================
        warning_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Avvisi Soglie Punteggio")
        self.score_warning_radio = wx.RadioBox(
            self,
            label="Livello di verbosità degli avvisi TTS per penalità punteggio:",
            choices=[
                "DISABLED (nessun avviso)",
                "MINIMAL (solo primo avviso)",
                "BALANCED (avvisi soglie critiche)",
                "COMPLETE (tutti gli avvisi)"
            ],
            majorDimension=1,  # Vertical layout
            style=wx.RA_SPECIFY_COLS
        )
        warning_box.Add(self.score_warning_radio, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(warning_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ========================================
        # PULSANTI SALVA / ANNULLA
        # ========================================
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_save = wx.Button(self, id=wx.ID_OK, label="&Salva modifiche")
        self.btn_save.SetToolTip("Salva le modifiche e chiudi la finestra opzioni (ALT+S)")
        
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="&Annulla modifiche")
        self.btn_cancel.SetToolTip("Annulla le modifiche e chiudi la finestra opzioni (ALT+A)")
        
        button_sizer.Add(self.btn_save, 0, wx.ALL, 5)
        button_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
        
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        
        # Set sizer and auto-resize dialog
        self.SetSizer(main_sizer)
        self.Fit()  # Auto-resize to fit all widgets
        
        # Load current settings into widgets
        self._load_settings_to_widgets()
        
        # Bind events for change detection
        self._bind_widget_events()
    
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
        
        # CheckBox widgets
        self.command_hints_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        self.scoring_check.Bind(wx.EVT_CHECKBOX, self.on_setting_changed)
        
        # ComboBox widget (TimerComboBox uses standard handler)
        self.timer_combo.Bind(wx.EVT_COMBOBOX, self.on_setting_changed)
        
        # Buttons
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save_click)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel_click)
    
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
        
        # Close dialog with OK status
        self.EndModal(wx.ID_OK)
    
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
        
        # Close dialog with Cancel status
        self.EndModal(wx.ID_CANCEL)
    
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
                self.EndModal(exit_code)
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
