# Python Pre-Commit Example

## Project Setup

```bash
# Initialize with uv
uv init my-project
cd my-project
uv add --dev pytest ruff bandit pip-audit mypy
```

## Running Checks

```bash
# Full check
.claude/skills/pre-commit-review/scripts/check_python.sh
```

**Expected output on success:**
- ✓ Compilation: PASSED
- ✓ Tests: PASSED (15 tests)
- ✓ Format: PASSED (ruff check + ruff format)
- ✓ Security: PASSED (bandit + pip-audit)
- All checks passed. Ready to commit.

## Common Issues

### Format Errors

```bash
# Fix with:
uv run ruff check --fix .
uv run ruff format .
```

### Security Vulnerabilities

```bash
# View details:
uv run bandit -r src/ -f json
uv run pip-audit --format json
```
