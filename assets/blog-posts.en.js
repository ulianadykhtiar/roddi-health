/* English text for the blog. Loaded after blog-posts.js on en/blog.html and
 * applied by position, so keep the order of BLOG_EN the same as BLOG_POSTS. */
(function () {
  var LABELS = {
    rat: 'Rats', hamster: 'Hamsters', 'guinea-pig': 'Guinea pigs', chinchilla: 'Chinchillas',
    degu: 'Degus', mouse: 'Mice', rabbit: 'Rabbits'
  };
  var TOPICS = { 'Симптоми': 'Symptoms', 'Харчування': 'Nutrition', 'Догляд': 'Care', 'Невідкладне': 'Urgent' };

  var BLOG_EN = [
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
