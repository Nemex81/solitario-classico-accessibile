"""
Sistema logging centralizzato - Solitario Classico Accessibile

Configurazione:
- RotatingFileHandler: 5MB max, 5 backup (25MB totale)
- Formato: timestamp - level - logger_name - message
- Auto-creazione directory logs/

Version:
    v2.3.0: Initial implementation

Author:
    Nemex81

Inspired by:
    hs_deckmanager/utyls/logger.py
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# Directory logs (auto-create)
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# File principale
LOG_FILE = LOGS_DIR / "solitario.log"


def setup_logging(level: int = logging.INFO, console_output: bool = False) -> None:
    """
    Configura logging globale dell'applicazione.
    
    Args:
        level: Livello minimo (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Se True, log anche su console (utile durante dev)
    
    Note:
        - Chiamare UNA VOLTA all'avvio in test.py
        - RotatingFileHandler previene file giganti (auto-rotation a 5MB)
        - Backup count 5 = max 25MB storage totale
    
    Example:
        >>> setup_logging(level=logging.DEBUG, console_output=True)
        >>> # Durante sviluppo: verbose + console
        >>> setup_logging(level=logging.INFO, console_output=False)
        >>> # In production: solo INFO+ su file
    
    Version:
        v2.3.0: Initial implementation
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create and configure file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,              # .log.1 ... .log.5
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Get root logger and configure
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
    
    # Disabilita log verbosi di librerie esterne
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('wx').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Factory per logger specifici.
    
    Args:
        name: Nome logger (es: 'gameplay', 'window_controller', 'error')
    
    Returns:
        Logger configurato con handler globale da setup_logging()
    
    Example:
        >>> logger = get_logger('gameplay')
        >>> logger.info("Card moved successfully")
        2026-02-14 14:30:12 - INFO - gameplay - Card moved successfully
    
    Note:
        - Chiamare get_logger() dopo setup_logging()
        - Logger multipli permettono filtering selettivo
    
    Version:
        v2.3.0: Initial implementation
    """
    return logging.getLogger(name)
