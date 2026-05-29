"""数据源：腾讯财经 qt.gtimg.cn + web.ifzq.gtimg.cn"""

import requests
import pandas as pd

from .base import (
    DEFAULT_HEADERS,
    StockNotFound,
    empty_quote,
    market_prefix,
    safe_float,
)

NAME = "tencent"

_HEADERS = {**DEFAULT_HEADERS, "Referer": "https://gu.qq.com/"}
_QUOTE_URL = "https://qt.gtimg.cn/q="
_KLINE_URL = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
_KLT_KEY = {"daily": "day", "weekly": "week", "monthly": "month"}


def _tx_symbol(code: str) -> str:
    return market_prefix(code) + code


def get_quote(code: str) -> dict:
    sym = _tx_symbol(code)
    resp = requests.get(_QUOTE_URL + sym, headers=_HEADERS, timeout=6)
    resp.raise_for_status()
    raw = resp.content.decode("gbk", errors="replace")
    if 'v_' not in raw or '~' not in raw:
        raise StockNotFound(f"腾讯未找到股票 {sym}: {raw[:60]}")
    try:
        body = raw.split('="', 1)[1].rsplit('";', 1)[0]
    except IndexError:
        raise StockNotFound(f"腾讯返回格式异常: {raw[:80]}")
    fields = body.split("~")
    if len(fields) < 50:
        raise RuntimeError(f"腾讯行情字段数异常: {len(fields)}")

    name = fields[1]
    price = safe_float(fields[3])
    prev_close = safe_float(fields[4])
    open_p = safe_float(fields[5])
    volume_hand = safe_float(fields[6])
    volume = volume_hand * 100 if volume_hand is not None else None
    change_amt = safe_float(fields[31])
    change_pct = safe_float(fields[32])
    high = safe_float(fields[33])
    low = safe_float(fields[34])
    amount_wan = safe_float(fields[37])
    amount = amount_wan * 10000 if amount_wan is not None else None
    turnover_rate = safe_float(fields[38])
    pe_ratio = safe_float(fields[39])
    total_cap_yi = safe_float(fields[44])
    circ_cap_yi = safe_float(fields[45])

    q = empty_quote(code, name, NAME)
    q.update({
        "price": price,
        "change_amt": change_amt,
        "change_pct": change_pct,
        "open": open_p,
        "prev_close": prev_close,
        "high": high,
        "low": low,
        "volume": volume,
        "amount": amount,
        "turnover_rate": turnover_rate,
        "pe_ratio": pe_ratio,
        "total_market_cap": total_cap_yi * 1e8 if total_cap_yi is not None else None,
        "circ_market_cap": circ_cap_yi * 1e8 if circ_cap_yi is not None else None,
    })
    return q


def get_kline(code: str, period: str, count: int) -> pd.DataFrame:
    if period not in _KLT_KEY:
        raise ValueError(f"不支持的周期: {period}")
    sym = _tx_symbol(code)
    key = _KLT_KEY[period]
    qty = max(count, 1) if count > 0 else 320
    params = {"param": f"{sym},{key},,,{min(qty, 3000)},qfq"}
    resp = requests.get(_KLINE_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"腾讯 K 线响应错误: {payload.get('msg')}")
    data = (payload.get("data") or {}).get(sym) or {}
    rows = data.get(f"qfq{key}") or data.get(key) or []
    if not rows:
        raise StockNotFound(f"腾讯未返回 {sym} K 线数据")

    parsed = []
    for r in rows:
        if len(r) < 6:
            continue
        parsed.append({
            "date": r[0],
            "open": safe_float(r[1]),
            "close": safe_float(r[2]),
            "high": safe_float(r[3]),
            "low": safe_float(r[4]),
            "volume": (safe_float(r[5]) or 0) * 100,
            "amount": safe_float(r[6]) * 10000 if len(r) > 6 and safe_float(r[6]) is not None else None,
            "turnover": safe_float(r[7]) if len(r) > 7 else None,
        })
    return pd.DataFrame(parsed)
