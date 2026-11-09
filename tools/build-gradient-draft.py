"""Build index-gradients.html: a duplicate of the landing with the soft pastel gradients
of the feature cards used in more places.

    python3 tools/build-gradient-draft.py

Reads index.html (so run it again after the homepage changes) and
  - replaces the pale circles behind the phone in the hero with a dome of soft colour
  - turns "До і після" into one big gradient panel with a frosted table,
  - gives the "Залишилися питання?" card in the FAQ a gradient.
Styles: assets/gradient-draft.css. The page is noindex and not linked anywhere.
"""
import re
import sys
import time

sys.exit('Retired: the homepage itself now has these gradients, so index-gradients.html is no longer rebuilt.')
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / 'index.html').read_text(encoding='utf-8')
out = src

# Head: a draft, kept out of search; our stylesheet after the site's.
out, n = re.subn(r'<!-- seo:start -->.*?<!-- seo:end -->',
                 '<title>Roddi Health — градієнти (чернетка)</title>\n  <meta name="robots" content="noindex, nofollow">',
                 out, count=1, flags=re.S)
assert n == 1
out, n = re.subn(r'(<link rel="stylesheet" href="assets/app-home\.css[^"]*">)',
                 r'\1\n  <link rel="stylesheet" href="assets/gradient-draft.css?v=' + str(int(time.time())) + '">', out, count=1)
assert n == 1

# Hero: both stages (desktop collage and the narrower one) hold the same pair of pale circles.
dome = ('<div data-reveal="zoom" data-d="420" class="hg-dome -translate-x-1/2 absolute left-1/2 size-[1292px] top-[534px]">'
        '<img alt="" src="assets/features/pastel-hero.jpg"></div>')
out, n = re.subn(r'<div class="-translate-x-1/2 absolute contents left-1/2 top-\[534px\]">.*?src="assets/ellipse11\.svg" />\s*</div>\s*</div>',
                 lambda m: dome, out, flags=re.S)
assert n == 2, n

# "До і після": the section becomes a gradient panel.
a = '<!-- ============ До і після ============ -->\n<section class="px-5 pb-[96px] md:pb-[130px]">'
assert a in out
out = out.replace(a, a.replace('<section class="px-5 pb-[96px] md:pb-[130px]">', '<section class="hg-ba px-5 pb-[96px] md:pb-[130px]">'))

# FAQ: the question card.
q = 'class="mt-[28px] rounded-[28px] bg-[#f4f5f7] p-[24px]"'
assert q in out
out = out.replace(q, 'class="hg-ask mt-[28px] rounded-[28px] p-[24px]"')

# Feature cards: the pastel pictures in the logo colour instead of the homepage's pink ones.
out = re.sub(r'assets/features/soft-(\d)\.jpg', r'assets/features/pastel-\1.jpg', out)

(ROOT / 'index-gradients.html').write_text(out, encoding='utf-8')
print('index-gradients.html written')
