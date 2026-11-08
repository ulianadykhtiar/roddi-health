#!/usr/bin/env python3
"""Builds the English pages in en/ from the Ukrainian ones, and fills the SEO
head and the crawler-readable blog list on every page (data: tools/seo.json).

Ukrainian pages are the source. After changing their text, add the new
phrase to tools/en.json and run:  python3 tools/build_en.py
The script stops and lists any Ukrainian text that has no translation.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "blog.html", "thank-you.html"]
CYR = re.compile("[А-Яа-яЇїІіЄєҐґ]")
TOKEN = re.compile(r"""(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<(?:[^<>"']|"[^"]*"|'[^']*')+>)""", re.S | re.I)
ATTR = re.compile(r"""\b(alt|placeholder|aria-label|title|content)="([^"]*)\"""")
# Search helpers in the blog script hold Cyrillic on purpose.
SCRIPT_OK = re.compile(r"function norm\(s\)")

data = json.loads((ROOT / "tools/en.json").read_text(encoding="utf-8"))
seo = json.loads((ROOT / "tools/seo.json").read_text(encoding="utf-8"))
SEO_RE = re.compile(r"<!-- seo:start -->.*?<!-- seo:end -->", re.S)
POSTS_RE = re.compile(r"<!-- posts:start -->.*?<!-- posts:end -->", re.S)
OTHER = {"uk": "en", "en": "uk"}
LOCALE = {"uk": "uk_UA", "en": "en_US"}
missing = []
used = {}


def norm(t):
    return " ".join(t.replace("&nbsp;", " ").replace(" ", " ").split())


def tr(t):
    key = norm(t)
    if key not in data["text"]:
        missing.append(key)
        return t
    val = data["text"][key]
    if isinstance(val, list):  # same letter, different words, in page order
        i = used.get(key, 0)
        used[key] = i + 1
        val = val[i % len(val)]
    return val


def text_node(t):
    if not CYR.search(t):
        return t
    lead = t[: len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    return lead + tr(t) + trail


def tag(m):
    return m.group(1) + '="' + tr(m.group(2)) + '"' if CYR.search(m.group(2)) else m.group(0)


def script(s):
    for k, v in data["script"].items():
        s = s.replace(k, v)
    for line in s.split("\n"):
        if CYR.search(line) and not line.strip().startswith("//") and not SCRIPT_OK.search(line):
            missing.append("script: " + line.strip()[:160])
    return s


def esc(t):
    return html.escape(t, quote=True)


def read_posts():
    """Title, excerpt, source and link of each blog post, in both languages."""
    uk_js = (ROOT / "assets/blog-posts.js").read_text(encoding="utf-8")
    en_js = (ROOT / "assets/blog-posts.en.js").read_text(encoding="utf-8")
    uk = re.findall(r"title: '([^']*)',\s*excerpt: '([^']*)',.*?source: '([^']*)', url: '([^']*)'", uk_js, re.S)
    en = re.findall(r"title: '([^']*)',\s*excerpt: '([^']*)',", en_js)
    if len(uk) != len(en):
        sys.exit("blog-posts.js and blog-posts.en.js have different numbers of posts")
    return {
        "uk": [{"title": t, "excerpt": e, "source": s, "url": u} for t, e, s, u in uk],
        "en": [{"title": e2[0], "excerpt": e2[1], "source": u2[2], "url": u2[3]} for e2, u2 in zip(en, uk)],
    }


posts = read_posts()


def posts_html(lang):
    return "".join(
        '<article class="blog-static"><h3><a href="%s" rel="noopener">%s</a></h3><p>%s</p><p>%s</p></article>'
        % (esc(p["url"]), esc(p["title"]), esc(p["excerpt"]), esc(p["source"]))
        for p in posts[lang]
    )


def json_ld(name, lang, page, url):
    site, org = seo["site"], seo["site"] + "/#organization"
    home = site + page_path("index.html", lang) if lang == "en" else site + "/"
    site_id = home + "#website"
    website = {"@type": "WebSite", "@id": site_id, "url": home, "name": seo["name"], "inLanguage": lang, "publisher": {"@id": org}}
    graph = []
    if name == "index.html":
        graph = [
            {"@type": "Organization", "@id": org, "name": seo["name"], "url": site + "/", "logo": site + "/assets/vector.svg",
             "email": seo["email"], "sameAs": seo["sameAs"]},
            website,
            {"@type": "SoftwareApplication", "name": seo["name"], "url": url, "applicationCategory": "HealthApplication",
             "description": page["app"], "inLanguage": lang, "publisher": {"@id": org}},
            {"@type": "FAQPage", "@id": url + "#faq", "inLanguage": lang, "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in page["faq"]]},
        ]
    elif name == "blog.html":
        graph = [
            website,
            {"@type": "CollectionPage", "@id": url + "#page", "url": url, "name": page["title"], "description": page["description"],
             "inLanguage": lang, "isPartOf": {"@id": site_id},
             "mainEntity": {"@type": "ItemList", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "name": p["title"], "url": p["url"]} for i, p in enumerate(posts[lang])]}},
        ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    return '<script type="application/ld+json">%s</script>' % body.replace("</", "<\\/")


def page_path(name, lang):
    return seo["pages"][name]["path"][lang]


def seo_head(name, lang):
    info = seo["pages"][name]
    page = info[lang]
    lines = ["<title>%s</title>" % esc(page["title"]), '<link rel="icon" type="image/svg+xml" href="/assets/vector.svg">']
    if info.get("noindex"):
        lines.append('<meta name="robots" content="noindex">')
        return "\n  ".join(lines)
    site = seo["site"]
    url = site + page_path(name, lang)
    image = "%s/assets/og-%s.jpg" % (site, lang)
    title, desc = esc(page["title"]), esc(page["description"])
    lines += [
        '<meta name="description" content="%s">' % desc,
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        '<link rel="canonical" href="%s">' % url,
        '<link rel="alternate" hreflang="uk" href="%s">' % (site + page_path(name, "uk")),
        '<link rel="alternate" hreflang="en" href="%s">' % (site + page_path(name, "en")),
        '<link rel="alternate" hreflang="x-default" href="%s">' % (site + page_path(name, "uk")),
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="%s">' % esc(seo["name"]),
        '<meta property="og:title" content="%s">' % title,
        '<meta property="og:description" content="%s">' % desc,
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % image,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="%s">' % LOCALE[lang],
        '<meta property="og:locale:alternate" content="%s">' % LOCALE[OTHER[lang]],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % title,
        '<meta name="twitter:description" content="%s">' % desc,
        '<meta name="twitter:image" content="%s">' % image,
        json_ld(name, lang, page, url),
    ]
    return "\n  ".join(lines)


def refresh_source(name):
    """Writes the current SEO head and blog list into a Ukrainian page."""
    path = ROOT / name
    s = path.read_text(encoding="utf-8")
    s = SEO_RE.sub(lambda m: "<!-- seo:start -->\n  %s\n  <!-- seo:end -->" % seo_head(name, "uk"), s)
    s = POSTS_RE.sub(lambda m: "<!-- posts:start -->%s<!-- posts:end -->" % posts_html("uk"), s)
    path.write_text(s, encoding="utf-8")


def build(name):
    used.clear()
    refresh_source(name)
    s = (ROOT / name).read_text(encoding="utf-8")
    # Filled in after translation: these two regions are generated per language.
    s = SEO_RE.sub('<meta name="__seo__">', s)
    s = POSTS_RE.sub('<meta name="__posts__">', s)
    for k, v in data["html"].items():
        s = s.replace(k, v)
    out = []
    for i, part in enumerate(TOKEN.split(s)):
        if i % 2 == 0:
            out.append(text_node(part))
        elif part.startswith("<!--"):
            continue
        elif part[:7].lower() == "<script":
            out.append(script(part))
        elif part[:6].lower() == "<style":
            out.append(part)
        else:
            out.append(ATTR.sub(tag, part))
    s = "".join(out)

    s = s.replace('<html lang="uk"', '<html lang="en"')
    # Absolute paths, so pages work at both /en/page.html and /en/page.
    s = re.sub(r"(?<![\w./-])assets/", "/assets/", s)
    s = re.sub(r'href="/(#[^"]*)?"', lambda m: 'href="/en/%s"' % (m.group(1) or ""), s)
    s = re.sub(r'href="(blog|thank-you)\.html"', r'href="/en/\1.html"', s)
    # Language switch: English is now the current page, Ukrainian the link.
    uk_href = "/" if name == "index.html" else "/" + name
    s = re.sub(
        r'<span class="lang-opt is-active" lang="uk" aria-current="true">UA</span>\s*<a href="[^"]*" class="lang-opt" lang="en" hreflang="en">EN</a>',
        '<a href="%s" class="lang-opt" lang="uk" hreflang="uk">UA</a>\n        <span class="lang-opt is-active" lang="en" aria-current="true">EN</span>' % uk_href,
        s,
    )
    s = s.replace(
        '<script src="/assets/blog-posts.js"></script>',
        '<script src="/assets/blog-posts.js"></script>\n<script src="/assets/blog-posts.en.js"></script>',
    )
    s = s.replace('<meta name="__seo__">', seo_head(name, "en"))
    s = s.replace('<meta name="__posts__">', posts_html("en"))
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en" / name).write_text(s, encoding="utf-8")


for page in PAGES:
    build(page)

if missing:
    print("No translation in tools/en.json for:")
    for m in dict.fromkeys(missing):
        print("  " + m)
    sys.exit(1)
print("Built en/: " + ", ".join(PAGES))
