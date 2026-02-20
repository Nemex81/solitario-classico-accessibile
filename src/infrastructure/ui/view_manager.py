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

# Import game logger for panel transition tracking
from src.infrastructure.logging import game_logger as log

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
        """Initialize with container sizer reference.
        
        Args:
            parent_frame: Main application frame (must have panel_container)
        
        Raises:
            AttributeError: If frame doesn't have panel_container
            ValueError: If panel_container doesn't have sizer
        """
        self.parent_frame = parent_frame
        
        # ✅ FIX 2: Get panel container and sizer
        if not hasattr(parent_frame, 'panel_container'):
            raise AttributeError("Frame must have 'panel_container'")
        
        self.panel_container = parent_frame.panel_container
        self.container_sizer = self.panel_container.GetSizer()
        
        if self.container_sizer is None:
            raise ValueError("panel_container must have sizer")
        
        self.panels: Dict[str, wx.Panel] = {}
        self.current_panel_name: Optional[str] = None
        
        logger.debug(f"ViewManager initialized with sizer: {self.container_sizer}")
    
    def register_panel(self, name: str, panel: wx.Panel) -> None:
        """Register panel and add to container sizer.
        
        Stores panel instance and adds it to the container sizer layout tree.
        Panel should be created with panel_container as parent.
        
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
        
        # ✅ FIX 3: Add to container sizer
        # proportion=1: Takes all available space
        # wx.EXPAND: Expands to fill available space
        self.container_sizer.Add(panel, 1, wx.EXPAND)
        logger.debug(f"✓ Added panel '{name}' to sizer")
        
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
        
        Panel Swap Architecture (v2.1):
            This method should ALWAYS be called from deferred context when
            transitioning during event handlers:
            
            ✅ CORRECT: Deferred call from event handler
                def on_esc_pressed(self):
                    self.app.CallAfter(self._safe_return_to_menu)
                
                def _safe_return_to_menu(self):
                    self.view_manager.show_panel('menu')  # Safe!
            
            ❌ WRONG: Direct call from event handler
                def on_esc_pressed(self):
                    self.view_manager.show_panel('menu')  # Risky!
                    # May cause nested event loops or timing issues
        
        Hide/Show Synchronous Nature:
            wxPython Hide() and Show() are synchronous C++ operations that
            update internal state immediately. No event processing needed:
            - panel.Hide() → IsShown() immediately returns False
            - panel.Show() → IsShown() immediately returns True
            - NO wx.SafeYield() needed (was added in v2.0.3, removed in v2.0.8)
        
        Anti-Pattern Avoided:
            ❌ wx.SafeYield() was added in v2.0.3 based on mistaken belief
               of race condition with IsShown(). This caused:
               - RuntimeError: wxYield called recursively
               - Nested event loop crashes during deferred transitions
               - Removed in v2.0.8 - unnecessary and harmful
        
        Version History:
            v2.0.1: Initial ViewManager implementation
            v2.0.3: Added wx.SafeYield() (mistaken belief of race condition)
            v2.0.8: Removed wx.SafeYield() (causes nested event loop crash)
            v2.1: Architectural documentation and pattern validation
        """
        if name not in self.panels:
            # Log warning for panel not registered
            log.warning_issued("ViewManager", f"Panel '{name}' not registered")
            logger.error(f"Panel not registered: {name}")
            return None
        
        # Store previous view for logging
        prev_panel = self.current_panel_name
        
        # ============================================================================
        # NO wx.SafeYield() - Hide() and Show() are synchronous C++ operations!
        # ============================================================================
        # Rationale:
        #   - Hide() and Show() update wxWidgets internal state immediately
        #   - IsShown() reflects state without delay (no event processing needed)
        #   - SafeYield() creates nested event loop → RuntimeError when called
        #     from deferred callbacks (self.app.CallAfter context)
        #   - Removed in v2.0.8 after identifying as crash root cause
        #
        # Historical Context:
        #   v2.0.3: Added SafeYield (thought it prevented race condition)
        #   v2.0.8: Removed SafeYield (caused nested loop crashes)
        #   v2.1: Documented architectural pattern for maintainability
        # ============================================================================
        
        # Hide all panels (skip target to avoid redundant operations)
        for panel_name, panel in self.panels.items():
            if panel_name == name:
                continue  # Skip target panel - will be shown next
            
            # Check if panel is shown before hiding (avoid redundant Hide())
            if panel.IsShown():
                try:
                    panel.Hide()
                    logger.debug(f"Hidden panel: {panel_name}")
                except Exception as e:
                    logger.warning(f"Error hiding panel {panel_name}: {e}")
        
        # Show requested panel
        target_panel = self.panels[name]
        target_panel.Show()
        
        # ✅ FIX 5: Refresh layout (container + frame)
        parent = target_panel.GetParent()  # panel_container
        if parent:
            parent.Layout()  # Layout container
            parent.Refresh()  # Repaint
            
            # ✅ NEW: Also layout frame hierarchy
            frame = parent.GetParent()  # SolitarioFrame
            if frame:
                frame.Layout()  # Complete propagation
                logger.debug(f"✓ Laid out frame for panel: {name}")
        
        # Set focus to panel
        target_panel.SetFocus()
        
        # Log panel transition (BEFORE updating current_panel_name)
        log.panel_switched(prev_panel or "none", name)
        
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
