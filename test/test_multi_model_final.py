#!/usr/bin/env python3
"""测试更新后的多模型配置"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import httpx


def test_model(name, base_url, api_key, model):
    """测试单个模型"""
    chat_url = base_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Translate 'Hello' to Chinese. Reply with just the translation.",
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
                error = response.text[:150] if response.text else "Unknown error"
                return {
                    "success": False,
                    "status": response.status_code,
                    "error": error,
                }
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)[:100]}


def main():
    # 加载配置
    with open("config/config.multi-model.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    models = config.get("models", [])

    print(f"\n{'=' * 70}")
    print(f"测试多模型配置")
    print(f"模型数量: {len(models)}")
    print(f"{'=' * 70}\n")

    results = []

    for i, model_config in enumerate(models, 1):
        name = model_config.get("name", "unknown")
        base_url = model_config.get("base_url", "")
        api_key = model_config.get("api_key", "")
        model = model_config.get("model", "")

        masked_key = api_key[:8] + "..." if len(api_key) > 8 else api_key

        print(f"\n[{i}/{len(models)}] 测试: {name}")
        print(f"  Model: {model}")
        print(f"  URL: {base_url}")
        print(f"  Key: {masked_key}")

        result = test_model(name, base_url, api_key, model)
        results.append({"name": name, **result})

        if result["success"]:
            print(f"  ✓ 成功 ({result['status']}): {result['response']}")
        elif result["status"] == 429:
            print(f"  ○ 配额用完 (429)")
        else:
            print(f"  ✗ 失败 ({result['status']}): {result['error'][:80]}")

    # 总结
    print(f"\n{'=' * 70}")
    print("测试结果:")
    success = [r for r in results if r["success"]]
    quota = [r for r in results if r["status"] == 429]
    failed = [r for r in results if not r["success"] and r["status"] != 429]

    print(f"  ✓ 可用: {len(success)}/{len(results)}")
    print(f"  ○ 配额用完: {len(quota)}/{len(results)}")
    print(f"  ✗ 失败: {len(failed)}/{len(results)}")
    print(f"{'=' * 70}")

    if success:
        print("\n可用模型:")
        for r in success:
            print(f"  ✓ {r['name']}")

    if quota:
        print("\n配额用完 (明天恢复):")
        for r in quota:
            print(f"  ○ {r['name']}")

    if failed:
        print("\n配置错误:")
        for r in failed:
            print(f"  ✗ {r['name']} ({r['status']})")

    return results


if __name__ == "__main__":
    main()
