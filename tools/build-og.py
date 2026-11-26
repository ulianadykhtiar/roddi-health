#!/usr/bin/env python3
"""Draw the social preview pictures (Open Graph, 1200x630) in the style of the home page hero.

Left: the blue logo and the hero headline (Onest, with the little pet photos chip, as on the page).
Right: the hero phone with the blue mascot hugging it, taken from the live markup of index.html,
on the same pale blue dome. The page's own CSS and fonts are used, rendered with headless Chrome.

    python3 tools/build-og.py          # writes assets/og-uk-v4.jpg and assets/og-en-v4.jpg

Needs Google Chrome (macOS path below) and Pillow (to save JPEG). Not run in CI.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OUT = {'uk': 'assets/og-uk-v4.jpg', 'en': 'assets/og-en-v4.jpg'}
SRC = {'uk': 'index.html', 'en': 'en/index.html'}
URL = 'roddihealth.app'

PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<link rel="stylesheet" href="assets/fonts/fonts.css">
<link rel="stylesheet" href="assets/tailwind.css">
<link rel="stylesheet" href="assets/styles.css">
<link rel="stylesheet" href="assets/theme.css">
<link rel="stylesheet" href="assets/app-home.css">
<style>
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; }}
  body {{ position: relative; font-family: 'Onest', sans-serif;
         background: linear-gradient(180deg, #ffffff 0%, #f6f8fd 45%, #e6eefb 100%); }}
  .dome {{ position: absolute; left: 610px; top: 250px; width: 760px; height: 760px; border-radius: 50%; overflow: hidden; opacity: .95; }}
  .dome img {{ width: 100%; height: 100%; object-fit: cover; }}
  .logo {{ position: absolute; left: 72px; top: 64px; width: 64px; height: 64px; }}
  h1.t-display {{ position: absolute; left: 72px; top: 178px; width: {w}px; margin: 0; text-align: left;
                  font-size: {size}px; line-height: 1.06; color: #0f0f11; text-wrap: initial; }}
  .url {{ position: absolute; left: 74px; bottom: 62px; font-size: 26px; font-weight: 500; color: #5a6788; letter-spacing: -0.01em; }}
  .scene {{ position: absolute; left: 0; top: 0; width: 1200px; height: 630px; overflow: hidden;
            -webkit-mask-image: linear-gradient(180deg, #000 82%, transparent 100%); mask-image: linear-gradient(180deg, #000 82%, transparent 100%); }}
  .scene .ip {{ left: 0; top: 0; transform-origin: 0 0; transform: translate({px}px, {py}px) scale({sc}); }}
</style></head><body>
<div class="dome"><img alt="" src="assets/features/pastel-hero.webp"></div>
<div class="scene">{phone}</div>
<img class="logo" alt="" src="assets/logo-mauve.svg">
<h1 class="t-display">{h1}</h1>
<div class="url">{url}</div>
</body></html>"""


def grab(lang):
    s = open(os.path.join(ROOT, SRC[lang]), encoding='utf-8').read()
    if lang == 'en':
        s = s.replace('../assets/', 'assets/')
    h1 = re.search(r'<h1[^>]*class="t-display[^"]*"[^>]*>(.*?)</h1>', s, re.S).group(1)
    # the desktop hero stage's phone (with the mascot layers inside it)
    stage = s[s.index('class="stage mx-auto mt-[6px] hidden lg:block"'):]
    i = stage.index('<div data-reveal="rise" data-d="560" class="ip"')
    depth, j = 0, i
    for m in re.finditer(r'<(/?)div\b', stage[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            j = i + m.end()
            j = stage.index('>', j) + 1
            break
    phone = stage[i:j]
    phone = re.sub(r'\sdata-reveal="[^"]*"|\sdata-d="[^"]*"', '', phone)
    phone = re.sub(r'style="left:\d+px;top:\d+px"', '', phone, count=1)
    return h1, phone


def main():
    from PIL import Image
    for lang in ('uk', 'en'):
        h1, phone = grab(lang)
        html = PAGE.format(lang=lang, h1=h1, phone=phone, url=URL, w=640 if lang == 'uk' else 670,
                           size=64 if lang == 'uk' else 54, px=752, py=196, sc=0.62)
        tmp = os.path.join(ROOT, f'_og-{lang}.html')
        png = os.path.join(tempfile.gettempdir(), f'og-{lang}.png')
        try:
            open(tmp, 'w', encoding='utf-8').write(html)
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            '--window-size=1200,630', '--virtual-time-budget=4000', f'--screenshot={png}', 'file://' + tmp],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        Image.open(png).convert('RGB').crop((0, 0, 1200, 630)).save(os.path.join(ROOT, OUT[lang]), quality=90, optimize=True, progressive=True)
        print('wrote', OUT[lang])


if __name__ == '__main__':
    sys.exit(main())
