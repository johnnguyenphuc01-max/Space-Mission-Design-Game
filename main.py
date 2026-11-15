"""Run with Python 3.12. --smoke renders all screens without a desktop."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
SMOKE='--smoke' in sys.argv
resolution=(1280,720) if SMOKE else (1920,1080)
for arg in sys.argv[1:]:
    if arg.startswith('--size='):
        try:
            w,h=map(int,arg[7:].lower().split('x'))
            if not (800<=w<=7680 and 600<=h<=4320):raise ValueError
            resolution=(w,h)
        except ValueError:raise SystemExit('Use --size=1280x720 (minimum 800x600).')
if SMOKE:
    from panda3d.core import loadPrcFileData
    loadPrcFileData('', f'load-display p3headlessgl\naudio-library-name null\nwin-size {resolution[0]} {resolution[1]}\nsync-video false')
    os.environ['MARS_SAVE_DIR']=str(ROOT/'test-output/save')
from ursina import Ursina,window,application
app=Ursina(title='MARS: Mission Architect',size=resolution,fullscreen=False,borderless=False,development_mode=False,editor_ui_enabled=False,window_type='offscreen' if SMOKE else 'onscreen')
application.asset_folder=ROOT
window.color=(.012,.027,.047,1)
from ursina import camera
camera.ui_lens.set_film_size(20 * (resolution[0]/resolution[1] if SMOKE else window.aspect_ratio),20)
from core.game import Game
game=Game()
if SMOKE:
    from tools.graphical_smoke import run
    run(app,game)
else:app.run()
