"""wxPython implementation of DialogProvider.

This module provides native modal dialogs using wxPython library.
Dialogs are accessible to screen readers (NVDA, JAWS on Windows).

Platform support:
    - Windows: Full support (NVDA, JAWS tested)
    - Linux: Partial (Orca may have focus issues with modals)
    - macOS: Not tested (should work with VoiceOver)

Known limitations:
    - Multiple wx.App() instances per session (harmless but verbose logs)
    - Focus stealing from pygame window (restored on close)
    - No async support (intentional - simplifies screen reader integration)
"""

import wx
from typing import Optional, Dict, Any, Callable

from src.infrastructure.ui.dialog_provider import DialogProvider


class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Args (v1.6.3.2):
        parent: IGNORED. Uses invisible wx.Frame as parent for all dialogs.
    
    Behavior (v1.6.3.2):
        - Creates invisible wx.Frame with wx.FRAME_NO_TASKBAR
        - All dialogs are children of this frame
        - Frame doesn't appear in ALT+TAB (NO_TASKBAR flag)
        - Dialogs don't appear in ALT+TAB (modal children)
    
    Note:
        Previous attempts (v1.6.3-v1.6.3.1) used pygame HWND with
        AssociateHandle(), but that doesn't establish proper modal
        parent-child relationships in wxPython. Invisible frame is
        the standard pattern for pygame+wxPython integration.
    
    Example:
        >>> provider = WxDialogProvider()  # No parent needed!
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog is child of invisible frame, won't show in ALT+TAB
    """
    
    def __init__(self, parent_frame: Optional[wx.Frame] = None):
        """Initialize with parent frame for proper modal hierarchy (v2.0.1).
        
        Args:
            parent_frame: Optional wx.Frame to use as parent for all dialogs.
                         If None, creates invisible frame (legacy behavior).
                         If provided, dialogs will be modal children of this frame.
        
        Note:
            hs_deckmanager pattern: Always provide parent_frame for proper
            modal relationships. Dialogs will appear over parent and won't
            show as separate windows in ALT+TAB.
        """
        super().__init__()
        self.parent_frame = parent_frame  # Store parent frame reference
        self._parent_frame = None  # Invisible wx.Frame (lazy init, fallback)
    
    def _get_parent(self):
        """Get parent frame for dialogs (v2.0.1 - hs_deckmanager pattern).
        
        Returns:
            wx.Frame: Parent frame for dialog parenting
        
        Note:
            If parent_frame was provided in __init__, use it (preferred).
            Otherwise, create invisible frame (legacy fallback).
            
            hs_deckmanager pattern: Always use explicit parent_frame for
            proper modal hierarchy and OS focus management.
        """
        # Use explicit parent frame if provided (hs_deckmanager pattern)
        if self.parent_frame is not None:
            return self.parent_frame
        
        # Fallback: Create invisible frame (lazy init)
        if self._parent_frame is not None:
            return self._parent_frame
        
        # Create invisible frame (no taskbar, hidden)
        self._parent_frame = wx.Frame(
            None,
            title="Solitario Dialog Parent",
            style=wx.FRAME_NO_TASKBAR  # CRITICAL: No ALT+TAB
        )
        # DO NOT call Show() - keep invisible!
        
        return self._parent_frame
    
    def show_alert(self, message: str, title: str) -> None:
        """DEPRECATED: Use show_info_async() to avoid nested event loops.
        
        Synchronous API maintained for backward compatibility.
        Will be removed in v3.0.
        
        Uses wx.MessageDialog with wx.OK | wx.ICON_INFORMATION.
        Screen reader announces title + message when dialog opens.
        
        Args:
            message: Alert content (supports multi-line with \\n)
            title: Window title
        """
        app = wx.App()  # Create app instance (on-demand pattern)
        dlg = wx.MessageDialog(
            self._get_parent(),  # Lazy handle conversion (prevents ALT+TAB separation)
            message,
            title,
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
        wx.Yield()  # Process pending events (important for screen reader focus)
    
    def show_yes_no(self, question: str, title: str) -> bool:
        """DEPRECATED: Use show_yes_no_async() to avoid nested event loops.
        
        Synchronous API maintained for backward compatibility.
        Will be removed in v3.0.
        
        Uses wx.MessageDialog with wx.YES_NO | wx.NO_DEFAULT.
        NO is default to prevent accidental confirmations.
        
        Args:
            question: Question text
            title: Window title
            
        Returns:
            True if Yes clicked, False if No clicked or dialog closed (ESC)
        """
        app = wx.App()
        dlg = wx.MessageDialog(
            self._get_parent(),  # Lazy handle conversion (prevents ALT+TAB separation)
            question,
            title,
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
        )
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        wx.Yield()
        return result
    
    def show_input(
        self,
        question: str,
        title: str,
        default: str = ""
    ) -> Optional[str]:
        """DEPRECATED: Synchronous API maintained for backward compatibility.
        
        Will be removed in v3.0. Consider using async pattern for future features.
        
        Uses wx.TextEntryDialog.
        Returns None if user cancels (ESC or Cancel button).
        
        Args:
            question: Prompt text
            title: Window title
            default: Pre-filled text value
            
        Returns:
            User input string, or None if cancelled
        """
        app = wx.App()
        dlg = wx.TextEntryDialog(
            self._get_parent(),  # Lazy handle conversion (prevents ALT+TAB separation)
            question,
            title,
            value=default
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            result = dlg.GetValue()
            dlg.Destroy()
            wx.Yield()
            return result
        else:
            dlg.Destroy()
            wx.Yield()
            return None
    
    def show_yes_no_async(
        self,
        title: str,
        message: str,
        callback: Callable[[bool], None]
    ) -> None:
        """Show yes/no dialog (semi-modal) with deferred callback.
        
        Pattern: ShowModal() called from wx.CallAfter() prevents nested event loops
        while ensuring proper dialog lifecycle (YES/NO/ESC all handled correctly).
        
        Architecture:
            1. Method returns immediately (non-blocking for caller)
            2. wx.CallAfter() schedules show_modal_and_callback() for next idle
            3. [wxPython processes current event handler to completion]
            4. [wxPython idle loop picks up deferred call]
            5. show_modal_and_callback() executes in clean context
            6. ShowModal() blocks until user responds (safe, no nested loop)
            7. Dialog destroyed, callback invoked, focus restored
        
        Why ShowModal is Safe Here:
            - Called from wx.CallAfter() = deferred context (not event handler)
            - No nested event loop because original handler already completed
            - All dialog buttons (YES/NO/ESC/X) work correctly
            - Focus returns to parent automatically after Destroy()
        
        Args:
            title: Dialog title
            message: Dialog message  
            callback: Function called with result (True=Yes, False=No/ESC/X)
        
        Example:
            >>> def on_result(confirmed: bool):
            ...     if confirmed:
            ...         print("User confirmed")
            ...     else:
            ...         print("User declined or cancelled")
            >>> provider.show_yes_no_async("Conferma", "Sei sicuro?", on_result)
            # Returns immediately, callback invoked after user responds
        
        Version:
            v2.2: Added async API to prevent nested event loops
            v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
        """
        
        def show_modal_and_callback():
            """Deferred function that shows modal dialog and invokes callback.
            
            This function executes in deferred context (wx.CallAfter), ensuring:
            - No nested event loop (original handler already completed)
            - ShowModal() blocks safely until user responds
            - All dialog buttons work correctly (YES/NO/ESC/X)
            - Dialog always destroyed (no memory leaks)
            - Callback invoked with correct result
            - Focus returns to parent automatically
            """
            # Create modal dialog
            dialog = wx.MessageDialog(
                parent=self._get_parent(),
                message=message,
                caption=title,
                style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
            )
            
            # ShowModal blocks until user clicks YES/NO/ESC/X
            # Returns: wx.ID_YES, wx.ID_NO, or wx.ID_CANCEL
            result_code = dialog.ShowModal()
            
            # Interpret result (True for YES, False for NO/ESC/X)
            result = (result_code == wx.ID_YES)
            
            # CRITICAL: Always destroy dialog (prevents memory leaks)
            dialog.Destroy()
            
            # Invoke callback with result (already in deferred context, safe)
            callback(result)
        
        # Defer entire dialog sequence to next idle cycle
        # This prevents nested event loops and ensures clean execution
        wx.CallAfter(show_modal_and_callback)
    
    def show_info_async(
        self,
        title: str,
        message: str,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Show non-blocking info dialog with optional callback.
        
        Args:
            title: Dialog title
            message: Info message
            callback: Optional function called when dialog closes
        
        Version:
            v2.2: Added async API
        """
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.OK | wx.ICON_INFORMATION
        )
        
        def on_dialog_close(event):
            dialog.Destroy()
            if callback:
                callback()
        
        dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
        dialog.Show()
    
    def show_error_async(
        self,
        title: str,
        message: str,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Show non-blocking error dialog with optional callback.
        
        Args:
            title: Dialog title
            message: Error message
            callback: Optional function called when dialog closes
        
        Version:
            v2.2: Added async API
        """
        dialog = wx.MessageDialog(
            parent=self._get_parent(),
            message=message,
            caption=title,
            style=wx.OK | wx.ICON_ERROR
        )
        
        def on_dialog_close(event):
            dialog.Destroy()
            if callback:
                callback()
        
        dialog.Bind(wx.EVT_CLOSE, on_dialog_close)
        dialog.Show()
    
    def show_statistics_report(
        self,
        stats: Dict[str, Any],
        final_score: Optional[Dict[str, Any]],
        is_victory: bool,
        deck_type: str
    ) -> None:
        """Show structured statistics report dialog.
        
        Creates a modal dialog with:
        - Title: "Congratulazioni!" (victory) or "Partita Terminata" (defeat)
        - Multiline TextCtrl displaying formatted report
        - Read-only, wordwrap, auto-focused for NVDA
        - OK button to close
        
        Args:
            stats: Final statistics dictionary
            final_score: Optional score breakdown
            is_victory: True if all 4 suits completed
            deck_type: "french" or "neapolitan" for suit name formatting
        
        Screen reader behavior:
            - NVDA reads entire report immediately on dialog open (SetFocus)
            - Report is structured with newlines for natural pauses
            - OK button accessible via TAB or ENTER
        
        Example:
            >>> provider.show_statistics_report(
            ...     stats={'elapsed_time': 125.5, 'move_count': 87, ...},
            ...     final_score={'final_score': 1250, ...},
            ...     is_victory=True,
            ...     deck_type="french"
            ... )
            # Dialog appears with formatted report
            # NVDA reads: "Congratulazioni! Hai Vinto! Tempo: 2 minuti..."
        """
        # Generate formatted report using ReportFormatter
        from src.presentation.formatters.report_formatter import ReportFormatter
        
        report_text = ReportFormatter.format_final_report(
            stats=stats,
            final_score=final_score,
            is_victory=is_victory,
            deck_type=deck_type
        )
        
        # Create wx.App instance (on-demand pattern)
        app = wx.App()
        
        # Create dialog with title
        title = "Congratulazioni!" if is_victory else "Partita Terminata"
        
        dlg = wx.Dialog(
            self._get_parent(),  # Lazy handle conversion (prevents ALT+TAB separation)
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.FRAME_FLOAT_ON_PARENT  # 🆕 v1.6.3 - Modal!
        )
        
        # Create vertical sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add multiline TextCtrl (read-only, wordwrap, accessible)
        text_ctrl = wx.TextCtrl(
            dlg,
            value=report_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
        )
        
        # Set minimum size for readability
        text_ctrl.SetMinSize((500, 350))
        
        # Add to sizer with expansion
        sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Add OK button (centered)
        btn_ok = wx.Button(dlg, wx.ID_OK, "OK")
        sizer.Add(btn_ok, 0, wx.ALL | wx.CENTER, 10)
        
        # Apply layout and center on screen
        dlg.SetSizer(sizer)
        dlg.Fit()
        dlg.CenterOnScreen()
        
        # CRITICAL: Auto-focus TextCtrl for immediate NVDA announcement
        # Must be done AFTER layout is complete
        text_ctrl.SetFocus()
        
        # Show modal (blocks until user clicks OK or presses ESC/ENTER)
        dlg.ShowModal()
        dlg.Destroy()
        
        # Yield to ensure focus returns to pygame window
        wx.Yield()
