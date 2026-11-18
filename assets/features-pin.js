/* "Що вміє Roddi Health": on desktop the section is pinned and its cards stack.
 * Scrolling slides the next card up from the bottom over the current one, which
 * shrinks a little; a strip of the next card always peeks below, so it is clear
 * the block scrolls. Each card holds still for a moment before the next arrives.
 * Clicking a list item scrolls to its card. Scenes are zoomed to fit their card. */
(function () {
  var root = document.querySelector('[data-fp]');
  if (!root) return;
  var stage = root.querySelector('.fp-stage');
  var links = [].slice.call(root.querySelectorAll('[data-fp-link]'));
  var slides = [].slice.call(root.querySelectorAll('[data-fp-slide]'));
  var n = slides.length, current = -1, ticking = false;
  var wide = matchMedia('(min-width: 1024px)');
  var HOLD = 0.3;   // share of each step a card stays put before the next one moves
  var GAP = 14;     // px between a card and the next one below it

  function setActive(i) {
    if (i === current) return;
    current = i;
    links.forEach(function (l, k) { l.classList.toggle('is-active', k === i); l.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); });
    runNumbers(slides[i]);
  }

  // Numbers in the active card count up from data-from to their value; [data-wob] ones then keep
  // ticking by a point or two, like live data. Without motion (or JS) they simply show the value.
  var calm = matchMedia('(prefers-reduced-motion: reduce)');
  var wobbleTimer = 0;
  function show(el, v) { el.textContent = Math.round(v); }
  function runNumbers(slide) {
    clearInterval(wobbleTimer);
    if (!slide || calm.matches || !wide.matches) return;
    var nums = [].slice.call(slide.querySelectorAll('[data-cnt]'));
    var t0 = performance.now();
    nums.forEach(function (el) { if (el.dataset.from) show(el, +el.dataset.from); });
    (function tick(now) {
      var k = Math.min(((now || performance.now()) - t0 - 250) / 1300, 1);
      if (k < 0) { requestAnimationFrame(tick); return; }
      var e = 1 - Math.pow(1 - k, 3);
      nums.forEach(function (el) { if (el.dataset.from) show(el, +el.dataset.from + (+el.dataset.cnt - +el.dataset.from) * e); });
      if (k < 1) requestAnimationFrame(tick);
    })();
    wobbleTimer = setInterval(function () {
      slide.querySelectorAll('[data-wob]').forEach(function (el) {
        var v = +el.dataset.cnt; show(el, v + Math.round((Math.random() - .5) * 4));
      });
    }, 1700);
  }

  function ease(t) { return t * t * (3 - 2 * t); }

  // Scroll position inside the section -> card position p in [0, n-1], with a hold on each card.
  function progress() {
    var span = root.offsetHeight - innerHeight;
    var r = span > 0 ? Math.min(Math.max(-root.getBoundingClientRect().top / span, 0), 1) * (n - 1) : 0;
    var k = Math.floor(r), f = r - k;
    return k + (f < HOLD ? 0 : ease((f - HOLD) / (1 - HOLD)));
  }

  function render() {
    ticking = false;
    if (!wide.matches) {
      slides.forEach(function (s) { s.style.transform = ''; s.style.opacity = ''; });
      return;
    }
    var p = progress(), h = slides[0].offsetHeight + GAP;
    slides.forEach(function (s, k) {
      var d = k - p;
      if (d >= 0) {                      // the next card: below, rising into place; later ones hidden
        s.style.transform = 'translate3d(0,' + (Math.min(d, 1.6) * h).toFixed(1) + 'px,0)';
        s.style.opacity = Math.min(Math.max(2 - d, 0), 1).toFixed(2);
      } else {                           // passed cards: stay under the new one, shrink a little
        var b = Math.min(-d, 1);
        s.style.transform = 'translate3d(0,' + (-b * 10).toFixed(1) + 'px,0) scale(' + (1 - b * 0.06).toFixed(3) + ')';
        s.style.opacity = (1 - Math.max(-d - 1, 0)).toFixed(2);
      }
    });
    setActive(Math.round(p));
  }

  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(render); } }

  links.forEach(function (l, i) {
    l.addEventListener('click', function (e) {
      e.preventDefault();
      var top = root.getBoundingClientRect().top + scrollY;
      var span = root.offsetHeight - innerHeight;
      var y = wide.matches ? top + span * i / Math.max(n - 1, 1) + 2 : slides[i].getBoundingClientRect().top + scrollY - 20;
      scrollTo({ top: y, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    });
  });

  // Desktop: zoom each 560×440 scene to fit its card. Phones stack the widgets at full size (CSS).
  function fit() {
    root.querySelectorAll('.fp-scene').forEach(function (sc) {
      var box = sc.parentElement, w = box.clientWidth - 24, h = box.clientHeight - 24;
      sc.style.setProperty('--z', wide.matches ? Math.max(Math.min(w / 560, h / 440, 1.3), 0.4).toFixed(3) : 1);
    });
  }

  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', function () { fit(); render(); });
  if (document.fonts) document.fonts.ready.then(fit);
  fit();
  setActive(0);
  render();
})();
