# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [
    ('app_icon.ico', '.'),
    ('app_icon.png', '.'),
    ('sorter_app', 'sorter_app'),
]
binaries = []
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'pymupdf',
    'fitz',
    'docx',
    'PIL',
    'sorter_app',
    'sorter_app.core',
    'sorter_app.core.classifier',
    'sorter_app.core.content_inspector',
    'sorter_app.core.duplicate_finder',
    'sorter_app.core.folder_watcher',
    'sorter_app.core.organizer_engine',
    'sorter_app.core.recycle_bin',
    'sorter_app.core.rule_engine',
    'sorter_app.core.undo_manager',
    'sorter_app.ui',
    'sorter_app.ui.assets',
    'sorter_app.ui.drop_zone_widget',
    'sorter_app.ui.duplicate_dialog',
    'sorter_app.ui.floating_widget',
    'sorter_app.ui.history_dialog',
    'sorter_app.ui.main_window',
    'sorter_app.ui.rule_dialog',
    'sorter_app.ui.theme',
]

a = Analysis(
    ['run_sorter.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'pandas', 'scipy', 'statsmodels', 'pyarrow'],
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
    name='Titus_OmniSort_Pro',
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
    icon='app_icon.ico',
)
