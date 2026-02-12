"""View Manager for multi-window stack management (hs_deckmanager pattern).

This module provides a stack-based window manager for navigating between
multiple views (menu, gameplay, options) with proper show/hide transitions.

Pattern: hs_deckmanager ViewManager
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> vm = ViewManager(parent_frame=main_frame)
    >>> vm.register_view('menu', lambda parent: MenuView(parent, controller))
    >>> vm.register_view('gameplay', lambda parent: GameplayView(parent, controller))
    >>> 
    >>> vm.push_view('menu')      # Show menu
    >>> vm.push_view('gameplay')  # Show gameplay, hide menu
    >>> vm.pop_view()             # Close gameplay, restore menu
"""

import wx
import logging
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)


class ViewManager:
    """Stack-based manager for multiple wxPython views (hs_deckmanager pattern).
    
    Manages LIFO (Last-In-First-Out) stack of views with automatic show/hide
    transitions. When a new view is pushed, the previous view is hidden but
    kept alive. When current view is popped, previous view is restored.
    
    This pattern enables clean navigation: menu → gameplay → options → gameplay → menu
    
    Features:
    - Factory pattern for view construction (register_view)
    - LIFO stack for view history
    - Automatic show/hide on push/pop
    - Parent frame reference for dialog coordination
    - Proper cleanup on pop (Destroy + wx.Yield)
    
    Attributes:
        parent_frame: Main application frame (for dialog parenting)
        views_stack: LIFO stack of active views
        view_constructors: Registry of view factory functions
    
    Example:
        >>> # Setup
        >>> vm = ViewManager(main_frame)
        >>> vm.register_view('menu', lambda p: MenuView(p, ctrl))
        >>> vm.register_view('game', lambda p: GameView(p, ctrl))
        >>> 
        >>> # Navigation
        >>> vm.push_view('menu')     # Stack: [menu]
        >>> vm.push_view('game')     # Stack: [menu (hidden), game (shown)]
        >>> vm.pop_view()            # Stack: [menu (shown)]
        >>> print(len(vm))           # Output: 1
    
    Note:
        Based on hs_deckmanager ViewManager pattern. Each view must be a
        wx.Frame or wx.Frame subclass.
    """
    
    def __init__(self, parent_frame: wx.Frame):
        """Initialize ViewManager with parent frame reference.
        
        Args:
            parent_frame: Main application frame (used for dialog parenting)
        
        Note:
            Parent frame is not directly used for view parenting (views are
            created with parent=None for independence), but stored for future
            dialog coordination if needed.
        """
        self.parent_frame = parent_frame
        self.views_stack: List[wx.Frame] = []
        self.view_constructors: Dict[str, Callable[[wx.Frame], wx.Frame]] = {}
        
        logger.debug(f"ViewManager initialized with parent_frame: {parent_frame}")
    
    def register_view(self, name: str, constructor: Callable[[wx.Frame], wx.Frame]) -> None:
        """Register a view constructor (factory pattern).
        
        Stores a factory function that creates a view when needed.
        The constructor receives parent frame as argument.
        
        Args:
            name: Unique identifier for this view type (e.g., 'menu', 'gameplay')
            constructor: Factory function that creates the view
                         Signature: (parent: wx.Frame) -> wx.Frame
        
        Example:
            >>> def create_menu(parent):
            ...     return MenuView(parent, controller=my_ctrl)
            >>> 
            >>> vm.register_view('menu', create_menu)
            >>> # Or with lambda:
            >>> vm.register_view('game', lambda p: GameView(p, my_ctrl))
        
        Note:
            Constructor should accept parent frame but may create view with
            parent=None for independence (hs_deckmanager pattern).
        """
        if name in self.view_constructors:
            logger.warning(f"Overwriting existing view constructor: {name}")
        
        self.view_constructors[name] = constructor
        logger.debug(f"Registered view constructor: {name}")
    
    def push_view(self, name: str, **kwargs) -> Optional[wx.Frame]:
        """Create and show new view, hide previous view (LIFO push).
        
        Creates a new view using registered constructor, hides current view
        (if any), and pushes new view onto stack.
        
        Args:
            name: Name of registered view to create
            **kwargs: Additional arguments passed to constructor (future use)
        
        Returns:
            Created view (wx.Frame), or None if view name not registered
        
        Raises:
            KeyError: If view name not registered (logged as error)
        
        Example:
            >>> vm.push_view('menu')      # Stack: [menu]
            >>> vm.push_view('gameplay')  # Stack: [menu (hidden), gameplay (shown)]
        
        Note:
            Previous view is hidden but NOT destroyed. Call pop_view() to
            destroy current view and restore previous one.
        """
        if name not in self.view_constructors:
            logger.error(f"View constructor not registered: {name}")
            return None
        
        # Hide current view if exists
        if self.views_stack:
            current_view = self.views_stack[-1]
            current_view.Hide()
            logger.debug(f"Hidden current view: {current_view.GetTitle()}")
        
        # Create new view using factory
        constructor = self.view_constructors[name]
        new_view = constructor(self.parent_frame)
        
        # Show new view
        new_view.Show()
        new_view.Raise()  # Bring to front
        new_view.SetFocus()
        
        # Push onto stack
        self.views_stack.append(new_view)
        
        logger.info(f"Pushed view '{name}' (stack depth: {len(self.views_stack)})")
        return new_view
    
    def pop_view(self) -> bool:
        """Close current view and restore previous view (LIFO pop).
        
        Destroys the current view (top of stack) and shows the previous view.
        If stack becomes empty after pop, returns False (no views remaining).
        
        Returns:
            True if view was popped and previous restored, False if stack empty
        
        Example:
            >>> vm.push_view('menu')
            >>> vm.push_view('gameplay')
            >>> vm.pop_view()  # Destroys gameplay, shows menu
            True
            >>> vm.pop_view()  # Destroys menu
            True
            >>> vm.pop_view()  # Stack empty
            False
        
        Note:
            Uses Destroy() + wx.Yield() pattern for proper cleanup.
            Previous view is automatically shown and focused.
        """
        if not self.views_stack:
            logger.warning("Cannot pop view: stack is empty")
            return False
        
        # Pop current view
        current_view = self.views_stack.pop()
        current_title = current_view.GetTitle()
        
        # Destroy current view
        current_view.Destroy()
        wx.Yield()  # Process pending events (cleanup)
        
        logger.info(f"Popped view '{current_title}' (stack depth: {len(self.views_stack)})")
        
        # Restore previous view if exists
        if self.views_stack:
            previous_view = self.views_stack[-1]
            previous_view.Show()
            previous_view.Raise()
            previous_view.SetFocus()
            logger.debug(f"Restored previous view: {previous_view.GetTitle()}")
        
        return True
    
    def get_current_view(self) -> Optional[wx.Frame]:
        """Get currently visible view (top of stack).
        
        Returns:
            Current view (wx.Frame), or None if stack is empty
        
        Example:
            >>> vm.push_view('menu')
            >>> current = vm.get_current_view()
            >>> print(current.GetTitle())
            'Menu Principal'
        """
        if self.views_stack:
            return self.views_stack[-1]
        return None
    
    def clear_stack(self) -> None:
        """Destroy all views and clear stack.
        
        Useful for cleanup or restart scenarios. Destroys all views in
        reverse order (top to bottom) and clears the stack.
        
        Example:
            >>> vm.clear_stack()  # All views destroyed
            >>> assert len(vm) == 0
        
        Note:
            Uses pop_view() internally for proper cleanup.
        """
        while self.views_stack:
            self.pop_view()
        
        logger.info("Stack cleared")
    
    def __len__(self) -> int:
        """Return current stack depth.
        
        Returns:
            Number of views currently on stack
        
        Example:
            >>> vm.push_view('menu')
            >>> vm.push_view('game')
            >>> assert len(vm) == 2
        """
        return len(self.views_stack)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        view_titles = [v.GetTitle() for v in self.views_stack]
        return f"ViewManager(stack_depth={len(self)}, views={view_titles})"


# Module-level documentation
__all__ = ['ViewManager']
