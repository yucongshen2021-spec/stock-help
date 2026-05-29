"""数据源：东方财富 push2.eastmoney.com（高频实时行情）"""

import requests
import pandas as pd

from .base import (
    DEFAULT_HEADERS,
    StockNotFound,
    em_secid,
    empty_quote,
    safe_float,
)

NAME = "eastmoney"

_HEADERS = {**DEFAULT_HEADERS, "Referer": "https://quote.eastmoney.com/"}
_PUSH_QUOTE = "https://push2.eastmoney.com/api/qt/stock/get"
_PUSH_KLINE = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
_KLT_MAP = {"daily": 101, "weekly": 102, "monthly": 103}


def get_quote(code: str) -> dict:
    fields = ",".join([
        "f43", "f44", "f45", "f46", "f47", "f48",
        "f57", "f58", "f60", "f116", "f117",
        "f162", "f168", "f169", "f170",
    ])
    resp = requests.get(
        _PUSH_QUOTE,
        params={"secid": em_secid(code), "fields": fields},
        headers=_HEADERS,
        timeout=8,
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data")
    if not data or not data.get("f57"):
        raise StockNotFound(f"东方财富未找到股票 {code}")

    def _div100(v):
        f = safe_float(v)
        return round(f / 100, 4) if f is not None else None

    q = empty_quote(code, str(data.get("f58", "")), NAME)
    q.update({
        "code": str(data.get("f57", code)),
        "price": _div100(data.get("f43")),
        "change_pct": _div100(data.get("f170")),
        "change_amt": _div100(data.get("f169")),
        "volume": safe_float(data.get("f47")),
        "amount": safe_float(data.get("f48")),
        "high": _div100(data.get("f44")),
        "low": _div100(data.get("f45")),
        "open": _div100(data.get("f46")),
        "prev_close": _div100(data.get("f60")),
        "turnover_rate": _div100(data.get("f168")),
        "pe_ratio": _div100(data.get("f162")),
        "total_market_cap": safe_float(data.get("f116")),
        "circ_market_cap": safe_float(data.get("f117")),
    })
    return q


def get_kline(code: str, period: str, count: int) -> pd.DataFrame:
    if period not in _KLT_MAP:
        raise ValueError(f"不支持的周期: {period}")
    params = {
        "secid": em_secid(code),
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": _KLT_MAP[period],
        "fqt": 1,
        "beg": "20100101",
        "end": "20500101",
    }
    resp = requests.get(_PUSH_KLINE, params=params, headers=_HEADERS, timeout=12)
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data") or {}
    klines = data.get("klines") or []
    if not klines:
        raise StockNotFound(f"东方财富未返回 {code} 的 K 线数据")

    rows = [line.split(",") for line in klines]
    df = pd.DataFrame(rows, columns=[
        "date", "open", "close", "high", "low",
        "volume", "amount", "amplitude", "change_pct", "change_amt", "turnover",
    ])
    for col in ["open", "close", "high", "low", "volume", "amount",
                "amplitude", "change_pct", "change_amt", "turnover"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.tail(count).reset_index(drop=True) if count > 0 else df
