"""Build the redesigned homepage drafts (Ukrainian) from one template.

    python3 tools/build-app-home.py

Writes three pages that differ only in the "Що вміє Roddi Health?" block:
    home-app.html     A: bento cards, a widget in each
    home-app-v3.html  B: cards with pet photos between the widget cards
    home-app-v4.html  C: numbered list pinned on the left, widget cards scroll on the right

Look: cool neutrals, black as the accent and for buttons; the app's dusty mauve
appears only inside app screens. Styles: assets/app-home.css. The pages reuse
the live site's scripts (forms.js, menu.js, carousel.js) and are kept out of
search (noindex).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INK, MUTED, FAINT, LINE, SOFT = '#0f0f11', '#6e727a', '#a2a6ad', '#e7e9ec', '#f4f5f7'
MAUVE, GREEN, GREEN_SOFT = '#c48bb0', '#2fae74', '#e6f5ee'
SHADOW = 'shadow-[0_1px_2px_rgba(15,15,17,.04),0_14px_34px_-22px_rgba(15,15,17,.28)]'

PETS = {'martin': 'image165.png', 'archie': 'image163.png', 'sky': 'image158.png', 'lilo': 'image167.png',
        'degu': 'image162.png', 'chin': 'image164.png', 'bunny': 'image166.png'}

def img(name):
    return f'assets/{PETS.get(name, name)}'

# ---------------------------------------------------------------- icons
def svg(path, size=18, sw=2):
    return (f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{path}</svg>')
I_CHECK = '<path d="M5 12.5l4.5 4.5L19 7.5"/>'
I_ARROW = '<path d="M5 12h14M13 6l6 6-6 6"/>'
I_BELL = '<path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>'
I_SUN = '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>'
I_SEARCH = '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>'
I_X = '<path d="M6 6l12 12M18 6 6 18"/>'
I_SPARK = '<path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6 5.6 18.4"/>'
I_PILL = '<rect x="3" y="8.5" width="18" height="7" rx="3.5" transform="rotate(-35 12 12)"/><path d="m9.2 8 5.6 8"/>'
I_CHART = '<path d="M4 19V5M4 19h16"/><path d="m7 15 4-4 3 3 5-6"/>'
I_CAL = '<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M8 3v4M16 3v4M3.5 10h17"/>'
I_NOTE = '<path d="M6 3.5h9l3.5 3.5v13.5H6z"/><path d="M9 11h6M9 15h4"/>'
I_HEART = '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>'

def pill(text, *, dark=False):
    """Small section label, like '✳ Можливості'."""
    cls = 'border-white/20 text-white/80' if dark else f'border-[{LINE}] bg-white text-[{INK}]'
    return (f'<span class="inline-flex items-center gap-[8px] rounded-full border {cls} px-[14px] py-[6px] text-[13px] font-medium">'
            f'{svg(I_SPARK, 13, 2.2)}{text}</span>')

def btn(text, href='#early-access', *, light=False, cls=''):
    """Black pill button with a round arrow, as in the references."""
    if light:
        return (f'<a href="{href}" class="btn-app btn-app-light {cls}">{text}<span class="btn-app-dot bg-[{INK}] text-white">{svg(I_ARROW, 16, 2.2)}</span></a>')
    return (f'<a href="{href}" class="btn-app {cls}">{text}<span class="btn-app-dot bg-white text-[{INK}]">{svg(I_ARROW, 16, 2.2)}</span></a>')

def faces(*names, size=22):
    return (f'<span class="flex shrink-0 -space-x-[7px]">' +
            ''.join(f'<img alt="" class="size-[{size}px] rounded-full object-cover ring-2 ring-white" src="{img(n)}">' for n in names) + '</span>')

def signup(form, *, dark=False, consent=False):
    """Email form wired to assets/forms.js (data-signup)."""
    field = 'bg-white border border-[#e7e9ec]' if not dark else 'bg-white'
    consent_html = ''
    if consent:
        consent_html = (f'<label class="mt-[14px] flex cursor-pointer items-start gap-[10px] text-left text-[14px] {"text-white/75" if dark else f"text-[{MUTED}]"}">'
                        f'<input type="checkbox" required class="mt-[2px] size-[18px] shrink-0 accent-[{INK}]">'
                        f'<span>Погоджуюсь отримувати листи про запуск. <a href="#" class="underline underline-offset-2">Політика конфіденційності</a></span></label>')
    return f'''<form data-signup data-form="{form}" novalidate class="relative w-full max-w-[520px]">
      <div class="signup {field}">
        <input type="email" name="email" autocomplete="email" inputmode="email" required placeholder="Ваш email" aria-label="Ваш email">
        <button class="btn-app btn-app-sm shrink-0 {"btn-app-white" if dark else ""}">Хочу ранній доступ</button>
      </div>
      <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="absolute -left-[9999px] size-px opacity-0">
      <p class="form-msg {"form-msg-dark" if dark else ""} mt-[10px]" role="status" aria-live="polite" hidden></p>{consent_html}
    </form>'''

# ---------------------------------------------------------------- widgets
def tick(state, size=20):
    if state == 'done':
        return f'<span class="flex size-[{size}px] shrink-0 items-center justify-center rounded-full bg-[{GREEN}] text-white">{svg(I_CHECK, size - 8, 3.4)}</span>'
    border = INK if state == 'now' else '#d5d8dc'
    return f'<span class="size-[{size}px] shrink-0 rounded-full border-2 border-[{border}]"></span>'

def task_row(time, icon, title, sub, pets, state='todo', *, compact=False):
    done, now = state == 'done', state == 'now'
    box = f'bg-white ring-1 ring-[{INK}] {SHADOW}' if now else f'bg-[{SOFT}]'
    t = 'text-[12px]' if compact else 'text-[13px]'
    btn_html = (f'<span class="mt-[10px] flex h-[34px] items-center justify-center gap-[6px] rounded-full bg-[{INK}] text-[12px] font-semibold text-white">'
                f'{svg(I_CHECK, 14, 3)}Позначити прийом</span>') if now else ''
    return (f'<div class="flex gap-[8px]{" opacity-50" if done else ""}">'
            f'<div class="flex w-[36px] shrink-0 flex-col items-center gap-[6px] pt-[8px]"><span class="text-[11px] font-semibold {f"text-[{INK}]" if now else f"text-[{FAINT}]"}">{time}</span>{tick(state)}</div>'
            f'<div class="min-w-0 flex-1 rounded-[18px] {box} p-[10px]"><div class="flex items-center gap-[10px]">'
            f'<span class="flex size-[36px] shrink-0 items-center justify-center rounded-[12px] {"bg-white" if not now else f"bg-[{SOFT}]"} text-[17px]">{icon}</span>'
            f'<div class="min-w-0 flex-1"><p class="truncate {t} font-semibold text-[{INK}]{" line-through" if done else ""}">{title}</p>'
            f'<p class="truncate text-[11px] text-[{MUTED}]">{sub}</p></div>{faces(*pets)}</div>{btn_html}</div></div>')

def w_today(title='На сьогодні', compact=False):
    rows = ''.join([
        task_row('08:00', '💊', 'Антибіотик', 'Мартін · 0,2 мл', ['martin'], 'done', compact=compact),
        task_row('12:00', '💧', 'Ліки для Мартіна', '[доза] · через 15 хв', ['martin'], 'now', compact=compact),
        task_row('17:30', '🪮', 'Чистка шерсті', 'М’яка щітка', ['archie'], compact=compact),
        task_row('19:00', '🥒', 'Вечірні овочі', 'Огірок, болгарський перець', ['martin', 'archie'], compact=compact),
    ])
    return (f'<div class="rounded-[26px] bg-white p-[14px] {SHADOW}">'
            f'<div class="flex items-center justify-between px-[4px]"><p class="flex items-center gap-[6px] text-[15px] font-semibold text-[{INK}]">{svg(I_SUN, 16)}{title}</p>'
            f'<span class="rounded-full bg-[{SOFT}] px-[10px] py-[3px] text-[11px] font-semibold text-[{MUTED}]">1 з 4</span></div>'
            f'<div class="mt-[12px] flex flex-col gap-[8px]">{rows}</div></div>')

def w_notification(text='Завтра об 11:00 — ветеринар 🩺', when='зараз'):
    return (f'<div class="flex items-center gap-[12px] rounded-[22px] bg-white/85 p-[12px] pr-[16px] backdrop-blur-[14px] {SHADOW}">'
            f'<span class="flex size-[38px] shrink-0 items-center justify-center rounded-[12px] bg-[{SOFT}]"><img alt="" class="size-[24px]" src="assets/vector.svg"></span>'
            f'<div class="min-w-0 flex-1"><div class="flex items-center justify-between gap-[8px]"><p class="text-[11px] font-semibold uppercase tracking-[0.04em] text-[{MUTED}]">Roddi Health</p>'
            f'<p class="text-[11px] text-[{FAINT}]">{when}</p></div><p class="mt-[2px] text-[14px] font-semibold text-[{INK}]">{text}</p></div></div>')

def w_weight(name='Мартін', grams='338', delta='+3 г'):
    return f'''<div class="rounded-[26px] bg-white p-[16px] {SHADOW}">
  <div class="flex items-start justify-between">
    <div><p class="text-[12px] font-medium text-[{MUTED}]">Вага · {name}</p><p class="mt-[2px] text-[28px] font-semibold leading-none tracking-[-0.02em] text-[{INK}]">{grams} <span class="text-[14px] font-medium text-[{MUTED}]">г</span></p></div>
    <span class="rounded-full bg-[{GREEN_SOFT}] px-[9px] py-[3px] text-[12px] font-semibold text-[#1f8a59]">{delta}</span>
  </div>
  <svg viewBox="0 0 220 64" preserveAspectRatio="none" class="mt-[12px] h-[64px] w-full overflow-visible" aria-hidden="true">
    <defs><linearGradient id="wg-{name}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".10"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient></defs>
    <path d="M0 40 C25 40 30 30 55 32 S90 44 110 38 S140 20 165 22 S195 14 220 12 L220 64 L0 64 Z" fill="url(#wg-{name})"/>
    <path data-draw d="M0 40 C25 40 30 30 55 32 S90 44 110 38 S140 20 165 22 S195 14 220 12" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    <circle cx="220" cy="12" r="4" fill="{INK}"/><circle cx="220" cy="12" r="8" fill="{INK}" fill-opacity=".12"/>
  </svg>
  <div class="mt-[6px] flex justify-between text-[10px] font-medium text-[{FAINT}]"><span>1.11</span><span>4.11</span><span>8.11</span></div>
</div>'''

def w_symptoms():
    days = [('П', '🙂', 0), ('В', '🙂', 0), ('С', '🙂', 0), ('Ч', '🤧', 1), ('П', '🙂', 0), ('С', '🙂', 0), ('Н', '', 2)]
    cells = ''
    for d, e, k in days:
        if k == 2:
            face = '<span class="size-[30px] rounded-full border-2 border-dashed border-[#d5d8dc]"></span>'
        elif k == 1:
            face = f'<span class="flex size-[30px] items-center justify-center rounded-full bg-[#fbeff5] text-[15px] ring-2 ring-[{MAUVE}]">{e}</span>'
        else:
            face = f'<span class="flex size-[30px] items-center justify-center rounded-full bg-[{GREEN_SOFT}] text-[15px]">{e}</span>'
        cells += f'<span class="flex flex-col items-center gap-[6px]">{face}<b class="text-[10px] font-medium text-[{FAINT}]">{d}</b></span>'
    return (f'<div class="rounded-[26px] bg-white p-[16px] {SHADOW}">'
            f'<div class="flex items-center justify-between"><p class="text-[14px] font-semibold text-[{INK}]">Симптоми · Арчі</p><p class="text-[11px] text-[{FAINT}]">цей тиждень</p></div>'
            f'<div class="mt-[14px] flex justify-between">{cells}</div>'
            f'<p class="mt-[12px] rounded-[12px] bg-[{SOFT}] px-[10px] py-[8px] text-[11px] text-[{MUTED}]">Чт · <b class="font-semibold text-[{INK}]">чхав зранку, апетит нормальний</b></p></div>')

def w_calendar():
    cells = '<span></span>' * 6
    for d in range(1, 31):
        cls = f'text-[{INK}]'
        dot = ''
        if d == 9:
            cls = 'bg-[#0f0f11] font-semibold text-white'
        elif d == 20:
            dot = f'<i class="absolute bottom-[2px] left-1/2 size-[4px] -translate-x-1/2 rounded-full bg-[{MAUVE}]"></i>'
        elif d in (3, 14):
            dot = f'<i class="absolute bottom-[2px] left-1/2 size-[4px] -translate-x-1/2 rounded-full bg-[{GREEN}]"></i>'
        elif d == 8:
            cls = f'ring-[1.5px] ring-[{INK}] font-semibold text-[{INK}]'
        cells += f'<span class="relative mx-auto flex size-[28px] items-center justify-center rounded-full text-[11px] font-medium {cls}">{d}{dot}</span>'
    head = ''.join(f'<span>{d}</span>' for d in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'])
    return (f'<div class="rounded-[26px] bg-white p-[16px] {SHADOW}">'
            f'<div class="flex items-center justify-between"><p class="text-[14px] font-semibold text-[{INK}]">Листопад 2026</p>'
            f'<span class="flex gap-[4px] text-[{MUTED}]"><span class="flex size-[24px] items-center justify-center rounded-full bg-[{SOFT}]">{svg("<path d=\"M15 18l-6-6 6-6\"/>", 11, 3)}</span>'
            f'<span class="flex size-[24px] items-center justify-center rounded-full bg-[{SOFT}]">{svg("<path d=\"M9 18l6-6-6-6\"/>", 11, 3)}</span></span></div>'
            f'<div class="mt-[12px] grid grid-cols-7 text-center text-[9px] font-medium uppercase text-[{FAINT}]">{head}</div>'
            f'<div class="mt-[6px] grid grid-cols-7 gap-y-[3px]">{cells}</div>'
            f'<div class="mt-[12px] flex items-center gap-[10px] rounded-[14px] bg-[{SOFT}] px-[12px] py-[10px]"><span class="size-[8px] shrink-0 rounded-full bg-[{INK}]"></span>'
            f'<p class="text-[12px] text-[{MUTED}]">Ветеринар · <b class="font-semibold text-[{INK}]">Пн, 9 листопада, 11:00</b></p></div></div>')

def w_visit():
    items = [('Діагноз', 'Легка респіраторна інфекція'), ('Призначення', 'Антибіотик · 10 днів'), ('Аналізи', 'Загальний аналіз крові · PDF')]
    rows = ''.join(f'<div class="flex items-center justify-between gap-[12px] border-t border-[{LINE}] py-[10px] text-[12px]"><span class="text-[{MUTED}]">{k}</span><b class="text-right font-semibold text-[{INK}]">{v}</b></div>' for k, v in items)
    return (f'<div class="rounded-[26px] bg-white p-[16px] {SHADOW}">'
            f'<div class="flex items-center gap-[10px]"><img alt="" class="size-[40px] rounded-full object-cover" src="{img("martin")}">'
            f'<div><p class="text-[14px] font-semibold text-[{INK}]">Огляд · Мартін</p><p class="text-[11px] text-[{FAINT}]">28 жовтня · клініка «Хвостик»</p></div></div>'
            f'<div class="mt-[12px]">{rows}</div></div>')

def w_search():
    def res(tag, color, text):
        return (f'<div class="rounded-[16px] border border-[{LINE}] bg-white p-[10px]"><p class="text-[9px] font-semibold uppercase tracking-[0.06em]" style="color:{color}">{tag}</p>'
                f'<p class="mt-[3px] text-[12px] font-medium leading-snug text-[{INK}]">{text}</p></div>')
    mark = lambda w: f'<mark class="rounded-[4px] bg-[#f6e4ef] px-[2px] text-inherit">{w}</mark>'
    return (f'<div class="rounded-[26px] bg-white p-[14px] {SHADOW}">'
            f'<div class="flex h-[40px] items-center gap-[8px] rounded-full bg-[{SOFT}] px-[14px] text-[{MUTED}]">{svg(I_SEARCH, 15, 2.4)}'
            f'<span class="caret text-[13px] font-medium text-[{INK}]">алергія</span><span class="ml-auto text-[10px] font-medium text-[{FAINT}]">3 результати</span></div>'
            f'<div class="mt-[10px] flex gap-[6px] text-[11px] font-semibold"><span class="rounded-full bg-[{INK}] px-[11px] py-[5px] text-white">Усі</span>'
            f'<span class="flex items-center gap-[5px] rounded-full bg-[{SOFT}] py-[3px] pl-[3px] pr-[10px] text-[{INK}]"><img alt="" class="size-[18px] rounded-full object-cover" src="{img("martin")}">Мартін</span>'
            f'<span class="flex items-center gap-[5px] rounded-full bg-[{SOFT}] py-[3px] pl-[3px] pr-[10px] text-[{INK}]"><img alt="" class="size-[18px] rounded-full object-cover" src="{img("archie")}">Арчі</span></div>'
            f'<div class="mt-[10px] flex flex-col gap-[8px]">'
            + res('Особливість · Арчі', '#d0453f', f'{mark("Алергія")} на кедрову стружку')
            + res('Нотатка · Мартін · 03.11', MUTED, f'Після {mark("алергії")} — тільки паперовий наповнювач')
            + res('Візит · Арчі · 28.10', MUTED, f'Перевірка на {mark("алергію")}, рекомендації') +
            '</div></div>')

def w_profile(name='Мартін', meta='Щур · 1 рік 8 міс', pet='martin'):
    tags = ''.join(f'<span class="rounded-full bg-[{SOFT}] px-[10px] py-[4px] text-[11px] font-medium text-[{INK}]">{t}</span>' for t in ['Алергія на кедр', 'Антибіотик · день 6', 'Вага 338 г'])
    return (f'<div class="rounded-[26px] bg-white p-[14px] {SHADOW}"><div class="flex items-center gap-[12px]">'
            f'<img alt="" class="size-[52px] rounded-full object-cover ring-[3px] ring-[{MAUVE}] ring-offset-2" src="{img(pet)}">'
            f'<div><p class="text-[16px] font-semibold text-[{INK}]">{name}</p><p class="text-[12px] text-[{MUTED}]">{meta}</p></div></div>'
            f'<div class="mt-[12px] flex flex-wrap gap-[6px]">{tags}</div></div>')

# ---------------------------------------------------------------- app phone
def app_avatar(src, name, *, selected=False, badge=False):
    ring = f'ring-[2.5px] ring-white ring-offset-[3px] ring-offset-[{MAUVE}]' if selected else ''
    inner = (f'<img alt="" class="size-full rounded-full object-cover" src="{img(src)}">' if src else
             '<span class="flex size-full items-center justify-center rounded-full bg-white text-[19px]">🐾</span>')
    dot = (f'<i class="absolute -right-[2px] -top-[2px] flex size-[16px] items-center justify-center rounded-full bg-[#e5484d] text-[10px] font-bold not-italic text-white ring-2 ring-[{MAUVE}]">!</i>' if badge else '')
    return (f'<span class="flex w-[52px] shrink-0 flex-col items-center gap-[6px]"><span class="relative size-[44px] rounded-full {ring}">{inner}{dot}</span>'
            f'<b class="text-[11px] font-semibold text-white">{name}</b></span>')

def app_phone(cls=''):
    """The app's home screen in a phone frame (from the current app design)."""
    rows = ''.join([
        task_row('08:00', '💊', 'Антибіотик', 'Мартін · 0,2 мл', ['martin'], 'done'),
        task_row('12:00', '💧', 'Ліки для Мартіна', '[доза] · через 15 хв', ['martin'], 'now'),
        task_row('17:30', '🪮', 'Чистка шерсті', 'М’яка щітка', ['archie']),
        task_row('19:00', '🥒', 'Вечірні овочі', 'Огірок, перець', ['martin', 'archie']),
    ])
    return f'''<div class="phone {cls}" aria-hidden="true">
  <div class="phone-screen">
    <div class="absolute left-1/2 top-[10px] z-10 h-[30px] w-[96px] -translate-x-1/2 rounded-full bg-[{INK}]"></div>
    <div class="rounded-b-[30px] bg-[{MAUVE}] px-[16px] pb-[16px] pt-[14px] text-white">
      <p class="pl-[16px] text-[14px] font-semibold">9:41</p>
      <div class="mt-[26px] flex items-start justify-between gap-[10px]">
        <div><p class="text-[11px] font-medium text-white/85">Неділя, 8 листопада</p><p class="mt-[3px] text-[21px] font-bold leading-[1.12] tracking-[-0.02em]">Про кого сьогодні дбаємо? 🙌</p></div>
        <span class="relative flex size-[40px] shrink-0 items-center justify-center rounded-full bg-white text-[{INK}]">{svg(I_BELL, 17, 2.2)}<i class="absolute right-[3px] top-[3px] size-[9px] rounded-full bg-[#e5484d]"></i></span>
      </div>
      <div class="mt-[14px] flex gap-[4px] overflow-hidden">{app_avatar(None, 'Усі', badge=True)}{app_avatar('martin', 'Мартін', selected=True)}{app_avatar('archie', 'Арчі', badge=True)}{app_avatar('sky', 'Скай')}{app_avatar('lilo', 'Ліло')}</div>
    </div>
    <div class="mx-[10px] mt-[10px] rounded-[24px] bg-white px-[10px] pb-[10px] pt-[12px]">
      <p class="flex items-center gap-[6px] px-[4px] text-[14px] font-semibold text-[{INK}]">{svg(I_SUN, 15)}На сьогодні</p>
      <div class="mt-[10px] flex flex-col gap-[7px]">{rows}</div>
    </div>
  </div>
</div>'''

