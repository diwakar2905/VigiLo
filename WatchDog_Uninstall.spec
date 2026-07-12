# -*- mode: python ; coding: utf-8 -*-
# WatchDog Uninstaller — PyInstaller spec
# Builds: ui/uninstaller_gui.py  ->  dist/uninstall.exe

import os

ROOT  = os.path.abspath('.')
SETUP = os.path.join(ROOT, 'setup')

block_cipher = None

a = Analysis(
    [os.path.join(ROOT, 'ui', 'uninstaller_gui.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(SETUP, 'app_icon.ico'), '.'),
    ],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'ui.styles', 'security.privilege', 'utils.system', 'core.uninstall_engine', 'services.persistence'],
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
    name='uninstall',
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
    icon=os.path.join(SETUP, 'app_icon.ico'),
    uac_admin=True,
    version=None,
)
