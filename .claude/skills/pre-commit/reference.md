# Technical Reference

## Tool Requirements by Language

| Language   | Compiler/Runtime | Test | Format | Security |
|------------|------------------|------|--------|----------|
| Rust       | cargo build      | cargo test | cargo fmt --check | cargo audit |
| Python     | uv run python -m py_compile | uv run pytest | uv run ruff check + ruff format --check | uv run bandit + pip-audit |
| TypeScript | tsc --noEmit     | npm test | prettier --check + eslint | npm audit |
| Java       | mvn compile      | mvn test | mvn spotless:check | mvn dependency-check:check |

## Exit Codes

- `0` - All checks passed
- `1` - Compilation failed
- `2` - Tests failed
- `3` - Format issues found
- `4` - Security vulnerabilities detected

## Environment Variables

- `STRICT_MODE=1` - Treat warnings as errors
- `SKIP_SECURITY=0` - Never skip security checks