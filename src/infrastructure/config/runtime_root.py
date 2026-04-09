"""Runtime root resolver — canonical source for frozen vs source mode paths.

In frozen (cx_Freeze) builds all runtime resources live relative to the
executable directory.  In source builds they live relative to the project root.

Public API
----------
get_runtime_root() -> Path
    Returns the canonical root directory for runtime resources.

Version
-------
v4.5.1 — initial implementation for cx_Freeze frozen-runtime correction.
"""

import os
import sys
from pathlib import Path

_cached_root: Path | None = None


def get_runtime_root() -> Path:
    """Return the canonical runtime root for resource resolution.

    Resolution rules (in priority order):

    1. ``SOLITARIO_ROOT`` environment variable — allows test / CI overrides.
    2. Frozen build (``sys.frozen`` set by cx_Freeze) →
       ``Path(sys.executable).parent`` (the build directory).
    3. Source build → project root derived from this module's ``__file__``:
       ``src/infrastructure/config/runtime_root.py`` → ``parents[3]``.

    The result is cached after the first call.

    Returns
    -------
    Path
        Absolute, resolved path to the runtime root.
    """
    global _cached_root
    if _cached_root is not None:
        return _cached_root

    env_override = os.environ.get("SOLITARIO_ROOT")
    if env_override:
        _cached_root = Path(env_override).resolve()
        return _cached_root

    if getattr(sys, "frozen", False):
        # cx_Freeze sets sys.frozen; the executable sits in the build dir.
        _cached_root = Path(sys.executable).resolve().parent
    else:
        # Source layout: src/infrastructure/config/runtime_root.py
        # parents[0] = src/infrastructure/config
        # parents[1] = src/infrastructure
        # parents[2] = src
        # parents[3] = project root
        _cached_root = Path(__file__).resolve().parents[3]

    return _cached_root
