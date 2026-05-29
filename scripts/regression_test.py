"""跨平台接口回归脚本。

预期已有一个运行中的后端服务监听 http://127.0.0.1:3001。
- 所有外部数据源接口（行情、K线、指标、分析、新闻）失败即标记 FAIL，不做兜底；
- AI 聊天接口若 DEEPSEEK_API_KEY 未配置，则显式 SKIP（不会算成 FAIL），其余情况按返回判断；
- 退出码：仅在出现 FAIL 时返回 1。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable, Optional


BASE = os.environ.get("BASE", "http://127.0.0.1:3001")
DEFAULT_TIMEOUT = 30
CHAT_TIMEOUT = 60


@dataclass
class Result:
    name: str
    status: str  # PASS / FAIL / SKIP
    detail: str


results: list[Result] = []


def _record(name: str, status: str, detail: str) -> None:
    results.append(Result(name=name, status=status, detail=detail))


def _snippet(body: bytes, limit: int = 400) -> str:
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception:
        text = repr(body[:limit])
    text = text.replace("\n", " ").strip()
    return text[:limit]


def _get(name: str, url: str, predicate: Callable[[int, bytes], bool], timeout: int = DEFAULT_TIMEOUT) -> Optional[tuple[int, bytes]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = r.read()
            ok = predicate(r.status, body)
            detail = f"HTTP {r.status}, len={len(body)}"
            if not ok:
                detail += f" | body={_snippet(body)}"
            _record(name, "PASS" if ok else "FAIL", detail)
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        ok = predicate(e.code, body)
        detail = f"HTTP {e.code}"
        if not ok:
            detail += f" | body={_snippet(body)}"
        _record(name, "PASS" if ok else "FAIL", detail)
    except Exception as e:
        _record(name, "FAIL", f"{type(e).__name__}: {e}")
    return None


def _post(name: str, url: str, body: str, predicate: Callable[[int, bytes], bool], timeout: int = DEFAULT_TIMEOUT) -> None:
    req = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
            ok = predicate(r.status, content)
            detail = f"HTTP {r.status}, len={len(content)}"
            if not ok:
                detail += f" | body={_snippet(content)}"
            _record(name, "PASS" if ok else "FAIL", detail)
    except urllib.error.HTTPError as e:
        content = e.read() if hasattr(e, "read") else b""
        ok = predicate(e.code, content)
        detail = f"HTTP {e.code}"
        if not ok:
            detail += f" | body={_snippet(content)}"
        _record(name, "PASS" if ok else "FAIL", detail)
    except Exception as e:
        _record(name, "FAIL", f"{type(e).__name__}: {e}")


def _wait_ready(timeout_seconds: int = 60) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            req = urllib.request.Request(
                BASE + "/api/runtime/ping",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main() -> int:
    if not _wait_ready():
        print("ERROR: backend not reachable at", BASE, file=sys.stderr)
        return 2

    _get(
        "GET /",
        BASE + "/",
        lambda s, b: s == 200 and (b"<html" in b.lower() or b"script" in b.lower()),
    )

    indexed = _get(
        "GET / (re-fetch for asset extraction)",
        BASE + "/",
        lambda s, b: s == 200,
    )
    if indexed is not None:
        _, body = indexed
        m = re.search(rb'(?:src|href)="(/assets/[^"]+)"', body)
        if m:
            asset_path = m.group(1).decode("utf-8")
            _get(
                "GET frontend asset",
                BASE + asset_path,
                lambda s, b: s == 200 and len(b) > 1000,
            )
        else:
            _record("GET frontend asset", "FAIL", "index.html 未匹配到 /assets/ 资源")

    _post(
        "POST /api/runtime/ping",
        BASE + "/api/runtime/ping",
        "{}",
        lambda s, b: s == 200 and b'"ok"' in b and b"true" in b,
    )

    _get(
        "GET /api/stock/search?q=贵州",
        BASE + "/api/stock/search?q=" + urllib.parse.quote("贵州"),
        lambda s, b: s == 200 and b'"data"' in b,
    )

    _get(
        "GET /api/stock/quote/600519",
        BASE + "/api/stock/quote/600519",
        lambda s, b: s == 200 and b'"price"' in b and b'"source"' in b,
    )

    _get(
        "GET /api/stock/kline/600519",
        BASE + "/api/stock/kline/600519?period=daily&count=30",
        lambda s, b: s == 200 and b'"date"' in b and b'"close"' in b,
    )

    _get(
        "GET /api/stock/indicators/600519",
        BASE + "/api/stock/indicators/600519?count=60",
        lambda s, b: s == 200 and (b'"macd"' in b or b'"rsi"' in b or b'"data"' in b),
    )

    _get(
        "GET /api/stock/analysis/600519",
        BASE + "/api/stock/analysis/600519",
        lambda s, b: s == 200 and (b'"summary"' in b or b'"signals"' in b or b'"data"' in b),
    )

    _get(
        "GET /api/stock/news/600519",
        BASE + "/api/stock/news/600519?count=5",
        lambda s, b: s == 200 and (b'"title"' in b or b'"data"' in b),
    )

    _get(
        "GET /api/stock/quote/000000 (invalid)",
        BASE + "/api/stock/quote/000000",
        lambda s, b: 400 <= s < 500,
    )

    if os.environ.get("DEEPSEEK_API_KEY"):
        payload = json.dumps({"messages": [{"role": "user", "content": "只回复：测试通过"}]}, ensure_ascii=False)
        _post(
            "POST /api/chat (stream)",
            BASE + "/api/chat",
            payload,
            lambda s, b: s == 200 and (b"data:" in b or len(b) > 0),
            timeout=CHAT_TIMEOUT,
        )
    else:
        _record("POST /api/chat (stream)", "SKIP", "DEEPSEEK_API_KEY 未设置")

    _post(
        "POST /api/runtime/shutdown",
        BASE + "/api/runtime/shutdown",
        "{}",
        lambda s, b: s == 200 and b'"ok"' in b,
    )

    print("=== REGRESSION RESULTS ===")
    for r in results:
        print(f"[{r.status}] {r.name} - {r.detail}")

    fails = sum(1 for r in results if r.status == "FAIL")
    skips = sum(1 for r in results if r.status == "SKIP")
    passes = sum(1 for r in results if r.status == "PASS")
    print("=== SUMMARY ===")
    print(f"total={len(results)} passed={passes} failed={fails} skipped={skips}")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
