"""
WindowController - Hierarchical Window Management with Lazy Initialization

Port from hs_deckmanager WinController with adaptations for solitaire app.

Provides centralized window management with:
- Lazy window creation (on-demand, not at startup)
- Parent stack for hierarchical navigation
- Automatic EVT_CLOSE binding for cleanup
- Window caching (create once, reuse)

Key Difference from ViewManager:
    ViewManager: Eager creation, panel-only, no parent tracking
    WindowController: Lazy creation, all windows, parent stack navigation

Version:
    v2.2.0: Ported from hs_deckmanager/src/views/wincontroller.py
"""

import wx
from typing import Optional, Dict, List, Any

from src.infrastructure.di.dependency_container import DependencyContainer
from src.infrastructure.ui.factories import ViewFactory, WindowKey


class WindowController:
    """Centralized window manager with parent stack and lazy initialization.
    
    Manages window lifecycle with hierarchical navigation support:
    - Lazy creation: Windows created on-demand, not at startup
    - Parent stack: Tracks navigation history for back/close operations
    - Caching: Windows created once and reused
    - Auto-cleanup: EVT_CLOSE bound automatically
    
    Navigation Pattern:
        1. create_window(key) - Create window (lazy), keep it hidden
        2. open_window(key) - Show window, hide current, push current to stack
        3. close_current_window() - Hide current, pop and show parent from stack
    
    Example:
        >>> # Setup
        >>> container = DependencyContainer()
        >>> win_ctrl = WindowController(container=container)
        >>> 
        >>> # Create windows (lazy, not shown yet)
        >>> win_ctrl.create_window(WindowKey.MENU_PANEL)
        >>> win_ctrl.create_window(WindowKey.GAMEPLAY_PANEL)
        >>> 
        >>> # Navigation: Menu → Gameplay
        >>> win_ctrl.open_window(WindowKey.MENU_PANEL)      # Shows menu
        >>> win_ctrl.open_window(WindowKey.GAMEPLAY_PANEL)  # Hides menu, shows gameplay
        >>> 
        >>> # Back: Gameplay → Menu
        >>> win_ctrl.close_current_window()  # Hides gameplay, restores menu
    
    Comparison with ViewManager:
        ViewManager (v2.1):
            - Eager creation (all panels created at startup)
            - Panel switching only (show_panel)
            - No parent tracking
            - Direct panel references
        
        WindowController (v2.2):
            - Lazy creation (windows created on-demand)
            - Hierarchical navigation (open/close with stack)
            - Parent stack tracking
            - Factory-based creation
    
    Version:
        v2.2.0: Ported from hs_deckmanager WinController
    """
    
    def __init__(self, container: DependencyContainer):
        """Initialize WindowController with dependency container.
        
        Args:
            container: DependencyContainer for dependency resolution
        
        Raises:
            ValueError: If container is None
        """
        if not container:
            raise ValueError("DependencyContainer required")
        
        self.container = container
        self.factory = ViewFactory(container=container)
        self.windows: Dict[WindowKey, wx.Window] = {}  # Cache: {key: window}
        self.current_window: Optional[wx.Window] = None  # Currently visible
        self.parent_stack: List[wx.Window] = []  # Stack for back navigation
    
    def get_current_window(self) -> Optional[wx.Window]:
        """Get currently visible window.
        
        Returns:
            Currently shown window, or None if no window visible
        
        Example:
            >>> current = win_ctrl.get_current_window()
            >>> if current:
            ...     print(f"Current: {current.__class__.__name__}")
        
        Version:
            v2.2.0: Initial implementation
        """
        return self.current_window
    
    def create_window(
        self,
        key: WindowKey,
        parent: Optional[wx.Window] = None,
        controller: Optional[Any] = None,
        **kwargs
    ) -> wx.Window:
        """Create window (lazy) without showing it.
        
        Creates window on-demand and caches it for reuse. If window already
        exists in cache, returns cached instance without recreation.
        
        Automatically binds EVT_CLOSE to close_current_window() for proper
        cleanup and navigation.
        
        Args:
            key: WindowKey identifying which window to create
            parent: Optional parent window (for wxPython hierarchy)
            controller: Optional controller instance (overrides container)
            **kwargs: Additional window-specific constructor parameters
        
        Returns:
            Window instance (newly created or from cache)
        
        Example:
            >>> # Create windows without showing them
            >>> menu = win_ctrl.create_window(WindowKey.MENU_PANEL)
            >>> gameplay = win_ctrl.create_window(
            ...     WindowKey.GAMEPLAY_PANEL,
            ...     controller=gameplay_controller
            ... )
            >>> 
            >>> # Second call returns cached instance
            >>> menu2 = win_ctrl.create_window(WindowKey.MENU_PANEL)
            >>> assert menu is menu2  # Same instance
        
        Version:
            v2.2.0: Initial implementation
        """
        # Return cached if already created
        if key in self.windows:
            return self.windows[key]
        
        # Create via factory
        window = self.factory.create_window(
            key=key,
            parent=parent,
            controller=controller,
            **kwargs
        )
        
        # Bind close event to close_current_window()
        window.Bind(wx.EVT_CLOSE, lambda e: self.close_current_window())
        
        # Cache window
        self.windows[key] = window
        
        return window
    
    def open_window(self, key: WindowKey, parent: Optional[wx.Window] = None) -> None:
        """Open window, hide current, push current to parent stack.
        
        Shows the specified window and hides the currently visible window.
        The current window is pushed to the parent stack so it can be
        restored later via close_current_window().
        
        This implements forward navigation in a hierarchical UI:
            Menu → Options: open_window(OPTIONS)
            Options → Stats: open_window(STATS)
        
        Args:
            key: WindowKey of window to open
            parent: Optional parent window (for wxPython hierarchy)
        
        Raises:
            ValueError: If window not created yet (must call create_window first)
        
        Example:
            >>> # Must create before opening
            >>> win_ctrl.create_window(WindowKey.MENU_PANEL)
            >>> win_ctrl.create_window(WindowKey.GAMEPLAY_PANEL)
            >>> 
            >>> # Navigation
            >>> win_ctrl.open_window(WindowKey.MENU_PANEL)      # Shows menu
            >>> win_ctrl.open_window(WindowKey.GAMEPLAY_PANEL)  # Menu→Gameplay
            >>> # Now menu is hidden and in parent_stack
        
        Version:
            v2.2.0: Initial implementation
        """
        if key not in self.windows:
            raise ValueError(
                f"Window {key} not created yet. "
                f"Call create_window({key}) first."
            )
        
        # Hide current window and push to parent stack
        if self.current_window:
            self.current_window.Hide()
            self.parent_stack.append(self.current_window)
        
        # Show new window
        self.current_window = self.windows[key]
        self.current_window.Show()
        
        # Set parent if provided
        if parent:
            self.current_window.SetParent(parent)
    
    def close_current_window(self) -> None:
        """Close current window, restore parent from stack.
        
        Hides the currently visible window and restores the previous window
        from the parent stack. This implements back navigation:
            Stats → Options: close_current_window()
            Options → Menu: close_current_window()
        
        If parent stack is empty, current_window is set to None (no window shown).
        
        This method is automatically called when user clicks window close button
        (EVT_CLOSE bound in create_window).
        
        Returns:
            None
        
        Example:
            >>> # Forward navigation
            >>> win_ctrl.open_window(WindowKey.MENU_PANEL)      # Current: Menu
            >>> win_ctrl.open_window(WindowKey.GAMEPLAY_PANEL)  # Current: Gameplay
            >>> 
            >>> # Back navigation
            >>> win_ctrl.close_current_window()  # Current: Menu (restored from stack)
            >>> win_ctrl.close_current_window()  # Current: None (stack empty)
        
        Version:
            v2.2.0: Initial implementation
        """
        if not self.current_window:
            return
        
        # Hide current
        self.current_window.Hide()
        
        # Restore parent from stack
        if self.parent_stack:
            self.current_window = self.parent_stack.pop()
            self.current_window.Show()
        else:
            # No parent, clear current (no window shown)
            self.current_window = None
