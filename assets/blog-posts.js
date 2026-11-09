/* Roddi Health — blog posts.
 *
 * Placeholder content: short summaries (written for this page, in Ukrainian) of
 * open articles by vets and animal-welfare organisations. Each card links to
 * the original. Replace or extend freely; the page builds itself from this list.
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
    rodent: 'rat', topic: 'Симптоми', featured: true,
    title: 'Респіраторні інфекції у щурів: на які ознаки зважати',
    excerpt: 'Чхання, хрипи чи «клацання» під час дихання, виділення з носа й червонуваті кірочки біля очей — найчастіші сигнали. Без лікування інфекція може бути небезпечною, тож із такими симптомами варто йти до ветеринара.',
    tags: 'дихання чхання хрипи нежить порфірин антибіотики застуда',
    source: 'PetMD', url: 'https://www.petmd.com/exotic/conditions/respiratory/upper-respiratory-infection-rats',
    photo: { src: 'f/fd/Fancy_rat_blaze.jpg', by: 'AlexK100', lic: 'CC BY-SA 2.0', page: 'https://commons.wikimedia.org/wiki/File:Fancy_rat_blaze.jpg' }
  },
  {
    rodent: 'rat', topic: 'Симптоми',
    title: 'Мікоплазмоз: чому щур важко дихає',
    excerpt: 'Мікоплазма є в багатьох щурів і може роками нічим себе не проявляти, а загострюватися на тлі стресу. Брудна клітка із запахом аміаку подразнює дихальні шляхи, тому регулярне прибирання — частина профілактики.',
    tags: 'мікоплазма дихання аміак прибирання клітка стрес хронічне',
    source: 'Walkerville Vet', url: 'https://www.walkervillevet.com.au/blog/mycoplasma-respiratory-infections-in-rats',
    photo: { src: '4/41/Fancy_rat_husky.jpg', by: 'Eurovaran', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Fancy_rat_husky.jpg', pos: '50% 35%' }
  },
  {
    rodent: 'rat', topic: 'Харчування',
    title: 'Чим годувати щура і як стежити за вагою',
    excerpt: 'Основа раціону — спеціальний гранульований корм для щурів, а овочі, трохи фруктів і білкові ласощі — доповнення. Щури легко набирають вагу, тому порції варто контролювати.',
    tags: 'їжа раціон корм гранули вага ожиріння ласощі фрукти',
    source: 'Blue Cross', url: 'https://www.bluecross.org.uk/advice/rat/food-and-weight',
    photo: { src: 'f/f4/Shy_baby_rat_looking_curious.jpg', by: 'Cat Ball', lic: 'CC0', page: 'https://commons.wikimedia.org/wiki/File:Shy_baby_rat_looking_curious.jpg' }
  },
  {
    rodent: 'rat', topic: 'Догляд',
    title: 'Як зробити життя щура цікавішим',
    excerpt: 'Щури розумні й допитливі, їм потрібні нові враження. Коробки, тунелі, мотузки та розсипаний корм, який треба шукати, допомагають уникнути нудьги.',
    tags: 'збагачення іграшки нудьга клітка гра пошук корму',
    source: 'Blue Cross', url: 'https://www.bluecross.org.uk/pet-advice/caring-your-rat',
    photo: { src: '2/26/Three_baby_rats_piled_up_in_their_bed.jpg', by: 'Cat Ball', lic: 'CC0', page: 'https://commons.wikimedia.org/wiki/File:Three_baby_rats_piled_up_in_their_bed.jpg' }
  },
  {
    rodent: 'hamster', topic: 'Невідкладне', featured: true,
    title: 'Мокрий хвіст у хом’яка: чому це терміново',
    excerpt: 'Мокрий, забруднений хвіст, млявість і відмова від їжі можуть означати тяжку кишкову інфекцію. Стан швидко погіршується, тому до ветеринара треба потрапити в першу ж добу.',
    tags: 'мокрий хвіст діарея пронос кишківник інфекція млявість антибіотики',
    source: 'Ask A Vet', url: 'https://askavet.com/blogs/news/husbandry-and-medical-care-of-hamsters-vet-approved-2025-guide-by-dr-duncan-houston-%F0%9F%90%B9',
    photo: { src: '7/73/Syrian_Hamster_Mid-grooming.jpg', by: 'John Stockla', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Syrian_Hamster_Mid-grooming.jpg' }
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
    rodent: 'guinea-pig', topic: 'Харчування', featured: true,
    title: 'Чому морським свинкам потрібен вітамін C',
    excerpt: 'Морські свинки, як і люди, не синтезують вітамін C самі, тож мають отримувати його з їжею щодня. Добре підходять болгарський перець і листова зелень. Вітамін у воді для пиття — ненадійне джерело.',
    tags: 'вітамін с цинга перець зелень раціон добавки',
    source: 'SPCA New Zealand', url: 'https://spca.nz/advice-and-welfare/article/why-is-vitamin-c-important-for-my-guinea-pigs',
    photo: { src: '2/2d/Heimtier_001_2010_08_14.jpg', by: 'Friedrich Haag', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Heimtier_001_2010_08_14.jpg' }
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
    rodent: 'degu', topic: 'Харчування', featured: true,
    title: 'Дегу і цукор: як уберегти від діабету',
    excerpt: 'Дегу погано засвоюють цукор, тому схильні до діабету. Фрукти, сухофрукти й солодкі овочі краще не давати. Основа раціону — сіно і корм для дегу. Діабет легше попередити, ніж лікувати.',
    tags: 'діабет цукор фрукти раціон сіно катаракта спрага',
    source: 'Exotic Direct', url: 'https://exoticdirect.co.uk/news/degu-food-advice-what-your-degu-should-be-eating-not-eating-diabetes-and-other-advice/',
    photo: { src: 'f/f4/Octodontidae_Octodon_degus_1.2.jpg', by: 'NasserHalaweh', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Octodontidae_Octodon_degus_1.2.jpg' }
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
  },
  {
    rodent: 'rabbit', topic: 'Невідкладне', featured: true,
    title: 'Стаз ШКТ у кролика: коли бити на сполох',
    excerpt: 'Кролик не їсть і не залишає посліду кілька годин — це привід терміново їхати до ветеринара. Найкраща профілактика — раціон, де основа сіно, а гранул і фруктів зовсім трохи.',
    tags: 'стаз шкт травлення послід сіно не їсть здуття',
    source: 'VCA Animal Hospitals', url: 'https://vcahospitals.com/vitality/know-your-pet/gastrointestinal-stasis-in-rabbits',
    photo: { src: 'd/db/Lopeared_rabbit_in_Artis_themepark%2C_South_Korea.jpg', by: 'Drcbrothephotographer', lic: 'CC0', page: 'https://commons.wikimedia.org/wiki/File:Lopeared_rabbit_in_Artis_themepark,_South_Korea.jpg' }
  },
  {
    rodent: 'rabbit', topic: 'Невідкладне',
    title: 'Кролик не їсть: що робити',
    excerpt: 'Відмова від їжі в кролика — не дрібниця: травлення може зупинитися за лічені години. Пояснюємо, які причини бувають і чому не варто чекати до ранку.',
    tags: 'не їсть апетит травлення зуби біль стаз',
    source: 'Walkerville Vet', url: 'https://www.walkervillevet.com.au/blog/rabbit-not-eating/',
    photo: { src: '3/31/Heimtier_004_2023_08_26.jpg', by: 'Friedrich Haag', lic: 'CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Heimtier_004_2023_08_26.jpg' }
  }
];
