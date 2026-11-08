/* "Who it's for" photos: an endless row sliding right to left along a gentle arc.
 * Cards are placed from JS each frame, so tilt and drop follow their position. */
(function () {
  var root = document.querySelector('[data-pet-carousel]');
  if (!root) return;

  var SPEED = 30;      // px per second
  var TILT = 4.5;      // degrees per card away from the centre
  var DROP = 7;        // px of drop, grows with distance squared
  var MAX_TILT = 14;

  // A second copy keeps the row full on very wide screens.
  [].slice.call(root.children).forEach(function (c) { root.appendChild(c.cloneNode(true)); });
  var cards = [].slice.call(root.children);
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cardW, step, loop, centre, pos = 0, last = 0, hovering = false, visible = false, frame = 0;

  function measure() {
    cardW = cards[0].offsetWidth;
    step = cardW * 1.1;
    loop = step * cards.length;
    centre = root.clientWidth / 2;
  }

  function place() {
    cards.forEach(function (c, i) {
      var x = ((i * step - pos) % loop + loop) % loop;
      if (x >= loop / 2) x -= loop;
      var t = x / step;
      var tilt = Math.max(-MAX_TILT, Math.min(MAX_TILT, t * TILT));
      c.style.transform = 'translate3d(' + (centre + x - cardW / 2).toFixed(1) + 'px,' + (t * t * DROP).toFixed(1) + 'px,0) rotate(' + tilt.toFixed(2) + 'deg)';
    });
  }

  function tick(now) {
    frame = 0;
    if (!visible || still) return;
    if (last && !hovering) pos = (pos + Math.min(now - last, 100) / 1000 * SPEED) % loop;
    last = now;
    place();
    frame = requestAnimationFrame(tick);
  }

  function start() { last = 0; if (!frame) frame = requestAnimationFrame(tick); }

  root.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hovering = true; });
  root.addEventListener('pointerleave', function () { hovering = false; });
  addEventListener('resize', function () { measure(); place(); });
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible) start();
  }).observe(root);

  measure();
  place();
})();
