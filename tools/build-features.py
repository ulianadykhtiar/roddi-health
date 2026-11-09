"""Build the "Що вміє Roddi Health" block on both homepages.

    python3 tools/build-features.py

Writes <section id="features"> into index.html and, in English, into en/index.html
(text from tools/features-en.json), with the stylesheet and script it needs.
Desktop: the section is pinned and its cards stack as you scroll; phones: the
features simply follow each other. Card backgrounds are assets/features/soft-1..4.jpg
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

# ---- scenes: 560×440 compositions of widgets ----
def scene_reminders():
    return f'''<div class="w" style="{at(118, 86, 330, 2)}">
  <div class="w-top"><span class="w-chip">Наступний крок · через 15 хв</span>{duo(MARTIN, ARCHIE)}</div>
  <span class="w-title">Ранковий раунд</span><span class="w-sub">3 препарати · Мартін і Арчі</span>
  <div class="w-prog"><span class="bar" style="--p:34%"><i></i></span><span>1/3</span></div>
  <div class="w-row"><span class="w-mark done">{CHECK}</span><span class="w-tile"><img alt="" src="{A}steam.svg"></span><span class="w-t"><b>Інгаляція</b><small>Фізрозчин, 15 хвилин</small></span></div>
  <div class="w-row"><span class="w-mark"></span><span class="w-tile"><img alt="" src="{A}pill-pink.svg"></span><span class="w-t"><b>Мелоксикам</b><small>0,05 мл · Мартін</small></span></div>
  <div class="w-row"><span class="w-mark"></span><span class="w-tile"><img alt="" src="{A}drop.svg"></span><span class="w-t"><b>Очні краплі</b><small>по 1 краплі · Арчі</small></span></div>
  <span class="w-btn">{CHECK}Відмітити все як дано</span>
</div>
<div style="{at(24, 14, 300, 3)}">{notif('Час дати Мелоксикам 💊', 'Мартін · 0,05 мл')}</div>
<div class="w" style="{at(368, 300, 190, 3)}"><div class="w-top"><b class="text-[13px]">Курс антибіотика</b></div>
  <span class="w-sub">день 6 з 10 · Арчі</span>
  <div class="w-seg-week"><i></i><i></i><i></i><i></i><i></i><i></i><i class="off"></i><i class="off"></i><i class="off"></i><i class="off"></i></div>
</div>'''

def scene_state():
    return f'''<div class="w" style="{at(22, 34, 360, 2)}">
  <div class="w-top"><span class="text-[13px] font-semibold text-[#6e727a]">Вага · Мартін</span><span class="w-chip green">+3 г за тиждень</span></div>
  <div class="mt-[8px] w-big">338 <small>г</small></div>
  <div class="w-seg"><span class="on">Тиждень</span><span>Місяць</span><span>Рік</span></div>
  <div class="relative mt-[14px]">
    <svg viewBox="0 0 328 120" class="block h-[120px] w-full overflow-visible" aria-hidden="true">
      <defs><linearGradient id="fp-wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a45588" stop-opacity=".22"/><stop offset="1" stop-color="#a45588" stop-opacity="0"/></linearGradient></defs>
      <g stroke="#eef0f3" stroke-width="1"><path d="M0 20H328M0 60H328M0 100H328"/></g>
      <path d="M0 78 C30 78 40 64 70 66 S110 88 140 80 S190 46 222 50 S280 30 328 24 L328 120 L0 120 Z" fill="url(#fp-wg)"/>
      <path d="M0 78 C30 78 40 64 70 66 S110 88 140 80 S190 46 222 50 S280 30 328 24" fill="none" stroke="#a45588" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M222 50V120" stroke="#a45588" stroke-opacity=".25" stroke-dasharray="3 4"/><circle cx="222" cy="50" r="9" fill="#a45588" fill-opacity=".16"/><circle cx="222" cy="50" r="4.5" fill="#fff" stroke="#a45588" stroke-width="2.6"/>
    </svg>
    <span class="w-tip" style="left:67.7%;top:41.7%">Пт · 337 г</span>
  </div>
  <div class="mt-[6px] flex justify-between text-[10.5px] font-semibold text-[#a2a6ad]"><span>Пн</span><span>Вт</span><span>Ср</span><span>Чт</span><span>Пт</span><span>Сб</span><span>Нд</span></div>
</div>
<div class="w" style="{at(232, 258, 316, 3)}">
  <div class="w-top"><b class="text-[14px]">Симптоми · Арчі</b><span class="text-[11.5px] font-medium text-[#a2a6ad]">цей тиждень</span></div>
  <div class="w-faces"><span><i class="ok">😊</i>Пн</span><span><i class="ok">😊</i>Вт</span><span><i>😐</i>Ср</span><span><i class="bad">🤧</i>Чт</span><span><i>😐</i>Пт</span><span><i class="ok">😊</i>Сб</span><span><i class="empty"></i>Нд</span></div>
</div>
<div class="w w-glass" style="{at(392, 120, 160, 4)};padding:12px 14px"><span class="text-[11px] font-semibold text-[#a2a6ad]">Нотатка · Чт</span><b class="mt-[3px] block text-[13px] leading-[1.3]">Чхав зранку, апетит нормальний 🤧</b></div>'''

def scene_vet():
    return f'''<div class="w" style="{at(20, 12, 300, 2)}">
  <div class="flex gap-[12px]"><span class="w-date"><small>Пн</small><b>9</b><small>лист</small></span>
    <div class="min-w-0"><span class="w-chip grey">Завтра · 11:00</span><b class="mt-[7px] block text-[16px]">Огляд у ветеринара</b><span class="w-sub">Мартін · клініка «Хвостик»</span></div></div>
  <div class="mt-[14px] border-t border-[#eef0f3] pt-[4px]">
    <p class="mt-[8px] text-[11px] font-bold uppercase tracking-[0.05em] text-[#a2a6ad]">Взяти на прийом</p>
    <div class="w-check"><span class="w-mark done">{CHECK}</span>Історія ліків за місяць</div>
    <div class="w-check"><span class="w-mark done">{CHECK}</span>Графік ваги</div>
    <div class="w-check"><span class="w-mark"></span>Спитати: продовжувати курс?</div>
  </div>
</div>
<div class="w" style="{at(272, 132, 280, 3)}">
  <div class="w-top"><div class="w-pet !gap-[10px]"><img alt="" class="!size-[34px] !shadow-none" src="{MARTIN}"><b class="!text-[15px]">Історія Мартіна</b></div><span class="w-chip">12 записів</span></div>
  <div class="w-tl">
    <div style="--c:#a45588"><small>28 жовтня</small><b>Огляд · легка інфекція</b><span>Антибіотик на 10 днів</span></div>
    <div style="--c:#3fcb7e"><small>14 жовтня</small><b>Аналіз крові</b><span class="w-file"><i>PDF</i>analiz-14-10.pdf</span></div>
    <div><small>30 вересня</small><b>Підпиляли зуби</b><span>Наступний огляд за 3 міс</span></div>
  </div>
</div>'''

def scene_notes():
    return f'''<div class="w" style="{at(20, 30, 340, 2)}">
  <div class="w-search">{svg('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>', 16, 2.4)}<b>алергія</b><span class="ml-auto text-[11px]">3 збіги</span></div>
  <div class="w-filters"><span>Усі</span><span><img alt="" src="{MARTIN}">Мартін</span><span><img alt="" src="{ARCHIE}">Арчі</span></div>
  <div class="w-res"><img alt="" src="{ARCHIE}"><div><small>Особливість · Арчі</small><p><mark>Алергія</mark> на кедрову стружку</p></div></div>
  <div class="w-res"><img alt="" src="{MARTIN}"><div><small>Нотатка · Мартін · 3 лист</small><p>Після <mark>алергії</mark> — лише паперовий наповнювач</p></div></div>
</div>
<div class="w" style="{at(300, 196, 250, 3)}">
  <div class="w-pet"><img alt="" src="{ARCHIE}"><div><b>Арчі</b><span>Хом’як · 11 місяців</span></div></div>
  <div class="w-tags"><span class="warn">Алергія на кедр</span><span>Боїться пилососа</span><span>Ласощі: гарбузове насіння</span><span>Вага 41 г</span></div>
</div>
<div class="w w-glass" style="{at(386, 70, 150, 4)};padding:12px 14px"><span class="text-[11px] font-semibold text-[#a2a6ad]">Профілі</span><div class="mt-[6px] flex -space-x-[8px]"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{MARTIN}"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{ARCHIE}"><img alt="" class="size-[30px] rounded-full ring-2 ring-white" src="{SKY}"></div><b class="mt-[6px] block text-[13px]">3 улюбленці</b></div>'''

SCENES = [scene_reminders, scene_state, scene_vet, scene_notes]

def background(i):
    """A soft pastel picture behind the widgets; it drifts slowly (see the CSS)."""
    return f'<div class="fp-glow" aria-hidden="true"><img alt="" src="assets/features/soft-{i + 1}.jpg"></div>'

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
