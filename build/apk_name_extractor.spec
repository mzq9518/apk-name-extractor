# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
datas = []

for tool_jar in sorted((project_root / "tools").glob("apktool_*.jar")):
    datas.append((str(tool_jar), "tools"))

hiddenimports = ["tkinter", "tkinter.filedialog", "tkinter.messagebox", "tkinter.scrolledtext"]

a = Analysis(
    ["src/apk_name_extractor/launcher.py"],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="APK Name Extractor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

app = BUNDLE(
    exe,
    name="APK Name Extractor.app",
    icon=None,
    bundle_identifier=None,
)
