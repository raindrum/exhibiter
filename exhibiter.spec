# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['exhibiter/gui.py'],
    binaries=[],
    datas=[
        ('README.md','.'),
        ('LICENSE.md','.'),
        ('exhibiter/template.docx','exhibiter')
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Exhibiter',
    icon='graphics/icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False
)

app = BUNDLE(exe,
    name='Exhibiter.app',
    icon='graphics/icon.icns',
    bundle_identifier='raindrum.exhibiter'
)
