# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\FileDragManager', 'FileDragManager'), ('C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\file_viewer_gui', 'file_viewer_gui'), ('C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\Word Processing', 'Word Processing')]
binaries = []
hiddenimports = ['PyQt6', 'PyQt6.QtWidgets', 'PyQt6.QtCore', 'PyQt6.QtGui', 'ui_components', 'text_editor', 'FileDragManager.main', 'FileDragManager.dialogs', 'FileDragManager.history', 'FileDragManager.utils', 'os', 'sys', 'shutil']
tmp_ret = collect_all('FileDragManager')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\integrated_app\\main.py'],
    pathex=['C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\file_viewer_gui', 'C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\Word Processing', 'C:\\Users\\28162\\Desktop\\git\\Note-Resource-Explorer\\FileDragManager'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.datas,
    [],
    name='综合应用',
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
)
