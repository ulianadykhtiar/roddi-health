#!/usr/bin/env python3
"""Builds the blog's own article pages (blog/<slug>.html) and assets/blog-articles.js.

    python3 tools/build-articles.py

The texts below are original overviews in Ukrainian written from the listed sources:
facts restated in our own words, never copied. Each article must name what it used, so
add a source whenever you add a fact. Run this script after any change to the list; it
also refreshes the crawler list in blog.html and the article URLs in sitemap.xml.
Nav and footer come from blog.html, so redesigns there carry over.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://roddihealth.app'
PUBLISHED = '2026-11-09'
UPDATED = '2026-11-09'
# When the facts were last compared with the sources. Each article may set its own
# 'published', 'updated' and 'checked' dates; these are the defaults.
CHECKED = '2026-11-09'
# Topics that get the "if it gets worse, go to the vet now" notice at the top.
ALERT_TOPICS = ('Симптоми', 'Невідкладне')
MONTHS = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']


def uk_date(iso):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MONTHS[int(m) - 1], y)


P = {
    'rat': {'src': 'f/fd/Fancy_rat_blaze.jpg', 'by': 'AlexK100', 'lic': 'CC BY-SA 2.0', 'page': 'https://commons.wikimedia.org/wiki/File:Fancy_rat_blaze.jpg'},
    'rat2': {'src': '4/41/Fancy_rat_husky.jpg', 'by': 'Eurovaran', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Fancy_rat_husky.jpg', 'pos': '50% 35%'},
    'hamster': {'src': '7/73/Syrian_Hamster_Mid-grooming.jpg', 'by': 'John Stockla', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Syrian_Hamster_Mid-grooming.jpg'},
    'hamster2': {'src': 'f/f5/Syrian_hamster_on_blanket.jpg', 'by': 'MarketBoiCYM', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Syrian_hamster_on_blanket.jpg', 'pos': '50% 40%'},
    'gp': {'src': 'e/ee/Cavia_porcellus01.jpg', 'by': 'Kacper Aleksander', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Cavia_porcellus01.jpg'},
    'gp2': {'src': 'b/bc/Caviidae_Cavia_porcellus_1.jpg', 'by': 'NasserHalaweh', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Caviidae_Cavia_porcellus_1.jpg'},
    'degu': {'src': 'f/f4/Octodontidae_Octodon_degus_1.2.jpg', 'by': 'NasserHalaweh', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Octodontidae_Octodon_degus_1.2.jpg'},
    'rabbit': {'src': '3/31/Heimtier_004_2023_08_26.jpg', 'by': 'Friedrich Haag', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Heimtier_004_2023_08_26.jpg'},
    'chin': {'src': '4/45/Napoleon_chinchilla_in_box.jpg', 'by': 'Bluerasberry', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Napoleon_chinchilla_in_box.jpg', 'pos': '50% 45%'},
    'chin2': {'src': 'e/e8/Chinchilla_lanigera1.jpg', 'by': 'Trurl66', 'lic': 'Public domain', 'page': 'https://commons.wikimedia.org/wiki/File:Chinchilla_lanigera1.jpg'},
    'mouse': {'src': 'e/ed/Pet_mouse_mini.jpg', 'by': 'Tiia Monto', 'lic': 'CC BY-SA 3.0', 'page': 'https://commons.wikimedia.org/wiki/File:Pet_mouse_mini.jpg'},
    'mouse2': {'src': '4/4d/Pet_mouse_drinking.jpg', 'by': 'Tiia Monto', 'lic': 'CC BY-SA 3.0', 'page': 'https://commons.wikimedia.org/wiki/File:Pet_mouse_drinking.jpg', 'pos': '50% 35%'},
}

S = {
    'petmd_uri': ('PetMD: інфекції верхніх дихальних шляхів у щурів', 'https://www.petmd.com/exotic/conditions/respiratory/upper-respiratory-infection-rats'),
    'petmd_rat': ('PetMD: памʼятка з догляду за щурами', 'https://www.petmd.com/exotic/rat-care-sheet'),
    'rspca_rat': ('RSPCA: чим годувати щурів', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/rats/diet'),
    'petmd_ham': ('PetMD: памʼятка з догляду за хомʼяками', 'https://www.petmd.com/exotic/hamster-care-sheet'),
    'petmd_syr': ('PetMD: сирійські хомʼяки', 'https://www.petmd.com/exotic/syrian-hamster-care-sheet'),
    'petmd_dwarf': ('PetMD: карликові хомʼяки', 'https://www.petmd.com/exotic/dwarf-hamster-care-sheet'),
    'petmd_wet': ('PetMD: мокрий хвіст у хомʼяків', 'https://www.petmd.com/exotic/condition/wet-tail-in-hamsters'),
    'petmd_gi_gp': ('PetMD: стаз ШКТ у морських свинок', 'https://www.petmd.com/exotic/gi-stasis-in-guinea-pigs'),
    'petmd_gp': ('PetMD: памʼятка з догляду за морськими свинками', 'https://www.petmd.com/exotic/guinea-pig-care-sheet'),
    'spca_c': ('SPCA New Zealand: вітамін C для морських свинок', 'https://spca.nz/advice-and-welfare/article/why-is-vitamin-c-important-for-my-guinea-pigs'),
    'petmd_gi_r': ('PetMD: стаз ШКТ у кроликів', 'https://www.petmd.com/rabbit/conditions/digestive/gastrointestinal-gi-stasis-rabbits'),
    'walker_r': ('Walkerville Vet: кролик не їсть', 'https://www.walkervillevet.com.au/blog/rabbit-not-eating/'),
    'exotic_d': ('Exotic Direct: чим годувати дегу', 'https://exoticdirect.co.uk/news/degu-food-advice-what-your-degu-should-be-eating-not-eating-diabetes-and-other-advice/'),
    'petmd_d': ('PetMD: догляд за дегу', 'https://www.petmd.com/exotic/care/caring-for-a-degu'),
    'petmd_m': ('PetMD: памʼятка з догляду за мишами', 'https://www.petmd.com/exotic/mouse-care-sheet'),
    # Sources for the mice and chinchilla articles (third item: English label).
    'rspca_mice': ('RSPCA: миші', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/mice', 'RSPCA: mice'),
    'rspca_mice_health': ('RSPCA: здоровʼя мишей', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/mice/health', 'RSPCA: mice health and welfare'),
    'rspca_mice_env': ('RSPCA: житло для мишей', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/mice/environment', 'RSPCA: creating a good home for mice'),
    'rspca_mice_company': ('RSPCA: як тримати мишей разом', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/mice/company', 'RSPCA: keeping mice together'),
    'rspcaau_mice_unwell': ('RSPCA Australia: як виглядає хвора миша', 'https://kb.rspca.org.au/categories/companion-animals/other-pets/rats-and-mice/what-does-an-unhealthy-mouse-look-like', 'RSPCA Australia: what does an unhealthy mouse look like?'),
    'rspcaau_mice_problems': ('RSPCA Australia: поширені хвороби мишей', 'https://kb.rspca.org.au/knowledge-base/what-are-common-health-problems-in-mice/', 'RSPCA Australia: common health problems in mice'),
    'rspcaau_mice_feed': ('RSPCA Australia: чим годувати мишей', 'https://kb.rspca.org.au/categories/companion-animals/other-pets/rats-and-mice/what-should-i-feed-my-mice', 'RSPCA Australia: what should I feed my mice?'),
    'rspcaau_mice_keep': ('RSPCA Australia: де тримати мишей', 'https://kb.rspca.org.au/categories/companion-animals/other-pets/rats-and-mice/where-should-i-keep-my-mice', 'RSPCA Australia: where should I keep my mice?'),
    'rspcavic_mice': ('RSPCA Victoria: догляд за мишами й щурами', 'https://rspcavic.org/learn/caring-for-your-mice-and-rats/', 'RSPCA Victoria: caring for your mice and rats'),
    'nsw_mice_health': ('Міністерство освіти Нового Південного Уельсу: здоровʼя мишей', 'https://education.nsw.gov.au/teaching-and-learning/animals-in-schools/animals-in-schools-species/mice/mice-health', 'NSW Department of Education: mice health'),
    'nsw_mice_env': ('Міністерство освіти Нового Південного Уельсу: умови утримання мишей', 'https://education.nsw.gov.au/teaching-and-learning/animals-in-schools/animals-in-schools-species/mice/mice-environment', 'NSW Department of Education: mice environment'),
    'pdsa_mice': ('PDSA: миші як домашні тварини', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/mouse-health', 'PDSA: mice as pets'),
    'petmd_chin_dust': ('PetMD: пилові ванни для шиншил', 'https://www.petmd.com/exotic/care/how-give-your-chinchilla-dust-bath', 'PetMD: chinchilla dust baths'),
    'petmd_chin': ('PetMD: памʼятка з догляду за шиншилами', 'https://www.petmd.com/exotic/chinchilla-care-sheet', 'PetMD: chinchilla care guide'),
    'petmd_chin_teeth': ('PetMD: переросли зуби в шиншил', 'https://www.petmd.com/exotic/conditions/mouth/overgrown-chinchilla-teeth', 'PetMD: overgrown chinchilla teeth'),
    'rspca_chin': ('RSPCA: шиншили як домашні тварини', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/chinchillas', 'RSPCA: keeping chinchillas as pets'),
    'rspca_chin_env': ('RSPCA: житло для шиншил', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/chinchillas/environment', 'RSPCA: creating a good home for chinchillas'),
    'rspca_chin_health': ('RSPCA: здоровʼя шиншил', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/chinchillas/health', 'RSPCA: chinchilla health and welfare'),
    'pdsa_chin': ('PDSA: здоровʼя шиншил', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/chinchilla-health', 'PDSA: chinchilla health'),
    'crossley_2001': ('Crossley D. A. Dental disease in chinchillas in the UK. Journal of Small Animal Practice, 2001 (наукова стаття)', 'https://doi.org/10.1111/j.1748-5827.2001.tb01977.x', 'Crossley D. A. Dental disease in chinchillas in the UK. Journal of Small Animal Practice, 2001 (research paper)'),
}


def ul(*items):
    return '<ul>' + ''.join('<li>%s</li>' % i for i in items) + '</ul>'


def table(head, rows):
    h = ''.join('<th scope="col">%s</th>' % c for c in head)
    b = ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>' for r in rows)
    return '<div class="ar-table"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)


ARTICLES = [
    dict(slug='chomu-shchur-chkhaie', rodent='rat', topic='Симптоми', photo='rat', featured=True,
         title='Чому щур чхає і коли їхати до ветеринара',
         seo='Чому щур чхає: причини, симптоми, коли до ветеринара',
         desc='Чому домашній щур чхає чи важко дихає: ранні ознаки респіраторної інфекції, небезпечні симптоми й що записати для ветеринара.',
         short='Навіть поодиноке чхання або червонуваті кірочки біля очей і носа можуть бути першими ознаками респіраторної інфекції. У щурів вона дуже поширена й без лікування може перейти в пневмонію, тому чхання варто показати ветеринару, а не чекати.',
         tags='чхає чхання дихання хрипи важко дихає нежить порфірин мікоплазма застуда',
         urgent=['хрипи або «клацання» під час дихання', 'щур дихає животом або з відкритим ротом', 'згорблена поза, різке схуднення', 'нахил голови, втрата рівноваги'],
         sections=[
             ('Які ознаки помітні спочатку', '<p>На початку симптоми легко пропустити: щур зрідка чхає, а біля очей чи носа зʼявляються дрібні червонуваті кірочки. За кілька днів можуть додатися:</p>' + ul('часте чхання й примружені очі', 'іржаві сльози або виділення з носа', 'гірший апетит і млявість', 'скуйовджена шерсть', 'зміни в поведінці: щур уникає рук, дратується чи кусається')),
             ('Чому це трапляється', '<p>Більшість щурів від природи носить бактерію <i>Mycoplasma pulmonis</i>, одну з найчастіших причин таких інфекцій. Вона передається від щура до щура. Захворювання також можуть викликати віруси й інші бактерії, які приєднуються, коли імунітет ослаблений.</p><p>Ризик підвищують вік, інші хвороби, стрес, аміак у брудній клітці, а ще дим, вейп, ароматичне мило, побутова хімія й свічки. Хвоя й кедр у наповнювачі теж подразнюють дихальні шляхи: краще обрати паперовий.</p>'),
             ('Що зробити до прийому', ul('Запишіться до лікаря, який працює з гризунами.', 'Приберіть клітку й усуньте різкі запахи поруч.', 'Зніміть відео дихання: лікарю це часто корисніше за опис.', 'Не давайте ліки чи антибіотики без призначення.')),
             ('Як знизити ризик', ul('Тримайте нових щурів окремо перші 2 тижні й спостерігайте за ними.', 'Регулярно прибирайте клітку, щоб не накопичувався аміак.', 'Ставте клітку в тихому чистому місці без протягів.')),
         ],
         check=['коли почалося чхання й скільки разів на день', 'відео дихання', 'поточна вага й чи змінився апетит', 'чи зʼявлялися нові щури', 'який наповнювач і чи були різкі запахи'],
         sources=['petmd_uri', 'petmd_rat'], related=['chym-goduvaty-shchura', 'skilky-zhyvut-gryzuny']),

    dict(slug='chym-goduvaty-shchura', rodent='rat', topic='Харчування', photo='rat2',
         title='Чим годувати щура: що можна, а що не можна',
         seo='Чим годувати домашнього щура: що можна і що не можна',
         desc='Основа раціону домашнього щура, скільки ласощів можна й таблиця продуктів: виноград, молоко, хліб, цибуля, помідори та інші.',
         short='Основа раціону домашнього щура — гранульований корм саме для щурів. Овочі, трохи фруктів, варене яйце, зерно й насіння дають у межах денної норми, а не понад неї. Виноград, родзинки, цибуля, цитрусові й шоколад не підходять.',
         tags='чим годувати що їсть раціон корм гранули виноград хліб помідор молоко капуста ласощі ожиріння',
         sections=[
             ('Що має бути основою', '<p>Обирайте гранули, створені саме для щурів. Корм для кроликів, морських свинок чи хомʼяків не дасть потрібних поживних речовин. Щури всеїдні, тож раціон можна доповнювати невеликою кількістю овочів, фруктів, вареного яйця, зерна й насіння.</p><p>Такі доповнення входять у денну порцію. PetMD радить, щоб ласощі становили не більше 10% раціону: щури легко набирають зайву вагу.</p>'),
             ('Чи можна щурам: коротка таблиця', table(['Продукт', 'Відповідь', 'Примітка'], [
                 ['Виноград, родзинки', 'Ні', 'У переліку шкідливих у RSPCA'],
                 ['Цибуля, часник', 'Ні', ''],
                 ['Цитрусові, ревінь', 'Ні', ''],
                 ['Волоські горіхи', 'Ні', 'У переліку шкідливих у RSPCA'],
                 ['Шоколад, кава, алкоголь', 'Ні', 'Токсичні, можуть бути смертельними'],
                 ['Сирі боби, картопля', 'Ні', ''],
                 ['Незрілі помідори', 'Ні', 'Про стиглі в цих джерелах окремо не сказано'],
                 ['Кісточки й насіння фруктів', 'Ні', ''],
                 ['Молочне', 'Краще уникати', 'Жирне; лише зрідка як ласощі'],
                 ['Зерно, хліб', 'Трохи', 'Зерно дозволене потроху; про хліб окремо не сказано'],
                 ['Більшість овочів', 'Так', 'Дрібними шматочками, у межах норми'],
             ])),
             ('Як годувати', ul('Двічі на день, уранці й увечері: щури їдять переважно на світанку й у сутінках.', 'Прибирайте те, що не зʼїли. Залишки овочів і фруктів викидайте щонайпізніше через 10 годин.', 'Солодке й жирне лишайте як винагороду під час дресирування.')),
         ],
         check=['чим саме годуєте й скільки на день', 'вага щура в динаміці', 'які ласощі давали останнім часом'],
         sources=['rspca_rat', 'petmd_rat'], related=['chomu-shchur-chkhaie', 'skilky-zhyvut-gryzuny']),

    dict(slug='chym-goduvaty-khomiaka', rodent='hamster', topic='Харчування', photo='hamster',
         title='Чим годувати хомʼяка: що можна, а що не можна',
         seo='Чим годувати хомʼяка вдома: що можна і що не можна',
         desc='Основа раціону хомʼяка і таблиця продуктів: яблуко, морква, капуста, персик, цитрусові, цибуля та інші. Чому надлишок овочів небезпечний.',
         short='Більшу частину раціону хомʼяка має становити готовий гранульований корм із вмістом білка 15–25%. Овочі дають помірно, бо надлишок свіжого може спричинити діарею, а для хомʼяка це небезпечно.',
         tags='чим годувати що їсть раціон корм яблуко морква капуста банан персик абрикос помідор перець кабачок джунгарик сирійський',
         sections=[
             ('Що має бути основою', '<p>Базою є якісний гранульований корм із 15–25% білка. Хомʼяки ховають їжу про запас, тому важливо регулярно перевіряти запаси. Вони активні вночі, тож свіже зручно давати ввечері.</p><p>Свіжі овочі обирайте з високим вмістом клітковини й давайте потроху. Фрукти містять багато цукру: яблуко чи ягоди лише зрідка й крихітними порціями.</p>'),
             ('Чи можна хомʼяку: коротка таблиця', table(['Продукт', 'Відповідь', 'Примітка'], [
                 ['Цибуля, часник', 'Ні', ''],
                 ['Шоколад', 'Ні', 'Токсичний'],
                 ['Цитрусові, ревінь', 'Ні', ''],
                 ['Мигдаль', 'Ні', 'У переліку PetMD'],
                 ['Сирі боби, сира картопля', 'Ні', ''],
                 ['Незрілі помідори', 'Ні', ''],
                 ['Кісточки й насіння фруктів', 'Ні', 'Зокрема насіння яблук, кісточки персика й абрикоса'],
                 ['Солодке, солоне, червоне мʼясо', 'Ні', ''],
                 ['Яблуко без насіння, банан, персик', 'Зрідка', 'Крихітний шматочок'],
                 ['Більшість овочів', 'Помірно', 'Морква, кабачок, перець: потроху'],
             ])),
             ('Чого остерігатися', ul('Різкої зміни корму чи марки: це може засмутити кишечник.', 'Надлишку овочів, фруктів чи солодких ласощів.', 'Зіпсованих залишків: прибирайте свіже через кілька годин, зокрема зі схованок.')),
         ],
         check=['чим годуєте й чи змінювали корм', 'що давали зі свіжого за останні дні', 'який вигляд має послід'],
         sources=['petmd_ham', 'petmd_syr', 'petmd_wet'], related=['mokryi-khvist-u-khomiaka', 'skilky-zhyvut-gryzuny']),

    dict(slug='mokryi-khvist-u-khomiaka', rodent='hamster', topic='Невідкладне', photo='hamster2',
         title='Мокрий хвіст у хомʼяка: симптоми й що робити',
         seo='Мокрий хвіст у хомʼяка: симптоми, причини, що робити',
         desc='Мокрий хвіст у хомʼяка часто є невідкладним станом. Симптоми, причини, чому хомʼяк не їсть і чому до лікаря треба протягом доби.',
         short='«Мокрий хвіст» — це діарея, через яку намокає шерсть під хвостом. Хомʼяк швидко втрачає рідину, тому стан часто є невідкладним: ветеринар-екзотолог має оглянути його в ідеалі протягом 24 годин.',
         tags='мокрий хвіст діарея пронос не їсть млявий хомяк помирає зневоднення',
         urgent=['мокра, злиплa шерсть під хвостом і на животі', 'водянистий послід', 'хомʼяк не їсть, млявий, ховається', 'роздутий або болючий живіт, згорблена поза'],
         sections=[
             ('Що це таке', '<p>Так зазвичай називають діарею в молодих хомʼяків, хоча вона трапляється в будь-якому віці. Через втрату рідини хомʼяк слабшає, гірше їсть, шерсть стає неохайною. Без своєчасного лікування він може загинути.</p>'),
             ('Чому це трапляється', '<p>Причини бувають інфекційні: бактерії, зокрема в хомʼяків віком 3–10 тижнів, найпростіші та кишкові паразити. Бувають і неінфекційні:</p>' + ul('раптова зміна корму чи його марки', 'забагато овочів, фруктів чи солодких ласощів', 'стрес', 'деякі антибіотики, зокрема пеніцилін, які порушують кишкову мікрофлору')),
             ('Що зробити зараз', ul('Телефонуйте лікарю, який працює з екзотичними тваринами.', 'Не давайте ліків, особливо антибіотиків, без призначення.', 'Ізолюйте хворого хомʼяка від інших і тримайте в чистоті й тиші.', 'Лікар може призначити рідини, антибіотики й підтримувальне лікування.')),
             ('Як знизити ризик', ul('Чиста клітка без зайвого стресу.', 'Збалансований корм без різких змін.', 'Карантин для нових хомʼяків.')),
         ],
         check=['коли зʼявилися симптоми', 'вік хомʼяка', 'зміни корму, нові тварини, стрес', 'які ліки давали останнім часом', 'коли їв і пив востаннє'],
         sources=['petmd_wet'], related=['chym-goduvaty-khomiaka', 'skilky-zhyvut-gryzuny']),

    dict(slug='morska-svynka-ne-yist', rodent='guinea-pig', topic='Невідкладне', photo='gp',
         title='Морська свинка не їсть: що робити',
         seo='Морська свинка не їсть і не пʼє: що робити',
         desc='Чому морська свинка не їсть і чому це невідкладний стан: ознаки стазу ШКТ, що записати для лікаря і чого не робити вдома.',
         short='Якщо морська свинка перестала їсти чи стало менше посліду, телефонуйте ветеринару відразу. Стаз шлунково-кишкового тракту без лікування може стати смертельним за 24–48 годин.',
         tags='не їсть не пє воду не какає стаз шкт сіно живіт скрегіт зубами нічого не їсть',
         urgent=['свинка не їсть або їсть набагато менше', 'менше посліду, він дрібний або його немає', 'млявість, згорблена поза', 'здутий чи твердий живіт, скрегіт зубами'],
         sections=[
             ('Чому це так небезпечно', '<p>Кишечник морської свинки має працювати постійно. Коли він сповільнюється, накопичуються гази й порушується баланс бактерій, а стан швидко погіршується.</p>'),
             ('Можливі причини', '<p>Стаз зазвичай є наслідком іншої проблеми:</p>' + ul('мало сіна й клітковини', 'зневоднення', 'біль чи хвороба, зокрема проблеми із зубами', 'стрес: зміна місця, поводження, компанії', 'мало руху') + '<p>Точну причину може встановити лише лікар: огляд зазвичай охоплює зуби, вагу, живіт, рентген і аналізи.</p>'),
             ('Що зробити зараз', ul('Телефонуйте ветеринару, не чекайте до ранку.', 'Запишіть, коли свинка востаннє їла й ходила в туалет.', 'Якщо є можливість, візьміть зразок посліду.', 'Не давайте ліки без призначення: морські свинки чутливі до багатьох антибіотиків.')),
             ('Як знизити ризик', ul('Сіно й чиста вода доступні постійно.', 'Щоденний рух.', 'До лікаря при перших змінах апетиту.')),
         ],
         check=['коли востаннє їла й пила', 'коли востаннє був послід і який він', 'вага сьогодні й тиждень тому', 'зміни в раціоні чи оточенні'],
         sources=['petmd_gi_gp'], related=['chym-goduvaty-morsku-svynku', 'skilky-zhyvut-gryzuny']),

    dict(slug='chym-goduvaty-morsku-svynku', rodent='guinea-pig', topic='Харчування', photo='gp2',
         title='Чим годувати морську свинку і де брати вітамін C',
         seo='Чим годувати морську свинку: сіно, овочі, вітамін C',
         desc='Раціон морської свинки: скільки сіна, які гранули, навіщо вітамін C, ознаки його нестачі й що не можна давати.',
         short='Приблизно 80% раціону морської свинки становлять трава й сіно, і вони мають бути доступні постійно. Вітамін C свинки не виробляють самі, тому отримують його щодня з їжею.',
         tags='чим годувати що їсть сіно овочі вітамін с цинга гранули петрушка раціон',
         sections=[
             ('Основа раціону', '<p>Майже будь-яке трав’яне сіно підходить. Винятком є люцерна: при регулярному споживанні вона може зашкодити. Гранули дають обмежено: обирайте такі, що зроблені на основі трав, збагачені вітаміном C і не прострочені. Вітаміну в гранулах різко меншає, якщо минуло понад 3 місяці від дати виробництва.</p>'),
             ('Навіщо вітамін C', '<p>Він потрібен для загоєння ран, стану шкіри, суглобів і ясен, а також для імунітету. На нестачу можуть вказувати скуйовджена шерсть, млявість, небажання ходити, гірший апетит, діарея, набряклі лапи чи суглоби, кровотечі або виразки на яснах і шкірі. Такі ознаки потребують огляду лікаря.</p><p>SPCA зазначає, що вітамін C у питній воді й гранулах є ненадійним джерелом, бо швидко руйнується. Найкраще щодня давати свіжі овочі й трохи фруктів.</p>'),
             ('Де джерела розходяться', '<p>SPCA радить листову зелень на кшталт кейлу, петрушки й шпинату заради вітаміну C. PetMD застерігає, що саме в цих овочах багато кальцію, а свинки схильні до каменів у сечовому міхурі. Обговоріть із ветеринаром, скільки такої зелені підходить саме вашій свинці.</p>'),
             ('Чого не давати', ul('Крохмалисте: горох, боби, кукурудзу, горіхи, крупи, печиво, тістечка.', 'Авокадо, цибулю, лілії.')),
         ],
         check=['який корм і як давно відкрита упаковка', 'які овочі даєте щодня', 'чи давали вітамін C окремо'],
         sources=['petmd_gp', 'spca_c'], related=['morska-svynka-ne-yist', 'skilky-zhyvut-gryzuny']),

    dict(slug='krolyk-ne-yist', rodent='rabbit', topic='Невідкладне', photo='rabbit',
         title='Кролик не їсть: чому це небезпечно й що робити',
         seo='Кролик не їсть і не пʼє: причини і що робити',
         desc='Чому кролик перестав їсти, ознаки стазу ШКТ, скільки годин не можна чекати і чого не робити вдома до прийому.',
         short='Кролик має їсти й випорожнюватися постійно. Більше 8 годин без їжі чи посліду — це вже відхилення, а стаз ШКТ є невідкладним станом, тож звертайтеся до ветеринара якнайшвидше.',
         tags='не їсть не їсть сіно не пє стаз шкт здувся живіт скрегіт зубами декоративний кролик нічого не їсть',
         urgent=['кролик не їсть або послід зник', 'скрегіт зубами, згорблена поза', 'здутий або болючий живіт', 'холодні вуха й лапи'],
         sections=[
             ('Що може бути причиною', '<p>Найчастіше причиною є стаз шлунково-кишкового тракту, але апетит також зникає через:</p>' + ul('проблеми із зубами', 'хвороби нирок і сечового міхура', 'абсцеси й пневмонію', 'непрохідність кишечника', 'стрес, біль, зневоднення') + '<p>Розрізнити стаз і непрохідність може лише лікар.</p>'),
             ('Скільки можна чекати', '<p>Джерела трохи різняться: PetMD вважає ненормальним понад 8 годин без їжі чи випорожнення, а клініка Walkerville радить іти до лікаря, якщо апетит не покращився за 12 годин або кролик притихлий. Безпечніше орієнтуватися на менший термін.</p>'),
             ('Чого не робити вдома', ul('Не масажуйте живіт: спершу треба виключити непрохідність.', 'Не покладайтеся на ананас, папаю чи мастила від «грудок шерсті»: вони зазвичай не потрібні й можуть зашкодити.', 'Не давайте ліки без призначення.')),
             ('Як знизити ризик', ul('Постійний доступ до якісного сіна.', 'Кролики лише на гранулах мають вищий ризик стазу.', 'Менше фруктів, зерна й обробленого корму.')),
         ],
         check=['коли востаннє їв', 'коли востаннє був послід і якого розміру', 'раціон і зміни в ньому', 'стрес, операції, інші хвороби'],
         sources=['petmd_gi_r', 'walker_r'], related=['skilky-zhyvut-gryzuny', 'morska-svynka-ne-yist']),

    dict(slug='chym-goduvaty-degu', rodent='degu', topic='Харчування', photo='degu',
         title='Чим годувати дегу: сіно, гранули й обережно з цукром',
         seo='Чим годувати дегу: що можна і що не можна',
         desc='Раціон дегу, чому цукор небезпечний через діабет і таблиця продуктів: морква, капуста, яблуко, огірок, виноград, петрушка.',
         short='Основа раціону дегу — якісне сіно. Гранули дають у малій кількості й без цукру та патоки, бо дегу схильні до діабету. Фрукти й крохмалисті овочі найкраще обмежити або виключити.',
         tags='чим годувати білка дегу діабет цукор сіно морква капуста яблука огірок виноград петрушка',
         sections=[
             ('Основа раціону', '<p>Більшу частину раціону становить сіно, наприклад тимофіївка чи лугове. Сіно зношує зуби й підтримує кишечник. Коричневе, надто зелене чи вкрите рожевим або білим нальотом сіно не годиться.</p><p>Гранули для дегу чи морських свинок дають обмежено: джерела називають приблизно 10 г на день або 1–2 столові ложки залежно від розміру тварини. У складі не має бути цукру чи патоки.</p>'),
             ('Чи можна дегу: коротка таблиця', table(['Продукт', 'Exotic Direct', 'PetMD'], [
                 ['Яблуко, морква, огірок', 'Раз на місяць', 'Фрукти уникати'],
                 ['Капуста, броколі', '1–2 рази на тиждень, може здувати', 'Окремо не сказано'],
                 ['Свіжі трави, петрушка', '1–2 рази на тиждень', 'Окремо не сказано'],
                 ['Горох, кукурудза', 'Раз на місяць', 'Уникати'],
                 ['Картопля', 'Окремо не перевірено', 'Уникати'],
                 ['Виноград та інші солодкі фрукти', 'Окремо не перевірено', 'Уникати'],
             ]) + '<p>Джерела розходяться, тому за наявності сумнівів дотримуйтесь суворішого варіанту й порадьтеся з ветеринаром.</p>'),
             ('Вода й вітамін C', '<p>Воду міняйте щодня. Вітамін C не додавайте у воду: неможливо проконтролювати дозу, і він швидко руйнується. За потреби він може надходити з їжі, наприклад із броколі чи червоного перцю.</p>'),
         ],
         check=['склад корму', 'що даєте понад сіно', 'чи пʼє більше звичайного, чи помутніли очі', 'вага в динаміці'],
         sources=['exotic_d', 'petmd_d'], related=['skilky-zhyvut-gryzuny', 'chym-goduvaty-morsku-svynku']),

    dict(slug='skilky-zhyvut-gryzuny', rodent='rat', topic='Догляд', photo='hamster2',
         title='Скільки живуть домашні гризуни: щури, хомʼяки, свинки, дегу',
         seo='Скільки живуть щури, хомʼяки, морські свинки, дегу вдома',
         desc='Порівняльна таблиця тривалості життя домашніх гризунів: щур, сирійський і карликовий хомʼяк, миша, морська свинка, дегу.',
         short='Найкоротший вік серед цих тварин у мишей, приблизно 1,5–2 роки. Щури й хомʼяки зазвичай живуть до 2–3 років, морські свинки до 8, а дегу 5–9 років.',
         tags='скільки живе років тривалість життя щур хомяк морська свинка дегу миша вік',
         sections=[
             ('Порівняльна таблиця', table(['Тварина', 'Середня тривалість за належного догляду'], [
                 ['Миша', '18–24 місяці'],
                 ['Щур', 'до 3 років'],
                 ['Сирійський хомʼяк', '2–3 роки'],
                 ['Карликовий хомʼяк', '2–3 роки'],
                 ['Морська свинка', 'до 8 років'],
                 ['Дегу', '5–9 років'],
             ]) + '<p>Це орієнтовні середні значення з памʼяток PetMD. Окремі тварини живуть менше чи довше.</p>'),
             ('Що найбільше впливає', ul('Раціон, що відповідає виду, без надлишку цукру й жиру.', 'Чисте житло без різких запахів і протягів.', 'Рух, заняття й спокійне поводження.', 'Планові огляди: для хомʼяків PetMD радить щонайменше раз на рік.', 'Звернення до лікаря при перших змінах: дрібні тварини погіршуються швидко.')),
             ('Чому важливо записувати', '<p>У таких тварин зміни ваги чи апетиту можуть бути єдиним раннім сигналом. Регулярні записи допомагають помітити тенденцію й показати її лікарю.</p>'),
         ],
         check=['вік тварини', 'вага в динаміці', 'перенесені хвороби й лікування'],
         sources=['petmd_rat', 'petmd_syr', 'petmd_dwarf', 'petmd_m', 'petmd_gp', 'petmd_d'], related=['chym-goduvaty-shchura', 'chym-goduvaty-khomiaka']),
    # ---- Mice and chinchillas (PR 2, 16 November 2026) ----
    dict(slug='zdorovia-myshi', rodent='mouse', topic='Симптоми', photo='mouse', featured=True,
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Як перевірити здоровʼя миші: щоденний огляд і тривожні ознаки',
         seo='Здоровʼя домашньої миші: щоденний огляд і коли до ветеринара',
         desc='На що дивитися під час щоденного огляду домашньої миші: очі, шерсть, дихання, послід, вага й поведінка. Які ознаки означають, що потрібен ветеринар.',
         short='Миші приховують нездужання, тож помітні симптоми часто означають, що тварина вже серйозно хвора. Короткий огляд уранці й увечері допомагає побачити зміни рано: тьмяні очі, скуйовджену шерсть, незвичне дихання, схуднення або мишу, яка сидить окремо від інших.',
         tags='здоровʼя огляд хвора миша чхає дихання шерсть кліщі пухлина грудка зуби схудла',
         urgent=['миша не їсть або не пʼє', 'сидить згорблено, очі тьмяні чи запалі', 'дихає часто, нерівно, з цоканням чи клацанням', 'діарея або виділення з очей чи носа', 'нахил голови, тремтіння чи судоми', 'гарячий здутий живіт або нова грудка'],
         sections=[
             ('Чому оглядати щодня', '<p>Миші швидко слабнуть, а біль показують дуже слабко, аж поки стан не стане важким. RSPCA Australia пояснює це тим, що миші є здобиччю і приховують хворобу: якщо миша виглядає хворою, вона вже серйозно хвора. Тому оглядайте мишей двічі на день, уранці й увечері, коли вони активні. Спершу кілька хвилин спокійно поспостерігайте, а потім придивіться до кожної.</p>'),
             ('Як виглядає здорова миша', ul('Очі ясні й широко відкриті.', 'Шерсть щільна, гладенька й блискуча.', 'Дихання рівне, без звуків.', 'Спить, згорнувшись клубочком. Якщо миша лежить витягнувшись, це може бути ознакою хвороби.', 'Рухається жваво, їсть і спить разом з іншими.')),
             ('На що звернути увагу', table(['Що перевірити', 'Що насторожує'], [
                 ['Очі', 'тьмяні чи запалі очі, примружування, виділення'],
                 ['Ніс і дихання', 'виділення з носа, цокання, часте або важке дихання з помітним рухом живота, часте чхання'],
                 ['Шерсть і шкіра', 'скуйовджена, брудна чи злиплa шерсть, послід під хвостом, почервоніла шкіра, проплішини'],
                 ['Послід', 'діарея, мʼякий послід із неприємним запахом'],
                 ['Вага й тіло', 'схуднення або швидкий набір ваги, грудки під шкірою'],
                 ['Поведінка', 'ховається більше звичайного, сидить окремо в кутку, мало рухається, не цікавиться їжею, пʼє набагато більше'],
             ]) + '<p>Щодо чхання джерела трохи різняться: шкільний посібник Нового Південного Уельсу вважає тривожним будь-яке чхання, а RSPCA Australia радить іти до лікаря, якщо миша чхнула більше кількох разів за годину-дві. Мʼякий послід теж буває різним. Миші зазвичай зʼїдають особливий мʼякий послід, і це норма, а от мʼякий послід із неприємним запахом, що лишається в клітці, вже насторожує.</p>'),
             ('Чому важлива вага', '<p>RSPCA зазначає, що втрата 20% маси тіла й більше може бути для миші смертельною. Для миші вагою 30 г це лише 6 г, тож на око таку зміну легко пропустити. Записи ваги допомагають побачити тенденцію й показати її лікарю.</p>'),
             ('Найчастіші проблеми', ul(
                 '<b>Дихальні інфекції.</b> За даними RSPCA Australia, їх часто спричиняють вірус Сендай і мікоплазма. Ознаки: чхання, цокання, важке дихання, нахил голови, миша менше вмивається й худне. Лікування полегшує симптоми, але інфекція й зміни в легенях лишаються. Лікування призначає ветеринар.',
                 '<b>Зуби.</b> Різці ростуть усе життя. Якщо вони переросли, миша гірше їсть, слинить, худне, може зʼявитися набряк морди. Зуби підрізає ветеринар, а тверді предмети для гризіння знижують ризик.',
                 '<b>Шкіра й кліщі.</b> Хутрові кліщі часто спричиняють проблеми зі шкірою: рідшу жирну шерсть на голові й тулубі та свербіж. Шерсть без ранок на шкірі може випадати й тому, що її обгризає домінантна миша.',
                 '<b>Пухлини.</b> Найпоширеніший рак у мишей — пухлини молочних залоз. RSPCA Australia пише, що вони можуть подвоїтися за два тижні або швидше й майже завжди злоякісні. Будь-яку нову грудку покажіть ветеринару одразу.')),
             ('Нові миші й візит до лікаря', '<p>Шкільний посібник Нового Південного Уельсу радить тримати нових мишей окремо чотири тижні й уважно спостерігати: вони можуть переносити хворобу без жодних ознак. Якщо ведете мишу до ветеринара, RSPCA Australia радить узяти з собою її сусідку, щоб після повернення вони пахли однаково й не посварилися. Обирайте лікаря, який працює з мишами.</p>'),
         ],
         check=['коли ви помітили зміни', 'вага сьогодні й раніше', 'фото або відео дихання й пози', 'чи їсть і пʼє, який послід', 'чи зʼявлялися нові миші', 'чим годуєте й яка підстилка'],
         sources=['rspca_mice_health', 'rspcaau_mice_unwell', 'rspcaau_mice_problems', 'nsw_mice_health', 'pdsa_mice'],
         related=['domashni-myshi', 'zdorovia-shynshyly'],
         en=dict(
             title='How to check a pet mouse’s health: daily check and warning signs',
             seo='Pet mouse health: daily check and when to see a vet',
             desc='What to look at during a pet mouse’s daily check: eyes, coat, breathing, droppings, weight and behaviour. Which signs mean your mouse needs a vet.',
             short='Mice hide illness, so by the time symptoms are obvious a mouse is often already seriously ill. A short check every morning and evening helps you spot changes early: dull eyes, a ruffled coat, unusual breathing, weight loss or a mouse that sits apart from the others.',
             tags='health check sick mouse sneezing breathing coat mites tumour lump teeth weight loss',
             urgent=['the mouse is not eating or drinking', 'it sits hunched, with dull or sunken eyes', 'breathing is fast, irregular, chattering or clicking', 'diarrhoea, or discharge from the eyes or nose', 'head tilt, tremors or fits', 'a hot swollen belly or a new lump'],
             sections=[
                 ('Why check every day', '<p>Mice can go downhill quickly and show only faint signs of pain until things are severe. RSPCA Australia explains that as prey animals they hide illness: if a mouse looks sick, it is already very sick. Check your mice twice a day, in the morning and evening when they are active. Watch quietly for a few minutes first, then look at each mouse closely.</p>'),
                 ('What a healthy mouse looks like', ul('Clear, wide-open eyes.', 'A dense, sleek, shiny coat.', 'Even, quiet breathing.', 'Sleeps curled up in a ball. A mouse lying stretched out may be unwell.', 'Moves briskly, eats and sleeps with the others.')),
                 ('What to look out for', table(['What to check', 'Warning signs'], [
                     ['Eyes', 'dull or sunken eyes, squinting, discharge'],
                     ['Nose and breathing', 'nasal discharge, chattering, fast or laboured breathing with a lot of belly movement, frequent sneezing'],
                     ['Coat and skin', 'ruffled, dirty or matted fur, droppings stuck under the tail, red skin, bald patches'],
                     ['Droppings', 'diarrhoea, soft foul-smelling droppings'],
                     ['Weight and body', 'weight loss or rapid weight gain, lumps under the skin'],
                     ['Behaviour', 'hiding more than usual, sitting alone in a corner, moving little, losing interest in food, drinking much more'],
                 ]) + '<p>Sources differ slightly on sneezing: the New South Wales schools guide treats any sneezing as a warning sign, while RSPCA Australia suggests seeing a vet if a mouse sneezes more than a few times over an hour or two. Soft droppings vary too. Mice normally eat a special soft dropping, which is healthy, but soft, foul-smelling droppings left in the cage are a concern.</p>'),
                 ('Why weight matters', '<p>The RSPCA notes that losing 20% or more of body weight can be fatal for a mouse. For a 30 g mouse that is just 6 g, so the change is easy to miss by eye. Keeping a weight record helps you see a trend and show it to the vet.</p>'),
                 ('Common problems', ul(
                     '<b>Respiratory infections.</b> According to RSPCA Australia, they are often caused by Sendai virus and Mycoplasma. Signs: sneezing, chattering, laboured breathing, head tilt, less grooming and weight loss. Treatment eases the symptoms, but the infection and the changes in the lungs remain. Treatment is prescribed by a vet.',
                     '<b>Teeth.</b> Incisors grow throughout life. If they overgrow, the mouse eats less, drools, loses weight and may get a swollen face. A vet trims the teeth, and hard things to gnaw lower the risk.',
                     '<b>Skin and mites.</b> Fur mites are a common cause of skin trouble: thinner, greasy fur on the head and body, and itching. Fur loss without sores can also come from a dominant mouse chewing others’ fur.',
                     '<b>Tumours.</b> The most common cancer in mice is mammary tumours. RSPCA Australia says they can double in size in two weeks or less and are almost always malignant. Show any new lump to a vet straight away.')),
                 ('New mice and vet visits', '<p>The New South Wales schools guide advises keeping new mice apart for four weeks and watching them closely, because they can carry disease without any signs. When you take a mouse to the vet, RSPCA Australia suggests bringing a cage-mate along so they still smell the same afterwards and don’t fall out. Choose a vet who treats mice.</p>'),
             ],
             check=['when you noticed the change', 'today’s weight and earlier weights', 'a photo or video of breathing and posture', 'whether it eats and drinks, what the droppings look like', 'whether any new mice arrived', 'what you feed and which bedding you use'],
         )),
    dict(slug='domashni-myshi', rodent='mouse', topic='Догляд', photo='mouse2',
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Домашні миші: житло, прибирання, корм і компанія',
         seo='Як доглядати за домашніми мишами: клітка, підстилка, корм',
         desc='Як облаштувати житло домашніх мишей, чим застелити й як часто прибирати, чим годувати й чому миші не мають жити поодинці. Огляд порад RSPCA, PDSA та інших організацій.',
         short='Миші — соціальні нічні тварини. Їм потрібні родичі тієї ж статі, просторе провітрюване житло без протягів і місця, щоб ховатися та лазити. Основа раціону — гранульований корм для мишей, свіжа зелень у межах денної норми й чиста вода щодня.',
         tags='клітка житло підстилка прибирання корм гранули компанія самці самки колесо температура',
         sections=[
             ('Компанія', '<p>Миші соціальні й мають жити з іншими мишами. Тримають сталі групи однієї статі. Самці часто агресивні до незнайомих самців, тому групу краще складати з братів, які росли разом. Самиці зазвичай легше приймають новеньких. Самця й самиць разом тримають, лише якщо самець кастрований. RSPCA радить тримати мишу поодинці, тільки якщо так скаже ветеринар, а інших гризунів у компанію мишам не підселяти.</p>'),
             ('Житло', ul(
                 'Точної норми площі для домашніх мишей джерела не дають. Радять якомога просторіше житло, а більшість кліток із зоомагазину PDSA вважає замалими.',
                 'Житло має добре провітрюватися, але без протягів. У скляних і суцільних пластикових боксах накопичується аміак.',
                 'Відстань між прутами не більша за 5 мм (RSPCA Australia) або 6 мм (PDSA).',
                 'Підлога суцільна: сітка травмує лапи.',
                 'Кілька рівнів, драбинки й мотузки: миші добре лазять.',
                 'Кілька схованок із двома виходами й темне місце для гнізда.')),
             ('Де поставити', '<p>PDSA і шкільний посібник Нового Південного Уельсу називають комфортною температуру 18–22 °C без різких перепадів. Не ставте клітку на сонці чи на протязі, у ванній, гаражі чи на заскленій веранді. Мишам потрібна тиша, подалі від телевізора й гучної музики: вони чутливі до шуму й світла. RSPCA Australia радить забезпечити 8–12 годин темряви й тиші на добу.</p>'),
             ('Підстилка й гніздо', table(['Підходить', 'Не підходить'], [
                 ['паперова чи картонна підстилка, целюлозні гранули', 'дрібна тирса, ароматизована чи фарбована підстилка'],
                 ['для гнізда: рваний папір, серветки, сіно', 'вата й пухнасті волокна: вони обплутують лапки'],
                 ['шар щонайменше 2 см, а в одному місці 3–4 см, щоб копати', 'кукурудзяні качани'],
             ]) + '<p>Щодо деревної стружки джерела розходяться: RSPCA Victoria й шкільний посібник Нового Південного Уельсу її допускають, а RSPCA, PDSA і RSPCA Australia радять уникати. Безпечніше обрати паперову підстилку.</p>'),
             ('Прибирання', ul(
                 'Щодня прибирайте послід і мокру підстилку.',
                 'Повне прибирання PDSA радить робити щотижня, RSPCA — раз на один-два тижні.',
                 'Миші мітять територію запахом. Повертайте назад трохи сухої старої підстилки, щоб житло не стало для них чужим.',
                 'Прибирайте ввечері, коли миші прокидаються.',
                 'Уранці й увечері перевіряйте поїлку: миші можуть забити носик підстилкою.')),
             ('Чим годувати', ul(
                 'Основа раціону — гранули чи брикети для мишей. Кожна гранула має все потрібне, і миша не може вибрати лише смачне.',
                 'Зернові суміші RSPCA Australia й RSPCA Victoria не радять: миші вибирають улюблене, а це веде до дисбалансу й ожиріння. PDSA допускає суміші, але радить перейти на гранули, якщо миша лишає частину корму.',
                 'Свіжа темна зелень і некрохмалисті овочі — невеликими порціями, у межах денної норми, а не понад неї.',
                 'Ласощі — не більше 10% калорій.',
                 'Не давайте шоколад, виноград і родзинки, авокадо, часник, цибулю, каву, чай, алкоголь, солодке, жирне, молочне й липку їжу.',
                 'Розсипайте частину корму, щоб миші його шукали.',
                 'Свіжа вода щодня. RSPCA Australia радить пляшечку-поїлку, а краще дві на випадок, якщо одна зламається.',
                 'Новий корм вводьте поступово.')),
             ('Гризіння й рух', '<p>Різці мишей ростуть усе життя, тому їм потрібні предмети для гризіння з необробленого дерева чи картону. Колесо має бути суцільним, без щілин і перекладин і достатньо великим, щоб миша бігала з рівною спиною. RSPCA нагадує, що колесо не має бути єдиною розвагою: додайте тунелі, коробки й мотузки.</p>'),
         ],
         check=['скільки мишей і якої статі живуть разом', 'розмір і тип клітки', 'яка підстилка й корм', 'як часто прибираєте', 'температура в кімнаті'],
         sources=['rspca_mice', 'rspca_mice_env', 'rspca_mice_company', 'pdsa_mice', 'rspcaau_mice_keep', 'rspcaau_mice_feed', 'rspcavic_mice', 'nsw_mice_env'],
         related=['zdorovia-myshi', 'pylovi-vanny-shynshyly'],
         en=dict(
             title='Pet mice: housing, cleaning, food and company',
             seo='How to care for pet mice: cage, bedding and food',
             desc='How to set up a home for pet mice, which bedding to use and how often to clean, what to feed and why mice should not live alone. An overview of advice from the RSPCA, PDSA and others.',
             short='Mice are social, nocturnal animals. They need same-sex companions, a roomy, well-ventilated home without draughts, and places to hide and climb. The core of the diet is a pelleted mouse food, with fresh greens within the daily ration and clean water every day.',
             tags='cage housing bedding cleaning food pellets company males females wheel temperature',
             sections=[
                 ('Company', '<p>Mice are social and should live with other mice. Keep stable single-sex groups. Males are often aggressive towards unfamiliar males, so a male group is best made of brothers who grew up together. Females usually accept newcomers more easily. A male lives with females only if he is neutered. The RSPCA advises keeping a mouse alone only if a vet says so, and not housing other rodents with mice.</p>'),
                 ('Housing', ul(
                     'Sources give no exact floor area for pet mice. They advise as much space as possible, and PDSA considers most pet-shop cages too small.',
                     'The home needs good airflow without draughts. Ammonia builds up in glass tanks and solid plastic boxes.',
                     'Bar spacing of no more than 5 mm (RSPCA Australia) or 6 mm (PDSA).',
                     'A solid floor: wire mesh hurts their feet.',
                     'Several levels, ladders and ropes: mice are good climbers.',
                     'Several hides with two exits, and a dark spot for a nest.')),
                 ('Where to put it', '<p>PDSA and the New South Wales schools guide give 18–22 °C as a comfortable range, without sudden swings. Keep the cage out of direct sun and draughts, and out of bathrooms, garages and conservatories. Mice need quiet, away from the TV and loud music, as they are sensitive to noise and light. RSPCA Australia suggests 8–12 hours of dark, quiet time a day.</p>'),
                 ('Bedding and nest', table(['Suitable', 'Not suitable'], [
                     ['paper or card bedding, cellulose pellets', 'fine sawdust, scented or coloured bedding'],
                     ['for the nest: shredded paper, tissues, hay', 'cotton wool and fluffy fibres: they tangle around feet'],
                     ['a layer of at least 2 cm, with one 3–4 cm area for digging', 'corn cobs'],
                 ]) + '<p>Sources disagree about wood shavings: RSPCA Victoria and the New South Wales schools guide allow them, while the RSPCA, PDSA and RSPCA Australia advise against them. Paper bedding is the safer choice.</p>'),
                 ('Cleaning', ul(
                     'Remove droppings and wet bedding every day.',
                     'PDSA recommends a full clean every week; the RSPCA says every one to two weeks.',
                     'Mice scent-mark their territory. Put back a little dry old bedding so the home still smells familiar.',
                     'Clean in the evening, when mice wake up.',
                     'Check the water bottle morning and evening: mice can block the spout with bedding.')),
                 ('What to feed', ul(
                     'The core of the diet is mouse pellets or blocks. Each pellet contains everything needed, so a mouse cannot pick out only the tasty bits.',
                     'RSPCA Australia and RSPCA Victoria advise against seed mixes: mice pick their favourite parts, which leads to imbalance and obesity. PDSA allows mixes but suggests switching to pellets if a mouse leaves part of the food.',
                     'Fresh dark greens and non-starchy vegetables in small portions, as part of the daily ration rather than on top of it.',
                     'Treats should be no more than 10% of calories.',
                     'Don’t give chocolate, grapes or raisins, avocado, garlic, onion, coffee, tea, alcohol, sweets, fatty or dairy foods, or sticky food.',
                     'Scatter some food so the mice can forage for it.',
                     'Fresh water every day. RSPCA Australia recommends a drinking bottle, ideally two in case one fails.',
                     'Introduce new food gradually.')),
                 ('Gnawing and exercise', '<p>Mice’s incisors grow throughout life, so they need things to gnaw made of untreated wood or cardboard. A wheel should be solid, with no gaps or rungs, and big enough for the mouse to run with a straight back. The RSPCA reminds owners that a wheel shouldn’t be the only enrichment: add tunnels, boxes and ropes.</p>'),
             ],
             check=['how many mice live together and their sex', 'cage size and type', 'which bedding and food you use', 'how often you clean', 'room temperature'],
         )),
    dict(slug='pylovi-vanny-shynshyly', rodent='chinchilla', topic='Догляд', photo='chin', featured=True,
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Пилові ванни для шиншили: навіщо, як часто й скільки тривати',
         seo='Пилова ванна для шиншили: як часто, скільки й який пил',
         desc='Чому шиншилу не купають у воді, який пил підходить для ванни, скільки вона має тривати і як часто її давати. Порівняння порад PetMD, RSPCA і PDSA.',
         short='Шиншила чиститься в пилу: він забирає з густого хутра зайвий жир і вологу. Купати у воді не можна, бо хутро довго сохне, а шкіра може запалитися. Ванну зі спеціальним пилом дають на обмежений час і після цього прибирають, щоб пил не подразнював очі.',
         tags='пилова ванна пил пісок купання хутро шерсть очі вологість',
         sections=[
             ('Навіщо шиншилі пил', '<p>Хутро шиншили дуже густе: з одного волосяного фолікула росте кілька десятків волосин (PetMD пише про до 60, RSPCA — про 60–90). Так ці тварини пристосувалися до холодних високогірʼїв. Перекочуючись у пилу, шиншила прибирає з хутра зайвий шкірний жир, бруд і вологу. PDSA попереджає, що без таких ванн хутро може звалюватися. А ще ванна для шиншили — розвага.</p>'),
             ('Чому не вода', '<p>Густе хутро довго сохне й затримує вологу. За даними PetMD, через це воно може звалюватися, а шкіра — запалюватися. Тому шиншилу не купають і не мочать.</p>'),
             ('Який пил обрати', ul(
                 'Беріть спеціальний пил або пісок для ванн шиншил. За PetMD, це тонкий очищений порошок із вулканічного попелу, пемзи, каоліну чи кварцового піску.',
                 'Звичайний пісок і схожі продукти, не призначені для шиншил, надто абразивні: вони можуть подразнити шкіру, очі й дихальні шляхи.',
                 'Надто дрібний пил може подразнювати ніс і очі, особливо в шиншил до року.',
                 'Коли пил грудкується, замініть його.')),
             ('Ємність', '<p>Потрібна відкрита зверху ємність, у якій шиншила може вільно перекочуватися, наприклад неглибока металева миска. Закрита ємність затримує вологу. Щодо шару пилу джерела різняться: PetMD радить близько 2,5 см, PDSA — 4–6 см.</p>'),
             ('Як часто й скільки', table(['Джерело', 'Як часто', 'Скільки'], [
                 ['PetMD, стаття про ванни', '2–4 рази на тиждень', '10–30 хв; для шиншил до року 3–4 хв'],
                 ['PetMD, памʼятка з догляду', 'щонайменше кілька разів на тиждень', 'не вказано'],
                 ['RSPCA', 'щодня', 'не вказано'],
                 ['PDSA', 'щодня', 'до 10 хв'],
             ]) + '<p>Спільне в усіх джерелах одне: ванну не лишають у клітці постійно. Узгодьте частоту з ветеринаром і стежте за станом хутра й шкіри. PetMD попереджає, що понад тиждень без ванни може призвести до надлишку жиру на шкірі й подразнення.</p>'),
             ('Чому ванну прибирають', '<p>Постійний доступ до пилу, за PetMD, може спричинити конʼюнктивіт і сухість шкіри. До того ж шиншили можуть використовувати ванну як туалет, тому RSPCA радить після купання прибирати пил або просіювати його.</p>'),
             ('Умови в кімнаті', '<p>RSPCA радить тримати шиншил удома в сухому провітрюваному приміщенні без протягів, бажано за 10–18 °C: спека, вологість і протяги можуть спричинити хворобу. PetMD додає, що вологість має бути нижчою за 40–50%, а клітку не ставлять на пряме сонце.</p>'),
             ('Коли до ветеринара', '<p>Покажіть шиншилу лікарю, якщо зʼявилися проплішини, виділення з очей чи носа, вологе хутро біля очей або рота. Про інші тривожні ознаки читайте в статті про здоровʼя шиншили.</p>'),
         ],
         check=['як часто й скільки триває ванна', 'який пил використовуєте', 'стан очей і хутра', 'температура й вологість у кімнаті'],
         sources=['petmd_chin_dust', 'petmd_chin', 'rspca_chin', 'rspca_chin_env', 'rspca_chin_health', 'pdsa_chin'],
         related=['zdorovia-shynshyly', 'domashni-myshi'],
         en=dict(
             title='Dust baths for chinchillas: why, how often and for how long',
             seo='Chinchilla dust bath: how often, how long and which dust',
             desc='Why chinchillas are not bathed in water, which dust to use, how long a bath should last and how often to offer it. A comparison of advice from PetMD, the RSPCA and PDSA.',
             short='Chinchillas clean themselves in dust, which takes excess oil and moisture out of their dense fur. Bathing them in water is a bad idea: the fur takes a long time to dry and the skin can become inflamed. A bath of special dust is offered for a limited time and then removed so the dust doesn’t irritate the eyes.',
             tags='dust bath dust sand bathing fur coat eyes humidity',
             sections=[
                 ('Why chinchillas need dust', '<p>A chinchilla’s fur is extremely dense: several dozen hairs grow from a single follicle (PetMD says up to 60, the RSPCA says 60–90). It is an adaptation to cold high mountains. By rolling in dust, a chinchilla removes excess skin oil, dirt and moisture from its coat. PDSA warns that without these baths the fur can become matted. A bath is also enrichment.</p>'),
                 ('Why not water', '<p>Dense fur dries slowly and holds moisture. According to PetMD, this can lead to matting and inflamed skin. That is why chinchillas are not bathed or wetted.</p>'),
                 ('Which dust to choose', ul(
                     'Use dust or sand made specifically for chinchilla baths. According to PetMD, it is a fine, cleaned powder made from volcanic ash, pumice, kaolin or silver sand.',
                     'Ordinary sand and similar products not meant for chinchillas are too abrasive and can irritate the skin, eyes and airways.',
                     'Extra-fine dust can irritate the nose and eyes, especially in chinchillas under a year old.',
                     'Replace the dust when it gets clumpy.')),
                 ('The bath bowl', '<p>Use an open-top bowl or tray the chinchilla can roll around in freely, such as a shallow metal bowl. A closed box traps moisture. Sources differ on depth: PetMD suggests about 2.5 cm (1 inch), PDSA 4–6 cm.</p>'),
                 ('How often and how long', table(['Source', 'How often', 'How long'], [
                     ['PetMD, dust bath article', '2–4 times a week', '10–30 min; 3–4 min for chinchillas under a year'],
                     ['PetMD, care guide', 'at least a few times a week', 'not stated'],
                     ['RSPCA', 'daily', 'not stated'],
                     ['PDSA', 'daily', 'up to 10 min'],
                 ]) + '<p>All sources agree on one thing: the bath does not stay in the cage all the time. Agree the frequency with your vet and watch the condition of the coat and skin. PetMD warns that going more than a week without a bath can lead to excess oil and skin irritation.</p>'),
                 ('Why the bath is removed', '<p>According to PetMD, constant access to dust can cause conjunctivitis and dry skin. Chinchillas may also use the bath as a toilet, so the RSPCA advises removing or sieving the dust after use.</p>'),
                 ('Room conditions', '<p>The RSPCA advises keeping chinchillas indoors in a dry, well-ventilated, draught-free room, ideally at 10–18 °C: heat, humidity and draughts can make them ill. PetMD adds that humidity should stay below 40–50% and the cage should be out of direct sunlight.</p>'),
                 ('When to see a vet', '<p>Take your chinchilla to a vet if you notice bald patches, discharge from the eyes or nose, or wet fur around the eyes or mouth. See our chinchilla health article for other warning signs.</p>'),
             ],
             check=['how often and how long the bath lasts', 'which dust you use', 'the condition of the eyes and coat', 'room temperature and humidity'],
         )),
    dict(slug='zdorovia-shynshyly', rodent='chinchilla', topic='Симптоми', photo='chin2',
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Здоровʼя шиншили: зуби, хутро, травлення й тривожні ознаки',
         seo='Здоровʼя шиншили: зуби, хутро, травлення, коли до ветеринара',
         desc='Чому зуби шиншили ростуть усе життя і як помітити проблеми з ними, що означають зміни в посліді та хутрі, яка температура безпечна і коли терміново їхати до ветеринара.',
         short='Зуби шиншили ростуть усе життя, тому основа раціону — необмежене сіно, а не солодкі суміші. Слина на підборідді, гірший апетит, схуднення чи менше посліду можуть означати біль у роті або проблеми з травленням. Шиншили приховують хворобу, тож такі ознаки — привід звернутися до ветеринара одразу.',
         tags='зуби слина слинотеча сіно послід не їсть хутро випадає стрес температура спека',
         urgent=['шиншила не їсть або посліду поменшало чи немає', 'слинотеча, мокре підборіддя', 'млявість, шиншила менше рухається', 'утруднене дихання', 'діарея або мʼякий послід'],
         sections=[
             ('Чому важливо помітити рано', '<p>PetMD зазначає, що шиншили добре приховують нездужання, тож проблеми із зубами можна не помітити до важкої стадії. PDSA і RSPCA радять оглядати шиншилу щодня, а RSPCA — ще й показувати її ветеринару щонайменше раз на рік.</p>'),
             ('Зуби', '<p>Зуби шиншили ростуть безперервно й стираються під час жування. Тому основа раціону — сіно й трава, причому PetMD радить давати якісне сіно без обмежень. Гранул дають небагато й без солодких ласощів. Сумішей на кшталт мюслі PDSA радить уникати: шиншила вибирає з них солодке, а це може призвести до болісної хвороби зубів. Для гризіння підійдуть блоки або гілки необробленої яблуні чи груші.</p>'
              + '<p>Ознаки проблем із зубами, за PetMD:</p>' + ul('слинотеча й мокре хутро на підборідді', 'шиншила гірше їсть, впускає їжу, тре лапою рот', 'схуднення й менше посліду', 'набряк щелепи чи морди', 'передні зуби переросли або ростуть криво', 'шиншила менше вмивається й мляво поводиться')
              + '<p>У британському дослідженні 2001 року (Crossley) зміни зубів виявили під час зовнішнього огляду в 35% шиншил, які виглядали здоровими. Автор також зазначив, що набряк щелепи, схуднення чи зміни в жуванні бувають за різних проблем із зубами, тож точну причину визначає ветеринар. За PetMD, огляд задніх зубів зазвичай потребує седації й рентгену, а підрізати зуби вдома не можна. Якщо через біль шиншила перестає їсти, може розвинутися стаз ШКТ або інфекція, небезпечна для життя вже за кілька годин або днів.</p>'),
             ('Травлення', '<p>RSPCA радить щодня перевіряти, що шиншила їсть і залишає багато сухого посліду. Якщо змінилися звички в їжі чи питті або посліду поменшало чи він зник, одразу звертайтеся до ветеринара: шиншила може бути серйозно хвора. Діарея і мʼякий послід теж привід для візиту.</p>'),
             ('Хутро й шкіра', '<p>Втрата хутра може бути ознакою хвороби чи травми. RSPCA також називає ознаками стресу обгризання власного чи чужого хутра й клаптики хутра, що відпадають, коли шиншилу тримають у руках. Це захисна реакція, яка може статися через неправильне поводження. Без пилових ванн хутро звалюється, про них є окрема стаття.</p>'),
             ('Тепло й вологість', '<p>Густе хутро — пристосування до холоду, тож спека й вологість для шиншили небезпечні. Джерела дають трохи різні межі: RSPCA радить 10–18 °C у сухому приміщенні без протягів, а PetMD — приблизно 13–21 °C, не вище 27 °C, з вологістю нижче 40–50% і без прямого сонця.</p>'),
             ('Щоденний огляд', ul(
                 'Очі й ніс без виділень, хутро біля очей і рота сухе.',
                 'Шиншила їсть, пʼє, послід звичайний і його багато.',
                 'Хутро без проплішин, шкіра без змін.',
                 'Лапи без натоптишів і ранок, шиншила не кульгає.',
                 'Немає незвичних набряків.',
                 'Вага стабільна: PetMD радить стежити за масою тіла.')),
         ],
         check=['коли шиншила востаннє нормально їла', 'скільки посліду за добу й який він', 'вага в динаміці', 'фото підборіддя, зубів і хутра', 'чим годуєте: сіно, гранули, ласощі', 'температура в кімнаті'],
         sources=['pdsa_chin', 'rspca_chin_health', 'rspca_chin_env', 'petmd_chin_teeth', 'petmd_chin', 'crossley_2001'],
         related=['pylovi-vanny-shynshyly', 'zdorovia-myshi'],
         en=dict(
             title='Chinchilla health: teeth, fur, digestion and warning signs',
             seo='Chinchilla health: teeth, fur, digestion and when to see a vet',
             desc='Why a chinchilla’s teeth grow throughout life and how to spot dental problems, what changes in droppings and fur mean, which temperatures are safe and when to see a vet urgently.',
             short='A chinchilla’s teeth grow throughout life, so the core of its diet is unlimited hay, not sugary mixes. Saliva on the chin, a poorer appetite, weight loss or fewer droppings can mean mouth pain or digestive trouble. Chinchillas hide illness, so these signs are a reason to see a vet straight away.',
             tags='teeth drooling slobbers hay droppings not eating fur loss stress temperature heat',
             urgent=['the chinchilla is not eating, or there are fewer or no droppings', 'drooling, a wet chin', 'lethargy, moving less', 'difficulty breathing', 'diarrhoea or soft droppings'],
             sections=[
                 ('Why spotting problems early matters', '<p>PetMD notes that chinchillas are good at hiding illness, so dental problems can go unnoticed until they are severe. PDSA and the RSPCA recommend checking your chinchilla every day, and the RSPCA also advises a vet check-up at least once a year.</p>'),
                 ('Teeth', '<p>A chinchilla’s teeth grow continuously and wear down through chewing. That is why the core of the diet is hay and grass, and PetMD advises unlimited good-quality hay. Pellets are given sparingly, without sugary treats. PDSA advises avoiding muesli-style mixes: chinchillas pick out the sugary bits, which can lead to painful dental disease. Chew blocks or untreated apple or pear branches are good for gnawing.</p>'
                  + '<p>Signs of dental problems, according to PetMD:</p>' + ul('drooling and wet fur on the chin', 'eating less, dropping food, pawing at the mouth', 'weight loss and fewer droppings', 'swelling of the jaw or face', 'overgrown or crooked front teeth', 'less grooming and lethargy')
                  + '<p>In a 2001 UK study (Crossley), dental changes were found on external examination in 35% of chinchillas that looked healthy. The author also noted that jaw swelling, weight loss or changes in chewing occur with various dental problems, so a vet has to find the actual cause. According to PetMD, examining the back teeth usually needs sedation and X-rays, and teeth must never be trimmed at home. If pain stops a chinchilla eating, gut stasis or infection can develop and become life-threatening within hours or days.</p>'),
                 ('Digestion', '<p>The RSPCA advises checking every day that your chinchilla eats and leaves plenty of dry droppings. If eating or drinking habits change, or droppings decrease or stop, contact a vet straight away: the chinchilla may be seriously ill. Diarrhoea and soft droppings are also a reason for a visit.</p>'),
                 ('Fur and skin', '<p>Fur loss can be a sign of illness or injury. The RSPCA also lists chewing its own or others’ fur, and patches of fur coming away when the chinchilla is handled, as signs of stress. Fur release is a defence response that can happen with rough handling. Without dust baths the fur becomes matted; we cover them in a separate article.</p>'),
                 ('Heat and humidity', '<p>Dense fur is an adaptation to cold, so heat and humidity are dangerous for chinchillas. Sources give slightly different ranges: the RSPCA recommends 10–18 °C in a dry, draught-free room, while PetMD gives roughly 13–21 °C, never above 27 °C, with humidity below 40–50% and no direct sun.</p>'),
                 ('Daily check', ul(
                     'Eyes and nose free of discharge, fur around the eyes and mouth dry.',
                     'The chinchilla eats and drinks, and droppings are normal and plentiful.',
                     'No bald patches, no skin changes.',
                     'No sore or injured feet, no limping.',
                     'No unusual swellings.',
                     'Stable weight: PetMD advises monitoring body weight.')),
             ],
             check=['when the chinchilla last ate normally', 'how many droppings a day and what they look like', 'weight over time', 'photos of the chin, teeth and fur', 'what you feed: hay, pellets, treats', 'room temperature'],
         )),
]

BY_SLUG = {a['slug']: a for a in ARTICLES}
LABEL = {
    'uk': {'rat': 'Щури', 'hamster': 'Хомʼяки', 'guinea-pig': 'Морські свинки', 'chinchilla': 'Шиншили', 'degu': 'Дегу', 'mouse': 'Миші', 'rabbit': 'Кролики'},
    'en': {'rat': 'Rats', 'hamster': 'Hamsters', 'guinea-pig': 'Guinea pigs', 'chinchilla': 'Chinchillas', 'degu': 'Degus', 'mouse': 'Mice', 'rabbit': 'Rabbits'},
}
TOPIC_EN = {'Симптоми': 'Symptoms', 'Харчування': 'Nutrition', 'Догляд': 'Care', 'Невідкладне': 'Urgent'}
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
INFO_URL = 'pro-materialy.html'


def en_date(iso):
    y, m, d = iso.split('-')
    return '%d %s %s' % (int(d), MONTHS_EN[int(m) - 1], y)


def date(iso, lang):
    return uk_date(iso) if lang == 'uk' else en_date(iso)


def text(a, lang):
    """The article's text fields in one language. English lives in a['en']."""
    return a if lang == 'uk' else a['en']


