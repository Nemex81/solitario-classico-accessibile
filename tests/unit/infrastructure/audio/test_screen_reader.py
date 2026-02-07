"""Tests for screen reader and TTS provider functionality.

Comprehensive test suite covering:
- TtsProvider abstraction and implementations
- ScreenReader service functionality
- Mock-based testing (no real TTS engines required)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.infrastructure.audio.screen_reader import ScreenReader
from src.infrastructure.audio.tts_provider import (
    TtsProvider,
    Sapi5Provider,
    NvdaProvider,
    create_tts_provider,
)
from src.domain.models.card import Card


class TestScreenReaderBasics:
    """Test basic ScreenReader functionality and configuration."""
    
    def test_initialization_with_tts_provider(self) -> None:
        """Test ScreenReader initializes correctly with TTS provider."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True, verbose=1)
        
        assert screen_reader.tts is mock_tts
        assert screen_reader.enabled is True
        assert screen_reader.verbose == 1
    
    def test_enabled_disabled_toggle(self) -> None:
        """Test enabling and disabling screen reader."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        assert screen_reader.enabled is True
        
        screen_reader.set_enabled(False)
        assert screen_reader.enabled is False
        
        screen_reader.set_enabled(True)
        assert screen_reader.enabled is True
    
    def test_verbose_level_control(self) -> None:
        """Test verbosity level clamping to valid range 0-2."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts)
        
        # Test normal values
        screen_reader.set_verbose(0)
        assert screen_reader.verbose == 0
        
        screen_reader.set_verbose(2)
        assert screen_reader.verbose == 2
        
        # Test clamping
        screen_reader.set_verbose(-5)
        assert screen_reader.verbose == 0
        
        screen_reader.set_verbose(10)
        assert screen_reader.verbose == 2


class TestAnnouncements:
    """Test ScreenReader announcement methods."""
    
    def test_announce_move_success(self) -> None:
        """Test announcing successful move."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        screen_reader.announce_move(success=True, message="carta spostata", interrupt=False)
        
        mock_tts.speak.assert_called_once_with(
            "Mossa eseguita: carta spostata",
            interrupt=False
        )
    
    def test_announce_move_failure(self) -> None:
        """Test announcing invalid move."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        screen_reader.announce_move(success=False, message="mossa illegale", interrupt=True)
        
        mock_tts.speak.assert_called_once_with(
            "Mossa non valida: mossa illegale",
            interrupt=True
        )
    
    def test_announce_card_covered(self) -> None:
        """Test announcing covered (face-down) card."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        # Create mock card that is covered
        mock_card = Mock(spec=Card)
        mock_card.get_name = "Sette"
        mock_card.get_suit = "cuori"
        mock_card.get_covered = True
        
        screen_reader.announce_card(mock_card)
        
        mock_tts.speak.assert_called_once_with(
            "Sette di cuori, coperta",
            interrupt=False
        )
    
    def test_announce_card_uncovered(self) -> None:
        """Test announcing uncovered (face-up) card."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        # Create mock card that is uncovered
        mock_card = Mock(spec=Card)
        mock_card.get_name = "Asso"
        mock_card.get_suit = "picche"
        mock_card.get_covered = False
        
        screen_reader.announce_card(mock_card)
        
        mock_tts.speak.assert_called_once_with(
            "Asso di picche, scoperta",
            interrupt=False
        )
    
    def test_announce_victory(self) -> None:
        """Test announcing game victory with statistics."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        screen_reader.announce_victory(moves=42, time=180)
        
        mock_tts.speak.assert_called_once_with(
            "Vittoria! Completato in 180 secondi con 42 mosse.",
            interrupt=True
        )


class TestTtsProvider:
    """Test TTS provider implementations and factory."""
    
    def test_sapi5_provider_initialization(self) -> None:
        """Test Sapi5Provider initialization on Windows."""
        with patch('sys.platform', 'win32'):
            with patch('builtins.__import__', side_effect=self._mock_import_pyttsx3):
                provider = Sapi5Provider()
                
                assert hasattr(provider, 'engine')
                assert provider.engine is not None
    
    def _mock_import_pyttsx3(self, name: str, *args, **kwargs):
        """Mock pyttsx3 import."""
        if name == 'pyttsx3':
            mock_module = Mock()
            mock_engine = Mock()
            mock_module.init = Mock(return_value=mock_engine)
            return mock_module
        return __import__(name, *args, **kwargs)
    
    def test_nvda_provider_initialization(self) -> None:
        """Test NvdaProvider initialization when NVDA is running."""
        with patch('builtins.__import__', side_effect=self._mock_import_nvda):
            provider = NvdaProvider()
            
            assert hasattr(provider, 'nvda')
            assert provider.nvda is not None
    
    def _mock_import_nvda(self, name: str, *args, **kwargs):
        """Mock accessible_output2 import."""
        if name == 'accessible_output2.outputs':
            mock_module = Mock()
            mock_nvda_class = Mock()
            mock_nvda_instance = Mock()
            mock_nvda_instance.is_active = Mock(return_value=True)
            mock_nvda_class.return_value = mock_nvda_instance
            mock_module.nvda = Mock()
            mock_module.nvda.NVDA = mock_nvda_class
            return mock_module
        return __import__(name, *args, **kwargs)
    
    @patch('src.infrastructure.audio.tts_provider.NvdaProvider')
    @patch('src.infrastructure.audio.tts_provider.Sapi5Provider')
    def test_create_tts_provider_auto(
        self,
        mock_sapi5: Mock,
        mock_nvda: Mock
    ) -> None:
        """Test factory with auto mode tries NVDA first, then SAPI5."""
        # NVDA fails, SAPI5 succeeds
        mock_nvda.side_effect = RuntimeError("NVDA not available")
        mock_sapi5_instance = Mock(spec=TtsProvider)
        mock_sapi5.return_value = mock_sapi5_instance
        
        provider = create_tts_provider(engine="auto")
        
        assert provider is mock_sapi5_instance
        mock_nvda.assert_called_once()
        mock_sapi5.assert_called_once()
    
    def test_create_tts_provider_invalid_engine(self) -> None:
        """Test factory raises ValueError for unknown engine."""
        with pytest.raises(ValueError, match="Unknown TTS engine"):
            create_tts_provider(engine="nonexistent")


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_announce_error_interrupts(self) -> None:
        """Test error announcements always interrupt."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        screen_reader.announce_error("Errore di sistema")
        
        mock_tts.speak.assert_called_once_with(
            "Errore: Errore di sistema",
            interrupt=True
        )
    
    def test_disabled_screen_reader_no_speech(self) -> None:
        """Test disabled screen reader doesn't call TTS."""
        mock_tts = Mock(spec=TtsProvider)
        screen_reader = ScreenReader(tts=mock_tts, enabled=False)
        
        # Try various announcements
        screen_reader.announce_move(True, "test")
        screen_reader.announce_error("test")
        screen_reader.announce_victory(10, 100)
        
        mock_card = Mock(spec=Card)
        mock_card.get_name = "Test"
        mock_card.get_suit = "test"
        mock_card.get_covered = False
        screen_reader.announce_card(mock_card)
        
        # TTS should never be called
        mock_tts.speak.assert_not_called()
    
    def test_tts_provider_failure_handling(self) -> None:
        """Test graceful handling of TTS provider failures."""
        mock_tts = Mock(spec=TtsProvider)
        mock_tts.speak.side_effect = Exception("TTS engine error")
        
        screen_reader = ScreenReader(tts=mock_tts, enabled=True)
        
        # Should not raise exception, but let it propagate
        # (caller should handle TTS failures)
        with pytest.raises(Exception, match="TTS engine error"):
            screen_reader.announce_move(True, "test")


