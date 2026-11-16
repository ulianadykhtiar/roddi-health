/* Roddi Health — blog posts.
 *
 * Cards that still lead to articles on other sites: a short summary in our own
 * words and a link to the original. The page marks each one as an article on an
 * external site. They are being replaced one by one with our own articles
 * (tools/build-articles.py). When an article replaces a card, remove the card here
 * and the entry at the same position in blog-posts.en.js, then run
 * tools/build-articles.py (it versions the script URLs so browsers fetch the new
 * file) and tools/build-blog-lists.py. Never translate or copy the original text.
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
  }
];
