#!/usr/bin/env python3
"""Builds the English pages in en/ from the Ukrainian ones.

Ukrainian pages are the source. After changing their text, add the new
phrase to tools/en.json and run:  python3 tools/build_en.py
The script stops and lists any Ukrainian text that has no translation.
"""
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


def build(name):
    used.clear()
    s = (ROOT / name).read_text(encoding="utf-8")
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
