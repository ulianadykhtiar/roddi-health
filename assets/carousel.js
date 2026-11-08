/* "Who it's for" photos on one circular arc, placed from JS.
 * Wider screens: an endless row drifting right to left.
 * Phones: one centred card that changes to the next every few seconds.
 * A finger can drag the row on any touch screen; on phones it then settles on a card. */
(function () {
  var root = document.querySelector('[data-pet-carousel]');
  if (!root) return;

  var SPEED = 30;           // px per second (drift)
  var HOLD = 2600;          // ms a card stays centred (phones)
  var SNAP = 320;           // ms of a change to another card (phones)
  var GAP = 1.17;           // distance between cards, in card widths
  var PHONE_GAP = 1.2;
  var ANGLE = 6, PHONE_ANGLE = 10;  // degrees along the arc from one card to the next
  var FLICK_FADE = 500;     // ms for a flick to lose most of its speed (drift)
  var FLICK_REACH = 0.18;   // s of flick speed counted when choosing a card (phones)

  // A second copy keeps the row full on very wide screens.
  [].slice.call(root.children).forEach(function (c) { root.appendChild(c.cloneNode(true)); });
  var cards = [].slice.call(root.children);
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phone = matchMedia('(max-width: 767px)');
  var cardW, step, loop, centre, pos = 0, last = 0, hovering = false, visible = false, frame = 0;
  var dragging = false, dragX = 0, dragT = 0, flick = 0; // flick is px per second
  var from = 0, to = 0, changeStart = 0, holdStart = 0;

  function wrap(p) { return (p % loop + loop) % loop; }

  function measure() {
    cardW = cards[0].offsetWidth;
    step = cardW * (phone.matches ? PHONE_GAP : GAP);
    loop = step * cards.length;
    centre = root.clientWidth / 2;
  }

  function place() {
    // Position and tilt both come from the same angle on the circle.
    var perCard = (phone.matches ? PHONE_ANGLE : ANGLE) * Math.PI / 180, radius = step / perCard;
    cards.forEach(function (c, i) {
      var x = wrap(i * step - pos);
      if (x >= loop / 2) x -= loop;
      var a = x / radius;
      var left = centre + radius * Math.sin(a) - cardW / 2, down = radius * (1 - Math.cos(a));
      c.style.transform = 'translate3d(' + left.toFixed(1) + 'px,' + down.toFixed(1) + 'px,0) rotate(' + (a * 180 / Math.PI).toFixed(2) + 'deg)';
    });
  }

  function changeTo(target, now) { from = pos; to = target; changeStart = now; }

  function tickPhone(now) {
    if (changeStart) {
      var p = Math.min((now - changeStart) / SNAP, 1);
      pos = from + (to - from) * (1 - Math.pow(1 - p, 3));
      place();
      if (p === 1) { pos = wrap(to); changeStart = 0; holdStart = now; }
    } else if (!still && now - holdStart >= HOLD) {
      changeTo((Math.round(pos / step) + 1) * step, now);
    }
  }

  function tickDrift(ms) {
    var drift = still || hovering ? 0 : SPEED;
    pos = wrap(pos + (drift + flick) * ms / 1000);
    flick *= Math.exp(-ms / FLICK_FADE);
    if (Math.abs(flick) < 1) flick = 0;
    place();
  }

  function tick(now) {
    frame = 0;
    if (!visible) return;
    var ms = last ? Math.min(now - last, 100) : 0;
    last = now;
    if (!dragging) {
      if (phone.matches) { if (!holdStart) holdStart = now; tickPhone(now); }
      else tickDrift(ms);
    }
    if (!still || flick || changeStart) frame = requestAnimationFrame(tick);
  }

  function start() { last = 0; holdStart = 0; if (!frame) frame = requestAnimationFrame(tick); }

  // Finger: touch-action in the CSS leaves vertical swipes to the page.
  root.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse') return;
    dragging = true; dragX = e.clientX; dragT = e.timeStamp; flick = 0; changeStart = 0;
    try { root.setPointerCapture(e.pointerId); } catch (err) {}
  });
  root.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var dx = e.clientX - dragX, ms = Math.max(e.timeStamp - dragT, 1);
    pos = wrap(pos - dx);
    flick = flick * 0.6 + (-dx / ms * 1000) * 0.4;
    dragX = e.clientX; dragT = e.timeStamp;
    place();
  });
  function release(e) {
    if (!dragging) return;
    dragging = false;
    if (e.timeStamp - dragT > 120) flick = 0; // finger rested before lifting
    if (phone.matches) {
      changeTo(Math.round((pos + flick * FLICK_REACH) / step) * step, performance.now());
      flick = 0;
    }
    if (!frame) { last = 0; frame = requestAnimationFrame(tick); }
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);

  root.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hovering = true; });
  root.addEventListener('pointerleave', function () { hovering = false; });
  addEventListener('resize', function () {
    var share = step ? pos / step : 0;
    measure();
    pos = phone.matches ? wrap(Math.round(share) * step) : share * step;
    changeStart = 0;
    place();
  });
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible) start();
  }).observe(root);

  measure();
  place();
})();
