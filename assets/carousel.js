/* "Who it's for" photos, placed from JS so tilt and drop follow each card's position.
 * The row drifts right to left without end, along one circular arc. On touch screens a finger can drag it
 * and flick it faster; it then eases back to the normal drift. */
(function () {
  var root = document.querySelector('[data-pet-carousel]');
  if (!root) return;

  var SPEED = 30;           // px per second
  var GAP = 1.17;           // distance between cards, in card widths
  var PHONE_GAP = 1.12;
  var ANGLE = 6, PHONE_ANGLE = 10;  // degrees along the arc from one card to the next
  var FLICK_FADE = 500;     // ms for a flick to lose most of its speed

  // A second copy keeps the row full on very wide screens.
  [].slice.call(root.children).forEach(function (c) { root.appendChild(c.cloneNode(true)); });
  var cards = [].slice.call(root.children);
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = matchMedia('(max-width: 767px)');
  var cardW, step, loop, centre, pos = 0, last = 0, hovering = false, visible = false, frame = 0;
  var dragging = false, dragX = 0, dragT = 0, flick = 0; // flick is px per second

  function measure() {
    cardW = cards[0].offsetWidth;
    step = cardW * (phone.matches ? PHONE_GAP : GAP);
    loop = step * cards.length;
    centre = root.clientWidth / 2;
  }

  function place() {
    // Cards sit on one circle: position and tilt both come from the same angle.
    var perCard = (phone.matches ? PHONE_ANGLE : ANGLE) * Math.PI / 180, radius = step / perCard;
    cards.forEach(function (c, i) {
      var x = ((i * step - pos) % loop + loop) % loop;
      if (x >= loop / 2) x -= loop;
      var a = x / radius;
      var left = centre + radius * Math.sin(a) - cardW / 2, down = radius * (1 - Math.cos(a));
      c.style.transform = 'translate3d(' + left.toFixed(1) + 'px,' + down.toFixed(1) + 'px,0) rotate(' + (a * 180 / Math.PI).toFixed(2) + 'deg)';
    });
  }

  function tick(now) {
    frame = 0;
    if (!visible) return;
    var ms = last ? Math.min(now - last, 100) : 0;
    last = now;
    if (!dragging) {
      var drift = still || hovering ? 0 : SPEED;
      pos = ((pos + (drift + flick) * ms / 1000) % loop + loop) % loop;
      flick *= Math.exp(-ms / FLICK_FADE);
      if (Math.abs(flick) < 1) flick = 0;
      place();
    }
    if (!still || flick) frame = requestAnimationFrame(tick);
  }

  function start() { last = 0; if (!frame) frame = requestAnimationFrame(tick); }

  // Finger: touch-action in the CSS leaves vertical swipes to the page.
  root.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse') return;
    dragging = true; dragX = e.clientX; dragT = e.timeStamp; flick = 0;
    try { root.setPointerCapture(e.pointerId); } catch (err) {}
  });
  root.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var dx = e.clientX - dragX, ms = Math.max(e.timeStamp - dragT, 1);
    pos = ((pos - dx) % loop + loop) % loop;
    flick = flick * 0.6 + (-dx / ms * 1000) * 0.4;
    dragX = e.clientX; dragT = e.timeStamp;
    place();
  });
  function release(e) {
    if (!dragging) return;
    dragging = false;
    if (e.timeStamp - dragT > 120) flick = 0; // finger rested before lifting
    start();
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);

  root.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hovering = true; });
  root.addEventListener('pointerleave', function () { hovering = false; });
  addEventListener('resize', function () {
    var share = step ? pos / step : 0;
    measure();
    pos = share * step;
    place();
  });
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible) start();
  }).observe(root);

  measure();
  place();
})();
