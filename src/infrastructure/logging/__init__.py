"""
Infrastructure Logging Package.

Public API:
    - setup_logging(): Configure global logging
    - get_logger(name): Create named logger
    - game_logger module: Semantic helper functions

Version:
    v2.3.0: Initial implementation
"""

from .logger_setup import setup_logging, get_logger
from .categorized_logger import setup_categorized_logging, LOGS_DIR, LOG_FILE

__all__ = ['setup_logging', 'get_logger', 'setup_categorized_logging', 'LOGS_DIR', 'LOG_FILE']