# ---------------------------------------------------------------- sections
def header():
    return f'''<dialog id="site-menu" class="site-menu" aria-label="Меню">
  <div class="site-menu-inner">
    <div class="flex items-center justify-between">
      <a href="/" class="flex items-center gap-[8px]" aria-label="Roddi Health — на головну"><img alt="" class="size-[34px]" src="assets/vector.svg"><span class="ff-montserrat text-[19px] font-semibold leading-[0.95]">roddi<br>health</span></a>
      <button type="button" data-menu-close class="menu-close" aria-label="Закрити меню">{svg(I_X, 18, 2.4)}</button>
    </div>
    <nav class="mt-[24px]">
      <a href="#features" class="site-menu-link" data-menu-close>Можливості</a>
      <a href="#for-whom" class="site-menu-link" data-menu-close>Для кого</a>
      <a href="#faq" class="site-menu-link" data-menu-close>Питання</a>
      <a href="blog.html" class="site-menu-link">Блог</a>
    </nav>
  </div>
</dialog>

<header class="site-header">
  <div class="mx-auto flex h-[72px] max-w-[1280px] items-center justify-between gap-[12px] px-5 md:px-8">
    <a href="#" class="flex items-center gap-[8px]" aria-label="Roddi Health"><img alt="" class="size-[34px]" src="assets/vector.svg"><span class="ff-montserrat hidden text-[19px] font-semibold leading-[0.95] sm:inline">roddi<br>health</span></a>
    <nav class="nav-pill hidden lg:flex" aria-label="Розділи">
      <a href="#features">Можливості</a><a href="#for-whom">Для кого</a><a href="#story">Історія</a><a href="#faq">Питання</a><a href="blog.html">Блог</a>
    </nav>
    <div class="flex items-center gap-[8px]">
      <div class="lang-switch" role="group" aria-label="Мова сайту"><span class="is-active" aria-current="true">UA</span><a href="/en/" hreflang="en" lang="en">EN</a></div>
      <a href="#early-access" class="btn-app btn-app-sm max-sm:hidden">Ранній доступ</a>
      <button type="button" data-menu-open class="menu-btn" aria-label="Меню" aria-haspopup="dialog" aria-controls="site-menu">{svg('<path d="M4 7h16M4 12h16M4 17h10"/>', 18, 2.4)}</button>
    </div>
  </div>
</header>'''

