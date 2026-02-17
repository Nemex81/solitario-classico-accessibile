# 📝 PHASE 10: Profile Management UI - Detailed Implementation Guide

**Status**: Implementation Ready  
**Estimated Time**: 60-75 minuti (4 commit)  
**Branch**: `copilot/implement-profile-system-v3-1-0`  
**Prerequisiti**: 
- Phase 1-8 completate ✅
- Phase 9.1-9.2 completate ✅
- Phase 9.3 DIFFERITA → Completa con questo piano ✅

---

## 🎯 Obiettivo Phase 10

Implementare interfaccia utente completa per gestione profili come specificato in `DESIGN_PROFILE_STATISTICS_SYSTEM.md`[cite:100]:

1. **Commit 10.1**: ProfileMenuPanel (wx.Dialog con 6 opzioni)
2. **Commit 10.2**: Create/Switch Profile dialogs
3. **Commit 10.3**: Rename/Delete Profile dialogs  
4. **Commit 10.4**: Wire DetailedStatsDialog (Phase 9.3) + Main menu integration

**Risultato finale**: Menu "P - Gestione Profili" completamente funzionante con tutti i dialogs wired.

---

## 📚 Context: Cosa Esiste Già

### ✅ Backend Completato (Feature 2)

**ProfileService** già implementato[cite:100]:
```python
# Disponibili in src/domain/services/profile_service.py
profile_service.create_profile(name: str) -> UserProfile
profile_service.switch_profile(profile_id: str) -> bool
profile_service.rename_profile(new_name: str) -> bool
profile_service.delete_profile(profile_id: str) -> bool
profile_service.list_profiles() -> List[Dict]
profile_service.active_profile -> UserProfile
```

### ✅ Dialog Stats Completati (Phase 5-6)

**DetailedStatsDialog** già creato[cite:103]:
- File: `src/presentation/dialogs/detailed_stats_dialog.py`
- 3 pagine navigabili (PageUp/PageDown)
- Pronto per essere wired al profile menu

### ✅ Menu Integration Parziale (Phase 9.1-9.2)

**MenuPanel modificato** in Phase 9[cite:99]:
- 5 pulsanti attuali: Gioca, Ultima Partita, Leaderboard, Opzioni, Esci
- Pattern pulsante nativo wxPython (TAB navigable, NVDA compatible)
- Serve aggiungere 6° pulsante "Gestione Profili"

---

## 📝 File Target Identificati

### Nuovo File da Creare

**File**: `src/infrastructure/ui/profile_menu_panel.py` (NEW)  
**Ruolo**: Dialog gestione profili con 6 opzioni + handler CRUD  
**Pattern**: Simile a OptionsDialog (modal dialog con pulsanti wx nativi)

### File da Modificare

1. **MenuPanel** (`src/infrastructure/ui/menu_panel.py`)  
   - Add: 6° pulsante "Gestione Profili"
   - Add: handler `on_profile_menu_click()`

2. **SolitarioController** (`acs_wx.py`)  
   - Add: `show_profile_menu()` method
   - Add: reference a ProfileMenuPanel

---

## 🔍 Design Reference

Dal `DESIGN_PROFILE_STATISTICS_SYSTEM.md`[cite:100]:

```markdown
### Submenu: Gestione Profili (P)

=== GESTIONE PROFILI ===

1. Cambia Profilo
2. Crea Nuovo Profilo
3. Rinomina Profilo Corrente
4. Elimina Profilo
5. Statistiche Dettagliate  ← Wire DetailedStatsDialog qui!
6. Imposta come Predefinito

ESC - Torna al Menu Principale
```

---

## ✅ COMMIT 10.1: ProfileMenuPanel Foundation (20-25 min)

### 🎯 Obiettivo

Creare `ProfileMenuPanel` con struttura base + 6 pulsanti nativi wxPython.

### 📝 File da Creare

**File**: `src/infrastructure/ui/profile_menu_panel.py` (NEW)

