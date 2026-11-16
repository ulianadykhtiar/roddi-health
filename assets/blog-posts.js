/* Roddi Health — blog posts.
 *
 * Cards that still lead to articles on other sites: a short summary in our own
 * words and a link to the original. The page marks each one as an article on an
 * external site. They are being replaced one by one with our own articles
 * (tools/build-articles.py). When an article replaces a card, remove the card here
 * and the entry at the same position in blog-posts.en.js, then run
 * tools/build-blog-lists.py. Never translate or copy the original text.
 *
 * Photos are free-licence pictures from Wikimedia Commons, saved locally in
 * assets/blog as <slug>-500.jpg and <slug>-960.jpg (slug = file name in lower
 * case, non-letters turned into '-'). A new photo needs both files there. CC BY / CC BY-SA require naming the author and licence,
 * which the card does from `photo.by` / `photo.lic` / `photo.page` — keep them
 * when swapping a photo. `photo.src` is the file's path on Commons
 * ("a/ab/File_name.jpg"); `photo.pos` sets object-position if the crop needs it.
 *
 * Post fields:
 *   rodent   — one of the keys in BLOG_RODENTS (drives the filter chips)
 *   topic    — one of the keys in BLOG_TOPICS
 *   title, excerpt — card text
 *   tags     — extra search keywords (not shown)
 *   source, url — publisher name and link to the original article
 *   featured — the first featured post (per filter) is shown as the large card
 */
var BLOG_RODENTS = [
  { key: 'rat',        label: 'Щури',           tint: '#f3e8ef' },
  { key: 'hamster',    label: 'Хом’яки',        tint: '#f3e8ef' },
  { key: 'guinea-pig', label: 'Морські свинки', tint: '#f2f2f4' },
  { key: 'chinchilla', label: 'Шиншили',        tint: '#f3e8ef' },
  { key: 'degu',       label: 'Дегу',           tint: '#f3e8ef' },
  { key: 'mouse',      label: 'Миші',           tint: '#f3e8ef' },
  { key: 'rabbit',     label: 'Кролики',        tint: '#f3e8ef' }
];

var BLOG_TOPICS = {
  'Симптоми':    '#a45588',
  'Харчування':  '#2f9e5b',
  'Догляд':      '#e0a800',
  'Невідкладне': '#e5484d'
};

