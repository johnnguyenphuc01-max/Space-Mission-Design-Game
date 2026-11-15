"""Invoked from graphical smoke: exercise actual UI callbacks and mission controls."""
from ursina import Button
from systems.engineering import COMPONENTS,default_design
from tests.test_mission import fly
from systems.mission import Mission

def run(g):
    def click(text):
        matches=[e for e in g.ui.children if isinstance(e,Button) and text in e.text]
        assert len(matches)==1,(text,[e.text for e in g.ui.children if isinstance(e,Button)])
        matches[0].on_mouse_enter();matches[0].on_mouse_exit();matches[0].on_click()
    g.show('menu');click('START MISSION');assert g.screen=='briefing'
    click('DESIGN SPACECRAFT');assert g.screen=='designer'
    for category in COMPONENTS:
        g.category=category
        for index in range(3):g.change_part(index);assert g.design[category]==index
    g.show('review');click('FIX BLOCKERS');assert g.screen=='planning'
    g.design=default_design();g.show('designer');click('PLAN MISSION')
    click('VIEW TRANSFER');click('BACK TO PLANNING');click('READINESS REVIEW');click('BEGIN MISSION')
    assert g.screen=='simulation'
    click('PAUSE');assert g.mission.paused
    click('PAUSE');assert not g.mission.paused
    click('SPEED');assert g.mission.speed==4
    click('VIEW');assert g.world.view==2
    click('SAVE & MENU');click('CONTINUE');assert g.screen=='simulation'
    click('END MISSION');assert g.screen=='confirm_end';click('KEEP FLYING')
    g.mission=fly(g.mission);assert g.mission.success
    g.record_result();click('COMPARE RUNS');click('BACK');click('REDESIGN');assert g.screen=='designer'
    g.show('menu');click('SETTINGS')
    for key in ('master','music','sfx','mute','reduced_motion','low_graphics'):g.setting(key)
    click('BACK');assert g.screen=='menu'
    # Restore defaults in the temporary smoke save.
    from core.save_manager import DEFAULT_SETTINGS
    g.settings.update(DEFAULT_SETTINGS);g.audio.apply()
    print('NAVIGATION CALLBACKS PASSED',flush=True)