```python
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
        """Handle \"Cambia Profilo\" button (Commit 10.2)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.2
    
    def _on_create_profile(self, event: wx.CommandEvent) -> None:
        """Handle \"Crea Nuovo Profilo\" button (Commit 10.2)."""
        self._announce("Opzione non ancora implementata.", interrupt=True)
        # PLACEHOLDER - Implementato in Commit 10.2
    
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
    
    def _announce(self, text: str, interrupt: bool = False) -> None:
        """Announce text via TTS if screen reader available.
        
        Args:
            text: Text to announce
            interrupt: If True, interrupts current speech
        """
        if self.screen_reader and self.screen_reader.tts:
            self.screen_reader.tts.speak(text, interrupt=interrupt)
    
    def _refresh_active_label(self) -> None:
        """Update active profile label after profile switch.
        
        Called after successful switch/create to reflect new active profile.
        Updates label text and announces change.
        """
        active_name = self.profile_service.active_profile.profile_name if self.profile_service.active_profile else "Nessuno"
        self.active_label.SetLabel(f"Profilo Attivo: {active_name}")
        self.Layout()  # Re-layout to adjust label width


# Module-level documentation
__all__ = ['ProfileMenuPanel']
```

### ✅ Validation Commit 10.1

**Test manuali**:
1. Avvia app (profilo default caricato)
2. *(NON ANCORA WIREATO - test dopo Commit 10.4)*
3. Per ora: verifica che file compila senza errori

**Commit message**:
```
feat(ui): Add ProfileMenuPanel foundation [Phase 10.1/10]

- Create ProfileMenuPanel: modal dialog with 6 buttons
- Layout: Title, active profile label, 6 options, close button
- Buttons: native wxPython (TAB navigable, NVDA compatible)
- Options (placeholders): Switch, Create, Rename, Delete, Stats, Default
- TTS announcements on focus and actions
- ESC closes and returns to main menu
- Logging: dialog_shown/closed events

Handlers are placeholders - implemented in commits 10.2-10.4.

Refs: DESIGN_PROFILE_STATISTICS_SYSTEM.md UI/UX section
```

---

## ✅ COMMIT 10.2: Create + Switch Profile Dialogs (18-22 min)

### 🎯 Obiettivo

Implementare handlers `_on_create_profile()` e `_on_switch_profile()` con dialogs nativi wx.

### 📝 File da Modificare: ProfileMenuPanel

**File**: `src/infrastructure/ui/profile_menu_panel.py` (MODIFIED)

**Implementare handler Create Profile**:

```python
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
    """
    self._announce("Crea nuovo profilo.", interrupt=True)
    
    # Show text entry dialog
    dlg = wx.TextEntryDialog(
        self,
        "Inserisci nome del nuovo profilo:",
        "Crea Profilo",
        value="",
        style=wx.OK | wx.CANCEL | wx.CENTER
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
        log.info(f"Profile created: {new_profile.profile_id} ({profile_name})")
        
        # Auto-switch to new profile
        self.profile_service.switch_profile(new_profile.profile_id)
        
        # Refresh UI
        self._refresh_active_label()
        
        # Announce success
        self._announce(f"Profilo {profile_name} creato e attivato.", interrupt=True)
        
    except Exception as e:
        log.error_occurred("ProfileMenuPanel", f"Failed to create profile: {e}", e)
        wx.MessageBox(
            f"Errore durante creazione profilo: {e}",
            "Errore",
            wx.OK | wx.ICON_ERROR
        )
        self._announce("Errore creazione profilo.", interrupt=True)


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
    """
    self._announce("Cambia profilo.", interrupt=True)
    
    # Load all profiles
    all_profiles = self.profile_service.list_profiles()
    
    if len(all_profiles) <= 1:
        wx.MessageBox(
            "Nessun altro profilo disponibile.\\n"
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
            self._refresh_active_label()
            
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
```

### ✅ Validation Commit 10.2

