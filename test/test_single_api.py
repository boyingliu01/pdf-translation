#!/usr/bin/env python3
"""测试智谱AI单独API调用"""

import httpx
import json

api_key = "***API_KEY_REMOVED***"
base_url = "https://open.bigmodel.com/api/paas/v4"

try:
    client = httpx.Client()
    response = client.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={"model": "glm-4-flash", "messages": [{"role": "user", "content": "test"}]},
        timeout=10.0
    )
    print(f"状态码：{response.status_code}")
    if response.status_code == 200:
        print("✓ 连接成功")
        print(f"响应：{ {[k[:100] + '...' if len(v) > 100 else v for k, v in response.json().items()}")
    else:
        print(f"响应：{response.text[:200]}")

except Exception as e:
    print(f"错误：{e}")
