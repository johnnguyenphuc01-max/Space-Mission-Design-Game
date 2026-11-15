import math,json
import pytest
from systems.engineering import *
from systems.mission import Mission
from core.save_manager import SaveManager,validate_mission,DEFAULT_SETTINGS

def fly(m,steps=20000):
    m.speed=12
    for _ in range(steps):
        if m.phase=='Mapping':
            choices=[i for i,c in enumerate(m.coverage) if c<80]
            if choices:
                # Avoid dust, preserve partially integrated exposure when possible.
                if m.selected not in choices or m.dusty:
                    choices.sort(key=lambda i:(2*3600<=m.ops_seconds<5*3600 and i in (0,2),i))
                    m.select(choices[0])
                if m.stored+m.p['camera']['data']<=m.s['storage']:m.imaging=True
            m.transmitting=True
        m.advance(.5)
        if m.phase=='Results':return m
    raise AssertionError('Mission did not terminate')

def test_reference_physics():
    assert 258<hohmann_days()<260
    assert 110<orbit_period(MISSION['orbits'][0])/60<115
    assert 2000<capture_dv(MISSION['orbits'][0],MISSION['transfers'][0])<2200

def test_mass_and_rocket_equation():
    d=default_design();s=stats(d,dict(launchers=1))
    assert s['mass']==s['dry']+450
    assert s['dv']==pytest.approx(G0*325*math.log(s['mass']/s['dry']))
    d['fuel']=2
    assert stats(d,dict(launchers=1))['dv']>s['dv']
    assert stats(d,dict(launchers=1))['mass']>s['mass']

def test_component_tradeoffs():
    d=default_design();cfg=dict(launchers=1);a=stats(d,cfg)
    d['solar']=2;b=stats(d,cfg)
    assert b['mass']>a['mass'] and b['generation']>a['generation'] and b['cost']>a['cost']
    d['camera']=2;c=stats(d,cfg)
    assert c['peak']>b['peak'] and c['resolution']<b['resolution']

def test_default_success():
    m=fly(Mission())
    assert m.success,m.outcome
    assert m.fuel>=0 and m.fraction>=.8 and m.battery>0
    assert sum(m.returned)<=sum(m.collected)
    assert 90<=m.result()['score']<=100

def test_insufficient_fuel():
    d=default_design();d['fuel']=0
    m=fly(Mission(design=d))
    assert not m.captured and not m.success and 'delta-v' in m.outcome

def test_slow_radio_fails():
    d=default_design();d['comms']=0
    m=fly(Mission(design=d))
    assert m.captured and not m.success and m.fraction<.8
    assert 'Return more data' in m.outcome

def test_underpowered_failure():
    d=default_design();d['solar']=0;d['battery']=0;d['camera']=2
    m=fly(Mission(design=d))
    assert not m.success
    assert m.health==0 or m.ops_seconds>=24*3600

def test_storage_and_return_bounds():
    m=Mission();m.phase='Mapping'
    for i in range(30):m.selected=i%5;m.image()
    assert 0<=m.stored<=m.s['storage']
    m.transmitting=True;m.speed=12
    for _ in range(100):m.advance(1)
    assert m.stored>=-1e-7
    assert all(r<=c for r,c in zip(m.returned,m.collected))

def test_pause_and_speed():
    m=Mission();m.paused=True;m.advance(1);assert m.phase_time==0
    m.paused=False;m.speed=4;m.advance(1);assert m.phase_time==pytest.approx(4)

def test_plan_blockers():
    d=default_design();c=dict(launchers=0,transfers=2,orbits=0)
    e,w=review(d,c);assert any('C3' in x for x in e)
    d={k:2 for k in COMPONENTS};e,w=review(d,c);assert any('Budget' in x for x in e)

def test_orbit_choice():
    d=default_design();lo=stats(d,dict(orbits=0));hi=stats(d,dict(orbits=1));ell=stats(d,dict(orbits=2))
    assert hi['resolution']>lo['resolution'] and hi['period']>lo['period']
    assert ell['required']<lo['required'] and ell['period']>hi['period']

def test_save_round_trip_and_resume(tmp_path):
    m=Mission();m.phase='Mapping';m.captured=True;m.ops_seconds=7000;m.image()
    store=SaveManager(tmp_path/'save.json');data=dict(version=1,settings=DEFAULT_SETTINGS,mission=m.to_dict(),history=[],best=0)
    assert store.save(data)
    restored=Mission(**store.load()['mission']);assert restored.to_dict()==m.to_dict()
    assert fly(restored).success

def test_corrupted_saves(tmp_path):
    store=SaveManager(tmp_path/'save.json')
    for content in ('{bad','[]','{"version":1,"mission":{}}','{"version":1,"settings":null}'):
        store.path.write_text(content);assert store.load()['mission'] is None
    for field,value in [('design',{'solar':-1}),('battery',float('nan')),('selected',99),('coverage',[999]*5),('speed',999)]:
        d=Mission().to_dict();d[field]=value;assert validate_mission(d) is None

def test_fixed_step_equivalence():
    a=Mission();b=Mission()
    for m in (a,b):m.phase='Mapping';m.captured=True;m.transmitting=True
    for _ in range(100):a.advance(.1)
    for _ in range(10):b.advance(1)
    assert a.ops_seconds==pytest.approx(b.ops_seconds)
    assert a.battery==pytest.approx(b.battery)

def test_dust_deterministic_and_eclipse():
    m=Mission();m.phase='Mapping';m.ops_seconds=3*3600;assert m.dusty
    m.select(1);assert not m.dusty
    m.ops_seconds=m.s['period']*.8;assert m.eclipse and m.generated_power==0 and not m.link
