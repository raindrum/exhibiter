# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['exhibiter.py'],
             pathex=['/home/simon/Shared/Development/exhibiter'],
             binaries=[],
             datas=[('README.md','.'),
                    ('LICENSE.md','.'),
                    ('assets','assets')],
             hiddenimports=['pdfrw'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='exhibiter',
          icon='icon.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='exhibiter')
