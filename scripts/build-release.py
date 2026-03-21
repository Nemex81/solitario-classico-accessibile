#!/usr/bin/env python
"""
build-release.py — Build Executable con cx_freeze, Versioning, Packaging

Esegue:
  - Aggiorna versione in pyproject.toml
  - Build cx_freeze → dist/solitario-classico/solitario.exe
  - Genera checksum SHA256
  - Crea MANIFEST.txt con dependencies

Uso:
  python scripts/build-release.py --version 3.6.0
  python scripts/build-release.py --version 3.6.0 --skip-test
  python scripts/build-release.py --clean
"""

import sys
import subprocess
import argparse
import logging
import hashlib
from pathlib import Path
import json
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def read_pyproject() -> dict:
    """Leggi pyproject.toml."""
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            logger.error("tomli not installed. Install: pip install tomli")
            return {}
    
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        logger.error("pyproject.toml not found")
        return {}
    
    with open(pyproject_path, 'rb') as f:
        return tomllib.load(f)

def update_version_in_pyproject(version: str) -> bool:
    """Aggiorna versione in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        logger.error("pyproject.toml not found")
        return False
    
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rimpiazza pattern version = "X.Y.Z"
    import re
    new_content = re.sub(
        r'version\s*=\s*["\'][\d.]+["\']',
        f'version = "{version}"',
        content
    )
    
    if new_content == content:
        logger.warning("Version not found in pyproject.toml (check format)")
        return False
    
    with open(pyproject_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info(f"✓ Updated pyproject.toml to version {version}")
    return True

def run_tests() -> bool:
    """Esegui unit tests (pre-release gate)."""
    logger.info("Running tests...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-m", "not gui", "-v"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error("✗ Tests failed:")
        logger.error(result.stdout)
        return False
    
    logger.info("✓ Tests passed")
    return True

def clean_build_artifacts() -> None:
    """Pulisci build artefatti vecchi."""
    logger.info("Cleaning old build artifacts...")
    
    paths_to_clean = [
        Path("build"),
        Path("dist"),
        Path("*.egg-info"),
    ]
    
    for pattern in paths_to_clean:
        if isinstance(pattern, str):
            for p in Path(".").glob(pattern):
                if p.is_dir():
                    subprocess.run(["rm", "-rf", str(p)])
                else:
                    p.unlink()
    
    logger.info("✓ Build artifacts cleaned")

def build_cx_freeze(version: str, output_dir: Optional[str] = None) -> bool:
    """Build cx_freeze executable."""
    logger.info(f"Building cx_freeze package (v{version})...")
    
    # Assume setup.py esiste e configura cx_freeze
    result = subprocess.run(
        [sys.executable, "setup.py", "build_exe"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error("✗ cx_freeze build failed:")
        logger.error(result.stdout)
        logger.error(result.stderr)
        return False
    
    logger.info("✓ cx_freeze build succeeded")
    
    # Verify executable exists
    exe_path = Path("dist/solitario-classico/solitario.exe")
    if not exe_path.exists():
        logger.warning(f"Executable not found at {exe_path}")
        return False
    
    logger.info(f"✓ Executable ready: {exe_path} ({exe_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return True

def generate_checksum(version: str) -> bool:
    """Genera SHA256 checksum per executable."""
    logger.info("Generating SHA256 checksum...")
    
    exe_path = Path("dist/solitario-classico/solitario.exe")
    if not exe_path.exists():
        logger.error(f"Executable not found: {exe_path}")
        return False
    
    # Calcola SHA256
    sha256 = hashlib.sha256()
    with open(exe_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    
    checksum = sha256.hexdigest()
    
    # Scrivi checksum file
    checksum_path = Path(f"dist/solitario-classico/solitario.exe.sha256")
    with open(checksum_path, 'w') as f:
        f.write(f"{checksum}  solitario.exe\n")
    
    logger.info(f"✓ Checksum: {checksum_path}")
    logger.info(f"  SHA256: {checksum[:16]}...")
    return True

def create_manifest(version: str) -> bool:
    """Crea MANIFEST.txt con list dependencies."""
    logger.info("Creating MANIFEST.txt...")
    
    manifest_path = Path("dist/solitario-classico/MANIFEST.txt")
    
    # Ottieni dependencies da requirements.txt
    req_path = Path("requirements.txt")
    dependencies = []
    
    if req_path.exists():
        with open(req_path, 'r') as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Scrivi MANIFEST
    manifest_content = f"""Solitario Classico Accessibile
Version: {version}
Build Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== PACKAGE CONTENTS ===
- solitario.exe (Main executable)
- solitario.exe.sha256 (SHA256 checksum)

=== DEPENDENCIES ===
"""
    
    for dep in dependencies:
        manifest_content += f"- {dep}\n"
    
    manifest_content += f"""
=== INSTALLATION ===
Extract dist/solitario-classico/ and run solitario.exe

=== ACCESSIBILITY ===
This application is fully keyboard-accessible and screen-reader compatible (NVDA/JAWS).

=== SYSTEM REQUIREMENTS ===
- Windows 10+ (x64)
- Screen reader (NVDA, JAWS, or similar) for accessibility

=== LICENSE ===
See LICENSE.md in source repository
"""
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    logger.info(f"✓ Manifest created: {manifest_path}")
    return True

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build release executable with cx_freeze"
    )
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Version number (e.g., 3.6.0)"
    )
    parser.add_argument(
        "--skip-test",
        action="store_true",
        help="Skip unit tests before build"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts and exit"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="dist/solitario-classico/",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts()
        return 0
    
    # Validate version format
    if not all(part.isdigit() for part in args.version.split('.')):
        logger.error(f"Invalid version format: {args.version}")
        return 1
    
    logger.info(f"Building release v{args.version}...")
    
    # Update version in pyproject.toml
    if not update_version_in_pyproject(args.version):
        logger.error("Failed to update version")
        return 1
    
    # Run tests
    if not args.skip_test:
        if not run_tests():
            logger.error("Tests failed. Fix before release.")
            return 1
    
    # Clean old artifacts
    clean_build_artifacts()
    
    # Build cx_freeze
    if not build_cx_freeze(args.version, args.output):
        return 1
    
    # Generate checksum
    if not generate_checksum(args.version):
        logger.error("Failed to generate checksum")
        return 1
    
    # Create manifest
    if not create_manifest(args.version):
        logger.error("Failed to create manifest")
        return 1
    
    print("\n" + "="*60)
    print(f"✅ Release v{args.version} built successfully!")
    print("="*60)
    print(f"\nOutputs:")
    print(f"  Executable: dist/solitario-classico/solitario.exe")
    print(f"  Checksum:   dist/solitario-classico/solitario.exe.sha256")
    print(f"  Manifest:   dist/solitario-classico/MANIFEST.txt")
    print(f"\nNext steps:")
    print(f"  1. git tag v{args.version}")
    print(f"  2. git push origin main")
    print(f"  3. git push origin v{args.version}")
    print(f"  4. Create GitHub Release + upload artifacts\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