def has_en(slug):
    return slug == 'pro-materialy' or 'en' in BY_SLUG.get(slug, {})


def source_label(k, lang):
    s = S[k]
    if lang == 'en':
        assert len(s) > 2, 'source %s needs an English label' % k
        return s[2]
    return s[0]


def e(t):
    return html.escape(t, quote=True)


def photo_file(src, w):
    name = urllib.parse.unquote(src.split('/')[-1]).rsplit('.', 1)[0].lower()
    name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
    path = 'assets/blog/%s-%d.jpg' % (name, w)
    assert (ROOT / path).exists(), path
    return path


blog = (ROOT / 'blog.html').read_text(encoding='utf-8')
blog_en = (ROOT / 'en' / 'blog.html').read_text(encoding='utf-8')


def strip_reveal(x):
    x = re.sub(r'\sdata-reveal(="[^"]*")?', '', x)
    x = re.sub(r'\sdata-d="\d+"', '', x)
    return x.replace(' aria-current="page"', '')


def relink(x):
    """Ukrainian pages sit one folder down (blog/), so their relative links get '../'."""
    x = re.sub(r'(src|href)="(assets/|index\.html|blog\.html|privacy\.html|en/)', lambda m: '%s="../%s' % (m.group(1), m.group(2)), x)
    return strip_reveal(x)


