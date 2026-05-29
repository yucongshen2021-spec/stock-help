import os
from ..config import Config
from .stock_data import (
    extract_stock_codes,
    find_stock_names_in_text,
    get_realtime_quote,
    get_technical_summary,
    get_stock_news,
)


def load_prompt_file(filename: str) -> str:
    path = os.path.join(Config.PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt() -> str:
    system = load_prompt_file("system.md")
    analysis = load_prompt_file("stock_analysis.md")
    return f"{system}\n\n---\n\n{analysis}"


def build_stock_context(user_message: str) -> str:
    """Detect stock codes/names in user message and fetch comprehensive data."""
    codes = extract_stock_codes(user_message)

    for code in find_stock_names_in_text(user_message):
        if code not in codes:
            codes.append(code)

    if not codes:
        return ""

    context_parts = []
    for code in codes[:3]:
        stock_context = _build_single_stock_context(code)
        if stock_context:
            context_parts.append(stock_context)

    if not context_parts:
        return ""

    header = "## 以下是系统自动获取的实时数据（请基于这些数据进行分析）\n\n"
    return header + "\n\n---\n\n".join(context_parts)


def _build_single_stock_context(code: str) -> str:
    """Build comprehensive context for a single stock: quote + technical + news."""
    parts = []

    try:
        quote = get_realtime_quote(code)
        parts.append(_format_quote(quote))
    except Exception:
        return ""

    try:
        tech = get_technical_summary(code)
        if "error" not in tech:
            parts.append(_format_technical(tech))
    except Exception:
        pass

    try:
        news = get_stock_news(code, count=8)
        valid_news = [n for n in news if "error" not in n]
        if valid_news:
            parts.append(_format_news(valid_news))
    except Exception:
        pass

    return "\n\n".join(parts)


def _format_quote(q: dict) -> str:
    change_symbol = "+" if (q.get("change_pct") or 0) >= 0 else ""
    lines = [
        f"### {q['name']}（{q['code']}）实时行情",
        f"- 最新价: {q['price']}",
        f"- 涨跌幅: {change_symbol}{q['change_pct']}%",
        f"- 涨跌额: {change_symbol}{q['change_amt']}",
        f"- 今开: {q['open']}  |  昨收: {q['prev_close']}",
        f"- 最高: {q['high']}  |  最低: {q['low']}",
        f"- 成交量: {q['volume']}  |  成交额: {q['amount']}",
        f"- 换手率: {q['turnover_rate']}%",
        f"- 市盈率(动态): {q['pe_ratio']}",
        f"- 总市值: {q['total_market_cap']}",
    ]
    return "\n".join(lines)


def _format_technical(t: dict) -> str:
    lines = [
        "### 技术面分析摘要",
        f"- 均线排列: {t['ma_pattern']}",
        f"- MACD 信号: {t['macd_signal']}（DIF={t['dif']}, DEA={t['dea']}）",
        f"- 量能趋势: {t['volume_trend']}",
        f"- 近5日涨跌: {'+' if t['price_5d_change'] >= 0 else ''}{t['price_5d_change']}%",
        f"- 近10日涨跌: {'+' if t['price_10d_change'] >= 0 else ''}{t['price_10d_change']}%",
        f"- 20日最高/最低: {t['high_20d']} / {t['low_20d']}",
        f"- 当前价在20日区间中的位置: {t['price_position_20d']}%（0%=最低点, 100%=最高点）",
        f"- 各均线值: MA5={t['ma5']}, MA10={t['ma10']}, MA20={t['ma20']}, MA60={t['ma60']}",
    ]
    return "\n".join(lines)


def _format_news(news_list: list[dict]) -> str:
    lines = ["### 近期相关新闻"]
    for i, n in enumerate(news_list, 1):
        title = n.get("title", "")
        time = n.get("time", "")
        source = n.get("source", "")
        content = n.get("content", "")
        lines.append(f"\n**{i}. {title}**")
        if time or source:
            lines.append(f"   来源: {source}  时间: {time}")
        if content:
            lines.append(f"   摘要: {content}")
    return "\n".join(lines)