**Test manuali**:
1. *(Dopo Commit 10.4: Main menu "P" → Profile menu)*
2. Pulsante "2. Crea Nuovo Profilo"
   - Input nome "TestPlayer"
   - Verifica: Profilo creato, label aggiornata "Profilo Attivo: TestPlayer"
   - TTS: "Profilo TestPlayer creato e attivato."
3. Pulsante "1. Cambia Profilo"
   - Verifica: Lista mostra profilo precedente + TestPlayer
   - Seleziona profilo precedente
   - Verifica: Label aggiornata, TTS annuncia cambio
4. Test edge cases:
   - Create con nome vuoto → Errore
   - Create con nome duplicato → Errore
   - Switch con solo 1 profilo → Messaggio info

**Commit message**:
```
feat(ui): Implement create/switch profile dialogs [Phase 10.2/10]

- Create profile: wx.TextEntryDialog with validation
  - Checks: non-empty, max 30 chars, no duplicates
  - Auto-switches to new profile after creation
  - Updates active label and announces success
- Switch profile: wx.SingleChoiceDialog with all profiles
  - Shows profile name + win stats
  - Marks current profile with "(attivo)"
  - Prevents selecting current profile
  - Updates UI after successful switch
- Error handling: validation failures, service errors
- TTS announcements for all actions
- Logging: profile_created, profile_switched events

Refs: DESIGN_PROFILE_STATISTICS_SYSTEM.md scenarios B, C
```

---

## ✅ COMMIT 10.3: Rename + Delete Profile Dialogs (15-18 min)

### 🎯 Obiettivo

Implementare handlers `_on_rename_profile()` e `_on_delete_profile()` con validazione e conferma.

### 📝 File da Modificare: ProfileMenuPanel

**File**: `src/infrastructure/ui/profile_menu_panel.py` (MODIFIED)

**Implementare handler Rename Profile**:

```python
def _on_rename_profile(self, event: wx.CommandEvent) -> None:
    """Handle \"Rinomina Profilo Corrente\" button.
    
    Flow:
    1. Check if active profile exists
    2. Show wx.TextEntryDialog with current name as default
    3. Validate new name (same rules as create)
    4. Call profile_service.rename_profile(new_name)
    5. Refresh active profile label
    6. Announce: "Profilo rinominato in: [nome]"
    
    Restrictions:
    - Guest profile cannot be renamed → Show error message
    - Same validation as create (non-empty, max 30, no duplicates)
    
    Note: Only renames active profile, not others.
    """
    self._announce("Rinomina profilo corrente.", interrupt=True)
    
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
        style=wx.OK | wx.CANCEL | wx.CENTER
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
    
    # Rename profile
    try:
        success = self.profile_service.rename_profile(new_name)
        
        if success:
            log.info(f"Profile renamed: {current_name} → {new_name}")
            
            # Refresh UI
            self._refresh_active_label()
            
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
    \"Sei sicuro di voler eliminare il profilo '[nome]'?
    Tutte le statistiche e partite salvate saranno perse.
    
    Questa operazione non può essere annullata.\"
    """
    self._announce("Elimina profilo.", interrupt=True)
    
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
            "Non puoi eliminare l'ultimo profilo rimanente.\\n"
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
        f"Sei sicuro di voler eliminare il profilo '{current_name}'?\\n\\n"
        f"Tutte le statistiche e partite salvate saranno perse.\\n\\n"
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
            log.info(f"Profile deleted: {current_id} ({current_name})")
            
            # Auto-switch to first available non-guest profile
            remaining = self.profile_service.list_profiles()
            next_profile = None
            for p in remaining:
                if not p.get('is_guest', False):
                    next_profile = p
                    break
            
            if next_profile:
                self.profile_service.switch_profile(next_profile['profile_id'])
            
            # Refresh UI
            self._refresh_active_label()
            
            # Announce
            new_name = self.profile_service.active_profile.profile_name
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
```

### ✅ Validation Commit 10.3

