#!/bin/bash
# commit message
export CI=true
export DEBIAN_FRONTEND=noninteractive
export GIT_TERMINAL_PROMPT=0
export GCM_INTERACTIVE=never
export HOMEBREW_NO_AUTO_UPDATE=1
export GIT_EDITOR=:
export EDITOR=:
export VISUAL=''
export GIT_SEQUENCE_EDITOR=:
export GIT_MERGE_AUTOEDIT=no
export GIT_PAGER=cat
export PAGER=cat
export npm_config_yes=true
export PIP_NO_INPUT=1
export YARN_ENABLE_IMMUTABLE_INSTALLS=false

git commit -m "feat: multi-model fallback system and AGENTS.md improvements

- Add multi-model configuration (config.multi-model.json)
  - Primary: ZhipuAI (glm-4-flash) - free tier
  - Secondary: Aliyun Bailian (qwen/glm/kimi) - Coding Plan
  - Tertiary: CodeBuddy Oversea (GPT/Gemini) - for sensitive content
  
- Add model connectivity test scripts
  - test_multi_model.py - basic connectivity test
  - test_multi_model_final.py - comprehensive test with priority
  - test_opencode_models.py - test all opencode providers
  
- Update AGENTS.md - streamline to ~150 lines
- Update CLAUDE.md with new commands and patterns

The multi-model system automatically falls back when:
1. Current model fails 3+ times consecutively
2. API quota exhausted
3. Network errors

Priority order: Zhipu -> Bailian -> CodeBuddy Overseas"
