"""
股票数据服务（多数据源版本）

数据源按 stock_sources.QUOTE_PROVIDERS / KLINE_PROVIDERS 的顺序依次尝试：
1. 东方财富 push2 (eastmoney)
2. 新浪财经    (sina)
3. 腾讯财经    (tencent)
4. 雪球        (xueqiu)
5. AKShare     (akshare_provider)

约束（来自用户规则：不允许任何兜底猜测）：
- 单次请求只采用某一个源的完整结果，不在不同源间合并字段
- 返回的 dict 始终带 `source` 字段，明确告知本次数据来源
- 真正"该股票不存在"（StockNotFound）会立即停止，不再尝试其他源
- 网络/限流错误才会换源
"""

import logging
import os
import re
import sys
from pathlib import Path

import akshare as ak
import pandas as pd

from .stock_sources import KLINE_PROVIDERS, QUOTE_PROVIDERS, StockNotFound

logger = logging.getLogger(__name__)


_STOCK_LIST_CACHE: pd.DataFrame | None = None


def _stock_list_path() -> Path:
    """A 股股票列表静态文件的真实路径。

    - PyInstaller 打包后，资源被解压到 sys._MEIPASS/app/data/stock_list.csv
    - 直接运行源码时，路径是 backend/app/data/stock_list.csv
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "app" / "data" / "stock_list.csv"
    return Path(__file__).resolve().parent.parent / "data" / "stock_list.csv"


def _get_stock_list() -> pd.DataFrame:
    """加载 A 股全市场代码/名称列表。

    数据源是随程序一起发布的静态 CSV（由 scripts/dump_stock_list.py 离线生成）。
    不在运行时访问外部数据源，避免客户网络或 CI 环境 IP 被屏蔽时搜索完全失效。
    """
    global _STOCK_LIST_CACHE
    if _STOCK_LIST_CACHE is not None:
        return _STOCK_LIST_CACHE

    path = _stock_list_path()
    if not path.is_file():
        raise RuntimeError(
            f"未找到股票列表静态文件: {path}。"
            f"请在源码目录执行 `python scripts/dump_stock_list.py` 生成后再重新打包。"
        )

    df = pd.read_csv(path, dtype={"code": str, "name": str}, encoding="utf-8")
    if df.empty or not {"code", "name"}.issubset(df.columns):
        raise RuntimeError(f"股票列表静态文件格式不正确: {path}")

    _STOCK_LIST_CACHE = df
    logger.info("loaded stock list from %s (rows=%d)", path, len(df))
    return _STOCK_LIST_CACHE


def search_stock(keyword: str) -> list[dict]:
    """股票名/代码模糊搜索（仅本地股票列表，不走外网行情源）。"""
    try:
        df = _get_stock_list()
        mask = df["code"].str.contains(keyword) | df["name"].str.contains(keyword)
        results = df[mask].head(20)
        return results.to_dict(orient="records")
    except Exception as e:
        raise RuntimeError(f"股票搜索失败: {e}")


def _try_providers(providers, op_name: str, code: str, op):
    """按 providers 顺序逐个尝试 op；遇 StockNotFound 立刻停。

    全部失败时抛出 RuntimeError，错误消息包含每个源的失败原因。
    """
    errors: list[str] = []
    for provider in providers:
        name = getattr(provider, "NAME", provider.__name__)
        try:
            result = op(provider)
            logger.info("[%s] %s(%s) -> %s", op_name, name, code, "OK")
            return result
        except StockNotFound:
            raise
        except Exception as e:
            msg = f"{name}: {type(e).__name__}: {str(e)[:160]}"
            errors.append(msg)
            logger.warning("[%s] %s(%s) FAIL: %s", op_name, name, code, msg)
            continue
    raise RuntimeError(f"全部数据源失败: {'; '.join(errors)}")


def get_realtime_quote(code: str) -> dict:
    """返回某只股票的实时行情。结果带 `source` 字段标明来源。"""
    return _try_providers(
        QUOTE_PROVIDERS,
        "quote",
        code,
        lambda p: p.get_quote(code),
    )


def _fetch_kline_raw(code: str, period: str) -> tuple[pd.DataFrame, str]:
    """统一获取 K 线 DataFrame，返回 (df, source_name)。"""
    df_holder = {}

    def _op(provider):
        df = provider.get_kline(code, period, count=0)
        if df is None or df.empty:
            raise StockNotFound(f"{provider.NAME} 返回空 K 线")
        df_holder["source"] = provider.NAME
        return df

    df = _try_providers(KLINE_PROVIDERS, f"kline_{period}", code, _op)
    return df, df_holder["source"]


def get_kline(code: str, period: str = "daily", count: int = 120) -> list[dict]:
    """K 线列表（按 count 截尾）。period: daily / weekly / monthly。"""
    df, source = _fetch_kline_raw(code, period)
    df = df.tail(count).reset_index(drop=True) if count > 0 else df

    return [
        {
            "source": source,
            "date": str(row["date"]),
            "open": _safe_float(row.get("open")),
            "close": _safe_float(row.get("close")),
            "high": _safe_float(row.get("high")),
            "low": _safe_float(row.get("low")),
            "volume": _safe_float(row.get("volume")),
            "amount": _safe_float(row.get("amount")),
            "turnover": _safe_float(row.get("turnover")),
        }
        for _, row in df.iterrows()
    ]


def get_indicators(code: str, count: int = 120) -> dict:
    """从日 K 线计算 MA + MACD。"""
    df, source = _fetch_kline_raw(code, "daily")

    close = pd.to_numeric(df["close"], errors="coerce")
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_bar = (dif - dea) * 2

    dates = df["date"].astype(str).tolist()
    sl = slice(-count, None) if count > 0 else slice(None)

    return {
        "source": source,
        "dates": dates[sl],
        "ma5": _series_to_list(ma5.iloc[sl]),
        "ma10": _series_to_list(ma10.iloc[sl]),
        "ma20": _series_to_list(ma20.iloc[sl]),
        "ma60": _series_to_list(ma60.iloc[sl]),
        "macd": {
            "dif": _series_to_list(dif.iloc[sl]),
            "dea": _series_to_list(dea.iloc[sl]),
            "bar": _series_to_list(macd_bar.iloc[sl]),
        },
    }


def get_technical_summary(code: str) -> dict:
    """生成技术分析摘要，基于日 K 线最近 65 天。"""
    try:
        df, source = _fetch_kline_raw(code, "daily")
    except StockNotFound:
        return {"error": "未获取到该股票的历史 K 线"}
    except Exception as e:
        return {"error": f"技术分析生成失败: {e}"}

    if len(df) < 65:
        return {"error": f"历史数据不足（{len(df)} 条），无法生成技术分析"}

    df = df.tail(65)
    close = pd.to_numeric(df["close"], errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")

    latest = float(close.iloc[-1])
    ma5 = float(close.rolling(5).mean().iloc[-1])
    ma10 = float(close.rolling(10).mean().iloc[-1])
    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma60 = float(close.rolling(60).mean().iloc[-1])

    if ma5 > ma10 > ma20 > ma60:
        ma_pattern = "多头排列（强势）"
    elif ma5 < ma10 < ma20 < ma60:
        ma_pattern = "空头排列（弱势）"
    elif ma5 > ma10 and ma10 < ma20:
        ma_pattern = "短期反弹，中期仍偏弱"
    elif ma5 < ma10 and ma10 > ma20:
        ma_pattern = "短期回调，中期仍偏强"
    else:
        ma_pattern = "均线交织，方向不明"

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9, adjust=False).mean()

    dif_val = float(dif.iloc[-1])
    dea_val = float(dea.iloc[-1])
    dif_prev = float(dif.iloc[-2])
    dea_prev = float(dea.iloc[-2])

    if dif_prev <= dea_prev and dif_val > dea_val:
        macd_signal = "金叉（买入信号）"
    elif dif_prev >= dea_prev and dif_val < dea_val:
        macd_signal = "死叉（卖出信号）"
    elif dif_val > dea_val and dif_val > 0:
        macd_signal = "零轴上方多头运行"
    elif dif_val < dea_val and dif_val < 0:
        macd_signal = "零轴下方空头运行"
    else:
        macd_signal = "DIF与DEA接近，等待方向选择"

    vol_5 = float(volume.tail(5).mean())
    vol_20 = float(volume.tail(20).mean())
    if vol_5 > vol_20 * 1.5:
        volume_trend = "近5日成交量显著放大（是20日均量的{:.0f}%）".format(vol_5 / vol_20 * 100)
    elif vol_5 > vol_20 * 1.1:
        volume_trend = "近5日成交量温和放大"
    elif vol_5 < vol_20 * 0.7:
        volume_trend = "近5日成交量明显萎缩（仅为20日均量的{:.0f}%）".format(vol_5 / vol_20 * 100)
    else:
        volume_trend = "近5日成交量平稳"

    recent_5 = close.tail(5).tolist()
    price_5d_change = (recent_5[-1] - recent_5[0]) / recent_5[0] * 100
    recent_10 = close.tail(10).tolist()
    price_10d_change = (recent_10[-1] - recent_10[0]) / recent_10[0] * 100

    high_20 = float(pd.to_numeric(df["high"], errors="coerce").tail(20).max())
    low_20 = float(pd.to_numeric(df["low"], errors="coerce").tail(20).min())
    price_position = (
        (latest - low_20) / (high_20 - low_20) * 100 if high_20 != low_20 else 50
    )

    return {
        "source": source,
        "latest_price": round(latest, 2),
        "ma5": round(ma5, 2),
        "ma10": round(ma10, 2),
        "ma20": round(ma20, 2),
        "ma60": round(ma60, 2),
        "ma_pattern": ma_pattern,
        "macd_signal": macd_signal,
        "dif": round(dif_val, 4),
        "dea": round(dea_val, 4),
        "volume_trend": volume_trend,
        "price_5d_change": round(price_5d_change, 2),
        "price_10d_change": round(price_10d_change, 2),
        "high_20d": round(high_20, 2),
        "low_20d": round(low_20, 2),
        "price_position_20d": round(price_position, 1),
    }


def get_stock_news(code: str, count: int = 10) -> list[dict]:
    """股票相关新闻（使用 akshare 的东方财富新闻接口）。"""
    try:
        df = ak.stock_news_em(symbol=code)
        df = df.head(count)
        results = []
        for _, row in df.iterrows():
            results.append({
                "title": str(row.get("新闻标题", "")),
                "content": str(row.get("新闻内容", ""))[:200],
                "time": str(row.get("发布时间", "")),
                "source": str(row.get("文章来源", "")),
                "url": str(row.get("新闻链接", "")),
            })
        return results
    except Exception as e:
        return [{"error": f"获取新闻失败: {e}"}]


def extract_stock_codes(text: str) -> list[str]:
    r"""从文本中提取 6 位股票代码。

    使用负向前后查 (?<!\d)...(?!\d) 而非 \b——Python 的 \b 把中文视为 word
    character，"下600519最" 之间不存在 \b 边界。
    """
    return re.findall(r"(?<!\d)(\d{6})(?!\d)", text)


def resolve_stock_name(name: str) -> str | None:
    """名称匹配股票代码（精确优先，再前缀）。"""
    try:
        df = _get_stock_list()
        row = df[df["name"] == name]
        if not row.empty:
            return row.iloc[0]["code"]
        partial = df[df["name"].str.contains(name)]
        if not partial.empty:
            return partial.iloc[0]["code"]
    except Exception:
        pass
    return None


def find_stock_names_in_text(text: str, max_matches: int = 3) -> list[str]:
    """扫描股票列表，返回文本中包含其完整名称的股票代码。"""
    try:
        df = _get_stock_list()
    except Exception:
        return []

    found: list[tuple[int, str]] = []
    for _, row in df.iterrows():
        name = row["name"]
        if not isinstance(name, str) or len(name) < 2:
            continue
        idx = text.find(name)
        if idx >= 0:
            found.append((idx, row["code"]))

    found.sort(key=lambda x: x[0])
    seen, result = set(), []
    for _, code in found:
        if code not in seen:
            seen.add(code)
            result.append(code)
        if len(result) >= max_matches:
            break
    return result


def _safe_float(val) -> float | None:
    try:
        if val is None or (hasattr(pd, "isna") and pd.isna(val)):
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def _series_to_list(s: pd.Series) -> list:
    return [None if pd.isna(v) else round(float(v), 4) for v in s]
