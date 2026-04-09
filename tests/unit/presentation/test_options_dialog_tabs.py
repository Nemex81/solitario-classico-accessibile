from __future__ import annotations

from unittest.mock import MagicMock

import pytest

wx_available = False
try:
    import wx

    _app = wx.GetApp() or wx.App(False)
    wx_available = True
except Exception:
    wx = None  # type: ignore[assignment]

from src.application.options_controller import OptionsWindowController
from src.domain.services.game_settings import GameSettings

pytestmark = pytest.mark.skipif(not wx_available, reason="wx not available in this environment")


def _make_dialog() -> object:
    from src.infrastructure.ui.options_dialog import OptionsDialog

    global _app
    if wx.GetApp() is None:
        _app = wx.App(False)

    frame = wx.Frame(None, title="Test")
    frame.Show()
    settings = GameSettings()
    controller = OptionsWindowController(settings)
    controller.open_window()
    dialog = OptionsDialog(parent=frame, controller=controller, screen_reader=MagicMock())
    return dialog, frame, settings


@pytest.mark.unit
@pytest.mark.gui
class TestOptionsDialogTabs:
    def test_options_dialog_uses_notebook_with_expected_tabs(self) -> None:
        dialog, frame, _settings = _make_dialog()
        notebook = dialog._options_notebook

        assert notebook is not None
        assert notebook.GetPageCount() == 4
        assert [notebook.GetPageText(index) for index in range(4)] == [
            "Generale",
            "Gameplay",
            "Audio e Accessibilità",
            "Visuale",
        ]

        dialog.Destroy()
        frame.Destroy()

    def test_visual_tab_uses_radiobox_for_theme(self) -> None:
        dialog, frame, _settings = _make_dialog()

        assert isinstance(dialog.visual_theme_radio, wx.RadioBox)
        assert dialog.visual_theme_radio.GetCount() == 3
        assert dialog.visual_theme_radio.GetString(1) == "Alto Contrasto"

        dialog.Destroy()
        frame.Destroy()

    def test_focus_targets_are_defined_for_each_tab(self) -> None:
        dialog, frame, _settings = _make_dialog()

        assert set(dialog._tab_focus_targets.keys()) == {0, 1, 2, 3}
        assert dialog._tab_focus_targets[0] is dialog.deck_type_radio
        assert dialog._tab_focus_targets[3] is dialog.display_mode_radio

        dialog.Destroy()
        frame.Destroy()

    def test_visual_controls_load_current_settings(self) -> None:
        dialog, frame, settings = _make_dialog()
        settings.display_mode = "visual"
        settings.visual_theme = "alto_contrasto"

        dialog._load_settings_to_widgets()

        assert dialog.display_mode_radio.GetSelection() == 1
        assert dialog.visual_theme_radio.GetSelection() == 1

        dialog.Destroy()
        frame.Destroy()