def relink_en(x):
    """en/blog.html mostly uses root paths already; its few relative ones point into en/."""
    x = re.sub(r'(src|href)="(index|privacy|thank-you|blog)\.html', lambda m: '%s="/en/%s.html' % (m.group(1), m.group(2)), x)
    return strip_reveal(x)


def chrome(src, fix):
    nav_at = src.index('<nav data-reveal="down"')
    return {
        'dialog': fix(src[src.index('<dialog id="site-menu"'):src.index('</dialog>') + 9]),
        'nav': fix(src[nav_at:src.index('</nav>', nav_at) + 6]),
        'foot': fix(src[src.index('<footer id="early-access"'):src.index('</footer>') + 9]).replace('data-form="blog"', 'data-form="article"'),
    }


CHROME = {'uk': chrome(blog, relink), 'en': chrome(blog_en, relink_en)}
# Ukrainian pages live in blog/, English ones in en/blog/.
UP = {'uk': '../', 'en': '../../'}
DIR = {'uk': 'blog', 'en': 'en/blog'}
LOCALE = {'uk': 'uk_UA', 'en': 'en_US'}
OG_IMG = {'uk': 'assets/og-uk-v2.jpg', 'en': 'assets/og-en-v2.jpg'}
THANKS = {'uk': '../thank-you.html', 'en': '/en/thank-you.html'}
SKIP = {'uk': 'Перейти до змісту', 'en': 'Skip to content'}


