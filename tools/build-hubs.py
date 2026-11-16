#!/usr/bin/env python3
"""Builds one hub page per animal (blog/shchury.html, en/blog/rats.html, ...) listing all our articles about that animal.

Run after tools/build-articles.py:  python3 tools/build-hubs.py
It reuses the page template and the article data of build-articles.py (it runs that script first, so the data is always current).
Also adds a "by animal" link row to blog.html / en/blog.html and the hubs to sitemap.xml (between hubs:start and hubs:end).
"""
import pathlib, re, runpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
g = runpy.run_path(str(ROOT / 'tools' / 'build-articles.py'))
ARTICLES, page, text, url_of, e, BASE, UP, BY_SLUG, TOPIC_EN, T = (g[k] for k in ('ARTICLES', 'page', 'text', 'url_of', 'e', 'BASE', 'UP', 'BY_SLUG', 'TOPIC_EN', 'T'))

# rodent key -> (slug uk, label uk, "about" uk, slug en, label en)
HUBS = {
    'rat':        ('shchury',        'Щури',           'щурів',         'rats',        'Rats'),
    'hamster':    ('khomiaky',       'Хом’яки',        'хом’яків',      'hamsters',    'Hamsters'),
    'guinea-pig': ('morski-svynky',  'Морські свинки', 'морських свинок', 'guinea-pigs', 'Guinea pigs'),
    'chinchilla': ('shynshyly',      'Шиншили',        'шиншил',        'chinchillas', 'Chinchillas'),
    'degu':       ('degu',           'Дегу',           'дегу',          'degus',       'Degus'),
    'mouse':      ('myshi',          'Миші',           'мишей',         'mice',        'Mice'),
    'rabbit':     ('kroliky',        'Кролики',        'кроликів',      'rabbits',     'Rabbits'),
}
COPY = {
    'uk': dict(h1='%s: здоров’я, харчування й догляд', title='%s: усі статті про здоров’я, харчування й догляд',
               desc='Усі матеріали Roddi Health про %s: чим годувати, які бувають хвороби й коли звертатися до ветеринара. Огляди відкритих джерел із посиланнями.',
               intro='Тут зібрано матеріали про %s: %s. У кожній статті є джерела й дата перевірки фактів. Матеріали довідкові й не замінюють ветеринара.',
               all='Усі матеріали блогу', row='За твариною'),
    'en': dict(h1='%s: health, food and care', title='%s: all articles on health, food and care',
               desc='All Roddi Health articles about %s: what to feed, common illnesses and when to see a vet. Overviews of open sources with links.',
               intro='Articles about %s are collected here: %s. Every article lists its sources and the date the facts were checked. They are reference material and do not replace a vet.',
               all='All blog articles', row='By animal'),
}


def arts(rodent, lang):
    return [a for a in ARTICLES if a['rodent'] == rodent and (lang == 'uk' or 'en' in a)]


def hub_slug(rodent, lang):
    return 'blog/' + HUBS[rodent][0 if lang == 'uk' else 3]


def hub_url(rodent, lang):
    return BASE + ('/' if lang == 'uk' else '/en/') + hub_slug(rodent, lang)