**Test manuali**:
1. **Rename Profile**:
   - Rinomina profilo attivo "TestPlayer" → "PlayerTest"
   - Verifica: Label aggiornata, TTS annuncia rinomina
   - Test edge case: Rinomina profilo Ospite → Errore
   
2. **Delete Profile**:
   - Crea profilo temporaneo "ToDelete"
   - Switch a "ToDelete"
   - Elimina "ToDelete" → Conferma YES
   - Verifica: Profilo eliminato, switch automatico a profilo precedente
   - Test edge case: Tenta eliminare ultimo profilo → Errore
   - Test edge case: Tenta eliminare profilo Ospite → Errore

**Commit message**:
```
feat(ui): Implement rename/delete profile dialogs [Phase 10.3/10]

- Rename profile: wx.TextEntryDialog with current name default
  - Validation: same as create (non-empty, max 30, no duplicates)
  - Guest profile cannot be renamed (shows error)
  - Updates active label and announces success
- Delete profile: wx.MessageDialog confirmation (destructive action)
  - Warns about data loss (stats + sessions)
  - Guest profile cannot be deleted (shows error)
  - Last profile cannot be deleted (shows error)
  - Auto-switches to first available profile after deletion
  - Updates UI and announces new active profile
- Error handling: validation, service errors, edge cases
- TTS announcements for all actions
- Logging: profile_renamed, profile_deleted events

Refs: DESIGN_PROFILE_STATISTICS_SYSTEM.md profile CRUD
```

---

## ✅ COMMIT 10.4: Wire Stats + Set Default + Main Menu Integration (15-20 min)

### 🎯 Obiettivo

1. Wire `_on_show_stats()` a DetailedStatsDialog (Phase 9.3 COMPLETA!)
2. Implementare `_on_set_default()`
3. Aggiungere pulsante "Gestione Profili" al menu principale

### 📝 File da Modificare: ProfileMenuPanel

**File**: `src/infrastructure/ui/profile_menu_panel.py` (MODIFIED)

**Implementare handlers Stats + Set Default**:

```python
def _on_show_stats(self, event: wx.CommandEvent) -> None:
    """Handle \"Statistiche Dettagliate\" button.
    
    Opens DetailedStatsDialog (Phase 5) with active profile stats.
    This is Phase 9.3 completion (deferred from Phase 9)!
    
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
        'global_stats': profile.global_stats,
        'timer_stats': profile.timer_stats,
        'difficulty_stats': profile.difficulty_stats,
        'scoring_stats': profile.scoring_stats
    }
    
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
    2. Call profile_service.set_default_profile(profile_id)
    3. Show success message
    4. Announce: "Profilo impostato come predefinito"
    
    Note: Only one profile can be default at a time (service handles this).
    Guest profile CAN be set as default (use case: family PC shared mode).
    
    Success message:
    \"Profilo '[nome]' impostato come predefinito.
    Sarà caricato automaticamente all'avvio dell'applicazione.\"
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
    
    # Set as default
    try:
        success = self.profile_service.set_default_profile(current_id)
        
        if success:
            log.info(f"Default profile set: {current_id} ({current_name})")
            
            # Show success message
            wx.MessageBox(
                f"Profilo '{current_name}' impostato come predefinito.\\n\\n"
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
```

### 📝 File da Modificare: MenuPanel

**File**: `src/infrastructure/ui/menu_panel.py` (MODIFIED)

**Modifiche** (aggiungere 6° pulsante "Gestione Profili"):

