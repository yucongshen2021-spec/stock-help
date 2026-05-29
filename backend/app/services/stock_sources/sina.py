"""数据源：新浪财经 hq.sinajs.cn + money.finance.sina.com.cn

行情接口返回 GBK 编码的 var hq_str_xxx="字段1,字段2,..." 文本。
字段顺序：https://blog.csdn.net/leshami/article/details/9474727
"""

import requests
import pandas as pd

from .base import (
    DEFAULT_HEADERS,
    StockNotFound,
    empty_quote,
    market_prefix,
    safe_float,
)

NAME = "sina"

_HEADERS = {**DEFAULT_HEADERS, "Referer": "https://finance.sina.com.cn/"}
_QUOTE_URL = "https://hq.sinajs.cn/list="
_KLINE_URL = (
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
    "CN_MarketData.getKLineData"
)
_KLT_SCALE = {"daily": 240, "weekly": 1680, "monthly": 7200}


def _sina_symbol(code: str) -> str:
    return market_prefix(code) + code


def get_quote(code: str) -> dict:
    sym = _sina_symbol(code)
    resp = requests.get(_QUOTE_URL + sym, headers=_HEADERS, timeout=6)
    resp.raise_for_status()
    raw = resp.content.decode("gbk", errors="replace")
    if "=\"\";" in raw or '=""' in raw.split("=", 1)[-1][:5]:
        raise StockNotFound(f"新浪未找到股票 {sym}")
    try:
        body = raw.split("=\"", 1)[1].split("\";", 1)[0]
    except IndexError:
        raise StockNotFound(f"新浪返回格式异常: {raw[:80]}")
    fields = body.split(",")
    if len(fields) < 32:
        raise RuntimeError(f"新浪行情字段数异常: {len(fields)}")

    name = fields[0]
    open_p = safe_float(fields[1])
    prev_close = safe_float(fields[2])
    price = safe_float(fields[3])
    high = safe_float(fields[4])
    low = safe_float(fields[5])
    volume = safe_float(fields[8])
    amount = safe_float(fields[9])

    change_amt = None
    change_pct = None
    if price is not None and prev_close not in (None, 0):
        change_amt = round(price - prev_close, 4)
        change_pct = round((price - prev_close) / prev_close * 100, 4)

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
    })
    return q


def get_kline(code: str, period: str, count: int) -> pd.DataFrame:
    if period not in _KLT_SCALE:
        raise ValueError(f"不支持的周期: {period}")
    sym = _sina_symbol(code)
    datalen = max(count, 1) if count > 0 else 300
    params = {
        "symbol": sym,
        "scale": _KLT_SCALE[period],
        "ma": "no",
        "datalen": min(datalen, 3000),
    }
    resp = requests.get(_KLINE_URL, params=params, headers=_HEADERS, timeout=10)
    resp.raise_for_status()
    items = resp.json()
    if not isinstance(items, list) or not items:
        raise StockNotFound(f"新浪未返回 {sym} 的 K 线数据")

    df = pd.DataFrame(items)
    df = df.rename(columns={"day": "date"})
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "amount" not in df.columns:
        df["amount"] = pd.NA
    if "turnover" not in df.columns:
        df["turnover"] = pd.NA
    return df[["date", "open", "close", "high", "low", "volume", "amount", "turnover"]]
