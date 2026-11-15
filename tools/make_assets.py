"""Generate original solar foil textures and PCM music/SFX, no downloaded audio."""
from pathlib import Path
import random,math,wave,struct
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]/'assets';random.seed(17)
im=Image.new('RGB',(512,256),(11,34,78));d=ImageDraw.Draw(im)
for x in range(0,512,32):
 for y in range(0,256,32):
  d.rectangle((x+2,y+2,x+29,y+29),fill=(20,52+random.randrange(20),110+random.randrange(50)),outline=(84,126,173))
  d.line((x+5,y+8,x+26,y+8),fill=(95,145,195))
im.save(ROOT/'textures/solar.png')
im=Image.new('RGB',(256,256));p=im.load()
for y in range(256):
 for x in range(256):
  v=int(18*math.sin(x*.15+math.sin(y*.21))+random.randrange(20));p[x,y]=(min(255,170+v),min(255,117+v),max(0,38+v//2))
im.save(ROOT/'textures/foil.png')
# Stylized Earth explicitly labelled as procedural artwork, not a geographic dataset.
im=Image.new('RGB',(512,256));p=im.load()
for y in range(256):
 for x in range(512):
  a=x/512*math.tau;b=y/256*math.pi
  n=math.sin(a*3+math.sin(b*5))+math.cos(a*5-b*4)*.5+math.sin(a*8+b*7)*.2
  p[x,y]=(180,207,215) if y<15 or y>241 else ((47,100,89) if n>.5 else (13,49,94))
im.save(ROOT/'textures/earth.png')
SR=22050
def write(name,values):
 with wave.open(str(ROOT/'sounds'/f'{name}.wav'),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR)
  f.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,v))*24000)) for v in values))
def tone(name,freq,dur=.16):
 write(name,(math.sin(2*math.pi*(freq*t+.3*freq*t*t))*math.sin(math.pi*t/dur)**2*.28 for t in (i/SR for i in range(int(SR*dur)))))
for name,f in [('click',620),('hover',440),('warning',190),('image',1200),('data',880),('milestone',520),('success',780),('failure',110),('deploy',340),('countdown',660)]:tone(name,f,.45 if name in ('success','failure','milestone') else .12)
write('launch',((random.random()-.5)*.55*min(1,i/SR)*max(0,1-i/(SR*5)) for i in range(SR*5)))
# All tones use integer cycles within the 24-second loop, with matching envelopes at boundaries.
dur=24
freqs=[110,165,220,261.625,329.625]
write('ambient',(sum(math.sin(2*math.pi*round(f*dur)/dur*t)*(.10+.03*math.sin(2*math.pi*t/dur+j)) for j,f in enumerate(freqs))*.22 for t in (i/SR for i in range(SR*dur))))
print('Original assets generated.')
