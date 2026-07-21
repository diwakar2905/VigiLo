# -*- mode: python ; coding: utf-8 -*-
# WatchDog Setup — PyInstaller spec
# Bundles: install_wizard.py  +  app_icon.ico  +  WatchDog.exe (payload)

import os

ROOT  = os.path.abspath('.')
SETUP = os.path.join(ROOT, 'setup')
DIST  = os.path.join(ROOT, 'dist')

block_cipher = None

a = Analysis(
    [os.path.join(SETUP, 'install_wizard.py')],
    pathex=[ROOT, SETUP],
    binaries=[
        # Bundle the WatchDog service executable so the installer can extract it
        (os.path.join(DIST, 'WatchDog.exe'), '.'),
    ],
    datas=[
        # Bundle the icon so iconbitmap() / wm_iconphoto() work from the EXE
        (os.path.join(SETUP, 'app_icon.ico'), '.'),
    ],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk'],
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
    name='WatchDog_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(SETUP, 'app_icon.ico'),
    uac_admin=True,            # request UAC elevation on launch
    version=None,
)
