"""
WidgetFactory - Factory for Common Widget Creation

Simplified version from hs_deckmanager adapted for solitaire's audio-first UI.

Provides consistent widget creation with:
- Accessibility-focused (screen reader labels)
- Standard button styling
- Layout helper methods
- Minimal visual styling (default wx appearance)

Future Enhancements:
    - Dark mode support via ColorManager
    - Custom fonts for better readability
    - Focus indicators for keyboard navigation

Version:
    v2.2.0: Created from hs_deckmanager pattern (simplified)
"""

import wx
from typing import Optional, Callable, Tuple

from src.infrastructure.di.dependency_container import DependencyContainer


class WidgetFactory:
    """Factory for creating common widgets with consistent styling.
    
    Simplified from hs_deckmanager focusing on solitaire's needs:
    - Audio-first interface (screen reader friendly)
    - Minimal visual styling (default wx appearance)
    - Standard button and layout helpers
    
    Note:
        This is a simplified version. hs_deckmanager includes ColorManager
        for theme support, which may be added in future versions for
        dark mode and visual customization.
    
    Example:
        >>> container = DependencyContainer()
        >>> factory = WidgetFactory(container=container)
        >>> button = factory.create_button(
        ...     parent=panel,
        ...     label="Start Game",
        ...     event_handler=on_start_click
        ... )
        >>> sizer = factory.create_sizer(wx.VERTICAL)
        >>> factory.add_to_sizer(sizer, button, proportion=0, flag=wx.CENTER)
    
    Version:
        v2.2.0: Initial implementation (simplified from hs_deckmanager)
    """
    
    def __init__(self, container: DependencyContainer):
        """Initialize WidgetFactory with dependency container.
        
        Args:
            container: DependencyContainer instance (for future DI needs)
        """
        self.container = container
    
    def create_button(
        self,
        parent: wx.Window,
        label: str,
        size: Tuple[int, int] = (180, 70),
        font_size: int = 16,
        event_handler: Optional[Callable] = None
    ) -> wx.Button:
        """Create button with consistent styling and accessibility.
        
        Creates a button with:
        - Bold font for better readability
        - Standard size for touch/keyboard use
        - Optional event handler binding
        - Screen reader friendly label
        
        Args:
            parent: Parent window for button
            label: Button text (also used by screen readers)
            size: Tuple (width, height) in pixels. Default: (180, 70)
            font_size: Font size in points. Default: 16
            event_handler: Optional click handler function
        
        Returns:
            Configured wx.Button instance
        
        Example:
            >>> def on_click(event):
            ...     print("Button clicked")
            >>> button = factory.create_button(
            ...     parent=panel,
            ...     label="New Game",
            ...     event_handler=on_click
            ... )
        
        Version:
            v2.2.0: Initial implementation
        """
        button = wx.Button(parent, label=label, size=size)
        button.SetFont(wx.Font(font_size, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        
        if event_handler:
            button.Bind(wx.EVT_BUTTON, event_handler)
        
        return button
    
    def create_sizer(self, orientation: int = wx.VERTICAL) -> wx.BoxSizer:
        """Create sizer for layout management.
        
        BoxSizer is wxPython's primary layout manager. Use orientation
        to control whether widgets stack vertically or horizontally.
        
        Args:
            orientation: wx.VERTICAL (default) or wx.HORIZONTAL
        
        Returns:
            wx.BoxSizer instance
        
        Example:
            >>> # Vertical layout (stack widgets top to bottom)
            >>> v_sizer = factory.create_sizer(wx.VERTICAL)
            >>> 
            >>> # Horizontal layout (stack widgets left to right)
            >>> h_sizer = factory.create_sizer(wx.HORIZONTAL)
        
        Version:
            v2.2.0: Initial implementation
        """
        return wx.BoxSizer(orientation)
    
    def add_to_sizer(
        self,
        sizer: wx.Sizer,
        element: wx.Window,
        proportion: int = 0,
        flag: int = wx.ALL,
        border: int = 10
    ) -> None:
        """Add element to sizer with default spacing parameters.
        
        Helper method to simplify adding widgets to sizers with consistent
        spacing and alignment.
        
        Args:
            sizer: Target sizer to add element to
            element: Widget to add (wx.Window subclass)
            proportion: Stretch factor (0 = fixed size, >0 = proportional)
            flag: Alignment and border flags (wx.ALL, wx.CENTER, etc.)
            border: Border size in pixels. Default: 10
        
        Returns:
            None (modifies sizer in place)
        
        Example:
            >>> sizer = factory.create_sizer(wx.VERTICAL)
            >>> button = factory.create_button(panel, "Click Me")
            >>> 
            >>> # Add with default spacing
            >>> factory.add_to_sizer(sizer, button)
            >>> 
            >>> # Add with custom alignment
            >>> factory.add_to_sizer(
            ...     sizer, button,
            ...     proportion=0,
            ...     flag=wx.CENTER | wx.ALL,
            ...     border=20
            ... )
        
        Version:
            v2.2.0: Initial implementation
        """
        sizer.Add(element, proportion=proportion, flag=flag, border=border)
