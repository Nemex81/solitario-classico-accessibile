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

__all__ = ['setup_logging', 'get_logger']