def url_of(slug, lang):
    return '%s/%s/%s' % (BASE, DIR[lang], slug)


def page(lang, slug, title, desc, jsonld, main, img=None, og='article'):
    url = url_of(slug, lang)
    image = BASE + '/' + (img or OG_IMG[lang])
    up = UP[lang]
    nav = CHROME[lang]['nav']
    alternates = ''
    if has_en(slug):
        alternates = ('\n  <link rel="alternate" hreflang="uk" href="%s">\n  <link rel="alternate" hreflang="en" href="%s">'
                      '\n  <link rel="alternate" hreflang="x-default" href="%s">') % (url_of(slug, 'uk'), url_of(slug, 'en'), url_of(slug, 'uk'))
        # The language switch leads to the same article in the other language.
        if lang == 'uk':
            nav = nav.replace('href="../en/blog.html" class="lang-opt"', 'href="../en/blog/%s.html" class="lang-opt"' % slug)
        else:
            nav = nav.replace('href="/blog.html" class="lang-opt"', 'href="/blog/%s.html" class="lang-opt"' % slug)
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} | Roddi Health</title>
  <link rel="icon" type="image/svg+xml" href="{up}assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="{up}assets/apple-touch-icon.png">
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{url}">{alternates}
  <meta property="og:type" content="{og}">
  <meta property="og:site_name" content="Roddi Health">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:locale" content="{LOCALE[lang]}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700;800&family=Montserrat:wght@600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{up}assets/tailwind.css?v=1">
  <link rel="stylesheet" href="{up}assets/styles.css?v=3">
  <script src="{up}assets/lang-prompt.js?v=2"></script>
  <script src="{up}assets/clarity.js?v=3"></script>
  <link rel="stylesheet" href="{up}assets/theme.css">
  <link rel="stylesheet" href="{up}assets/app-home.css?v=47">
  <link rel="stylesheet" href="{up}assets/pages.css?v=5">