def hero():
    strip = f'''
      <div class="strip-card w-[210px] h-[250px] bg-[{INK}] text-white p-[20px] flex flex-col justify-between" data-reveal data-d="500">
        <span class="flex size-[38px] items-center justify-center rounded-full bg-white/10">{svg(I_BELL, 18)}</span>
        <p class="text-[20px] font-medium leading-[1.2] tracking-[-0.01em]">Ліки, вага й візити — без «а я точно дав?»</p>
      </div>
      <div class="strip-card w-[220px] h-[300px] overflow-hidden" data-reveal data-d="600">
        <img alt="Щур Мартін їсть ласощі" class="size-full object-cover" src="{img('martin')}">
        <span class="glass-chip absolute bottom-[14px] left-[14px]">Мартін · 338 г</span>
      </div>
      <div class="relative z-10 -mb-[40px] shrink-0" data-reveal="rise" data-d="300">{app_phone('w-[300px]')}</div>
      <div class="w-[270px] shrink-0 self-center" data-reveal data-d="700">{w_weight()}</div>
      <div class="strip-card w-[220px] h-[270px] overflow-hidden" data-reveal data-d="800">
        <img alt="Хом’як Арчі" class="size-full object-cover" src="{img('archie')}">
        <div class="absolute inset-x-[10px] bottom-[10px]">{w_notification('Ветеринар завтра 11:00', 'Арчі')}</div>
      </div>'''
    return f'''<section class="relative overflow-hidden pt-[40px] md:pt-[64px]">
  <svg class="pointer-events-none absolute left-0 top-[520px] h-[300px] w-full md:top-[470px]" viewBox="0 0 1440 300" preserveAspectRatio="none" fill="none" aria-hidden="true"><path d="M-20 220 C 240 60, 420 300, 720 150 S 1200 40, 1460 180" stroke="#d5d8dc" stroke-width="1.5" stroke-dasharray="5 7"/></svg>
  <div class="relative mx-auto max-w-[980px] px-5 text-center">
    <div data-reveal>{pill('Ранній доступ · безкоштовно під час бети')}</div>
    <h1 data-reveal data-d="80" class="t-display mt-[22px]">Усе про здоров’я <span class="word-chip"><img alt="" src="{img('martin')}"><img alt="" src="{img('archie')}"><img alt="" src="{img('sky')}"></span> вашого гризуна в&nbsp;одному додатку</h1>
    <p data-reveal data-d="160" class="mx-auto mt-[22px] max-w-[600px] text-[17px] leading-[1.45] text-[{MUTED}] md:text-[19px]">Нагадування про ліки, облік симптомів, ваги й візитів до ветеринара. Уся історія лікування завжди під рукою, навіть якщо у вас кілька улюбленців.</p>
    <div data-reveal data-d="240" class="mt-[30px] flex justify-center">{signup('hero')}</div>
    <div data-reveal data-d="320" class="mt-[18px] flex items-center justify-center gap-[10px] text-[14px] text-[{MUTED}]">
      {faces('sky', 'bunny', 'lilo', 'martin', size=30)}
      <p>Блог, з якого все почалося, читають <b class="font-semibold text-[{INK}]"><span data-count="6000">6&nbsp;000</span>+ людей</b></p>
    </div>
  </div>
  <div class="hero-strip mt-[56px] md:mt-[72px]">{strip}
  </div>
</section>'''

