from flask import Blueprint, request, jsonify
from ..services.stock_data import (
    search_stock,
    get_realtime_quote,
    get_kline,
    get_indicators,
    get_technical_summary,
    get_stock_news,
)

stock_bp = Blueprint("stock", __name__)


@stock_bp.route("/search")
def stock_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "缺少搜索关键词 q"}), 400
    try:
        results = search_stock(q)
        return jsonify({"data": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/quote/<code>")
def stock_quote(code: str):
    try:
        data = get_realtime_quote(code)
        return jsonify({"data": data})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/kline/<code>")
def stock_kline(code: str):
    period = request.args.get("period", "daily")
    count = request.args.get("count", "120", type=int)
    try:
        data = get_kline(code, period=period, count=count)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/indicators/<code>")
def stock_indicators(code: str):
    count = request.args.get("count", "120", type=int)
    try:
        data = get_indicators(code, count=count)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/analysis/<code>")
def stock_analysis(code: str):
    try:
        data = get_technical_summary(code)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/news/<code>")
def stock_news(code: str):
    count = request.args.get("count", "10", type=int)
    try:
        data = get_stock_news(code, count=count)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
