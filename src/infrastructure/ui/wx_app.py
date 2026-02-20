"""wxPython application wrapper for Solitario audiogame.

This module provides the main wx.App wrapper that manages the wxPython
application lifecycle. Replaces pygame event loop with wx.MainLoop().

Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> app = SolitarioWxApp(on_init_complete=lambda app: setup_game(app))
    >>> app.MainLoop()  # Start wx event loop
"""

import wx
from typing import Optional, Callable


class SolitarioWxApp(wx.App):
    """wxPython application wrapper for audiogame interface.
    
    Manages wx.App lifecycle and provides post-initialization callback
    for setting up game components after wxPython is ready.
    
    This class follows the wxPython pattern where OnInit() is called
    automatically after __init__(), allowing proper initialization order:
    1. wx.App.__init__() - wxPython framework setup
    2. OnInit() - Application-specific setup
    3. on_init_complete callback - Game component setup
    4. MainLoop() - Event loop start
    
    Attributes:
        on_init_complete: Optional callback function called after OnInit()
            Signature: callback(app: SolitarioWxApp) -> None
    
    Example:
        >>> def setup_game(app):
        ...     # Create frame, menu, controllers
        ...     app.frame = SolitarioFrame(...)
        ...     app.menu = WxVirtualMenu(...)
        >>> 
        >>> app = SolitarioWxApp(on_init_complete=setup_game)
        >>> app.MainLoop()  # Blocks until app closes
    
    Note:
        This is a minimal wrapper. The frame, menu, and game logic
        are set up via the callback to maintain separation of concerns.
    """
    
    def __init__(
        self, 
        on_init_complete: Optional[Callable[['SolitarioWxApp'], None]] = None,
        redirect: bool = False,  # No stdout redirection for audiogame
        filename: Optional[str] = None,
        useBestVisual: bool = False,
        clearSigInt: bool = True
    ):
        """Initialize wxPython application.
        
        Args:
            on_init_complete: Optional callback invoked after OnInit().
                Receives self (SolitarioWxApp) as argument.
            redirect: If True, redirect stdout/stderr to wx window (default False)
            filename: If redirect=True, log to this file
            useBestVisual: Try to use best visual mode (default False)
            clearSigInt: Clear SIGINT handler for CTRL+C handling (default True)
        
        Note:
            OnInit() is called automatically by wx.App after __init__()
        """
        self.on_init_complete = on_init_complete
        
        # Call parent __init__ - this triggers OnInit() internally
        super().__init__(
            redirect=redirect,
            filename=filename,
            useBestVisual=useBestVisual,
            clearSigInt=clearSigInt
        )
    
    def OnInit(self) -> bool:
        """wxPython initialization callback.
        
        Called automatically by wx.App after __init__().
        Invokes on_init_complete callback if provided.
        
        Returns:
            bool: True to continue app initialization, False to abort
        
        Note:
            This method is called by wxPython framework, not user code.
            Override this to add application-specific initialization.
        """
        # Call user-provided callback if present
        if self.on_init_complete is not None:
            self.on_init_complete(self)
        
        # Return True to indicate successful initialization
        return True
    
    def OnExit(self) -> int:
        """Cleanup callback when app is exiting.
        
        Called automatically by wx.App during shutdown.
        Override to add cleanup logic (e.g., save settings, close resources).
        
        Returns:
            int: Exit code (0 for success)
        """
        # Default implementation - no cleanup needed
        return 0


def create_app(on_init_complete: Optional[Callable[[SolitarioWxApp], None]] = None) -> SolitarioWxApp:
    """Factory function to create SolitarioWxApp instance.
    
    Convenience function for creating the app with proper configuration.
    
    Args:
        on_init_complete: Optional callback for post-init setup
    
    Returns:
        SolitarioWxApp: Configured application instance (not yet started)
    
    Example:
        >>> def setup(app):
        ...     print("App initialized!")
        >>> 
        >>> app = create_app(on_init_complete=setup)
        >>> app.MainLoop()  # Start event loop
    """
    return SolitarioWxApp(
        on_init_complete=on_init_complete,
        redirect=False,  # No stdout redirect for audiogame
        clearSigInt=True  # Allow CTRL+C handling
    )


# Module-level documentation
__all__ = ['SolitarioWxApp', 'create_app']