```python
# In init_ui_elements() method

def init_ui_elements(self) -> None:
    \"\"\"Create menu buttons with accessibility (single-frame pattern).
    
    Creates:
    - Title label (bold, 16pt)
    - Play button → controller.start_gameplay()
    - Last Game button → controller.show_last_game_summary() (v3.1.0)
    - Leaderboard button → controller.show_leaderboard() (v3.1.0)
    - Profile Menu button → controller.show_profile_menu() (v3.1.0 Phase 10)  ← NEW!
    - Options button → controller.show_options()
    - Exit button → controller.show_exit_dialog()
    \"\"\"
    # Title label (bold, 16pt)
    title = wx.StaticText(self, label="Menu Principale")
    title.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
    self.sizer.Add(title, flag=wx.CENTER | wx.TOP, border=20)
    
    # Create buttons
    btn_play = wx.Button(self, label="Gioca al solitario classico")
    btn_play.Bind(wx.EVT_BUTTON, self.on_play_click)
    btn_play.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    btn_last_game = wx.Button(self, label="Ultima Partita (risultati)")
    btn_last_game.Bind(wx.EVT_BUTTON, self.on_last_game_click)
    btn_last_game.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    btn_leaderboard = wx.Button(self, label="Leaderboard Globale")
    btn_leaderboard.Bind(wx.EVT_BUTTON, self.on_leaderboard_click)
    btn_leaderboard.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    # NEW: Profile Menu button
    btn_profile_menu = wx.Button(self, label="Gestione Profili")
    btn_profile_menu.Bind(wx.EVT_BUTTON, self.on_profile_menu_click)
    btn_profile_menu.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    btn_options = wx.Button(self, label="Opzioni di gioco")
    btn_options.Bind(wx.EVT_BUTTON, self.on_options_click)
    btn_options.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    btn_exit = wx.Button(self, label="Esci dal gioco")
    btn_exit.Bind(wx.EVT_BUTTON, self.on_exit_click)
    btn_exit.Bind(wx.EVT_SET_FOCUS, self.on_button_focus)
    
    # Add buttons to vertical sizer
    btn_sizer = wx.BoxSizer(wx.VERTICAL)
    for btn in [btn_play, btn_last_game, btn_leaderboard, btn_profile_menu, btn_options, btn_exit]:  # ADD btn_profile_menu
        btn_sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 20)
    
    self.sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER)
    
    # Set initial focus and announce menu opened
    btn_play.SetFocus()
    self.announce("Menu principale. 6 opzioni disponibili.", interrupt=True)  # UPDATE: 5 → 6


# Add handler for profile menu button
def on_profile_menu_click(self, event: wx.CommandEvent) -> None:
    \"\"\"Handle \"Gestione Profili\" button click.
    
    Delegates to controller.show_profile_menu() which displays
    the ProfileMenuPanel modal dialog.
    
    Args:
        event: wx.CommandEvent from button click or ENTER key
    
    Version:
        v3.1.0 Phase 10.4
    \"\"\"
    if self.controller and hasattr(self.controller, 'show_profile_menu'):
        self.controller.show_profile_menu()
```

### 📝 File da Modificare: SolitarioController

**File**: `acs_wx.py` (MODIFIED)

**Aggiungere metodo show_profile_menu()**:

```python
# In SolitarioController class

def show_profile_menu(self) -> None:
    \"\"\"Show profile management menu (called from MenuPanel).
    
    Opens ProfileMenuPanel modal dialog with:
    - 6 options: Switch, Create, Rename, Delete, Stats, Set Default
    - Native wxPython buttons (TAB navigable, NVDA compatible)
    - Real-time profile updates reflected in menu
    
    Returns to main menu when closed (ESC or Close button).
    
    Version:
        v3.1.0 Phase 10.4
    \"\"\"
    from src.infrastructure.ui.profile_menu_panel import ProfileMenuPanel
    
    log.info("Profile menu requested from main menu")
    
    # Check if ProfileService is available
    if not self.engine or not hasattr(self.engine, 'profile_service'):
        log.warning_issued("SolitarioController", "ProfileService not available")
        wx.MessageBox(
            "Servizio profili non disponibile.",
            "Errore",
            wx.OK | wx.ICON_ERROR
        )
        return
    
    profile_service = self.engine.profile_service
    if profile_service is None:
        log.warning_issued("SolitarioController", "ProfileService not initialized")
        wx.MessageBox(
            "Servizio profili non inizializzato.",
            "Errore",
            wx.OK | wx.ICON_ERROR
        )
        return
    
    # Open ProfileMenuPanel modal
    panel = ProfileMenuPanel(
        parent=self.frame,
        profile_service=profile_service,
        screen_reader=self.screen_reader
    )
    panel.ShowModal()
    panel.Destroy()
    
    log.info("Profile menu closed, returned to main menu")
```

