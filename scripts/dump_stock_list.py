"""一次性拉取 A 股全市场股票列表并写入静态数据文件。

设计要点：
- 用 akshare.stock_info_a_code_name() 拉取 A 股 code+name 列表；
- 写入 backend/app/data/stock_list.csv，作为产品静态资源，随程序一起发布；
- 后端运行时从该静态文件加载，不再访问外部网络（避免客户 / CI 环境因 IP 被屏蔽导致搜索失效）。

刷新机制：
- 这是一次性脚本。需要更新股票列表（如新增 IPO）时，开发/运维手动重新执行一次：
    python scripts/dump_stock_list.py
- 不在正式版 exe 里提供"运行时刷新"通道。
"""

from __future__ import annotations

from pathlib import Path

import akshare as ak
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "backend" / "app" / "data" / "stock_list.csv"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"[dump_stock_list] fetching A-share list via akshare ...")
    df: pd.DataFrame = ak.stock_info_a_code_name()
    if df is None or df.empty:
        raise RuntimeError("akshare 返回空股票列表，本次刷新中止")

    required = {"code", "name"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"akshare 返回字段缺失，期望包含 {required}，实际 {list(df.columns)}")

    df = df[["code", "name"]].copy()
    df["code"] = df["code"].astype(str).str.zfill(6)
    df["name"] = df["name"].astype(str)
    df = df.drop_duplicates(subset=["code"]).sort_values("code").reset_index(drop=True)

    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"[dump_stock_list] wrote {len(df)} rows -> {OUTPUT}")


if __name__ == "__main__":
    main()
