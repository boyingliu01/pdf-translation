#!/usr/bin/env python3
"""测试 opencode.json 中配置的所有模型"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import httpx
from pathlib import Path

# 加载配置
CONFIG_PATH = Path.home() / ".opencode" / "opencode.json"


def load_config():
    """加载 opencode.json 配置"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_model(provider_name, provider_config, model_name):
    """测试单个模型"""
    base_url = provider_config["options"]["baseURL"]
    api_key = provider_config["options"]["apiKey"]

    chat_url = base_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": "Say 'Hello' in Chinese. Reply with just the translation.",
            }
        ],
        "temperature": 0.3,
        "max_tokens": 50,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(chat_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                return {"success": True, "status": 200, "response": content[:50]}
            elif response.status_code == 429:
                return {"success": False, "status": 429, "error": "Quota exceeded"}
            else:
                error = response.text[:100] if response.text else "Unknown error"
                return {
                    "success": False,
                    "status": response.status_code,
                    "error": error,
                }
    except httpx.TimeoutException:
        return {"success": False, "status": "timeout", "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)[:100]}


def test_all_models():
    """测试所有模型"""
    config = load_config()
    providers = config.get("provider", {})

    print(f"\n{'=' * 70}")
    print(f"测试模型配置")
    print(f"配置文件: {CONFIG_PATH}")
    print(f"Provider数量: {len(providers)}")
    print(f"{'=' * 70}\n")

    results = []

    for provider_name, provider_config in providers.items():
        models = provider_config.get("models", {})
        print(f"\n{'─' * 70}")
        print(f"Provider: {provider_name}")
        print(f"Base URL: {provider_config['options']['baseURL']}")
        print(f"Models: {len(models)}")
        print(f"{'─' * 70}")

        for model_name in models.keys():
            print(f"  测试 {model_name}...", end=" ")
            result = test_model(provider_name, provider_config, model_name)
            results.append({"provider": provider_name, "model": model_name, **result})

            if result["success"]:
                print(f"✓ 200 ({result['response']})")
            elif result["status"] == 429:
                print(f"○ 429 (配额已用完)")
            else:
                print(f"✗ {result['status']} ({result.get('error', '')[:30]}...)")

    # 总结
    print(f"\n{'=' * 70}")
    print("测试结果总结:")
    success = [r for r in results if r["success"]]
    quota_exceeded = [r for r in results if r["status"] == 429]
    failed = [r for r in results if not r["success"] and r["status"] != 429]

    print(f"  ✓ 可用: {len(success)}/{len(results)}")
    print(f"  ○ 配额用完: {len(quota_exceeded)}/{len(results)}")
    print(f"  ✗ 失败: {len(failed)}/{len(results)}")
    print(f"{'=' * 70}")

    # 按provider分组显示
    print("\n按 Provider 分组:")
    for provider_name in providers.keys():
        provider_results = [r for r in results if r["provider"] == provider_name]
        provider_success = [r for r in provider_results if r["success"]]
        provider_quota = [r for r in provider_results if r["status"] == 429]
        print(f"\n  {provider_name}:")
        print(f"    可用: {len(provider_success)}/{len(provider_results)}")
        print(f"    配额用完: {len(provider_quota)}/{len(provider_results)}")
        for r in provider_results:
            if r["success"]:
                print(f"      ✓ {r['model']}")
            elif r["status"] == 429:
                print(f"      ○ {r['model']} (配额已用完)")

    return results


def generate_multi_model_config(results):
    """基于测试结果生成多模型配置文件"""
    config = load_config()
    providers = config.get("provider", {})

    models_config = []

    # 优先选择国外模型（codebuddy-oversea）用于处理敏感词
    # 然后是国内模型作为备用
    priority_order = ["codebuddy-oversea", "bailian-coding-plan", "volcengine-plan"]

    for provider_name in priority_order:
        if provider_name not in providers:
            continue

        provider_config = providers[provider_name]
        base_url = provider_config["options"]["baseURL"]
        api_key = provider_config["options"]["apiKey"]

        provider_results = [
            r for r in results if r["provider"] == provider_name and r["success"]
        ]
        quota_results = [
            r for r in results if r["provider"] == provider_name and r["status"] == 429
        ]

        # 选择最佳模型
        selected_models = []

        if provider_name == "codebuddy-oversea":
            # 国外模型优先级：GPT-5 > Gemini > DeepSeek
            priority_models = [
                "gpt-5.4",
                "gpt-5.3-codex",
                "gpt-5.2-codex",
                "gpt-5.2",
                "gpt-5.1",
                "gpt-5.1-codex-max",
                "gemini-3.0-pro",
                "gemini-3.0-flash",
                "deepseek-v3.2",
            ]
        elif provider_name == "bailian-coding-plan":
            # 阿里云优先级：GLM > Qwen
            priority_models = [
                "glm-5",
                "glm-4.7",
                "kimi-k2.5",
                "qwen3.5-plus",
                "qwen3-max-2026-01-23",
                "qwen3-coder-next",
                "qwen3-coder-plus",
            ]
        else:  # volcengine-plan
            # 火山引擎优先级
            priority_models = [
                "glm-4.7",
                "kimi-k2.5",
                "deepseek-v3.2",
                "ark-code-latest",
                "doubao-seed-2.0-pro",
                "doubao-seed-2.0-code",
                "doubao-seed-code",
            ]

        # 添加可用的模型
        for model_name in priority_models:
            if any(r["model"] == model_name for r in provider_results):
                selected_models.append(
                    {
                        "name": f"{provider_name.split('-')[0]}-{model_name}",
                        "api_key": api_key,
                        "base_url": base_url,
                        "model": model_name,
                    }
                )
            elif any(r["model"] == model_name for r in quota_results):
                # 配额用完的也加上，明天可能恢复
                selected_models.append(
                    {
                        "name": f"{provider_name.split('-')[0]}-{model_name}",
                        "api_key": api_key,
                        "base_url": base_url,
                        "model": model_name,
                        "note": "配额暂时用完，明天恢复",
                    }
                )

        models_config.extend(selected_models)

    multi_model_config = {
        "translation_engine": "openai",
        "models": models_config,
        "fallback": {"consecutive_failures": 3},
        "qps": 4,
        "min_text_length": 5,
        "debug": True,
        "custom_system_prompt": None,
    }

    return multi_model_config


if __name__ == "__main__":
    results = test_all_models()

    print("\n\n" + "=" * 70)
    print("生成多模型配置文件...")
    print("=" * 70)

    multi_config = generate_multi_model_config(results)

    output_path = "config/config.multi-model.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(multi_config, f, indent=2, ensure_ascii=False)

    print(f"\n配置文件已生成: {output_path}")
    print(f"包含 {len(multi_config['models'])} 个模型")
    print("\n模型列表:")
    for m in multi_config["models"]:
        note = m.get("note", "")
        status = "○" if note else "✓"
        print(f"  {status} {m['name']} ({m['model']}) {note}")
