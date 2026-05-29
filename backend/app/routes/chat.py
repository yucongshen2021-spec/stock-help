import json

from flask import Blueprint, Response, jsonify, request

from ..services.context import build_stock_context, build_system_prompt
from ..services.deepseek import chat_stream

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """流式聊天接口。

    DeepSeek 的 API Key / Base URL / Model 全部从后端 .env 读取，
    不接受前端传入（避免凭据泄漏到浏览器存储）。
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "请求体不能为空"}), 400

    messages = body.get("messages", [])
    if not messages:
        return jsonify({"error": "messages 不能为空"}), 400

    last_user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break

    system_prompt = build_system_prompt()
    stock_context = build_stock_context(last_user_msg)

    full_messages = [{"role": "system", "content": system_prompt}]
    if stock_context:
        full_messages.append({"role": "system", "content": stock_context})
    full_messages.extend(messages)

    def generate():
        try:
            for chunk in chat_stream(full_messages):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
