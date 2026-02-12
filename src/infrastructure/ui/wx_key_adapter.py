"""wxPython to pygame event adapter for keyboard input.

This module provides translation layer between wx.KeyEvent and pygame.event.Event,
enabling wxPython-based audiogame to use existing pygame-based game logic without
modification.

Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+, pygame 2.x (for event structure only)
Platform: Windows (primary), Linux (tested), macOS (untested)

Usage:
    >>> adapter = WxKeyEventAdapter()
    >>> # In wx event handler:
    >>> pygame_event = adapter.convert_to_pygame_event(wx_key_event)
    >>> gameplay_controller.handle_keyboard_events([pygame_event])
"""

import wx
import pygame
from typing import Dict, Optional


class WxKeyEventAdapter:
    """Adapter for translating wx.KeyEvent to pygame.event.Event.
    
    Provides bidirectional mapping between wxPython and pygame key codes,
    preserving modifier keys (SHIFT, CTRL, ALT) and creating pygame-compatible
    event objects that existing game logic can process unchanged.
    
    This adapter enables gradual migration from pygame to wxPython by allowing
    new wxPython event loop to feed events to existing pygame-based handlers.
    
    Attributes:
        wx_to_pygame_map: Dict mapping wx key codes to pygame key codes (80+ entries)
    
    Example:
        >>> adapter = WxKeyEventAdapter()
        >>> 
        >>> def on_key_event(wx_event: wx.KeyEvent):
        ...     # Convert wx event to pygame event
        ...     pygame_event = adapter.convert_to_pygame_event(wx_event)
        ...     
        ...     # Pass to existing pygame-based handler
        ...     gameplay_controller.handle_keyboard_events([pygame_event])
        >>> 
        >>> frame = SolitarioFrame(on_key_event=on_key_event)
    
    Note:
        This is a temporary adapter for migration phase. Once migration is complete,
        gameplay_controller.py can be refactored to use wx events directly.
    """
    
    def __init__(self):
        """Initialize adapter with complete key mapping."""
        self.wx_to_pygame_map = self._build_key_mapping()
    
    def _build_key_mapping(self) -> Dict[int, int]:
        """Build complete mapping from wx key codes to pygame key codes.
        
        Returns:
            Dict[int, int]: Mapping of wx.WXK_* constants to pygame.K_* constants
        
        Note:
            This mapping covers 80+ keys including:
            - Arrow keys (4)
            - Special keys (11)
            - Function keys (12)
            - Number row (10)
            - Letters A-Z (26)
            - Numpad keys (14)
            
            Total: 77+ explicit mappings
        """
        return {
            # === ARROW KEYS (4) ===
            wx.WXK_UP: pygame.K_UP,
            wx.WXK_DOWN: pygame.K_DOWN,
            wx.WXK_LEFT: pygame.K_LEFT,
            wx.WXK_RIGHT: pygame.K_RIGHT,
            
            # === SPECIAL KEYS (11) ===
            wx.WXK_RETURN: pygame.K_RETURN,
            wx.WXK_SPACE: pygame.K_SPACE,
            wx.WXK_ESCAPE: pygame.K_ESCAPE,
            wx.WXK_TAB: pygame.K_TAB,
            wx.WXK_BACK: pygame.K_BACKSPACE,
            wx.WXK_DELETE: pygame.K_DELETE,
            wx.WXK_HOME: pygame.K_HOME,
            wx.WXK_END: pygame.K_END,
            wx.WXK_PAGEUP: pygame.K_PAGEUP,
            wx.WXK_PAGEDOWN: pygame.K_PAGEDOWN,
            wx.WXK_INSERT: pygame.K_INSERT,
            
            # === FUNCTION KEYS (12) ===
            wx.WXK_F1: pygame.K_F1,
            wx.WXK_F2: pygame.K_F2,
            wx.WXK_F3: pygame.K_F3,
            wx.WXK_F4: pygame.K_F4,
            wx.WXK_F5: pygame.K_F5,
            wx.WXK_F6: pygame.K_F6,
            wx.WXK_F7: pygame.K_F7,
            wx.WXK_F8: pygame.K_F8,
            wx.WXK_F9: pygame.K_F9,
            wx.WXK_F10: pygame.K_F10,
            wx.WXK_F11: pygame.K_F11,
            wx.WXK_F12: pygame.K_F12,
            
            # === NUMBER ROW (10) ===
            ord('0'): pygame.K_0,
            ord('1'): pygame.K_1,
            ord('2'): pygame.K_2,
            ord('3'): pygame.K_3,
            ord('4'): pygame.K_4,
            ord('5'): pygame.K_5,
            ord('6'): pygame.K_6,
            ord('7'): pygame.K_7,
            ord('8'): pygame.K_8,
            ord('9'): pygame.K_9,
            
            # === LETTERS A-Z (26) ===
            # Note: ord('A') == 65, ord('Z') == 90
            # pygame.K_a == 97, pygame.K_z == 122
            # wxPython GetKeyCode() returns uppercase (65-90)
            # pygame constants are lowercase (97-122)
            ord('A'): pygame.K_a,
            ord('B'): pygame.K_b,
            ord('C'): pygame.K_c,
            ord('D'): pygame.K_d,
            ord('E'): pygame.K_e,
            ord('F'): pygame.K_f,
            ord('G'): pygame.K_g,
            ord('H'): pygame.K_h,
            ord('I'): pygame.K_i,
            ord('J'): pygame.K_j,
            ord('K'): pygame.K_k,
            ord('L'): pygame.K_l,
            ord('M'): pygame.K_m,
            ord('N'): pygame.K_n,
            ord('O'): pygame.K_o,
            ord('P'): pygame.K_p,
            ord('Q'): pygame.K_q,
            ord('R'): pygame.K_r,
            ord('S'): pygame.K_s,
            ord('T'): pygame.K_t,
            ord('U'): pygame.K_u,
            ord('V'): pygame.K_v,
            ord('W'): pygame.K_w,
            ord('X'): pygame.K_x,
            ord('Y'): pygame.K_y,
            ord('Z'): pygame.K_z,
            
            # === NUMPAD (14) ===
            wx.WXK_NUMPAD0: pygame.K_KP0,
            wx.WXK_NUMPAD1: pygame.K_KP1,
            wx.WXK_NUMPAD2: pygame.K_KP2,
            wx.WXK_NUMPAD3: pygame.K_KP3,
            wx.WXK_NUMPAD4: pygame.K_KP4,
            wx.WXK_NUMPAD5: pygame.K_KP5,
            wx.WXK_NUMPAD6: pygame.K_KP6,
            wx.WXK_NUMPAD7: pygame.K_KP7,
            wx.WXK_NUMPAD8: pygame.K_KP8,
            wx.WXK_NUMPAD9: pygame.K_KP9,
            wx.WXK_NUMPAD_ENTER: pygame.K_KP_ENTER,
            wx.WXK_NUMPAD_ADD: pygame.K_KP_PLUS,
            wx.WXK_NUMPAD_SUBTRACT: pygame.K_KP_MINUS,
            wx.WXK_NUMPAD_MULTIPLY: pygame.K_KP_MULTIPLY,
            wx.WXK_NUMPAD_DIVIDE: pygame.K_KP_DIVIDE,
            wx.WXK_NUMPAD_DECIMAL: pygame.K_KP_PERIOD,
        }
    
    def convert_to_pygame_event(self, wx_event: wx.KeyEvent) -> Optional[pygame.event.Event]:
        """Convert wx.KeyEvent to pygame.event.Event.
        
        Creates a pygame KEYDOWN event with translated key code and modifiers.
        If key code is not in mapping, returns None.
        
        Args:
            wx_event: wx.KeyEvent from keyboard input
        
        Returns:
            Optional[pygame.event.Event]: pygame KEYDOWN event, or None if unmapped key
        
        Example:
            >>> wx_event = ...  # from EVT_KEY_DOWN
            >>> pygame_event = adapter.convert_to_pygame_event(wx_event)
            >>> if pygame_event:
            ...     print(f"Pygame key: {pygame_event.key}")
            ...     print(f"Modifiers: {pygame_event.mod}")
        
        Note:
            The returned event is a pygame.event.Event with:
            - type = pygame.KEYDOWN
            - key = translated pygame key code
            - mod = translated modifier flags
            - unicode = character representation (if available)
        """
        # Get wx key code
        wx_key_code = wx_event.GetKeyCode()
        
        # Look up pygame equivalent
        pygame_key_code = self.wx_to_pygame_map.get(wx_key_code)
        
        if pygame_key_code is None:
            # Key not in mapping - could be unsupported key
            return None
        
        # Translate modifiers
        pygame_modifiers = self._get_pygame_modifiers(wx_event)
        
        # Get unicode character (if available)
        # Note: wx_event.GetUnicodeKey() is more reliable than chr(GetKeyCode())
        try:
            unicode_char = chr(wx_event.GetUnicodeKey())
        except (ValueError, AttributeError):
            unicode_char = ''
        
        # Create pygame event
        # Note: pygame.event.Event is a custom object with dynamic attributes
        pygame_event = pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame_key_code,
            mod=pygame_modifiers,
            unicode=unicode_char
        )
        
        return pygame_event
    
    def _get_pygame_modifiers(self, wx_event: wx.KeyEvent) -> int:
        """Extract modifier keys from wx.KeyEvent and translate to pygame format.
        
        Translates wx modifier methods to pygame.KMOD_* bitflags.
        
        Args:
            wx_event: wx.KeyEvent to extract modifiers from
        
        Returns:
            int: Bitmask of pygame.KMOD_* flags
        
        Pygame modifier constants:
            - pygame.KMOD_SHIFT (1): Either SHIFT key
            - pygame.KMOD_CTRL (64): Either CTRL key
            - pygame.KMOD_ALT (256): Either ALT key
            - pygame.KMOD_LSHIFT (1): Left SHIFT
            - pygame.KMOD_RSHIFT (2): Right SHIFT
            - pygame.KMOD_LCTRL (64): Left CTRL
            - pygame.KMOD_RCTRL (128): Right CTRL
            - pygame.KMOD_LALT (256): Left ALT
            - pygame.KMOD_RALT (512): Right ALT
        
        Note:
            wxPython doesn't distinguish left/right modifiers reliably,
            so we use the generic SHIFT/CTRL/ALT flags.
        """
        mods = 0
        
        # Check for SHIFT (either left or right)
        if wx_event.ShiftDown():
            mods |= pygame.KMOD_SHIFT  # Generic SHIFT flag
        
        # Check for CTRL (either left or right)
        if wx_event.ControlDown():
            mods |= pygame.KMOD_CTRL  # Generic CTRL flag
        
        # Check for ALT (either left or right)
        if wx_event.AltDown():
            mods |= pygame.KMOD_ALT  # Generic ALT flag
        
        # Note: pygame also has KMOD_META (1024) for Meta/Windows key,
        # but wxPython doesn't have reliable MetaDown() on all platforms
        # If needed in future: if wx_event.MetaDown(): mods |= pygame.KMOD_META
        
        return mods
    
    def get_key_name(self, wx_key_code: int) -> str:
        """Get human-readable name for wx key code.
        
        Useful for debugging and logging.
        
        Args:
            wx_key_code: wx key code (from GetKeyCode())
        
        Returns:
            str: Human-readable key name, or "UNKNOWN" if not mapped
        
        Example:
            >>> adapter.get_key_name(wx.WXK_ESCAPE)
            'ESCAPE'
            >>> adapter.get_key_name(ord('A'))
            'A'
            >>> adapter.get_key_name(wx.WXK_F5)
            'F5'
        """
        # Try to find in reverse mapping
        pygame_key = self.wx_to_pygame_map.get(wx_key_code)
        
        if pygame_key is None:
            return f"UNKNOWN({wx_key_code})"
        
        # Get pygame key name
        try:
            return pygame.key.name(pygame_key).upper()
        except:
            return f"KEY_{pygame_key}"


# Module-level documentation
__all__ = ['WxKeyEventAdapter']
