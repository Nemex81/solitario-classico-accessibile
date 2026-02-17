"""ProfileMenuPanel - Profile management dialog with native wxPython widgets.

Provides CRUD operations for user profiles:
- Create new profile
- Switch active profile
- Rename current profile
- Delete profile
- View detailed stats
- Set default profile

Pattern: Modal wx.Dialog (similar to OptionsDialog pattern)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> from src.infrastructure.ui.profile_menu_panel import ProfileMenuPanel
    >>> panel = ProfileMenuPanel(parent=frame, profile_service=service, screen_reader=sr)
    >>> result = panel.ShowModal()
    >>> panel.Destroy()
"""

import wx
from typing import Optional, List, Dict

from src.domain.services.profile_service import ProfileService
from src.infrastructure.accessibility.screen_reader import ScreenReader
from src.infrastructure.logging import game_logger as log


class ProfileMenuPanel(wx.Dialog):
    """Profile management dialog with native buttons (NVDA accessible).
    
    Features:
    - 6 wx.Button widgets for profile operations
    - TAB navigation between buttons
    - ENTER to activate focused button
    - ESC to close and return to main menu
    - TTS announcements on button focus
    - Real-time profile list updates
    
    Button Actions:
    1. Switch Profile → Show profile selector dialog
    2. Create New → Show create profile dialog
    3. Rename Current → Show rename dialog
    4. Delete Profile → Show confirmation + delete
    5. Detailed Stats → Open DetailedStatsDialog (Phase 9.3!)
    6. Set Default → Mark current profile as default
    
    Attributes:
        profile_service: ProfileService instance for CRUD ops
        screen_reader: ScreenReader for TTS announcements
    
    Example:
        >>> panel = ProfileMenuPanel(parent, profile_service, screen_reader)
        >>> panel.ShowModal()  # Blocks until closed
        >>> # User actions handled internally via buttons
        >>> panel.Destroy()
    
    Version:
        v3.1.0: Initial implementation (Phase 10.1)
    """
    
    def __init__(
        self,
        parent,
        profile_service: ProfileService,
        screen_reader: Optional[ScreenReader] = None
    ):
        """Initialize ProfileMenuPanel.
        
        Args:
            parent: Parent window (typically SolitarioFrame)
            profile_service: ProfileService for CRUD operations
            screen_reader: Optional ScreenReader for TTS (None = silent mode)
        
        Note:
            Dialog is modal - blocks parent until closed.
            Initial focus on "Switch Profile" button.
            TTS announces: "Gestione Profili. Profilo attivo: [nome]. 6 opzioni disponibili."
        """
        super().__init__(
            parent,
            title="Gestione Profili",
            style=wx.DEFAULT_DIALOG_STYLE
        )
        
        self.profile_service = profile_service
        self.screen_reader = screen_reader
        
        # Create UI
        self._create_ui()
        
        # Log dialog opened
        log.dialog_shown("profile_menu", "Gestione Profili")
        
        # Announce dialog opened
        active_name = profile_service.active_profile.profile_name if profile_service.active_profile else "Nessuno"
        self._announce(
            f"Gestione Profili. Profilo attivo: {active_name}. 6 opzioni disponibili.",
            interrupt=True
        )
    
    def _create_ui(self) -> None:
        """Create dialog UI with title, active profile info, and 6 buttons.
        
        Layout:
        - Title label (bold, 14pt): "GESTIONE PROFILI"
        - Active profile label: "Profilo Attivo: [Nome]"
        - 6 buttons vertically stacked (20px padding)
        - Buttons are wx.EXPAND (full width)
        - First button receives initial focus
        
        Buttons bind:
        - EVT_BUTTON: Click handler
        - EVT_SET_FOCUS: TTS announcement
        
        ESC handling: EVT_CLOSE bound to _on_close()
        """
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title label
        title = wx.StaticText(self, label="GESTIONE PROFILI")
        title_font = title.GetFont()
        title_font.PointSize = 14
        title_font = title_font.Bold()
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 15)
        
        # Active profile info
        active_name = self.profile_service.active_profile.profile_name if self.profile_service.active_profile else "Nessuno"
        self.active_label = wx.StaticText(self, label=f"Profilo Attivo: {active_name}")
        active_font = self.active_label.GetFont()
        active_font = active_font.Bold()
        self.active_label.SetFont(active_font)
        sizer.Add(self.active_label, 0, wx.ALL | wx.CENTER, 10)
        
        # Separator
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 10)
        
        # Create buttons
        btn_switch = wx.Button(self, label="1. Cambia Profilo")
        btn_switch.Bind(wx.EVT_BUTTON, self._on_switch_profile)
        btn_switch.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        btn_create = wx.Button(self, label="2. Crea Nuovo Profilo")
        btn_create.Bind(wx.EVT_BUTTON, self._on_create_profile)
        btn_create.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        btn_rename = wx.Button(self, label="3. Rinomina Profilo Corrente")
        btn_rename.Bind(wx.EVT_BUTTON, self._on_rename_profile)
        btn_rename.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        btn_delete = wx.Button(self, label="4. Elimina Profilo")
        btn_delete.Bind(wx.EVT_BUTTON, self._on_delete_profile)
        btn_delete.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        btn_stats = wx.Button(self, label="5. Statistiche Dettagliate")
        btn_stats.Bind(wx.EVT_BUTTON, self._on_show_stats)
        btn_stats.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        btn_default = wx.Button(self, label="6. Imposta come Predefinito")
        btn_default.Bind(wx.EVT_BUTTON, self._on_set_default)
        btn_default.Bind(wx.EVT_SET_FOCUS, self._on_button_focus)
        
        # Add buttons to sizer
        for btn in [btn_switch, btn_create, btn_rename, btn_delete, btn_stats, btn_default]:
            sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 10)
        
        # Separator
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 10)
        
        # Close button
        btn_close = wx.Button(self, wx.ID_CANCEL, "Chiudi (ESC)")
        btn_close.Bind(wx.EVT_BUTTON, self._on_close)
        sizer.Add(btn_close, 0, wx.ALL | wx.CENTER, 10)
        
        # Finalize layout
        self.SetSizer(sizer)
        self.Fit()
        
        # Set initial focus
        btn_switch.SetFocus()
        
        # Bind ESC key
        self.Bind(wx.EVT_CLOSE, self._on_close)
    
    def _on_button_focus(self, event: wx.FocusEvent) -> None:
        """Announce button label when focused (NVDA accessibility).
        
        Called automatically on TAB navigation or SetFocus().
        Announces button label via TTS without interrupting.
        
        Args:
            event: wx.FocusEvent from button focus change
        """
        button = event.GetEventObject()
        self._announce(button.GetLabel(), interrupt=False)
        event.Skip()
    
    def _on_switch_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Cambia Profilo\" button.
        
        Flow:
        1. Load all profiles from profile_service.list_profiles()
        2. Build choice list (exclude current active)
        3. Show wx.SingleChoiceDialog
        4. On selection: call profile_service.switch_profile(profile_id)
        5. Refresh active profile label
        6. Announce: "Profilo cambiato a: [nome]"
        
        Special case:
        - Only 1 profile (current) → Message "Nessun altro profilo disponibile"
        - Guest profile: Show in list but mark as "(Ospite)"
        
        Returns to profile menu after switch (no auto-close).
        
        Version: v3.1.0 Phase 10.2
        """
        self._announce("Cambia profilo.", interrupt=True)
        
        # Load all profiles
        all_profiles = self.profile_service.list_profiles()
        
        if len(all_profiles) <= 1:
            wx.MessageBox(
                "Nessun altro profilo disponibile.\n"
                "Crea un nuovo profilo prima di cambiare.",
                "Cambia Profilo",
                wx.OK | wx.ICON_INFORMATION
            )
            self._announce("Nessun altro profilo disponibile.", interrupt=True)
            return
        
        # Build choice list (profile_name + win stats)
        current_id = self.profile_service.active_profile.profile_id if self.profile_service.active_profile else None
        choices = []
        profile_ids = []
        
        for profile in all_profiles:
            pid = profile['profile_id']
            name = profile['profile_name']
            wins = profile.get('total_victories', 0)
            games = profile.get('total_games', 0)
            
            # Mark current profile
            if pid == current_id:
                label = f"{name} (attivo) - {wins} vittorie su {games}"
            else:
                label = f"{name} - {wins} vittorie su {games}"
            
            choices.append(label)
            profile_ids.append(pid)
        
        # Show choice dialog
        dlg = wx.SingleChoiceDialog(
            self,
            "Seleziona profilo da attivare:",
            "Cambia Profilo",
            choices,
            style=wx.OK | wx.CANCEL | wx.CENTRE
        )
        
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            self._announce("Cambio annullato.", interrupt=True)
            return
        
        selection_idx = dlg.GetSelection()
        dlg.Destroy()
        
        selected_id = profile_ids[selection_idx]
        
        # Skip if selecting current profile
        if selected_id == current_id:
            self._announce("Profilo già attivo.", interrupt=True)
            return
        
        # Switch profile
        try:
            success = self.profile_service.switch_profile(selected_id)
            
            if success:
                log.info(f"Profile switched to: {selected_id}")
                
                # Refresh UI
                self._update_active_label()
                
                # Announce
                new_name = self.profile_service.active_profile.profile_name
                self._announce(f"Profilo cambiato a: {new_name}.", interrupt=True)
            else:
                wx.MessageBox(
                    "Impossibile cambiare profilo.",
                    "Errore",
                    wx.OK | wx.ICON_ERROR
                )
                self._announce("Errore cambio profilo.", interrupt=True)
                
        except Exception as e:
            log.error_occurred("ProfileMenuPanel", f"Failed to switch profile: {e}", e)
            wx.MessageBox(
                f"Errore durante cambio profilo: {e}",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Errore cambio profilo.", interrupt=True)
    
    def _on_create_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Crea Nuovo Profilo\" button.
        
        Flow:
        1. Show wx.TextEntryDialog for profile name input
        2. Validate name (non-empty, max 30 chars, no duplicates)
        3. Call profile_service.create_profile(name)
        4. Auto-switch to new profile
        5. Refresh active profile label
        6. Announce success via TTS
        
        Validation errors:
        - Empty name → "Nome profilo non può essere vuoto"
        - Too long → "Nome profilo troppo lungo (max 30 caratteri)"
        - Duplicate → "Profilo già esistente"
        
        Success: "Profilo [nome] creato e attivato."
        
        Version: v3.1.0 Phase 10.2
        """
        self._announce("Crea nuovo profilo.", interrupt=True)
        
        # Show text entry dialog
        dlg = wx.TextEntryDialog(
            self,
            "Inserisci nome del nuovo profilo:",
            "Crea Profilo",
            value="",
            style=wx.OK | wx.CANCEL | wx.CENTRE
        )
        
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            self._announce("Creazione annullata.", interrupt=True)
            return
        
        profile_name = dlg.GetValue().strip()
        dlg.Destroy()
        
        # Validate name
        if not profile_name:
            wx.MessageBox(
                "Nome profilo non può essere vuoto.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nome vuoto, riprova.", interrupt=True)
            return
        
        if len(profile_name) > 30:
            wx.MessageBox(
                "Nome profilo troppo lungo (massimo 30 caratteri).",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nome troppo lungo, riprova.", interrupt=True)
            return
        
        # Check duplicates
        all_profiles = self.profile_service.list_profiles()
        existing_names = [p['profile_name'] for p in all_profiles]
        if profile_name in existing_names:
            wx.MessageBox(
                f"Un profilo con nome '{profile_name}' esiste già.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nome già esistente, riprova.", interrupt=True)
            return
        
        # Create profile
        try:
            new_profile = self.profile_service.create_profile(profile_name)
            if new_profile:
                log.info(f"Profile created: {new_profile.profile_id} ({profile_name})")
                
                # Auto-switch to new profile
                self.profile_service.switch_profile(new_profile.profile_id)
                
                # Refresh UI
                self._update_active_label()
                
                # Announce success
                self._announce(f"Profilo {profile_name} creato e attivato.", interrupt=True)
            else:
                wx.MessageBox(
                    "Errore durante creazione profilo.",
                    "Errore",
                    wx.OK | wx.ICON_ERROR
                )
                self._announce("Errore creazione profilo.", interrupt=True)
            
        except Exception as e:
            log.error_occurred("ProfileMenuPanel", f"Failed to create profile: {e}", e)
            wx.MessageBox(
                f"Errore durante creazione profilo: {e}",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Errore creazione profilo.", interrupt=True)
    
    def _on_rename_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Rinomina Profilo\" button (Commit 10.3)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.3
    
    def _on_delete_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Elimina Profilo\" button (Commit 10.3)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.3
    
    def _on_show_stats(self, event: wx.CommandEvent) -> None:
        """Handle \"Statistiche Dettagliate\" button (Commit 10.4 - Phase 9.3!)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.4
    
    def _on_set_default(self, event: wx.CommandEvent) -> None:
        """Handle \"Imposta come Predefinito\" button (Commit 10.4)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.4
    
    def _on_close(self, event) -> None:
        """Handle ESC or Close button - return to main menu.
        
        Sets dialog result to wx.ID_CANCEL and closes.
        Announces: "Ritorno al menu principale."
        Logs: dialog_closed("profile_menu", "closed")
        """
        self._announce("Ritorno al menu principale.", interrupt=True)
        log.dialog_closed("profile_menu", "closed")
        self.EndModal(wx.ID_CANCEL)
    
    def _announce(self, message: str, interrupt: bool = False) -> None:
        """Announce message via TTS (safe wrapper).
        
        Args:
            message: Text to announce
            interrupt: Whether to interrupt current speech
        
        Note:
            Silently fails if screen_reader not available.
        """
        if self.screen_reader and hasattr(self.screen_reader, 'tts') and self.screen_reader.tts:
            self.screen_reader.tts.speak(message, interrupt=interrupt)
    
    def _update_active_label(self) -> None:
        """Update \"Profilo Attivo\" label after profile change.
        
        Called after successful switch/create/delete operations.
        Refreshes label text with current active profile name.
        """
        active_name = self.profile_service.active_profile.profile_name if self.profile_service.active_profile else "Nessuno"
        self.active_label.SetLabel(f"Profilo Attivo: {active_name}")


# Module-level documentation
__all__ = ['ProfileMenuPanel']
