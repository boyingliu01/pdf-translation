#!/usr/bin/env python3
"""测试各个API的正确端点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import json

# 智谱AI 正确配置（已知可用）
zhipu_config = {
    "api_key": "***API_KEY_REMOVED***",
    "base_url": "https://open.bigmodel.cn/api/paas/v4",
    "model": "glm-4-flash"
}

# 智谱AI 测试 models 端点
zhipu_models_url = "https://open.bigmodel.cn/api/paas/v4/models"

# DeepSeek 正确配置（已知可用）
deepseek_config = {
    "api_key": "803de240-5683-4ce3-9cbd-0ad5192db942",
    "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
    "model": "deepseek-v3.2"
}

# DeepSeek 测试 models 端点
deepseek_models_url = "https://ark.cn-beijing.volces.com/api/coding/v3/models"

# Gemini/SiliconFlow 配置
gemini_config = {
    "api_key": "ck_fb8jzqbplx4w.u9tk4adryX5bYc9YgDkJV_tZRujzy4InMUyjvgkxvjQ",
    "base_url": "https://www.codebuddy.ai/v2",
    "model": "gemini-3.0-flash"
}


def test_api(name, config, test_models_url):
    """测试API连接"""
    client = httpx.Client()
    url = config["base_url"]

    print(f"\n{'='*60}")
    print(f"测试 {name}")
    print(f"Base URL: {url}")

    try:
        # 测试 /models 端点
        models_response = client.post(
            test_models_url,
            json={"model": config["model"]},
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            },
            timeout=10.0
        )
        print(f"/models 端点: HTTP {models_response.status_code}")
        if models_response.status_code == 200:
            print("✓ /models 端点可用")
        else:
            print(f"✗ /models 端点返回: {models_response.status_code} - {models_response.text[:200]}")

        # 测试 /chat/completions 端点
        chat_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        chat_response = client.post(
            chat_url,
            json={"model": config["model"], "messages": [{"role": "user", "content": "test"}]},
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            },
            timeout=10.0
        )
        print(f"/chat/completions 端点: HTTP {chat_response.status_code}")
        if chat_response.status_code == 200:
            print("✓ /chat/completions 端点可用")
            result = json.loads(chat_response.text)
            if "choices" in result and len(result["choices"]) > 0:
                print(f"  回复：{result['choices'][0].get('message', {})[:100]}...")
        else:
            print(f"✗ /chat/completions 端点返回: {chat_response.status_code} - {chat_response.text[:200]}")

    except httpx.TimeoutException:
        print("✗ 超时错误")
    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP错误: {e}")
    except Exception as e:
        print(f"✗ 其他错误: {e}")


if __name__ == "__main__":
    # 测试智谱AI
    test_api("智谱AI (zhipu)", zhipu_config, zhipu_models_url)

    # 测试 DeepSeek
    test_api("DeepSeek", deepseek_config, deepseek_models_url)

    # 测试 Gemini
    test_api("Gemini", gemini_config, "")
