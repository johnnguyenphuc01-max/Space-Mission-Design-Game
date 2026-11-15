"""SI mass/power/energy; orbital calculations explicitly use km and seconds."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=json.loads((ROOT/'data/components.json').read_text())
MISSION=json.loads((ROOT/'data/missions.json').read_text())
TARGETS=json.loads((ROOT/'data/scientific_targets.json').read_text())
MU=42828.0
RADIUS=3389.5
G0=9.80665

def default_design(): return {key:1 for key in COMPONENTS}
def parts(design): return {k:v[design.get(k,1)] for k,v in COMPONENTS.items()}
def plans(config):
    return tuple(MISSION[k][config.get(k,0)] for k in ('launchers','transfers','orbits'))
def orbit_period(orbit):
    a=RADIUS+(orbit['peri']+orbit['apo'])/2
    return 2*math.pi*math.sqrt(a**3/MU)
def capture_dv(orbit,transfer):
    rp=RADIUS+orbit['peri']; a=RADIUS+(orbit['peri']+orbit['apo'])/2
    return (math.sqrt(transfer['vinf']**2+2*MU/rp)-math.sqrt(MU*(2/rp-1/a)))*1000+transfer['correction']
def hohmann_days():
    return 365.256/2*((1+1.524)/2)**1.5

def stats(design,config):
    p=parts(design); launch,transfer,orbit=plans(config)
    dry=150+sum(x['mass'] for x in p.values()); fuel=p['fuel']['fuel']; wet=dry+fuel
    base=55+sum(p[k]['power'] for k in ('computer','attitude','thermal'))
    return dict(dry=dry,mass=wet,fuel=fuel,cost=18+sum(x['cost'] for x in p.values())+launch['cost'],
        generation=p['solar']['watts']/1.524**2,base=base,peak=base+p['camera']['power']+p['comms']['power'],
        battery=p['battery']['wh'],storage=p['computer']['storage'],rate=p['comms']['mbps'],
        dv=G0*p['propulsion']['isp']*math.log(wet/dry),required=capture_dv(orbit,transfer),
        period=orbit_period(orbit),resolution=math.hypot(p['camera']['gsd'],p['attitude']['blur'])*orbit['peri']/400)

def review(design,config):
    s=stats(design,config); l,t,o=plans(config); errors=[]; warnings=[]
    if s['mass']>l['capacity']: errors.append('Payload exceeds Mars injection capacity. Choose a larger launcher or lighter hardware.')
    if s['cost']>MISSION['budget']: errors.append('Budget exceeded. Reduce equipment or launcher cost.')
    if t['c3']>l['c3']: errors.append('Launcher cannot deliver this departure C3. Choose a stronger launcher or Hohmann window.')
    if s['dv']<s['required']: warnings.append('INSUFFICIENT DELTA-V: Mars capture will fail. Add fuel or improve engine efficiency.')
    if s['generation']*.65<s['base']: warnings.append('POWER DEFICIT: eclipse-averaged solar power is below idle demand. Fit larger wings.')
    elif s['generation']<s['peak']: warnings.append('Peak load exceeds sunlight generation. Alternate imaging and transmission.')
    if s['rate']<.1: warnings.append('SLOW RADIO: the 24-hour operations limit may leave most data onboard.')
    if s['resolution']>20: warnings.append('Image sharpness limits coverage. Improve camera, pointing, or lower the orbit.')
    return errors,warnings
