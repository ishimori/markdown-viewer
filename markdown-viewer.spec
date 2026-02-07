# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/templates', 'templates'), ('src/style.css', '.'), ('src/icon.ico', '.'), ('HELP.md', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'PIL', 'Pillow', 'PyQt6.QtBluetooth', 'PyQt6.QtNfc', 'PyQt6.QtSensors', 'PyQt6.QtSerialPort', 'PyQt6.QtTest', 'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets', 'PyQt6.Qt3DCore', 'PyQt6.Qt3DRender', 'PyQt6.QtCharts', 'PyQt6.QtDataVisualization'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='markdown-viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\icon.ico'],
)
