from __future__ import annotations

import argparse
import ctypes
import os
import sys
from pathlib import Path


REQUIRED_DIRECTORIES: tuple[str, ...] = ("assets", "config", "lib")
REQUIRED_EXECUTABLES: tuple[str, ...] = ("solitario.exe", "solitario-diag.exe")
REQUIRED_PYGAME_DLLS: tuple[str, ...] = (
    "SDL2.dll",
    "SDL2_mixer.dll",
    "SDL2_image.dll",
    "SDL2_ttf.dll",
)


def _find_file(root_dir: Path, file_name: str) -> Path | None:
    for path in root_dir.rglob(file_name):
        if path.is_file():
            return path
    return None


def _validate_structure(build_dir: Path, errors: list[str]) -> None:
    for dir_name in REQUIRED_DIRECTORIES:
        target = build_dir / dir_name
        if not target.is_dir():
            errors.append(f"Directory mancante: {target}")

    for exe_name in REQUIRED_EXECUTABLES:
        target = build_dir / exe_name
        if not target.is_file():
            errors.append(f"Executable mancante: {target}")


def _validate_pygame_dlls(build_dir: Path, errors: list[str]) -> None:
    for dll_name in REQUIRED_PYGAME_DLLS:
        dll_path = _find_file(build_dir, dll_name)
        if dll_path is None:
            errors.append(f"DLL mancante: {dll_name}")
            continue

        try:
            os.add_dll_directory(str(dll_path.parent))
        except (AttributeError, FileNotFoundError, OSError):
            pass

        try:
            ctypes.WinDLL(str(dll_path))
        except OSError as exc:
            errors.append(f"DLL non caricabile: {dll_path} ({exc})")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate cx_Freeze output for Solitario Classico Accessibile."
    )
    parser.add_argument("build_dir", type=Path, help="Path to dist/solitario-classico")
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    errors: list[str] = []

    if not build_dir.is_dir():
        print(f"Build directory non trovata: {build_dir}")
        return 1

    _validate_structure(build_dir, errors)
    _validate_pygame_dlls(build_dir, errors)

    if errors:
        print("VALIDAZIONE BUILD FALLITA")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDAZIONE BUILD OK")
    print(f"Build dir: {build_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())