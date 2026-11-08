/* English text for the blog. Loaded after blog-posts.js on en/blog.html and
 * applied by position, so keep the order of BLOG_EN the same as BLOG_POSTS. */
(function () {
  var LABELS = {
    rat: 'Rats', hamster: 'Hamsters', 'guinea-pig': 'Guinea pigs', chinchilla: 'Chinchillas',
    degu: 'Degus', mouse: 'Mice', rabbit: 'Rabbits'
  };
  var TOPICS = { 'Симптоми': 'Symptoms', 'Харчування': 'Nutrition', 'Догляд': 'Care', 'Невідкладне': 'Urgent' };

  var BLOG_EN = [
    { title: 'Respiratory infections in rats: signs to watch for',
      excerpt: 'Sneezing, wheezing or “clicking” when breathing, nasal discharge and reddish crusts around the eyes are the most common signals. Left untreated, an infection can be dangerous, so these symptoms call for a vet visit.',
      tags: 'breathing sneezing wheezing runny nose porphyrin antibiotics cold' },
    { title: 'Mycoplasmosis: why a rat struggles to breathe',
      excerpt: 'Many rats carry mycoplasma and show no signs for years, with flare-ups triggered by stress. A dirty cage that smells of ammonia irritates the airways, so regular cleaning is part of prevention.',
      tags: 'mycoplasma breathing ammonia cleaning cage stress chronic' },
    { title: 'What to feed a rat and how to watch its weight',
      excerpt: 'A complete pelleted rat food is the basis of the diet, with vegetables, a little fruit and protein treats as extras. Rats gain weight easily, so it’s worth controlling portions.',
      tags: 'food diet pellets weight obesity treats fruit' },
    { title: 'How to make a rat’s life more interesting',
      excerpt: 'Rats are smart and curious, and they need new experiences. Boxes, tunnels, ropes and scattered food to forage for all help prevent boredom.',
      tags: 'enrichment toys boredom cage play foraging' },
    { title: 'Wet tail in hamsters: why it’s urgent',
      excerpt: 'A wet, soiled tail, lethargy and refusing food can mean a severe intestinal infection. The condition worsens quickly, so a hamster needs to see a vet within the first day.',
      tags: 'wet tail diarrhea intestines infection lethargy antibiotics' },
    { title: 'The 25 most common questions about hamsters',
      excerpt: 'Vets answer what owners ask most: what cage is needed, what to feed, whether two hamsters can live together and how to tell if one is ill.',
      tags: 'cage food questions beginner tips cagemates syrian dwarf' },
    { title: 'Why guinea pigs need vitamin C',
      excerpt: 'Like humans, guinea pigs can’t make their own vitamin C, so they need it from food every day. Bell peppers and leafy greens are good sources. Vitamin C added to drinking water is unreliable.',
      tags: 'vitamin c scurvy pepper greens diet supplements' },
    { title: 'Scurvy in guinea pigs: how to spot it in time',
      excerpt: 'Signs of vitamin C deficiency can appear after just 2–3 weeks of poor diet: stiffness, joint pain, bleeding gums and a poor coat. It’s treatable if caught early.',
      tags: 'scurvy vitamin c joints gums coat deficiency' },
    { title: 'Basic guinea pig care',
      excerpt: 'Unlimited hay, fresh vegetables, guinea pig pellets and clean water are the basis of the diet. They also need a roomy cage and company, since they’re social animals.',
      tags: 'hay water cage company diet vegetables' },
    { title: 'Chinchilla dust baths: how and how often',
      excerpt: 'Chinchillas aren’t bathed in water because their dense fur dries poorly. Instead, offer special bathing dust and remove the bath after about half an hour to avoid irritating the eyes.',
      tags: 'dust bath bathing fur coat eyes sand' },
    { title: 'Chinchilla health: teeth, coat and digestion',
      excerpt: 'A chinchilla’s teeth grow throughout life, so it needs unlimited hay and safe things to chew. Drooling or refusing food are reasons to have a vet check the teeth.',
      tags: 'teeth hay chewing drool digestion coat overheating' },
    { title: 'Degus and sugar: how to prevent diabetes',
      excerpt: 'Degus process sugar poorly and are prone to diabetes. It’s best to avoid fruit, dried fruit and sweet vegetables. Hay and degu food should form the basis of the diet. Diabetes is easier to prevent than to treat.',
      tags: 'diabetes sugar fruit diet hay cataract thirst' },
    { title: 'Degus at home: what owners need to know',
      excerpt: 'Degus are active by day and live in groups. They need space, a wheel, things to chew and dust baths. Excessive thirst or cloudy eyes are reasons to see a vet.',
      tags: 'cage wheel company dust bath eyes thirst' },
    { title: 'Mouse health: a one-minute daily check',
      excerpt: 'Mice often hide pain, so it’s best to catch changes early: check the eyes, nose, coat, breathing and droppings. Sneezing or “chattering” when breathing are reasons to see a vet.',
      tags: 'check sneezing breathing droppings coat pain' },
    { title: 'Routine care for pet mice',
      excerpt: 'An owner’s guide from the MSD Vet Manual: how to set up housing, how often to clean, what to feed and how to notice the first signs of illness.',
      tags: 'cage cleaning food prevention vet water' },
    { title: 'GI stasis in rabbits: when to raise the alarm',
      excerpt: 'A rabbit that isn’t eating and hasn’t passed droppings for several hours needs an urgent vet visit. The best prevention is a diet based on hay, with only small amounts of pellets and fruit.',
      tags: 'gi stasis digestion droppings hay not eating bloating' },
    { title: 'Rabbit not eating: what to do',
      excerpt: 'A rabbit refusing food is no small matter: digestion can stop within hours. We explain the possible causes and why you shouldn’t wait until morning.',
      tags: 'not eating appetite digestion teeth pain stasis' }
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
