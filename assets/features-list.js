/* "What Roddi Health can do": highlight the feature whose card is mid-screen. */
(function () {
  var links = document.querySelectorAll('[data-feat-link]');
  if (!links.length || !('IntersectionObserver' in window)) return;
  var spy = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (l) { l.classList.toggle('is-active', l.dataset.featLink === e.target.dataset.feat); });
    });
  }, { rootMargin: '-45% 0px -45% 0px' });
  document.querySelectorAll('[data-feat]').forEach(function (el) { spy.observe(el); });
})();