### ✅ Validation Commit 10.4

**Test manuali**:
1. **Main Menu Integration**:
   - Avvia app → Menu principale
   - Verifica: 6 pulsanti visibili (Gioca, Ultima Partita, Leaderboard, **Gestione Profili**, Opzioni, Esci)
   - TTS: "Menu principale. 6 opzioni disponibili."
   
2. **Profile Menu Access**:
   - Clicca "Gestione Profili" (o TAB + ENTER)
   - Verifica: ProfileMenuPanel appare
   - TTS: "Gestione Profili. Profilo attivo: [nome]. 6 opzioni disponibili."
   
3. **Detailed Stats (Phase 9.3 FINALE!)**:
   - In profile menu, clicca "5. Statistiche Dettagliate"
   - Verifica: DetailedStatsDialog appare con 3 pagine
   - Verifica: PageUp/PageDown funzionano
   - Verifica: ESC chiude e torna a profile menu
   
4. **Set Default**:
   - Crea profilo "TestDefault"
   - Switch a "TestDefault"
   - Clicca "6. Imposta come Predefinito"
   - Verifica: Messaggio successo "Sarà caricato automaticamente..."
   - Chiudi app e riavvia
   - Verifica: "TestDefault" è profilo attivo all'avvio

5. **Full Workflow**:
   - Create profile "Player1"
   - Switch to "Player1"
   - View detailed stats (vuote, nuov profilo)
   - Rename to "Player1Renamed"
   - Set as default
   - Create profile "Player2"
   - Switch back to "Player1Renamed"
   - Delete "Player2"
   - Verify all operations work seamlessly

**Commit message**:
```
feat(ui): Wire stats dialog + set default + main menu integration [Phase 10.4/10]

- ProfileMenuPanel: Implement show_stats handler
  - Opens DetailedStatsDialog (Phase 5) with active profile stats
  - Completes Phase 9.3 (deferred task)!
  - Shows 3 pages: global, timer, scoring/difficulty
- ProfileMenuPanel: Implement set_default handler
  - Marks active profile as default (auto-load on startup)
  - Success message explains behavior
  - Guest profile can be set as default
- MenuPanel: Add 6th button "Gestione Profili"
  - Updated TTS: "6 opzioni disponibili"
  - Handler: on_profile_menu_click()
- SolitarioController: Add show_profile_menu() method
  - Opens ProfileMenuPanel modal
  - Validates ProfileService availability
  - Returns to main menu on close
- All ProfileMenuPanel handlers now implemented (10.1-10.4)
- NVDA compatible throughout
- Logging: all profile operations

Closes: Phase 9.3 (detailed stats in profile menu)
Closes: Phase 10 (Profile Management UI)
Feature 3 now 100% complete!

Refs: DESIGN_PROFILE_STATISTICS_SYSTEM.md UI/UX section
Refs: IMPLEMENTATION_STATS_PRESENTATION.md Phase 9.3
```

---

## ✅ Phase 10 COMPLETA!

### 📊 Risultati Finali

**Commit totali**: 4  
**Tempo effettivo**: 60-75 minuti  
**File creati**: 1 (`profile_menu_panel.py`)  
**File modificati**: 3 (`menu_panel.py`, `acs_wx.py`, `profile_menu_panel.py`)

