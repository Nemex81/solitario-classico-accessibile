"""
Sistema logging categorizzato - Solitario Classico Accessibile

Sostituisce il monolite solitario.log con 5 file separati per categoria,
mantenendo l'API pubblica (setup_logging) completamente immutata.

Strategia: Multi-handler su named loggers Python esistenti.
Il routing è già risolto dai named loggers — questa funzione aggiunge
solo i RotatingFileHandler dedicati a ciascun logger.

Categorie attive:
    - game      → game_logic.log    (lifecycle partita, mosse)
    - ui        → ui_events.log     (navigazione, dialogs, TTS)
    - error     → errors.log        (errori, warnings)
    - timer     → timer.log         (lifecycle timer, scadenza)

Categorie future (decommentare in CATEGORIES + aggiungere logger in game_logger.py):
    - profile   → profiles.log      (CRUD profili)
    - scoring   → scoring.log       (calcoli punteggio)
    - storage   → storage.log       (I/O file/JSON)

Root logger:
    solitario.log → library logs (wx, PIL, urllib3)

Compatibilità:
    logger_setup.py espone ancora setup_logging() come thin wrapper.
    acs_wx.py e i test esistenti non richiedono modifiche.

Version:
    v3.3.0: Initial implementation (replaces monolithic solitario.log)

Author:
    Nemex81
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ── Configurazione paths ───────────────────────────────────────────────────────

LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "solitario.log"   # root logger (library logs)

# ── Registro categorie ─────────────────────────────────────────────────────────

CATEGORIES: dict[str, str] = {
    'game':    'game_logic.log',
    'ui':      'ui_events.log',
    'error':   'errors.log',
    'timer':   'timer.log',
    # Categorie future — attiva decommentando + aggiungendo named logger in game_logger.py
    # 'profile':  'profiles.log',
    # 'scoring':  'scoring.log',
    # 'storage':  'storage.log',
}

# ── Formatter condiviso ────────────────────────────────────────────────────────

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_categorized_logging(
    logs_dir: Path = LOGS_DIR,
    level: int = logging.INFO,
    console_output: bool = False,
) -> None:
    """
    Configura logging multi-file categorizzato.

    Crea un RotatingFileHandler dedicato per ogni categoria in CATEGORIES,
    con propagate=False per evitare duplicazione su solitario.log.
    Il root logger mantiene solitario.log per i log di librerie esterne.

    Args:
        logs_dir:       Directory log (default: Path("logs"))
        level:          Livello minimo (default: logging.INFO)
        console_output: Se True, log anche su console (per sviluppo)

    Note:
        Chiamare UNA VOLTA all'avvio, prima di qualsiasi altra init.
        Sostituisce setup_logging() di logger_setup.py (ora thin wrapper).
        Guard anti-doppia-registrazione: se handler già presenti, skip.

    Example:
        >>> setup_categorized_logging(level=logging.DEBUG, console_output=True)
        >>> # Risultato: 5 file in logs/
        >>> #   game_logic.log, ui_events.log, errors.log, timer.log, solitario.log

    Version:
        v3.3.0: Initial implementation
    """
    logs_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # ── Handler per ogni categoria ─────────────────────────────────────────────
    for category, filename in CATEGORIES.items():
        logger = logging.getLogger(category)

        # Guard anti-doppia-registrazione (es. nei test che chiamano setup più volte)
        if logger.handlers:
            continue

        handler = RotatingFileHandler(
            logs_dir / filename,
            maxBytes=5 * 1024 * 1024,   # 5 MB
            backupCount=3,               # .log.1 / .log.2 / .log.3
            encoding='utf-8',
        )
        handler.setFormatter(formatter)
        handler.setLevel(level)

        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False         # CRITICO: evita duplicazione su solitario.log

    # ── Root logger: solitario.log (library logs: wx, PIL, urllib3) ────────────
    root_logger = logging.getLogger()
    root_log_path = str((logs_dir / 'solitario.log').resolve())
    # Guard precisa: controlla solo RotatingFileHandler per solitario.log,
    # ignorando gli handler di pytest o altri framework di test.
    already_has_root_file = any(
        isinstance(h, RotatingFileHandler)
        and getattr(h, 'baseFilename', None) == root_log_path
        for h in root_logger.handlers
    )
    if not already_has_root_file:
        root_handler = RotatingFileHandler(
            logs_dir / 'solitario.log',
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8',
        )
        root_handler.setFormatter(formatter)
        root_handler.setLevel(level)
        root_logger.addHandler(root_handler)
        root_logger.setLevel(level)

    # ── Console handler (solo sviluppo) ────────────────────────────────────────
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)

    # ── Sopprimi noise da librerie esterne ─────────────────────────────────────
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('wx').setLevel(logging.WARNING)
