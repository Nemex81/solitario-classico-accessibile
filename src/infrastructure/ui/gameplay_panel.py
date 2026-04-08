"""GameplayPanel - Dual-mode gameplay panel (audio-only / visual).

Supports two rendering modes:
  audio_only (default):  No visual rendering.  All interaction via TTS/NVDA.
  visual:                Renders cards using CardRenderer + BoardLayoutManager
                         on every board-state change.  NVDA also works because
                         an off-screen wx.StaticText is updated with descriptive
                         text after each move.

F3 toggles between the two modes during gameplay.

Pattern: Single-frame panel-swap (wxPython standard)
Clean Architecture Layer: Infrastructure/UI
Dependency: wxPython 4.1.x+
Platform: Windows (primary), Linux (tested), macOS (untested)
"""

from __future__ import annotations

import logging

import wx

from src.application.board_state import BoardState
from src.infrastructure.ui.board_layout_manager import BoardLayoutManager
from src.infrastructure.ui.card_image_cache import CardImageCache
from src.infrastructure.ui.card_renderer import CardRenderer
from src.infrastructure.ui.visual_theme import ThemeProperties, get_theme

from .basic_panel import BasicPanel

_log = logging.getLogger(__name__)

_DISPLAY_AUDIO = "audio_only"
_DISPLAY_VISUAL = "visual"
_BLINK_MS = 500


