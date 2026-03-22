#!/bin/bash
# Pre-commit Hook Template
# 
# Salva come: .git/hooks/pre-commit
# Rendi eseguibile: chmod +x .git/hooks/pre-commit
#
# Eseguito automaticamente prima di ogni git commit.
# Per disabilitare: git commit --no-verify

set -e  # Exit on first error

PROJECT_ROOT="$(cd "$(dirname "$0")/../../" && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Running pre-commit validation checks..."
echo "=========================================="

# 1. Syntax Check
echo ""
echo "[1/5] Syntax validation..."
if ! python -m py_compile src/**/*.py 2>/dev/null; then
    # Try alternative find command for Windows
    if ! find src -name "*.py" -exec python -m py_compile {} \; 2>/dev/null; then
        echo "✗ Syntax check failed"
        exit 1
    fi
fi
echo "✓ Syntax check passed"

# 2. Type Hints Check (mypy)
echo ""
echo "[2/5] Type hints validation (mypy)..."
if ! python -m mypy src/ --strict --python-version 3.8 2>/dev/null ; then
    echo "✗ Type hints check failed (run: mypy src/ --strict for details)"
    exit 1
fi
echo "✓ Type hints check passed"

# 3. Import Cycles Check (pylint)
echo ""
echo "[3/5] Import cycles validation..."
if python -m pylint src/ --disable=all --enable=cyclic-import 2>&1 | grep -i "cyclic-import"; then
    echo "✗ Import cycle detected"
    exit 1
fi
echo "✓ Import cycles check passed"

# 4. No Print Statements
echo ""
echo "[4/5] Print statements check..."
PRINT_COUNT=$(grep -r "print(" src/ --include="*.py" | grep -v "__main__" | wc -l)
if [ "$PRINT_COUNT" -gt 0 ]; then
    echo "✗ Found $PRINT_COUNT print() statement(s) in src/"
    echo "   Use logging instead: from src.infrastructure.logging import categorized_logger"
    grep -r "print(" src/ --include="*.py" | grep -v "__main__" | head -5
    exit 1
fi
echo "✓ No print statements found"

# 5. Unit Tests & Coverage
echo ""
echo "[5/5] Unit tests & coverage..."
if ! python -m pytest -m "not gui" --cov=src --cov-report=term-missing --cov-fail-under=85 -q 2>/dev/null; then
    echo "✗ Test coverage check failed (target: >= 85%)"
    echo "   Run: pytest -m \"not gui\" --cov=src --cov-report=html"
    exit 1
fi
echo "✓ Test coverage check passed"

echo ""
echo "=========================================="
echo "✅ All pre-commit checks passed!"
echo "=========================================="
echo ""

exit 0
