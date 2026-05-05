# AGENTS.md - Config Directory

**Generated:** 2026-05-05

## OVERVIEW

JSON configuration templates for multiple translation engine providers. All use OpenAI-compatible API abstraction.

## WHERE TO LOOK

| File | Purpose |
|------|---------|
| `config.json` | Active config (gitignored, contains real API keys) |
| `config.example.json` | Full template with multi-model fallback support |
| `config.zhipu.json` | ZhipuAI/GLM-4-Flash (recommended, free) |
| `config.openai.json` | OpenAI native |
| `config.siliconflow.json` | SiliconFlow/DeepSeek |
| `config.volcengine.json` | VolcEngine/Doubao (PRO) |
| `config.test.json` | Test config with placeholder API key |
| `config.multi-model.json` | Multi-model fallback configuration |
| `config.bailian-only.json` | Alibaba Bailian single-provider |
| `config.foreign-only.json` | Foreign language source optimization |

## SCHEMA

```json
{
  "translation_engine": "openai",
  "openai_api_key": "your-key",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_model": "glm-4-flash",
  "qps": 4,
  "min_text_length": 5,
  "debug": false,
  "custom_system_prompt": null
}
```

## ANTI-PATTERNS
- Never commit `config.json` (gitignored, contains real keys)
- Never use empty strings for API key placeholders — use `"your-api-key-here"`
- Multi-model config uses `"models": [{...}]` array, not separate top-level fields
