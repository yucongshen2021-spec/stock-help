"""数据源：AKShare（最后一道，依赖另一套接口集合，作为前 4 源全失败时的备用）"""

import akshare as ak
import pandas as pd

from .base import StockNotFound, empty_quote, safe_float

NAME = "akshare"

_PERIOD_MAP = {"daily": "daily", "weekly": "weekly", "monthly": "monthly"}


def get_quote(code: str) -> dict:
    """走 ak.stock_bid_ask_em（东方财富）取实时行情。

    与 stock_sources.eastmoney 共用 push2 接口，但走 akshare 封装好的请求头/重试。
    """
    try:
        df = ak.stock_bid_ask_em(symbol=code)
    except Exception as e:
        raise RuntimeError(f"akshare 行情请求失败: {e}")
    if df is None or df.empty:
        raise StockNotFound(f"akshare 未找到股票 {code}")

    kv = dict(zip(df["item"].astype(str), df["value"]))

    def _v(key):
        return safe_float(kv.get(key))

    q = empty_quote(code, str(kv.get("股票简称", "")), NAME)
    q["price"] = _v("最新")
    q["open"] = _v("今开")
    q["prev_close"] = _v("昨收")
    q["high"] = _v("最高")
    q["low"] = _v("最低")
    q["volume"] = _v("总手") if _v("总手") is not None else _v("成交量")
    q["amount"] = _v("成交额")
    q["change_amt"] = _v("涨跌")
    q["change_pct"] = _v("涨幅")
    q["turnover_rate"] = _v("换手")
    q["pe_ratio"] = _v("市盈率")
    return q


def get_kline(code: str, period: str, count: int) -> pd.DataFrame:
    if period not in _PERIOD_MAP:
        raise ValueError(f"不支持的周期: {period}")
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period=_PERIOD_MAP[period],
            adjust="qfq",
        )
    except Exception as e:
        raise RuntimeError(f"akshare K 线请求失败: {e}")
    if df is None or df.empty:
        raise StockNotFound(f"akshare 未返回 {code} K 线数据")

    df = df.rename(columns={
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
        "换手率": "turnover",
    })
    df["date"] = df["date"].astype(str)
    for col in ["open", "close", "high", "low", "volume", "amount", "turnover"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "turnover" not in df.columns:
        df["turnover"] = pd.NA
    return df[["date", "open", "close", "high", "low", "volume", "amount", "turnover"]].tail(count if count > 0 else len(df))
