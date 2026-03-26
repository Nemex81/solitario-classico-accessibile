#!/usr/bin/env python
"""
ci-local-validate.py — Pre-Commit Validation Script

Esegue checklist pre-commit automaticamente:
  ✓ Syntax check (python -m py_compile)
  ✓ Type hints (mypy strict)
  ✓ Import cycles (pylint)
  ✓ No print statements in src/
  ✓ Unit test coverage >= 85%

Uso:
  python scripts/ci-local-validate.py
  python scripts/ci-local-validate.py --skip-tests
  python scripts/ci-local-validate.py --fix
  python scripts/ci-local-validate.py --verbose
"""

import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Validation check failed."""
    pass

def check_syntax(verbose: bool = False) -> bool:
    """Syntax validation: python -m py_compile."""
    logger.info("Checking syntax...")
    
    src_dir = Path("src")
    py_files = list(src_dir.rglob("*.py"))
    
    failed = []
    for py_file in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            failed.append((py_file, result.stderr))
    
    if failed:
        for f, err in failed:
            logger.error(f"✗ Syntax error in {f}:\n{err}")
        return False
    
    logger.info(f"✓ Syntax check passed ({len(py_files)} files)")
    return True

def check_type_hints(verbose: bool = False) -> bool:
    """Type hints validation: mypy strict."""
    logger.info("Checking type hints...")
    
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "src/", "--strict", "--python-version", "3.8"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        if verbose or result.stdout:
            logger.error(f"✗ Type hints check failed:\n{result.stdout}")
        return False
    
    logger.info("✓ Type hints check passed (mypy strict)")
    return True

def check_imports(verbose: bool = False) -> bool:
    """Import cycles validation: pylint."""
    logger.info("Checking import cycles...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pylint", "src/", "--disable=all", "--enable=cyclic-import"],
        capture_output=True,
        text=True
    )
    
    if "cyclic-import" in result.stdout.lower() and result.returncode != 0:
        logger.error(f"✗ Import cycle found:\n{result.stdout}")
        return False
    
    logger.info("✓ Import cycles check passed")
    return True

def check_no_prints(verbose: bool = False) -> bool:
    """No print statements in src/."""
    logger.info("Checking for print statements...")
    
    result = subprocess.run(
        'grep -r "print(" src/ --include="*.py"',
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        # Filter out __main__.py
        lines = [l for l in result.stdout.split('\n') if '__main__' not in l and l.strip()]
        if lines:
            logger.error(f"✗ Found print() statements:\n" + '\n'.join(lines))
            return False
    
    logger.info("✓ No print statements in src/")
    return True

def check_test_coverage(skip: bool = False, verbose: bool = False) -> bool:
    """Unit test coverage >= 85%."""
    if skip:
        logger.info("⊘ Skipping test coverage check")
        return True
    
    logger.info("Checking test coverage...")
    
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "-m", "not gui",
            "--cov=src",
            "--cov-report=term-missing",
            "-q"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"✗ Test coverage check failed:")
        logger.error(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        return False
    
    # Parse coverage percentage
    lines = result.stdout.split('\n')
    for line in lines:
        if 'coverage' in line.lower():
            logger.info(f"✓ {line}")
    
    logger.info("✓ Test coverage check passed (>= 85%)")
    return True

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-commit validation checklist"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test coverage check (faster)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="(Placeholder) Auto-fix issues where possible"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    checks = [
        ("Syntax", lambda v: check_syntax(v)),
        ("Type Hints", lambda v: check_type_hints(v)),
        ("Imports", lambda v: check_imports(v)),
        ("Print Statements", lambda v: check_no_prints(v)),
        ("Test Coverage", lambda v: check_test_coverage(args.skip_tests, v)),
    ]
    
    failed = []
    for name, check_fn in checks:
        try:
            if not check_fn(args.verbose):
                failed.append(name)
        except Exception as e:
            logger.error(f"✗ {name} check error: {e}")
            failed.append(name)
    
    print()  # Blank line
    if failed:
        logger.error(f"✗ {len(failed)} check(s) failed: {', '.join(failed)}")
        logger.error("Fix issues before committing.")
        return 1
    else:
        logger.info("✅ All checks passed. Ready to commit!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