class TestTtsProviderMethods:
    """Test TTS provider method implementations."""
    
    def test_sapi5_speak_with_interrupt(self) -> None:
        """Test Sapi5Provider speak method with interrupt."""
        with patch('sys.platform', 'win32'):
            mock_engine = Mock()
            with patch('builtins.__import__') as mock_import:
                # Configure mock to return pyttsx3 with mock engine
                def import_side_effect(name, *args, **kwargs):
                    if name == 'pyttsx3':
                        mock_module = Mock()
                        mock_module.init = Mock(return_value=mock_engine)
                        return mock_module
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = import_side_effect
                
                provider = Sapi5Provider()
                provider.speak("test message", interrupt=True)
                
                mock_engine.stop.assert_called_once()
                mock_engine.say.assert_called_once_with("test message")
                mock_engine.runAndWait.assert_called_once()
    
    def test_sapi5_set_rate(self) -> None:
        """Test Sapi5Provider rate setting."""
        with patch('sys.platform', 'win32'):
            mock_engine = Mock()
            with patch('builtins.__import__') as mock_import:
                # Configure mock to return pyttsx3 with mock engine
                def import_side_effect(name, *args, **kwargs):
                    if name == 'pyttsx3':
                        mock_module = Mock()
                        mock_module.init = Mock(return_value=mock_engine)
                        return mock_module
                    return __import__(name, *args, **kwargs)
                
                mock_import.side_effect = import_side_effect
                
                provider = Sapi5Provider()
                provider.set_rate(5)  # Rate of 5 should map to 225
                
                mock_engine.setProperty.assert_called_with('rate', 225)
    
    def test_nvda_speak_with_interrupt(self) -> None:
        """Test NvdaProvider speak method with interrupt."""
        mock_nvda_instance = Mock()
        mock_nvda_instance.is_active = Mock(return_value=True)
        
        with patch('builtins.__import__') as mock_import:
            # Configure mock to return accessible_output2 with NVDA
            def import_side_effect(name, *args, **kwargs):
                if name == 'accessible_output2.outputs':
                    mock_module = Mock()
                    mock_nvda_class = Mock(return_value=mock_nvda_instance)
                    mock_module.nvda = Mock()
                    mock_module.nvda.NVDA = mock_nvda_class
                    return mock_module
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            provider = NvdaProvider()
            provider.speak("test message", interrupt=True)
            
            mock_nvda_instance.speak.assert_called_once_with(
                "test message",
                interrupt=True
            )
