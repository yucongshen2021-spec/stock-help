"""CI / 本地调试用的 Flask 启动脚本。

与 backend/launcher.py 区别：
- 不启动 webbrowser；
- 不启动心跳 watchdog（不会因为没心跳自动退出）；
- 不做端口占用清理；
- 显式注入 on_shutdown，让 /api/runtime/shutdown 真正能退出进程。

用法：python scripts/ci_server.py
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
FRONTEND_DIST = ROOT / "frontend" / "dist"

sys.path.insert(0, str(BACKEND))


def _shutdown() -> None:
    threading.Timer(0.3, lambda: os._exit(0)).start()


def main() -> None:
    from app import create_app  # noqa: E402
    from app.config import Config  # noqa: E402

    static_dir = str(FRONTEND_DIST) if FRONTEND_DIST.is_dir() else None
    app = create_app(static_dir=static_dir, on_shutdown=_shutdown)
    print(f"[ci_server] starting on 127.0.0.1:{Config.FLASK_PORT} static={static_dir}")
    app.run(host="127.0.0.1", port=Config.FLASK_PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
