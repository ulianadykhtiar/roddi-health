#!/usr/bin/env python3
# Usage: python3 tools/make-hero-mascot.py assets/mascot   (needs Pillow and numpy)
"""Draws the hero mascot in two layers, in phone coordinates (phone frame = 387x812 at 0,0).
back: body, ears, tail, face (goes behind the phone); front: paw on the top edge + arm over the right edge."""
import sys, numpy as np
from PIL import Image, ImageFilter
OUT = sys.argv[1]
X0, Y0, W, H, K = 140, -180, 580, 660, 2          # canvas in phone px, K = supersampling
yy, xx = np.mgrid[0:H*K, 0:W*K].astype(np.float32)
px = xx / K + X0; py = yy / K + Y0
def ell(cx, cy, rx, ry, rot=0):
    c, s = np.cos(np.radians(rot)), np.sin(np.radians(rot))
    u = ((px-cx)*c + (py-cy)*s) / rx; v = (-(px-cx)*s + (py-cy)*c) / ry
    return (np.sqrt(u*u+v*v) - 1) * min(rx, ry)
def seg(ax, ay, bx, by, r):
    vx, vy = bx-ax, by-ay; t = np.clip(((px-ax)*vx + (py-ay)*vy) / (vx*vx+vy*vy), 0, 1)
    return np.hypot(px-ax-t*vx, py-ay-t*vy) - r
def bez(p0, p1, p2, r0, r1, n=60):
    d = np.full(px.shape, 1e9, np.float32)
    for i in range(n+1):
        t = i/n; x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]; y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        d = np.minimum(d, np.hypot(px-x, py-y) - (r0 + (r1-r0)*t))
    return d
def smin(a, b, k):
    h = np.clip(0.5 + 0.5*(b-a)/k, 0, 1); return b*(1-h) + a*h - k*h*(1-h)
def shade(d, hl, dark_from):
    inner = np.clip(-d/70, 0, 1) ** 0.6
    rim, mid = np.array([120, 172, 250.]), np.array([44, 112, 240.])
    col = rim[None, None] * (1-inner[..., None]) + mid[None, None] * inner[..., None]
    hx, hy, hr = hl
    g = np.exp(-((px-hx)**2 + (py-hy)**2) / (2*hr*hr))[..., None] * np.clip(inner, .3, 1)[..., None]
    col = col*(1-g*.85) + np.array([96, 196, 253.])*g*.85
    dk = np.clip((py - dark_from) / 220, 0, 1)[..., None] * .22
    col = col*(1-dk) + np.array([30, 80, 220.])*dk
    soft = 5.0
    a = np.clip(0.5 - d/soft, 0, 1)
    a = np.maximum(a, np.exp(-np.maximum(d, 0)/14) * .18 * (d > 0))   # faint haze around the edge
    return np.dstack([col, a*255])
def img(arr):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    return im.filter(ImageFilter.GaussianBlur(1.2*K)).resize((W, H), Image.LANCZOS)

# ---- back layer
body = smin(ell(480, 62, 124, 114, 18), ell(500, 262, 142, 236), 70)
body = smin(body, ell(408, -82, 70, 68), 26)
body = smin(body, ell(548, -10, 66, 64), 26)
tail = bez((590, 300), (690, 250), (634, 136), 20, 14)
back = shade(np.minimum(body, tail), (455, 95, 95), 120)
# glow under the body: fade the bottom out
fade = np.clip((470 - py) / 190, 0, 1) ** 1.4
back[..., 3] *= fade
bk = img(back)
# face (sharp, dark), drawn after the blur
from PIL import ImageDraw
face = Image.new('RGBA', (W*K, H*K), (0, 0, 0, 0)); d = ImageDraw.Draw(face)
def P(x, y): return ((x-X0)*K, (y-Y0)*K)
ink = (14, 20, 34, 255)
for cx, cy in ((404, 18), (512, 66)):
    a, b = P(cx-11, cy-15), P(cx+11, cy+15); d.ellipse([a, b], fill=ink)
# smile: arc, tilted with the head
sm = Image.new('RGBA', (120*K, 80*K), (0, 0, 0, 0)); ds = ImageDraw.Draw(sm)
ds.arc([20*K, -10*K, 80*K, 40*K], 20, 160, fill=ink, width=7*K)
for ang in (20, 160):
    ex = 50*K + 30*K*np.cos(np.radians(ang)) - 0; ey = 15*K + 25*K*np.sin(np.radians(ang))
    ex = 50*K + (30*K-3.5*K)*np.cos(np.radians(ang)); ey = 15*K + (25*K-3.5*K)*np.sin(np.radians(ang))
    ds.ellipse([ex-3.5*K, ey-3.5*K, ex+3.5*K, ey+3.5*K], fill=ink)
sm = sm.rotate(-24, resample=Image.BICUBIC, center=(50*K, 15*K))
face.alpha_composite(sm, (int((452-X0-50)*K), int((48-Y0-15)*K)))
face = face.resize((W, H), Image.LANCZOS)
bk.alpha_composite(face); bk.save(OUT + '/mascot-hero-back.png', optimize=True)

# ---- front layer: paw on the top edge, arm over the right edge
paw = ell(224, -10, 50, 34, -4)
arm = smin(seg(520, 206, 374, 228, 44), ell(372, 230, 50, 45), 20)
fr = shade(np.minimum(paw, arm), (230, -30, 40), 260)
# second highlight for the arm
fr2 = shade(arm, (420, 205, 60), 260)
use_arm = (arm < paw)[..., None]
fr = np.where(use_arm, fr2, fr)
# arm fades where it meets the body (the body is behind, so blend it out at the right end)
fr[..., 3] *= np.where(use_arm[..., 0], np.clip((585 - px) / 80, 0, 1), 1)
img(fr).save(OUT + '/mascot-hero-front.png', optimize=True)
print('ok')
