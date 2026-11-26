#!/usr/bin/env python3
"""Builds llms.txt and llms-full.txt, the plain-text maps of the site for AI assistants and answer engines.

    python3 tools/build-llms.py

llms.txt      short: what Roddi Health is, key facts, FAQ, and a link plus one-line summary for every page and article
llms-full.txt the same plus the full text of every article (both languages) and its sources

Everything is read from the built pages (titles, summaries, dates, sources), so nothing here is typed twice.
The script is idempotent; CI runs it and fails if the files are out of date.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://roddihealth.app'


def read(p):
    return (ROOT / p).read_text(encoding='utf-8')


def jsonld(html):
    out = []
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            j = json.loads(b)
        except ValueError:
            continue
        out += j.get('@graph') or [j]
    return out


class Text(HTMLParser):
    """Turns the article body into plain markdown-ish text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []; self.buf = []; self.tag = None; self.depth = 0

    def handle_starttag(self, tag, a):
        if tag in ('h2', 'h3', 'p', 'li'):
            self.flush(); self.tag = tag
        if tag == 'br':
            self.buf.append(' ')

    def handle_endtag(self, tag):
        if tag in ('h2', 'h3', 'p', 'li'):
            self.flush()

    def handle_data(self, d):
        self.buf.append(d)

    def flush(self):
        t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        self.buf = []
        if t:
            prefix = {'h2': '\n### ', 'h3': '\n#### ', 'li': '- '}.get(self.tag, '')
            self.out.append(prefix + t)
        self.tag = None


def body_text(html):
    m = re.search(r'<div class="ar-body">(.*?)</div>\s*(?:<div class="ar-src|<section|<footer|<aside)', html, re.S)
    if not m:
        m = re.search(r'<div class="ar-body">(.*)', html, re.S)
    p = Text(); p.feed(m.group(1)); p.flush()
    return '\n\n'.join(p.out).replace('\n\n- ', '\n- ')


def article(path):
    html = read(path)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S).group(1)
    h1 = re.sub(r'<[^>]+>', '', h1).strip()
    short = re.search(r'<p class="ar-short-l">[^<]*</p><p>(.*?)</p>', html, re.S)
    short = re.sub(r'<[^>]+>', '', short.group(1)).strip() if short else ''
    url = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
    post = next((n for n in jsonld(html) if n.get('@type') == 'BlogPosting'), {})
    return {'title': h1, 'short': short, 'url': url, 'updated': post.get('dateModified', ''),
            'sources': post.get('citation') or [], 'body': body_text(html)}


def faq(path):
    for n in jsonld(read(path)):
        if n.get('@type') == 'FAQPage':
            return [(q['name'], re.sub(r'<[^>]+>', '', q['acceptedAnswer']['text']).strip()) for q in n['mainEntity']]
    return []


def hub(path):
    html = read(path)
    h1 = re.sub(r'<[^>]+>', '', re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S).group(1)).strip()
    url = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
    return h1, url


HEAD = """# Roddi Health

> Roddi Health is a mobile app in development for owners of rats, hamsters, guinea pigs, rabbits, chinchillas, degus, mice and other small pets. It brings medication reminders, symptom and weight logs and vet visit history together in one place, even for several pets. Roddi Health does not replace a veterinary consultation.

Status: in development, with a free early access list. It is free during the beta. Launch date, pricing and platforms are not announced yet.

The project grew out of a rat blog followed by 7,000+ people on Instagram and TikTok (@marchin_rats). Contact: roddihealth@gmail.com

The site is available in Ukrainian (default) and English. Articles are original overviews written from the veterinary sources they name (RSPCA, PDSA, PetMD and similar); they are reference material, not diagnosis or treatment advice.
"""


def main():
    uk = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'blog').glob('*/*.html'))
    en = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'en/blog').glob('*/*.html'))
    arts = [article(p) for p in uk], [article(p) for p in en]
    hubs_uk = [hub(p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / 'blog').glob('*.html')) if p.name != 'pro-materialy.html']
    hubs_en = [hub(p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / 'en/blog').glob('*.html')) if p.name != 'pro-materialy.html']

    L = [HEAD, '## Main pages\n',
         f'- [Roddi Health in English]({BASE}/en): what the app does, who it is for, FAQ and early access sign-up',
         f'- [Roddi Health українською]({BASE}/): додаток для здоров\'я гризунів, ранній доступ',
         f'- [Privacy policy]({BASE}/en/privacy): what is collected and why, who is responsible, how to unsubscribe or delete data',
         f'- [How we prepare materials]({BASE}/en/blog/pro-materialy): the editorial policy, sources, update and review dates\n']
    f_en = faq('en/index.html')
    if f_en:
        L.append('## Frequently asked questions\n')
        for q, a in f_en:
            L.append(f'**{q}** {a}\n')
    L.append('## Blog\n')
    L.append(f'- [Rodent health blog]({BASE}/en/blog): short guides on symptoms, nutrition, care and emergencies, each citing its veterinary sources')
    L.append(f'- [Блог про здоров\'я гризунів]({BASE}/blog): короткі поради з посиланнями на ветеринарні джерела')
    for h, u in hubs_en:
        L.append(f'- [{h}]({u})')
    for h, u in hubs_uk:
        L.append(f'- [{h}]({u})')
    L.append('\n## Articles in English\n')
    for a in arts[1]:
        L.append(f"- [{a['title']}]({a['url']}): {a['short']}")
    L.append('\n## Статті українською\n')
    for a in arts[0]:
        L.append(f"- [{a['title']}]({a['url']}): {a['short']}")
    L.append('\n## Optional\n')
    L.append(f'- [Full text of all articles]({BASE}/llms-full.txt): one plain-text file with every article and its sources')
    L.append(f'- [Sitemap]({BASE}/sitemap.xml)')
    (ROOT / 'llms.txt').write_text('\n'.join(L) + '\n', encoding='utf-8')

    F = [HEAD, f'Short version with links: {BASE}/llms.txt\n']
    for label, group in (('English articles', arts[1]), ('Статті українською', arts[0])):
        F.append(f'\n# {label}\n')
        for a in group:
            F.append(f"## {a['title']}\n\nURL: {a['url']}\nUpdated: {a['updated']}\n\nSummary: {a['short']}\n\n{a['body']}\n")
            if a['sources']:
                F.append('Sources:\n' + '\n'.join('- ' + s for s in a['sources']) + '\n')
    (ROOT / 'llms-full.txt').write_text('\n'.join(F) + '\n', encoding='utf-8')
    print('llms.txt: %d articles uk, %d en; llms-full.txt written' % (len(arts[0]), len(arts[1])))


if __name__ == '__main__':
    main()
