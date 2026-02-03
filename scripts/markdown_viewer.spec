# -*- mode: python ; coding: utf-8 -*-
import os
spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_dir = os.path.dirname(spec_dir)

block_cipher = None

a = Analysis(
    [os.path.join(project_dir, 'src', 'main.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'src', 'style.css'), '.'),
        (os.path.join(project_dir, 'src', 'assets'), 'assets'),
        (os.path.join(project_dir, 'src', 'templates'), 'templates'),
    ],
    hiddenimports=[
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MarkdownViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
