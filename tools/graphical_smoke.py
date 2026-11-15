"""Offscreen rendering and screen/action smoke test. Not a manual usability test."""
from pathlib import Path
from panda3d.core import Filename
from systems.mission import Mission

def run(app,g):
    out=Path('test-output');out.mkdir(exist_ok=True)
    g.saved['mission']=None;g.history=[];g.best=0;g.show('menu')
    def render(name):
        if g.screen=='simulation':g.refresh_telemetry()
        g.world.tick(1,g.mission if g.screen=='simulation' else None,True)
        # Render enough frames for deferred scene destruction and camera easing.
        for _ in range(5):app.taskMgr.step();app.graphicsEngine.renderFrame()
        app.win.saveScreenshot(Filename.fromOsSpecific(str((out/f'{name}.png').resolve())))
        print('RENDERED',name,flush=True)
    render('menu')
    for name in ('briefing','designer','planning','trajectory','review','guide','settings','credits'):
        g.show(name);render(name)
    g.launch();render('launch')
    for phase in ('Earth departure','Cruise','Mars arrival','Mapping'):
        g.mission.phase=phase;g.mission.phase_time=4;g.mission.captured=phase=='Mapping'
        if phase=='Mapping':
            g.mission.ops_seconds=g.mission.s['period']*.17;g.mission.fuel=16.66;g.mission.message='Orbit achieved. Select a target and arm the camera.'
        g.world.tick(.1,g.mission);render(phase.replace(' ','_'))
    g.mission.coverage=[80]*5;g.mission.collected=[100]*5;g.mission.returned=[90]*5;g.mission.finish('Graphical smoke test result.')
    g.record_result();render('results');g.show('compare');render('compare')
    g.show('designer');g.change_part(2);render('redesign')
    from tools.navigation_smoke import run as navigation
    navigation(g)
    print('GRAPHICAL SMOKE PASSED',flush=True)
    app.destroy()
