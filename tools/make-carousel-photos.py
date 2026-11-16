#!/usr/bin/env python3
"""Makes the 4:5 crops for the home page carousel (assets/carousel/*.jpg) from the free-licence photos already saved in assets/blog/.

Run by hand when a photo changes (needs Pillow); the results are committed. CI does not run it.
Each entry: output name, source file in assets/blog (960 px wide version), horizontal focus (0..1: where the animal is), vertical focus.
Credits for these photos live in tools/build-credits.py.
"""
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = [
    ('degu',       'octodon-degus-209581281-960.jpg',       0.30, 0.5),
    ('guinea-pig', 'cavia-porcellus01-960.jpg',             0.65, 0.5),
    ('hamster',    'syrian-hamster-on-blanket-960.jpg',     0.5,  0.45),
    ('chinchilla', 'napoleon-chinchilla-in-box-960.jpg',    0.5,  0.5),
    ('rat',        'fancy-rat-husky-960.jpg',               0.55, 0.5),
    ('rabbit',     'heimtier-004-2023-08-26-960.jpg',       0.40, 0.5),
    ('mouse',      'pet-mouse-mini-960.jpg',                0.30, 0.5),
]
RATIO = 4 / 5
for name, src, fx, fy in PHOTOS:
    im = Image.open(ROOT / 'assets' / 'blog' / src).convert('RGB')
    w, h = im.size
    cw, ch = (int(h * RATIO), h) if w / h > RATIO else (w, int(w / RATIO))
    left = min(max(int(fx * w - cw / 2), 0), w - cw)
    top = min(max(int(fy * h - ch / 2), 0), h - ch)
    im = im.crop((left, top, left + cw, top + ch)).resize((520, 650), Image.LANCZOS)
    im.save(ROOT / 'assets' / 'carousel' / (name + '.jpg'), quality=82, optimize=True, progressive=True)
    print(name, (cw, ch), 'from', (w, h))
