/* Hero: the photos and emoji around the phone drift a little away from the cursor, lightly.
 * Within ~420px of the pointer each one is pushed up to ~22px along the line from the pointer,
 * more the closer it is. The listener is on the whole page, so nothing above the hero can swallow it.
 * Off for touch screens and when reduced motion is requested. */
(function () {
  if (!matchMedia('(hover: hover)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var R = 420, MAX = 22;
  var items = [].slice.call(document.querySelectorAll('.stage .hb, .stage .hi'));
  if (!items.length) return;
  items.forEach(function (el) {
    el.style.transition = 'opacity .7s, transform .6s cubic-bezier(.16, 1, .3, 1)';
    el._inner = el.closest('.stage-inner');
    el._ox = el._oy = 0;                          // the offset asked for last time, in screen px
  });
  var x = -9999, y = -9999, queued = false;

  function apply() {
    queued = false;
    items.forEach(function (el) {
      var b = el.getBoundingClientRect();
      if (!b.width) return;                       // a stage hidden at this screen size
      var s = el._inner.getBoundingClientRect().width / el._inner.offsetWidth || 1;   // the stage is scaled to fit
      // Where the item sits without our push, so the push does not feed back into itself.
      var cx = b.left + b.width / 2 - el._ox, cy = b.top + b.height / 2 - el._oy;
      var dx = cx - x, dy = cy - y;
      var d = Math.max(Math.hypot(dx, dy), 40);
      var k = d < R ? Math.pow(1 - d / R, 1.4) * MAX / d : 0;
      el._ox = dx * k; el._oy = dy * k;
      el.style.transform = k ? 'translate3d(' + (el._ox / s).toFixed(1) + 'px,' + (el._oy / s).toFixed(1) + 'px,0)' : '';
    });
  }
  function reset() { x = y = -9999; apply(); }

  addEventListener('pointermove', function (e) {
    x = e.clientX; y = e.clientY;
    if (!queued) { queued = true; requestAnimationFrame(apply); }
  }, { passive: true });
  document.addEventListener('mouseout', function (e) { if (!e.relatedTarget) reset(); });   // the pointer left the window
  addEventListener('blur', reset);
})();
