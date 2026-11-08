/* "Who it's for" photos, placed from JS so tilt and drop follow each card's position.
 * Wider screens: an endless row drifting right to left.
 * Phones: one centred card that changes to the next every few seconds. */
(function () {
  var root = document.querySelector('[data-pet-carousel]');
  if (!root) return;

  var SPEED = 30;      // px per second (drift)
  var HOLD = 2600;     // ms a card stays centred (phones)
  var SNAP = 320;      // ms of the change to the next card (phones)
  var TILT = 4.5;      // degrees per card away from the centre
  var DROP = 7;        // px of drop, grows with distance squared
  var MAX_TILT = 14;

  // A second copy keeps the row full on very wide screens.
  [].slice.call(root.children).forEach(function (c) { root.appendChild(c.cloneNode(true)); });
  var cards = [].slice.call(root.children);
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = matchMedia('(max-width: 767px)');
  var cardW, step, loop, centre, pos = 0, last = 0, hovering = false, visible = false, frame = 0;
  var from = 0, to = 0, changeStart = 0, holdStart = 0;

  function measure() {
    cardW = cards[0].offsetWidth;
    step = cardW * (phone.matches ? 1.06 : 1.1);
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

  function snapToCard() {
    pos = (Math.round(pos / step) * step) % loop;
    changeStart = 0;
  }

  function tickPhone(now) {
    if (changeStart) {
      var p = Math.min((now - changeStart) / SNAP, 1);
      pos = from + (to - from) * (1 - Math.pow(1 - p, 3));
      place();
      if (p === 1) { pos = to % loop; changeStart = 0; holdStart = now; }
    } else if (now - holdStart >= HOLD) {
      from = pos; to = pos + step; changeStart = now;
    }
  }

  function tick(now) {
    frame = 0;
    if (!visible || still) return;
    if (phone.matches) {
      if (!holdStart) holdStart = now;
      tickPhone(now);
    } else {
      if (last && !hovering) pos = (pos + Math.min(now - last, 100) / 1000 * SPEED) % loop;
      last = now;
      place();
    }
    frame = requestAnimationFrame(tick);
  }

  function start() { last = 0; holdStart = 0; if (!frame) frame = requestAnimationFrame(tick); }

  function resized() {
    var share = step ? pos / step : 0;
    measure();
    pos = share * step;
    if (phone.matches) snapToCard();
    place();
  }

  root.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hovering = true; });
  root.addEventListener('pointerleave', function () { hovering = false; });
  addEventListener('resize', resized);
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible) start();
  }).observe(root);

  measure();
  place();
})();
