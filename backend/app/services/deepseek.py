from openai import OpenAI

from ..config import Config


def _client() -> OpenAI:
    """构造 OpenAI client，参数全部来自 .env。"""
    if not Config.DEEPSEEK_API_KEY:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY，请在 .env 中填写")
    return OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL,
    )


def chat_stream(messages: list[dict]):
    """流式调用 DeepSeek（模型从 .env 读取）。"""
    client = _client()
    response = client.chat.completions.create(
        model=Config.DEEPSEEK_MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content
