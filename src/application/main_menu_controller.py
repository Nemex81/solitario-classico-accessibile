from typing import List, Optional

from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType


class MainMenuController:
    """Controller for the main menu logic with audio feedback.

    This class is intentionally lightweight; the UI layer (wx) handles the
    actual rendering of buttons, while the controller tracks a cursor position
    and emits audio events when the user navigates or makes selections.

    The controller exposes the same set of actions used by the old
    ``InputHandler`` and the new ``OptionsWindowController`` so the codebase
    can uniformly play sounds during menu interaction. Boundary hits are
    signalled with ``TABLEAU_BUMPER`` even though the terminology comes from
    gameplay; the sound is repurposed as a "cannot move further" effect.
    """

    def __init__(
        self,
        audio_manager: Optional[object] = None,
        items: Optional[List[str]] = None,
    ) -> None:
        self._audio = audio_manager
        # six standard buttons if not overridden
        self.items = items or [
            "Nuova Partita",
            "Opzioni",
            "Ultima Partita",
            "Leaderboard",
            "Gestione Profili",
            "Esci",
        ]
        self.cursor: int = 0
        # emit open sound so that external code can call it when the menu is
        # shown; constructors may be used directly in tests
        if self._audio:
            try:
                self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_MENU_OPEN))
            except Exception:
                pass

    # navigation helpers --------------------------------------------------
    def navigate_up(self) -> int:
        if self.cursor <= 0:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_BOUNDARY_HIT))
                except Exception:
                    pass
        else:
            self.cursor -= 1
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_NAVIGATE))
                except Exception:
                    pass
        return self.cursor

    def navigate_down(self) -> int:
        if self.cursor >= len(self.items) - 1:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_BOUNDARY_HIT))
                except Exception:
                    pass
        else:
            self.cursor += 1
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_NAVIGATE))
                except Exception:
                    pass
        return self.cursor

    # actions ------------------------------------------------------------
    def select(self) -> str:
        if self._audio:
            try:
                self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_BUTTON_CLICK))
            except Exception:
                pass
        return self.items[self.cursor]

    def cancel(self) -> None:
        if self._audio:
            try:
                self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_CANCEL))
            except Exception:
                pass
        return None
