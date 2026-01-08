#!/usr/bin/env bash
set -euo pipefail

echo "=== Rust Pre-Commit Check ==="
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

    if [ ! -f "Cargo.toml" ]; then
        echo "✗ FAILED: Cargo.toml not found"
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

run_check_with_output() {
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

run_check_output() {
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

if check_command rustfmt; then
    run_check "Checking format (rustfmt)" "cargo fmt -- --check" "cargo fmt"
else
    echo "⚠ rustfmt not installed, skipping format check"
    echo "  Install: rustup component add rustfmt"
    echo ""
fi

if check_command cargo-clippy; then
    run_check "Running clippy" "cargo clippy -- -D warnings" "cargo clippy --fix"
else
    echo "⚠ clippy not installed, skipping lint check"
    echo "  Install: rustup component add clippy"
    echo ""
fi

run_check "Checking compilation" "cargo build" "cargo build"

run_check "Running tests" "cargo test" "cargo test"

if check_command cargo-deny; then
    run_check "Security audit (cargo-deny)" "cargo deny check" "cargo deny check"
else
    if check_command cargo-audit; then
        run_check "Security audit (cargo-audit)" "cargo audit" "cargo audit"
    else
        echo "⚠ cargo-deny/cargo-audit not installed, skipping security audit"
        echo "  Install: cargo install cargo-deny"
        echo ""
    fi
fi

if check_command cargo-tarpaulin; then
    run_timeout_check "Code coverage" 300 "cargo tarpaulin --timeout 120 --out Stdout" "cargo tarpaulin"
else
    echo "⚠ cargo-tarpaulin not installed, skipping coverage check"
    echo "  Install: cargo install cargo-tarpaulin"
    echo ""
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
                *"format"*) echo "  cargo fmt" ;;
                *"clippy"*) echo "  cargo clippy --fix" ;;
                *"compilation"*) echo "  cargo build" ;;
                *"tests"*) echo "  cargo test" ;;
                *"cargo-deny"*) echo "  cargo deny check" ;;
                *"cargo-audit"*) echo "  cargo audit" ;;
            esac
            ;;
        *)
            echo "  cargo fmt && cargo clippy --fix && cargo test"
            ;;
    esac
    echo ""
    exit 1
fi