</head>
<body class="page-soft">
<a class="skip-link" href="#main">{SKIP[lang]}</a>
{CHROME[lang]['dialog']}
<header class="relative bg-white">
  {nav}
</header>
{main}
{CHROME[lang]['foot']}
<script>window.RODDI_THANKS = '{THANKS[lang]}';</script>
<script src="{up}assets/forms.js?v=2"></script>
<script src="{up}assets/menu.js?v=2"></script>
</body>
</html>
'''


T = {
    'uk': dict(
        note=('<p class="ar-note"><b>Довідковий матеріал.</b> Це загальна інформація з відкритих джерел, а не діагноз чи призначення, '
              'і вона не замінює консультації ветеринара. Перш ніж ухвалювати будь-яке рішення щодо здоровʼя тварини, порадьтеся з лікарем. '
              '<a href="%s">Як ми готуємо матеріали</a></p>' % INFO_URL),
        legal=('<p class="ar-legal">Roddi Health не є ветеринарною клінікою і не надає ветеринарних послуг. Матеріал має лише інформаційний характер, '
               'може бути неповним або застарілим і не замінює огляду лікаря. Ви самостійно приймаєте рішення щодо догляду за твариною. '
               'Назви джерел наведено для посилання: вони не писали й не схвалювали цей текст. '
               '<a href="%s">Докладніше про матеріали блогу</a>.</p>' % INFO_URL),
        alert=('<p class="ar-alert" role="note"><b>Якщо стан тварини погіршується, негайно звертайтеся до ветеринара.</b> '
               'Не відкладайте візит і не лікуйте тварину самостійно за статтею.</p>'),
        urgent_label='Коли потрібен ветеринар терміново', urgent_h='Терміново до ветеринара, якщо:',
        home='Головна', blog='Блог', crumbs='Навігація', short='Коротко',
        meta='Редакція Roddi Health · оновлено %s · огляд відкритих джерел',
        photo='Фото', check_h='Що записати перед дзвінком ветеринару',
        check_p='Такі нотатки легше вести в одному місці. Саме для цього ми робимо Roddi Health.', cta='Хочу ранній доступ',
        sources_h='Джерела',
        checked='Факти звірено з джерелами %s. Знайшли помилку чи посилання не відкривається? Напишіть на <a href="mailto:roddihealth@gmail.com">roddihealth@gmail.com</a>.',
        related_label='Схожі матеріали', related_h='Читайте також', author='Редакція Roddi Health',
        home_url='../index.html', blog_url='../blog.html', blog_ld=BASE + '/blog', home_ld=BASE + '/'),
    'en': dict(
        note=('<p class="ar-note"><b>Reference material.</b> This is general information from open sources, not a diagnosis or a prescription, '
              'and it does not replace a consultation with a vet. Talk to a vet before making any decision about your animal’s health. '
              '<a href="%s">How we prepare our articles</a></p>' % INFO_URL),
        legal=('<p class="ar-legal">Roddi Health is not a veterinary clinic and does not provide veterinary services. This article is for information only, '
               'may be incomplete or out of date, and does not replace an examination by a vet. You make your own decisions about caring for your animal. '
               'Sources are named for reference: they did not write or endorse this text. '
               '<a href="%s">More about our blog articles</a>.</p>' % INFO_URL),
        alert=('<p class="ar-alert" role="note"><b>If your animal’s condition gets worse, see a vet straight away.</b> '
               'Don’t put off the visit and don’t treat your pet yourself based on this article.</p>'),
        urgent_label='When a vet is needed urgently', urgent_h='See a vet urgently if:',
        home='Home', blog='Blog', crumbs='Breadcrumbs', short='In short',
        meta='Roddi Health editorial team · updated %s · overview of open sources',
        photo='Photo', check_h='What to note down before you call the vet',
        check_p='Notes like these are easier to keep in one place. That’s what we’re building Roddi Health for.', cta='Get early access',
        sources_h='Sources',
        checked='Facts checked against the sources on %s. Found a mistake or a link that doesn’t open? Write to <a href="mailto:roddihealth@gmail.com">roddihealth@gmail.com</a>.',
        related_label='Related articles', related_h='Read next', author='Roddi Health editorial team',
        home_url='/en/index.html', blog_url='/en/blog.html', blog_ld=BASE + '/en/blog', home_ld=BASE + '/en/'),
}


def article(a, lang):
    t, x = T[lang], text(a, lang)
    url = url_of(a['slug'], lang)
    ph = P[a['photo']]
    img = photo_file(ph['src'], 960)
    pos = ph.get('pos', '50% 50%')
    published, updated, checked = a.get('published', PUBLISHED), a.get('updated', UPDATED), a.get('checked', CHECKED)
    alert = t['alert'] if a.get('alert', a['topic'] in ALERT_TOPICS) else ''
    urgent = ''
    if x.get('urgent'):
        urgent = '<aside class="ar-urgent" aria-label="%s"><h2>%s</h2>' % (t['urgent_label'], t['urgent_h']) + ul(*x['urgent']) + '</aside>'
    body = ''.join('<h2>%s</h2>%s' % (h, c) for h, c in x['sections'])
    check = ''.join('<li>%s</li>' % c for c in x['check'])
    sources = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (e(S[k][1]), e(source_label(k, lang))) for k in a['sources'])
    rel = [r for r in a['related'] if lang == 'uk' or has_en(r)]
    topic = a['topic'] if lang == 'uk' else TOPIC_EN[a['topic']]
    related = ''.join('<a href="%s.html" class="ar-rel"><span>%s</span><b>%s</b></a>'
                      % (r, e(BY_SLUG[r]['topic'] if lang == 'uk' else TOPIC_EN[BY_SLUG[r]['topic']]), e(text(BY_SLUG[r], lang)['title'])) for r in rel)
    related_sec = '<section class="ar-related" aria-label="%s"><h2>%s</h2><div>%s</div></section>' % (t['related_label'], t['related_h'], related) if rel else ''
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BlogPosting', 'headline': x['title'], 'description': x['desc'], 'image': [BASE + '/' + img],
         'datePublished': published, 'dateModified': updated, 'inLanguage': lang, 'mainEntityOfPage': url,
         'author': {'@type': 'Organization', 'name': t['author'], 'url': url_of('pro-materialy', lang)},
         'publisher': {'@type': 'Organization', 'name': 'Roddi Health', 'url': BASE + '/', 'logo': {'@type': 'ImageObject', 'url': BASE + '/assets/favicon-32.png'}},
         'citation': [S[k][1] for k in a['sources']]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['home'], 'item': t['home_ld']},
            {'@type': 'ListItem', 'position': 2, 'name': t['blog'], 'item': t['blog_ld']},
            {'@type': 'ListItem', 'position': 3, 'name': x['title']}]},
    ]}
    main = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="{t['crumbs']}"><a href="{t['home_url']}">{t['home']}</a><span aria-hidden="true">/</span><a href="{t['blog_url']}">{t['blog']}</a><span aria-hidden="true">/</span><b>{e(LABEL[lang][a['rodent']])}</b></nav>
  <h1 class="t-h1">{e(x['title'])}</h1>
  <p class="ar-meta">{t['meta'] % date(updated, lang)}</p>
  <div class="ar-short soft-grad soft-grad--ask"><p class="ar-short-l">{t['short']}</p><p>{e(x['short'])}</p></div>
  {alert}
  {t['note']}
  <figure class="ar-fig"><img alt="{e(x['title'])}" src="{UP[lang]}{img}" width="960" height="540" style="object-position:{pos}"><figcaption>{t['photo']}: <a href="{e(ph['page'])}" target="_blank" rel="noopener">{e(ph['by'])}</a>, {e(ph['lic'])}, Wikimedia Commons</figcaption></figure>
  {urgent}
  <div class="ar-body">{body}</div>
  <section class="ar-check"><h2>{t['check_h']}</h2><ul>{check}</ul><p>{t['check_p']}</p><a href="#early-access" class="btn-app btn-app-sm">{t['cta']}</a></section>
  <section class="ar-sources"><h2>{t['sources_h']}</h2><ul>{sources}</ul><p class="ar-checked">{t['checked'] % date(checked, lang)}</p></section>
  {t['legal']}
  {related_sec}
</main>
'''
    return page(lang, a['slug'], x['seo'], x['desc'], ld, main, img)


