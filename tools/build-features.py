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

# ---- scenes: 560×440 compositions. Flat colour-block cards that overlap in layers, huge heavy
# numbers that count up, bars that fill, a chart that draws itself (see features-pin.css/.js).
def cnt(v, frm=None, wob=False):
    """A number that counts up from `frm` when its card becomes active (the text is the final value)."""
    a = f' data-from="{frm}"' if frm is not None else ''
    w = ' data-wob' if wob else ''
    return f'<span data-cnt="{v}"{a}{w}>{v}</span>'

def pills(*items):
    return '<div class="k-pills">' + ''.join(f'<span>{t}</span>' for t in items) + '</div>'

def scene_reminders():
    return f"""<div class="k k-white" style="{at(16, 8, 230, 2)};--i:0">
  <p class="k-l">Дози виконано сьогодні</p>
  <div class="k-bar" style="--p:67%"><i></i><b>{cnt(67, 20, True)}%</b></div>
</div>
<div class="k k-peach" style="{at(62, 98, 446, 1)};--i:1;height:216px;padding-top:36px">
  <p class="k-l">Мартін · Арчі</p>
  <h4 class="k-h">Ранковий<br>раунд</h4>
  {pills('3 препарати', '15 хв', 'далі 20:00')}
  <img class="k-cut" alt="" src="assets/hero-rat.png" style="width:196px;right:6px;bottom:-4px">
</div>
<div class="k k-glass" style="{at(16, 338, 292, 3)};--i:2">
  <span class="k-logo"><img alt="" src="assets/logo-white.svg"></span>
  <div><b>Час дати Мелоксикам 💊</b><small>Мартін · 0,05 мл · зараз</small></div>
</div>
<div class="k k-soft" style="{at(344, 252, 200, 3)};--i:3">
  <p class="k-l">Наступна доза</p>
  <div class="k-huge">20:<span>00</span></div>
  <div class="k-input"><span>Мелоксикам</span><i>{CHECK}</i></div>
</div>"""

def scene_state():
    return f"""<div class="k-pan"><div class="k-dash">
<div class="k k-green" style="left:-10px;top:84px;width:70px;height:236px;--i:0"><p class="k-l">Норма</p></div>
<div class="k k-red" style="left:70px;top:48px;width:132px;height:132px;--i:1"><p class="k-l">Вага · Мартін</p><div class="k-num">{cnt(338, 300, True)}<small>г</small></div></div>
<div class="k k-coral" style="left:70px;top:190px;width:132px;height:132px;--i:2"><p class="k-l">за тиждень</p><div class="k-num">+{cnt(3, 0)}<small>г</small></div></div>
<div class="k k-lilac" style="left:212px;top:48px;width:122px;height:64px;--i:3"><p class="k-l">Добре</p><div class="k-num sm">{cnt(5, 0)}<small>дн</small></div></div>
<div class="k k-violet" style="left:212px;top:118px;width:122px;height:64px;--i:4"><p class="k-l">Так собі</p><div class="k-num sm">{cnt(1, 0)}<small>дн</small></div></div>
<div class="k k-purple" style="left:212px;top:188px;width:122px;height:64px;--i:5"><p class="k-l">Погано</p><div class="k-num sm">{cnt(1, 0)}<small>дн</small></div></div>
<div class="k k-chart" style="left:344px;top:48px;width:236px;height:274px;--i:6"><p class="k-l">Вага за тиждень</p>
  <svg viewBox="0 0 220 210" class="k-svg" aria-hidden="true">
    <path class="area" d="M0 150 L30 168 L60 120 L90 140 L120 84 L150 104 L180 56 L220 28 V210 H0Z"/>
    <path class="line" pathLength="1" d="M0 150 L30 168 L60 120 L90 140 L120 84 L150 104 L180 56 L220 28"/>
    <g class="dots"><circle cx="30" cy="168" r="5"/><circle cx="60" cy="120" r="5"/><circle cx="90" cy="140" r="5"/><circle cx="120" cy="84" r="5"/><circle cx="150" cy="104" r="5"/><circle cx="180" cy="56" r="5"/></g>
  </svg>
  <div class="k-ax"><span>Пн</span><span>Ср</span><span>Пт</span><span>Нд</span></div></div>
<div class="k k-yellow" style="left:590px;top:48px;width:112px;height:274px;--i:7"><p class="k-l">Апетит</p><div class="k-num">{cnt(78, 40, True)}<small>%</small></div></div>
</div></div>"""

def scene_vet():
    return f"""<div class="k k-peach" style="{at(18, 56, 340, 1)};--i:0;height:236px">
  <p class="k-l">Візит · завтра</p>
  <h4 class="k-h sm">Огляд у<br>ветеринара</h4>
  {pills('11:00', '«Хвостик»')}
  <img class="k-cut" alt="" src="assets/hero-hamster.png" style="width:190px;right:-8px;bottom:-6px">
</div>
<div class="k k-white k-prof" style="{at(372, 18, 172, 3)};--i:1">
  <p class="k-l">Профіль</p>
  <img class="k-ava" alt="" src="{MARTIN}"><b>Мартін</b>
  <div class="k-stats"><span><i>{cnt(12, 0)}</i>записів</span><span><i>{cnt(4, 0)}</i>ліки</span><span><i>{cnt(338, 300)}</i>грам</span></div>
</div>
<div class="k k-soft" style="{at(262, 244, 200, 4)};--i:2">
  <p class="k-l">Наступний візит</p>
  <div class="k-huge sm">9 лист<br>2026</div>
  <div class="k-input"><span>Спитати лікаря</span><i>{CHECK}</i></div>
</div>
<div class="k k-white k-mini" style="{at(18, 318, 220, 3)};--i:3">
  <p class="k-l">Вага · Мартін</p>
  <div class="k-num">{cnt(338, 310)}<small>г</small></div>
  <svg viewBox="0 0 120 40" class="k-spark" aria-hidden="true"><path class="line" pathLength="1" d="M0 32 L20 28 L40 34 L60 18 L80 22 L100 8 L120 4"/><circle cx="120" cy="4" r="4"/></svg>
</div>"""

def scene_notes():
    return f"""<div class="k k-white k-search" style="{at(20, 20, 372, 2)};--i:0">
  <p class="k-l">Пошук</p>
  <div class="k-q"><mark>алергія</mark><i class="k-caret"></i></div>
  <small>{cnt(3, 0)} збіги · усі улюбленці</small>
</div>
<div class="k k-purple" style="{at(76, 138, 290, 3)};--i:1">
  <p class="k-l">Особливість · Арчі</p>
  <h4 class="k-t">Алергія на кедрову стружку</h4>
</div>
<div class="k k-yellow" style="{at(150, 236, 232, 4)};--i:2">
  <p class="k-l">Нотатка · Мартін · 3 лист</p>
  <h4 class="k-t">Після алергії лише паперовий наповнювач</h4>
</div>
<div class="k k-white k-prof" style="{at(392, 96, 156, 5)};--i:3">
  <p class="k-l">Профіль</p>
  <img class="k-ava" alt="" src="{ARCHIE}"><b>Арчі</b><span class="k-sub">Хом’як · 11 міс</span>
  <div class="k-stats"><span><i>{cnt(41, 0)}</i>грам</span><span><i>{cnt(3, 0)}</i>тегів</span></div>
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
        f'<div class="fp-card tone-{i + 1}"><div class="fp-scene-wrap"><div class="fp-scene" aria-hidden="true">{SCENES[i]()}</div></div></div></article>'
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
