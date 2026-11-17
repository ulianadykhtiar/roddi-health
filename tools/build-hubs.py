#!/usr/bin/env python3
"""Builds one hub page per animal (blog/shchury.html, en/blog/rats.html, ...) with photo cards for all our articles about that animal.
Articles live under their hub: /blog/shchury/<slug>. The old flat URLs (/blog/<slug>) get 301 redirects, written into vercel.json here.

Run after tools/build-articles.py:  python3 tools/build-hubs.py
It reuses the page template and the article data of build-articles.py (it runs that script first, so the data is always current).
Also adds a "by animal" link row to blog.html / en/blog.html and the hubs to sitemap.xml (between hubs:start and hubs:end).
"""
import pathlib, re, runpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
g = runpy.run_path(str(ROOT / 'tools' / 'build-articles.py'))
(ARTICLES, page, text, url_of, e, BASE, BY_SLUG, TOPIC_EN, T, HUB_SLUG, LABEL, DIR, hub_path, file_href, photo_file, P) = (
    g[k] for k in ('ARTICLES', 'page', 'text', 'url_of', 'e', 'BASE', 'BY_SLUG', 'TOPIC_EN', 'T', 'HUB_SLUG', 'LABEL', 'DIR', 'hub_path', 'file_href', 'photo_file', 'P'))

COPY = {
    'uk': dict(h1='%s: здоров’я, харчування й догляд', title='%s: усі статті про здоров’я, харчування й догляд',
               desc='Усі матеріали Roddi Health про %s: чим годувати, які бувають хвороби й коли звертатися до ветеринара. Огляди відкритих джерел із посиланнями.',
               intro='Тут зібрано матеріали про %s: %s. У кожній статті є джерела й дата перевірки фактів. Матеріали довідкові й не замінюють ветеринара.',
               all='Усі матеріали блогу', row='За твариною', others='Інші тварини', read='Читати', count=('стаття', 'статті', 'статей'), photo='Фото'),
    'en': dict(h1='%s: health, food and care', title='%s: all articles on health, food and care',
               desc='All Roddi Health articles about %s: what to feed, common illnesses and when to see a vet. Overviews of open sources with links.',
               intro='Articles about %s are collected here: %s. Every article lists its sources and the date the facts were checked. They are reference material and do not replace a vet.',
               all='All blog articles', row='By animal', others='Other animals', read='Read', count=('article', 'articles', 'articles'), photo='Photo'),
}
TOPIC_COLOR = {'Симптоми': '#3172c8', 'Харчування': '#2f7d4f', 'Догляд': '#8a6500', 'Невідкладне': '#c62828'}


def plural(n, forms, lang):
    if lang == 'en':
        return forms[0] if n == 1 else forms[1]
    if n % 10 == 1 and n % 100 != 11: return forms[0]
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return forms[1]
    return forms[2]


def arts(rodent, lang):
    return [a for a in ARTICLES if a['rodent'] == rodent and (lang == 'uk' or 'en' in a)]


def hub_url(rodent, lang):
    return BASE + '/' + hub_path(rodent, lang)


def hub_href(rodent, lang):
    return '/' + hub_path(rodent, lang) + '.html'