INFO_TITLE = 'Про матеріали блогу та відмова від відповідальності'
INFO_DESC = 'Як Roddi Health готує матеріали блогу: які джерела обирає, як позначає чужі статті й дату перевірки фактів, обмеження інформації та як повідомити про помилку.'
INFO_UPDATED = '2026-11-16'
info_ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': INFO_TITLE, 'description': INFO_DESC, 'url': BASE + '/blog/pro-materialy', 'inLanguage': 'uk', 'dateModified': INFO_UPDATED}
info_main = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="Навігація"><a href="../index.html">Головна</a><span aria-hidden="true">/</span><a href="../blog.html">Блог</a><span aria-hidden="true">/</span><b>Про матеріали</b></nav>
  <h1 class="t-h1">{e(INFO_TITLE)}</h1>
  <p class="ar-meta">Оновлено {uk_date(INFO_UPDATED)}</p>
  <div class="ar-body">
    <h2>Як ми готуємо статті</h2>
    <p>Статті блогу є власними оглядами редакції Roddi Health українською. Ми читаємо матеріали ветеринарів, ветеринарних організацій, університетів і зоозахисних організацій, зіставляємо їх і викладаємо факти своїми словами у власній структурі. Там, де джерела розходяться, ми це показуємо.</p>
    <p>Ми не копіюємо, не перекладаємо й не переказуємо абзац за абзацом чужі статті. Факти беремо з кількох джерел і під кожною статтею даємо їх перелік із прямими посиланнями.</p>
    <p>У підготовці текстів ми використовуємо інструменти на основі ШІ. Статті не є рецензованими ветеринарними публікаціями, якщо це не зазначено окремо біля конкретної статті.</p>
    <h2>Які джерела ми обираємо</h2>
    <p>Насамперед ми спираємося на ветеринарні асоціації й довідники, університети, державні й профільні організації та рецензовані наукові статті. Матеріали зоозахисних організацій і ветеринарних клінік використовуємо як додаткові. Якщо твердження не вдається перевірити за джерелом, ми його не публікуємо.</p>
    <h2>Ліки й дози</h2>
    <p>Ми не наводимо дози ліків і не радимо препарати. Призначити лікування може лише ветеринар, який оглянув тварину.</p>
    <h2>Дата перевірки</h2>
    <p>У кожній статті вказано, коли факти востаннє звіряли з джерелами. Ми переглядаємо матеріали, коли змінюються рекомендації або коли нам повідомляють про помилку чи посилання, що не відкривається.</p>
    <h2>Симптоми й невідкладні стани</h2>
    <p>Статті про симптоми й невідкладні стани мають помітне попередження: якщо стан тварини погіршується, негайно звертайтеся до ветеринара. Такі статті допомагають зрозуміти, що відбувається й що розповісти лікарю, але не дають змоги поставити діагноз удома.</p>
    <h2>Статті на сторонніх сайтах</h2>
    <p>Частина карток у блозі поки веде на статті інших сайтів. Такі картки позначені написом «стаття на сторонньому сайті», а їхній текст є нашим коротким описом, а не цитатою. Ми поступово замінюємо їх власними оглядами.</p>
    <h2>Це не ветеринарна консультація</h2>
    <p>Roddi Health не є ветеринарною клінікою і не надає ветеринарних послуг. Матеріали блогу мають лише інформаційний характер і не є діагнозом, планом лікування чи рекомендацією щодо ліків або доз. Вони не замінюють огляду ветеринара.</p>
    <p>Перш ніж ухвалювати будь-яке рішення щодо здоровʼя тварини, порадьтеся з ветеринаром і самостійно перевірте інформацію. Якщо тварині погано, не відкладайте звернення через прочитане на сайті.</p>
    <h2>Обмеження</h2>
    <p>Ми намагаємося підтримувати матеріали точними, але не гарантуємо, що вони повні, актуальні чи підходять саме вашій тварині. Рекомендації змінюються, а джерела можуть не збігатися. Ви самостійно приймаєте рішення щодо догляду за твариною. У межах, дозволених законом, Roddi Health не відповідає за наслідки використання цієї інформації.</p>
    <h2>Згадані джерела</h2>
    <p>Назви організацій і сайтів наведено лише для посилання. Вони не повʼязані з Roddi Health, не писали й не схвалювали наші тексти. За вміст зовнішніх сайтів відповідають їхні власники.</p>
    <h2>Фото й авторські права</h2>
    <p>Фотографії в блозі взято з Wikimedia Commons і мають вільні ліцензії. Біля кожного фото вказано автора, ліцензію й посилання на файл.</p>
    <h2>Помилки й звернення</h2>
    <p>Якщо ви знайшли помилку або вважаєте, що матеріал порушує ваші права, напишіть на <a href="mailto:roddihealth@gmail.com">roddihealth@gmail.com</a>: ми перевіримо й виправимо або приберемо його.</p>
  </div>
