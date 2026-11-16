#!/usr/bin/env python3
"""Local server that behaves like Vercel for this site:  python3 tools/serve.py [port]   (default 8766)

- clean URLs: /blog/shchury opens blog/shchury.html, /en opens en/index.html (python -m http.server cannot do this);
- redirects from vercel.json (old article addresses) with their real status;
- 404.html with a 404 status for unknown addresses.
"""
import http.server, json, pathlib, sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
REDIRECTS = {r['source']: r['destination'] for r in json.loads((ROOT / 'vercel.json').read_text(encoding='utf-8')).get('redirects', [])}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def resolve(self, path):
        rel = path.strip('/')
        for cand in ((ROOT / rel) if rel else ROOT / 'index.html', ROOT / (rel + '.html'), ROOT / rel / 'index.html'):
            if cand.is_file():
                return '/' + str(cand.relative_to(ROOT))
        return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path in REDIRECTS:
            self.send_response(308)
            self.send_header('Location', REDIRECTS[path])
            self.end_headers()
            return
        found = self.resolve(path)
        if found:
            self.path = found + (('?' + urlparse(self.path).query) if urlparse(self.path).query else '')
            return super().do_GET()
        page = (ROOT / '404.html').read_bytes()
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    do_HEAD = do_GET

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    print('http://localhost:%d' % PORT)
    http.server.ThreadingHTTPServer(('', PORT), Handler).serve_forever()
