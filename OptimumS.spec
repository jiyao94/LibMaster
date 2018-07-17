# -*- mode: python -*-

block_cipher = None


a = Analysis(['OptimumS.py'],
             pathex=['C:\\Users\\XH\\source\\repos\\OptimumS'],
             binaries=[],
             datas=[('./ui','./pyforms/gui/controls')],
             hiddenimports=['pyforms.settings','pyforms.gui.settings','PyQt5.sip'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='OptimumS',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='OptimumS')