**Funzionalità implementate**:
- ✅ ProfileMenuPanel con 6 opzioni native wxPython
- ✅ Create Profile (validation + auto-switch)
- ✅ Switch Profile (list selector + stats preview)
- ✅ Rename Profile (validation + guest protection)
- ✅ Delete Profile (confirmation + auto-switch + safeguards)
- ✅ **Detailed Stats (Phase 9.3 COMPLETA!)**
- ✅ Set Default Profile (startup behavior)
- ✅ Main menu integration (6° pulsante)
- ✅ NVDA accessibility completa (TTS, focus, keyboard)

### 🎉 Feature 3 COMPLETATA AL 100%!

**Phase 9.3 differita** → **ORA COMPLETA** in Phase 10.4!

```markdown
# Feature 3: Stats Presentation v3.1.0 UI

**Status**: ✅ COMPLETATA AL 100%

**Componenti**:
- ✅ Phase 1-6: All dialogs (Victory, Abandon, GameInfo, DetailedStats, Leaderboard)
- ✅ Phase 7-8: GameEngine integration + NVDA polish
- ✅ Phase 9.1: LastGameDialog + menu "U"
- ✅ Phase 9.2: Leaderboard + menu "L"
- ✅ Phase 9.3: **Detailed stats wired (via Phase 10.4)** ← NOW DONE!
- ✅ Phase 10: Profile Management UI completa

**Feature Stack**:
- ✅ Feature 1: Timer System (v2.7.0)
- ✅ Feature 2: Profile System Backend (v3.0.0)
- ✅ Feature 3: Stats Presentation UI (v3.1.0) ← COMPLETE!
```

---

## 📝 Update Documentation

Dopo Phase 10 completa, aggiornare:

### TODO.md

```markdown
# In TODO.md

## 🎯 Feature 3: Stats Presentation v3.1.0 UI

- [x] **Phase 9.1**: "Ultima Partita" menu option
- [x] **Phase 9.2**: Leaderboard menu option
- [x] **Phase 9.3**: Detailed stats in profile menu (via Phase 10.4)
- [x] **Phase 10**: Profile Management UI
  - [x] Phase 10.1: ProfileMenuPanel foundation
  - [x] Phase 10.2: Create + Switch profile dialogs
  - [x] Phase 10.3: Rename + Delete profile dialogs
  - [x] Phase 10.4: Wire stats + Set default + Main menu integration
- [x] **✅ Feature 3 COMPLETATA AL 100%**
```

### IMPLEMENTATION_STATS_PRESENTATION.md

```markdown
# In IMPLEMENTATION_STATS_PRESENTATION.md

- [x] **Phase 9**: Menu integration (3 commits)
  - [x] 9.1: LastGameDialog + menu "U"
  - [x] 9.2: Leaderboard + menu "L"
  - [x] 9.3: ~~Deferred~~ → **Completed in Phase 10.4** ✅
- [x] **Phase 10**: Profile Management UI (4 commits) ← ADD THIS
  - [x] 10.1: ProfileMenuPanel foundation
  - [x] 10.2: Create + Switch dialogs
  - [x] 10.3: Rename + Delete dialogs
  - [x] 10.4: Wire stats + integration

**FEATURE 3 STATUS**: ✅ 100% COMPLETA
```

---

## 🧪 Testing Finale Completo

### Manual NVDA Checklist (40+ items)

**Profile Menu Integration**:
- [ ] Main menu: 6 pulsanti visibili e navigabili con TAB
- [ ] TTS annuncia: "Menu principale. 6 opzioni disponibili."
- [ ] Pulsante "Gestione Profili" focus e ENTER apre ProfileMenuPanel

**ProfileMenuPanel**:
- [ ] Dialog apre con titolo "GESTIONE PROFILI"
- [ ] TTS annuncia: "Gestione Profili. Profilo attivo: [nome]. 6 opzioni disponibili."
- [ ] Label "Profilo Attivo: [nome]" visibile
- [ ] 6 pulsanti navigabili con TAB
- [ ] ESC chiude e torna a main menu

