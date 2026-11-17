/* Language choice: Ukrainian or English.
 *
 * - Nothing is redirected on the first visit. If the browser's language differs from the page's, a small dialog asks which
 *   language to show. Search engines never see it (no script, no saved choice), so they index both versions as they are.
 * - The choice is kept in localStorage (roddi:lang). It is also saved when a visitor uses the UA/EN switcher.
 * - Later, a visitor who chose a language and lands on the other version from outside the site (a search result, a link)
 *   is taken to the version they chose.
 * - The cookie banner (clarity.js) waits until the dialog is closed, so the two never stack.
 * Both language versions are linked with <link rel="alternate" hreflang="..."> in the head; that is where the target comes from. */
(function (w, d) {
  var KEY = 'roddi:lang';
  var cur = d.documentElement.lang === 'en' ? 'en' : 'uk';
  function read() { try { var v = localStorage.getItem(KEY); return v === 'en' || v === 'uk' ? v : null; } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function alt(lang) {
    var l = d.querySelector('link[rel="alternate"][hreflang="' + lang + '"]');
    if (!l) return null;
    var p; try { p = new URL(l.href).pathname; } catch (e) { return null; }
    if (!/(^|\.)roddihealth\.app$/.test(location.hostname) && p === '/en') p = '/en/index.html'; // local server has no clean URLs
    return p;
  }

  // The switcher in the header counts as a choice too.
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.lang-opt');
    if (a && (a.getAttribute('lang') === 'en' || a.getAttribute('lang') === 'uk')) write(a.getAttribute('lang'));
  });

  var saved = read();
  var first = ((navigator.languages && navigator.languages[0]) || navigator.language || 'uk').toLowerCase();
  var wanted = first.indexOf('uk') === 0 ? 'uk' : 'en';

  if (saved) {
    // Arrived from outside the site on the other version: take them to the one they chose.
    var fromOutside = !d.referrer || new URL(d.referrer, location.href).origin !== location.origin;
    var target = saved !== cur && fromOutside ? alt(saved) : null;
    if (target) { location.replace(target + location.search + location.hash); return; }
    return;
  }
  if (wanted === cur || !alt(wanted)) return;

  w.roddiLangPending = true;

  function finish(choice) {
    write(choice);
    w.roddiLangPending = false;
    w.dispatchEvent(new Event('roddi:lang-done'));
  }

  function show() {
    var st = d.createElement('style');
    st.textContent = '.lp{border:0;padding:0;margin:auto;inset:0;background:transparent;max-width:none;max-height:none;color:#0f0f11;font:400 15px/1.45 Onest,system-ui,sans-serif}' +
      '.lp::backdrop{background:rgba(15,15,17,.45);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}' +
      '.lp-box{box-sizing:border-box;width:min(400px,calc(100vw - 32px));padding:28px 24px 24px;border-radius:28px;background:#fff;text-align:center;box-shadow:0 24px 64px -24px rgba(15,15,17,.5)}' +
      '.lp-t{margin:0 0 4px;font-size:22px;line-height:1.15;font-weight:600;letter-spacing:-.02em}.lp-s{margin:0 0 20px;color:#6e727a}' +
      '.lp-row{display:flex;gap:10px}.lp-b{flex:1;min-height:48px;border:0;border-radius:999px;font:500 15px Onest,system-ui,sans-serif;cursor:pointer;background:#fff;color:#0f0f11;box-shadow:inset 0 0 0 1px #d9dce1;transition:translate .2s ease}' +
      '.lp-b:hover{translate:0 -1px}.lp-b.is-main{background:#0f0f11;color:#fff;box-shadow:none}.lp-b:focus-visible{outline:2px solid #3172c8;outline-offset:2px}' +
      '@media (prefers-reduced-motion:reduce){.lp-b{transition:none}}';
    d.head.appendChild(st);
    var dlg = d.createElement('dialog');
    dlg.className = 'lp';
    dlg.setAttribute('aria-labelledby', 'lp-t');
    var names = { uk: 'Українська', en: 'English' };
    var order = wanted === 'en' ? ['en', 'uk'] : ['uk', 'en'];
    dlg.innerHTML = '<div class="lp-box"><h2 class="lp-t" id="lp-t">Choose your language</h2><p class="lp-s">Оберіть мову сайту</p><div class="lp-row">' +
      order.map(function (l, i) { return '<button type="button" class="lp-b' + (i === 0 ? ' is-main' : '') + '" data-l="' + l + '" lang="' + l + '">' + names[l] + '</button>'; }).join('') + '</div></div>';
    d.body.appendChild(dlg);
    var done = false;
    function pick(l) {
      if (done) return; done = true;
      finish(l);
      dlg.close();
      var target = l !== cur ? alt(l) : null;
      if (target) location.href = target + location.search + location.hash; else dlg.remove();
    }
    dlg.addEventListener('click', function (e) { var b = e.target.closest('button[data-l]'); if (b) pick(b.getAttribute('data-l')); });
    dlg.addEventListener('cancel', function (e) { e.preventDefault(); pick(cur); }); // Esc keeps the page as it is and remembers that
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    var first = dlg.querySelector('button'); if (first) first.focus();
  }
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', show); else show();
})(window, document);