def build(rodent, lang):
    items = arts(rodent, lang)
    if not items:
        return None
    c, t = COPY[lang], T[lang]
    label = LABEL[lang][rodent]
    about = LABEL[lang][rodent].lower() if lang == 'en' else {'rat': 'щурів', 'hamster': 'хом’яків', 'guinea-pig': 'морських свинок', 'chinchilla': 'шиншил', 'degu': 'дегу', 'mouse': 'мишей', 'rabbit': 'кроликів'}[rodent]
    topics = []
    for a in items:
        tp = a['topic'] if lang == 'uk' else TOPIC_EN[a['topic']]
        if tp.lower() not in topics: topics.append(tp.lower())
    cards = ''
    for a in items:
        x = text(a, lang)
        ph = P[a['photo']]
        tp = a['topic'] if lang == 'uk' else TOPIC_EN[a['topic']]
        cards += ('<article class="hub-card"><img alt="" src="/%s" width="500" height="312" loading="lazy" style="object-position:%s">'
                  '<div class="hub-card-b"><span class="hub-tag" style="--c:%s">%s</span>'
                  '<h2><a href="%s">%s</a></h2><p>%s</p><span class="hub-more" aria-hidden="true">%s →</span></div></article>') % (
            photo_file(ph['src'], 500), ph.get('pos', '50% 50%'), TOPIC_COLOR.get(a['topic'], '#6e727a'), e(tp), file_href(a['slug'], lang), e(x['title']), e(x['short']), c['read'])
    hero_ph = P[items[0]['photo']]
    count = '%d %s' % (len(items), plural(len(items), c['count'], lang))
    others = ''.join('<a class="hub-chip" href="%s">%s</a>' % (hub_href(r, lang), e(LABEL[lang][r])) for r in HUB_SLUG if r != rodent and arts(r, lang))
    url = hub_url(rodent, lang)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': c['title'] % label, 'description': c['desc'] % about, 'url': url, 'inLanguage': lang,
         'isPartOf': {'@type': 'WebSite', 'url': BASE + '/', 'name': 'Roddi Health'},
         'hasPart': [{'@type': 'Article', 'headline': text(a, lang)['title'], 'url': url_of(a['slug'], lang)} for a in items]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['home'], 'item': t['home_ld']},
            {'@type': 'ListItem', 'position': 2, 'name': t['blog'], 'item': t['blog_ld']},
            {'@type': 'ListItem', 'position': 3, 'name': label}]}]}
    main = f'''<main id="main" class="hub">
  <nav class="ar-crumb" aria-label="{t['crumbs']}"><a href="{t['home_url']}">{t['home']}</a><span aria-hidden="true">/</span><a href="{t['blog_url']}">{t['blog']}</a><span aria-hidden="true">/</span><b>{e(label)}</b></nav>
  <section class="hub-hero soft-grad soft-grad--ask">
    <div class="hub-hero-t"><span class="hub-count">{count}</span><h1 class="t-h1">{e(c['h1'] % label)}</h1><p>{e(c['intro'] % (about, ', '.join(topics)))}</p></div>
    <figure class="hub-photo"><img alt="{e(label)}" src="/{photo_file(hero_ph['src'], 960)}" width="960" height="540" style="object-position:{hero_ph.get('pos', '50% 50%')}"><figcaption>{c['photo']}: <a href="{e(hero_ph['page'])}" target="_blank" rel="noopener">{e(hero_ph['by'])}</a>, {e(hero_ph['lic'])}</figcaption></figure>
  </section>
  <section class="hub-grid" aria-label="{e(label)}">{cards}</section>
  <section class="hub-others"><h2>{c['others']}</h2><div>{others}</div></section>
  <p class="ar-checked"><a href="{t['blog_url']}">{c['all']}</a></p>
</main>'''
    html = page(lang, HUB_SLUG[rodent][0 if lang == 'uk' else 1], c['title'] % label, c['desc'] % about, ld, main)
    # page() builds the URL from the slug, so give the hub its own path; hreflang pair and language switch lead to the same hub in the other language
    wrong = '%s/%s/%s' % (BASE, DIR[lang], HUB_SLUG[rodent][0 if lang == 'uk' else 1])
    html = html.replace(wrong, url)
    alt = ('\n  <link rel="alternate" hreflang="uk" href="%s">\n  <link rel="alternate" hreflang="en" href="%s">\n  <link rel="alternate" hreflang="x-default" href="%s">'
           % (hub_url(rodent, 'uk'), hub_url(rodent, 'en'), hub_url(rodent, 'uk')))
    html = html.replace('<link rel="canonical" href="%s">' % url, '<link rel="canonical" href="%s">%s' % (url, alt), 1)
    if lang == 'uk':
        html = html.replace('href="/en/blog.html" class="lang-opt"', 'href="%s" class="lang-opt"' % hub_href(rodent, 'en'))
    else:
        html = html.replace('href="/blog.html" class="lang-opt"', 'href="%s" class="lang-opt"' % hub_href(rodent, 'uk'))
    out = ROOT / (hub_path(rodent, lang) + '.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    return out


built = {'uk': [], 'en': []}
for r in HUB_SLUG:
    for lang in ('uk', 'en'):
        if build(r, lang):
            built[lang].append(r)

# "By animal" link row on the blog pages, so crawlers and readers can reach the hubs.
for lang, path in (('uk', ROOT / 'blog.html'), ('en', ROOT / 'en' / 'blog.html')):
    c = COPY[lang]
    links = ' · '.join('<a href="%s">%s</a>' % (hub_href(r, lang), LABEL[lang][r]) for r in built[lang])
    block = ('<!-- hubs:start --><nav class="mt-[28px] text-center text-[15px] text-[#6e727a] [&_a]:underline [&_a]:underline-offset-4 [&_a:hover]:text-[#0f0f11]" aria-label="%s"><b>%s:</b> %s</nav><!-- hubs:end -->'
             % (c['row'], c['row'], links))
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'<!-- hubs:start -->.*?<!-- hubs:end -->\s*', '', s, flags=re.S)
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

# 301 redirects from the old flat article URLs (/blog/<slug>, /blog/<slug>.html) to the new ones under the animal.
import json
vc = json.loads((ROOT / 'vercel.json').read_text(encoding='utf-8'))
reds = []
for a in ARTICLES:
    for lang in ('uk', 'en'):
        if lang == 'en' and 'en' not in a:
            continue
        new = '/' + g['art_path'](a['slug'], lang)
        hub = HUB_SLUG[a['rodent']][0 if lang == 'uk' else 1]
        olds = ['/%s/%s' % (DIR[lang], a['slug']), '/%s/%s/%s' % (DIR[lang], hub, a['slug'])]   # flat, and nested with the Ukrainian slug
        for base in olds:
            if base == new:
                continue   # the Ukrainian page keeps its address
            for src in (base, base + '.html'):
                reds.append({'source': src, 'destination': new, 'permanent': True})
vc['redirects'] = reds
(ROOT / 'vercel.json').write_text(json.dumps(vc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('hubs:', {k: len(v) for k, v in built.items()}, 'redirects:', len(reds))