</main>
'''

INFO_TITLE_EN = 'About our blog articles and disclaimer'
INFO_DESC_EN = 'How Roddi Health prepares its blog articles: which sources we use, how we mark other sites’ articles and fact-check dates, the limits of the information and how to report a mistake.'
info_ld_en = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': INFO_TITLE_EN, 'description': INFO_DESC_EN, 'url': BASE + '/en/blog/pro-materialy', 'inLanguage': 'en', 'dateModified': INFO_UPDATED}
info_main_en = f'''<main id="main" class="ar">
  <nav class="ar-crumb" aria-label="Breadcrumbs"><a href="/en/index.html">Home</a><span aria-hidden="true">/</span><a href="/en/blog.html">Blog</a><span aria-hidden="true">/</span><b>About our articles</b></nav>
  <h1 class="t-h1">{e(INFO_TITLE_EN)}</h1>
  <p class="ar-meta">Updated {en_date(INFO_UPDATED)}</p>
  <div class="ar-body">
    <h2>How we prepare articles</h2>
    <p>Our blog articles are original overviews written by the Roddi Health editorial team. We read material from vets, veterinary organisations, universities and animal welfare organisations, compare it and set out the facts in our own words and our own structure. Where sources disagree, we show it.</p>
    <p>We do not copy, translate or retell other articles paragraph by paragraph. We take facts from several sources and list them under each article with direct links. Our articles are written in Ukrainian first; the English versions are our own translations of our own texts.</p>
    <p>We use AI-based tools when preparing texts. Articles are not peer-reviewed veterinary publications unless this is stated next to a specific article.</p>
    <h2>Which sources we choose</h2>
    <p>We rely first on veterinary associations and reference works, universities, government and specialist bodies, and peer-reviewed research. Material from animal welfare organisations and veterinary clinics is used as a supplement. If we cannot check a statement against a source, we do not publish it.</p>
    <h2>Medicines and doses</h2>
    <p>We do not give medicine doses or recommend medicines. Only a vet who has examined the animal can prescribe treatment.</p>
    <h2>Fact-check date</h2>
    <p>Each article shows when its facts were last checked against the sources. We review articles when recommendations change or when someone reports a mistake or a broken link.</p>
    <h2>Symptoms and emergencies</h2>
    <p>Articles about symptoms and emergencies carry a visible notice: if your animal’s condition gets worse, see a vet straight away. These articles help you understand what may be happening and what to tell the vet, but they do not let you diagnose your animal at home.</p>
    <h2>Articles on other sites</h2>
    <p>Some cards in the blog still lead to articles on other websites. They are marked “article on an external site”, and their text is our own short description, not a quotation. We are gradually replacing them with our own overviews.</p>
    <h2>This is not veterinary advice</h2>
    <p>Roddi Health is not a veterinary clinic and does not provide veterinary services. Blog articles are for information only and are not a diagnosis, a treatment plan or a recommendation about medicines or doses. They do not replace an examination by a vet.</p>
    <p>Before making any decision about your animal’s health, talk to a vet and check the information yourself. If your animal is unwell, don’t delay getting help because of something you read on this site.</p>
    <h2>Limitations</h2>
    <p>We try to keep our articles accurate, but we do not guarantee that they are complete, up to date or suitable for your animal. Recommendations change and sources may disagree. You make your own decisions about caring for your animal. To the extent permitted by law, Roddi Health is not responsible for the consequences of using this information.</p>
    <h2>Sources we mention</h2>
    <p>Organisations and websites are named for reference only. They are not affiliated with Roddi Health and did not write or endorse our texts. The owners of external websites are responsible for their content.</p>
    <h2>Photos and copyright</h2>
    <p>Blog photos come from Wikimedia Commons and have free licences. Each photo shows its author, licence and a link to the file.</p>
    <h2>Mistakes and requests</h2>
    <p>If you find a mistake or believe that something on the blog infringes your rights, write to <a href="mailto:roddihealth@gmail.com">roddihealth@gmail.com</a>: we will check it and correct or remove it.</p>
  </div>
