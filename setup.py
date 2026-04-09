from __future__ import annotations

import re
import shutil
import stat
import sys
from pathlib import Path

from cx_Freeze import Executable, setup


ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist" / "solitario-classico"


def _handle_remove_readonly(
    func: object,
    path: str,
    exc_info: tuple[type[BaseException], BaseException, object],
) -> None:
    """Retry removal after clearing read-only flags on Windows/OneDrive paths."""
    del exc_info
    target_path = Path(path)
    target_path.chmod(stat.S_IWRITE | stat.S_IREAD)
    func(path)


def _prepare_build_dir() -> None:
    """Remove the previous frozen build before cx_Freeze tries to clean it.

    cx_Freeze performs a plain ``shutil.rmtree`` on ``build_exe`` and aborts if
    that fails. Under Windows, OneDrive-managed directories can surface files or
    folders with restrictive attributes that require a permission reset first.
    """
    if not DIST_DIR.exists():
        return
    shutil.rmtree(DIST_DIR, onerror=_handle_remove_readonly)


def _read_version() -> str:
    """Read the application version from pyproject or project profile."""
    pyproject_path = ROOT_DIR / "pyproject.toml"
    if pyproject_path.exists():
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject_text)
        if version_match:
            return version_match.group(1)

    profile_path = ROOT_DIR / ".github" / "project-profile.md"
    if profile_path.exists():
        profile_text = profile_path.read_text(encoding="utf-8")
        version_match = re.search(r'^version:\s*["\']?([^"\'\n]+)["\']?', profile_text, re.MULTILINE)
        if version_match:
            return version_match.group(1).strip()

    return "0.0.0"


def _read_long_description() -> str:
    """Use the repository README as the package long description when present."""
    readme_path = ROOT_DIR / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return "Solitario Classico Accessibile"


def _collect_include_files() -> list[tuple[str, str]]:
    """Collect runtime assets and config files for both root and lib paths.

    The application currently resolves resources in two different ways:
    - relative paths like ``assets/sounds`` or ``config/audio_config.json``
    - paths derived from ``__file__`` inside modules under ``src/``

    Copying assets/config to both the build root and ``lib/`` keeps the
    frozen runtime compatible without refactoring application paths.
    """
    include_pairs: list[tuple[str, str]] = []
    for source_name, target_name in (
        ("assets", "assets"),
        ("config", "config"),
        ("assets", "lib/assets"),
        ("config", "lib/config"),
    ):
        source_path = ROOT_DIR / source_name
        if source_path.exists():
            include_pairs.append((str(source_path), target_name))
    return include_pairs


# After each build_exe run, validate the resulting bundle with
# `python scripts/validate_frozen_build.py dist/solitario-classico`.


BUILD_EXE_OPTIONS: dict[str, object] = {
    "build_exe": str(DIST_DIR),
    "packages": [
        "src",
        "src.application",
        "src.domain",
        "src.infrastructure",
        "src.presentation",
        "accessible_output2",
        "pygame",
        "wx",
    ],
    "includes": [
        "accessible_output2.outputs.auto",
        "accessible_output2.outputs.nvda",
        "accessible_output2.outputs.sapi5",
        "pygame",
        "wx.adv",
        "wx.html",
        "wx.lib.agw.aui",
        "src.infrastructure.audio.audio_events",
        "src.infrastructure.config.audio_config_loader",
        "src.infrastructure.config.scoring_config_loader",
        "src.infrastructure.ui.widgets.timer_combobox",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "test",
        "pydoc",
        "html",
        "http",
        "xmlrpc",
    ],
    "include_files": _collect_include_files(),
    "zip_include_packages": [],
    "zip_exclude_packages": ["*"],
    "include_msvcr": sys.platform == "win32",
    "optimize": 1,
}


BASE = "Win32GUI" if sys.platform == "win32" else None


_prepare_build_dir()


setup(
    name="solitario-classico-accessibile",
    version=_read_version(),
    description="Solitario classico accessibile con supporto NVDA e wxPython.",
    long_description=_read_long_description(),
    long_description_content_type="text/markdown",
    author="Nemex81",
    options={"build_exe": BUILD_EXE_OPTIONS},
    executables=[
        Executable(
            script=str(ROOT_DIR / "acs_wx.py"),
            base=BASE,
            target_name="solitario.exe",
        ),
        Executable(
            script=str(ROOT_DIR / "acs_wx.py"),
            base=None,
            target_name="solitario-diag.exe",
        )
    ],
)