"""
ViewFactory - Factory for Window and Panel Creation

Port from hs_deckmanager with simplifications for solitaire app.

Provides centralized window/panel creation with:
- Dependency injection via DependencyContainer
- Window registry via WindowKey enum
- Lazy initialization support
- Auto-resolution of dependencies from container

Version:
    v2.2.0: Ported from hs_deckmanager/src/views/builder/view_factory.py
"""

from enum import Enum
from typing import Optional, Any, Dict, Type
import wx

from src.infrastructure.di.dependency_container import DependencyContainer

# Import window classes
from src.infrastructure.ui.wx_frame import SolitarioFrame
from src.infrastructure.ui.menu_panel import MenuPanel
from src.infrastructure.ui.gameplay_panel import GameplayPanel
from src.infrastructure.ui.options_dialog import OptionsDialog


class WindowKey(Enum):
    """Unique identifiers for registered windows.
    
    Each key maps to a specific window/panel class in ALL_WINDOWS registry.
    """
    MAIN_FRAME = "main_frame"           # SolitarioFrame (main window)
    MENU_PANEL = "menu_panel"           # MenuPanel
    GAMEPLAY_PANEL = "gameplay_panel"   # GameplayPanel
    OPTIONS_DIALOG = "options_dialog"   # OptionsDialog
    # Future extensions: STATISTICS_WINDOW, HELP_WINDOW, etc.


# Window Registry - Maps keys to window classes
ALL_WINDOWS: Dict[WindowKey, Type] = {
    WindowKey.MAIN_FRAME: SolitarioFrame,
    WindowKey.MENU_PANEL: MenuPanel,
    WindowKey.GAMEPLAY_PANEL: GameplayPanel,
    WindowKey.OPTIONS_DIALOG: OptionsDialog,
}


class ViewFactory:
    """Factory for creating windows and panels with dependency injection.
    
    Centralizes window creation logic and integrates with DependencyContainer
    for automatic dependency resolution.
    
    Features:
        - Registry-based window creation via WindowKey enum
        - Automatic dependency resolution from container
        - Support for custom constructor kwargs
        - Type-safe window creation
    
    Example:
        >>> container = DependencyContainer()
        >>> factory = ViewFactory(container=container)
        >>> frame = factory.create_window(WindowKey.MAIN_FRAME, parent=None)
        >>> menu = factory.create_window(WindowKey.MENU_PANEL, parent=frame)
    
    Version:
        v2.2.0: Created from hs_deckmanager pattern
    """
    
    def __init__(self, container: DependencyContainer):
        """Initialize ViewFactory with dependency container.
        
        Args:
            container: DependencyContainer instance for resolving dependencies
        """
        self.container = container
    
    def create_window(
        self,
        key: WindowKey,
        parent: Optional[wx.Window] = None,
        **kwargs: Any
    ) -> wx.Window:
        """Create a window/panel by key with automatic dependency resolution.
        
        This method:
        1. Looks up window class from ALL_WINDOWS registry
        2. Resolves any controller dependencies from container (if registered)
        3. Instantiates window with parent + resolved deps + custom kwargs
        4. Returns fully initialized window instance
        
        Args:
            key: WindowKey identifying which window to create
            parent: Optional parent window (for wxPython hierarchy)
            **kwargs: Additional constructor arguments (override defaults)
        
        Returns:
            Newly created wx.Window instance
        
        Raises:
            KeyError: If window key not registered in ALL_WINDOWS
            KeyError: If required dependency not registered in container
        
        Example:
            >>> # Create frame (no controller needed)
            >>> frame = factory.create_window(WindowKey.MAIN_FRAME)
            >>> 
            >>> # Create panel with controller from container
            >>> menu = factory.create_window(
            ...     WindowKey.MENU_PANEL,
            ...     parent=frame,
            ...     container=container  # Pass container if panel needs it
            ... )
        
        Version:
            v2.2.0: Initial implementation
        """
        if key not in ALL_WINDOWS:
            raise KeyError(f"Window key not registered: {key}")
        
        window_class = ALL_WINDOWS[key]
        
        # Build constructor arguments
        # Start with parent (if provided)
        constructor_args = {}
        if parent is not None:
            constructor_args['parent'] = parent
        
        # Auto-resolve controller from container if registered
        # Convention: controller key = "{window_key}_controller"
        controller_key = f"{key.value}_controller"
        if self.container.has(controller_key):
            controller = self.container.resolve(controller_key)
            constructor_args['controller'] = controller
        
        # Merge with custom kwargs (custom kwargs override defaults)
        constructor_args.update(kwargs)
        
        # Instantiate window
        window = window_class(**constructor_args)
        
        return window