</main>
'''

for lang in ('uk', 'en'):
    (ROOT / DIR[lang]).mkdir(parents=True, exist_ok=True)
for a in ARTICLES:
    (ROOT / 'blog' / (a['slug'] + '.html')).write_text(article(a, 'uk'), encoding='utf-8')
    if 'en' in a:
        (ROOT / 'en' / 'blog' / (a['slug'] + '.html')).write_text(article(a, 'en'), encoding='utf-8')
(ROOT / 'blog' / 'pro-materialy.html').write_text(page('uk', 'pro-materialy', INFO_TITLE, INFO_DESC, info_ld, info_main, og='website'), encoding='utf-8')
(ROOT / 'en' / 'blog' / 'pro-materialy.html').write_text(page('en', 'pro-materialy', INFO_TITLE_EN, INFO_DESC_EN, info_ld_en, info_main_en, og='website'), encoding='utf-8')

# Data for the cards on blog.html and en/blog.html.
cards = [{'rodent': a['rodent'], 'topic': a['topic'], 'title': a['title'], 'excerpt': a['short'], 'tags': a['tags'],
          'source': 'Roddi Health', 'url': 'blog/%s.html' % a['slug'], 'internal': True, 'featured': bool(a.get('featured')), 'photo': P[a['photo']]} for a in ARTICLES]
(ROOT / 'assets/blog-articles.js').write_text('/* Built by tools/build-articles.py. Do not edit by hand. */\nvar BLOG_ARTICLES = ' + json.dumps(cards, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')
cards_en = [{'rodent': a['rodent'], 'topic': TOPIC_EN[a['topic']], 'title': a['en']['title'], 'excerpt': a['en']['short'], 'tags': a['en']['tags'],
             'source': 'Roddi Health', 'url': '/en/blog/%s.html' % a['slug'], 'internal': True, 'featured': bool(a.get('featured')), 'photo': P[a['photo']]}
            for a in ARTICLES if 'en' in a]
(ROOT / 'assets/blog-articles.en.js').write_text('/* Built by tools/build-articles.py. Do not edit by hand. */\nvar BLOG_ARTICLES = ' + json.dumps(cards_en, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')

# Links for crawlers that do not run the page's script.
static = '<!-- articles:start -->' + ''.join(
    '<article class="blog-static"><h3><a href="blog/%s.html">%s</a></h3><p>%s</p></article>' % (a['slug'], e(a['title']), e(a['short'])) for a in ARTICLES) + '<!-- articles:end -->'
if '<!-- articles:start -->' in blog:
    blog = re.sub(r'<!-- articles:start -->.*?<!-- articles:end -->', lambda m: static, blog, flags=re.S)
else:
    assert blog.count('<!-- posts:start -->') == 1
    blog = blog.replace('<!-- posts:start -->', static + '<!-- posts:start -->')
(ROOT / 'blog.html').write_text(blog, encoding='utf-8')

# Sitemap.
sm = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
sm = re.sub(r'\s*<!-- articles:start -->.*?<!-- articles:end -->', '', sm, flags=re.S)
pages = [(a['slug'], a.get('updated', UPDATED)) for a in ARTICLES] + [('pro-materialy', INFO_UPDATED)]
urls = ''.join('\n  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (url_of(s, lang), d)
               for lang in ('uk', 'en') for s, d in pages if lang == 'uk' or has_en(s))
sm = sm.replace('</urlset>', '  <!-- articles:start -->' + urls + '\n  <!-- articles:end -->\n</urlset>')
(ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
print('built', len(ARTICLES), 'articles,', len(cards_en), 'in English')