MEMES = [('image157.png', 'Я точно дав ліки? Чи то було вчора…', -4),
         ('image161.png', 'А коли був останній огляд у лікаря?', 3),
         ('image159.png', 'Де ж ця клята нотатка з призначеннями?', -2),
         ('image160.png', 'Знову прогавила антибіотик', 4)]

def memes():
    cards = ''.join(
        f'<figure data-reveal="toss" data-d="{150 + i * 90}" class="meme-card" style="--r:{r}deg">'
        f'<img alt="" class="aspect-[4/3] w-full rounded-[18px] object-cover" src="assets/{src}">'
        f'<figcaption class="px-[6px] pb-[4px] pt-[14px]"><span class="text-[12px] font-medium text-[{FAINT}]">[знайомо]</span>'
        f'<p class="mt-[6px] text-[18px] font-medium leading-[1.25] tracking-[-0.01em] text-[{INK}]">{cap}</p></figcaption></figure>'
        for i, (src, cap, r) in enumerate(MEMES))
    return f'''<section class="px-5 py-[96px] md:py-[130px]">
  <div class="mx-auto max-w-[1280px]">
    <div class="flex flex-col items-start justify-between gap-[20px] md:flex-row md:items-end">
      <div><div data-reveal>{pill('Впізнаєте себе?')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px] max-w-[640px]">Турбота про здоров’я гризуна часто живе в голові й нотатках</h2></div>
      <p data-reveal data-d="160" class="max-w-[380px] text-[16px] leading-[1.45] text-[{MUTED}]">Якщо хоч одна з цих думок вам знайома, Roddi Health зробить ваше життя спокійнішим.</p>
    </div>
    <div class="meme-row mt-[48px]">{cards}</div>
  </div>
</section>'''

