# -*- mode: python ; coding: utf-8 -*-
# WatchDog Setup — PyInstaller spec
# Bundles: ui/installer_gui.py  +  app_icon.ico  +  WatchDog.exe (payload)  +  uninstall.exe (payload)

import os

ROOT  = os.path.abspath('.')
SETUP = os.path.join(ROOT, 'setup')
DIST  = os.path.join(ROOT, 'dist')

block_cipher = None

a = Analysis(
    [os.path.join(ROOT, 'ui', 'installer_gui.py')],
    pathex=[ROOT],
    binaries=[
        # Bundle the WatchDog service executable so the installer can extract it
        (os.path.join(DIST, 'WatchDog.exe'), '.'),
        # Bundle the uninstaller executable
        (os.path.join(DIST, 'uninstall.exe'), '.'),
    ],
    datas=[
        # Bundle the icon so iconbitmap() / wm_iconphoto() work from the EXE
        (os.path.join(SETUP, 'app_icon.ico'), '.'),
        (os.path.join(SETUP, 'branding.png'), '.'),
    ],
    hiddenimports=['PIL', 'PIL.Image', 'PIL.ImageTk', 'ui.styles', 'security.privilege', 'utils.system', 'core.install_engine', 'services.persistence'],
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
