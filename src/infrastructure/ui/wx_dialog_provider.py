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
    
    Args (v1.6.2):
        parent: Optional pygame window handle to use as dialog parent.
                If provided, dialogs will be modal children (recommended).
                If None, dialogs are top-level windows (legacy fallback).
    
    Behavior:
        - With parent: Dialogs don't appear in ALT+TAB switcher
        - Without parent: Dialogs appear as separate windows (confusing UX)
    
    Example:
        >>> import pygame
        >>> screen = pygame.display.set_mode((800, 600))
        >>> provider = WxDialogProvider(parent=screen)  # RECOMMENDED
        >>> provider.show_alert("Hai vinto!", "Congratulazioni")
        # Dialog is child of pygame window, won't show in ALT+TAB
    """
    
    def __init__(self, parent=None):
        """Initialize dialog provider with native handle conversion.
        
        Args:
            parent: Optional parent window for modal dialogs.
                    Can be:
                    - None: Dialogs will be top-level (appear in ALT+TAB)
                    - int: Native window handle (HWND on Windows, XID on Linux)
                           Will be converted to wx.Window via AssociateHandle()
                    - wx.Window: Already a valid wxPython window (used as-is)
        
        Note (v1.6.3 FIX):
            When parent is an int (native handle from pygame), we create a wx.Window
            and associate it with the handle. This makes dialogs modal children,
            preventing ALT+TAB separation and crashes.
        """
        super().__init__()
        
        # 🆕 v1.6.3 BUG FIX: Convert native handle to wx.Window
        if parent is not None and isinstance(parent, int):
            # parent is a native window handle (HWND on Windows, XID on Linux)
            # Create empty wx.Window and associate with native handle
            import sys
            
            if sys.platform == "win32":
                # Windows: HWND handle
                self.parent = wx.Window()
                self.parent.AssociateHandle(parent)
            elif sys.platform.startswith("linux"):
                # Linux: X11 window ID (XID)
                self.parent = wx.Window()
                self.parent.AssociateHandle(parent)
            else:
                # Unsupported platform - fallback to None
                self.parent = None
        else:
            # parent is already wx.Window or None - use as-is
            self.parent = parent
    
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
            self.parent,  # Child of pygame window (prevents ALT+TAB separation)
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
            self.parent,  # Child of pygame window (prevents ALT+TAB separation)
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
            self.parent,  # Child of pygame window (prevents ALT+TAB separation)
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
            self.parent,  # Child of pygame window (prevents ALT+TAB separation)
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
