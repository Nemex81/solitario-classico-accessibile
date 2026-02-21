"""
Sistema logging centralizzato - Solitario Classico Accessibile

DEPRECATO: La logica reale è in categorized_logger.py (v3.2.0).
Mantenuto come thin wrapper per backward compatibility:
- acs_wx.py chiama ancora setup_logging() senza modifiche
- I test importano ancora LOGS_DIR, get_logger() senza modifiche

Version:
    v2.3.0: Initial implementation
    v3.2.0: Thin wrapper → categorized_logger.py

Author:
    Nemex81
"""

import logging

# Re-export per backward compatibility
from .categorized_logger import (
    setup_categorized_logging,
    LOGS_DIR,       # Path("logs") — usato da test_logger_setup.py
    LOG_FILE,       # LOGS_DIR / "solitario.log" — usato da test_logger_setup.py
)


def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    """
    Configura logging globale dell'applicazione.

    DEPRECATED: Thin wrapper su setup_categorized_logging().
    Mantenuto per backward compatibility con acs_wx.py e test esistenti.

    Args:
        level:          Livello minimo (default: logging.INFO)
        console_output: Se True, log anche su console

    Example:
        >>> setup_logging(level=logging.DEBUG, console_output=True)

    Version:
        v2.3.0: Initial implementation
        v3.2.0: Thin wrapper → categorized_logger.py
    """
    setup_categorized_logging(level=level, console_output=console_output)


def get_logger(name: str) -> logging.Logger:
    """
    Factory per logger specifici.

    Args:
        name: Nome logger (es: 'gameplay', 'window_controller')

    Returns:
        Logger configurato

    Example:
        >>> logger = get_logger('gameplay')
        >>> logger.info("Card moved successfully")
    """
    return logging.getLogger(name)
