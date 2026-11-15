"""Atomic local saves. Invalid content is rejected, never executed."""
import json,os,math
from pathlib import Path
from systems.engineering import COMPONENTS,MISSION
from systems.mission import Mission,PHASES
DEFAULT_SETTINGS=dict(master=.7,music=.45,sfx=.7,mute=False,reduced_motion=False,low_graphics=False)
def save_path():
    return Path(os.environ.get('MARS_SAVE_DIR',Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'MarsMissionArchitect'))/'save.json'
def valid_choices(d,options):
    return isinstance(d,dict) and set(d)==set(options) and all(type(d[k]) is int and 0<=d[k]<len(options[k]) for k in options)
def validate_mission(raw):
    if not isinstance(raw,dict):return None
    if not valid_choices(raw.get('design'),COMPONENTS):return None
    if not valid_choices(raw.get('config'),{k:MISSION[k] for k in ('launchers','transfers','orbits')}):return None
    try:
        m=Mission(**raw)
        if m.phase not in PHASES or type(m.selected) is not int or not 0<=m.selected<5 or m.speed not in (1,4,12):return None
        for a in (m.coverage,m.collected,m.returned):
            if not isinstance(a,list) or len(a)!=5 or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in a):return None
        if any(x>100 for x in m.coverage) or any(r>c for r,c in zip(m.returned,m.collected)):return None
        for key in ('phase_time','ops_seconds','battery','fuel','health','temperature','exposure'):
            x=getattr(m,key)
            if type(x) not in (int,float) or not math.isfinite(x):return None
        if not 0<=m.battery<=m.s['battery'] or not 0<=m.fuel<=m.s['fuel'] or not 0<=m.health<=100:return None
        if m.ops_seconds<0 or m.phase_time<0 or m.stored>m.s['storage']+.01:return None
        if any(type(getattr(m,k)) is not bool for k in ('imaging','transmitting','paused','captured')):return None
        if not isinstance(m.message,str) or not isinstance(m.outcome,str):return None
        return m
    except (TypeError,ValueError,KeyError,OverflowError):return None
class SaveManager:
    def __init__(self,path=None):self.path=Path(path) if path else save_path();self.error=''
    def load(self):
        default=dict(version=1,settings=DEFAULT_SETTINGS.copy(),mission=None,history=[],best=0)
        try:
            d=json.loads(self.path.read_text())
            if not isinstance(d,dict) or d.get('version')!=1:return default
            settings=d.get('settings',{})
            if isinstance(settings,dict):
                for k,v in settings.items():
                    if k in ('master','music','sfx') and type(v) in (int,float) and math.isfinite(v):default['settings'][k]=max(0,min(1,v))
                    elif k in DEFAULT_SETTINGS and type(v) is bool:default['settings'][k]=v
            m=validate_mission(d.get('mission'));default['mission']=m.to_dict() if m else None
            history=d.get('history',[])
            if isinstance(history,list):
                default['history']=[r for r in history[-10:] if isinstance(r,dict) and type(r.get('score')) is int and 0<=r['score']<=100 and type(r.get('cost')) in (int,float) and isinstance(r.get('success'),bool)]
            default['best']=max([r['score'] for r in default['history']]+[0])
        except (OSError,ValueError,TypeError):pass
        return default
    def save(self,data):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,allow_nan=False));tmp.replace(self.path)
            self.error='';return True
        except (OSError,ValueError) as e:self.error=str(e);return False
