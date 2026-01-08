---
name: github-actions-generator
description: Generate GitHub Actions workflows for CI/CD pipelines. Supports Rust, Python, TypeScript, Java and more. Includes code review, security scanning, testing, and release workflows. Use when setting up CI/CD, GitHub Actions, or automated workflows.
---

# GitHub Actions Workflow Generator

## Overview
This Skill generates production-ready GitHub Actions workflows for various programming languages, including CI pipelines, security scanning, code review automation, and release workflows.

## Supported Languages

| Language | Template | Features |
|----------|----------|----------|
| Rust | [rust-ci.yml](templates/rust-ci.yml) | Build, test, clippy, fmt, security audit |
| Python | [python-ci.yml](templates/python-ci.yml) | Pytest, ruff, mypy, security scan |
| TypeScript | [typescript-ci.yml](templates/typescript-ci.yml) | Build, test, ESLint, Prettier |
| Java | [java-ci.yml](templates/java-ci.yml) | Maven/Gradle, JUnit, SpotBugs |
| Release | [release.yml](templates/release.yml) | Semantic versioning, changelog, artifacts |

## Instructions

### Step 1: Analyze Project
1. Detect the project's primary language(s)
2. Identify package manager (npm, pip, cargo, maven, etc.)
3. Check for existing test frameworks
4. Review project structure

### Step 2: Select Appropriate Templates
Based on the detected language, use the corresponding template from [templates/](templates/).

### Step 3: Customize Workflow
1. Adjust Node/Python/Java/Rust versions as needed
2. Configure caching strategies
3. Add project-specific build steps
4. Set up environment variables and secrets

### Step 4: Generate Files
Create workflow files in `.github/workflows/` directory.

## Workflow Types

### CI Workflow
- **Triggers**: Push to main/develop, Pull requests
- **Jobs**: Lint, Test, Build, Security scan
- **Matrix**: Multiple OS/language versions

### Release Workflow
- **Triggers**: Tags, Manual dispatch
- **Jobs**: Build, Test, Create release, Upload artifacts

For detailed workflow syntax, see [reference.md](reference.md).
For usage examples, see [examples.md](examples.md).