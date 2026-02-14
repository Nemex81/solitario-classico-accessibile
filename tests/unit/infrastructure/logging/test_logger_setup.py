"""
Unit tests per logger_setup module.

Testa:
- Setup configurazione
- Auto-creazione directory
- Logger factory
- File rotation (mock)
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.infrastructure.logging.logger_setup import setup_logging, get_logger, LOGS_DIR


class TestSetupLogging:
    """
    Test suite per setup_logging().
    """
    
    def setup_method(self):
        """Clear all handlers before each test."""
        logging.root.handlers.clear()
    
    def test_logs_directory_created(self):
        """
        Test: Directory logs/ creata automaticamente.
        """
        # Assert - LOGS_DIR is created at module import
        assert LOGS_DIR.exists()
        assert LOGS_DIR.is_dir()
    
    def test_rotating_handler_configured(self):
        """
        Test: RotatingFileHandler con maxBytes e backupCount corretti.
        """
        # Act
        setup_logging()
        
        # Assert
        root_logger = logging.getLogger()
        handlers = [h for h in root_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        
        assert len(handlers) > 0
        handler = handlers[0]
        assert handler.maxBytes == 5 * 1024 * 1024  # 5MB
        assert handler.backupCount == 5
    
    def test_console_output_optional(self):
        """
        Test: Console handler aggiunto solo se console_output=True.
        """
        # Act
        setup_logging(console_output=True)
        
        # Assert
        root_logger = logging.getLogger()
        stream_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) 
                          and not isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(stream_handlers) > 0


class TestGetLogger:
    """
    Test suite per get_logger() factory.
    """
    
    def test_returns_logger_instance(self):
        """
        Test: get_logger() ritorna istanza logging.Logger.
        """
        # Act
        logger = get_logger('test')
        
        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test'
    
    def test_same_name_returns_same_instance(self):
        """
        Test: Chiamare get_logger() con stesso nome ritorna stessa istanza.
        """
        # Act
        logger1 = get_logger('game')
        logger2 = get_logger('game')
        
        # Assert
        assert logger1 is logger2
