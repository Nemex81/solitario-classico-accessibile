import pytest

from src.infrastructure.audio import audio_events


class TestAudioEventTypeConstants:
    @pytest.mark.unit
    def test_all_new_constants_exist(self):
        """Verify that the 21 new event constants are defined on AudioEventType."""
        names = [
            'CARD_FLIP', 'CARD_SHUFFLE', 'CARD_SHUFFLE_WASTE', 'TABLEAU_DROP',
            'CARDS_EXHAUSTED', 'MULTI_CARD_MOVE', 'UI_NAVIGATE_FRAME',
            'UI_NAVIGATE_PILE', 'UI_CONFIRM', 'UI_TOGGLE', 'UI_FOCUS_CHANGE',
            'UI_BOUNDARY_HIT', 'UI_NOTIFICATION', 'UI_ERROR', 'UI_MENU_OPEN',
            'UI_MENU_CLOSE', 'UI_BUTTON_CLICK', 'UI_BUTTON_HOVER',
            'SETTING_SAVED', 'SETTING_CHANGED', 'SETTING_LEVEL_CHANGED',
            'SETTING_VOLUME_CHANGED', 'SETTING_MUSIC_CHANGED',
            'SETTING_SWITCH_ON', 'SETTING_SWITCH_OFF', 'WELCOME_MESSAGE'
        ]

        for name in names:
            assert hasattr(audio_events.AudioEventType, name), \
                f"Missing constant {name} on AudioEventType"

    @pytest.mark.unit
    def test_constants_are_strings(self):
        """Each constant should be a non-empty string."""
        for attr, value in vars(audio_events.AudioEventType).items():
            if attr.isupper():
                assert isinstance(value, str)
                assert value, f"AudioEventType.{attr} is empty"
