import threading
from pathlib import Path
from typing import Callable

from flask import Flask, abort, jsonify, send_file
from flask_cors import CORS


def create_app(
    static_dir: str | None = None,
    on_shutdown: Callable[[], None] | None = None,
    on_heartbeat: Callable[[], None] | None = None,
):
    app = Flask(__name__)
    CORS(app)

    from .routes.chat import chat_bp
    from .routes.stock import stock_bp

    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(stock_bp, url_prefix="/api/stock")

    @app.post("/api/runtime/ping")
    def runtime_ping():
        if on_heartbeat:
            on_heartbeat()
        return jsonify({"ok": True})

    @app.post("/api/runtime/shutdown")
    def runtime_shutdown():
        if on_shutdown:
            threading.Thread(target=on_shutdown, daemon=True).start()
        return jsonify({"ok": True})

    if static_dir:
        static_path = Path(static_dir)

        @app.get("/")
        def serve_index():
            index = static_path / "index.html"
            if not index.is_file():
                abort(404)
            return send_file(index)

        @app.get("/assets/<path:filename>")
        def serve_assets(filename: str):
            asset = static_path / "assets" / filename
            if not asset.is_file():
                abort(404)
            return send_file(asset)

    return app
