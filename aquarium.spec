# aquarium.spec
import os

block_cipher = None

a = Analysis(
    ['main_aquarium.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('underwater-ambience-6201.wav', '.'),
        ('bubbles-69893.mp3', '.'),
        ('balloon-inflate-4-184055.mp3', '.'),
        ('material-chest-open-394472.mp3', '.'),
	('shark.wav', '.'),
	('mockups.txt', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='aquarium',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='aquarium.ico',
)