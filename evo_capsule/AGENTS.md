# AGENTS.md - Evo Capsule Directory

**Generated:** 2026-05-05

## OVERVIEW

EvoMap capsule packaging for custom BabelDOC patches distribution. Contains control character fix and cross-page paragraph handling.

## WHERE TO LOOK

| File | Purpose |
|------|---------|
| `manifest.json` | Capsule manifest (name, version, dependencies) |
| `capsule_info.json` | Capsule metadata and description |
| `content/README.md` | Capsule documentation (problem, solution, patches) |
| `content/pdf_translator.py` | Patched translation core |
| `content/translate_pdf.py` | Patched CLI entry |
| `content/requirements.txt` | Capsule-specific dependencies |
| `content/USAGE.md` | Usage instructions for capsule consumers |
| `content/config/` | Capsule config templates |

## KEY PATCHES
1. **Control Character Cleaning** — removes ASCII 0-31 from JSON input/output to prevent parsing failures
2. **Multi-Model Fallback** — automatic switch on BadRequestError/content_filter
3. **Cross-Page Paragraph Merging** — detects incomplete sentences at page boundaries and merges them

## ANTI-PATTERNS
- Do not modify capsule content without testing against BabelDOC 0.x+
- Capsule patches must be synchronized with root `pdf_translator.py` patches