FEATURES = [
    ('Нагадування', 'Не пропустіть жодної дози', 'Налаштуйте курс лікування один раз, і нагадування прийдуть вчасно. Позначайте прийом одним дотиком. Так само працюють нагадування про візити, зважування та чистку клітки.', I_PILL),
    ('Стан і вага', 'Стежте, як змінюється стан', 'Записуйте симптоми й вагу, а додаток покаже динаміку на графіку. Так легше помітити зміни вчасно.', I_CHART),
    ('Візити', 'Приходьте до ветеринара з готовою історією', 'Візити, призначення, поточне й минуле лікування, аналізи в одному профілі улюбленця. На прийомі не доведеться згадувати.', I_CAL),
    ('Нотатки', 'Усе під рукою', 'Нотатки, особливості здоров’я та швидкий пошук: знайдете потрібне за секунди, навіть якщо у вас кілька гризунів.', I_NOTE),
]

def features_head(center=False):
    align = 'items-center text-center' if center else 'items-start'
    return f'''<div class="flex flex-col {align}">
      <div data-reveal>{pill('Можливості')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Що вміє Roddi Health</h2>
      <p data-reveal data-d="160" class="mt-[14px] max-w-[520px] text-[16px] leading-[1.45] text-[{MUTED}]">Чотири речі, які забирають найбільше нервів, зібрані в одному місці.</p>
    </div>'''

def feat_text(i, *, dark=False):
    tag, title, text, icon = FEATURES[i]
    c1, c2 = ('text-white', 'text-white/70') if dark else (f'text-[{INK}]', f'text-[{MUTED}]')
    chip = 'bg-white/10 text-white' if dark else f'bg-white text-[{INK}]'
    return (f'<span class="flex size-[40px] items-center justify-center rounded-full {chip}">{svg(icon, 19)}</span>'
            f'<h3 class="mt-[18px] text-[22px] font-semibold leading-[1.2] tracking-[-0.02em] {c1}">{title}</h3>'
            f'<p class="mt-[8px] text-[15px] leading-[1.45] {c2}">{text}</p>')

def features_a():
    """A: 2×2 bento, text on top, the widget below in a white panel."""
    widgets = [
        f'<div class="grid gap-[10px]">{w_today()}</div>',
        f'<div class="grid gap-[10px] sm:grid-cols-2 md:grid-cols-1 xl:grid-cols-2">{w_weight()}{w_symptoms()}</div>',
        f'<div class="grid gap-[10px] sm:grid-cols-2 md:grid-cols-1 xl:grid-cols-2">{w_calendar()}{w_visit()}</div>',
        f'<div class="grid gap-[10px]">{w_search()}</div>',
    ]
    cards = ''.join(
        f'<article data-reveal data-d="{(i % 2) * 120}" class="feature-card {"bg-[#0f0f11]" if i == 0 else ""}">'
        f'<div class="max-w-[440px]">{feat_text(i, dark=i == 0)}</div><div class="mt-auto pt-[28px]">{widgets[i]}</div></article>'
        for i in range(4))
    return f'''<section id="features" class="px-5 py-[96px] md:py-[130px]">
  <div class="mx-auto max-w-[1280px]">{features_head(center=True)}
    <div class="mt-[48px] grid gap-[16px] md:grid-cols-2">{cards}</div>
  </div>
</section>'''

def photo_card(src, alt, big, small, extra=''):
    return (f'<article data-reveal class="photo-card"><img alt="{alt}" class="absolute inset-0 size-full object-cover" src="{img(src)}">'
            f'<div class="absolute inset-0 bg-gradient-to-t from-black/55 via-black/0 to-black/25"></div>'
            f'<div class="relative flex h-full flex-col justify-between p-[24px] text-white"><span class="flex size-[40px] items-center justify-center rounded-full bg-white/15 backdrop-blur-[8px]">{svg(I_HEART, 19)}</span>'
            f'<div>{extra}<p class="text-[40px] font-semibold leading-none tracking-[-0.03em]">{big}</p><p class="mt-[8px] max-w-[260px] text-[15px] leading-[1.4] text-white/85">{small}</p></div></div></article>')

def features_b():
    """B: three columns; real pet photos sit between the widget cards."""
    def card(i, widget, d=0):
        return (f'<article data-reveal data-d="{d}" class="feature-card">{feat_text(i)}'
                f'<div class="mt-auto pt-[24px]">{widget}</div></article>')
    species = ''.join(f'<span class="rounded-full bg-white/15 px-[10px] py-[4px] text-[12px] font-medium backdrop-blur-[8px]">{s}</span>'
                      for s in ['Щури', 'Хом’яки', 'Свинки', 'Шиншили', 'Дегу', 'Кролики', 'Миші'])
    return f'''<section id="features" class="px-5 py-[96px] md:py-[130px]">
  <div class="mx-auto max-w-[1280px]">{features_head(center=True)}
    <div class="mt-[48px] grid gap-[16px] md:grid-cols-2 lg:grid-cols-3">
      {card(0, w_today(compact=True))}
      {photo_card('martin', 'Щур Мартін на ковдрі', '6 000+', 'людей стежать за Мартіном і Арчі в блозі, з якого почався Roddi Health')}
      {card(1, '<div class="grid gap-[10px]">' + w_weight() + w_symptoms() + '</div>', 120)}
      {card(2, w_calendar())}
      {card(3, w_search(), 120)}
      {photo_card('chin', 'Шиншила', '7 видів', 'і кожен зі своїм профілем: від щурів до кроликів', f'<div class="mb-[16px] flex flex-wrap gap-[6px]">{species}</div>')}
    </div>
  </div>
</section>'''

