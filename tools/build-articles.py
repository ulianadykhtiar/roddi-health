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
    'degu2': {'src': '6/69/Octodon_degus_209581281.jpg', 'by': 'Ben Lyle Bedard', 'lic': 'CC BY 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Octodon_degus_209581281.jpg'},
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
    'petmd_gp': ('PetMD: памʼятка з догляду за морськими свинками', 'https://www.petmd.com/exotic/guinea-pig-care-sheet', 'PetMD: guinea pig care sheet'),
    'spca_c': ('SPCA New Zealand: вітамін C для морських свинок', 'https://spca.nz/advice-and-welfare/article/why-is-vitamin-c-important-for-my-guinea-pigs'),
    'petmd_gi_r': ('PetMD: стаз ШКТ у кроликів', 'https://www.petmd.com/rabbit/conditions/digestive/gastrointestinal-gi-stasis-rabbits'),
    'walker_r': ('Walkerville Vet: кролик не їсть', 'https://www.walkervillevet.com.au/blog/rabbit-not-eating/'),
    'exotic_d': ('Exotic Direct: чим годувати дегу', 'https://exoticdirect.co.uk/news/degu-food-advice-what-your-degu-should-be-eating-not-eating-diabetes-and-other-advice/'),
    'petmd_d': ('PetMD: догляд за дегу', 'https://www.petmd.com/exotic/care/caring-for-a-degu', 'PetMD: caring for a degu'),
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
    # Sources for the guinea pig and degu articles (PR 3).
    'rspca_gp': ('RSPCA: морські свинки як домашні тварини', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/guineapigs', 'RSPCA: keeping guinea pigs as pets'),
    'rspca_gp_diet': ('RSPCA: чим годувати морську свинку', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/guineapigs/diet', 'RSPCA: what to feed a guinea pig'),
    'rspca_gp_env': ('RSPCA: житло для морських свинок', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/guineapigs/environment', 'RSPCA: creating a good home for guinea pigs'),
    'rspca_gp_company': ('RSPCA: як тримати морських свинок разом', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/guineapigs/company', 'RSPCA: keeping guinea pigs together'),
    'rspca_gp_health': ('RSPCA: здоровʼя морських свинок', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/guineapigs/health', 'RSPCA: guinea pig health and welfare'),
    'pdsa_gp': ('PDSA: морські свинки як домашні тварини', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/guinea-pigs-as-pets', 'PDSA: guinea pigs as pets'),
    'pdsa_gp_diet': ('PDSA: раціон морської свинки', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/your-guinea-pig-s-diet', 'PDSA: your guinea pig’s diet'),
    'pdsa_gp_home': ('PDSA: ідеальне житло для морських свинок', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/the-ideal-home-for-your-guinea-pig', 'PDSA: the ideal home for your guinea pigs'),
    'pdsa_gp_health': ('PDSA: здоровʼя морських свинок', 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/guinea-pig-health', 'PDSA: guinea pig health'),
    'rspcaau_gp_keep': ('RSPCA Australia: де тримати морських свинок', 'https://kb.rspca.org.au/categories/companion-animals/other-pets/guinea-pigs/where-should-i-keep-my-guinea-pigs', 'RSPCA Australia: where should I keep my guinea pigs?'),
    'petmd_gp_vitc': ('PetMD: нестача вітаміну C у морських свинок', 'https://www.petmd.com/exotic/conditions/cardiovascular/c_ex_gp_vitamin_c_deficiency', 'PetMD: vitamin C deficiency in guinea pigs'),
    'improve_vitc': ('Improve International: морські свинки й проблема вітаміну C', 'https://improveinternational.com/uk/clinical-library/guinea-pigs-and-the-vitamin-c-problem', 'Improve International: guinea pigs and the vitamin C problem'),
    'rspca_degu': ('RSPCA: дегу як домашні тварини', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus', 'RSPCA: keeping degus as pets'),
    'rspca_degu_env': ('RSPCA: житло для дегу', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus/environment', 'RSPCA: a good home for degus'),
    'rspca_degu_diet': ('RSPCA: чим годувати дегу', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus/diet', 'RSPCA: what to feed degus'),
    'rspca_degu_health': ('RSPCA: здоровʼя дегу', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus/health', 'RSPCA: degu health and welfare'),
    'rspca_degu_company': ('RSPCA: як тримати дегу разом', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus/company', 'RSPCA: keeping degus together'),
    'rspca_degu_behaviour': ('RSPCA: поведінка дегу', 'https://www.rspca.org.uk/adviceandwelfare/pets/rodents/degus/behaviour', 'RSPCA: degu behaviour'),
    'pdsa_degu': ('PDSA: дегу як домашні тварини', 'https://pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/ideal-environment-for-degus', 'PDSA: degus as pets'),
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
             desc='How to set up a home for pet mice, which bedding to use, how often to clean, what to feed and why mice should not live alone. Advice from the RSPCA, PDSA and others.',
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
             seo='Chinchilla health: teeth, fur, digestion, when to see a vet',
             desc='Why a chinchilla’s teeth never stop growing, how to spot dental problems, what changes in droppings and fur mean, safe temperatures and when to see a vet.',
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
    # ---- Guinea pigs and degus (PR 3, 16 November 2026) ----
    dict(slug='tsynga-u-morskoi-svynky', rodent='guinea-pig', topic='Симптоми', photo='gp',
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Цинга в морської свинки: ознаки нестачі вітаміну C і профілактика',
         seo='Цинга в морської свинки: симптоми й коли до ветеринара',
         desc='Чому морська свинка не може жити без вітаміну C з їжею, як проявляється його нестача, чому корм із часом втрачає вітамін і що зробить ветеринар.',
         short='Морські свинки не синтезують вітамін C самі, тож мають щодня отримувати його з їжею. За PetMD, ознаки нестачі можуть зʼявитися вже через 2–3 тижні неповноцінного раціону: гіршають шерсть, апетит і вага, рани довго гояться, тварині боляче рухатися. Причину визначає й лікування призначає ветеринар.',
         tags='цинга вітамін с нестача шерсть суглоби кульгає не їсть гранули перець добавки',
         urgent=['свинка не їсть або посліду поменшало чи немає', 'не хоче рухатися, кульгає, болять суглоби', 'утруднене дихання', 'сильна діарея', 'різка млявість, згорблена поза'],
         sections=[
             ('Чому вітамін C має бути в їжі', '<p>На відміну від більшості тварин, морські свинки не мають ферменту, потрібного для синтезу вітаміну C, тож отримують його лише з їжею. Вітамін C потрібен, зокрема, для утворення колагену. PDSA попереджає, що без нього свинці загрожує цинга.</p>'),
             ('Як проявляється нестача', '<p>PetMD, стаття якого написана ветеринаром, називає такі ознаки:</p>' + ul(
                 'груба, тьмяна чи нерівна шерсть',
                 'млявість і пригнічений вигляд',
                 'гірший апетит, схуднення, а в молодих свинок слабкий набір ваги',
                 'рани гояться повільно, свинка частіше хворіє на інфекції',
                 'проблеми із зубами й біль під час жування',
                 'діарея',
                 'біль у кістках і суглобах, набряклі суглоби: свинка неохоче рухається чи кульгає')
              + '<p>У важких випадках нестача може призвести до переломів, паралічу, сепсису й загибелі тварини. Багато з цих ознак бувають і за інших хвороб, тому причину визначає ветеринар.</p>'),
             ('Як швидко це стається', '<p>За PetMD, ознаки нестачі можуть зʼявитися вже через 2–3 тижні раціону, у якому замало вітаміну C. Найчастіші причини: мало свіжих овочів, немає збагаченого корму або корм і ласощі застаріли.</p>'),
             ('Свіжі овочі щодня', '<p>RSPCA називає свіжі овочі й зелень чудовим джерелом вітаміну C. Серед того, що можна давати часто, організація згадує болгарський перець, огірок, селеру, ромен і петрушку. PetMD до продуктів, багатих на вітамін C, відносить червоний і зелений перець, брокколі, цвітну капусту, полуницю й ківі.</p>'
              + '<p>Щодо зелені з високим вмістом кальцію джерела розходяться. RSPCA дає капусту кале й шпинат лише як ласощі кілька разів на тиждень. Памʼятка PetMD радить уникати петрушки, шпинату, кале й кульбаби через ризик каменів, а стаття PetMD про вітамін C називає кале й петрушку його джерелами. Якщо сумніваєтеся, порадьтеся з ветеринаром.</p>'),
             ('Гранули втрачають вітамін', ul(
                 'Обирайте гранули саме для морських свинок, на основі трав і збагачені вітаміном C.',
                 'Вітамін C у кормі з часом руйнується, швидше на теплі, світлі й повітрі.',
                 'PDSA радить зберігати гранули в сухому, прохолодному й темному місці та використати протягом трьох місяців після купівлі. За памʼяткою PetMD, вміст вітаміну різко падає через три місяці після дати виробництва.',
                 'RSPCA радить щодня давати свіжу порцію гранул, а не досипати до старої, і не годувати кормом після кінця терміну придатності.')),
             ('Вітамін у воді й добавки', '<p>Вітамін C у питній воді — ненадійний спосіб: він швидко руйнується, а PetMD пише, що такі добавки діють менше доби. PDSA не радить додавати вітамін у воду ще й тому, що через смак свинка може менше пити.</p>'
              + '<p>За PDSA, якщо свинка щодня отримує збалансований раціон зі свіжою зеленню, окремі добавки не потрібні. Надлишок вітаміну теж може шкодити: Improve International, видання для ветеринарів, повʼязує надмірне його вживання з каменями в сечовій системі й проблемами із суглобами. Тому добавки варто обговорити з ветеринаром.</p>'),
             ('Що зробить ветеринар', '<p>За PetMD, ветеринар оглядає свинку й розпитує про раціон, інколи робить рентген чи аналіз крові. Часто достатньо виправити раціон, а у важких випадках лікар сам призначає вітамін. Зміни зубів можуть лишитися надовго.</p>'),
         ],
         check=['чим годуєте й скільки свіжих овочів щодня', 'дата виробництва й відкриття пачки гранул', 'чи даєте добавки, які саме й як', 'вага в динаміці', 'відео того, як свинка рухається'],
         sources=['petmd_gp_vitc', 'petmd_gp', 'pdsa_gp_diet', 'rspca_gp_diet', 'rspca_gp_health', 'improve_vitc'],
         related=['chym-goduvaty-morsku-svynku', 'dohliad-za-morskoiu-svynkoiu'],
         en=dict(
             title='Scurvy in guinea pigs: signs of vitamin C deficiency and prevention',
             seo='Scurvy in guinea pigs: symptoms and when to see a vet',
             desc='Why a guinea pig needs vitamin C from its food, how a deficiency shows, why pellets lose vitamin C over time and what a vet will do.',
             short='Guinea pigs can’t make vitamin C themselves, so they need it from food every day. According to PetMD, signs of deficiency can appear after just 2–3 weeks of a poor diet: the coat, appetite and weight get worse, wounds heal slowly and moving becomes painful. A vet finds the cause and prescribes treatment.',
             tags='scurvy vitamin c deficiency coat joints limping not eating pellets pepper supplements',
             urgent=['the guinea pig is not eating, or there are fewer or no droppings', 'it doesn’t want to move, limps or has painful joints', 'difficulty breathing', 'severe diarrhoea', 'sudden lethargy, hunched posture'],
             sections=[
                 ('Why vitamin C must come from food', '<p>Unlike most animals, guinea pigs lack the enzyme needed to make vitamin C, so they get it only from food. Vitamin C is needed, among other things, to make collagen. PDSA warns that without it a guinea pig is at risk of scurvy.</p>'),
                 ('How a deficiency shows', '<p>PetMD, in an article written by a vet, lists these signs:</p>' + ul(
                     'a rough, dull or patchy coat',
                     'lethargy and a depressed look',
                     'poor appetite and weight loss, or poor weight gain in young animals',
                     'wounds heal slowly and infections become more frequent',
                     'dental problems and pain when chewing',
                     'diarrhoea',
                     'bone and joint pain, swollen joints: the guinea pig is reluctant to move or limps')
                  + '<p>In severe cases a deficiency can lead to fractures, paralysis, sepsis and death. Many of these signs also occur with other diseases, so a vet has to find the cause.</p>'),
                 ('How quickly it happens', '<p>According to PetMD, signs can appear after just 2–3 weeks of a diet that is too low in vitamin C. The most common reasons are too little fresh produce, no fortified food, or food and treats that are too old.</p>'),
                 ('Fresh vegetables every day', '<p>The RSPCA calls fresh vegetables and herbs an excellent source of vitamin C. Among foods that can be given often, it lists bell peppers, cucumber, celery, romaine lettuce and parsley. PetMD lists red and green peppers, broccoli, cauliflower, strawberries and kiwi among foods rich in vitamin C.</p>'
                  + '<p>Sources disagree about high-calcium greens. The RSPCA gives kale and spinach only as treats a few times a week. PetMD’s care sheet advises avoiding parsley, spinach, kale and dandelion because of the risk of stones, while PetMD’s vitamin C article lists kale and parsley as good sources. If in doubt, ask your vet.</p>'),
                 ('Pellets lose vitamin C', ul(
                     'Choose pellets made for guinea pigs, grass-based and fortified with vitamin C.',
                     'Vitamin C in food breaks down over time, faster with heat, light and air.',
                     'PDSA advises storing pellets somewhere dry, cool and dark and using them within three months of purchase. According to PetMD’s care sheet, vitamin C levels drop sharply three months after the production date.',
                     'The RSPCA advises giving a fresh portion of pellets daily instead of topping up the old one, and not feeding food past its best-before date.')),
                 ('Vitamin C in water and supplements', '<p>Vitamin C in drinking water is unreliable: it breaks down quickly, and PetMD says such additives last less than a day. PDSA advises against adding it to water also because the taste can make a guinea pig drink less.</p>'
                  + '<p>According to PDSA, a guinea pig that gets a balanced diet with fresh greens every day does not need separate supplements. Too much vitamin C can also do harm: Improve International, a publisher for vets, links excessive amounts with urinary stones and joint problems. So it is worth discussing supplements with your vet.</p>'),
                 ('What a vet will do', '<p>According to PetMD, the vet examines the guinea pig and asks about its diet, and sometimes takes X-rays or a blood test. Correcting the diet is often enough, and in severe cases the vet prescribes vitamin C. Dental changes can last a long time.</p>'),
             ],
             check=['what you feed and how much fresh produce a day', 'the production date and opening date of the pellet bag', 'whether you give supplements, which ones and how', 'weight over time', 'a video of how the guinea pig moves'],
         )),
    dict(slug='dohliad-za-morskoiu-svynkoiu', rodent='guinea-pig', topic='Догляд', photo='gp2',
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Базовий догляд за морськими свинками: сіно, корм, житло й компанія',
         seo='Як доглядати за морською свинкою: раціон, клітка, компанія',
         desc='Скільки сіна, гранул і овочів потрібно морській свинці, яким має бути житло, з ким вона може жити й що перевіряти щодня. Огляд порад RSPCA, PDSA та PetMD.',
         short='Основа раціону морської свинки — необмежене сіно й трава. До них додають трохи гранул для свинок, щодня свіжі овочі й чисту воду. Свинки соціальні й живуть парами чи групами. Їм потрібне просторе житло із суцільною підлогою, схованками й місцем для руху.',
         tags='сіно гранули овочі вода клітка вольєр підстилка прибирання компанія кастрація температура',
         sections=[
             ('Сіно і трава', '<p>Сіно має становити більшу частину раціону й бути доступним постійно. PDSA оцінює його частку у 85–90%, PetMD — приблизно у 80%. RSPCA радить якомога частіше, в ідеалі щодня, давати свіжу траву. Скошена газонокосаркою трава небезпечна, її не дають.</p>'),
             ('Гранули', '<p>Обирайте однорідні гранули саме для морських свинок, на основі трав, а не суміші на кшталт мюслі. PDSA радить приблизно одну столову ложку на дорослу свинку на день, RSPCA — порцію за інструкцією виробника, щодня свіжу.</p>'),
             ('Овочі й фрукти', '<p>PDSA радить приблизно чашку овочів на свинку на день, 5–6 різних видів, серед них багаті на вітамін C. RSPCA серед того, що можна давати часто, називає болгарський перець, огірок, селеру, ромен і петрушку, а брокколі, шпинат, кале, моркву й четвертинку яблука — як ласощі кілька разів на тиждень. Фрукти через цукор дають зрідка. Нові продукти вводьте поступово.</p>'
              + '<p>Не давайте салат айсберг, картоплю, цибулю, часник, гриби, авокадо, ревінь, шоколад, хліб і печиво, горіхи й зерно.</p>'),
             ('Вода', '<p>Свіжа чиста вода має бути завжди. RSPCA радить перевіряти її двічі на день, а взимку стежити, щоб вона не замерзала. Миску чи поїлку мийте щодня.</p>'),
             ('Житло', '<p>Джерела дають різні мінімальні розміри:</p>' + table(['Джерело', 'Мінімум'], [
                 ['PetMD', 'клітка приблизно 91 × 76 × 46 см'],
                 ['PDSA', 'будиночок щонайменше 1,5 × 1 м і вольєр щонайменше 2 × 1 м'],
                 ['RSPCA Australia', 'для пари щонайменше 2 × 0,5 м, висота не менше 30 см'],
             ]) + '<p>Усі сходяться в тому, що більше краще. Підлога має бути суцільною, без сітки. RSPCA радить мати схованок на одну більше, ніж свинок, а ще щодня давати свинкам місце для руху. PetMD радить щонайменше годину на день поза кліткою.</p>'),
             ('Температура', '<p>RSPCA називає комфортною кімнатну температуру 17–20 °C. Вище 26 °C зростає ризик теплового удару, нижче 15 °C свинка може переохолодитися. PDSA попереджає про тепловий удар вище 27 °C. Не ставте житло біля батарей, сонячних вікон і на протязі.</p>'),
             ('Підстилка й прибирання', '<p>Підходять безпилове сіно чи паперова підстилка, вату не використовують. Щодо деревної стружки джерела розходяться, тож паперова підстилка — безпечніший вибір. Щодня прибирайте мокру підстилку й залишки свіжої їжі, а раз на тиждень робіть ґрунтовне прибирання.</p>'),
             ('Компанія', '<p>RSPCA радить тримати свинку щонайменше з однією дружньою свинкою, якщо ветеринар не порадив інакше. Добре уживаються кастрований самець з однією чи кількома самками, дві самки, брати, які росли разом. Самця, що живе із самками, обовʼязково каструють: за PDSA, самки можуть завагітніти вже приблизно з трьох тижнів. Кролик не компанія для свинки, тримати їх разом не радять.</p>'),
             ('Огляди', ul(
                 'Щодня оглядайте свинку: обличчя й очі, шерсть, задню частину тіла, лапи.',
                 'Раз на тиждень перевіряйте передні зуби й кігті. Зуби, що переросли, виправляє лише ветеринар.',
                 'У спеку двічі на день оглядайте задню частину тіла: забруднена шерсть приваблює мух.',
                 'Щонайменше раз на рік показуйте свинку ветеринару.',
                 'Якщо змінилися харчування, пиття чи послід або послід зник, одразу звертайтеся до ветеринара. Утруднене дихання — невідкладний стан.')),
         ],
         check=['скільки свинок і якої статі живуть разом', 'розмір житла', 'чим годуєте й скільки', 'температура в кімнаті', 'вага в динаміці'],
         sources=['rspca_gp', 'rspca_gp_diet', 'rspca_gp_env', 'rspca_gp_company', 'rspca_gp_health', 'pdsa_gp', 'pdsa_gp_diet', 'pdsa_gp_home', 'pdsa_gp_health', 'rspcaau_gp_keep', 'petmd_gp'],
         related=['tsynga-u-morskoi-svynky', 'morska-svynka-ne-yist'],
         en=dict(
             title='Basic guinea pig care: hay, food, housing and company',
             seo='How to care for a guinea pig: diet, cage and company',
             desc='How much hay, pellets and vegetables a guinea pig needs, what its home should be like, who it can live with and what to check daily. RSPCA, PDSA and PetMD advice.',
             short='The core of a guinea pig’s diet is unlimited hay and grass. On top of that come a few guinea pig pellets, fresh vegetables every day and clean water. Guinea pigs are social and live in pairs or groups. They need a roomy home with a solid floor, hides and space to move.',
             tags='hay pellets vegetables water cage run bedding cleaning company neutering temperature',
             sections=[
                 ('Hay and grass', '<p>Hay should make up most of the diet and be available at all times. PDSA puts its share at 85–90%, PetMD at about 80%. The RSPCA advises giving fresh grass as often as possible, ideally daily. Lawnmower clippings are dangerous and must not be fed.</p>'),
                 ('Pellets', '<p>Choose uniform pellets made for guinea pigs, grass-based, rather than muesli-style mixes. PDSA suggests about one tablespoon per adult guinea pig a day; the RSPCA says a portion following the manufacturer’s instructions, fresh each day.</p>'),
                 ('Vegetables and fruit', '<p>PDSA suggests about a cup of vegetables per guinea pig a day, 5–6 different kinds, including some rich in vitamin C. Among foods that can be given often, the RSPCA lists bell peppers, cucumber, celery, romaine lettuce and parsley, while broccoli, spinach, kale, carrot and a quarter of an apple are treats for a few times a week. Fruit is given rarely because of its sugar. Introduce new foods gradually.</p>'
                  + '<p>Don’t give iceberg lettuce, potato, onion, garlic, mushrooms, avocado, rhubarb, chocolate, bread and biscuits, nuts or grains.</p>'),
                 ('Water', '<p>Fresh, clean water must always be available. The RSPCA advises checking it twice a day and making sure it doesn’t freeze in winter. Wash the bowl or bottle every day.</p>'),
                 ('Housing', '<p>Sources give different minimum sizes:</p>' + table(['Source', 'Minimum'], [
                     ['PetMD', 'a cage of about 91 × 76 × 46 cm'],
                     ['PDSA', 'a hutch of at least 1.5 × 1 m and a run of at least 2 × 1 m'],
                     ['RSPCA Australia', 'at least 2 × 0.5 m for a pair, at least 30 cm high'],
                 ]) + '<p>All agree that bigger is better. The floor should be solid, not mesh. The RSPCA advises having one more hide than there are guinea pigs, and giving them space to move every day. PetMD suggests at least an hour a day outside the cage.</p>'),
                 ('Temperature', '<p>The RSPCA gives 17–20 °C as a comfortable room temperature. Above 26 °C the risk of heatstroke rises, and below 15 °C a guinea pig can get chilled. PDSA warns of heatstroke above 27 °C. Keep the home away from radiators, sunny windows and draughts.</p>'),
                 ('Bedding and cleaning', '<p>Dust-free hay or paper bedding works well; cotton wool should not be used. Sources disagree about wood shavings, so paper bedding is the safer choice. Remove wet bedding and leftover fresh food every day, and do a thorough clean once a week.</p>'),
                 ('Company', '<p>The RSPCA advises keeping a guinea pig with at least one friendly companion unless a vet advises otherwise. Good pairings are a neutered male with one or more females, two females, or brothers raised together. A male living with females must be neutered: according to PDSA, females can become pregnant from about three weeks old. A rabbit is not a companion for a guinea pig, and keeping them together is not advised.</p>'),
                 ('Health checks', ul(
                     'Check your guinea pig every day: face and eyes, coat, rear end and feet.',
                     'Check the front teeth and nails once a week. Overgrown teeth must be corrected by a vet.',
                     'In hot weather check the rear end twice a day: soiled fur attracts flies.',
                     'Take your guinea pig to a vet at least once a year.',
                     'If eating, drinking or droppings change, or droppings stop, contact a vet straight away. Difficulty breathing is an emergency.')),
             ],
             check=['how many guinea pigs live together and their sex', 'the size of the home', 'what you feed and how much', 'room temperature', 'weight over time'],
         )),
    dict(slug='degu-vdoma', rodent='degu', topic='Догляд', photo='degu2',
         published='2026-11-16', updated='2026-11-16', checked='2026-11-16',
         title='Дегу вдома: житло, компанія, раціон і здоровʼя',
         seo='Як доглядати за дегу: клітка, корм, пилові ванни, діабет',
         desc='Яка клітка потрібна дегу, чому їх не тримають поодинці, чим годувати, щоб уберегти від діабету, як давати пилові ванни й чому не можна брати за хвіст.',
         short='Дегу активні вдень і живуть групами, тож поодинці їх не тримають. Їм потрібна висока металева клітка з кількома рівнями й колесом, глибока підстилка для риття й пилові ванни кілька разів на тиждень. Основа раціону — сіно, а гранули дають потроху й без цукру, бо дегу схильні до діабету.',
         tags='дегу клітка компанія сіно гранули діабет катаракта зуби хвіст пилова ванна колесо',
         sections=[
             ('Спосіб життя й компанія', '<p>Дегу активні вдень і дуже балакучі. Це соціальні тварини: RSPCA попереджає, що поодинці вони можуть впадати в депресію, і радить тримати дегу самого лише за порадою ветеринара. Тримають одностатеві групи або кастрованого самця із самками, причому в змішаній групі має бути не більше одного самця. PetMD не радить селити дегу з іншими гризунами чи кроликами. Тривалість життя джерела оцінюють по-різному: PDSA — 6–8 років, іноді 9, RSPCA — 6–7 років, PetMD — 5–9 років.</p>'),
             ('Клітка', ul(
                 'Клітка має бути металевою: пластик і дерево дегу прогризають. PetMD радить уникати пластикових кліток і аксесуарів.',
                 'Розмір: PDSA радить якомога більшу клітку, а PetMD для двох дегу називає мінімум приблизно 71 × 46 × 71 см і відстань між прутами не більше 1,3 см.',
                 'Висока клітка з кількома рівнями, полиці й підлога суцільні. Суцільний дах допомагає дегу почуватися в безпеці.',
                 'Гілки груші, яблуні чи бука для лазіння й гризіння.',
                 'Будиночок із сіном для сну.',
                 'Скляні акваріуми не підходять: RSPCA повʼязує їх із проблемами дихання.',
                 'Ставте клітку в приміщенні, без протягів і прямого сонця, подалі від телевізора й музики: вібрація їх лякає.')),
             ('Тепло', '<p>RSPCA радить, щоб у приміщенні з кліткою було не вище 20 °C, і просить ставити її подалі від батарей. Якщо дегу лежить плазом на животі, вона може перегріватися: одразу звертайтеся до ветеринара.</p>'),
             ('Рух і риття', '<p>Потрібне суцільне колесо, достатньо велике, щоб дегу бігала з рівною спиною. PetMD називає діаметр 25–30 см. PDSA радить щодня випускати дегу щонайменше на пів години в безпечну кімнату чи вольєр, де закриті дроти й дерево. Для риття потрібен глибокий шар сіна й рваного паперу. Щодо деревної стружки джерела розходяться: RSPCA допускає нетоксичну стружку, PetMD не радить її через ризик для дихання.</p>'),
             ('Пилові ванни', table(['Джерело', 'Як часто', 'Як'], [
                 ['PDSA', 'кілька разів на тиждень', 'пісок для шиншил чи хомʼяків, не лишати постійно, бо сушить шкіру'],
                 ['RSPCA', '2–3 рази на тиждень, приблизно по 20 хв', 'важка миска з шаром піску близько 4 см, після купання прибрати'],
                 ['PetMD', 'приблизно двічі на тиждень', 'пил для шиншил, поза кліткою'],
             ])),
             ('Раціон', ul(
                 'Основа — сіно без обмежень.',
                 'Гранули для дегу: PDSA і PetMD радять одну-дві столові ложки на день. Якщо їх немає, підходять гранули для морських свинок чи шиншил без меляси.',
                 'Корм для кроликів, хомʼяків і піщанок, а також суміші із сухофруктами RSPCA вважає непридатними.',
                 'Листова зелень і овочі — невеликими порціями. PDSA радить один-два рази на тиждень, PetMD — кілька разів на тиждень.',
                 'Фрукти, мед, мелясу й насіння PetMD радить не давати зовсім. PDSA допускає зрідка шматочок яблука. Моркву, батат і буряк RSPCA дозволяє лише крихітними шматочками зрідка.',
                 'Будьте обережні з магазинними ласощами: часто вони надто солодкі.',
                 'Дегу зʼїдають частину свого посліду: це норма.',
                 'Новий корм вводьте поступово.')),
             ('Діабет', '<p>За RSPCA і PDSA, дегу схильні до діабету 2 типу, особливо якщо в раціоні багато вуглеводів і цукру. PDSA називає такі ознаки: помутніння очей (катаракта), дегу багато пʼє й часто мочиться, набирає зайву вагу. Якщо помітили щось із цього, зверніться до ветеринара. Детальніше про раціон читайте в статті «Чим годувати дегу».</p>'),
             ('Зуби', '<p>Зуби дегу ростуть безперервно й стираються під час жування сіна. RSPCA пише, що здорові зуби жовто-помаранчеві, а білі можуть бути ознакою хвороби, і радить оглядати їх щотижня. За PDSA, про проблеми із зубами можуть свідчити слинотеча, набряк морди, виділення з очей і зміна кольору зубів. Виправляти зуби, що переросли, може лише ветеринар.</p>'),
             ('Хвіст і як брати на руки', '<p>Дегу ніколи не беруть і не тягнуть за хвіст. Шкіра з кінчика хвоста може злізти, і тоді потрібен ветеринар, бо є ризик інфекції. RSPCA радить дати дегу самій залізти на долоню й підняти її в складених долонях, низько над підлогою. Руки, що нависають згори, тварину лякають.</p>'),
             ('Огляди', '<p>RSPCA радить оглядати дегу щодня. У здорової дегу ясні очі, чисті вуха, блискуча шерсть, чистий хвіст і задня частина тіла. Насторожують виділення з носа, волога біля рота, помутніння очей і білі зуби. Щонайменше раз на рік показуйте дегу ветеринару. PetMD радить терміново звертатися до лікаря, якщо дегу гірше їсть, худне, важко дихає, має діарею, погано жує чи стала млявою.</p>'),
         ],
         check=['скільки дегу і якої статі живуть разом', 'чим годуєте, чи бувають солодощі', 'скільки дегу пʼє', 'стан очей і колір зубів', 'температура в кімнаті'],
         sources=['rspca_degu', 'rspca_degu_env', 'rspca_degu_diet', 'rspca_degu_health', 'rspca_degu_company', 'rspca_degu_behaviour', 'pdsa_degu', 'petmd_d'],
         related=['chym-goduvaty-degu', 'pylovi-vanny-shynshyly'],
         en=dict(
             title='Degus at home: housing, company, diet and health',
             seo='How to care for degus: cage, food, dust baths and diabetes',
             desc='Which cage degus need, why they are not kept alone, how to feed them to prevent diabetes, how to give dust baths and why never to hold them by the tail.',
             short='Degus are active by day and live in groups, so they are not kept alone. They need a tall metal cage with several levels and a wheel, deep bedding for digging and dust baths a few times a week. The core of the diet is hay, with a few sugar-free pellets, because degus are prone to diabetes.',
             tags='degu cage company hay pellets diabetes cataract teeth tail dust bath wheel',
             sections=[
                 ('Lifestyle and company', '<p>Degus are active by day and very vocal. They are social animals: the RSPCA warns that alone they can become depressed and advises keeping a single degu only on a vet’s advice. Keep single-sex groups or a neutered male with females, with no more than one male in a mixed group. PetMD advises against housing degus with other rodents or rabbits. Sources give different lifespans: PDSA says 6–8 years, sometimes 9; the RSPCA 6–7 years; PetMD 5–9 years.</p>'),
                 ('The cage', ul(
                     'The cage must be metal: degus chew through plastic and wood. PetMD advises avoiding plastic cages and accessories.',
                     'Size: PDSA advises as large a cage as possible, and PetMD gives a minimum of about 71 × 46 × 71 cm for two degus, with bars no more than 1.3 cm apart.',
                     'A tall cage with several levels and solid shelves and floor. A solid roof helps degus feel safe.',
                     'Pear, apple or beech branches for climbing and gnawing.',
                     'A nest box with hay for sleeping.',
                     'Glass tanks are not suitable: the RSPCA links them to breathing problems.',
                     'Keep the cage indoors, out of draughts and direct sun, away from the TV and music: vibration frightens them.')),
                 ('Heat', '<p>The RSPCA advises keeping the room with the cage no warmer than 20 °C and placing it away from radiators. A degu lying flat on its stomach may be overheating: contact a vet straight away.</p>'),
                 ('Exercise and digging', '<p>A solid wheel is needed, big enough for the degu to run with a straight back. PetMD gives a diameter of 25–30 cm. PDSA advises letting degus out for at least half an hour a day into a safe room or pen with wires and wood covered. For digging they need a deep layer of hay and shredded paper. Sources disagree on wood shavings: the RSPCA allows non-toxic shavings, while PetMD advises against them because of the risk to breathing.</p>'),
                 ('Dust baths', table(['Source', 'How often', 'How'], [
                     ['PDSA', 'a few times a week', 'chinchilla or hamster sand, not left in all the time because it dries the skin'],
                     ['RSPCA', '2–3 times a week, about 20 min each', 'a heavy bowl with about 4 cm of sand, removed after use'],
                     ['PetMD', 'about twice a week', 'chinchilla dust, outside the cage'],
                 ])),
                 ('Diet', ul(
                     'The core is unlimited hay.',
                     'Degu pellets: PDSA and PetMD suggest one to two tablespoons a day. If degu pellets are not available, guinea pig or chinchilla pellets without molasses will do.',
                     'The RSPCA considers rabbit, hamster and gerbil food, and mixes with dried fruit, unsuitable.',
                     'Leafy greens and vegetables in small portions: PDSA suggests once or twice a week, PetMD a few times a week.',
                     'PetMD advises no fruit, honey, molasses or seeds at all. PDSA allows an occasional bit of apple. The RSPCA allows carrot, sweet potato and beetroot only in tiny pieces now and then.',
                     'Be careful with shop-bought treats: they are often too sugary.',
                     'Degus eat some of their own droppings: this is normal.',
                     'Introduce new food gradually.')),
                 ('Diabetes', '<p>According to the RSPCA and PDSA, degus are prone to type 2 diabetes, especially on a diet high in carbohydrates and sugar. PDSA lists these signs: cloudy eyes (cataracts), drinking a lot and urinating often, and weight gain. If you notice any of these, see a vet.</p>'),
                 ('Teeth', '<p>Degus’ teeth grow continuously and wear down as they chew hay. The RSPCA says healthy teeth are yellow-orange, white teeth can be a sign of illness, and advises checking them every week. According to PDSA, dental problems can show as drooling, a swollen face, discharge from the eyes and a change in tooth colour. Only a vet should correct overgrown teeth.</p>'),
                 ('The tail and handling', '<p>Never pick up or pull a degu by the tail. The skin on the tip of the tail can come off, and then a vet is needed because of the risk of infection. The RSPCA advises letting the degu climb onto your palm and lifting it in cupped hands, low over the floor. Hands swooping down from above frighten them.</p>'),
                 ('Health checks', '<p>The RSPCA advises checking degus every day. A healthy degu has bright, clear eyes, clean ears, a glossy coat, and a clean tail and rear end. Warning signs include nasal discharge, wetness around the mouth, cloudy eyes and white teeth. Take your degus to a vet at least once a year. PetMD advises seeing a vet urgently if a degu eats less, loses weight, breathes with difficulty, has diarrhoea, struggles to chew or becomes lethargic.</p>'),
             ],
             check=['how many degus live together and their sex', 'what you feed and whether they get sweet things', 'how much the degus drink', 'the condition of the eyes and tooth colour', 'room temperature'],
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
INFO_DESC_EN = 'How Roddi Health prepares its blog articles: which sources we use, how we mark external articles and fact-check dates, and how to report a mistake.'
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
