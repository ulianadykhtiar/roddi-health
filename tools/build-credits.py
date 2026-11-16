#!/usr/bin/env python3
"""Builds credits.html and en/credits.html: authors and licences of the photos in the home page carousel (assets/carousel/).

Run after tools/build-articles.py:  python3 tools/build-credits.py
Photo data (author, licence, Commons page) comes from the P table in build-articles.py; the crops are made by make-carousel-photos.py.
CC BY / CC BY-SA ask for: author, title with a link to the source, the licence with a link, and a note that the photo was changed (we crop it).
"""
import pathlib, runpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
g = runpy.run_path(str(ROOT / 'tools' / 'build-articles.py'))
page, e, BASE, T, P = (g[k] for k in ('page', 'e', 'BASE', 'T', 'P'))

PHOTOS = [  # carousel file, key in P, name uk, name en
    ('degu', 'degu2', 'Дегу', 'Degu'), ('guinea-pig', 'gp', 'Морська свинка', 'Guinea pig'), ('hamster', 'hamster2', 'Хом’як', 'Hamster'),
    ('chinchilla', 'chin', 'Шиншила', 'Chinchilla'), ('rat', 'rat2', 'Щур', 'Rat'), ('rabbit', 'rabbit', 'Кролик', 'Rabbit'), ('mouse', 'mouse', 'Миша', 'Mouse'),
]
LICENSE_URL = {
    'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/', 'CC BY-SA 4.0': 'https://creativecommons.org/licenses/by-sa/4.0/',
    'CC BY-SA 3.0': 'https://creativecommons.org/licenses/by-sa/3.0/', 'CC BY-SA 2.0': 'https://creativecommons.org/licenses/by-sa/2.0/',
    'CC0': 'https://creativecommons.org/publicdomain/zero/1.0/',
}
COPY = {
    'uk': dict(title='Фото на головній: автори й ліцензії', h1='Фото на головній: автори й ліцензії', slug='credits', path='credits', crumb='Автори фото', home='Головна', home_href='/index.html',
               desc='Автори, джерела й ліцензії фото тварин у каруселі на головній сторінці Roddi Health. Усі фото з Wikimedia Commons, з вільними ліцензіями.',
               intro='Фото тварин у каруселі на головній сторінці взято з Wikimedia Commons за вільними ліцензіями. Ми їх обрізали під вертикальну картку, більше нічого не змінювали. Фото в статтях блогу підписані під кожною статтею.',
               cols=('Фото', 'Назва файлу', 'Автор', 'Ліцензія'), changed='обрізано', lic_intro='Якщо хочете використати фото самі, перейдіть на сторінку файлу й дотримуйтеся умов ліцензії.', other='/en/credits.html'),
    'en': dict(title='Home page photos: authors and licences', h1='Home page photos: authors and licences', slug='credits', path='en/credits', crumb='Photo credits', home='Home', home_href='/en/index.html',
               desc='Authors, sources and licences of the animal photos in the carousel on the Roddi Health home page. All photos are from Wikimedia Commons under free licences.',
               intro='The animal photos in the carousel on the home page come from Wikimedia Commons under free licences. We cropped them to fit a vertical card and changed nothing else. Photos in blog articles are credited under each article.',
               cols=('Photo', 'File name', 'Author', 'Licence'), changed='cropped', lic_intro='If you want to use a photo yourself, open the file page and follow the licence terms.', other='/credits.html'),
}


def build(lang):
    c, t = COPY[lang], T[lang]
    rows = ''
    for fname, key, nu, ne in PHOTOS:
        ph = P[key]
        file_name = ph['page'].rsplit('File:', 1)[1]
        lic = ph['lic']
        lic_html = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (LICENSE_URL[lic], e(lic)) if lic in LICENSE_URL else e(lic)
        rows += ('<tr><td><img src="/assets/carousel/%s.jpg" alt="%s" width="64" height="80" loading="lazy"></td>'
                 '<td><a href="%s" target="_blank" rel="noopener">%s</a><br><span>%s</span></td><td>%s</td><td>%s</td></tr>') % (
            fname, e(nu if lang == 'uk' else ne), e(ph['page']), e(file_name), c['changed'], e(ph['by']), lic_html)
    main = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="{t['crumbs']}"><a href="{c['home_href']}">{c['home']}</a><span aria-hidden="true">/</span><b>{c['crumb']}</b></nav>
  <h1 class="t-h1">{e(c['h1'])}</h1>
  <p class="ar-meta">{e(c['intro'])}</p>
  <div class="ar-table"><table><thead><tr><th>{c['cols'][0]}</th><th>{c['cols'][1]}</th><th>{c['cols'][2]}</th><th>{c['cols'][3]}</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="ar-checked">{e(c['lic_intro'])}</p>
</main>'''
    html = page(lang, c['slug'], c['title'], c['desc'], {'@context': 'https://schema.org', '@type': 'WebPage', 'name': c['title'], 'url': BASE + '/' + c['path'], 'inLanguage': lang}, main, og='website')
    url = BASE + '/' + c['path']
    html = html.replace('%s/%s/%s' % (BASE, g['DIR'][lang], c['slug']), url)   # page() puts articles under /blog; this page is at the site root
    html = html.replace('content="index, follow, max-image-preview:large, max-snippet:-1"', 'content="noindex, follow"')
    # the language switch leads to the same page in the other language; no hreflang pair needed for a noindex page
    if lang == 'uk':
        html = html.replace('href="/en/blog.html" class="lang-opt"', 'href="%s" class="lang-opt"' % c['other'])
    else:
        html = html.replace('href="/blog.html" class="lang-opt"', 'href="%s" class="lang-opt"' % c['other'])
    (ROOT / (c['path'] + '.html')).write_text(html, encoding='utf-8')


for lang in ('uk', 'en'):
    build(lang)
print('credits pages written')
