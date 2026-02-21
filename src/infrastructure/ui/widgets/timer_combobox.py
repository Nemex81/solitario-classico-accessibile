"""TimerComboBox - Custom wx.ComboBox widget for timer duration selection.

This module provides a specialized ComboBox widget for selecting game timer duration
with preset values from 0 (disabled) to 60 minutes in 5-minute increments.

Version: v2.4.0
Pattern: Custom wx widget with domain-specific preset values
Clean Architecture Layer: Presentation/Widgets
Dependency: wxPython 4.1.x+

Features:
- 13 preset options: "0 minuti - Timer disattivato", "5 minuti", "10 minuti", ..., "60 minuti"
- Read-only ComboBox (prevents manual input)
- Helper methods: get_selected_minutes(), set_minutes(minutes)
- NVDA screen reader compatible (automatic wx support)
- Always enabled (no disabled state like previous CheckBox+ComboBox pattern)

Usage:
    >>> import wx
    >>> app = wx.App()
    >>> frame = wx.Frame(None)
    >>> timer_combo = TimerComboBox(frame)
    >>> timer_combo.set_minutes(15)  # Set to "15 minuti"
    >>> print(timer_combo.get_selected_minutes())  # Returns: 15
    >>> timer_combo.set_minutes(0)  # Set to "0 minuti - Timer disattivato"
    >>> print(timer_combo.get_selected_minutes())  # Returns: 0
"""

import wx
from typing import List


