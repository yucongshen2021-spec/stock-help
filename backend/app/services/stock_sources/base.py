"""Shared helpers for stock data providers."""


class StockNotFound(ValueError):
    """Raised when a provider authoritatively reports the stock does not exist.

    主入口遇到此异常应立即停止，不再尝试其他 provider。
    """


def market_prefix(code: str) -> str:
    """Return 'sh' / 'sz' / 'bj' for the given 6-digit A-share code.

    判断标准（基于官方代码段）：
    - 上海（sh）：6 / 5 / 9 开头，以及 11xxxx 113xxx 等可转债（这里只覆盖股票）
    - 北京（bj）：8 / 4 开头
    - 深圳（sz）：其余（0 / 3 开头）
    """
    if not code or len(code) != 6 or not code.isdigit():
        raise StockNotFound(f"非法股票代码: {code}")
    first = code[0]
    if first in ("6", "5", "9"):
        return "sh"
    if first in ("8", "4"):
        return "bj"
    return "sz"


def em_secid(code: str) -> str:
    """East-Money 风格的 secid: 1.xxxxxx (沪/科创) / 0.xxxxxx (深) / 0.xxxxxx (北交所)"""
    mkt = market_prefix(code)
    return f"{1 if mkt == 'sh' else 0}.{code}"


def xq_symbol(code: str) -> str:
    """Xueqiu 风格: SH600519 / SZ000001 / BJ430047."""
    return market_prefix(code).upper() + code


# 各 provider 共用的 UA，避免被默认 python-requests 拒绝
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def safe_float(v):
    """Convert v to float, return None for empty/invalid (no fallback guessing)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s in ("", "-", "null", "None"):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def empty_quote(code: str, name: str, source: str) -> dict:
    """构造统一字段集的空 quote，未提供的字段全为 None。"""
    return {
        "source": source,
        "code": code,
        "name": name,
        "price": None,
        "change_pct": None,
        "change_amt": None,
        "volume": None,
        "amount": None,
        "high": None,
        "low": None,
        "open": None,
        "prev_close": None,
        "turnover_rate": None,
        "pe_ratio": None,
        "total_market_cap": None,
        "circ_market_cap": None,
    }
