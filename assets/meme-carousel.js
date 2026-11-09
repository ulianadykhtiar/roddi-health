/* "Sound familiar?" on phones: the same arc carousel as "Who it's for".
 * One centred card that changes every few seconds; a finger can drag it. */
(function () {
  var root = document.querySelector('.meme-row');
  if (!root) return;

  var HOLD = 1400, SNAP = 240, GAP = 1.12;
  var ANGLE = 10 * Math.PI / 180, FLICK_REACH = 0.18;

  var originals = [].slice.call(root.children);
  originals.forEach(function (c) {
    var copy = c.cloneNode(true);
    copy.classList.add('meme-clone');
    copy.setAttribute('aria-hidden', 'true');
    copy.removeAttribute('data-reveal');
    root.appendChild(copy);
  });
  var cards = [].slice.call(root.children);
  var phone = matchMedia('(max-width: 639px)');
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var active = false, visible = false, frame = 0;
  var cardW = 0, step = 1, loop = 1, centre = 0, pos = 0;
  var dragging = false, dragX = 0, dragT = 0, flick = 0;
  var from = 0, to = 0, changeStart = 0, holdStart = 0;

  function wrap(p) { return (p % loop + loop) % loop; }

  function measure() {
    cardW = cards[0].offsetWidth;
    step = cardW * GAP;
    loop = step * cards.length;
    centre = root.clientWidth / 2;
    var tallest = 0;
    cards.forEach(function (c) { tallest = Math.max(tallest, c.offsetHeight); });
    root.style.height = tallest + 56 + 'px';
  }

  function place() {
    var radius = step / ANGLE;
    cards.forEach(function (c, i) {
      var x = wrap(i * step - pos);
      if (x >= loop / 2) x -= loop;
      var a = x / radius;
      var left = centre + radius * Math.sin(a) - cardW / 2, down = radius * (1 - Math.cos(a));
      c.style.transform = 'translate3d(' + left.toFixed(1) + 'px,' + down.toFixed(1) + 'px,0) rotate(' + (a * 180 / Math.PI).toFixed(2) + 'deg)';
    });
  }

  function changeTo(target, now) { from = pos; to = target; changeStart = now; }

  function tick(now) {
    frame = 0;
    if (!visible || !active) return;
    if (!dragging) {
      if (!holdStart) holdStart = now;
      if (changeStart) {
        var p = Math.min((now - changeStart) / SNAP, 1);
        pos = from + (to - from) * (1 - Math.pow(1 - p, 3));
        place();
        if (p === 1) { pos = wrap(to); changeStart = 0; holdStart = now; }
      } else if (!still && now - holdStart >= HOLD) {
        changeTo((Math.round(pos / step) + 1) * step, now);
      }
    }
    if (!still || changeStart) frame = requestAnimationFrame(tick);
  }
  function start() { holdStart = 0; if (!frame) frame = requestAnimationFrame(tick); }

  root.addEventListener('pointerdown', function (e) {
    if (!active || e.pointerType === 'mouse') return;
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
    if (e.timeStamp - dragT > 120) flick = 0;
    changeTo(Math.round((pos + flick * FLICK_REACH) / step) * step, performance.now());
    flick = 0;
    if (!frame) frame = requestAnimationFrame(tick);
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);

  function setup() {
    active = phone.matches;
    root.classList.toggle('is-carousel', active);
    if (active) {
      originals.forEach(function (c) { c.removeAttribute('data-reveal'); });
      var share = step > 1 ? pos / step : 0;
      measure();
      pos = wrap(Math.round(share) * step);
      changeStart = 0;
      place();
      if (visible) start();
    } else {
      cards.forEach(function (c) { c.style.transform = ''; });
      root.style.height = '';
    }
  }

  addEventListener('resize', setup);
  addEventListener('load', setup);
  if (document.fonts) document.fonts.ready.then(setup);
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible && active) start();
  }).observe(root);
  setup();
})();
