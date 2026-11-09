"""Generate the soft pastel backgrounds of the "Що вміє" cards (our own artwork).

    python3 tools/make-feature-backgrounds.py

Writes assets/features/soft-1.jpg … soft-4.jpg (1600×1000): rose, powder-pink and
beige light, painted as blurred motion, one look per feature:
    1 swirl        colour spinning around a point
    2 sweep        diagonal streaks, like a camera moved while shooting
    3 petals       large soft folds with light and shadow
    4 flow         vertical streaks with a gentle wave
Needs Pillow and numpy. The same seed gives the same pictures.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'features'
W, H = 800, 500          # painted at half size, scaled up at the end (it's all blur anyway)

def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)

CREAM, POWDER, BLUSH, ROSE, DEEP = map(hexc, ['#fbf3ee', '#fbe2e4', '#f6c5d1', '#ee9fb8', '#e08aa8'])
PEACH, BEIGE, SAND, WHITE = map(hexc, ['#f8cdb6', '#f1dfcb', '#e9cfb4', '#ffffff'])

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def blobs(img, rng, n, colours, rmin, rmax, alpha=(0.35, 0.8), stretch=(1, 1)):
    """Soft round splashes of colour (Gaussian), optionally stretched and turned."""
    for _ in range(n):
        cx, cy = rng.uniform(-0.1, 1.1) * W, rng.uniform(-0.1, 1.1) * H
        r = rng.uniform(rmin, rmax)
        a = rng.uniform(0, np.pi)
        sx, sy = rng.uniform(*stretch), 1.0
        dx, dy = xx - cx, yy - cy
        u = (dx * np.cos(a) + dy * np.sin(a)) / sx
        v = (-dx * np.sin(a) + dy * np.cos(a)) / sy
        m = np.exp(-(u * u + v * v) / (2 * r * r))[..., None] * rng.uniform(*alpha)
        c = colours[rng.integers(len(colours))]
        img[:] = img * (1 - m) + c * m
    return img

def to_pil(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def average(frames):
    acc, n = np.zeros((H, W, 3), np.float32), 0
    for f in frames:
        acc += np.asarray(f, np.float32); n += 1
    return acc / n

def spin_blur(im, centre, degrees, steps=36):
    return average(im.rotate(d, resample=Image.BICUBIC, center=centre, fillcolor=tuple(int(x) for x in POWDER))
                   for d in np.linspace(-degrees / 2, degrees / 2, steps))

def streak_blur(im, angle, length, steps=40):
    a = np.radians(angle)
    return average(ImageChops.offset(im, int(round(np.cos(a) * t)), int(round(np.sin(a) * t)))
                   for t in np.linspace(-length / 2, length / 2, steps))

def finish(a, name, rng, blur=3, grain=3.4):
    im = to_pil(a).filter(ImageFilter.GaussianBlur(blur)).resize((W * 2, H * 2), Image.LANCZOS)
    b = np.asarray(im, np.float32)
    b = b * 0.96 + CREAM * 0.04          # a whisper of cream keeps it soft
    b += rng.normal(0, grain, b.shape[:2])[..., None]   # fine film grain
    to_pil(b).save(OUT / name, quality=86, optimize=True, progressive=True)
    print(name)

def swirl(seed=11):
    rng = np.random.default_rng(seed)
    a = np.empty((H, W, 3), np.float32); a[:] = BLUSH
    blobs(a, rng, 22, [POWDER, ROSE, PEACH, BEIGE, CREAM, DEEP], 40, 110, alpha=(0.5, 0.9), stretch=(1, 2.2))
    blobs(a, rng, 120, [WHITE, CREAM, ROSE, DEEP, PEACH, SAND], 5, 16, alpha=(0.55, 0.95), stretch=(1.5, 4))
    im = to_pil(a).filter(ImageFilter.GaussianBlur(1))
    return spin_blur(im, (W * 0.6, H * 0.62), 42, 48)

def sweep(seed=23):
    rng = np.random.default_rng(seed)
    a = np.empty((H, W, 3), np.float32); a[:] = POWDER
    blobs(a, rng, 16, [PEACH, BLUSH, BEIGE, CREAM, SAND], 60, 160, alpha=(0.55, 0.9))
    blobs(a, rng, 70, [ROSE, DEEP, BLUSH, PEACH, SAND], 6, 22, alpha=(0.5, 0.9), stretch=(3, 7))
    blobs(a, rng, 30, [WHITE, CREAM], 10, 40, alpha=(0.6, 0.95), stretch=(2, 5))
    return streak_blur(to_pil(a), -24, 240, 56)

def petals(seed=5):
    rng = np.random.default_rng(seed)
    a = np.empty((H, W, 3), np.float32); a[:] = POWDER
    # Large folds: long tilted ellipses with a bright edge and a soft shadow beside it.
    for _ in range(13):
        c = [BLUSH, ROSE, PEACH, BEIGE, CREAM, SAND][rng.integers(6)]
        cx, cy = rng.uniform(0, 1) * W, rng.uniform(0, 1) * H
        r, ang = rng.uniform(60, 150), rng.uniform(0, np.pi)
        for k, (col, off, al) in enumerate([(DEEP, 0.3, 0.5), (c, 0.0, 0.92), (WHITE, -0.24, 0.65)]):
            dx, dy = xx - cx - np.cos(ang + 1.57) * r * off, yy - cy - np.sin(ang + 1.57) * r * off
            u = (dx * np.cos(ang) + dy * np.sin(ang)) / 2.8
            v = (-dx * np.sin(ang) + dy * np.cos(ang)) / (0.8 if k != 1 else 1.0)
            m = np.exp(-(u * u + v * v) / (2 * r * r * 0.3))[..., None] * al
            a[:] = a * (1 - m) + col * m
    im = to_pil(a).filter(ImageFilter.GaussianBlur(4))
    return streak_blur(im, 14, 50, 20)

def flow(seed=41):
    rng = np.random.default_rng(seed)
    a = np.empty((H, W, 3), np.float32); a[:] = CREAM
    blobs(a, rng, 14, [BLUSH, POWDER, PEACH, BEIGE], 50, 120, alpha=(0.5, 0.85))
    blobs(a, rng, 90, [ROSE, DEEP, BLUSH, PEACH, SAND, WHITE], 6, 20, alpha=(0.5, 0.9), stretch=(0.12, 0.3))
    im = Image.fromarray(np.clip(streak_blur(to_pil(a), 90, 280, 56), 0, 255).astype(np.uint8))
    # A gentle sideways wave, so the streaks bend like fabric.
    b = np.asarray(im, np.float32)
    shift = (np.sin(np.linspace(0, 3 * np.pi, H)) * 22).astype(int)
    return np.stack([np.roll(b[y], shift[y], axis=0) for y in range(H)])

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (fn, blur) in enumerate([(swirl, 2.5), (sweep, 3), (petals, 4), (flow, 2.5)], 1):
        finish(fn(), f'soft-{i}.jpg', np.random.default_rng(100 + i), blur=blur)
