#!/usr/bin/env python3
"""Tells Bing, Yandex, Seznam, Naver and other IndexNow search engines (and through Bing, ChatGPT search and Copilot) that pages changed.

    python3 tools/indexnow.py            submit every URL of sitemap.xml
    python3 tools/indexnow.py URL ...    submit only these URLs

Run it after a deploy has gone live. The key file https://roddihealth.app/fc91802e7a2213fcff50ca169e6f0715.txt proves the site is ours (the key is public by design).
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = 'roddihealth.app'
KEY = 'fc91802e7a2213fcff50ca169e6f0715'

urls = sys.argv[1:] or re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', body, {'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow accepted', len(urls), 'URLs, HTTP', r.status)
except urllib.error.HTTPError as e:
    print('IndexNow answered HTTP', e.code, '(200 and 202 mean accepted)', e.read()[:200])
