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
from typing import Optional

from src.infrastructure.ui.dialog_provider import DialogProvider


class WxDialogProvider(DialogProvider):
    """wxPython implementation of DialogProvider.
    
    Creates wx.App() instance on-demand for each dialog (legacy pattern).
    This approach works because pygame manages the main event loop,
    and wxPython dialogs run in modal mode (blocking).
    
    Example:
        >>> provider = WxDialogProvider()
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog appears, blocks execution until user clicks OK
        >>> print("Dialog closed")
    """
    
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
            None,  # No parent window (top-level)
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
            None,
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
            None,
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
