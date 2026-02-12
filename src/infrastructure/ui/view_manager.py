"""Panel Manager for single-frame panel-swap (wxPython standard pattern).

This module provides a manager for showing/hiding panels within a single
frame, implementing the standard wxPython panel-swap pattern.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> vm = ViewManager(parent_frame=main_frame)
    >>> menu_panel = MenuPanel(parent=main_frame.panel_container, controller=ctrl)
    >>> game_panel = GameplayPanel(parent=main_frame.panel_container, controller=ctrl)
    >>> vm.register_panel('menu', menu_panel)
    >>> vm.register_panel('gameplay', game_panel)
    >>> vm.show_panel('menu')      # Show menu, hide all others
    >>> vm.show_panel('gameplay')  # Show gameplay, hide menu
"""

import wx
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ViewManager:
    """Manager for single-frame panel-swap (wxPython standard pattern).
    
    Manages multiple panels within a single frame, showing/hiding them
    as needed. This is the standard wxPython pattern for multi-view
    applications within a single window.
    
    Features:
    - Dictionary-based panel registry
    - Show/hide panel transitions
    - Current panel tracking
    - Proper layout refresh on swap
    
    Attributes:
        parent_frame: Main application frame (for context)
        panels: Dictionary of registered panels {name: panel}
        current_panel_name: Name of currently visible panel
    
    Example:
        >>> # Setup
        >>> vm = ViewManager(main_frame)
        >>> menu = MenuPanel(parent=frame.panel_container, controller=ctrl)
        >>> game = GameplayPanel(parent=frame.panel_container, controller=ctrl)
        >>> vm.register_panel('menu', menu)
        >>> vm.register_panel('gameplay', game)
        >>> 
        >>> # Navigation
        >>> vm.show_panel('menu')     # Show menu, hide gameplay
        >>> vm.show_panel('gameplay') # Show gameplay, hide menu
        >>> current = vm.get_current_panel_name()  # 'gameplay'
    
    Note:
        Based on wxPython single-frame best practices. All panels must
        be children of the same parent container (typically frame.panel_container).
    """
    
    def __init__(self, parent_frame: wx.Frame):
        """Initialize ViewManager with parent frame reference.
        
        Args:
            parent_frame: Main application frame (for context)
        
        Note:
            Parent frame is stored for context but panels are created
            separately and passed to register_panel().
        """
        self.parent_frame = parent_frame
        self.panels: Dict[str, wx.Panel] = {}
        self.current_panel_name: Optional[str] = None
        
        logger.debug(f"ViewManager initialized with parent_frame: {parent_frame}")
    
    def register_panel(self, name: str, panel: wx.Panel) -> None:
        """Register a panel for show/hide management.
        
        Stores panel instance in registry for later show/hide operations.
        Panel should already be created and parented to frame.panel_container.
        
        Args:
            name: Unique identifier for this panel (e.g., 'menu', 'gameplay')
            panel: wx.Panel instance (must be child of frame.panel_container)
        
        Example:
            >>> menu_panel = MenuPanel(parent=frame.panel_container, controller=ctrl)
            >>> vm.register_panel('menu', menu_panel)
            >>> 
            >>> game_panel = GameplayPanel(parent=frame.panel_container, controller=ctrl)
            >>> vm.register_panel('gameplay', game_panel)
        
        Note:
            Panel is initially hidden after registration. Call show_panel()
            to make it visible.
        """
        if name in self.panels:
            logger.warning(f"Overwriting existing panel: {name}")
        
        self.panels[name] = panel
        panel.Hide()  # Initially hidden
        logger.debug(f"Registered panel: {name}")
    
    def show_panel(self, name: str) -> Optional[wx.Panel]:
        """Show specified panel, hide all others (panel swap).
        
        This is the core panel-swap operation: hides current panel,
        shows requested panel, and refreshes layout.
        
        Args:
            name: Name of registered panel to show
        
        Returns:
            Shown panel (wx.Panel), or None if panel name not registered
        
        Raises:
            KeyError: If panel name not registered (logged as error)
        
        Example:
            >>> vm.show_panel('menu')      # Show menu, hide others
            >>> vm.show_panel('gameplay')  # Show gameplay, hide menu
        
        Note:
            Uses Hide/Show/Layout pattern for smooth transitions.
            SetFocus() ensures keyboard input goes to correct panel.
        """
        if name not in self.panels:
            logger.error(f"Panel not registered: {name}")
            return None
        
        # Hide all panels
        for panel_name, panel in self.panels.items():
            if panel.IsShown():
                panel.Hide()
                logger.debug(f"Hidden panel: {panel_name}")
        
        # Show requested panel
        target_panel = self.panels[name]
        target_panel.Show()
        
        # Refresh layout
        parent = target_panel.GetParent()
        if parent:
            parent.Layout()
            parent.Refresh()
        
        # Set focus to panel
        target_panel.SetFocus()
        
        # Update current panel tracking
        self.current_panel_name = name
        
        logger.info(f"Showed panel: {name}")
        return target_panel
    
    def get_current_panel_name(self) -> Optional[str]:
        """Get name of currently visible panel.
        
        Returns:
            Current panel name (str), or None if no panel visible
        
        Example:
            >>> vm.show_panel('menu')
            >>> current = vm.get_current_panel_name()
            >>> print(current)  # 'menu'
        """
        return self.current_panel_name
    
    def get_current_view(self) -> Optional[str]:
        """Get name of currently visible panel (legacy compatibility).
        
        This method provides backward compatibility with the old ViewManager
        API that tracked views as frames. Now it simply returns the current
        panel name.
        
        Returns:
            Current panel name (str), or None if no panel visible
        
        Note:
            Alias for get_current_panel_name(). Kept for compatibility
            with existing code that checks current view state.
        """
        return self.current_panel_name
    
    def get_panel(self, name: str) -> Optional[wx.Panel]:
        """Get panel instance by name.
        
        Args:
            name: Name of registered panel
        
        Returns:
            Panel instance (wx.Panel), or None if not registered
        
        Example:
            >>> menu = vm.get_panel('menu')
            >>> if menu:
            ...     menu.update_score(100)
        """
        return self.panels.get(name)
    
    def __len__(self) -> int:
        """Return number of registered panels.
        
        Returns:
            Number of panels in registry
        
        Example:
            >>> vm.register_panel('menu', menu_panel)
            >>> vm.register_panel('game', game_panel)
            >>> assert len(vm) == 2
        """
        return len(self.panels)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        panel_names = list(self.panels.keys())
        return f"ViewManager(panel_count={len(self)}, panels={panel_names}, current={self.current_panel_name})"


# Module-level documentation
__all__ = ['ViewManager']