def features_c():
    """C: numbered list pinned on the left; each feature's widgets scroll by on the right."""
    items = ''.join(
        f'<li><a href="#feat-{i + 1}" data-feat-link="{i}" class="feat-link{" is-active" if i == 0 else ""}">'
        f'<span class="feat-num">0{i + 1}</span><span><b class="block text-[18px] font-semibold tracking-[-0.01em]">{FEATURES[i][1]}</b>'
        f'<span class="feat-sub mt-[3px] block text-[13px]">{FEATURES[i][0]}</span></span></a></li>' for i in range(4))
    panels = [
        f'<div class="grid items-start gap-[12px] lg:grid-cols-[1fr_0.9fr]">{w_today()}<div class="grid gap-[12px]">{w_notification()}{w_notification("Час зважити Арчі ⚖️", "18:00")}{w_profile()}</div></div>',
        f'<div class="grid items-start gap-[12px] lg:grid-cols-2">{w_weight()}{w_symptoms()}<div class="lg:col-span-2">{w_weight("Арчі", "41", "−1 г")}</div></div>',
        f'<div class="grid items-start gap-[12px] lg:grid-cols-2">{w_calendar()}<div class="grid gap-[12px]">{w_visit()}{w_notification("Завтра об 11:00 — ветеринар 🩺", "вчора")}</div></div>',
        f'<div class="grid items-start gap-[12px] lg:grid-cols-[1fr_0.8fr]">{w_search()}<div class="grid gap-[12px]">{w_profile("Арчі", "Хом’як · 11 міс", "archie")}<div class="relative h-[220px] overflow-hidden rounded-[26px]"><img alt="Хом’як Арчі" class="size-full object-cover" src="{img("archie")}"></div></div></div>',
    ]
    cards = ''.join(
        f'<article id="feat-{i + 1}" data-feat="{i}" class="feat-panel">'
        f'<div class="mb-[24px] max-w-[520px] lg:hidden">{feat_text(i)}</div>'
        f'<p class="mb-[18px] hidden text-[13px] font-medium text-[{MUTED}] lg:block">0{i + 1} / {FEATURES[i][0]}</p>'
        f'<p class="mb-[24px] hidden max-w-[520px] text-[17px] leading-[1.45] text-[{INK}] lg:block">{FEATURES[i][2]}</p>{panels[i]}</article>'
        for i in range(4))
    return f'''<section id="features" class="px-5 py-[96px] md:py-[130px]">
  <div class="mx-auto grid max-w-[1280px] gap-[40px] lg:grid-cols-[minmax(0,420px)_minmax(0,1fr)] lg:gap-[56px]">
    <div class="lg:sticky lg:top-[96px] lg:self-start">{features_head()}
      <ol class="mt-[32px] hidden flex-col gap-[6px] rounded-[30px] bg-[{SOFT}] p-[8px] lg:flex">{items}</ol>
    </div>
    <div class="flex flex-col gap-[16px]">{cards}</div>
  </div>
</section>'''

def orbit_cta():
    """Early-access block: pet avatars orbit the call to action."""
    spots = [('martin', 0, 54), ('archie', 60, 54), ('sky', 128, 54), ('lilo', 200, 54), ('bunny', 262, 54), ('degu', 318, 54),
             ('chin', 30, 40), ('martin', 150, 40), ('archie', 250, 40)]
    pets = ''
    for name, angle, r in spots:
        pets += (f'<span class="orbit-pet" style="--a:{angle}deg;--k:{r / 100}"><img alt="" src="{img(name)}"></span>')
    return f'''<section class="px-5 pb-[96px] md:pb-[130px]">
  <div class="orbit-wrap mx-auto max-w-[1280px]">
    <div class="orbit" aria-hidden="true"><span class="orbit-ring" style="--s:80%"></span><span class="orbit-ring" style="--s:108%"></span>{pets}</div>
    <div class="relative z-10 mx-auto flex max-w-[560px] flex-col items-center px-5 text-center">
      <div data-reveal>{pill('Ранній доступ')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Станьте одним із перших, хто спробує</h2>
      <p data-reveal data-d="160" class="mt-[14px] text-[16px] leading-[1.45] text-[{MUTED}]">Запишіться на ранній доступ: спробуєте додаток до публічного запуску й вплинете на його функції.</p>
      <div data-reveal data-d="240" class="mt-[26px] flex w-full justify-center">{signup('cta')}</div>
      <p data-reveal data-d="300" class="mt-[12px] text-[13px] text-[{FAINT}]">Безкоштовно під час бети. Лише новини про запуск, без спаму.</p>
    </div>
  </div>
</section>'''

def for_whom():
    pets = [('degu', 'Дегу на підвіконні'), ('sky', 'Морська свинка на лежанці'), ('archie', 'Хом’як поруч із пальцем людини'),
            ('chin', 'Сіра шиншила'), ('martin', 'Щур їсть ласощі на ковдрі'), ('bunny', 'Кролик із висячими вухами'), ('lilo', 'Домашня миша')]
    cards = ''.join(f'<div class="pet-card"><img alt="{a}" decoding="async" src="{img(n)}"></div>' for n, a in pets)
    chips = ''.join(f'<span class="rounded-full border border-[{LINE}] bg-white px-[16px] py-[8px] text-[15px] font-medium">{s}</span>'
                    for s in ['🐀 Щури', '🐹 Хом’яки', '🐹 Морські свинки', '🐇 Кролики', '🐭 Шиншили', '🐿️ Дегу', '🐁 Миші'])
    return f'''<section id="for-whom" class="overflow-hidden bg-[{SOFT}] py-[96px] md:py-[130px]">
  <div class="mx-auto flex max-w-[860px] flex-col items-center px-5 text-center">
    <div data-reveal>{pill('Для кого')}</div>
    <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Для всіх маленьких улюбленців</h2>
    <p data-reveal data-d="160" class="mt-[14px] max-w-[620px] text-[16px] leading-[1.45] text-[{MUTED}]">Для власників щурів, хом’яків, морських свинок, кроликів, шиншил, дегу, мишей та інших маленьких улюбленців, яким потрібен уважний догляд за здоров’ям.</p>
    <div data-reveal data-d="220" class="mt-[24px] flex flex-wrap justify-center gap-[8px]">{chips}</div>
  </div>
  <div data-pet-carousel class="pet-carousel mt-[40px] md:mt-[56px]" aria-hidden="true">{cards}</div>
</section>'''

