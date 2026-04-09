import pytest

from src.presentation.options_formatter import OptionsFormatter


@pytest.mark.unit
class TestOptionsFormatterHelp:
    def test_help_text_matches_wx_dialog_navigation(self) -> None:
        result = OptionsFormatter.format_help_text()

        assert "TAB" in result
        assert "scheda" in result.lower()
        assert "SPAZIO" in result
        assert "ESC" in result
