# EvoMap Capsule Evaluation: PDF Translation with BabelDOC Patches

## Capsule Suitability: ✅ HIGHLY SUITABLE

### Why This Makes a Good EvoMap Capsule

1. **Reusable Pattern**: The patches we developed solve common BabelDOC/pdf2zh issues that many users encounter
2. **Well-Defined Problem**: Control characters causing JSON parsing failures is a specific, reproducible issue
3. **Documented Solution**: Complete with code patches, tests, and usage examples
4. **Self-Contained**: Can be packaged as a capsule with all necessary components

### Capsule Components

**Core Innovation**:
- `_apply_babeldoc_patch()` - Monkey-patches BabelDOC's `_clean_json_output` to remove control characters
- `_apply_babeldoc_fallback_patch()` - Multi-model fallback for content filter errors
- `_is_incomplete_sentence()` + `patch_babeldoc_cross_page()` - Cross-page paragraph merging

**Key Features**:
1. **Control Character Cleaning** - Fixes `\x00-\x1f` control chars that break JSON parsing
2. **Multi-Model Fallback** - Auto-switch models on API errors
3. **Cross-Page Paragraph Merging** - Intelligently joins paragraphs split across pages
4. **Progress Callbacks** - Real-time translation progress

### Target Audience

- AI Agent developers needing PDF translation
- Users of BabelDOC/pdf2zh experiencing control character issues
- Researchers translating academic papers

### Comparison: Our Solution vs Existing

| Feature | pdf2zh-next-mcp | Our Solution |
|---------|----------------|--------------|
| Architecture | MCP Server | Python Library |
| Requires Service | Yes | No |
| Multi-Model Fallback | ❌ | ✅ |
| Control Char Handling | ❌ | ✅ |
| Cross-Page Merging | ❌ | ✅ |
| Progress Callbacks | ❌ | ✅ |

### Capsule Structure

```
pdf-translation-capsule/
├── manifest.json           # EvoMap metadata
├── pdf_translator.py       # Core library with patches
├── SKILL.md               # Usage documentation
├── config/
│   ├── config.example.json
│   ├── config.zhipu.json
│   └── config.openai.json
└── test/
    └── test_clean_json_output.py
```

### Usage Pattern (Capsule Consumer)

```python
# Import the patched translator
from pdf_translation_capsule import PDFTranslator

# Config with fallback models
config = {
    "models": [
        {"name": "primary", "api_key": "...", "model": "glm-4-flash"},
        {"name": "backup", "api_key": "...", "model": "gpt-4o-mini"}
    ],
    "fallback": {"consecutive_failures": 3}
}

# Translate with automatic fallback
translator = PDFTranslator(config_dict=config)
result = translator.translate_pdf("paper.pdf", output_dir="./output")
```

### Recommendation

**YES, publish to EvoMap.** This capsule provides:
1. A battle-tested solution to real BabelDOC issues
2. Unique features not available in existing tools
3. Easy integration for AI agents
4. Clear documentation and examples

The control character patch alone justifies the capsule - it's a common problem with no existing solution in the BabelDOC ecosystem.
