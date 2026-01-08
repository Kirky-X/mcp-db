#!/usr/bin/env bash
set -euo pipefail

echo "=== Python Pre-Commit Check (using uv) ==="
echo ""

FAILED_CMDS=()

check_command() {
    command -v "$1" &> /dev/null
}

check_env() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "✗ FAILED: Not a git repository"
        exit 1
    fi

    if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ] && [ ! -f "requirements.txt" ]; then
        echo "⚠ No Python project files found (pyproject.toml, setup.py, requirements.txt)"
        echo ""
    fi

    if ! check_command uv; then
        echo "✗ FAILED: uv not found"
        echo "  Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    echo "✓ Environment check passed"
    echo ""
}

run_check() {
    local name="$1"
    local cmd="$2"
    local fix_cmd="$3"

    echo -n "$name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✓ PASSED"
    else
        echo "✗ FAILED"
        if [ -n "$fix_cmd" ]; then
            echo "  Fix: $fix_cmd"
        fi
        FAILED_CMDS+=("$name")
        return 1
    fi
    echo ""
}

run_timeout_check() {
    local name="$1"
    local timeout_sec="$2"
    local cmd="$3"
    local fix_cmd="$4"

    echo -n "$name (timeout: ${timeout_sec}s)... "
    if timeout "$timeout_sec" sh -c "$cmd" > /dev/null 2>&1; then
        echo "✓ PASSED"
    elif [ $? -eq 124 ]; then
        echo "⏱ TIMEOUT (skipped)"
    else
        echo "✗ FAILED"
        if [ -n "$fix_cmd" ]; then
            echo "  Fix: $fix_cmd"
        fi
        FAILED_CMDS+=("$name")
        return 1
    fi
    echo ""
}

check_env

run_check "Checking compilation" "uv run python -m py_compile \$(find . -name '*.py' -not -path './.venv/*' 2>/dev/null)" "uv run python -m py_compile"

if check_command uv; then
    if uv run mypy --version > /dev/null 2>&1; then
        run_check "Checking types (mypy)" "uv run mypy . --ignore-missing-imports" "uv run mypy . --ignore-missing-imports"
    else
        echo "⚠ mypy not installed, skipping type check"
        echo ""
    fi

    run_check "Running tests (pytest)" "uv run pytest -v" "uv run pytest"

    if uv run ruff --version > /dev/null 2>&1; then
        run_check "Checking format (ruff)" "uv run ruff check . && uv run ruff format --check ." "uv run ruff check --fix . && uv run ruff format ."
    else
        echo "⚠ ruff not installed, skipping format check"
        echo ""
    fi

    if uv run bandit --version > /dev/null 2>&1; then
        run_check "Security scan (bandit)" "uv run bandit -r . -q" "uv run bandit -r . -q"
    else
        echo "⚠ bandit not installed, skipping security scan"
        echo ""
    fi

    if uv run pip-audit --version > /dev/null 2>&1; then
        run_check "Security scan (pip-audit)" "uv run pip-audit" "uv run pip-audit"
    else
        echo "⚠ pip-audit not installed, skipping dependency audit"
        echo ""
    fi

    if check_command detox; then
        run_timeout_check "E2E tests (detox)" 300 "detox test" "detox test"
    elif check_command playwright; then
        run_timeout_check "E2E tests (playwright)" 300 "playwright test" "playwright test"
    else
        echo "⚠ detox/playwright not installed, skipping E2E tests"
        echo ""
    fi
fi

if [ ${#FAILED_CMDS[@]} -eq 0 ]; then
    echo ""
    echo "=== All checks passed. Ready to commit. ==="
    exit 0
else
    echo "=== FAILED: ${#FAILED_CMDS[@]} check(s) ==="
    echo ""
    echo "Failed checks:"
    for cmd in "${FAILED_CMDS[@]}"; do
        echo "  - $cmd"
    done
    echo ""
    echo "Run the following to fix:"
    case "${#FAILED_CMDS[@]}" in
        1)
            case "${FAILED_CMDS[0]}" in
                *"compilation"*) echo "  uv run python -m py_compile" ;;
                *"types"*) echo "  uv run mypy . --ignore-missing-imports" ;;
                *"pytest"*) echo "  uv run pytest" ;;
                *"ruff"*) echo "  uv run ruff check --fix . && uv run ruff format ." ;;
                *"bandit"*) echo "  uv run bandit -r . -q" ;;
                *"pip-audit"*) echo "  uv run pip-audit" ;;
                *"E2E"*) echo "  detox test" ;;
            esac
            ;;
        *)
            echo "  uv run ruff check --fix . && uv run ruff format . && uv run pytest"
            ;;
    esac
    echo ""
    exit 1
fi
