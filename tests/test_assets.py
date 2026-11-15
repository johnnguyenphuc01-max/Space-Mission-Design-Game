from pathlib import Path
import wave
from PIL import Image
from systems.engineering import ROOT,COMPONENTS,TARGETS

def test_shipped_textures_decode():
    for file in (ROOT/'assets/textures').iterdir():
        with Image.open(file) as image:
            image.verify()

def test_audio_is_nonempty_pcm():
    for file in (ROOT/'assets/sounds').glob('*.wav'):
        with wave.open(str(file)) as audio:
            assert audio.getnchannels()==1 and audio.getsampwidth()==2
            assert audio.getnframes()>2000
            assert any(audio.readframes(22050))

def test_catalog_integrity():
    assert len(COMPONENTS)==9 and len(TARGETS)==5
    for key,options in COMPONENTS.items():
        assert len(options)==3
        assert len({p['id'] for p in options})==3
        assert all(p['mass']>=0 and p['cost']>=0 and p['power']>=0 for p in options)
