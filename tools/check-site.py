#!/usr/bin/env python3
"""Checks the static site for the mistakes that were easy to ship by accident.

Run:  python3 tools/check-site.py      (CI runs it on every pull request; exit code 1 = problems found)

For every public page: title, description, canonical, one h1, alt on images, valid JSON-LD, no [placeholders]
in visible text, no dead "#" links, every local link/src/href points to a file, every #anchor exists.
Also: every sitemap URL maps to a file.
"""
import json, pathlib, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {'index-gradients.html', '404.html'}          # draft and error page: not part of the sitemap
SITE = 'https://roddihealth.app'
problems = []


def bad(page, msg):
    problems.append(f'{page}: {msg}')


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''; self.in_title = False; self.skip = 0
        self.ids = set(); self.refs = []; self.metas = {}; self.canonical = None
        self.h1 = 0; self.imgs_noalt = 0; self.ld = []; self.in_ld = False; self.text = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        if 'id' in a: self.ids.add(a['id'])
        if tag == 'title': self.in_title = True
        if tag == 'h1': self.h1 += 1
        if tag == 'img' and 'alt' not in a: self.imgs_noalt += 1
        if tag == 'meta' and a.get('name'): self.metas[a['name']] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')
        if tag == 'a' and 'href' in a: self.refs.append(('href', '#top-of-page' if a['href'] == '#' and a.get('aria-label') else a['href']))   # a named logo link to "#" scrolls to the top: fine
        if tag in ('img', 'script', 'source', 'video', 'audio') and a.get('src'): self.refs.append(('src', a['src']))
        if tag == 'link' and a.get('href') and a.get('rel') in ('stylesheet', 'icon', 'apple-touch-icon', 'preload'): self.refs.append(('href', a['href']))
        if tag == 'script':
            self.skip += 1
            if a.get('type') == 'application/ld+json': self.in_ld = True
        if tag == 'style': self.skip += 1

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1); self.in_ld = False

    def handle_data(self, d):
        if self.in_title: self.title += d
        elif self.in_ld: self.ld.append(d)
        elif not self.skip: self.text.append(d)


def resolve(page_path, ref):
    """Map a local reference to a file path inside the project, or None if it points elsewhere."""
    u = urlparse(ref)
    if u.scheme in ('http', 'https', 'mailto', 'tel', 'data', 'javascript') or ref.startswith('//'):
        return None
    path = unquote(u.path)
    if not path:
        return page_path
    base = ROOT if path.startswith('/') else page_path.parent
    target = (base / path.lstrip('/')).resolve()
    for cand in (target, target.with_suffix('.html'), target / 'index.html'):
        if cand.is_file(): return cand
    return target


pages = sorted(p for p in list(ROOT.glob('*.html')) + list(ROOT.glob('en/*.html')) + list(ROOT.glob('blog/*.html')) if p.name not in SKIP)
parsed = {}
for p in pages:
    rel = p.relative_to(ROOT).as_posix()
    html = p.read_text(encoding='utf-8')
    pg = Page(); pg.feed(html); parsed[p.resolve()] = pg
    noindex = 'noindex' in pg.metas.get('robots', '')
    if not pg.title.strip(): bad(rel, 'no <title>')
    if len(pg.title) > 75: bad(rel, f'title is {len(pg.title)} characters (over 75)')
    if not noindex:
        d = pg.metas.get('description', '')
        if not 70 <= len(d) <= 170: bad(rel, f'description is {len(d)} characters (want 70-170)')
        if not pg.canonical: bad(rel, 'no canonical link')
    if pg.h1 != 1: bad(rel, f'{pg.h1} <h1> (want exactly 1)')
    if pg.imgs_noalt: bad(rel, f'{pg.imgs_noalt} <img> without alt')
    for blob in ([''.join(pg.ld)] if pg.ld else []):
        try: json.loads(blob)
        except Exception as e: bad(rel, f'JSON-LD does not parse: {e}')
    visible = re.sub(r'\s+', ' ', ' '.join(pg.text))
    for m in re.findall(r'\[[^\]\[]{3,80}\]', visible): bad(rel, f'placeholder in text: {m}')

for p in pages:
    pg = parsed[p.resolve()]; rel = p.relative_to(ROOT).as_posix()
    for kind, ref in pg.refs:
        if ref in ('#', ''): bad(rel, f'dead {kind}="{ref}"'); continue
        if ref == '#top-of-page': continue
        t = resolve(p, ref)
        if t is None: continue
        if not t.is_file(): bad(rel, f'{kind}="{ref}" points to a missing file'); continue
        frag = urlparse(ref).fragment
        if frag and t.suffix == '.html':
            tp = parsed.get(t.resolve())
            if tp is None:
                tp = Page(); tp.feed(t.read_text(encoding='utf-8')); parsed[t.resolve()] = tp
            if frag not in tp.ids: bad(rel, f'anchor #{frag} not found in {t.relative_to(ROOT).as_posix()}')

sm = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
for url in sorted(set(re.findall(r'<loc>([^<]+)</loc>', sm))):
    path = url.replace(SITE, '') or '/'
    t = resolve(ROOT / 'index.html', path)
    if t is None or not t.is_file(): bad('sitemap.xml', f'{url} has no file')

if problems:
    print(f'{len(problems)} problem(s):')
    for m in problems: print(' -', m)
    sys.exit(1)
print(f'ok: {len(pages)} pages checked')
