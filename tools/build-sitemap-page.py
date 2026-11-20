#!/usr/bin/env python3
"""Builds sitemap.html (served at /sitemap): a readable list of every page, built from sitemap.xml.

Run after build-articles.py / build-hubs.py:  python3 tools/build-sitemap-page.py
sitemap.xml itself stays plain XML for search engines (browsers no longer render XSLT, so it can't be made pretty).
"""
import html, pathlib, re
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://roddihealth.app'
sm = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
urls = []
for u in re.findall(r'<loc>([^<]+)</loc>', sm):
    if u not in urls:
        urls.append(u)


def file_of(path):
    path = path.strip('/') or 'index'
    for c in (ROOT / (path + '.html'), ROOT / path / 'index.html'):
        if c.is_file():
            return c
    if path == 'en':
        return ROOT / 'en' / 'index.html'
    raise SystemExit('no file for ' + path)


def title_of(path):
    t = re.search(r'<title>(.*?)</title>', file_of(path).read_text(encoding='utf-8'), re.S).group(1)
    return html.unescape(re.sub(r'\s*[|·]\s*Roddi Health\s*$', '', t)).strip()


COPY = {
    'uk': dict(lang='uk', h='Карта сайту', intro='Усі сторінки Roddi Health в одному місці.', groups=('Основні сторінки', 'Статті за твариною', 'Усі статті'), other='English', other_href='#en', home='На головну'),
    'en': dict(lang='en', h='Site map', intro='Every page of Roddi Health in one place.', groups=('Main pages', 'Articles by animal', 'All articles'), other='Українською', other_href='#uk', home='Home'),
}


def section(lang):
    c = COPY[lang]
    main, hubs, arts = [], [], []
    for u in urls:
        path = urlparse(u).path
        is_en = path == '/en' or path.startswith('/en/')
        if is_en != (lang == 'en'):
            continue
        parts = [x for x in path.strip('/').split('/') if x and x != 'en']
        item = (path or '/', title_of(path))
        if len(parts) == 3 and parts[0] == 'blog':
            arts.append(item)
        elif len(parts) == 2 and parts[0] == 'blog' and parts[1] != 'pro-materialy':
            hubs.append(item)
        else:
            main.append(item)
    def block(title, items):
        if not items:
            return ''
        li = ''.join('<li><a href="%s">%s</a><span>%s</span></li>' % (html.escape(p), html.escape(t), html.escape(p)) for p, t in items)
        return '<h3>%s</h3><ul>%s</ul>' % (title, li)
    return '<section id="%s" lang="%s"><h2>%s</h2>%s%s%s</section>' % (
        lang, lang, 'Українською' if lang == 'uk' else 'English', block(c['groups'][0], main), block(c['groups'][1], hubs), block(c['groups'][2], arts))


page = '''<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Карта сайту · Roddi Health</title>
  <meta name="robots" content="noindex, follow">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg?v=blue1">
  <meta name="theme-color" content="#75a1da">
  <link rel="manifest" href="/manifest.webmanifest">
  <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/onest-cyrillic-400.woff2" crossorigin>
  <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/onest-latin-400.woff2" crossorigin>
  <link rel="stylesheet" href="/assets/fonts/fonts.css?v=1">
  <style>
    *{box-sizing:border-box}
    body{margin:0;padding:32px 20px 72px;font:16px/1.45 Onest,system-ui,sans-serif;color:#0f0f11;background:linear-gradient(180deg,#d8e5f6 0,#e9f0f8 360px,#fff 700px) no-repeat #fff}
    main{max-width:960px;margin:0 auto}
    .top{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:28px}
    .top img{height:34px}
    .top a{font-size:15px;font-weight:500;text-decoration:none;padding:10px 18px;border-radius:999px;background:#fff;box-shadow:inset 0 0 0 1px #d9dce1}
    h1{margin:0 0 6px;font-size:clamp(30px,5vw,44px);letter-spacing:-.03em;line-height:1.1;font-weight:600}
    .lead{margin:0 0 28px;color:#404955}
    .cols{display:grid;gap:18px}
    section{padding:22px 22px 14px;border-radius:28px;background:#fff;box-shadow:0 0 0 1px #e7e9ec}
    h2{margin:0 0 4px;font-size:22px;letter-spacing:-.02em;font-weight:600}
    h3{margin:18px 0 6px;color:#6e727a;font-size:13px;font-weight:600;letter-spacing:.02em;text-transform:uppercase}
    ul{margin:0;padding:0;list-style:none}
    li{display:flex;flex-direction:column;gap:1px;padding:9px 0;border-top:1px solid #eef0f2}
    li:first-child{border-top:0}
    li a{font-weight:500;text-underline-offset:3px}
    li a:hover{color:#3172c8}
    li span{color:#8f8a94;font-size:13px;word-break:break-all}
    a{color:inherit}
    a:focus-visible{outline:2px solid #3172c8;outline-offset:3px;border-radius:6px}
    @media (min-width:860px){.cols{grid-template-columns:1fr 1fr;align-items:start}}
  </style>
</head>
<body>
  <main>
    <div class="top"><a href="/" aria-label="Roddi Health" style="padding:0;background:none;box-shadow:none"><img src="/assets/logo-black.svg" alt="Roddi Health"></a><a href="/">На головну / Home</a></div>
    <h1>Карта сайту · Site map</h1>
    <p class="lead">Усі сторінки Roddi Health в одному місці. · Every page of Roddi Health in one place. Для пошукових систем є <a href="/sitemap.xml">sitemap.xml</a>.</p>
    <div class="cols">%s%s</div>
  </main>
</body>
</html>
''' % (section('uk'), section('en'))
(ROOT / 'sitemap.html').write_text(page, encoding='utf-8')
print('sitemap.html:', len(urls), 'urls')
