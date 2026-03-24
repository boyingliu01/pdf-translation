#!/usr/bin/env python3
"""测试多模型配置中每个API的连接性 - 使用实际翻译请求"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import httpx
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_chat_completion(base_url: str, api_key: str, model: str) -> dict:
    """测试实际的chat completion请求"""
    chat_url = base_url.rstrip("/") + "/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful translator."},
            {
                "role": "user",
                "content": "Translate 'Hello' to Chinese. Reply with just the translation.",
            },
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
            else:
                error_detail = (
                    response.text[:200] if response.text else "No error details"
                )
                return {
                    "success": False,
                    "status": response.status_code,
                    "error": error_detail,
                }
    except httpx.TimeoutException:
        return {"success": False, "status": "timeout", "error": "Request timed out"}
    except httpx.ConnectError as e:
        return {"success": False, "status": "connection_error", "error": str(e)}
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)}


def test_model_connectivity(config_path: str):
    """测试配置文件中每个模型的连接性"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    models = config.get("models", [])

    if not models:
        print("错误：配置文件中没有找到 'models' 数组")
        return

    print(f"\n{'=' * 70}")
    print(f"配置文件：{config_path}")
    print(f"模型数量：{len(models)}")
    print(f"{'=' * 70}")

    results = []

    for i, model_config in enumerate(models, 1):
        name = model_config.get("name", "unknown")
        base_url = model_config.get("base_url", "")
        api_key = model_config.get("api_key", "")
        model = model_config.get("model", "")

        # 隐藏API key的部分显示
        masked_key = api_key[:8] + "..." if len(api_key) > 8 else api_key

        print(f"\n[{i}/{len(models)}] 测试模型: {name}")
        print(f"  URL: {base_url}")
        print(f"  Model: {model}")
        print(f"  API Key: {masked_key}")
        print(f"  {'-' * 50}")

        result = test_chat_completion(base_url, api_key, model)
        results.append({"name": name, **result})

        if result["success"]:
            print(f"  ✓ 连接成功 (HTTP {result['status']})")
            print(f"    响应: {result['response']}")
        else:
            print(f"  ✗ 连接失败 ({result['status']})")
            print(f"    错误: {result['error']}")

    # 总结
    print(f"\n{'=' * 70}")
    print("测试结果总结：")
    success_count = sum(1 for r in results if r.get("success"))
    print(f"  ✓ 成功：{success_count}/{len(results)}")
    print(f"  ✗ 失败：{len(results) - success_count}/{len(results)}")
    print(f"{'=' * 70}")

    print("\n详细结果：")
    for r in results:
        status = "✓" if r.get("success") else "✗"
        print(f"  {status} {r['name']}: {r.get('status', 'unknown')}")

    return results


if __name__ == "__main__":
    config_path = "config/config.multi-model.json"
    test_model_connectivity(config_path)
