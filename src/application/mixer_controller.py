from typing import Dict, List, Optional

from src.infrastructure.audio.audio_events import AudioEvent, AudioEventType


class MixerController:
    """Accessible mixer for adjusting audio volumes.

    The controller maintains a small set of channels (master, music, effects)
    and allows navigation between them as well as value changes. Each operation
    emits audio events and uses the provided screen reader for TTS feedback
    when the verbose level is high.
    """

    def __init__(
        self,
        audio_manager: Optional[object] = None,
        screen_reader: Optional[object] = None,
        channels: Optional[Dict[str, int]] = None,
    ) -> None:
        self._audio = audio_manager
        self._sr = screen_reader
        # 0-100 percent values
        self.channels: Dict[str, int] = channels or {
            "master": 50,
            "music": 50,
            "effects": 50,
        }
        self._order: List[str] = list(self.channels.keys())
        self.cursor: int = 0
        if self._audio:
            try:
                self._audio.play_event(AudioEvent(event_type=AudioEventType.MIXER_OPENED))
            except Exception:
                pass
        if self._sr:
            try:
                self._sr.tts.speak("Mixer opened", interrupt=True)
            except Exception:
                pass

    def navigate_up(self) -> int:
        if self.cursor <= 0:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.TABLEAU_BUMPER))
                except Exception:
                    pass
        else:
            self.cursor -= 1
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_NAVIGATE))
                except Exception:
                    pass
            if self._sr:
                self._sr.tts.speak(self._order[self.cursor], interrupt=True)
        return self.cursor

    def navigate_down(self) -> int:
        if self.cursor >= len(self._order) - 1:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.TABLEAU_BUMPER))
                except Exception:
                    pass
        else:
            self.cursor += 1
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_NAVIGATE))
                except Exception:
                    pass
            if self._sr:
                self._sr.tts.speak(self._order[self.cursor], interrupt=True)
        return self.cursor

    def increase(self) -> int:
        key = self._order[self.cursor]
        if self.channels[key] < 100:
            self.channels[key] += 10
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_SELECT))
                except Exception:
                    pass
            if self._sr:
                self._sr.tts.speak(f"{key} {self.channels[key]} percent", interrupt=True)
        else:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.TABLEAU_BUMPER))
                except Exception:
                    pass
        return self.channels[key]

    def decrease(self) -> int:
        key = self._order[self.cursor]
        if self.channels[key] > 0:
            self.channels[key] -= 10
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.UI_SELECT))
                except Exception:
                    pass
            if self._sr:
                self._sr.tts.speak(f"{key} {self.channels[key]} percent", interrupt=True)
        else:
            if self._audio:
                try:
                    self._audio.play_event(AudioEvent(event_type=AudioEventType.TABLEAU_BUMPER))
                except Exception:
                    pass
        return self.channels[key]
