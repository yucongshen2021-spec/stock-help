"""
股票行情/K线 多数据源适配层

每个 provider 模块独立实现：
- NAME: 数据源标识
- get_quote(code) -> dict          可选
- get_kline(code, period, count)   可选

调用方按 PROVIDERS 列表的顺序逐个尝试。

异常约定：
- StockNotFound(ValueError)  明确该股票不存在/未上市，立即停止，不再换源
- 其他 Exception              该 provider 不可用，尝试下一个
"""

from .base import StockNotFound
from . import eastmoney, sina, tencent, xueqiu, akshare_provider

QUOTE_PROVIDERS = [
    eastmoney,
    sina,
    tencent,
    xueqiu,
    akshare_provider,
]

KLINE_PROVIDERS = [
    eastmoney,
    sina,
    tencent,
    xueqiu,
    akshare_provider,
]

__all__ = ["StockNotFound", "QUOTE_PROVIDERS", "KLINE_PROVIDERS"]
