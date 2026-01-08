---
name: pre-commit-code-review
description: Comprehensive pre-commit code review for Rust, Python, TypeScript, and Java. Validates compilation, tests, formatting, and security vulnerabilities. Use when reviewing code before commit or checking code quality.
allowed-tools: Bash, Read, Grep, Glob
---

# Pre-Commit Code Review Skill

## Overview

This skill performs strict pre-commit validation including:
1. **Compilation check** - Ensures code compiles without errors
2. **Test execution** - All tests must pass
3. **Format validation** - Zero formatting warnings
4. **Security scan** - No vulnerabilities detected

## Instructions

1. Detect the project language(s) from file extensions
2. Run the appropriate check script from `scripts/`
3. Report ALL issues - do not proceed if any check fails
4. Provide actionable fix suggestions

## Language-Specific Commands

### Rust
```bash
"$CLAUDE_PROJECT_DIR"/.claude/skills/pre-commit-review/scripts/check_rust.sh
```

Python (using uv)
"$CLAUDE_PROJECT_DIR"/.claude/skills/pre-commit-review/scripts/check_python.sh
TypeScript
"$CLAUDE_PROJECT_DIR"/.claude/skills/pre-commit-review/scripts/check_typescript.sh
Java
"$CLAUDE_PROJECT_DIR"/.claude/skills/pre-commit-review/scripts/check_java.sh
Strict Requirements
ALL checks must pass before approving commit
Zero tolerance for warnings in format checks
No known vulnerabilities in dependencies
Report exact file:line for each issue
For detailed examples, see PYTHON_EXAMPLE.md.
For technical reference, see REFERENCE.md.