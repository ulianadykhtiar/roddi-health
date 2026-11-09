/* "Why I'm building Roddi Health": a montage of blog videos and stories styled as a story. */
(function () {
  function isVideo(el) { return el.tagName === 'VIDEO'; }
  var story = document.querySelector('[data-story]');
  if (!story) return;
  var stage = story.querySelector('.story-stage');
  var media = [].slice.call(stage.children);
  var videos = media.filter(isVideo);
  var barsBox = story.querySelector('.story-bars');
  var button = story.querySelector('.story-toggle');
  var comments = [].slice.call(story.querySelectorAll('.story-c'));
  var en = document.documentElement.lang === 'en';
  var labels = en ? ['Pause video', 'Play video'] : ['Призупинити відео', 'Відтворити відео'];
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // m: index in the stage (videos first, then the photo), a/b: start and end
  // in seconds. Neighbouring clips always use different media, so the next
  // video can be sought in advance and the cut lands without a stall.
  var CLIPS = [
    { m: 0, a: 0.2, b: 3.4 },
    { m: 1, a: 2.0, b: 5.0 },
    { m: 5, a: 0, b: 3.2 },
    { m: 2, a: 6.0, b: 9.0 },
    { m: 0, a: 13.0, b: 16.2 },
    { m: 3, a: 0.5, b: 3.7 },
    { m: 4, a: 0.5, b: 3.7 }
  ];
  var bars = CLIPS.map(function () {
    var bar = document.createElement('span');
    var fill = document.createElement('i');
    bar.className = 'story-bar';
    bar.appendChild(fill);
    barsBox.appendChild(bar);
    return fill;
  });

  var clip = 0;
  var still = 0; // seconds shown of the current photo
  var lastTick = performance.now();
  var userPaused = reduce;
  var inView = !('IntersectionObserver' in window);
  videos.forEach(function (v) { v.muted = true; });

  function current() { return media[CLIPS[clip].m]; }
  function running() { return inView && !document.hidden && !userPaused; }

  function paint() {
    var c = CLIPS[clip];
    var el = current();
    var done = isVideo(el) ? el.currentTime - c.a : still;
    var k = Math.max(0, Math.min(1, done / (c.b - c.a)));
    bars.forEach(function (fill, i) {
      fill.style.transform = 'scaleX(' + (i < clip ? 1 : i > clip ? 0 : k) + ')';
    });
  }

  function sync() {
    var el = current();
    if (isVideo(el)) {
      if (running()) el.play().catch(function () {});
      else el.pause();
    }
    story.classList.toggle('is-paused', userPaused);
    button.setAttribute('aria-label', labels[userPaused ? 1 : 0]);
  }

  function show(n) {
    var was = current();
    if (isVideo(was)) was.pause();
    clip = n % CLIPS.length;
    still = 0;
    var c = CLIPS[clip];
    var el = media[c.m];
    if (isVideo(el) && Math.abs(el.currentTime - c.a) > 0.15) el.currentTime = c.a;
    media.forEach(function (x) { x.classList.toggle('is-live', x === el); });
    stage.style.setProperty('--clip', (c.b - c.a) + 's');
    var next = CLIPS[(clip + 1) % CLIPS.length];
    if (isVideo(media[next.m])) media[next.m].currentTime = next.a;
    sync();
  }

  function tick() {
    var now = performance.now();
    var dt = Math.min(now - lastTick, 300) / 1000;
    lastTick = now;
    var c = CLIPS[clip];
    var el = current();
    if (isVideo(el)) {
      if (!el.paused && el.currentTime >= c.b) { show(clip + 1); return; }
    } else if (running()) {
      still += dt;
      if (still >= c.b - c.a) { show(clip + 1); return; }
    }
    paint();
  }
  (function loop() { tick(); requestAnimationFrame(loop); })();
  setInterval(tick, 200); // rAF rests in throttled frames

  function toggle() { userPaused = !userPaused; sync(); }
  stage.addEventListener('click', toggle);
  button.addEventListener('click', toggle);

  // One comment at a time; the rotation rests while the montage is paused.
  var active = 0;
  if (!reduce && comments.length > 1) {
    setInterval(function () {
      if (!running()) return;
      comments[active].classList.remove('is-on');
      active = (active + 1) % comments.length;
      comments[active].classList.add('is-on');
    }, 4000);
  }

  var loaded = false;
  function warm() {
    if (loaded) return;
    loaded = true;
    videos.forEach(function (v) { v.preload = 'auto'; });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) warm();
      });
    }, { rootMargin: '600px 0px' }).observe(story);
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { inView = e.isIntersecting; sync(); });
    }, { threshold: 0.25 }).observe(story);
  } else { warm(); }
  document.addEventListener('visibilitychange', sync);
  show(0);
})();
