/* Hero: the photos and emoji around the phone drift a little away from the cursor, very lightly.
 * Within ~260px of the pointer each one is pushed up to ~14px along the line from the pointer;
 * the existing slow transition on [data-reveal] makes the movement soft. Off for touch screens
 * and when reduced motion is requested. */
(function () {
  if (!matchMedia('(hover: hover)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var R = 260, MAX = 14;
  document.querySelectorAll('.stage').forEach(function (stage) {
    var items = [].slice.call(stage.querySelectorAll('.hb, .hi'));
    if (!items.length) return;
    function reset() { items.forEach(function (el) { el.style.transform = ''; }); }
    stage.addEventListener('pointermove', function (e) {
      items.forEach(function (el) {
        var b = el.getBoundingClientRect();
        var dx = b.left + b.width / 2 - e.clientX, dy = b.top + b.height / 2 - e.clientY;
        var d = Math.hypot(dx, dy) || 1;
        var k = d < R ? Math.pow(1 - d / R, 2) * MAX / d : 0;
        el.style.transform = k ? 'translate3d(' + (dx * k).toFixed(1) + 'px,' + (dy * k).toFixed(1) + 'px,0)' : '';
      });
    });
    stage.addEventListener('pointerleave', reset);
  });
})();
