"""Original modular orbiter geometry. Scale is illustrative, not engineering CAD."""
from ursina import Entity,Mesh,color,Cone
from ursina.shaders import lit_with_shadows_shader
from math import sin,cos,pi
from systems.engineering import parts,ROOT

def dish_mesh():
    verts=[];tri=[]
    for j in range(7):
        r=max(.002,j/6)
        for i in range(40):
            a=i/40*2*pi;verts.append((r*cos(a),.35*r*r,r*sin(a)))
    for j in range(6):
        for i in range(40):
            a=j*40+i;b=j*40+(i+1)%40;c=a+40;d=b+40
            tri.extend(((a,c,b),(b,c,d)))
    m=Mesh(vertices=verts,triangles=tri,mode='triangle');m.generate_normals();return m
class Spacecraft(Entity):
    def __init__(self,design,**kwargs):
        super().__init__(**kwargs);p=parts(design);self.wings=[]
        def box(pos,scale,c,texture=None):
            return Entity(parent=self,model='cube',position=pos,scale=scale,color=c,texture=texture,shader=lit_with_shadows_shader)
        gold=color.rgb32(224,179,85);silver=color.rgb32(177,191,207)
        box((0,0,0),(1.1,1.25,.9),gold,'foil.png')
        box((0,.66,0),(1.2,.06,1),silver)
        box((0,-.66,0),(1.2,.08,1),silver)
        span=p['solar']['span']
        for sign in (-1,1):
            pivot=Entity(parent=self,x=sign*.6);self.wings.append(pivot)
            Entity(parent=pivot,model='cube',x=sign*span/2,scale=(span,.055,.85),texture='solar.png',shader=lit_with_shadows_shader)
            Entity(parent=pivot,model='cube',x=sign*span/2,y=-.045,scale=(span+.1,.04,.05),color=silver)
            for n in range(1,4):Entity(parent=pivot,model='cube',x=sign*span*n/4,scale=(.025,.065,.9),color=silver)
        Entity(parent=self,model='sphere',position=(0,0,.5),scale=(.65+p['fuel']['fuel']/2000,1,.7),color=silver,shader=lit_with_shadows_shader)
        Entity(parent=self,model='cube',position=(.58,.15,0),scale=(.04,.7,.6),color=color.rgb32(45,57,70),shader=lit_with_shadows_shader)
        Entity(parent=self,model='cube',position=(-.58,.15,0),scale=(.04,.6,.5),color=color.rgb32(126,141,157),shader=lit_with_shadows_shader)
        self.dish=Entity(parent=self,model=dish_mesh(),position=(0,.9,0),scale=p['comms']['dish']*.65,rotation=(15,0,20),color=silver,double_sided=True,shader=lit_with_shadows_shader)
        Entity(parent=self.dish,model='cube',y=.3,scale=(.04,.6,.04),color=gold)
        self.imager=Entity(parent=self,position=(.25,-.4,-.6),scale=.8+p['camera']['mass']/150)
        Entity(parent=self.imager,model='cube',scale=(.42,.42,.5),color=silver,shader=lit_with_shadows_shader)
        Entity(parent=self.imager,model='sphere',z=-.28,scale=(.29,.29,.06),color=color.rgb32(40,171,220))
        Entity(parent=self,model=Cone(32),y=-.91,rotation_z=180,scale=(.45,.5,.45),color=color.rgb32(52,67,84),shader=lit_with_shadows_shader)
        self.flame=Entity(parent=self,model='sphere',y=-1.3,scale=(.22,.9,.22),color=color.rgba32(73,184,255,200),enabled=False)
        # Visible wheel housings, avionics and battery modules.
        for x in (-.35,.35):box((x,-.34,-.49),(.24,.34,.13),color.rgb32(64,79,96))
        box((0,.36,-.49),(.75,.24,.13),color.rgb32(84,107,124))
    def deploy(self,f):
        for i,w in enumerate(self.wings):w.rotation_z=(1-f)*(85 if i==0 else -85)
