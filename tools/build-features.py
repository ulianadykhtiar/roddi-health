"""Build the "Що вміє Roddi Health" block on both homepages.

    python3 tools/build-features.py

Writes <section id="features"> into index.html and, in English, into en/index.html
(text from tools/features-en.json), with the stylesheet and script it needs.
Desktop: the section is pinned and its cards stack as you scroll; phones: the
features simply follow each other. Card backgrounds are assets/features/pastel-1..4.jpg
(made by tools/make-feature-backgrounds.py). Styles and behaviour:
assets/features-pin.css and assets/features-pin.js. Edit this file, not the HTML.
"""
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def svg(path, size=18, sw=2):
    return (f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{path}</svg>')
CHECK = svg('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 13, 3.4)
SPARK = '<path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4"/>'
ICONS = ['<rect x="3" y="8.5" width="18" height="7" rx="3.5" transform="rotate(-35 12 12)"/><path d="m9.2 8 5.6 8"/>',
         '<path d="M4 19V5M4 19h16"/><path d="m7 15 4-4 3 3 5-6"/>',
         '<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M8 3v4M16 3v4M3.5 10h17"/>',
         '<path d="M6 3.5h9l3.5 3.5v13.5H6z"/><path d="M9 11h6M9 15h4"/>']

FEATURES = [
    ('Нагадування', 'Не пропустіть жодної дози', 'Налаштуйте курс лікування один раз, і нагадування прийдуть вчасно. Позначайте прийом одним дотиком. Так само працюють нагадування про візити, зважування та чистку клітки.'),
    ('Стан і вага', 'Стежте, як змінюється стан', 'Записуйте симптоми й вагу, а додаток покаже динаміку на графіку. Так легше помітити зміни вчасно.'),
    ('Візити', 'Приходьте до ветеринара з готовою історією', 'Візити, призначення, поточне й минуле лікування, аналізи в одному профілі улюбленця. На прийомі не доведеться згадувати.'),
    ('Нотатки', 'Усе під рукою', 'Нотатки, особливості здоров’я та швидкий пошук: знайдете потрібне за секунди, навіть якщо у вас кілька гризунів.'),
]

A = 'assets/app/'
MARTIN, ARCHIE, SKY = A + 'martin.png', A + 'archie.png', A + 'sky.png'

def at(x, y, w=None, z=None):
    s = f'left:{x}px;top:{y}px'
    if w: s += f';--w:{w}px'
    if z: s += f';z-index:{z}'
    return s

def duo(*imgs):
    return '<span class="w-duo">' + ''.join(f'<img alt="" src="{i}">' for i in imgs) + '</span>'

def notif(title, sub, when='зараз', glass=True):
    return (f'<div class="w w-notif{" w-glass" if glass else ""}"><span class="logo"><img alt="" src="assets/logo-white.svg"></span>'
            f'<div class="min-w-0 flex-1"><div class="flex justify-between gap-[8px]"><small>Roddi Health</small><small class="!normal-case !tracking-normal">{when}</small></div>'
            f'<b>{title}</b><span>{sub}</span></div></div>')

# ---- scenes: 560×440 compositions of app-style widgets ----
# Components (see assets/features-pin.css): a-h heading, a-opt pill row (.on = chosen, navy),
# a-tiles / a-tile emoji tiles, a-steps segments, a-cta pill button.
L = {  # line icons, same family as the app's list rows
    'tag': '<path d="M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.3 8.3a1.5 1.5 0 0 1 0 2.1l-5.6 5.6a1.5 1.5 0 0 1-2.1 0z"/><circle cx="8" cy="8" r="1.4"/>',
    'clip': '<rect x="5" y="4.5" width="14" height="16.5" rx="3"/><path d="M9 4.5V3.5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1M8.5 11h7M8.5 15h5"/>',
    'chart': '<path d="M4 19V5M4 19h16"/><path d="m7.5 15 3.5-4 3 3 5-6"/>',
    'drop': '<path d="M12 3.5s6 6.2 6 10.3a6 6 0 0 1-12 0C6 9.700 12 3.500 12 3.500z"/>',
    'steam': '<path d="M8 4c-1.500 1.700 1.500 3 0 4.700M12.500 4c-1.500 1.700 1.500 3 0 4.700M17 4c-1.500 1.700 1.500 3 0 4.700"/><path d="M4.500 13h15a0 0 0 0 1 0 0 7 7 0 0 1-7 7h-1a7 7 0 0 1-7-7z"/>',
    'pill': '<path d="M10.5 20.5a4.5 4.5 0 0 1-6.4-6.4l9.9-9.9a4.5 4.5 0 0 1 6.4 6.4z"/><path d="m8.5 8.5 7 7"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.500-3.500"/>',
    'paw': '<circle cx="6.500" cy="10" r="1.800"/><circle cx="10" cy="6" r="1.800"/><circle cx="14" cy="6" r="1.800"/><circle cx="17.500" cy="10" r="1.800"/><path d="M12 12.500c-3 0-5 2.700-5 4.700 0 1.600 1.300 2.300 2.800 2.300 1 0 1.500-.4 2.200-.4s1.200.4 2.200.4c1.500 0 2.800-.7 2.800-2.300 0-2-2-4.700-5-4.700z"/>',
}
def ic(name, size=22):
    return svg(L[name], size, 2)

def opt(icon, label, right='', on=False):
    r = f'<em>{right}</em>' if right else ''
    return f'<div class="a-opt{" on" if on else ""}">{icon}<b>{label}</b>{r}</div>'

def steps(n, total):
    return '<div class="a-steps">' + ''.join(f'<i{" class=on" if i < n else ""}></i>' for i in range(total)) + '</div>'

# Data-viz pieces, in the style of premium widget apps: gradient rings, a gradient slider with a
# scale, segmented battery bars, dot matrices, a tinted card. Their CSS is the .g-* block in
# assets/features-pin.css (shared with the hero widgets).
BLUE, VIOLET, AMBER, CORAL, PINK, GREEN = '#5b8def', '#6a55dc', '#f2a93b', '#ee5a2a', '#ec5b8e', '#2fb36d'
L['bolt'] = '<path d="M13 2.5 4.500 13.500h6.500L10 21.500l8.500-11H12z"/>'
L['face'] = '<circle cx="12" cy="12" r="9"/><path d="M8.500 14.500c1 1.300 2.100 2 3.500 2s2.500-.7 3.500-2M9 9.500v.5M15 9.500v.5"/>'
L['note'] = '<path d="M6 3.500h9l3.500 3.500v13.500H6z"/><path d="M9 11h6M9 15h4"/>'

def lab(icon, text, color='#6b7494', cls=''):
    return f'<div class="g-lab {cls}"><span style="color:{color}">{ic(icon, 18)}</span>{text}</div>'

def num(value, unit='', cls=''):
    u = f'<small>{unit}</small>' if unit else ''
    return f'<div class="g-num {cls}">{value}{u}</div>'

def ring(p, text, s=112, c1=AMBER, c2=CORAL, t=15):
    return f'<span class="g-ring" style="--p:{p};--s:{s}px;--t:{t}px;--c1:{c1};--c2:{c2}"><b>{text}</b></span>'

def bat(n, total, cls=''):
    return f'<div class="g-bat {cls}">' + ''.join(f'<i{" class=on" if i < n else ""}></i>' for i in range(total)) + '</div>'

def dots(cols, rows=5, w=4):
    """cols: [(filled dots, colour, label)]; dots fill from the bottom, one column per item."""
    out = []
    for n, color, name in cols:
        cells = ''.join(f'<i{" class=on" if rows * w - 1 - idx < n else ""}></i>' for idx in range(rows * w))
        out.append(f'<div class="g-col" style="--cd:{color}"><div class="g-grid" style="--w:{w}">{cells}</div><small>{name}</small></div>')
    return '<div class="g-dots">' + ''.join(out) + '</div>'

def slider(x, labels):
    return (f'<div class="g-slider" style="--x:{x}%"><i></i></div>'
            '<div class="g-scale">' + ''.join(f'<span>{t}</span>' for t in labels) + '</div>')

def scene_reminders():
    return f"""<div class="w w-tint" style="{at(22, 44, 304, 2)}">
  {lab('bolt', 'Курс антибіотика', '#fff', 'on-tint')}
  {num('60', '%', 'on-tint')}
  <p class="g-sub on-tint">День 6 з 10 · Арчі</p>
  {bat(6, 10)}
  <div class="g-chips"><span class="g-chip up">Далі о 20:00</span><span class="g-chip down">ще 4 дні</span></div>
</div>
<div class="w" style="{at(344, 16, 206, 3)}">
  {lab('pill', 'Дози сьогодні', AMBER)}
  <div class="g-center">{ring(33, '1/3', 104)}</div>
  <div class="g-two"><span><small>Дано</small><b>1</b></span><span><small>Лишилось</small><b>2</b></span></div>
</div>
<div style="{at(34, 308, 330, 4)}">{notif('Час дати Мелоксикам 💊', 'Мартін · 0,05 мл')}</div>
<div class="w" style="{at(388, 252, 162, 3)}">
  {lab('drop', 'Очні краплі', BLUE)}
  {num('1', 'крапля')}
  <p class="g-sub">Арчі · 21:00</p>
</div>"""

def scene_state():
    return f"""<div class="w" style="{at(22, 22, 360, 2)}">
  <div class="a-top">{lab('chart', 'Вага · Мартін', BLUE)}<span class="g-chip up">+3 г</span></div>
  {num('338', 'г')}
  <p class="g-sub">за тиждень · норма 320–360</p>
  {slider(47, ['300', '320', '340', '360', '380'])}
</div>
<div class="w" style="{at(22, 232, 316, 3)}">
  {lab('face', 'Симптоми · Арчі', PINK)}
  {dots([(14, BLUE, 'Пн'), (11, BLUE, 'Вт'), (7, AMBER, 'Ср'), (3, PINK, 'Чт'), (8, AMBER, 'Пт'), (13, BLUE, 'Сб'), (15, BLUE, 'Нд')], 5, 3)}
</div>
<div class="w" style="{at(358, 222, 192, 4)}">
  {lab('note', 'Апетит', VIOLET)}
  <div class="g-center" style="margin:12px 0 8px">{ring(80, '80%', 96, '#7aa8ff', VIOLET, 14)}</div>
  <p class="g-sub" style="text-align:center;margin:0">чхав, але їсть добре</p>
</div>"""

def scene_vet():
    return f"""<div class="w" style="{at(22, 20, 262, 2)}">
  {lab('clip', 'Візит · 11:00', VIOLET)}
  <div class="g-dateRow"><div class="g-date"><small>Пн</small><b>9</b><small>листопада</small></div>{ring(67, '2/3', 96, AMBER, CORAL, 13)}</div>
  <div class="g-two rings"><span>{ring(100, '3/3', 78, '#7aa8ff', VIOLET, 11)}</span><span>{ring(0, '–', 78, AMBER, CORAL, 11)}</span></div>
</div>
<div class="w" style="{at(304, 38, 246, 3)}">
  {lab('tag', 'Огляд · Мартін', AMBER)}
  <div class="g-center">{ring(75, '75%', 112, AMBER, CORAL, 15)}</div>
  <div class="g-two"><span><small>Клініка</small><b>«Хвостик»</b></span><span><small>Записів</small><b>12</b></span></div>
</div>
<div class="w" style="{at(304, 292, 246, 4)}">
  {lab('clip', 'Історія Мартіна', '#6b7494')}
  <div class="g-hist"><span><b>Огляд</b><small>28 жовт</small></span><span><b>Аналіз крові</b><small>14 жовт</small></span></div>
</div>"""

def scene_notes():
    return f"""<div class="w" style="{at(20, 22, 336, 2)}">
  <div class="a-opt on" style="margin-top:0">{ic('search')}<b>алергія</b><em>3 збіги</em></div>
  <div class="g-tiles">
    <div class="on"><i>🐾</i>Усі</div>
    <div><img alt="" src="{MARTIN}">Мартін</div>
    <div><img alt="" src="{ARCHIE}">Арчі</div>
  </div>
  {opt(ic('tag', 20), 'Алергія на кедр', 'Арчі')}
</div>
<div class="w" style="{at(372, 36, 178, 3)}">
  {lab('note', 'Нотатки', VIOLET)}
  {num('24')}
  {dots([(14, BLUE, 'Ліки'), (9, AMBER, 'Вага'), (6, PINK, 'Стан')], 4, 3)}
</div>
<div class="w" style="{at(300, 240, 250, 3)}">
  <div class="w-pet"><img alt="" src="{ARCHIE}"><div><b>Арчі</b><span>Хом’як · 11 місяців</span></div></div>
  <div class="w-tags"><span class="warn">Алергія на кедр</span><span>Боїться пилососа</span><span>Гарбузове насіння</span></div>
</div>"""

SCENES = [scene_reminders, scene_state, scene_vet, scene_notes]

def background(i):
    """A soft pastel picture behind the widgets; it drifts slowly (see the CSS)."""
    return f'<div class="fp-glow" aria-hidden="true"><img alt="" src="assets/features/pastel-{i + 1}.jpg?v=blue1"></div>'

def pill(text):
    return (f'<span class="inline-flex items-center gap-[8px] rounded-full border border-[#e7e9ec] bg-white text-[#0f0f11] px-[14px] py-[6px] text-[13px] font-medium">'
            f'{svg(SPARK, 13, 2.2)}{text}</span>')

def section():
    items = ''.join(
        f'<li><a href="#feat-{i + 1}" data-fp-link class="fp-link{" is-active" if i == 0 else ""}"><span class="fp-num">0{i + 1}</span>'
        f'<span><b>{title}</b><span class="fp-desc"><span>{text}</span></span></span></a></li>'
        for i, (tag, title, text) in enumerate(FEATURES))
    slides = ''.join(
        f'<article id="feat-{i + 1}" data-fp-slide class="fp-slide{" is-active" if i == 0 else ""}">'
        f'<div class="fp-m-text"><span class="fp-m-icon">{svg(ICONS[i], 19)}</span><h3>{title}</h3><p>{text}</p></div>'
        f'<div class="fp-card">{background(i)}<div class="fp-scene-wrap"><div class="fp-scene" aria-hidden="true">{SCENES[i]()}</div></div></div></article>'
        for i, (tag, title, text) in enumerate(FEATURES))
    return f'''<section id="features" data-fp class="fp">
  <div class="fp-pin">
    <div>
      <div data-reveal>{pill('Можливості')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Що вміє Roddi Health</h2>
      <p data-reveal data-d="160" class="mt-[14px] max-w-[520px] text-[16px] leading-[1.45] text-[#6e727a]">Чотири речі, які забирають найбільше нервів, зібрані в одному місці.</p>
      <ol class="fp-list">{items}</ol>
    </div>
    <div class="fp-stage">{slides}</div>
  </div>
</section>'''

EN = json.loads((ROOT / 'tools' / 'features-en.json').read_text(encoding='utf-8'))
BUST = str(int(time.time()))  # new query on every build, so browsers fetch fresh CSS/JS

def english(html):
    """The section in English: every text node from tools/features-en.json, assets one folder up."""
    def node(m):
        t = m.group(1).strip()
        if not t or not re.search('[А-Яа-яІіЇїЄєҐґ]', t):
            return m.group(0)
        if t not in EN:
            raise SystemExit(f'No English for: {t!r} (add it to tools/features-en.json)')
        return m.group(0).replace(t, EN[t])
    html = re.sub(r'>([^<>]+)<', node, html)
    return html.replace('src="assets/', 'src="../assets/')

def put_section(page, html, prefix=''):
    """Swap the features block, its stylesheet and its script in a page."""
    page, n = re.subn(r'<section id="features".*?</section>', lambda m: html, page, count=1, flags=re.S)
    assert n == 1
    css = f'<link rel="stylesheet" href="{prefix}assets/features-pin.css?v={BUST}">'
    if 'features-pin.css' in page:
        page = re.sub(r'<link rel="stylesheet" href="[^"]*features-pin\.css[^"]*">', css, page)
    else:
        page = page.replace('</head>', f'  {css}\n</head>', 1)
    page = re.sub(r'<script src="[^"]*features-(?:list|pin)\.js[^"]*" defer></script>',
                  f'<script src="{prefix}assets/features-pin.js?v={BUST}" defer></script>', page)
    return page

if __name__ == '__main__':
    for path, html, prefix in [('index.html', section(), ''), ('en/index.html', english(section()), '../')]:
        f = ROOT / path
        f.write_text(put_section(f.read_text(encoding='utf-8'), html, prefix), encoding='utf-8')
        print(path, 'updated')
