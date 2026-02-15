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
from src.infrastructure.logging import game_logger as log


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
        
        # Log dialog shown
        log.dialog_shown("yes_no", title)
        
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
            
            # Log dialog closed with result
            log.dialog_closed("yes_no", "yes" if result else "no")
            
            # CRITICAL: Always destroy dialog (prevents memory leaks)
            dialog.Destroy()
            
            # Invoke callback with result (already in deferred context, safe)
            callback(result)
        
        # Defer entire dialog sequence to next idle cycle
        # This prevents nested event loops and ensures clean execution
        # wxPython handles graceful shutdown automatically - no check needed
        wx.CallAfter(show_modal_and_callback)
    
    def show_rematch_prompt_async(
        self,
        callback: Callable[[bool], None]
    ) -> None:
        """Show rematch confirmation dialog (non-blocking).
        
        Asks user if they want to play another game after completing current one.
        Wrapper around show_yes_no_async() with Italian rematch message.
        
        Args:
            callback: Function called with result (True=rematch, False=return to menu)
        
        Italian message:
            Title: "Rivincita?"
            Message: "Vuoi giocare ancora?"
        
        Flow:
            1. Dialog.Show() called (non-blocking)
            2. User responds YES/NO
            3. Dialog closes
            4. [wxPython event loop processes callback]
            5. callback(wants_rematch) invoked (deferred context)
            6. Caller handles rematch logic safely
        
        Note:
            This method provides the same async pattern as show_abandon_game_prompt_async(),
            show_new_game_prompt_async(), and show_exit_app_prompt_async() in DialogManager.
            Ensures consistent behavior across all game flow dialogs.
        
        Example:
            >>> def on_result(wants_rematch):
            ...     if wants_rematch:
            ...         self.start_gameplay()
            ...     else:
            ...         self._safe_return_to_main_menu()
            >>> provider.show_rematch_prompt_async(on_result)
        
        Version:
            v2.5.0: Added for Bug #68 async refactoring (final fix)
        """
        # Delegate to show_yes_no_async with rematch-specific message
        self.show_yes_no_async(
            title="Rivincita?",
            message="Vuoi giocare ancora?",
            callback=callback
        )
    
    def show_info_async(
        self,
        title: str,
        message: str,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Show info dialog (semi-modal) with optional callback.
        
        Pattern: ShowModal() called from wx.CallAfter() for consistency with
        show_yes_no_async(). Ensures proper dialog lifecycle.
        
        Args:
            title: Dialog title
            message: Info message
            callback: Optional function called after dialog closes
        
        Example:
            >>> def on_closed():
            ...     print("Info dialog closed")
            >>> provider.show_info_async("Info", "Partita avviata!", on_closed)
        
        Version:
            v2.2: Added async API
            v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
        """
        
        def show_modal_and_callback():
            """Deferred function that shows modal info dialog."""
            dialog = wx.MessageDialog(
                parent=self._get_parent(),
                message=message,
                caption=title,
                style=wx.OK | wx.ICON_INFORMATION
            )
            
            # ShowModal blocks until user clicks OK or ESC
            dialog.ShowModal()
            
            # Always destroy dialog
            dialog.Destroy()
            
            # Invoke optional callback
            if callback:
                callback()
        
        # Defer entire dialog sequence
        wx.CallAfter(show_modal_and_callback)
    
    def show_error_async(
        self,
        title: str,
        message: str,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Show error dialog (semi-modal) with optional callback.
        
        Pattern: ShowModal() called from wx.CallAfter() for consistency with
        show_yes_no_async(). Ensures proper dialog lifecycle.
        
        Args:
            title: Dialog title
            message: Error message
            callback: Optional function called after dialog closes
        
        Example:
            >>> def on_closed():
            ...     print("Error acknowledged")
            >>> provider.show_error_async("Errore", "Mossa non valida!", on_closed)
        
        Version:
            v2.2: Added async API
            v2.2.1: Fixed to use semi-modal pattern (ShowModal + CallAfter)
        """
        
        def show_modal_and_callback():
            """Deferred function that shows modal error dialog."""
            dialog = wx.MessageDialog(
                parent=self._get_parent(),
                message=message,
                caption=title,
                style=wx.OK | wx.ICON_ERROR
            )
            
            # ShowModal blocks until user clicks OK or ESC
            dialog.ShowModal()
            
            # Always destroy dialog
            dialog.Destroy()
            
            # Invoke optional callback
            if callback:
                callback()
        
        # Defer entire dialog sequence
        wx.CallAfter(show_modal_and_callback)
    
    def show_statistics_report_async(
        self,
        stats: Dict[str, Any],
        final_score: Optional[Dict[str, Any]],
        is_victory: bool,
        deck_type: str,
        callback: Callable[[], None]
    ) -> None:
        """Show structured statistics report dialog (NON-BLOCKING).
        
        Async version that uses wx.CallAfter() to avoid nested event loop issues.
        
        Args:
            stats: Final statistics dictionary
            final_score: Optional score breakdown
            is_victory: True if all 4 suits completed
            deck_type: "french" or "neapolitan" for suit name formatting
            callback: Function called when dialog closes (no arguments)
        
        Flow:
            1. Method returns immediately (non-blocking)
            2. wx.CallAfter() schedules show_modal_and_callback()
            3. [wxPython idle loop picks up deferred call]
            4. Dialog shown with ShowModal() (safe in deferred context)
            5. User presses OK or ESC
            6. Dialog destroyed
            7. callback() invoked (deferred context)
            8. Caller continues flow (e.g., show rematch dialog)
        
        Why This Works:
            - No wx.App() creation (uses existing app instance)
            - ShowModal() in deferred context = no nested event loop
            - wx.GetApp() always valid after this pattern
            - Consistent with all other async dialogs
        
        Example:
            >>> def on_stats_closed():
            ...     print("Stats closed, showing rematch dialog...")
            ...     self.show_rematch_prompt_async(on_rematch)
            >>> provider.show_statistics_report_async(
            ...     stats, score, True, 'french', on_stats_closed
            ... )
            # Returns immediately, callback invoked after user closes dialog
        
        Version:
            v2.5.0: Refactored to async for Bug #68 regressione fix
        """
        
        def show_modal_and_callback():
            """Deferred function: show modal dialog then invoke callback."""
            # Generate formatted report using ReportFormatter
            from src.presentation.formatters.report_formatter import ReportFormatter
            
            report_text = ReportFormatter.format_final_report(
                stats=stats,
                final_score=final_score,
                is_victory=is_victory,
                deck_type=deck_type
            )
            
            # Get parent frame (NO wx.App() creation!)
            parent = self._get_parent()
            
            # Create dialog with title
            title = "Congratulazioni!" if is_victory else "Partita Terminata"
            
            dlg = wx.Dialog(
                parent,
                title=title,
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.FRAME_FLOAT_ON_PARENT
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
            text_ctrl.SetFocus()
            
            # Show modal (blocks until user clicks OK or presses ESC/ENTER)
            dlg.ShowModal()
            
            # Always destroy
            dlg.Destroy()
            
            # Log closure
            print("Statistics report closed")
            
            # Invoke callback (continue async chain)
            callback()
        
        # Defer entire dialog sequence
        wx.CallAfter(show_modal_and_callback)
    
    def show_statistics_report(
        self,
        stats: Dict[str, Any],
        final_score: Optional[Dict[str, Any]],
        is_victory: bool,
        deck_type: str
    ) -> None:
        """DEPRECATED: Use show_statistics_report_async() instead.
        
        Synchronous API maintained for backward compatibility.
        Creates nested event loop - avoid if possible.
        
        Will be removed in v3.0.
        """
        import warnings
        warnings.warn(
            "show_statistics_report() is deprecated, use show_statistics_report_async()",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Fallback: Call async version with empty callback
        self.show_statistics_report_async(
            stats, final_score, is_victory, deck_type,
            callback=lambda: None  # No-op callback
        )