class GameplayPanel(BasicPanel):
    """Dual-mode gameplay panel.

    Supports ``audio_only`` (default) and ``visual`` rendering modes.
    Toggle with F3 during gameplay.

    In *visual* mode:
    - EVT_PAINT redraws the full board on every board-state change.
    - A blink timer (500 ms) toggles the cursor highlight.
    - An off-screen ``wx.StaticText`` (_nvda_info_zone) is updated with a text
      description so NVDA reads the current board position.

    In *audio_only* mode:
    - EVT_PAINT is a no-op (the panel background suffices).
    - The blink timer is stopped.
    - All TTS behaviour is unchanged.
    """

    def __init__(
        self,
        parent: wx.Window,
        controller: object,
        container: object | None = None,
        display_mode: str = _DISPLAY_AUDIO,
        theme_name: str = "standard",
        **kwargs: object,
    ) -> None:
        self.container = container
        self._display_mode: str = display_mode
        self._board_state: BoardState | None = None
        self._card_renderer: CardRenderer = CardRenderer()
        self._layout_manager: BoardLayoutManager = BoardLayoutManager()
        self._current_theme: ThemeProperties = get_theme(theme_name)
        self._image_cache: CardImageCache | None = None
        self._cursor_blink_on: bool = True
        self._blink_timer: wx.Timer | None = None
        self._nvda_info_zone: wx.StaticText | None = None

        super().__init__(parent=parent, controller=controller, **kwargs)

        # Bind extra events
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

        # Setup blink timer
        self._blink_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_blink_timer, self._blink_timer)
        if self._display_mode == _DISPLAY_VISUAL:
            self._blink_timer.Start(_BLINK_MS)

        # Register board observer
        self._try_register_observer()
    
    def _try_register_observer(self) -> None:
        """Register the board-state observer on the gameplay controller, if available."""
        try:
            gc = getattr(self.controller, "gameplay_controller", None)
            if gc is not None and hasattr(gc, "set_on_board_changed"):
                gc.set_on_board_changed(self._on_board_changed)
        except Exception:  # pragma: no cover
            _log.debug("Cannot register board observer — controller not ready yet")

    def _get_image_cache(self) -> CardImageCache:
        """Lazy-initialize the card image cache.

        The assets path is resolved relative to this module's location so the
        cache works regardless of the current working directory.

        Returns:
            Shared CardImageCache instance for this panel.
        """
        if self._image_cache is None:
            import pathlib
            assets = pathlib.Path(__file__).parent.parent.parent.parent / "assets" / "img"
            self._image_cache = CardImageCache(assets)
        return self._image_cache

    def init_ui_elements(self) -> None:
        """Create UI elements for both modes.

        For *audio_only* mode a simple label is shown.
        For *visual* mode the label is hidden and the panel surface is used
        directly as a canvas.

        The off-screen NVDA info zone is always created so that it can be
        updated from ``_on_board_changed`` regardless of mode.
        """
        label = wx.StaticText(
            self,
            label="Partita in corso\n\nPremi H per comandi disponibili\nF3: attiva/disattiva modalita visiva",
        )
        label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)

        # Off-screen NVDA info zone — always created, always invisible to sighted users
        self._nvda_info_zone = wx.StaticText(self, label="", pos=(-10000, -10000))
        self._nvda_info_zone.SetSize(1, 1)

    # -----------------------------------------------------------------------
    # EVT_PAINT
    # -----------------------------------------------------------------------

    def _on_paint(self, event: wx.PaintEvent) -> None:
        """Paint handler — renders board in visual mode; no-op in audio_only."""
        if self._display_mode != _DISPLAY_VISUAL or self._board_state is None:
            dc = wx.PaintDC(self)  # must consume the event even when skipping
            dc.Clear()
            return

        dc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetClientSize()
        theme = self._current_theme

        if theme.use_card_images:
            cache = self._get_image_cache()
            bg_bmp = cache.get_background_bitmap(w, h)
            if bg_bmp is not None:
                dc.DrawBitmap(bg_bmp, 0, 0)
            else:
                dc.SetBackground(wx.Brush(wx.Colour(*theme.bg_color)))
                dc.Clear()
        else:
            dc.SetBackground(wx.Brush(wx.Colour(*theme.bg_color)))
            dc.Clear()

        layout = self._layout_manager.calculate_layout(w, h, theme)
        state = self._board_state

        for pile_idx, pile in enumerate(state.piles):
            for card_idx, card in enumerate(pile):
                rect = self._layout_manager.get_card_rect(pile_idx, card_idx, pile, layout)
                if rect is None:
                    continue
                cx, cy, cw, ch = rect
                highlighted = (
                    self._cursor_blink_on
                    and state.cursor_pile_idx == pile_idx
                    and state.cursor_card_idx == card_idx
                )
                selected = (
                    state.selection_active
                    and state.selected_pile_idx == pile_idx
                )
                bitmap: object | None = None
                if theme.use_card_images and card.face_up:
                    cache = self._get_image_cache()
                    bitmap = cache.get_bitmap(card.rank, card.suit, cw, ch)
                self._card_renderer.draw_card(
                    dc, card, cx, cy, cw, ch, theme,
                    bitmap=bitmap,
                    highlighted=highlighted,
                    selected=selected,
                )

    # -----------------------------------------------------------------------
    # EVT_SIZE
    # -----------------------------------------------------------------------

    def _on_size(self, event: wx.SizeEvent) -> None:
        """Recalculate layout and repaint on panel resize."""
        if self._image_cache is not None:
            self._image_cache.invalidate_size_cache()
        self.Refresh()
        event.Skip()

    # -----------------------------------------------------------------------
    # EVT_TIMER (blink)
    # -----------------------------------------------------------------------

    def _on_blink_timer(self, event: wx.TimerEvent) -> None:
        """Toggle cursor blink and redraw."""
        self._cursor_blink_on = not self._cursor_blink_on
        if self._display_mode == _DISPLAY_VISUAL:
            self.Refresh()

    # -----------------------------------------------------------------------
    # Board observer callback
    # -----------------------------------------------------------------------

    def _on_board_changed(self, board_state: BoardState) -> None:
        """Called by GameplayController when board state changes.

        Updates the local snapshot, the NVDA info zone, and triggers a
        repaint in visual mode.
        """
        self._board_state = board_state
        if self._nvda_info_zone is not None:
            nvda_text = self._build_nvda_text(board_state)
            self._nvda_info_zone.SetLabel(nvda_text)
            self.SetName(nvda_text)
        if self._display_mode == _DISPLAY_VISUAL:
            self.Refresh()

    def _build_nvda_text(self, state: BoardState) -> str:
        """Build a short descriptive string for the NVDA info zone.

        Args:
            state: Current board state snapshot.

        Returns:
            Human-readable string, e.g. "Pila 3, carta 2: Re di cuori".
        """
        pile_idx = state.cursor_pile_idx
        card_idx = state.cursor_card_idx
        if 0 <= pile_idx < len(state.piles):
            pile = state.piles[pile_idx]
            if 0 <= card_idx < len(pile):
                card = pile[card_idx]
                if card.face_up:
                    return f"Pila {pile_idx + 1}, carta {card_idx + 1}: {card.rank} di {card.suit}"
                return f"Pila {pile_idx + 1}, carta {card_idx + 1}: coperta"
        if state.game_over:
            return "Partita terminata"
        return f"Pila {pile_idx + 1}"

    # -----------------------------------------------------------------------
    # Display mode toggle
    # -----------------------------------------------------------------------

    def toggle_display_mode(self) -> None:
        """Toggle between audio_only and visual modes."""
        if self._display_mode == _DISPLAY_AUDIO:
            self._display_mode = _DISPLAY_VISUAL
            if self._blink_timer is not None:
                self._blink_timer.Start(_BLINK_MS)
            _log.info("GameplayPanel: modalita visiva attivata")
        else:
            self._display_mode = _DISPLAY_AUDIO
            if self._blink_timer is not None:
                self._blink_timer.Stop()
            _log.info("GameplayPanel: modalita audio attivata")
        self.Refresh()

    def apply_visual_settings(self, display_mode: str, theme_name: str) -> None:
        """Apply persisted visual preferences to the current panel instance."""
        self._display_mode = _DISPLAY_VISUAL if display_mode == _DISPLAY_VISUAL else _DISPLAY_AUDIO
        self.set_theme(theme_name)
        self._cursor_blink_on = True

        if self._blink_timer is not None:
            if self._display_mode == _DISPLAY_VISUAL:
                self._blink_timer.Start(_BLINK_MS)
            else:
                self._blink_timer.Stop()

        self.Refresh()

    @property
    def display_mode(self) -> str:
        """Current display mode string."""
        return self._display_mode

    def set_theme(self, theme_name: str) -> None:
        """Change the visual theme and repaint.

        Args:
            theme_name: One of ``"standard"``, ``"alto_contrasto"``, ``"grande"``.
        """
        self._current_theme = get_theme(theme_name)
        if self._display_mode == _DISPLAY_VISUAL:
            self.Refresh()

    # -----------------------------------------------------------------------
    # Keyboard input
    # -----------------------------------------------------------------------

    def on_key_down(self, event: wx.KeyEvent) -> None:
        """Route keyboard events to gameplay controller.

        Intercepts:
        - ESC  → show abandon dialog
        - F3   → toggle display mode
        - All others → GameplayController.handle_wx_key_event()
        """
        key_code = event.GetKeyCode()

        # ESC: show abandon dialog
        if key_code == wx.WXK_ESCAPE:
            self._handle_esc(event)
            return

        # F3: toggle display mode
        if key_code == wx.WXK_F3:
            self.toggle_display_mode()
            return  # consumed — do NOT skip

        # All other keys: route to gameplay controller
        if self.controller and hasattr(self.controller, "gameplay_controller"):
            handled = self.controller.gameplay_controller.handle_wx_key_event(event)
            if handled:
                return

        event.Skip()
    
    def _handle_esc(self, event: wx.KeyEvent) -> None:
        """Handle ESC key by showing abandon game confirmation dialog.
        
        Always shows confirmation dialog when ESC is pressed during gameplay.
        User must explicitly choose Yes or No to abandon or continue.
        
        Flow:
            1. User presses ESC
            2. Show "Vuoi abbandonare la partita?" dialog
            3. User chooses:
               - Yes: Abandon game and return to menu
               - No: Continue playing
        
        Args:
            event: wx.KeyEvent for ESC key
        
        Example:
            User presses ESC → Dialog shown with Yes/No options
            User selects No → Game continues
            User presses ESC again → Dialog shown again
        
        Note:
            This prevents accidental game abandonment by always requiring
            explicit user confirmation via dialog.
        
        New in v1.7.5: Simplified to always show dialog (removed double-ESC quick exit)
        """
        if self.controller:
            self.controller.show_abandon_game_dialog()


# Module-level documentation
__all__ = ['GameplayPanel']