def story():
    return f'''<section id="story" class="px-5 py-[96px] md:py-[130px]">
  <div class="mx-auto grid max-w-[1280px] items-center gap-[40px] lg:grid-cols-2 lg:gap-[72px]">
    <div data-reveal="zoom" class="relative">
      <div class="relative aspect-[4/5] overflow-hidden rounded-[36px] bg-[{SOFT}]">
        <img alt="Щур Мартін" class="size-full object-cover" src="{img('martin')}">
        <div class="absolute inset-x-[16px] bottom-[16px] flex items-center gap-[12px] rounded-[22px] bg-white/85 p-[12px] backdrop-blur-[14px]">
          {faces('martin', 'archie', size=40)}
          <div class="min-w-0 flex-1"><p class="text-[14px] font-semibold text-[{INK}]">@marchin_rats</p><p class="text-[12px] text-[{MUTED}]">Мартін і Арчі · 6 000+ підписників</p></div>
          <a href="https://www.instagram.com/marchin_rats/" target="_blank" rel="noopener" class="btn-app btn-app-sm">Instagram</a>
        </div>
      </div>
      <div class="absolute -right-[12px] -top-[18px] hidden w-[250px] rotate-[4deg] md:block lg:-right-[28px]">{w_notification('Мартіну час на ліки 💊', '08:00')}</div>
    </div>
    <div>
      <div data-reveal>{pill('Чому я створюю Roddi Health')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Усе почалося з любові до пацюків 🐭</h2>
      <div data-reveal data-d="160" class="mt-[22px] flex flex-col gap-[16px] text-[17px] leading-[1.5] text-[{MUTED}]">
        <p>Коли в моєму житті з’явилися двоє пацюків, я створила Instagram-блог, щоб ділитися їхніми пригодами. Разом із радістю прийшли й турботи про здоров’я: візити до ветеринара, ліки, симптоми, зміни ваги. Усе це я постійно записувала або тримала в голові.</p>
        <p class="text-[22px] font-medium leading-[1.35] tracking-[-0.01em] text-[{INK}]">«Тому я роблю додаток, який потрібен мені самій, разом з іншими власниками гризунів.»</p>
      </div>
      <div data-reveal data-d="240" class="mt-[30px] flex flex-wrap items-center gap-[10px]">
        {btn('Хочу ранній доступ')}
        <a href="https://www.tiktok.com/@marchin_rats" target="_blank" rel="noopener" class="btn-app btn-app-light">TikTok</a>
      </div>
    </div>
  </div>
</section>'''

COMPARE = [('«Я дала ліки зранку?» Будильники й стікери', 'Нагадування й позначка в один дотик'),
           ('Симптоми — у фото й повідомленнях', 'Щоденник симптомів з датами'),
           ('Вага — у нотатках, які не знайти', 'Графік ваги'),
           ('На прийомі згадую все з пам’яті', 'Уся історія готова'),
           ('Кілька гризунів — плутаю, кому які ліки', 'Окремий профіль для кожного')]

def before_after():
    before = ''.join(f'<li data-reveal data-d="{i * 70}" class="flex items-start gap-[12px] border-t border-[{LINE}] py-[16px]"><span class="mt-[1px] flex size-[22px] shrink-0 items-center justify-center rounded-full bg-white text-[{FAINT}]">{svg(I_X, 12, 3)}</span><span>{a}</span></li>' for i, (a, _) in enumerate(COMPARE))
    after = ''.join(f'<li data-reveal data-d="{150 + i * 70}" class="flex items-start gap-[12px] border-t border-white/12 py-[16px]"><span class="mt-[1px] flex size-[22px] shrink-0 items-center justify-center rounded-full bg-white text-[{INK}]">{svg(I_CHECK, 12, 3.4)}</span><span>{b}</span></li>' for i, (_, b) in enumerate(COMPARE))
    return f'''<section class="px-5 pb-[96px] md:pb-[130px]">
  <div class="mx-auto max-w-[1280px]">
    <div class="flex flex-col items-start justify-between gap-[20px] md:flex-row md:items-end">
      <div><div data-reveal>{pill('До і після')}</div><h2 data-reveal data-d="80" class="t-h2-app mt-[18px] max-w-[620px]">Від хаосу в нотатках до спокою</h2></div>
      <p data-reveal data-d="160" class="max-w-[420px] text-[16px] leading-[1.45] text-[{MUTED}]">Як змінюється турбота про здоров’я улюбленця, коли все важливе зібрано <b class="font-semibold text-[{INK}]">в одному місці</b>.</p>
    </div>
    <div class="mt-[44px] grid gap-[16px] md:grid-cols-2">
      <div data-reveal class="rounded-[32px] bg-[{SOFT}] p-[28px] md:p-[36px]"><p class="text-[14px] font-medium text-[{MUTED}]">Без додатка</p><ul class="mt-[18px] text-[17px] text-[{MUTED}]">{before}</ul></div>
      <div data-reveal data-d="120" class="rounded-[32px] bg-[{INK}] p-[28px] text-white md:p-[36px]"><p class="flex items-center gap-[8px] text-[14px] font-medium text-white/70"><img alt="" class="size-[20px]" src="assets/vector.svg">З Roddi Health</p><ul class="mt-[18px] text-[17px] font-medium">{after}</ul></div>
    </div>
  </div>
</section>'''

FAQ = [('Коли запуск?', 'Ми працюємо над першою версією. [Орієнтовний період.] Усім, хто залишить email, напишемо першими.'),
       ('Скільки це коштуватиме?', 'Під час бети Roddi Health безкоштовний. [Ціни після запуску.]'),
       ('Чи замінює додаток ветеринара?', 'Ні. Roddi Health допомагає вести історію здоров’я й не пропускати лікування, але не замінює консультацію ветеринара.'),
       ('Що з моїми даними?', '[Де зберігаються дані і як вони захищені.]'),
       ('Для яких тварин?', 'Для щурів, хом’яків, морських свинок, кроликів, шиншил, дегу, мишей та інших маленьких улюбленців. Не знайшли свого — напишіть нам.'),
       ('На яких пристроях?', '[Платформи на старті: iOS / Android / веб.]'),
       ('Якою мовою?', '[Мови інтерфейсу на старті.]'),
       ('Що ви робите з моєю поштою?', 'Надсилаємо лише новини про запуск і запрошення до раннього доступу. Без спаму, відписатися можна будь-коли.')]

def faq():
    items = ''.join(f'<details data-reveal data-d="{i * 50}"{" open" if i == 0 else ""}><summary><span>{q}</span><i class="faq-plus" aria-hidden="true"></i></summary><p>{a}</p></details>'
                    for i, (q, a) in enumerate(FAQ))
    return f'''<section id="faq" class="px-5 pb-[96px] md:pb-[130px]">
  <div class="faq mx-auto grid max-w-[1280px] gap-[32px] lg:grid-cols-[minmax(0,1fr)_minmax(0,720px)] lg:gap-[64px]">
    <div class="lg:sticky lg:top-[96px] lg:self-start">
      <div data-reveal>{pill('Питання')}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Поширені запитання</h2>
      <div data-reveal data-d="160" class="mt-[28px] rounded-[28px] bg-[{SOFT}] p-[24px]">
        <p class="text-[18px] font-semibold tracking-[-0.01em]">Залишилися питання?</p>
        <p class="mt-[6px] text-[15px] leading-[1.45] text-[{MUTED}]">Напишіть на <a href="mailto:roddihealth@gmail.com" class="font-medium text-[{INK}] underline underline-offset-2">roddihealth@gmail.com</a>, і ми відповімо якомога швидше.</p>
        <div class="mt-[18px]">{btn('Написати нам', 'mailto:roddihealth@gmail.com')}</div>
      </div>
    </div>
    <div class="faq-list">{items}</div>
  </div>
</section>'''

