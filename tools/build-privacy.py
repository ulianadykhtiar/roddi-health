#!/usr/bin/env python3
"""Builds the privacy policy pages: privacy.html (Ukrainian) and en/privacy.html (English).

    python3 tools/build-privacy.py

The text lives below; nav, footer and the head (styles, scripts) are taken from
blog.html and en/blog.html, so redesigns there carry over after a rebuild. When the
policy changes in substance (new data, new service, new purpose), change DATE and
CONSENT_VERSION in assets/forms.js too: that version is stored with every sign-up.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://roddihealth.app'
OG = {'uk': BASE + '/assets/og-uk-v2.jpg', 'en': BASE + '/assets/og-en-v2.jpg'}
MAIL = 'roddihealth@gmail.com'

T = {
    'uk': dict(
        lang='uk', locale='uk_UA', file='privacy.html', url=BASE + '/privacy', other_file='en/privacy.html',
        title='Політика конфіденційності | Roddi Health', h1='Політика конфіденційності',
        desc='Які дані збирає Roddi Health, навіщо, кому ми їх довіряємо, скільки зберігаємо та як ви можете керувати даними й cookies.',
        meta='Оновлено 19 листопада 2026', skip='Перейти до змісту', home='Головна', crumb='Політика конфіденційності', nav='Навігація',
        body=f'''
    <h2>Хто ми</h2>
    <p>Roddi Health — додаток для здоров’я гризунів, який зараз розробляється. Сайт roddihealth.app ведуть Уляна і Вероніка Дихтяр, засновниці проєкту (далі «ми»). Ми відповідаємо за обробку ваших персональних даних. З будь-яких питань про ваші дані пишіть на <a href="mailto:{MAIL}">{MAIL}</a>.</p>
    <h2 id="data">Які дані ми збираємо і навіщо</h2>
    <ul>
      <li><b>Email.</b> Ви залишаєте його у формі раннього доступу. Разом з ним ми зберігаємо дату й час, форму й сторінку, з якої ви підписалися, мову сайту та факт вашої згоди (версію її тексту). Навіщо: щоб написати вам про запуск і запросити до раннього доступу, а також час від часу надсилати новини застосунку й корисні матеріали про догляд за гризунами, щоб ви про нас не забували. Підстава: ваша згода.</li>
      <li><b>Відповіді короткого опитування</b> (необов’язково): які у вас тварини й скільки їх, коли востаннє давали ліки, який у вас телефон (iPhone чи Android), чи хочете тестувати додаток, коментар. Вони прив’язані до вашого email. Навіщо: зрозуміти, що потрібно власникам гризунів, і спланувати запуск. Підстава: ваша згода.</li>
      <li><b>Листи до нас.</b> Якщо ви пишете на нашу пошту, ми зберігаємо листування, щоб відповісти.</li>
      <li><b>Технічні дані.</b> Хостинг автоматично зберігає службові журнали (IP-адреса, браузер, час запиту). Вони потрібні для безпеки й роботи сайту, ми їх не аналізуємо.</li>
    </ul>
    <p>Ми не збираємо дані про здоров’я людей. Відповіді про тварин пов’язані лише з вашим email.</p>
    <h2 id="cookies">Cookies і аналітика</h2>
    <p>Ми використовуємо <a href="https://privacy.microsoft.com/privacystatement" target="_blank" rel="noopener">Microsoft Clarity</a>, щоб бачити, як відвідувачі користуються сайтом (теплові карти й записи сесій), і покращувати його. Clarity встановлює cookies та впізнає вас між візитами лише тоді, коли ви дозволили аналітику в банері на сайті. Без вашої згоди він працює в обмеженому режимі без cookies і не пов’язує ваші візити між собою. Рекламних cookies ми не використовуємо.</p>
    <p>Ваш вибір зберігається в пам’яті браузера. Змінити його можна будь-коли через посилання «Налаштування cookies» у футері сайту.</p>
    <h2 id="third">Кому ми довіряємо дані</h2>
    <p>Ми не продаємо ваші дані й не передаємо їх для реклами. Для роботи сайту ми користуємося сервісами, які обробляють дані за нашим дорученням:</p>
    <ul>
      <li>Vercel: хостинг сайту;</li>
      <li>Google: Таблиці й Apps Script (там зберігаються заявки), Google Fonts (шрифти сайту);</li>
      <li>Microsoft: Clarity, див. вище;</li>
      <li>jsDelivr: мережа доставки, з якої завантажується бібліотека стилів.</li>
    </ul>
    <p>Ці сервіси можуть обробляти дані на серверах у різних країнах, зокрема в США.</p>
    <h2>Скільки ми зберігаємо дані</h2>
    <p>Email і відповіді опитування ми зберігаємо, доки ви не відкличете згоду або не попросите їх видалити, але не довше, ніж потрібно для запуску й розсилки. Листування зберігаємо, доки воно потрібне для відповіді.</p>
    <h2 id="rights">Ваші права</h2>
    <p>Ви можете будь-коли попросити показати, виправити чи видалити ваші дані, обмежити їх обробку, отримати їхню копію або відкликати згоду. Відкликання не впливає на законність обробки до нього. Напишіть на <a href="mailto:{MAIL}">{MAIL}</a>, і ми відповімо протягом місяця.</p>
    <p>Якщо ви вважаєте, що ми порушуємо ваші права, можете поскаржитися до наглядового органу: в Україні це Уповноважений Верховної Ради України з прав людини, у країнах ЄС — орган із захисту даних вашої країни. Ми обробляємо дані відповідно до законодавства України про захист персональних даних, а для відвідувачів з ЄС, ЄЕЗ і Великої Британії також відповідно до GDPR.</p>
    <h2>Як відписатися</h2>
    <p>Кожен лист матиме посилання для відписки. Ви також можете написати нам на пошту, і ми видалимо вашу адресу зі списку.</p>
    <h2>Діти</h2>
    <p>Сайт не призначений для дітей до 16 років. Якщо ви вважаєте, що дитина залишила нам дані, напишіть, і ми їх видалимо.</p>
    <h2>Зміни</h2>
    <p>Якщо ми змінимо цю політику, оновимо дату на початку сторінки.</p>
'''),
    'en': dict(
        lang='en', locale='en_US', file='en/privacy.html', url=BASE + '/en/privacy', other_file='privacy.html',
        title='Privacy Policy | Roddi Health', h1='Privacy Policy',
        desc='What data Roddi Health collects and why, who we trust with it, how long we keep it and how you can manage your data and cookies.',
        meta='Updated November 19, 2026', skip='Skip to content', home='Home', crumb='Privacy Policy', nav='Navigation',
        body=f'''
    <h2>Who we are</h2>
    <p>Roddi Health is an app for rodent health that is currently in development. The roddihealth.app website is run by Uliana and Veronika Dykhtiar, the founders of the project (“we”). We are responsible for processing your personal data. For any question about your data, write to <a href="mailto:{MAIL}">{MAIL}</a>.</p>
    <h2 id="data">What data we collect and why</h2>
    <ul>
      <li><b>Email.</b> You leave it in the early access form. With it we store the date and time, the form and page you signed up from, the site language and the fact of your consent (the version of its text). Why: to write to you about the launch and invite you to early access, and from time to time to send app news and useful materials about rodent care, so you do not forget about us. Legal basis: your consent.</li>
      <li><b>Answers to the short survey</b> (optional): which pets you have and how many, when you last gave medication, what phone you use (iPhone or Android), whether you want to test the app, and a comment. They are linked to your email. Why: to understand what rodent owners need and plan the launch. Legal basis: your consent.</li>
      <li><b>Emails to us.</b> If you write to our address, we keep the correspondence so we can reply.</li>
      <li><b>Technical data.</b> Our host automatically keeps service logs (IP address, browser, time of request). They are needed for security and for the site to work, and we do not analyze them.</li>
    </ul>
    <p>We do not collect health data about people. Answers about your pets are linked only to your email.</p>
    <h2 id="cookies">Cookies and analytics</h2>
    <p>We use <a href="https://privacy.microsoft.com/privacystatement" target="_blank" rel="noopener">Microsoft Clarity</a> to see how visitors use the site (heatmaps and session recordings) and to improve it. Clarity sets cookies and recognizes you between visits only if you have allowed analytics in the banner on the site. Without your consent it works in a limited mode without cookies and does not link your visits together. We do not use advertising cookies.</p>
    <p>Your choice is kept in your browser. You can change it at any time with the “Cookie settings” link in the site footer.</p>
    <h2 id="third">Who we trust with data</h2>
    <p>We do not sell your data or share it for advertising. To run the site we use services that process data on our behalf:</p>
    <ul>
      <li>Vercel: website hosting;</li>
      <li>Google: Sheets and Apps Script (where sign-ups are stored) and Google Fonts (the site’s typefaces);</li>
      <li>Microsoft: Clarity, see above;</li>
      <li>jsDelivr: the content delivery network the style library is loaded from.</li>
    </ul>
    <p>These services may process data on servers in different countries, including the United States.</p>
    <h2>How long we keep data</h2>
    <p>We keep your email and survey answers until you withdraw consent or ask us to delete them, but no longer than needed for the launch and the mailing. We keep correspondence as long as it is needed to reply.</p>
    <h2 id="rights">Your rights</h2>
    <p>You can ask at any time to see, correct or delete your data, restrict its processing, get a copy of it or withdraw your consent. Withdrawing does not affect the lawfulness of processing before it. Write to <a href="mailto:{MAIL}">{MAIL}</a> and we will reply within a month.</p>
    <p>If you believe we are violating your rights, you can complain to a supervisory authority: in Ukraine, the Ukrainian Parliament Commissioner for Human Rights; in the EU, the data protection authority of your country; in the UK, the Information Commissioner’s Office. We process data in line with Ukrainian personal data protection law and, for visitors from the EU, the EEA and the UK, the GDPR.</p>
    <h2>How to unsubscribe</h2>
    <p>Every email will contain an unsubscribe link. You can also write to us and we will remove your address from the list.</p>
    <h2>Children</h2>
    <p>The site is not intended for children under 16. If you believe a child has left us data, write to us and we will delete it.</p>
    <h2>Changes</h2>
    <p>If we change this policy, we will update the date at the top of the page.</p>
'''),
}


def strip_reveal(x):
    x = re.sub(r'\sdata-reveal(="[^"]*")?', '', x)
    return re.sub(r'\sdata-d="\d+"', '', x)


def build(lang):
    c = T[lang]
    prefix = '' if lang == 'uk' else '../'
    src = (ROOT / ('blog.html' if lang == 'uk' else 'en/blog.html')).read_text(encoding='utf-8')
    head = src[:src.index('</head>')]
    seo = '\n'.join([
        f'  <title>{c["title"]}</title>',
        '  <link rel="icon" type="image/svg+xml" href="%sassets/favicon.svg">' % prefix,
        '  <link rel="icon" type="image/png" sizes="32x32" href="%sassets/favicon-32.png">' % prefix,
        '  <link rel="apple-touch-icon" sizes="180x180" href="%sassets/apple-touch-icon.png">' % prefix,
        f'  <meta name="description" content="{c["desc"]}">',
        '  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        f'  <link rel="canonical" href="{c["url"]}">',
        f'  <link rel="alternate" hreflang="uk" href="{T["uk"]["url"]}">',
        f'  <link rel="alternate" hreflang="en" href="{T["en"]["url"]}">',
        f'  <link rel="alternate" hreflang="x-default" href="{T["uk"]["url"]}">',
        '  <meta property="og:type" content="website">',
        '  <meta property="og:site_name" content="Roddi Health">',
        f'  <meta property="og:title" content="{c["h1"]}">',
        f'  <meta property="og:description" content="{c["desc"]}">',
        f'  <meta property="og:url" content="{c["url"]}">',
        f'  <meta property="og:image" content="{OG[lang]}">',
        f'  <meta property="og:locale" content="{c["locale"]}">',
        '  <meta name="twitter:card" content="summary_large_image">',
        '  <script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebPage", "name": "%s", "description": "%s", "url": "%s", "inLanguage": "%s"}</script>'
        % (c['h1'], c['desc'], c['url'], c['lang']),
    ])
    if '<!-- seo:start -->' in head:
        head = re.sub(r'<!-- seo:start -->.*?<!-- seo:end -->', lambda m: seo, head, count=1, flags=re.S)
    else:  # the English pages carry the same block without the markers: from <title> to the last JSON-LD
        a = head.index('  <title>')
        ld = head.rindex('</script>', 0, head.index('<link rel="preconnect"'))
        assert 'application/ld+json' in head[a:ld], 'JSON-LD not found in ' + lang
        head = head[:a] + seo + head[ld + len('</script>'):]

    dialog = strip_reveal(src[src.index('<dialog id="site-menu"'):src.index('</dialog>') + 9])
    nav_start = src.index('<nav data-reveal="down"')
    nav = strip_reveal(src[nav_start:src.index('</nav>', nav_start) + 6]).replace(' aria-current="page"', '')
    foot = strip_reveal(src[src.index('<footer id="early-access"'):src.index('</footer>') + 9]).replace('data-form="blog"', 'data-form="privacy"')
    # The language switch goes to the same page in the other language.
    other = ('en/privacy.html' if lang == 'uk' else '/privacy.html')
    nav = re.sub(r'(<a href=")[^"]*(" class="lang-opt")', r'\g<1>%s\2' % other, nav, count=1)

    home = 'index.html' if lang == 'uk' else '/en/index.html'
    main = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="{c['nav']}"><a href="{home}">{c['home']}</a><span aria-hidden="true">/</span><b>{c['crumb']}</b></nav>
  <h1 class="t-h1">{c['h1']}</h1>
  <p class="ar-meta">{c['meta']}</p>
  <div class="ar-body">{c['body']}  </div>
</main>'''
    html = f'''{head}</head>
<body class="page-soft">
<a class="skip-link" href="#main">{c['skip']}</a>
{dialog}
<header class="relative bg-white">
  {nav}
</header>
{main}

{foot}
<script src="{prefix}assets/forms.js?v=3"></script>
<script src="{prefix}assets/menu.js?v=2"></script>
</body>
</html>
'''
    (ROOT / c['file']).write_text(html, encoding='utf-8')
    print(c['file'], 'written')


for lg in ('uk', 'en'):
    build(lg)
