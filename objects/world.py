import math,random
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from objects.spacecraft import Spacecraft
from systems.engineering import ROOT,TARGETS,plans
CYAN=color.rgb32(56,189,248)
def line(points,c=CYAN,parent=scene,thickness=1):
    return Entity(parent=parent,model=Mesh(vertices=points,mode='line',thickness=thickness),color=c)
def ring(radius,parent=scene,c=CYAN):
    return line([(radius*math.cos(i*math.tau/180),0,radius*math.sin(i*math.tau/180)) for i in range(181)],c,parent)
class World:
    def __init__(self):
        self.root=Entity();self.angle=0;self.mode='menu';self.view=1;self.zoom=13
        self.camera_yaw=0;self.camera_pitch=12
        random.seed(12);v=[];cols=[]
        for i in range(900):
            q=Vec3(random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1)).normalized()*80
            v.append(q);cols.append(color.rgb32(100+random.randrange(155),160+random.randrange(95),255))
        self.stars=Entity(model=Mesh(vertices=v,colors=cols,mode='point',thickness=1.5))
        AmbientLight(color=color.rgb32(95,108,132))
        light=DirectionalLight(color=color.rgb32(255,225,194));light.look_at(Vec3(1,-1,1))
        self.ship=None;self.markers=[]
    def clear(self):
        destroy(self.root);self.root=Entity();self.markers=[];self.ship=None
    def setup(self,mode,design,config):
        self.clear();self.mode=mode;self.config=config;self.zoom=13;self.camera_yaw=0;self.camera_pitch=12
        if mode=='simulation':self.zoom=20
        self.mars=Entity(parent=self.root,model='sphere',texture='mars.jpg',scale=5,shader=lit_with_shadows_shader,rotation=(15,35,0))
        self.earth=Entity(parent=self.root,model='sphere',texture='earth.png',scale=4,position=(-7,0,4),shader=lit_with_shadows_shader,enabled=False)
        self.ship=Spacecraft(design,parent=self.root,scale=.45,position=(4,0,0),rotation=(10,-25,10))
        self.orbit=ring(4,self.root,color.rgba32(65,143,186,150));self.orbit.rotation_z=65
        self.rocket=Entity(parent=self.root,enabled=False)
        Entity(parent=self.rocket,model=Cylinder(32,start=-.5),scale=(.55,2.2,.55),color=color.rgb32(221,228,236),shader=lit_with_shadows_shader)
        Entity(parent=self.rocket,model=Cone(32),y=1.45,scale=(.55,.7,.55),color=color.white,shader=lit_with_shadows_shader)
        Entity(parent=self.rocket,model='cube',y=-.7,scale=(1,.5,.15),color=color.rgb32(36,92,148))
        self.exhaust=Entity(parent=self.rocket,model='sphere',y=-1.6,scale=(.4,1.5,.4),color=color.rgb32(255,155,65))
        if mode=='designer':
            self.mars.enabled=False;self.orbit.enabled=False;self.ship.position=(0,0,0);self.ship.scale=.8
        elif mode in ('planning','briefing'):
            self.mars.position=(4,0,3);self.mars.scale=.8;self.earth.enabled=True;self.earth.position=(-3,0,0);self.earth.scale=.65
            Entity(parent=self.root,model='sphere',scale=.65,position=(0,0,0),color=color.rgb32(255,203,91))
            self.orbit.enabled=False;ring(3,self.root,color.rgb32(35,80,120));ring(4.57,self.root,color.rgb32(96,66,56))
            line([(-.78-3.78*math.cos(i*math.pi/80),.05,3.69*math.sin(i*math.pi/80)) for i in range(81)],CYAN,self.root)
            self.ship.scale=.15;self.ship.position=(0,0,3.5)
        elif mode=='menu':
            self.mars.position=(3,0,3);self.mars.scale=6;self.orbit.position=self.mars.position;self.orbit.scale=1.1
            self.ship.position=(3,-1,-1)
        elif mode=='simulation':
            self.orbit.rotation=(0,0,0)
            self.cruise_path=line([(-8+i*.2, -.9+math.sin(i/80*math.pi)*.8,3) for i in range(81)],color.rgb32(40,100,150),self.root)
            self.cruise_path.enabled=False
            self.scan=line([(0,0,0),(0,0,1)],color.rgb32(56,189,248),self.root,2)
            self.downlink=line([(0,0,0),(1,0,0)],color.rgb32(80,225,160),self.root,2)
            self.scan.enabled=False;self.downlink.enabled=False
            orbit=plans(config)[2]
            self.visual_r=4+(orbit['peri']-300)/1000
            self.visual_a=self.visual_r+(orbit['apo']-orbit['peri'])/5000
            self.visual_e=(self.visual_a-self.visual_r)/self.visual_a
            self.visual_b=self.visual_a*math.sqrt(1-self.visual_e**2)
            self.orbit.model.vertices=[self.orbit_point(i*math.tau/180) for i in range(181)]
            self.orbit.model.generate()
            for t in TARGETS:
                lat=math.radians(t['lat']);lon=math.radians(t['lon'])
                marker=Entity(parent=self.mars,model='sphere',position=(.505*math.cos(lat)*math.sin(lon),.505*math.sin(lat),-.505*math.cos(lat)*math.cos(lon)),scale=.018,color=CYAN)
                self.markers.append(marker)
        camera.fov=48
    def tick(self,dt,mission=None,reduced=False):
        if not reduced:self.angle+=dt*.12;self.mars.rotation_y+=dt*2
        if self.mode=='menu' and not reduced:
            self.ship.position=(3+math.sin(self.angle)*1.6,-1+math.sin(self.angle*.7)*.5,-1)
        if self.mode=='designer':
            self.ship.rotation_y+=0 if reduced else dt*4
        if self.mode=='simulation' and mission:
            phase=mission.phase
            self.cruise_path.enabled=phase=='Cruise'
            self.mars.enabled=phase in ('Mars arrival','Mapping','Results');self.earth.enabled=phase in ('Launch','Earth departure')
            self.orbit.enabled=phase in ('Mapping','Results');self.rocket.enabled=phase=='Launch'
            self.ship.enabled=phase!='Launch'
            if phase=='Launch':
                self.earth.position=(0,-6,3);self.earth.scale=10
                self.rocket.position=(0,-1+max(0,mission.phase_time-3)*.65,0)
                self.exhaust.enabled=mission.phase_time>3;self.exhaust.scale_y=1.4+.2*math.sin(self.angle*80)
            elif phase=='Earth departure':
                self.earth.position=(-4,-1,4);self.earth.scale=6
                self.ship.position=(1+mission.phase_time*.08,0,0);self.ship.scale=.55;self.ship.deploy(min(1,mission.phase_time/5))
            elif phase=='Cruise':
                self.ship.position=(-2+mission.phase_time/18*4,0,0);self.ship.scale=.7;self.ship.rotation_y+=0 if reduced else dt*5
            elif phase=='Mars arrival':
                self.mars.position=(1,0,4);self.mars.scale=2+mission.phase_time*.32
                self.ship.position=(-2,0,0);self.ship.flame.enabled=True
            else:
                self.mars.position=(0,0,0);self.mars.scale=5;self.ship.flame.enabled=False;self.ship.scale=.24
                mean=mission.ops_seconds/mission.s['period']*math.tau
                a=mean
                for _ in range(5):a-=(a-self.visual_e*math.sin(a)-mean)/(1-self.visual_e*math.cos(a))
                self.ship.position=self.orbit_point(a);self.ship.look_at(self.mars)
                self.scan.enabled=mission.imaging and mission.opportunity and not mission.dusty
                self.downlink.enabled=mission.transmitting and mission.link and mission.stored>0
                for beam,end in ((self.scan, self.markers[mission.selected].world_position),(self.downlink,Vec3(-8,2,-2))):
                    if beam.enabled:
                        beam.model.vertices=[self.ship.position,end];beam.model.generate()
                for i,m in enumerate(self.markers):m.color=color.rgb32(80,225,160) if mission.coverage[i]>=80 else CYAN
                if mission.imaging:self.ship.imager.rotation_y=math.sin(self.angle*20)*12
        if self.mode in ('briefing','planning'):
            pos=Vec3(0,9,-10);target=Vec3(0,0,1)
        elif self.mode=='simulation' and self.view==2 and mission and mission.phase=='Mapping':
            target=self.ship.world_position;pos=target+Vec3(2,1.5,-3.2)
        else:
            target=Vec3(0,0,0);yaw=math.radians(self.camera_yaw);pitch=math.radians(self.camera_pitch)
            distance=self.zoom*(1.45 if self.view==3 and self.mode=='simulation' else 1)
            pos=target+Vec3(math.sin(yaw)*math.cos(pitch),math.sin(pitch),-math.cos(yaw)*math.cos(pitch))*distance
        camera.position=lerp(camera.position,pos,min(1,dt*6)) if not reduced else pos
        camera.look_at(target)
    def orbit_point(self,a):
        return Vec3(self.visual_b*math.sin(a)*.5,self.visual_b*math.sin(a)*.866,self.visual_a*(math.cos(a)-self.visual_e))
    def input(self,key):
        if key=='scroll up':self.zoom=max(8,self.zoom-1)
        if key=='scroll down':self.zoom=min(22,self.zoom+1)
        if key=='r':self.zoom=13;self.camera_yaw=0;self.camera_pitch=12;self.view=1
        if key in ('1','2','3'):self.view=int(key)
    def drag(self):
        if held_keys['right mouse']:
            self.camera_yaw+=mouse.velocity[0]*200;self.camera_pitch=max(-70,min(70,self.camera_pitch-mouse.velocity[1]*200))