def build(rodent, lang):
    items = arts(rodent, lang)
    if len(items) < 2:
        return None
    c, t = COPY[lang], T[lang]
    label = HUBS[rodent][1 if lang == 'uk' else 4]
    about = HUBS[rodent][2] if lang == 'uk' else HUBS[rodent][4].lower()
    topics = []
    for a in items:
        tp = a['topic'] if lang == 'uk' else TOPIC_EN[a['topic']]
        if tp.lower() not in topics: topics.append(tp.lower())
    cards = ''.join('<a href="%s%s.html" class="ar-rel"><span>%s</span><b>%s</b></a>' % (
        '' if lang == 'uk' else '/en/blog/', a['slug'] if lang != 'uk' else a['slug'],
        e(a['topic'] if lang == 'uk' else TOPIC_EN[a['topic']]), e(text(a, lang)['title'])) for a in items)
    url = hub_url(rodent, lang)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': c['title'] % label, 'description': c['desc'] % about, 'url': url, 'inLanguage': lang,
         'isPartOf': {'@type': 'WebSite', 'url': BASE + '/', 'name': 'Roddi Health'},
         'hasPart': [{'@type': 'Article', 'headline': text(a, lang)['title'], 'url': url_of(a['slug'], lang)} for a in items]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['home'], 'item': t['home_ld']},
            {'@type': 'ListItem', 'position': 2, 'name': t['blog'], 'item': t['blog_ld']},
            {'@type': 'ListItem', 'position': 3, 'name': label}]}]}
    blog_href = '../blog.html' if lang == 'uk' else '/en/blog.html'
    home_href = '../index.html' if lang == 'uk' else '/en/index.html'
    main = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="{t['crumbs']}"><a href="{home_href}">{t['home']}</a><span aria-hidden="true">/</span><a href="{blog_href}">{t['blog']}</a><span aria-hidden="true">/</span><b>{label}</b></nav>
  <h1 class="t-h1">{e(c['h1'] % label)}</h1>
  <p class="ar-meta">{e(c['intro'] % (about, ', '.join(topics)))}</p>
  <section class="ar-related" aria-label="{e(label)}"><div>{cards}</div></section>
  <p class="ar-checked"><a href="{blog_href}">{c['all']}</a></p>
</main>'''
    other = 'en' if lang == 'uk' else 'uk'
    html = page(lang, HUBS[rodent][0 if lang == 'uk' else 3], c['title'] % label, c['desc'] % about, ld, main)
    # hreflang pair and the language switch lead to the same hub in the other language
    alt = ('\n  <link rel="alternate" hreflang="uk" href="%s">\n  <link rel="alternate" hreflang="en" href="%s">\n  <link rel="alternate" hreflang="x-default" href="%s">'
           % (hub_url(rodent, 'uk'), hub_url(rodent, 'en'), hub_url(rodent, 'uk')))
    html = html.replace('<link rel="canonical" href="%s">' % url, '<link rel="canonical" href="%s">%s' % (url, alt), 1)
    if lang == 'uk':
        html = html.replace('href="../en/blog.html" class="lang-opt"', 'href="../en/blog/%s.html" class="lang-opt"' % HUBS[rodent][3])
    else:
        html = html.replace('href="/blog.html" class="lang-opt"', 'href="/blog/%s.html" class="lang-opt"' % HUBS[rodent][0])
    out = ROOT / ('' if lang == 'uk' else 'en') / (hub_slug(rodent, lang) + '.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out


built = {'uk': [], 'en': []}
for r in HUBS:
    for lang in ('uk', 'en'):
        if lang == 'en' and not build(r, 'uk'):
            continue
        if build(r, lang):
            built[lang].append(r)

# "By animal" row at the end of the blog pages, so crawlers and readers can reach the hubs.
for lang, path in (('uk', ROOT / 'blog.html'), ('en', ROOT / 'en' / 'blog.html')):
    c = COPY[lang]
    base = '' if lang == 'uk' else '/en/'
    links = ' · '.join('<a href="%s%s">%s</a>' % (base, hub_slug(r, lang), HUBS[r][1 if lang == 'uk' else 4]) for r in built[lang])
    block = ('<!-- hubs:start --><nav class="mt-[28px] text-center text-[15px] text-[#6e727a] [&_a]:underline [&_a]:underline-offset-4 [&_a:hover]:text-[#0f0f11]" aria-label="%s"><b>%s:</b> %s</nav><!-- hubs:end -->'
             % (c['row'], c['row'], links))
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'<!-- hubs:start -->.*?<!-- hubs:end -->', '', s, flags=re.S)
    anchor = '<div id="blog-empty"'
    assert s.count(anchor) == 1, path
    s = s.replace(anchor, block + '\n    ' + anchor, 1)
    path.write_text(s, encoding='utf-8')

# Sitemap entries.
sm = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
sm = re.sub(r'\s*<!-- hubs:start -->.*?<!-- hubs:end -->', '', sm, flags=re.S)
last = g.get('UPDATED', '2026-11-16')
urls = ''.join('\n  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (hub_url(r, lang), last) for lang in ('uk', 'en') for r in built[lang])
sm = sm.replace('</urlset>', '  <!-- hubs:start -->' + urls + '\n  <!-- hubs:end -->\n</urlset>')
(ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
print('hubs:', {k: len(v) for k, v in built.items()})
