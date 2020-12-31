# -*- mode: python ; coding: utf-8 -*-

# 本文件用于打包 Windows 程序
# 建议在虚拟环境下打包
# pyinstaller --clean -F build_exe.spec

block_cipher = None


a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('cli/config.json','cli')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['altgraph', 'pip', 'setuptools', 'pyinstaller','pyinstaller-hooks-contrib','future','pefile', 'pywin32-ctypes'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='CDUT选课',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='CDUT选课')
