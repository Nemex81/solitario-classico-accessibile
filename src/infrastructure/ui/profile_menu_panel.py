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
        4. On selection: call profile_service.load_profile(profile_id)
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
        
        # Switch profile (load_profile sets it as active)
        try:
            success = self.profile_service.load_profile(selected_id)
            
            if success:
                log.debug_state("profile_switched", {"profile_id": selected_id})
                
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
                log.debug_state("profile_created", {"profile_id": new_profile.profile_id, "name": profile_name})
                
                # Auto-switch to new profile (load_profile sets it as active)
                self.profile_service.load_profile(new_profile.profile_id)
                
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
        """Handle \"Rinomina Profilo Corrente\" button.
        
        Flow:
        1. Check if active profile exists
        2. Show wx.TextEntryDialog with current name as default
        3. Validate new name (same rules as create)
        4. Modify active_profile.profile_name and save_active_profile()
        5. Refresh active profile label
        6. Announce: "Profilo rinominato in: [nome]"
        
        Restrictions:
        - Guest profile cannot be renamed → Show error message
        - Same validation as create (non-empty, max 30, no duplicates)
        
        Note: Only renames active profile, not others.
        
        Version: v3.1.0 Phase 10.3
        """
        self._announce("Rinomina profilo corrente.", interrupt=True)
        
        # Check if active profile exists
        if not self.profile_service.active_profile:
            wx.MessageBox(
                "Nessun profilo attivo.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nessun profilo attivo.", interrupt=True)
            return
        
        # Check guest profile
        if self.profile_service.active_profile.is_guest:
            wx.MessageBox(
                "Il profilo Ospite non può essere rinominato.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Profilo ospite non rinominabile.", interrupt=True)
            return
        
        current_name = self.profile_service.active_profile.profile_name
        
        # Show text entry dialog
        dlg = wx.TextEntryDialog(
            self,
            f"Inserisci nuovo nome per profilo '{current_name}':",
            "Rinomina Profilo",
            value=current_name,
            style=wx.OK | wx.CANCEL | wx.CENTRE
        )
        
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            self._announce("Rinomina annullata.", interrupt=True)
            return
        
        new_name = dlg.GetValue().strip()
        dlg.Destroy()
        
        # Skip if same name
        if new_name == current_name:
            self._announce("Nome identico, nessuna modifica.", interrupt=True)
            return
        
        # Validate name (same as create)
        if not new_name:
            wx.MessageBox(
                "Nome profilo non può essere vuoto.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nome vuoto, riprova.", interrupt=True)
            return
        
        if len(new_name) > 30:
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
        if new_name in existing_names:
            wx.MessageBox(
                f"Un profilo con nome '{new_name}' esiste già.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nome già esistente, riprova.", interrupt=True)
            return
        
        # Rename profile inline
        try:
            # Modify active profile name and save
            self.profile_service.active_profile.profile_name = new_name
            success = self.profile_service.save_active_profile()
            
            if success:
                log.debug_state("profile_renamed", {"old_name": current_name, "new_name": new_name})
                
                # Refresh UI
                self._update_active_label()
                
                # Announce
                self._announce(f"Profilo rinominato in: {new_name}.", interrupt=True)
            else:
                wx.MessageBox(
                    "Impossibile rinominare profilo.",
                    "Errore",
                    wx.OK | wx.ICON_ERROR
                )
                self._announce("Errore rinomina profilo.", interrupt=True)
        
        except Exception as e:
            log.error_occurred("ProfileMenuPanel", f"Failed to rename profile: {e}", e)
            wx.MessageBox(
                f"Errore durante rinomina: {e}",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Errore rinomina profilo.", interrupt=True)
    
    def _on_delete_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Elimina Profilo\" button.
        
        Flow:
        1. Check if active profile can be deleted
        2. Show wx.MessageDialog confirmation (YES/NO)
        3. On YES: call profile_service.delete_profile(profile_id)
        4. Auto-switch to default profile (or first available)
        5. Refresh active profile label
        6. Announce: "Profilo eliminato. Attivo: [nome nuovo]"
        
        Restrictions:
        - Guest profile cannot be deleted → Show error
        - Last remaining profile cannot be deleted → Show error
        - Requires confirmation dialog (destructive action)
        
        Confirmation message:
        "Sei sicuro di voler eliminare il profilo '[nome]'?
        Tutte le statistiche e partite salvate saranno perse.
        
        Questa operazione non può essere annullata."
        
        Version: v3.1.0 Phase 10.3
        """
        self._announce("Elimina profilo.", interrupt=True)
        
        # Check if active profile exists
        if not self.profile_service.active_profile:
            wx.MessageBox(
                "Nessun profilo attivo.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nessun profilo attivo.", interrupt=True)
            return
        
        # Check guest profile
        if self.profile_service.active_profile.is_guest:
            wx.MessageBox(
                "Il profilo Ospite non può essere eliminato.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Profilo ospite non eliminabile.", interrupt=True)
            return
        
        # Check if last profile
        all_profiles = self.profile_service.list_profiles()
        non_guest_profiles = [p for p in all_profiles if not p.get('is_guest', False)]
        
        if len(non_guest_profiles) <= 1:
            wx.MessageBox(
                "Non puoi eliminare l'ultimo profilo rimanente.\n"
                "Crea un nuovo profilo prima di eliminare questo.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Impossibile eliminare ultimo profilo.", interrupt=True)
            return
        
        current_name = self.profile_service.active_profile.profile_name
        current_id = self.profile_service.active_profile.profile_id
        
        # Show confirmation dialog
        dlg = wx.MessageDialog(
            self,
            f"Sei sicuro di voler eliminare il profilo '{current_name}'?\n\n"
            f"Tutte le statistiche e partite salvate saranno perse.\n\n"
            f"Questa operazione non può essere annullata.",
            "Conferma Eliminazione",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result != wx.ID_YES:
            self._announce("Eliminazione annullata.", interrupt=True)
            return
        
        # Delete profile
        try:
            success = self.profile_service.delete_profile(current_id)
            
            if success:
                log.debug_state("profile_deleted", {"profile_id": current_id, "name": current_name})
                
                # Auto-switch to first available non-guest profile
                remaining = self.profile_service.list_profiles()
                next_profile = None
                for p in remaining:
                    if not p.get('is_guest', False):
                        next_profile = p
                        break
                
                if next_profile:
                    # Switch to next profile (load_profile sets it as active)
                    self.profile_service.load_profile(next_profile['profile_id'])
                
                # Refresh UI
                self._update_active_label()
                
                # Announce
                new_name = self.profile_service.active_profile.profile_name if self.profile_service.active_profile else "Sconosciuto"
                self._announce(f"Profilo {current_name} eliminato. Attivo: {new_name}.", interrupt=True)
            else:
                wx.MessageBox(
                    "Impossibile eliminare profilo.",
                    "Errore",
                    wx.OK | wx.ICON_ERROR
                )
                self._announce("Errore eliminazione profilo.", interrupt=True)
        
        except Exception as e:
            log.error_occurred("ProfileMenuPanel", f"Failed to delete profile: {e}", e)
            wx.MessageBox(
                f"Errore durante eliminazione: {e}",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Errore eliminazione profilo.", interrupt=True)
    
    def _on_show_stats(self, event: wx.CommandEvent) -> None:
        """Handle \"Statistiche Dettagliate\" button (Phase 9.3 COMPLETION!).
        
        Flow:
        1. Check if active profile exists
        2. Load stats from profile_service
        3. Build stats_data dict (format expected by DetailedStatsDialog)
        4. Open DetailedStatsDialog (modal, blocks until closed)
        5. Returns to profile menu after closing
        
        Stats data structure:
        {
            'profile_name': str,
            'global_stats': GlobalStats,
            'timer_stats': TimerStats,
            'difficulty_stats': DifficultyStats,
            'scoring_stats': ScoringStats
        }
        
        Note: This completes Feature 3 implementation (Phase 9.3)!
        
        Version: v3.1.0 Phase 10.4
        """
        from src.presentation.dialogs.detailed_stats_dialog import DetailedStatsDialog
        
        self._announce("Statistiche dettagliate.", interrupt=True)
        
        # Check active profile
        if self.profile_service.active_profile is None:
            wx.MessageBox(
                "Nessun profilo attivo.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nessun profilo attivo.", interrupt=True)
            return
        
        # Build stats data
        profile = self.profile_service.active_profile
        stats_data = {
            'profile_name': profile.profile_name,
            'global_stats': self.profile_service.global_stats,
            'timer_stats': self.profile_service.timer_stats,
            'difficulty_stats': self.profile_service.difficulty_stats,
            'scoring_stats': self.profile_service.scoring_stats
        }
        
        log.info_query_requested("detailed_stats", f"profile_{profile.profile_name}")
        
        # Open DetailedStatsDialog (Phase 5 - already implemented!)
        dialog = DetailedStatsDialog(self, stats_data)
        dialog.ShowModal()
        dialog.Destroy()
        
        # Return to profile menu (no announce needed, dialog handles TTS)
    
    def _on_set_default(self, event: wx.CommandEvent) -> None:
        """Handle \"Imposta come Predefinito\" button.
        
        Marks active profile as default (auto-selected on app startup).
        
        Flow:
        1. Check if active profile exists
        2. Set active_profile.is_default = True and save_active_profile()
        3. Show success message
        4. Announce: "Profilo impostato come predefinito"
        
        Note: Only one profile can be default at a time (service handles this).
        Guest profile CAN be set as default (use case: family PC shared mode).
        
        Success message:
        "Profilo '[nome]' impostato come predefinito.
        Sarà caricato automaticamente all'avvio dell'applicazione."
        
        Version: v3.1.0 Phase 10.4
        """
        self._announce("Imposta come predefinito.", interrupt=True)
        
        # Check active profile
        if self.profile_service.active_profile is None:
            wx.MessageBox(
                "Nessun profilo attivo.",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Nessun profilo attivo.", interrupt=True)
            return
        
        current_name = self.profile_service.active_profile.profile_name
        current_id = self.profile_service.active_profile.profile_id
        
        # Set as default inline
        try:
            # Set is_default flag and save
            self.profile_service.active_profile.is_default = True
            success = self.profile_service.save_active_profile()
            
            if success:
                log.debug_state("default_profile_set", {"profile_id": current_id, "name": current_name})
                
                # Show success message
                wx.MessageBox(
                    f"Profilo '{current_name}' impostato come predefinito.\n\n"
                    f"Sarà caricato automaticamente all'avvio dell'applicazione.",
                    "Profilo Predefinito",
                    wx.OK | wx.ICON_INFORMATION
                )
                
                self._announce(f"Profilo {current_name} impostato come predefinito.", interrupt=True)
            else:
                wx.MessageBox(
                    "Impossibile impostare profilo come predefinito.",
                    "Errore",
                    wx.OK | wx.ICON_ERROR
                )
                self._announce("Errore impostazione predefinito.", interrupt=True)
        
        except Exception as e:
            log.error_occurred("ProfileMenuPanel", f"Failed to set default profile: {e}", e)
            wx.MessageBox(
                f"Errore durante impostazione: {e}",
                "Errore",
                wx.OK | wx.ICON_ERROR
            )
            self._announce("Errore impostazione predefinito.", interrupt=True)
    
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
