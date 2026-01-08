# Project Documentation Examples

This file provides concrete examples of using the doc-generator Skill.

## Example 1: Generate Full Documentation Suite

**User Request**:
```
Generate all documentation for this project
```

**Claude Response**:
"What language would you like the documentation to be generated in?"

**User Response**:
```
Chinese
```

**Generated Files**:
- `README.md` (English)
- `README_zh.md` (Chinese)
- `CONTRIBUTING.md` (Chinese)
- `ARCHITECTURE.md` (Chinese)
- `API_REFERENCE.md` (Chinese)

---

## Example 2: Generate README Only

**User Request**:
```
Create a README for this project in Japanese
```

**Generated Files**:
- `README.md` (English)
- `README_ja.md` (Japanese)

---

## Example 3: Generate API Documentation

**User Request**:
```
Generate API reference documentation in Spanish
```

**Generated Files**:
- `API_REFERENCE.md` (Spanish)

---

## Example 4: Generate Architecture Documentation

**User Request**:
```
Create architecture documentation for this project in German
```

**Generated Files**:
- `ARCHITECTURE.md` (German)

---

## Example 5: Update Existing Documentation

**User Request**:
```
Update the README to include the new authentication feature, keep it in French
```

**Generated Files**:
- `README.md` (English - updated)
- `README_fr.md` (French - updated)

---

## Language Code Reference

| Language | Code | README Filename |
|----------|------|-----------------|
| Chinese | zh | README_zh.md |
| Japanese | ja | README_ja.md |
| Korean | ko | README_ko.md |
| Spanish | es | README_es.md |
| French | fr | README_fr.md |
| German | de | README_de.md |
| Portuguese | pt | README_pt.md |
| Russian | ru | README_ru.md |

---

## Sample Output Structure

After running the Skill with Chinese as the target language:
```
project/
├── README.md # English (always generated)
├── README_zh.md # Chinese
├── CONTRIBUTING.md # Chinese
├── ARCHITECTURE.md # Chinese
└── API_REFERENCE.md # Chinese
```
---

## Tips

1. **Always specify the language** when asked - this ensures consistent documentation
2. **README is always bilingual** - English version is required for international accessibility
3. **Other docs follow user preference** - CONTRIBUTING, ARCHITECTURE, API docs use specified language only
4. **Be specific about scope** - mention which documents you need if you don't want the full suite