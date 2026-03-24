#!/usr/bin/env python3
"""测试多模型配置中每个API的连接性"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def test_model_connectivity(config_path: str):
    """测试配置文件中每个模型的连接性"""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    models = config.get("models", [])

    if not models:
        print("错误：配置文件中没有找到 'models' 数组")
        return

    print(f"\n{'='*60}")
    print(f"配置文件：{config_path}")
    print(f"模型数量：{len(models)}")
    print(f"{'='*60}")

    results = []

    for i, model_config in enumerate(models, 1):
        name = model_config.get("name", "unknown")
        base_url = model_config.get("base_url", "")
        api_key = model_config.get("api_key", "")
        model = model_config.get("model", "")

        # 隐藏API key的部分显示
        masked_key = api_key[:8] + "..." if len(api_key) > 8 else api_key

        print(f"\n模型 {i}/{name}")
        print(f"  URL: {base_url}")
        print(f"  Model: {model}")
        print(f"  API Key: {masked_key}")

        try:
            # 尝试连接
            client = httpx.Client()

            # 发送一个简单的测试请求
            test_url = base_url.replace("/chat/completions", "")
            if test_url.endswith("/"):
                test_url = test_url[:-1]

            response = client.post(
                test_url + "/models",
                json={"model": "gpt-3.5-turbo"},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                print(f"  ✓ 连接成功 (HTTP {response.status_code})")
                results.append({"model": name, "status": "success", "code": 200})
            else:
                print(f"  ✗ 连接失败 (HTTP {response.status_code})")
                results.append({"model": name, "status": "failed", "code": response.status_code})

        except httpx.TimeoutException:
            print(f"  ✗ 超时错误")
            results.append({"model": name, "status": "error", "code": "timeout"})

        except httpx.HTTPStatusError as e:
            print(f"  ✗ HTTP错误: {e}")
            results.append({"model": name, "status": "error", "code": str(e.response.status_code)})

        except Exception as e:
            print(f"  ✗ 其他错误: {e}")
            results.append({"model": name, "status": "error", "code": "unknown"})

    # 总结
    print(f"\n{'='*60}")
    print("测试结果总结：")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"  成功：{success_count}/{len(results)}")
    print(f"  失败：{len(results) - success_count}/{len(results)}")

    return results


if __name__ == "__main__":
    config_path = "config/config.multi-model.json"
    test_model_connectivity(config_path)