def footer():
    return f'''<footer id="early-access" class="px-3 pb-3 md:px-4 md:pb-4">
  <div class="rounded-[36px] bg-[{INK}] px-5 pb-[28px] pt-[80px] text-white md:rounded-[44px] md:px-10 md:pt-[110px]">
    <div class="mx-auto flex max-w-[760px] flex-col items-center text-center">
      <div data-reveal>{pill('Скоро запуск', dark=True)}</div>
      <h2 data-reveal data-d="80" class="t-h2-app mt-[18px]">Дізнайтеся першими, коли Roddi Health запрацює</h2>
      <p data-reveal data-d="160" class="mt-[14px] max-w-[520px] text-[16px] leading-[1.45] text-white/70">Залиште email, і ми напишемо про запуск та запросимо до раннього доступу.</p>
      <div data-reveal data-d="240" class="mt-[28px] flex w-full justify-center">{signup('footer', dark=True, consent=True)}</div>
    </div>
    <div class="mx-auto mt-[80px] grid max-w-[1280px] items-center gap-[24px] border-t border-white/12 pt-[28px] md:grid-cols-[1fr_auto_1fr]">
      <div class="order-2 flex justify-center gap-[10px] md:order-1 md:justify-start">
        <a href="https://www.instagram.com/marchin_rats/" target="_blank" rel="noopener" aria-label="Instagram" class="foot-icon"><img alt="" class="size-[22px]" src="assets/qlementineiconsinstagramfill16.svg"></a>
        <a href="https://www.tiktok.com/@marchin_rats" target="_blank" rel="noopener" aria-label="TikTok" class="foot-icon"><img alt="" class="size-[22px]" src="assets/akariconstiktokfill.svg"></a>
        <a href="mailto:roddihealth@gmail.com" aria-label="Email" class="foot-icon"><img alt="" class="size-[22px]" src="assets/griddyiconsemailfilled.svg"></a>
      </div>
      <a href="#" class="order-1 flex items-center justify-center gap-[8px] md:order-2" aria-label="Roddi Health"><img alt="" class="size-[36px]" src="assets/vector.svg"><span class="ff-montserrat text-left text-[21px] font-semibold leading-[0.95]">roddi<br>health</span></a>
      <nav class="order-3 flex flex-wrap justify-center gap-x-[24px] gap-y-[8px] text-[14px] text-white/75 md:justify-end">
        <a href="blog.html" class="hover:text-white">Блог</a><a href="#" class="hover:text-white">Політика конфіденційності</a><a href="mailto:roddihealth@gmail.com" class="hover:text-white">Контакти</a><a href="#" class="hover:text-white">Про проєкт</a>
      </nav>
    </div>
    <div class="mx-auto mt-[24px] flex max-w-[1280px] flex-col justify-between gap-[6px] text-center text-[13px] text-white/50 md:flex-row md:text-left">
      <p>Roddi Health не замінює консультацію ветеринара.</p><p>© 2026 Roddi Health</p>
    </div>
  </div>
</footer>'''

def draft_switch(current):
    links = ''.join(f'<a href="{href}" class="{"is-active" if key == current else ""}">{label}</a>'
                    for key, label, href in [('a', 'A · бенто', 'home-app.html'), ('b', 'B · з фото', 'home-app-v3.html'), ('c', 'C · список', 'home-app-v4.html')])
    return f'<nav class="draft-switch" aria-label="Варіанти блоку «Що вміє»"><span>Чернетка · «Що вміє»:</span>{links}</nav>'

SCRIPT = '''<script>
  var reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-d]').forEach(function (el) { el.style.setProperty('--d', el.dataset.d + 'ms'); });
  if (!('IntersectionObserver' in window)) document.documentElement.classList.remove('js');
  var revealer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); revealer.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('[data-reveal]').forEach(function (el) { revealer.observe(el); });
  addEventListener('scroll', function () {
    if (innerHeight + scrollY < document.documentElement.scrollHeight - 4) return;
    document.querySelectorAll('[data-reveal]:not(.is-in)').forEach(function (el) { el.classList.add('is-in'); });
  }, { passive: true });
  // Count-up numbers.
  function fmt(n) { return String(n).replace(/\\B(?=(\\d{3})+(?!\\d))/g, '\\u00a0'); }
  var counter = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      counter.unobserve(e.target);
      var el = e.target, to = +el.dataset.count, t0 = performance.now();
      (function tick(t) { var k = Math.min(1, (t - t0) / 1600); el.textContent = fmt(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(tick); })(t0);
    });
  });
  if (!reduceMotion) document.querySelectorAll('[data-count]').forEach(function (el) { el.textContent = '0'; counter.observe(el); });
  // In-page links. Smooth scrolling can stall where the browser draws few frames
  // (e.g. Claude's built-in browser), so jump if it hasn't started. Keep this fallback.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var id = a.getAttribute('href').slice(1);
    e.preventDefault();
    if (!id && a.getAttribute('aria-label') !== 'Roddi Health') return;
    var target = id ? document.getElementById(id) : document.documentElement;
    if (!target) return;
    var go = function (behavior) { if (id) target.scrollIntoView({ behavior: behavior, block: 'start' }); else scrollTo({ top: 0, behavior: behavior }); };
    var y0 = scrollY;
    go(reduceMotion ? 'instant' : 'smooth');
    if (!reduceMotion) setTimeout(function () { if (scrollY === y0) go('instant'); }, 200);
    if (location.hash !== (id ? '#' + id : '')) history.pushState(null, '', id ? '#' + id : location.pathname + location.search);
  });
  // One FAQ answer open at a time.
  document.querySelectorAll('.faq details').forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) document.querySelectorAll('.faq details[open]').forEach(function (o) { if (o !== d) o.open = false; }); });
  });
  // Variant C: highlight the feature whose card is in the middle of the screen.
  var links = document.querySelectorAll('[data-feat-link]');
  if (links.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) { l.classList.toggle('is-active', l.dataset.featLink === e.target.dataset.feat); });
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    document.querySelectorAll('[data-feat]').forEach(function (el) { spy.observe(el); });
  }
</script>
<script src="assets/forms.js"></script>
<script src="assets/menu.js"></script>
<script src="assets/carousel.js"></script>'''

def page(variant, features):
    return f'''<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Roddi Health — новий дизайн (чернетка {variant.upper()})</title>
  <link rel="icon" type="image/svg+xml" href="/assets/vector.svg">
  <meta name="robots" content="noindex, nofollow">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&family=Montserrat:wght@600&display=swap" rel="stylesheet">
  <script>document.documentElement.classList.add('js');</script>
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.11"></script>
  <!-- Generated by tools/build-app-home.py; edit that file, not this page. -->
  <link rel="stylesheet" href="assets/app-home.css">
</head>
<body>
{header()}
<main>
{hero()}
{memes()}
{features}
{orbit_cta()}
{for_whom()}
{story()}
{before_after()}
{faq()}
</main>
{footer()}
{draft_switch(variant)}
{SCRIPT}
</body>
</html>
'''

for variant, name, feats in [('a', 'home-app.html', features_a()), ('b', 'home-app-v3.html', features_b()), ('c', 'home-app-v4.html', features_c())]:
    (ROOT / name).write_text(page(variant, feats), encoding='utf-8')
    print(name, 'written')
