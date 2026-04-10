from unittest.mock import Mock

from src.application.game_engine import GameEngine


class TestSelectionReplacement:
    def test_select_card_at_cursor_replaces_existing_selection(self) -> None:
        engine = GameEngine.create(audio_enabled=False)
        engine.screen_reader = Mock()
        engine.screen_reader.tts = Mock()

        first_pile = engine.table.pile_base[0]
        second_pile = engine.table.pile_base[1]

        for card in first_pile.cards:
            card.set_uncover()
        for card in second_pile.cards:
            card.set_uncover()

        engine.cursor.pile_idx = 0
        engine.cursor.card_idx = 0
        first_card_name = str(first_pile.cards[0].get_name)
        success, _ = engine.select_card_at_cursor()
        assert success is True

        engine.cursor.pile_idx = 1
        engine.cursor.card_idx = 0
        second_card_name = str(second_pile.cards[0].get_name)
        success, message = engine.select_card_at_cursor()

        assert success is True
        assert "sostituendo la carta selezionata" in message.lower()
        assert first_card_name in message
        assert second_card_name in message
        assert engine.selection.selected_cards[0] == second_pile.cards[0]
        assert engine.screen_reader.tts.speak.call_args_list[-1].kwargs["interrupt"] is True

    def test_failed_replacement_restores_previous_selection(self) -> None:
        engine = GameEngine.create(audio_enabled=False)
        engine.screen_reader = Mock()
        engine.screen_reader.tts = Mock()

        source_pile = engine.table.pile_base[0]
        blocked_pile = engine.table.pile_base[1]

        for card in source_pile.cards:
            card.set_uncover()
        for card in blocked_pile.cards:
            card.set_cover()

        engine.cursor.pile_idx = 0
        engine.cursor.card_idx = 0
        first_card = source_pile.cards[0]
        success, _ = engine.select_card_at_cursor()
        assert success is True

        engine.cursor.pile_idx = 1
        engine.cursor.card_idx = 0
        success, message = engine.select_card_at_cursor()

        assert success is False
        assert "coperta" in message.lower()
        assert engine.selection.selected_cards[0] == first_card
        assert engine.selection.origin_pile == source_pile
