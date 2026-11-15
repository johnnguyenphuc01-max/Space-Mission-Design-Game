"""Authoring script: fictional balanced hardware, not NASA specifications."""
import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]/'data'
c={}
def category(key, rows):
    c[key]=[dict(id=f'{key}_{i}',name=r[0],mass=r[1],cost=r[2],power=r[3],description=r[4],**r[5]) for i,r in enumerate(rows)]
category('solar',[
('Compact wings',30,8,0,'Light and cheap; limited electricity at Mars.',dict(watts=520,span=1.5)),
('Mapper wings',65,18,0,'Balanced arrays. Output falls with distance squared.',dict(watts=1250,span=2.5)),
('Deep-space wings',110,30,0,'More electricity, more launch mass and cost.',dict(watts=2200,span=3.3))])
category('battery',[
('Reserve 300',12,4,0,'Small eclipse reserve; avoid running camera and radio together.',dict(wh=300)),
('Reserve 800',30,9,0,'Stores daytime energy for eclipse operations.',dict(wh=800)),
('Reserve 1600',60,17,0,'Longer operations in shadow, with a mass penalty.',dict(wh=1600))])
category('camera',[
('Survey imager',20,8,45,'Wide coverage, modest data. 12 m/pixel at 400 km.',dict(gsd=12,data=180,exposure=8)),
('Mapping imager',45,20,110,'Sharper images need more power and storage.',dict(gsd=5,data=420,exposure=10)),
('Precision imager',85,38,240,'Very sharp but data-heavy; needs accurate pointing.',dict(gsd=1,data=1400,exposure=16))])
category('comms',[
('Low-gain link',8,4,25,'Very slow downlink can strand valuable images onboard.',dict(mbps=.018,dish=.55)),
('Mapper dish',22,12,70,'Directional antenna with useful data return.',dict(mbps=3,dish=1)),
('High-gain dish',40,25,120,'Fast downlink, but higher power draw and cost.',dict(mbps=8,dish=1.5))])
category('computer',[
('Compact avionics',8,5,22,'Limited storage and slower image processing.',dict(storage=900,processing=.8)),
('Science avionics',15,12,35,'Balanced storage and processing speed.',dict(storage=4200,processing=1)),
('Data workstation',30,22,65,'Holds many large images; uses extra power.',dict(storage=12000,processing=1.3))])
category('propulsion',[
('Monopropellant',25,8,0,'Simple thruster; low specific impulse uses more fuel.',dict(isp=220)),
('Bipropellant',40,18,0,'Higher specific impulse improves manoeuvre efficiency.',dict(isp=325)),
('Efficient bipropellant',55,30,0,'Efficient chemical engine with higher dry mass and cost.',dict(isp=350))])
category('fuel',[
('Lean tank',12,5,0,'Only 120 kg propellant: capture may be impossible.',dict(fuel=120)),
('Transfer tank',22,10,0,'450 kg propellant for capture and corrections.',dict(fuel=450)),
('Extended tank',35,17,0,'650 kg propellant adds capability and launch mass.',dict(fuel=650))])
category('attitude',[
('Basic wheels',8,5,12,'Coarse pointing blurs high-resolution images.',dict(blur=10)),
('Precision wheels',18,12,20,'Accurate pointing keeps mapping images sharp.',dict(blur=2)),
('Fine guidance',30,24,30,'Sub-metre pointing contribution; higher cost.',dict(blur=.4))])
category('thermal',[
('Passive blanket',8,3,5,'Low power but limited heat rejection during intensive work.',dict(limit=220)),
('Mapper radiator',20,9,15,'Rejects the heat of normal mapping operations.',dict(limit=420)),
('Active thermal loop',38,19,35,'Handles high power instruments with extra mass.',dict(limit=650))])
(D/'components.json').write_text(json.dumps(c,indent=2))
plans={
'launchers':[
 dict(name='Aster 1',cost=30,capacity=800,c3=9,description='Fictional light Mars injector; payload capacity is at the stated C3, not LEO.'),
 dict(name='Aster 2',cost=50,capacity=1400,c3=16,description='Fictional medium Mars injector. Higher departure energy and payload.'),
 dict(name='Aster Heavy',cost=85,capacity=2200,c3=25,description='Fictional heavy injector; expensive performance reserve.')],
 'transfers':[
 dict(name='Hohmann window',days=259,c3=8.7,vinf=2.65,correction=80,description='Near circular, coplanar minimum-energy reference. Launch at a suitable planetary alignment.'),
 dict(name='Fast opportunity',days=210,c3=15,vinf=3.4,correction=140,description='Illustrative faster transfer: more departure energy and harder Mars capture.'),
 dict(name='Off-window attempt',days=300,c3=23,vinf=4.2,correction=280,description='Illustrative poor alignment: expensive departure and arrival; no ephemeris optimization.')],
 'orbits':[
 dict(name='Low mapping',peri=300,apo=300,description='Sharp images but narrow swath. Higher capture delta-v.'),
 dict(name='Regional mapper',peri=600,apo=600,description='Wider swath and longer period; lower surface resolution.'),
 dict(name='Elliptical survey',peri=400,apo=8000,description='Images at periapsis; long period reduces imaging opportunities.')],
 'budget':260,'lifetime_hours':24,'minimum_coverage':80,'return_fraction':.8}
(D/'missions.json').write_text(json.dumps(plans,indent=2))
targets=[
 dict(name='Jezero',lat=18.38,lon=77.58,reason='Ancient lake and river delta; sediment layers record past water.'),
 dict(name='Gale',lat=-4.49,lon=137.42,reason='Layered mountain records changing environments over time.'),
 dict(name='Eberswalde',lat=-23.90,lon=326.74,reason='Preserved river delta, a record of sediment transport.'),
 dict(name='Holden',lat=-26.40,lon=325.16,reason='Flood deposits and alluvial fans reveal water activity.'),
 dict(name='Mawrth Vallis',lat=23.99,lon=341.04,reason='Clay-rich layers record water-rock interactions.')]
(D/'scientific_targets.json').write_text(json.dumps(targets,indent=2))
