"""Deterministic mission rules, independent of Ursina. One ops second = 60 simulated seconds."""
from dataclasses import dataclass,field,asdict
import math
from systems.engineering import *
PHASES=('Launch','Earth departure','Cruise','Mars arrival','Mapping','Results')
DURATIONS=(8,8,18,10)
@dataclass
class Mission:
    design:dict=field(default_factory=default_design)
    config:dict=field(default_factory=lambda:dict(launchers=1,transfers=0,orbits=0))
    phase:str='Launch'
    phase_time:float=0
    ops_seconds:float=0
    battery:float=-1
    fuel:float=-1
    health:float=100
    temperature:float=20
    selected:int=0
    imaging:bool=False
    transmitting:bool=False
    paused:bool=False
    speed:int=1
    exposure:float=0
    coverage:list=field(default_factory=lambda:[0.]*5)
    collected:list=field(default_factory=lambda:[0.]*5)
    returned:list=field(default_factory=lambda:[0.]*5)
    message:str='Launch sequence armed.'
    outcome:str=''
    captured:bool=False
    def __post_init__(self):
        if self.battery<0:self.battery=self.s['battery']
        if self.fuel<0:self.fuel=self.s['fuel']
    @property
    def s(self):return stats(self.design,self.config)
    @property
    def p(self):return parts(self.design)
    @property
    def stored(self):return sum(self.collected)-sum(self.returned)
    @property
    def fraction(self):return sum(self.returned)/sum(self.collected) if sum(self.collected)>0 else 0
    @property
    def eclipse(self):return self.ops_seconds%self.s['period']/self.s['period']>.65
    @property
    def link(self):return self.ops_seconds%self.s['period']/self.s['period']<.52
    @property
    def dusty(self):return 2*3600<=self.ops_seconds<5*3600 and self.selected in (0,2)
    @property
    def opportunity(self):
        # Abstract scheduled polar passes: deliberately not a geographic ground-track solver.
        f=(self.ops_seconds/self.s['period']+self.selected*.18)%1
        return f<.60 and not self.eclipse
    @property
    def generated_power(self):return 0 if self.eclipse else self.s['generation']
    @property
    def load(self):return self.s['base']+(self.p['camera']['power'] if self.imaging else 0)+(self.p['comms']['power'] if self.transmitting and self.link else 0)
    def select(self,i):
        if i!=self.selected:self.exposure=0
        self.selected=i
    def toggle_image(self):
        self.imaging=not self.imaging
        self.message='Imaging armed: waiting for a clear sunlit pass.' if self.imaging else 'Camera off. Battery can recover.'
    def toggle_radio(self):
        self.transmitting=not self.transmitting
        self.message='Downlink scheduled for Earth visibility windows.' if self.transmitting else 'Radio off.'
    def advance(self,dt):
        if self.paused or self.phase=='Results':return
        # Small fixed upper bound makes accelerated runs stable and reproducible.
        remaining=max(0,min(dt,1))*self.speed
        while remaining>1e-9 and self.phase!='Results':
            step=min(.1,remaining);remaining-=step;self._step(step)
    def _step(self,dt):
        if self.phase!='Mapping':
            self.phase_time+=dt
            index=PHASES.index(self.phase)
            if self.phase_time>=DURATIONS[index]:
                self.phase_time=0
                if self.phase=='Mars arrival':
                    s=self.s
                    if s['dv']+1e-6<s['required']:
                        self.finish('Capture failed: insufficient delta-v. Increase fuel or engine specific impulse.');return
                    self.fuel=s['mass']*math.exp(-s['required']/(G0*self.p['propulsion']['isp']))-s['dry']
                    self.captured=True
                self.phase=PHASES[index+1]
                self.message={'Earth departure':'Separation confirmed. Solar arrays deploying.', 'Cruise':'Navigation online. Coasting toward Mars.', 'Mars arrival':'Mars approach. Preparing capture burn.', 'Mapping':'Orbit achieved. Select a target and arm the camera.'}[self.phase]
            return
        sim_dt=dt*60;self.ops_seconds+=sim_dt
        self.battery=max(0,min(self.s['battery'],self.battery+(self.generated_power-self.load)*sim_dt/3600))
        heat=max(0,self.load-self.p['thermal']['limit'])/30
        self.temperature=max(-20,min(100,self.temperature+(heat-(self.temperature-18)/18)*sim_dt/3600))
        if self.battery<=0:
            self.health=max(0,self.health-sim_dt*.035);self.imaging=False;self.transmitting=False
            self.message='POWER LOSS: instruments shut down. Sunlight is needed to recover.'
        if self.temperature>55:self.health=max(0,self.health-sim_dt*.01)
        if self.imaging and self.battery>0:
            if self.dusty:self.message='Dust over target: select another region or wait until operations hour 5.'
            elif self.opportunity:
                self.exposure+=dt*self.p['computer']['processing']
                if self.exposure>=self.p['camera']['exposure']:
                    self.exposure=0;self.image()
            else:self.message='Camera armed. Waiting for a sunlit target pass.'
        if self.transmitting and self.link and self.battery>0:
            remaining=self.p['comms']['mbps']/8*sim_dt
            for i in range(5):
                amount=min(remaining,self.collected[i]-self.returned[i]);self.returned[i]+=amount;remaining-=amount
        if self.health<=0:self.finish('Spacecraft lost: battery depletion or overheating. Increase solar/thermal capacity and reduce loads.')
        elif all(c>=MISSION['minimum_coverage'] for c in self.coverage) and self.fraction>=MISSION['return_fraction']:
            self.finish('Mission complete: all five regions mapped and at least 80% of science data received.')
        elif self.ops_seconds>=MISSION['lifetime_hours']*3600:
            self.finish('Operations deadline reached. '+('Return more data: improve radio or schedule downlinks earlier.' if self.fraction<.8 else 'Map every region: use clear passes and improve imaging/pointing.'))
    def image(self):
        i=self.selected;cam=self.p['camera']; data=cam['data']
        if self.coverage[i]>=100:
            self.imaging=False;self.message='Region complete. Select the next target.';return
        if self.stored+data>self.s['storage']:
            self.imaging=False;self.message='STORAGE FULL: transmit data before taking another image.';return
        altitude=plans(self.config)[2]['peri']
        gain=min(55,40*(altitude/400)*min(1,15/self.s['resolution']))
        if self.temperature>45:gain*=.7
        self.coverage[i]=min(100,self.coverage[i]+gain)
        self.collected[i]+=data
        self.message=f"Image stored: {TARGETS[i]['name']} +{gain:.0f}% coverage. {data} MB added."
        if self.coverage[i]>=80:self.imaging=False
    def finish(self,reason):
        self.outcome=reason;self.phase='Results';self.imaging=False;self.transmitting=False
    @property
    def success(self):return self.captured and self.health>0 and all(c>=80 for c in self.coverage) and self.fraction>=.8
    def result(self):
        s=self.s
        science=sum(min(c/80,1) for c in self.coverage)/5
        # 50 mapping + 30 returned fraction + 10 capture + 10 budget efficiency.
        score=round(50*science+30*self.fraction+10*self.captured+10*max(0,1-s['cost']/MISSION['budget']))
        return dict(success=self.success,score=score,coverage=self.coverage.copy(),fraction=self.fraction,
                    fuel=self.fuel,cost=s['cost'],mass=s['mass'],outcome=self.outcome,design=self.design.copy(),config=self.config.copy())
    def to_dict(self):return asdict(self)
