# -*- mode: python ; coding: utf-8 -*-
# WatchDog Payload — PyInstaller spec
# Builds: main.py  ->  dist/WatchDog.exe

import os

ROOT = os.path.abspath('.')
SETUP = os.path.join(ROOT, 'setup')

a = Analysis(
    ['main.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pyautogui', 'PIL', 'psutil', 'pyaudio', 'win32evtlog', 'win32gui', 'win32con', 'win32com',
        'api.telegram_client', 'config.manager', 'config.schema', 'logs.logger',
        'security.sanitizer', 'security.privilege', 'services.persistence', 'services.upload_queue',
        'services.telegram_polling', 'core.engine', 'core.event_monitor', 'core.shutdown_listener',
        'modules.base', 'modules.camera', 'modules.audio', 'modules.screenshot', 'modules.locking',
        'modules.locate', 'modules.system_stats', 'modules.file_manager', 'modules.speech'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WatchDog',
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
)
