/* Microsoft Clarity: heatmaps and session recordings for roddihealth.app.
 * Runs only on the live domain, so local and preview visits are not recorded. */
(function (c, l, a, r, i, t, y) {
  if (c.location.hostname !== 'roddihealth.app') return;
  c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
  t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
  y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
})(window, document, 'clarity', 'script', 'zah0cbuajb');
