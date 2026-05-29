import os
import sys
from pathlib import Path


def _app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _load_env() -> None:
    from dotenv import load_dotenv

    env_path = _app_base_dir() / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=True, encoding="utf-8")


def _prompts_dir() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "app", "prompts")
    return os.path.join(os.path.dirname(__file__), "prompts")


_load_env()


class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "3001"))
    PROMPTS_DIR = _prompts_dir()