class TimerComboBox(wx.ComboBox):
    """Custom ComboBox for timer duration selection with preset values.
    
    Provides a ComboBox with 13 preset timer duration options:
    - "0 minuti - Timer disattivato" (timer disabled)
    - "5 minuti", "10 minuti", "15 minuti", ..., "60 minuti" (5-minute increments)
    
    Features:
    - Read-only (wx.CB_READONLY) - prevents manual text input
    - Always enabled (no Enable/Disable state management)
    - Domain-specific preset values for game timer
    - Helper methods for getting/setting values in minutes (int)
    - NVDA announces all preset options during navigation
    
    Note:
        This widget replaces the previous CheckBox+ComboBox pattern.
        The "0 minuti - Timer disattivato" option replaces the CheckBox
        functionality, simplifying the UI to a single widget.
    
    Example:
        >>> parent = wx.Frame(None)
        >>> timer_combo = TimerComboBox(parent)
        >>> timer_combo.set_minutes(30)  # Select "30 minuti"
        >>> minutes = timer_combo.get_selected_minutes()  # Returns 30
        >>> timer_combo.set_minutes(0)  # Select "0 minuti - Timer disattivato"
    """
    
    # Preset timer duration options (13 total: 0, 5, 10, 15, ..., 60)
    TIMER_PRESETS_MINUTES: List[int] = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        value: str = "",
        pos: tuple = wx.DefaultPosition,
        size: tuple = wx.DefaultSize,
        style: int = wx.CB_READONLY,
        name: str = "timerComboBox"
    ):
        """Initialize TimerComboBox with preset duration options.
        
        Args:
            parent: Parent window
            id: Widget ID (default: wx.ID_ANY)
            value: Initial value (default: "" - will be set to "0 minuti - Timer disattivato")
            pos: Widget position (default: wx.DefaultPosition)
            size: Widget size (default: wx.DefaultSize)
            style: Widget style (default: wx.CB_READONLY - prevents manual input)
            name: Widget name for wx identification (default: "timerComboBox")
        
        Note:
            If value is empty or invalid, defaults to "0 minuti - Timer disattivato".
            Style is forced to wx.CB_READONLY to prevent manual text input.
        """
        # Generate choices from presets
        choices = self._generate_choices()
        
        # Force read-only style (prevent manual input)
        style = style | wx.CB_READONLY
        
        # Initialize parent wx.ComboBox
        super().__init__(
            parent=parent,
            id=id,
            value=value if value else choices[0],  # Default to "0 minuti - Timer disattivato"
            pos=pos,
            size=size,
            choices=choices,
            style=style,
            name=name
        )
        
        # Set default selection to 0 minutes (disabled) if no value provided
        if not value:
            self.SetSelection(0)
    
    def _generate_choices(self) -> List[str]:
        """Generate ComboBox choices from preset minutes.
        
        Returns:
            List of formatted strings:
            - "0 minuti - Timer disattivato"
            - "5 minuti"
            - "10 minuti"
            - ...
            - "60 minuti"
        
        Note:
            Special formatting for 0 minutes to indicate timer disabled state.
        """
        choices = []
        for minutes in self.TIMER_PRESETS_MINUTES:
            if minutes == 0:
                choices.append("0 minuti - Timer disattivato")
            else:
                choices.append(f"{minutes} minuti")
        return choices
    
    def get_selected_minutes(self) -> int:
        """Get currently selected timer duration in minutes.
        
        Returns:
            int: Timer duration in minutes (0 = disabled, 5-60 = enabled)
        
        Example:
            >>> timer_combo.SetValue("15 minuti")
            >>> timer_combo.get_selected_minutes()
            15
            >>> timer_combo.SetValue("0 minuti - Timer disattivato")
            >>> timer_combo.get_selected_minutes()
            0
        
        Note:
            Parses the selected ComboBox value to extract the numeric minutes.
            Handles both "X minuti" and "0 minuti - Timer disattivato" formats.
        """
        selected_value = self.GetValue()
        
        # Handle "0 minuti - Timer disattivato" special case
        if selected_value.startswith("0 ") or "disattivato" in selected_value.lower():
            return 0
        
        # Parse "X minuti" format (e.g., "15 minuti" -> 15)
        try:
            minutes_str = selected_value.split()[0]  # Extract first token
            return int(minutes_str)
        except (ValueError, IndexError):
            # Fallback: if parsing fails, return 0 (disabled)
            return 0
    
    def set_minutes(self, minutes: int) -> None:
        """Set timer duration to specified minutes.
        
        Args:
            minutes: Timer duration in minutes. Must be one of TIMER_PRESETS_MINUTES.
                     If not in presets, rounds to nearest preset value.
        
        Example:
            >>> timer_combo.set_minutes(30)  # Select "30 minuti"
            >>> timer_combo.set_minutes(0)   # Select "0 minuti - Timer disattivato"
            >>> timer_combo.set_minutes(17)  # Rounds to 15 (nearest preset)
        
        Note:
            If minutes is not in TIMER_PRESETS_MINUTES, selects the nearest preset.
            Values < 2.5 round to 0, values >= 57.5 round to 60.
        """
        # If exact match in presets, use it
        if minutes in self.TIMER_PRESETS_MINUTES:
            target_minutes = minutes
        else:
            # Round to nearest preset
            target_minutes = self._round_to_nearest_preset(minutes)
        
        # Find the corresponding choice string
        if target_minutes == 0:
            target_value = "0 minuti - Timer disattivato"
        else:
            target_value = f"{target_minutes} minuti"
        
        # Set ComboBox value
        self.SetValue(target_value)
    
    def _round_to_nearest_preset(self, minutes: int) -> int:
        """Round minutes to nearest preset value.
        
        Args:
            minutes: Target minutes (any integer)
        
        Returns:
            int: Nearest preset value from TIMER_PRESETS_MINUTES
        
        Example:
            >>> self._round_to_nearest_preset(17)
            15
            >>> self._round_to_nearest_preset(23)
            25
            >>> self._round_to_nearest_preset(2)
            0
        """
        # Handle negative values
        if minutes < 0:
            return 0
        
        # Handle values above max preset
        if minutes > self.TIMER_PRESETS_MINUTES[-1]:
            return self.TIMER_PRESETS_MINUTES[-1]
        
        # Find nearest preset
        nearest = min(self.TIMER_PRESETS_MINUTES, key=lambda x: abs(x - minutes))
        return nearest
    
    def get_preset_count(self) -> int:
        """Get total number of preset options.
        
        Returns:
            int: Number of preset options (13 for current implementation)
        
        Example:
            >>> timer_combo.get_preset_count()
            13
        """
        return len(self.TIMER_PRESETS_MINUTES)
    
    def get_presets(self) -> List[int]:
        """Get list of all preset minutes values.
        
        Returns:
            List[int]: Copy of TIMER_PRESETS_MINUTES
        
        Example:
            >>> timer_combo.get_presets()
            [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        """
        return self.TIMER_PRESETS_MINUTES.copy()
