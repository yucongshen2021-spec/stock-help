"""
Chat SSE 集成测试
测试目标:
1. 后端可正确接收 messages 并返回 SSE 流
2. 后端能识别股票代码 600519 并注入实时数据/技术分析/新闻到 prompt
3. DeepSeek API 流式返回有效内容
"""
import io
import json
import sys
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def stream_chat(user_message: str, model: str = None):
    body = {"messages": [{"role": "user", "content": user_message}]}
    if model:
        body["model"] = model

    print(f"\n>>> 用户问题: {user_message}")
    print(">>> 流式响应:\n")

    full_text = []
    with requests.post(
        "http://127.0.0.1:3001/api/chat",
        json=body,
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue
            payload = line[6:]
            if payload == "[DONE]":
                break
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if "error" in data:
                print(f"\n!!! 错误: {data['error']}")
                return None
            chunk = data.get("content", "")
            full_text.append(chunk)
            print(chunk, end="", flush=True)

    print("\n\n=== END ===")
    return "".join(full_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: py test_chat.py '<question>'")
        sys.exit(1)
    text = stream_chat(sys.argv[1])
    if text:
        print(f"\n总字符数: {len(text)}")