var BLOG_POSTS = [
  {
    rodent: 'rat', topic: 'Догляд',
    title: 'Як зробити життя щура цікавішим',
    excerpt: 'Щури розумні й допитливі, їм потрібні нові враження. Коробки, тунелі, мотузки та розсипаний корм, який треба шукати, допомагають уникнути нудьги.',
    tags: 'збагачення іграшки нудьга клітка гра пошук корму',
    source: 'Blue Cross', url: 'https://www.bluecross.org.uk/pet-advice/caring-your-rat',
    photo: { src: '2/26/Three_baby_rats_piled_up_in_their_bed.jpg', by: 'Cat Ball', lic: 'CC0', page: 'https://commons.wikimedia.org/wiki/File:Three_baby_rats_piled_up_in_their_bed.jpg' }
  },
  {
    rodent: 'hamster', topic: 'Догляд',
    title: '25 найчастіших запитань про хом’яків',
    excerpt: 'Ветеринари відповідають на те, що найчастіше питають власники: яка клітка потрібна, чим годувати, чи можна тримати двох хом’яків разом і як зрозуміти, що тварина хворіє.',
    tags: 'клітка корм питання поради новачкам сусіди сирійський джунгарик',
    source: 'VetVerified', url: 'https://vetverified.com/articles/the-top-25-hamster-care-questions-answered-by-uk-vets',
    photo: { src: 'f/f5/Syrian_hamster_on_blanket.jpg', by: 'MarketBoiCYM', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Syrian_hamster_on_blanket.jpg', pos: '50% 40%' }
  },
  {
    rodent: 'guinea-pig', topic: 'Симптоми',
    title: 'Цинга в морських свинок: як помітити вчасно',
    excerpt: 'Ознаки нестачі вітаміну C можуть з’явитися вже за 2–3 тижні неправильного харчування: скутість, біль у суглобах, кровоточивість ясен, погана шерсть. Стан лікується, якщо почати вчасно.',
    tags: 'цинга вітамін с суглоби ясна шерсть дефіцит',
    source: 'Unusual Pet Vets', url: 'https://unusualpetvets.com.au/scurvy-in-guinea-pigs-and-the-importance-of-vitamin-c',
    photo: { src: 'e/ee/Cavia_porcellus01.jpg', by: 'Kacper Aleksander', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Cavia_porcellus01.jpg' }
  },
  {
    rodent: 'guinea-pig', topic: 'Догляд',
    title: 'Базовий догляд за морською свинкою',
    excerpt: 'Необмежене сіно, свіжі овочі, корм для морських свинок і чиста вода — основа раціону. А ще простора клітка й компанія: це соціальні тварини.',
    tags: 'сіно вода клітка компанія раціон овочі',
    source: 'RSPCA Australia', url: 'https://www.rspca.org.au/latest-news/blog/how-should-i-care-my-guinea-pig/',
    photo: { src: 'b/bc/Caviidae_Cavia_porcellus_1.jpg', by: 'NasserHalaweh', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Caviidae_Cavia_porcellus_1.jpg' }
  },
  {
    rodent: 'chinchilla', topic: 'Догляд', featured: true,
    title: 'Пилові ванни для шиншили: як і як часто',
    excerpt: 'Шиншилу не купають у воді: густе хутро погано висихає. Натомість дають спеціальний пісок-пил і прибирають ванночку приблизно через пів години, щоб не подразнювати очі.',
    tags: 'пилова ванна купання хутро шерсть очі пісок',
    source: 'PetMD', url: 'https://www.petmd.com/exotic/care/how-give-your-chinchilla-dust-bath',
    photo: { src: '4/45/Napoleon_chinchilla_in_box.jpg', by: 'Bluerasberry', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Napoleon_chinchilla_in_box.jpg', pos: '50% 45%' }
  },
  {
    rodent: 'chinchilla', topic: 'Симптоми',
    title: 'Здоров’я шиншили: зуби, шерсть, травлення',
    excerpt: 'Зуби шиншили ростуть усе життя, тому їй потрібне необмежене сіно і безпечні предмети для гризіння. Слинотеча чи відмова від їжі — привід перевірити зуби у ветеринара.',
    tags: 'зуби сіно гризіння слина травлення шерсть перегрів',
    source: 'PDSA', url: 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/chinchilla-health',
    photo: { src: 'e/e8/Chinchilla_lanigera1.jpg', by: 'Trurl66', lic: 'Public domain', page: 'https://commons.wikimedia.org/wiki/File:Chinchilla_lanigera1.jpg' }
  },
  {
    rodent: 'degu', topic: 'Догляд',
    title: 'Дегу вдома: що потрібно знати власнику',
    excerpt: 'Дегу — активні денні тварини, які живуть групами. Їм потрібні простір, колесо, предмети для гризіння й пилові ванни. Сильна спрага чи помутніння очей — привід звернутися до лікаря.',
    tags: 'клітка колесо компанія пилова ванна очі спрага',
    source: 'PetMD', url: 'https://www.petmd.com/exotic/care/caring-for-a-degu',
    photo: { src: '6/69/Octodon_degus_209581281.jpg', by: 'Ben Lyle Bedard', lic: 'CC BY 4.0', page: 'https://commons.wikimedia.org/wiki/File:Octodon_degus_209581281.jpg' }
  },
  {
    rodent: 'mouse', topic: 'Симптоми', featured: true,
    title: 'Здоров’я мишей: щоденний огляд за хвилину',
    excerpt: 'Миші часто приховують біль, тому зміни краще ловити рано: подивіться на очі, ніс, шерсть, дихання й послід. Чхання чи «цокання» під час дихання — привід звернутися до ветеринара.',
    tags: 'огляд чхання дихання послід шерсть біль',
    source: 'PDSA', url: 'https://www.pdsa.org.uk/pet-help-and-advice/looking-after-your-pet/small-pets/mouse-health',
    photo: { src: 'e/ed/Pet_mouse_mini.jpg', by: 'Tiia Monto', lic: 'CC BY-SA 3.0', page: 'https://commons.wikimedia.org/wiki/File:Pet_mouse_mini.jpg' }
  },
  {
    rodent: 'mouse', topic: 'Догляд',
    title: 'Рутинний догляд за домашніми мишами',
    excerpt: 'Довідник для власників від MSD Vet Manual: як облаштувати житло, як часто прибирати, як годувати і як помітити перші ознаки хвороби.',
    tags: 'клітка прибирання корм профілактика ветеринар вода',
    source: 'MSD Vet Manual', url: 'https://www.msdvetmanual.com/all-other-pets/mice/routine-health-care-of-mice',
    photo: { src: '4/4d/Pet_mouse_drinking.jpg', by: 'Tiia Monto', lic: 'CC BY-SA 3.0', page: 'https://commons.wikimedia.org/wiki/File:Pet_mouse_drinking.jpg', pos: '50% 35%' }
  }
];
