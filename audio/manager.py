from pathlib import Path
from ursina import Audio
ROOT=Path(__file__).resolve().parents[1]/'assets/sounds'
class AudioManager:
    def __init__(self,settings):
        self.settings=settings;self.sounds={};self.music=None
        try:
            self.music=Audio(ROOT/'ambient.wav',loop=True,autoplay=True)
            for p in ROOT.glob('*.wav'):
                if p.stem!='ambient':self.sounds[p.stem]=Audio(p,autoplay=False)
        except Exception as e:print('Audio unavailable:',e)
        self.apply()
    def apply(self):
        s=self.settings;master=0 if s['mute'] else s['master']
        if self.music:self.music.volume=master*s['music']
        for sound in self.sounds.values():sound.volume=master*s['sfx']
    def play(self,name):
        try:
            if name in self.sounds:self.sounds[name].play()
        except Exception:pass
