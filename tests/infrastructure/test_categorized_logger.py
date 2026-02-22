"""
Test unitari per src/infrastructure/logging/categorized_logger.py

Verifica:
- Creazione file di log per ogni categoria attiva
- Guard anti-doppia-registrazione (idempotenza)
- propagate=False su tutti i named logger (no duplicazioni su root)
- Retrocompatibilità wrapper setup_logging() -> setup_categorized_logging()
- Soppressione rumore librerie esterne (PIL, urllib3, wx)

Non richiede wx. Usa tmp_path di pytest per isolamento filesystem.
Marker: @pytest.mark.unit
"""

import logging
import pytest

from src.infrastructure.logging.categorized_logger import (
    CATEGORIES,
    setup_categorized_logging,
)
from src.infrastructure.logging.logger_setup import setup_logging


# ---------------------------------------------------------------------------
# Fixture: reset stato logging tra i test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_logging():
    """
    Rimuove i handler aggiunti dai test dai named logger e dal root logger,
    garantendo isolamento tra i test. Cleanup eseguito sia PRIMA che DOPO ogni
    test per prevenire contaminazioni quando i test vengono eseguiti in ordine
    arbitrario (es. pytest-randomly).
    """
    def _cleanup():
        for category in CATEGORIES:
            logger = logging.getLogger(category)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            logger.propagate = True  # ripristina default

        root = logging.getLogger()
        for handler in root.handlers[:]:
            handler.close()
            root.removeHandler(handler)

    _cleanup()  # Pre-test: stato pulito indipendentemente dall'ordine di esecuzione
    yield
    _cleanup()  # Post-test: cleanup per i test successivi


# ---------------------------------------------------------------------------
# Test 1: creazione file di log per ogni categoria attiva
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_creates_log_files_for_all_categories(tmp_path):
    """
    setup_categorized_logging() deve creare un file .log per ogni categoria
    in CATEGORIES, più solitario.log per il root logger.
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for category, filename in CATEGORIES.items():
        log_file = tmp_path / filename
        assert log_file.exists(), (
            f"File di log mancante per categoria '{category}': {log_file}"
        )

    # Root logger
    assert (tmp_path / "solitario.log").exists(), (
        "solitario.log mancante (root logger)"
    )


# ---------------------------------------------------------------------------
# Test 2: guard anti-doppia-registrazione (idempotenza)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_idempotent_no_duplicate_handlers(tmp_path):
    """
    Chiamare setup_categorized_logging() due volte non deve aggiungere
    handler duplicati ai named logger. Ogni logger deve avere esattamente 1 handler.
    """
    setup_categorized_logging(logs_dir=tmp_path)
    setup_categorized_logging(logs_dir=tmp_path)  # seconda chiamata

    for category in CATEGORIES:
        logger = logging.getLogger(category)
        assert len(logger.handlers) == 1, (
            f"Logger '{category}' ha {len(logger.handlers)} handler dopo doppia init "
            f"(atteso: 1)"
        )


# ---------------------------------------------------------------------------
# Test 3: propagate=False su tutti i named logger
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_sets_propagate_false_on_all_category_loggers(tmp_path):
    """
    Ogni named logger per categoria deve avere propagate=False per evitare
    che i messaggi vengano duplicati su solitario.log (root logger).
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for category in CATEGORIES:
        logger = logging.getLogger(category)
        assert logger.propagate is False, (
            f"Logger '{category}' ha propagate=True (deve essere False)"
        )


# ---------------------------------------------------------------------------
# Test 4: retrocompatibilità wrapper setup_logging()
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_logging_wrapper_creates_same_files(tmp_path):
    """
    setup_logging() in logger_setup.py è un thin wrapper su
    setup_categorized_logging(). Deve produrre gli stessi file di log.
    """
    setup_logging(logs_dir=tmp_path)

    for category, filename in CATEGORIES.items():
        log_file = tmp_path / filename
        assert log_file.exists(), (
            f"Wrapper setup_logging() non ha creato '{filename}' per '{category}'"
        )


# ---------------------------------------------------------------------------
# Test 5: soppressione rumore librerie esterne
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_setup_suppresses_external_library_loggers(tmp_path):
    """
    Dopo setup_categorized_logging(), i logger di librerie esterne (PIL,
    urllib3, wx) devono avere livello >= WARNING per non inquinare i log.
    """
    setup_categorized_logging(logs_dir=tmp_path)

    for lib in ('PIL', 'urllib3', 'wx'):
        lib_logger = logging.getLogger(lib)
        assert lib_logger.level >= logging.WARNING, (
            f"Logger '{lib}' ha livello {lib_logger.level} "
            f"(atteso >= {logging.WARNING})"
        )
