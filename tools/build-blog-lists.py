#!/usr/bin/env python3
"""Refreshes the two blog lists that build_en.py normally writes, without touching anything else.

    python3 tools/build-blog-lists.py

blog.html and en/blog.html each carry
  * the post list for bots without JavaScript (between posts:start and posts:end), and
  * an ItemList in the page's structured data (inside seo:start / seo:end).
build_en.py rebuilds whole English pages and must not be run right now, so this script
updates only these two lists from assets/blog-posts.js, assets/blog-posts.en.js and
assets/blog-articles.js. Run it after adding or removing a card or an article.
Differences from build_en.py: each static card says it is an article on an external site,
and the Ukrainian ItemList also lists our own articles. Running build_en.py would undo both,
so port them there before using it again.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://roddihealth.app'
EXTERNAL = {'uk': 'стаття на сторонньому сайті', 'en': 'article on an external site'}
# blog.html keeps build_en.py's markers; en/blog.html is generated without them, so there the
# list is the run of static cards at the start of #blog-grid.
POSTS_RE = re.compile(r'<!-- posts:start -->.*?<!-- posts:end -->', re.S)
EN_POSTS_RE = re.compile(r'(<div id="blog-grid"[^>]*>)(?:<article class="blog-static">.*?</article>)*', re.S)
LD_RE = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def esc(t):
    return html.escape(t, quote=True)


def read_posts():
    uk_js = (ROOT / 'assets/blog-posts.js').read_text(encoding='utf-8')
    en_js = (ROOT / 'assets/blog-posts.en.js').read_text(encoding='utf-8')
    uk = re.findall(r"title: '([^']*)',\s*excerpt: '([^']*)',.*?source: '([^']*)', url: '([^']*)'", uk_js, re.S)
    en = re.findall(r"title: '([^']*)',\s*excerpt: '([^']*)',", en_js)
    if len(uk) != len(en):
        sys.exit('blog-posts.js and blog-posts.en.js have different numbers of posts')
    return {
        'uk': [{'title': t, 'excerpt': e, 'source': s, 'url': u} for t, e, s, u in uk],
        'en': [{'title': e2[0], 'excerpt': e2[1], 'source': u2[2], 'url': u2[3]} for e2, u2 in zip(en, uk)],
    }


def read_articles():
    js = (ROOT / 'assets/blog-articles.js').read_text(encoding='utf-8')
    return json.loads(js[js.index('['):js.rindex(']') + 1])


posts = read_posts()
articles = read_articles()


def posts_html(lang):
    return ''.join(
        '<article class="blog-static"><h3><a href="%s" rel="noopener">%s</a></h3><p>%s</p><p>%s · %s</p></article>'
        % (esc(p['url']), esc(p['title']), esc(p['excerpt']), esc(p['source']), EXTERNAL[lang])
        for p in posts[lang])


def item_list(lang):
    # Our own articles exist only in Ukrainian so far, so the English list has just the cards.
    items = [(a['title'], BASE + '/' + a['url']) for a in articles] if lang == 'uk' else []
    items += [(p['title'], p['url']) for p in posts[lang]]
    return [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'url': u} for i, (n, u) in enumerate(items)]


def refresh(name, lang):
    path = ROOT / name
    s = path.read_text(encoding='utf-8')
    if lang == 'uk':
        assert len(POSTS_RE.findall(s)) == 1, name
        s = POSTS_RE.sub(lambda m: '<!-- posts:start -->%s<!-- posts:end -->' % posts_html(lang), s)
    else:
        assert len(EN_POSTS_RE.findall(s)) == 1, name
        s = EN_POSTS_RE.sub(lambda m: m.group(1) + posts_html(lang), s)
    m = LD_RE.search(s)
    assert m, name
    data = json.loads(m.group(2).replace('<\\/', '</'))
    page = next(g for g in data['@graph'] if g.get('@type') == 'CollectionPage')
    page['mainEntity']['itemListElement'] = item_list(lang)
    body = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    s = s[:m.start(2)] + body + s[m.end(2):]
    path.write_text(s, encoding='utf-8')
    return len(page['mainEntity']['itemListElement'])


for name, lang in (('blog.html', 'uk'), ('en/blog.html', 'en')):
    print(name, refresh(name, lang), 'items')
