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

# ---- scenes: 560×440 compositions built from the same components as the hero phone screen ----
# (.ip-card, .ip-sec, .ip-next / .ip-nc / .ip-ni, .ip-task / .ip-tc, .ip-pa, .ip-stack: assets/app-home.css;
#  the few .fx-* extras: assets/features-pin.css)
H = 'assets/home/'

def sec(title, count):
    return f'<div class="ip-sec"><span><img alt="" src="{H}sun.svg"><b>{title}</b></span><em>{count}</em></div>'

def pa(name):
    return f'<img alt="" class="ip-pa" src="{H}{name}">'

def stack(*names):
    return '<span class="ip-avs ip-stack">' + ''.join(pa(n) for n in names) + '</span>'

def trow(time, title, sub, right=''):
    return f'<div class="ip-task"><b class="ip-tm">{time}</b><div class="ip-tc"><div><b>{title}</b><span>{sub}</span></div>{right}</div></div>'

def nextb(time, label, badge, who, sub, btn):
    return (f'<div class="ip-next"><b class="ip-tm ip-tm1">{time}</b><div class="ip-nc"><div class="ip-nt"><b>{label}</b>'
            f'<span class="ip-badge"><img alt="" src="{H}timer.svg">{badge}</span></div>'
            f'<div class="ip-ni"><div class="ip-nw"><div><b>{who}</b><span>{sub}</span></div></div>'
            f'<div class="ip-start"><b>{btn}</b><span><img alt="" src="{H}chev-dark.svg"></span></div></div></div></div>')

def card(x, y, w, z, inner, cls=''):
    return f'<div class="ip-card fx {cls}" style="{at(x, y, w, z)}">{inner}</div>'

def li(text, on=False):
    mark = CHECK if on else ''
    return f'<div class="fx-li"><span class="fx-dot{" on" if on else ""}">{mark}</span>{text}</div>'

def scene_reminders():
    return (card(14, 14, 346, 2, sec('Важливе на сьогодні', '1 з 3') + nextb('11:00', 'Наступний крок:', 'через 15 хв', 'Мартін, Арчі', '3 препарати', 'Дати ліки'))
      + f'<div style="{at(190, 334, 340, 3)}">{notif("Час дати Мелоксикам 💊", "Мартін · 0,05 мл")}</div>'
      + card(372, 56, 178, 3, '<b class="fx-t">Курс антибіотика</b><span class="fx-s">день 6 з 10 · Арчі</span>'
             '<div class="w-seg-week"><i></i><i></i><i></i><i></i><i></i><i></i><i class="off"></i><i class="off"></i><i class="off"></i><i class="off"></i></div>'))

def scene_state():
    chart = f"""<div class="relative mt-[14px]">
    <svg viewBox="0 0 328 110" class="block h-[110px] w-full overflow-visible" aria-hidden="true">
      <defs><linearGradient id="fp-wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a5fba" stop-opacity=".22"/><stop offset="1" stop-color="#2a5fba" stop-opacity="0"/></linearGradient></defs>
      <g stroke="#eef0f6" stroke-width="1"><path d="M0 20H328M0 60H328M0 100H328"/></g>
      <path d="M0 78 C30 78 40 64 70 66 S110 88 140 80 S190 46 222 50 S280 30 328 24 L328 110 L0 110 Z" fill="url(#fp-wg)"/>
      <path d="M0 78 C30 78 40 64 70 66 S110 88 140 80 S190 46 222 50 S280 30 328 24" fill="none" stroke="#2a5fba" stroke-width="2.8" stroke-linecap="round"/>
      <circle cx="222" cy="50" r="9" fill="#2a5fba" fill-opacity=".16"/><circle cx="222" cy="50" r="4.5" fill="#fff" stroke="#2a5fba" stroke-width="2.6"/>
    </svg>
    <span class="w-tip" style="left:67.7%;top:38%">Пт · 337 г</span>
  </div>"""
    faces = ''.join(f'<span><i class="{c}">{e}</i>{d}</span>' for e, c, d in [('😊', 'ok', 'Пн'), ('😊', 'ok', 'Вт'), ('😐', '', 'Ср'), ('🤧', 'bad', 'Чт'), ('😐', '', 'Пт'), ('😊', 'ok', 'Сб'), ('', 'empty', 'Нд')])
    return (card(20, 20, 352, 2, f'<div class="fx-top"><span class="fx-h"><img alt="" src="{H}sun.svg">Вага · Мартін</span><span class="fx-chip">+3 г за тиждень</span></div>'
                 '<div class="w-big mt-[10px]">338 <small>г</small></div><div class="w-seg"><span class="on">Тиждень</span><span>Місяць</span><span>Рік</span></div>' + chart)
      + card(228, 262, 320, 3, '<div class="fx-top"><span class="fx-h">Симптоми · Арчі</span><em>цей тиждень</em></div>' + f'<div class="fx-faces">{faces}</div>')
      + f'<div class="w w-glass" style="{at(396, 116, 154, 4)};padding:12px 14px"><span class="text-[11px] font-semibold text-[#8a90a8]">Нотатка · Чт</span><b class="mt-[3px] block text-[13px] leading-[1.3]">Чхав зранку, апетит нормальний 🤧</b></div>')

def scene_vet():
    return (card(16, 12, 336, 2, sec('Візит · завтра', '11:00')
                 + trow('11:00', 'Огляд у ветеринара', 'Мартін · клініка «Хвостик»', pa('pet-martin.png'))
                 + '<p class="fx-cap">Взяти на прийом</p><div class="fx-list">'
                 + li('Історія ліків за місяць', True) + li('Графік ваги', True) + li('Спитати про курс') + '</div>')
      + card(298, 262, 254, 3, '<div class="fx-top"><span class="fx-h">Історія Мартіна</span><span class="fx-chip">12 записів</span></div>'
             '<div class="w-tl"><div style="--c:#2a5fba"><small>28 жовтня</small><b>Огляд · легка інфекція</b><span>Антибіотик на 10 днів</span></div>'
             '</div>'))

def scene_notes():
    return (card(16, 22, 344, 2, f'<div class="w-search">{svg("<circle cx=\'11\' cy=\'11\' r=\'7\'/><path d=\'M20 20l-3.5-3.5\'/>", 16, 2.4)}<b>алергія</b><span class="ml-auto text-[11px]">3 збіги</span></div>'
                 + trow2('Алергія на кедр', 'Особливість · Арчі', pa('pet-andriyko.png'))
                 + trow2('Лише паперовий наповнювач', 'Нотатка · Мартін · 3 лист', pa('pet-martin.png')))
      + card(300, 232, 250, 3, f'<div class="w-pet"><img alt="" src="{ARCHIE}"><div><b>Арчі</b><span>Хом’як · 11 місяців</span></div></div>'
             '<div class="w-tags"><span class="warn">Алергія на кедр</span><span>Боїться пилососа</span></div>')
      + f'<div class="w w-glass" style="{at(386, 100, 154, 4)};padding:12px 14px"><span class="text-[11px] font-semibold text-[#8a90a8]">Профілі</span>'
        f'<div class="mt-[6px] flex -space-x-[8px]"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{MARTIN}"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{ARCHIE}"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{SKY}"></div><b class="mt-[6px] block text-[13px]">3 улюбленці</b></div>')

def trow2(title, sub, right):
    return f'<div class="ip-tc fx-res"><div><b>{title}</b><span>{sub}</span></div>{right}</div>'

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
