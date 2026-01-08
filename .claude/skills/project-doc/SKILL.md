---
name: project-doc
description: Generate project documentation including README, CONTRIBUTING, ARCHITECTURE, and API reference. Use when creating, updating, or generating project documentation.
---

# Documentation Generator

## Overview
This Skill generates consistent, high-quality project documentation.

## Available Templates

| Template | Purpose |
|----------|---------|
| [README.md](templates/README.md) | Main project documentation |
| [CONTRIBUTING.md](templates/CONTRIBUTING.md) | Contribution guidelines |
| [ARCHITECTURE.md](templates/ARCHITECTURE.md) | Architecture design document |
| [architecture-template.md](templates/architecture-template.md) | Simplified architecture template |
| [api-spec-template.md](templates/api-spec-template.md) | API specification template |
| [API_REFERENCE.md](templates/API_REFERENCE.md) | API reference documentation |

## Instructions

### Step 1: Ask for Target Language
**IMPORTANT**: Before generating any documentation, you MUST ask the user:

> "What language would you like the documentation to be generated in? (e.g., Chinese/中文, Japanese/日本語, Spanish/Español, etc.)"

Wait for the user's response before proceeding.

### Step 2: Generate README (Always English + Localized)
README files are ALWAYS generated in two versions:
1. `README.md` - English version (required)
2. `README_{lang}.md` - Localized version (e.g., `README_zh.md` for Chinese)

**Process**:
1. Read [templates/README.md](templates/README.md)
2. Analyze project structure and codebase
3. Generate `README.md` in English
4. Generate `README_{lang}.md` in the user's specified language

### Step 3: Generate Other Documents (User's Language)
All other documents are generated in the user's specified language ONLY.

#### CONTRIBUTING
1. Read [templates/CONTRIBUTING.md](templates/CONTRIBUTING.md)
2. Generate `CONTRIBUTING.md` in the specified language
3. Include code standards, PR process, issue templates

#### Architecture Documentation
1. Read [templates/ARCHITECTURE.md](templates/ARCHITECTURE.md) or [templates/architecture-template.md](templates/architecture-template.md)
2. Analyze project directory structure and core modules
3. Generate architecture diagrams (ASCII or Mermaid)
4. Document data flow and key design decisions
5. Output in the specified language

#### API Documentation
1. Read [templates/api-spec-template.md](templates/api-spec-template.md) or [templates/API_REFERENCE.md](templates/API_REFERENCE.md)
2. Scan codebase for API endpoints/functions
3. Extract parameters, return values, examples
4. Output in the specified language

## Language Code Reference

| Language | File Suffix |
|----------|-------------|
| Chinese | `_zh` |
| Japanese | `_ja` |
| Korean | `_ko` |
| Spanish | `_es` |
| French | `_fr` |
| German | `_de` |
| Portuguese | `_pt` |
| Russian | `_ru` |

## Example Workflow

**User**: "Generate documentation for this project"

**Claude**: "What language would you like the documentation to be generated in?"

**User**: "Chinese"

**Claude generates**:
- `README.md` (English)
- `README_zh.md` (Chinese)
- `CONTRIBUTING.md` (Chinese)
- `ARCHITECTURE.md` (Chinese)
- `API_REFERENCE.md` (Chinese)

## Notes

- Always understand project context before generating
- Keep documentation in sync with code
- Use clear and concise language
- Include runnable code examples
- README must always have an English version for international accessibility