/* English text for the blog. Loaded after blog-posts.js on en/blog.html and
 * applied by position, so keep the order of BLOG_EN the same as BLOG_POSTS. */
(function () {
  var LABELS = {
    rat: 'Rats', hamster: 'Hamsters', 'guinea-pig': 'Guinea pigs', chinchilla: 'Chinchillas',
    degu: 'Degus', mouse: 'Mice', rabbit: 'Rabbits'
  };
  var TOPICS = { 'Симптоми': 'Symptoms', 'Харчування': 'Nutrition', 'Догляд': 'Care', 'Невідкладне': 'Urgent' };

  var BLOG_EN = [
    { title: 'How to make a rat’s life more interesting',
      excerpt: 'Rats are smart and curious, and they need new experiences. Boxes, tunnels, ropes and scattered food to forage for all help prevent boredom.',
      tags: 'enrichment toys boredom cage play foraging' },
    { title: 'The 25 most common questions about hamsters',
      excerpt: 'Vets answer what owners ask most: what cage is needed, what to feed, whether two hamsters can live together and how to tell if one is ill.',
      tags: 'cage food questions beginner tips cagemates syrian dwarf' },
    { title: 'Scurvy in guinea pigs: how to spot it in time',
      excerpt: 'Signs of vitamin C deficiency can appear after just 2–3 weeks of poor diet: stiffness, joint pain, bleeding gums and a poor coat. It’s treatable if caught early.',
      tags: 'scurvy vitamin c joints gums coat deficiency' },
    { title: 'Basic guinea pig care',
      excerpt: 'Unlimited hay, fresh vegetables, guinea pig pellets and clean water are the basis of the diet. They also need a roomy cage and company, since they’re social animals.',
      tags: 'hay water cage company diet vegetables' },
    { title: 'Degus at home: what owners need to know',
      excerpt: 'Degus are active by day and live in groups. They need space, a wheel, things to chew and dust baths. Excessive thirst or cloudy eyes are reasons to see a vet.',
      tags: 'cage wheel company dust bath eyes thirst' }
  ];

  BLOG_RODENTS.forEach(function (r) { r.label = LABELS[r.key]; });
  Object.keys(TOPICS).forEach(function (uk) {
    BLOG_TOPICS[TOPICS[uk]] = BLOG_TOPICS[uk];
    delete BLOG_TOPICS[uk];
  });
  BLOG_POSTS.forEach(function (p, i) {
    p.topic = TOPICS[p.topic];
    p.title = BLOG_EN[i].title;
    p.excerpt = BLOG_EN[i].excerpt;
    p.tags = BLOG_EN[i].tags;
  });
})();
