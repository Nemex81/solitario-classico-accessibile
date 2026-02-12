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
from typing import Optional, Dict, Any

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
    
    def __init__(self, parent=None):
        """Initialize with invisible wx.Frame parent (v1.6.3.2).
        
        Args:
            parent: IGNORED. Previous attempts used pygame HWND, but
                    AssociateHandle() doesn't establish modal relationships.
        
        Note:
            Creates invisible wx.Frame (lazy) as parent for all dialogs.
            Frame has wx.FRAME_NO_TASKBAR to prevent ALT+TAB appearance.
            Standard pattern for pygame+wxPython integration.
        """
        super().__init__()
        self._parent_frame = None  # Invisible wx.Frame (lazy init)
    
    def _get_parent(self):
        """Get invisible parent frame (lazy initialization).
        
        Returns:
            wx.Frame: Invisible frame for dialog parenting
        
        Note (v1.6.3.2):
            Creates invisible wx.Frame with wx.FRAME_NO_TASKBAR flag.
            This prevents the frame itself from appearing in ALT+TAB.
            All dialogs are created as children of this frame, which
            makes them modal and prevents ALT+TAB separation.
            
            Standard pattern for pygame+wxPython integration.
        """
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
        """Show modal alert with OK button.
        
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
        """Show modal Yes/No dialog.
        
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
        """Show modal text input dialog.
        
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
