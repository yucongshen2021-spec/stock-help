# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import os
import akshare

spec_dir = Path(os.getcwd())
project_root = spec_dir.parent
frontend_dist = project_root / "frontend" / "dist"
akshare_file_fold = Path(akshare.__file__).resolve().parent / "file_fold"

block_cipher = None

a = Analysis(
    ["launcher.py"],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=[
        ("app/prompts", "app/prompts"),
        ("app/data", "app/data"),
        (str(frontend_dist), "frontend_dist"),
        (str(akshare_file_fold), "akshare/file_fold"),
    ],
    hiddenimports=[
        "flask",
        "flask_cors",
        "werkzeug",
        "dotenv",
        "akshare",
        "openai",
        "httpx",
        "pandas",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "torchvision",
        "scipy",
        "pytest",
        "sympy",
        "matplotlib",
        "IPython",
        "jupyter",
        "notebook",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="股票AI助手",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
