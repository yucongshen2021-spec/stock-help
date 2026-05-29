"""数据源：雪球 stock.xueqiu.com

需要先访问 https://xueqiu.com/ 获取 anti-CSRF cookie，否则 API 返回 400。
本模块用模块级 Session 自动维护。
"""

import threading
import time

import pandas as pd
import requests

from .base import (
    DEFAULT_HEADERS,
    StockNotFound,
    empty_quote,
    safe_float,
    xq_symbol,
)

NAME = "xueqiu"

_HEADERS = {**DEFAULT_HEADERS, "Referer": "https://xueqiu.com/"}
_QUOTE_URL = "https://stock.xueqiu.com/v5/stock/quote.json"
_KLINE_URL = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
_KLT_PERIOD = {"daily": "day", "weekly": "week", "monthly": "month"}

_session: requests.Session | None = None
_session_ts: float = 0.0
_lock = threading.Lock()
_COOKIE_TTL_SECONDS = 1800


def _get_session() -> requests.Session:
    """Return a Session with valid xueqiu cookies (refreshed every 30 min)."""
    global _session, _session_ts
    with _lock:
        if _session is None or (time.time() - _session_ts) > _COOKIE_TTL_SECONDS:
            s = requests.Session()
            s.headers.update(_HEADERS)
            s.get("https://xueqiu.com/", timeout=6)
            _session = s
            _session_ts = time.time()
        return _session


def _request_json(url: str, params: dict) -> dict:
    """Issue a GET with auto cookie refresh on 400 (cookie expired)."""
    sess = _get_session()
    resp = sess.get(url, params=params, timeout=8)
    if resp.status_code == 400:
        with _lock:
            global _session
            _session = None
        sess = _get_session()
        resp = sess.get(url, params=params, timeout=8)
    resp.raise_for_status()
    return resp.json()


def get_quote(code: str) -> dict:
    symbol = xq_symbol(code)
    payload = _request_json(_QUOTE_URL, {"symbol": symbol, "extend": "detail"})
    if payload.get("error_code"):
        raise RuntimeError(f"雪球错误: {payload.get('error_description')}")
    data = payload.get("data") or {}
    quote = data.get("quote") or {}
    if not quote.get("code"):
        raise StockNotFound(f"雪球未找到股票 {symbol}")

    q = empty_quote(code, quote.get("name") or "", NAME)
    q.update({
        "code": str(quote.get("code") or code),
        "price": safe_float(quote.get("current")),
        "change_amt": safe_float(quote.get("chg")),
        "change_pct": safe_float(quote.get("percent")),
        "open": safe_float(quote.get("open")),
        "prev_close": safe_float(quote.get("last_close")),
        "high": safe_float(quote.get("high")),
        "low": safe_float(quote.get("low")),
        "volume": safe_float(quote.get("volume")),
        "amount": safe_float(quote.get("amount")),
        "turnover_rate": safe_float(quote.get("turnover_rate")),
        "pe_ratio": safe_float(quote.get("pe_ttm")),
        "total_market_cap": safe_float(quote.get("market_capital")),
        "circ_market_cap": safe_float(quote.get("float_market_capital")),
    })
    return q


def get_kline(code: str, period: str, count: int) -> pd.DataFrame:
    if period not in _KLT_PERIOD:
        raise ValueError(f"不支持的周期: {period}")
    symbol = xq_symbol(code)
    qty = max(count, 1) if count > 0 else 320
    params = {
        "symbol": symbol,
        "begin": int(time.time() * 1000),
        "period": _KLT_PERIOD[period],
        "type": "before",
        "count": f"-{min(qty, 3000)}",
        "indicator": "kline",
    }
    payload = _request_json(_KLINE_URL, params)
    if payload.get("error_code"):
        raise RuntimeError(f"雪球 K 线错误: {payload.get('error_description')}")
    data = payload.get("data") or {}
    columns = data.get("column") or []
    items = data.get("item") or []
    if not items:
        raise StockNotFound(f"雪球未返回 {symbol} K 线数据")

    df = pd.DataFrame(items, columns=columns)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.strftime("%Y-%m-%d")
    df["amount"] = df["amount"] if "amount" in df.columns else pd.NA
    df["turnover"] = df["turnoverrate"] if "turnoverrate" in df.columns else pd.NA
    return df[["date", "open", "close", "high", "low", "volume", "amount", "turnover"]]
