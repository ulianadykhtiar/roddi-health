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
UPDATED_UK = '9 листопада 2026'

P = {
    'rat': {'src': 'f/fd/Fancy_rat_blaze.jpg', 'by': 'AlexK100', 'lic': 'CC BY-SA 2.0', 'page': 'https://commons.wikimedia.org/wiki/File:Fancy_rat_blaze.jpg'},
    'rat2': {'src': '4/41/Fancy_rat_husky.jpg', 'by': 'Eurovaran', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Fancy_rat_husky.jpg', 'pos': '50% 35%'},
    'hamster': {'src': '7/73/Syrian_Hamster_Mid-grooming.jpg', 'by': 'John Stockla', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Syrian_Hamster_Mid-grooming.jpg'},
    'hamster2': {'src': 'f/f5/Syrian_hamster_on_blanket.jpg', 'by': 'MarketBoiCYM', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Syrian_hamster_on_blanket.jpg', 'pos': '50% 40%'},
    'gp': {'src': 'e/ee/Cavia_porcellus01.jpg', 'by': 'Kacper Aleksander', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Cavia_porcellus01.jpg'},
    'gp2': {'src': 'b/bc/Caviidae_Cavia_porcellus_1.jpg', 'by': 'NasserHalaweh', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Caviidae_Cavia_porcellus_1.jpg'},
    'degu': {'src': 'f/f4/Octodontidae_Octodon_degus_1.2.jpg', 'by': 'NasserHalaweh', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Octodontidae_Octodon_degus_1.2.jpg'},
    'rabbit': {'src': '3/31/Heimtier_004_2023_08_26.jpg', 'by': 'Friedrich Haag', 'lic': 'CC BY-SA 4.0', 'page': 'https://commons.wikimedia.org/wiki/File:Heimtier_004_2023_08_26.jpg'},
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
]

BY_SLUG = {a['slug']: a for a in ARTICLES}
LABEL = {'rat': 'Щури', 'hamster': 'Хомʼяки', 'guinea-pig': 'Морські свинки', 'degu': 'Дегу', 'rabbit': 'Кролики'}
INFO_URL = 'pro-materialy.html'


def e(t):
    return html.escape(t, quote=True)


def photo_file(src, w):
    name = urllib.parse.unquote(src.split('/')[-1]).rsplit('.', 1)[0].lower()
    name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
    path = 'assets/blog/%s-%d.jpg' % (name, w)
    assert (ROOT / path).exists(), path
    return path


blog = (ROOT / 'blog.html').read_text(encoding='utf-8')


def relink(x):
    x = re.sub(r'\sdata-reveal(="[^"]*")?', '', x)
    x = re.sub(r'\sdata-d="\d+"', '', x)
    x = re.sub(r'(src|href)="(assets/|index\.html|blog\.html|en/)', lambda m: '%s="../%s' % (m.group(1), m.group(2)), x)
    return x.replace(' aria-current="page"', '')


DIALOG = relink(blog[blog.index('<dialog id="site-menu"'):blog.index('</dialog>') + 9])
NAV = relink(blog[blog.index('<nav data-reveal="down"'):blog.index('</nav>', blog.index('<nav data-reveal="down"')) + 6])
FOOT = relink(blog[blog.index('<footer id="early-access"'):blog.index('</footer>') + 9]).replace('data-form="blog"', 'data-form="article"')


def page(slug, title, desc, jsonld, main, img=None, og='article'):
    url = '%s/blog/%s' % (BASE, slug)
    image = BASE + '/' + (img or 'assets/og-uk.jpg')
    return f'''<!doctype html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} | Roddi Health</title>
  <link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="../assets/apple-touch-icon.png">
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="{og}">
  <meta property="og:site_name" content="Roddi Health">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:locale" content="uk_UA">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700;800&family=Montserrat:wght@600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.11"></script>
  <style type="text/tailwindcss">@theme {{ --breakpoint-wide: 85rem; }}</style>
  <link rel="stylesheet" href="../assets/styles.css?v=2">
  <script src="../assets/clarity.js"></script>
  <link rel="stylesheet" href="../assets/theme.css">
  <link rel="stylesheet" href="../assets/app-home.css?v=47">
  <link rel="stylesheet" href="../assets/pages.css?v=3">
</head>
<body class="page-soft">
{DIALOG}
<header class="relative bg-white">
  {NAV}
</header>
{main}
{FOOT}
<script>window.RODDI_THANKS = '../thank-you.html';</script>
<script src="../assets/forms.js?v=2"></script>
<script src="../assets/menu.js?v=2"></script>
</body>
</html>
'''


SHORT_NOTE = ('<p class="ar-note"><b>Важливо.</b> Це загальна інформація з відкритих джерел, а не діагноз чи призначення. '
              'Перш ніж ухвалювати будь-яке рішення щодо здоровʼя тварини, порадьтеся з ветеринаром і перевірте інформацію. '
              '<a href="%s">Як ми готуємо матеріали</a></p>' % INFO_URL)
LEGAL = ('<p class="ar-legal">Roddi Health не є ветеринарною клінікою і не надає ветеринарних послуг. Матеріал має лише інформаційний характер, '
         'може бути неповним або застарілим і не замінює огляду лікаря. Ви самостійно приймаєте рішення щодо догляду за твариною. '
         'Назви джерел наведено для посилання: вони не писали й не схвалювали цей текст. '
         '<a href="%s">Докладніше про матеріали блогу</a>.</p>' % INFO_URL)


def article(a):
    url = '%s/blog/%s' % (BASE, a['slug'])
    ph = P[a['photo']]
    img = photo_file(ph['src'], 960)
    pos = ph.get('pos', '50% 50%')
    urgent = ''
    if a.get('urgent'):
        urgent = '<aside class="ar-urgent" aria-label="Коли потрібен ветеринар терміново"><h2>Терміново до ветеринара, якщо:</h2>' + ul(*a['urgent']) + '</aside>'
    body = ''.join('<h2>%s</h2>%s' % (h, c) for h, c in a['sections'])
    check = ''.join('<li>%s</li>' % c for c in a['check'])
    sources = ''.join('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (e(S[k][1]), e(S[k][0])) for k in a['sources'])
    related = ''.join('<a href="%s.html" class="ar-rel"><span>%s</span><b>%s</b></a>' % (r, e(BY_SLUG[r]['topic']), e(BY_SLUG[r]['title'])) for r in a['related'])
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BlogPosting', 'headline': a['title'], 'description': a['desc'], 'image': [BASE + '/' + img],
         'datePublished': PUBLISHED, 'dateModified': UPDATED, 'inLanguage': 'uk', 'mainEntityOfPage': url,
         'author': {'@type': 'Organization', 'name': 'Редакція Roddi Health', 'url': BASE + '/blog/pro-materialy'},
         'publisher': {'@type': 'Organization', 'name': 'Roddi Health', 'url': BASE + '/', 'logo': {'@type': 'ImageObject', 'url': BASE + '/assets/favicon-32.png'}},
         'citation': [S[k][1] for k in a['sources']]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Головна', 'item': BASE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Блог', 'item': BASE + '/blog'},
            {'@type': 'ListItem', 'position': 3, 'name': a['title']}]},
    ]}
    main = f'''<main class="ar">
  <nav class="ar-crumb" aria-label="Навігація"><a href="../index.html">Головна</a><span aria-hidden="true">/</span><a href="../blog.html">Блог</a><span aria-hidden="true">/</span><b>{e(LABEL[a['rodent']])}</b></nav>
  <h1 class="t-h1">{e(a['title'])}</h1>
  <p class="ar-meta">Редакція Roddi Health · оновлено {UPDATED_UK} · огляд відкритих джерел</p>
  <div class="ar-short soft-grad soft-grad--ask"><p class="ar-short-l">Коротко</p><p>{e(a['short'])}</p></div>
  {SHORT_NOTE}
  <figure class="ar-fig"><img alt="{e(a['title'])}" src="../{img}" width="960" height="540" style="object-position:{pos}"><figcaption>Фото: <a href="{e(ph['page'])}" target="_blank" rel="noopener">{e(ph['by'])}</a>, {e(ph['lic'])}, Wikimedia Commons</figcaption></figure>
  {urgent}
  <div class="ar-body">{body}</div>
  <section class="ar-check"><h2>Що записати перед дзвінком ветеринару</h2><ul>{check}</ul><p>Такі нотатки легше вести в одному місці. Саме для цього ми робимо Roddi Health.</p><a href="#early-access" class="btn-app btn-app-sm">Хочу ранній доступ</a></section>
  <section class="ar-sources"><h2>Джерела</h2><ul>{sources}</ul></section>
  {LEGAL}
  <section class="ar-related" aria-label="Схожі матеріали"><h2>Читайте також</h2><div>{related}</div></section>
</main>
'''
    return page(a['slug'], a['seo'], a['desc'], ld, main, img)


INFO_TITLE = 'Про матеріали блогу та відмова від відповідальності'
INFO_DESC = 'Як Roddi Health готує матеріали блогу, які джерела використовує, обмеження інформації та як звʼязатися щодо авторських прав.'
info_ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': INFO_TITLE, 'description': INFO_DESC, 'url': BASE + '/blog/pro-materialy', 'inLanguage': 'uk'}
info_main = f'''<main class="ar">
  <nav class="ar-crumb" aria-label="Навігація"><a href="../index.html">Головна</a><span aria-hidden="true">/</span><a href="../blog.html">Блог</a><span aria-hidden="true">/</span><b>Про матеріали</b></nav>
  <h1 class="t-h1">{e(INFO_TITLE)}</h1>
  <p class="ar-meta">Оновлено {UPDATED_UK}</p>
  <div class="ar-body">
    <h2>Як ми готуємо статті</h2>
    <p>Статті блогу є власними оглядами редакції Roddi Health українською. Ми читаємо відкриті матеріали ветеринарів, клінік і зоозахисних організацій, зіставляємо їх, викладаємо факти своїми словами й показуємо місця, де джерела розходяться. Під кожною статтею є перелік джерел із посиланнями. Ми не копіюємо чужі тексти.</p>
    <p>У підготовці текстів ми використовуємо інструменти на основі ШІ. Статті не є рецензованими ветеринарними публікаціями, якщо це не зазначено окремо біля конкретної статті.</p>
    <h2>Це не ветеринарна консультація</h2>
    <p>Roddi Health не є ветеринарною клінікою і не надає ветеринарних послуг. Матеріали блогу мають лише інформаційний характер і не є діагнозом, планом лікування чи рекомендацією щодо ліків або доз. Вони не замінюють огляду ветеринара.</p>
    <p>Перш ніж ухвалювати будь-яке рішення щодо здоровʼя тварини, порадьтеся з ветеринаром і самостійно перевірте інформацію. Якщо тварині погано, не відкладайте звернення через прочитане на сайті.</p>
    <h2>Обмеження</h2>
    <p>Ми намагаємося підтримувати матеріали точними, але не гарантуємо, що вони повні, актуальні чи підходять саме вашій тварині. Рекомендації змінюються, а джерела можуть не збігатися. Ви самостійно приймаєте рішення щодо догляду за твариною. У межах, дозволених законом, Roddi Health не відповідає за наслідки використання цієї інформації.</p>
    <h2>Згадані джерела</h2>
    <p>Назви організацій і сайтів наведено лише для посилання. Вони не пов’язані з Roddi Health, не писали й не схвалювали наші тексти. За вміст зовнішніх сайтів відповідають їхні власники.</p>
    <h2>Фото й авторські права</h2>
    <p>Фотографії в блозі мають вільні ліцензії й підписані іменем автора та ліцензією. Якщо ви вважаєте, що матеріал порушує ваші права, або знайшли помилку, напишіть на <a href="mailto:roddihealth@gmail.com">roddihealth@gmail.com</a>: ми перевіримо й виправимо або приберемо його.</p>
  </div>
</main>
'''

(ROOT / 'blog').mkdir(exist_ok=True)
for a in ARTICLES:
    (ROOT / 'blog' / (a['slug'] + '.html')).write_text(article(a), encoding='utf-8')
(ROOT / 'blog' / 'pro-materialy.html').write_text(page('pro-materialy', INFO_TITLE, INFO_DESC, info_ld, info_main, og='website'), encoding='utf-8')

# Data for the cards on blog.html.
cards = [{'rodent': a['rodent'], 'topic': a['topic'], 'title': a['title'], 'excerpt': a['short'], 'tags': a['tags'],
          'source': 'Roddi Health', 'url': 'blog/%s.html' % a['slug'], 'internal': True, 'featured': bool(a.get('featured')), 'photo': P[a['photo']]} for a in ARTICLES]
(ROOT / 'assets/blog-articles.js').write_text('/* Built by tools/build-articles.py. Do not edit by hand. */\nvar BLOG_ARTICLES = ' + json.dumps(cards, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')

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
urls = ''.join('\n  <url>\n    <loc>%s/blog/%s</loc>\n    <lastmod>%s</lastmod>\n  </url>' % (BASE, s, UPDATED) for s in [a['slug'] for a in ARTICLES] + ['pro-materialy'])
sm = sm.replace('</urlset>', '  <!-- articles:start -->' + urls + '\n  <!-- articles:end -->\n</urlset>')
(ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
print('built', len(ARTICLES), 'articles')
