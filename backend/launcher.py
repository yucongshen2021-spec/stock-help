import ctypes
import logging
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path


def _app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _log_path() -> Path:
    return _app_dir() / "startup.log"


def _setup_logging() -> None:
    logging.basicConfig(
        filename=str(_log_path()),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
        force=True,
    )


def _fix_stdio() -> None:
    if not getattr(sys, "frozen", False):
        return
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _show_error(message: str) -> None:
    logging.error(message)
    if sys.platform == "win32":
        ctypes.windll.user32.MessageBoxW(0, message, "股票AI助手", 0x10)


def _resolve_frontend_dist() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        dist = Path(sys._MEIPASS) / "frontend_dist"
    else:
        dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

    if not dist.is_dir():
        raise FileNotFoundError(f"未找到前端静态文件目录: {dist}")

    index = dist / "index.html"
    if not index.is_file():
        raise FileNotFoundError(f"未找到 index.html: {index}")

    return dist


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _pids_listening_on(port: int) -> list[int]:
    if sys.platform != "win32":
        return []
    try:
        raw = subprocess.check_output(
            ["netstat", "-ano", "-p", "TCP"],
            creationflags=0x08000000,
            stderr=subprocess.DEVNULL,
        )
        out = raw.decode(errors="ignore")
    except Exception:
        return []

    pids: set[int] = set()
    suffix = f":{port}"
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        if parts[0].upper() != "TCP":
            continue
        local_addr = parts[1]
        state = parts[3]
        if state.upper() != "LISTENING":
            continue
        if not local_addr.endswith(suffix):
            continue
        try:
            pids.add(int(parts[4]))
        except ValueError:
            continue
    return sorted(pids)


def _kill_pid(pid: int) -> bool:
    if sys.platform != "win32":
        return False
    PROCESS_TERMINATE = 0x0001
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not handle:
        return False
    try:
        ok = ctypes.windll.kernel32.TerminateProcess(handle, 1)
        return bool(ok)
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def _ensure_port_free(port: int) -> None:
    if _port_available("127.0.0.1", port):
        return
    pids = _pids_listening_on(port)
    logging.info("port %d in use by PIDs: %s", port, pids)
    for pid in pids:
        ok = _kill_pid(pid)
        logging.info("kill PID %d -> %s", pid, ok)
    for _ in range(20):
        time.sleep(0.2)
        if _port_available("127.0.0.1", port):
            logging.info("port %d freed", port)
            return
    raise RuntimeError(
        f"端口 {port} 仍被占用，无法关闭占用进程：{pids}"
    )


def _open_browser_later(url: str, delay_seconds: float = 1.5) -> None:
    def _worker():
        time.sleep(delay_seconds)
        webbrowser.open(url)

    threading.Thread(target=_worker, daemon=True).start()


def _start_runtime_watchdog(timeout_seconds: int = 60):
    state = {"last_ping": time.monotonic()}
    lock = threading.Lock()

    def heartbeat():
        with lock:
            state["last_ping"] = time.monotonic()

    def shutdown():
        logging.info("received shutdown request, exiting process")
        time.sleep(0.2)
        os._exit(0)

    def watchdog():
        while True:
            time.sleep(2)
            with lock:
                idle_seconds = time.monotonic() - state["last_ping"]
            if idle_seconds > timeout_seconds:
                logging.info(
                    "heartbeat timeout reached: idle_seconds=%.2f timeout=%d",
                    idle_seconds,
                    timeout_seconds,
                )
                os._exit(0)

    threading.Thread(target=watchdog, daemon=True).start()
    return heartbeat, shutdown


def main() -> None:
    from app import create_app
    from app.config import Config

    static_dir = _resolve_frontend_dist()
    env_path = _app_dir() / ".env"

    logging.info("app_dir=%s", _app_dir())
    logging.info("static_dir=%s", static_dir)
    logging.info("env_path=%s exists=%s", env_path, env_path.is_file())

    _ensure_port_free(Config.FLASK_PORT)

    heartbeat, shutdown = _start_runtime_watchdog(timeout_seconds=60)
    app = create_app(
        static_dir=str(static_dir),
        on_shutdown=shutdown,
        on_heartbeat=heartbeat,
    )
    url = f"http://127.0.0.1:{Config.FLASK_PORT}"
    logging.info("starting server at %s", url)
    _open_browser_later(url)
    app.run(host="127.0.0.1", port=Config.FLASK_PORT, debug=False, threaded=True)


if __name__ == "__main__":
    _setup_logging()
    _fix_stdio()
    try:
        main()
    except Exception:
        msg = traceback.format_exc()
        _show_error(f"启动失败，详情已写入:\n{_log_path()}\n\n{msg}")
        sys.exit(1)
