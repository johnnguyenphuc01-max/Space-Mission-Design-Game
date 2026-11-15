"""Run on Windows in the game's venv; produces an application folder, not a lone EXE."""
import sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
if sys.platform!='win32':raise SystemExit('Build on Windows with Python 3.12. Cross-building is not supported.')
subprocess.run([sys.executable,'-m','pip','install','pyinstaller==6.22.0'],check=True)
args=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--console','--name','MarsMissionArchitect',
      '--add-data','assets;assets','--add-data','data;data','--add-data','docs;docs']
for package in ('ursina','panda3d','direct','gltf','simplepbr'):
    args+=['--collect-all',package]
args+=['--hidden-import','PIL.Image','main.py']
subprocess.run(args,cwd=root,check=True)
print('Created dist/MarsMissionArchitect. Keep its EXE and _internal folder together.')
print('Run the complete acceptance checklist on the target Windows laptop before distributing.')
