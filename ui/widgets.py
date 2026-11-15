from ursina import *
NAVY=color.rgb32(7,17,31);PANEL=color.rgba32(8,20,35,242);CYAN=color.rgb32(56,189,248);WHITE=color.rgb32(248,250,252);MUTED=color.rgb32(148,163,184);ORANGE=color.rgb32(228,107,53)
def label(parent,text,x,y,scale=1,c=WHITE):
    return Text(parent=parent,text=text,position=(x,y,-.03),scale=scale,color=c,origin=(-.5,.5))
def panel(parent,x,y,w,h):
    Entity(parent=parent,model='quad',position=(x,y,.01),scale=(w,h),color=PANEL)
    Entity(parent=parent,model='quad',position=(x-w/2,y,0),scale=(.002,h),color=color.rgb32(30,72,95))
def button(parent,text,x,y,callback,w=.3,accent=False,audio=None):
    b=Button(parent=parent,text=text,position=(x,y,-.02),scale=(w,.048),color=color.rgb32(20,66,89) if accent else color.rgb32(16,35,53),highlight_color=color.rgb32(31,94,120),pressed_color=CYAN,text_color=WHITE,pressed_scale=.97)
    b.text_size=.8
    b.highlight_text_size=.8
    def click():
        if audio:audio.play('click')
        callback()
    b.on_click=click
    if audio:
        original_hover=b.on_mouse_enter
        def hover():
            original_hover();audio.play('hover')
        b.on_mouse_enter=hover
    return b
class Bar:
    def __init__(self,parent,x,y,w=.3):
        Entity(parent=parent,model='quad',position=(x+w/2,y,-.01),scale=(w,.007),color=color.rgb32(32,49,65))
        self.fill=Entity(parent=parent,model='quad',position=(x,y,-.02),origin=(-.5,0),scale=(w,.007),color=CYAN);self.width=w
    def set(self,value):self.fill.scale_x=self.width*max(.001,min(1,value));self.fill.color=ORANGE if value<.15 else CYAN
