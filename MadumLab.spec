# -*- mode: python ; coding: utf-8 -*-

import sys, os
from PyInstaller.utils.hooks import collect_submodules
block_cipher = None

# 1) Votre script principal
script = "MadumLab.py"

# 2) Datas à embarquer (logo + icône)
datas = [
    ("MadumLab.png", "."),
    ("MadumLab.ico", "."),
]

# 3) Modules Qt à exclure
excludes = [
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtMultimedia",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtNetwork",
]

# 4) Hidden imports (tous les sous‑modules Qt widgets, styles, etc.)
hidden_imports = collect_submodules("PySide6")

a = Analysis(
    [script],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MadumLab",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,
    icon="MadumLab.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    name="MadumLab",
)
