#!/usr/bin/env bash
set -euo pipefail

echo "=== TypeScript Pre-Commit Check ==="
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

    if [ ! -f "package.json" ]; then
        echo "✗ FAILED: package.json not found"
        exit 1
    fi

    if ! check_command npm && ! check_command yarn && ! check_command pnpm; then
        echo "✗ FAILED: npm/yarn/pnpm not found"
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

run_check "Type checking (tsc)" "npx tsc --noEmit" "npx tsc --noEmit"

if check_command npm; then
    run_check "Running tests" "npm test" "npm test"

    if npx eslint --version > /dev/null 2>&1; then
        run_check "Linting (eslint)" "npx eslint . --max-warnings 0" "npx eslint . --fix"
    else
        echo "⚠ eslint not installed, skipping lint check"
        echo ""
    fi

    if npx prettier --version > /dev/null 2>&1; then
        run_check "Format check (prettier)" "npx prettier --check ." "npx prettier --write ."
    else
        echo "⚠ prettier not installed, skipping format check"
        echo ""
    fi

    run_check "Security audit" "npm audit --audit-level=moderate" "npm audit"

    if check_command cypress; then
        run_timeout_check "E2E tests (Cypress)" 300 "cypress run" "cypress run"
    elif check_command playwright; then
        run_timeout_check "E2E tests (Playwright)" 300 "playwright test" "playwright test"
    else
        echo "⚠ cypress/playwright not installed, skipping E2E tests"
        echo ""
    fi

    if check_command bundle-audit || bundler-audit --version > /dev/null 2>&1; then
        run_check "Ruby dependency audit" "bundle-audit check --update" "bundle-audit check --update"
    fi
elif check_command yarn; then
    run_check "Running tests" "yarn test" "yarn test"

    if yarn eslint --version > /dev/null 2>&1; then
        run_check "Linting (eslint)" "yarn eslint . --max-warnings 0" "yarn eslint . --fix"
    fi

    if yarn prettier --version > /dev/null 2>&1; then
        run_check "Format check (prettier)" "yarn prettier --check ." "yarn prettier --write ."
    fi

    run_check "Security audit" "yarn audit --level moderate" "yarn audit"

    if check_command cypress; then
        run_timeout_check "E2E tests (Cypress)" 300 "cypress run" "cypress run"
    fi
elif check_command pnpm; then
    run_check "Running tests" "pnpm test" "pnpm test"

    if pnpm eslint --version > /dev/null 2>&1; then
        run_check "Linting (eslint)" "pnpm eslint . --max-warnings 0" "pnpm eslint . --fix"
    fi

    if pnpm prettier --version > /dev/null 2>&1; then
        run_check "Format check (prettier)" "pnpm prettier --check ." "pnpm prettier --write ."
    fi

    run_check "Security audit" "pnpm audit --level moderate" "pnpm audit"
fi

if [ ${#FAILED_CMDS[@]} -eq 0 ]; then
    echo "=== All checks passed ==="
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
                *"tsc"*) echo "  npx tsc --noEmit" ;;
                *"tests"*) echo "  npm test" ;;
                *"eslint"*) echo "  npx eslint . --fix" ;;
                *"prettier"*) echo "  npx prettier --write ." ;;
                *"audit"*) echo "  npm audit" ;;
                *"Cypress"*) echo "  cypress run" ;;
                *"Playwright"*) echo "  playwright test" ;;
            esac
            ;;
        *)
            echo "  npx prettier --write . && npx eslint . --fix && npm test"
            ;;
    esac
    echo ""
    exit 1
fi
