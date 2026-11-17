#!/usr/bin/env python3
"""Builds assets/tailwind.css, the static replacement for the Tailwind Play CDN script.

Run it after you add or change Tailwind classes in any page or script:  python3 tools/build-css.py
Needs Node (npm). It installs the pinned Tailwind CLI into a temporary folder, so nothing is added to the project.
Classes are read from the files listed in tools/tailwind-input.css.
"""
import pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION = '4.1.11'

src = (ROOT / 'tools' / 'tailwind-input.css').read_text(encoding='utf-8')
# @source paths are written relative to tools/; make them absolute for the temporary build folder.
src = re.sub(r'@source "\.\./', '@source "%s/' % ROOT, src)

with tempfile.TemporaryDirectory() as tmp:
    for cmd in (['npm', 'init', '-y'], ['npm', 'i', '--silent', f'@tailwindcss/cli@{VERSION}', f'tailwindcss@{VERSION}']):
        subprocess.run(cmd, cwd=tmp, check=True, stdout=subprocess.DEVNULL)
    (pathlib.Path(tmp) / 'in.css').write_text(src, encoding='utf-8')
    out = ROOT / 'assets' / 'tailwind.css'
    r = subprocess.run(['./node_modules/.bin/tailwindcss', '-i', 'in.css', '-o', str(out), '--minify'], cwd=tmp)
    if r.returncode:
        sys.exit(r.returncode)
print('assets/tailwind.css?v=blue1 written,', out.stat().st_size, 'bytes')
