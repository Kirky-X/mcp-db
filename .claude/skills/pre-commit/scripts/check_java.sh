#!/usr/bin/env bash
set -euo pipefail

echo "=== Java Pre-Commit Check ==="
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

    if [ ! -f "pom.xml" ] && [ ! -f "build.gradle" ]; then
        echo "✗ FAILED: pom.xml or build.gradle not found"
        exit 1
    fi

    if ! check_command mvn && ! check_command ./gradlew; then
        echo "✗ FAILED: Maven or Gradle not found"
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

check_env

if [ -f "pom.xml" ] || check_command mvn; then
    run_check "Compiling" "mvn compile -q" "mvn compile"
    run_check "Running tests" "mvn test -q" "mvn test"
    run_check "Format check (Spotless)" "mvn spotless:check -q" "mvn spotless:apply"

    if check_command mvn; then
        if mvn spotbugs:check > /dev/null 2>&1; then
            run_check "Static analysis (SpotBugs)" "mvn spotbugs:check -q" "mvn spotbugs:check"
        else
            run_check "Static analysis (SpotBugs)" "mvn spotbugs:check -q" "mvn spotbugs:check"
        fi
        run_check "Security scan (OWASP)" "mvn dependency-check:check -q" "mvn dependency-check:check"
    else
        echo "⚠ Maven not installed, skipping SpotBugs and OWASP checks"
        echo ""
    fi
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] || check_command ./gradlew; then
    run_check "Compiling" "./gradlew compileJava --quiet" "./gradlew compileJava"
    run_check "Running tests" "./gradlew test --quiet" "./gradlew test"
    run_check "Format check" "./gradlew spotlessCheck --quiet" "./gradlew spotlessApply"
    run_check "Static analysis" "./gradlew checkstyleMain --quiet" "./gradlew checkstyleMain"

    if check_command gradle; then
        run_check "Security scan (dependency-check)" "gradle dependencyCheckAnalyze --quiet" "gradle dependencyCheckAnalyze"
    fi
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
                *"compiling"*) echo "  mvn compile" ;;
                *"tests"*) echo "  mvn test" ;;
                *"format"*) echo "  mvn spotless:apply" ;;
                *"static"*) echo "  mvn spotbugs:check" ;;
                *"security"*) echo "  mvn dependency-check:check" ;;
            esac
            ;;
        *)
            echo "  mvn compile && mvn test && mvn spotless:apply"
            ;;
    esac
    echo ""
    exit 1
fi