**Create Profile**:
- [ ] Dialog input testo appare
- [ ] Nome vuoto → Errore + TTS
- [ ] Nome > 30 char → Errore + TTS
- [ ] Nome duplicato → Errore + TTS
- [ ] Nome valido → Profilo creato + auto-switch + TTS annuncia successo
- [ ] Label "Profilo Attivo" aggiornata

**Switch Profile**:
- [ ] Lista profili appare con wx.SingleChoiceDialog
- [ ] Profilo corrente marcato con "(attivo)"
- [ ] Mostra statistiche (vittorie/partite) per ogni profilo
- [ ] Selezione profilo diverso → Switch + TTS annuncia cambio
- [ ] Label "Profilo Attivo" aggiornata
- [ ] Solo 1 profilo → Messaggio "Nessun altro profilo disponibile"

**Rename Profile**:
- [ ] Dialog input testo con nome corrente precompilato
- [ ] Validazione come Create (vuoto, troppo lungo, duplicato)
- [ ] Profilo Ospite → Errore "non rinominabile"
- [ ] Nome valido → Rinomina + TTS annuncia successo
- [ ] Label "Profilo Attivo" aggiornata

**Delete Profile**:
- [ ] Dialog conferma appare con warning distruttivo
- [ ] Profilo Ospite → Errore "non eliminabile"
- [ ] Ultimo profilo → Errore "impossibile eliminare"
- [ ] Conferma YES → Profilo eliminato + auto-switch + TTS annuncia
- [ ] Label "Profilo Attivo" aggiornata
- [ ] Conferma NO → Annullato + TTS

**Detailed Stats (Phase 9.3!)** ← KEY TEST!
- [ ] Pulsante "5. Statistiche Dettagliate" apre DetailedStatsDialog
- [ ] Dialog mostra 3 pagine (Globali, Timer, Punteggio)
- [ ] PageUp/PageDown cambia pagina
- [ ] ESC chiude dialog e torna a ProfileMenuPanel (non main menu!)
- [ ] TTS annuncia statistiche su ogni pagina
- [ ] Statistiche profilo vuoto mostrano valori 0/default

**Set Default**:
- [ ] Pulsante "6. Imposta come Predefinito"
- [ ] Messaggio successo "Sarà caricato automaticamente..."
- [ ] TTS annuncia impostazione
- [ ] Chiudi app + riavvia → Profilo default caricato all'avvio

**Integration Flow**:
- [ ] Main menu → Profile menu → Create → Switch → Rename → Delete → Stats → Set default → Close → Main menu
- [ ] Tutti i passaggi fluidi senza crash
- [ ] TTS appropriato in ogni step
- [ ] Focus management corretto

---

## 🚀 Pronto per Merge!

Dopo Phase 10 completa + testing NVDA + testing manuale:

1. **Update CHANGELOG.md** con v3.1.0 features complete
2. **Update README.md** (screenshot menu con 6 pulsanti)
3. **Commit finale**: `chore: Complete v3.1.0 - Stats Presentation + Profile UI`
4. **Tag release**: `git tag v3.1.0`
5. **Merge** `copilot/implement-profile-system-v3-1-0` → `refactoring-engine`
6. **Celebrate!** 🎉

**Feature 3 completamente implementata - ZERO debito tecnico!**

---

## 📚 Riferimenti

- **Design**: `DESIGN_PROFILE_STATISTICS_SYSTEM.md` (UI/UX section)
- **Backend**: Feature 2 - Profile System (ProfileService CRUD)
- **Dialogs**: Phase 5 (DetailedStatsDialog) + Phase 6 (LeaderboardDialog)
- **Menu Integration**: Phase 9 (LastGameDialog + Leaderboard menu)
- **Phase 9.3 Deferred**: Now completed in Phase 10.4!

**Documento creato**: 17 Febbraio 2026, 20:21 CET  
**Autore**: Perplexity AI (su richiesta Luca)  
**Prossimo Step**: Implementazione Phase 10 con GitHub Copilot Agent
