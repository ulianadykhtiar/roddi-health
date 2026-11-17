/* Microsoft Clarity (heatmaps and session recordings) behind a consent banner.
 *
 * - Clarity loads only on roddihealth.app, so local and preview visits are not recorded.
 * - Until the visitor allows analytics, Clarity is told "denied": it sets no cookies and does
 *   not link visits together (it also holds for visitors from the EEA, the UK and Switzerland,
 *   where Clarity requires a consent signal: window.clarity('consentv2', {...})).
 * - The choice is kept in localStorage under roddi:consent ("granted" or "denied") and can be
 *   changed with the "Cookie settings" button that this script adds to the footer links.
 * The banner shows on every host, so it can be checked locally.
 * Team visits: opening /me once marks this browser (localStorage roddi:internal). Then Clarity never loads and no banner shows. */
(function (c, l, a, r, i, t, y) {
  var KEY = 'roddi:consent';
  var EN = l.documentElement.lang === 'en';
  var live = c.location.hostname === 'roddihealth.app';
  var TEXT = EN
    ? { msg: 'We use Microsoft Clarity to see how people use the site. Allow analytics cookies?', yes: 'Allow', no: 'Decline', more: 'Details', settings: 'Cookie settings', label: 'Cookies', href: '/en/privacy.html#cookies' }
    : { msg: 'Ми використовуємо Microsoft Clarity, щоб бачити, як люди користуються сайтом. Дозволити аналітичні cookies?', yes: 'Дозволити', no: 'Відхилити', more: 'Докладніше', settings: 'Налаштування cookies', label: 'Cookies', href: '/privacy.html#cookies' };

  function internal() { try { return localStorage.getItem('roddi:internal') === '1'; } catch (e) { return false; } }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function signal(granted) {
    if (typeof c[a] === 'function') c[a]('consentv2', { ad_Storage: 'denied', analytics_Storage: granted ? 'granted' : 'denied' });
  }

  if (live && !internal()) {
    c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
    signal(read() === 'granted'); // queued first, applied when the tag loads
    t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
    y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
  }

  var css = '.ck{position:fixed;left:16px;bottom:16px;z-index:90;box-sizing:border-box;width:min(390px,calc(100vw - 32px));padding:18px;border:1px solid #e7e9ec;border-radius:24px;background:#fff;color:#0f0f11;font:400 14px/1.45 Onest,system-ui,sans-serif;box-shadow:0 1px 2px rgba(15,15,17,.06),0 24px 56px -24px rgba(15,15,17,.4);opacity:0;transform:translateY(12px);transition:opacity .35s ease,transform .45s cubic-bezier(.16,1,.3,1)}' +
    '.ck.is-in{opacity:1;transform:none}.ck p{margin:0}.ck a{color:#6e727a;text-decoration:underline;text-underline-offset:2px}.ck a:hover{color:#0f0f11}' +
    '.ck-row{display:flex;gap:8px;margin-top:14px}.ck-btn{flex:1;min-height:44px;padding:0 16px;border:0;border-radius:999px;font:500 14px Onest,system-ui,sans-serif;cursor:pointer;transition:translate .2s ease,box-shadow .2s ease}' +
    '.ck-btn:hover{translate:0 -1px;box-shadow:0 8px 16px -10px rgba(15,15,17,.5)}.ck-yes{background:#0f0f11;color:#fff}.ck-no{background:#fff;color:#0f0f11;box-shadow:inset 0 0 0 1px #d9dce1}' +
    '.ck-btn:focus-visible{outline:2px solid #3172c8;outline-offset:2px}' +
    '.cookie-settings{padding:0;border:0;background:none;color:inherit;font:inherit;cursor:pointer}.cookie-settings:hover{color:#fff}' +
    '@media (max-width:639px){.ck{left:12px;bottom:12px;width:calc(100vw - 24px);padding:16px}}' +
    '@media (prefers-reduced-motion:reduce){.ck{transition:none}}';

  var box = null;
  function hide() {
    if (!box) return;
    var b = box; box = null;
    b.classList.remove('is-in');
    setTimeout(function () { if (b.parentNode) b.parentNode.removeChild(b); }, 400);
  }
  function choose(granted) { write(granted ? 'granted' : 'denied'); signal(granted); hide(); }
  function show(focus) {
    if (box) return;
    box = l.createElement('div');
    box.className = 'ck';
    box.setAttribute('role', 'region');
    box.setAttribute('aria-label', TEXT.label);
    box.innerHTML = '<p>' + TEXT.msg + ' <a href="' + TEXT.href + '">' + TEXT.more + '</a></p>' +
      '<div class="ck-row"><button type="button" class="ck-btn ck-no">' + TEXT.no + '</button><button type="button" class="ck-btn ck-yes">' + TEXT.yes + '</button></div>';
    box.querySelector('.ck-yes').addEventListener('click', function () { choose(true); });
    box.querySelector('.ck-no').addEventListener('click', function () { choose(false); });
    l.body.appendChild(box);
    setTimeout(function () { if (box) box.classList.add('is-in'); }, 30); // a timer, not rAF: rAF stalls in background tabs
    if (focus) box.querySelector('.ck-yes').focus();
  }

  function ready() {
    if (internal()) return; // team browser: no analytics, so no consent banner or footer button either
    var st = l.createElement('style');
    st.textContent = css;
    l.head.appendChild(st);
    // "Cookie settings" next to the other footer links, so the choice can be changed as easily as it was made.
    var nav = l.querySelector('footer nav');
    if (nav) {
      var b = l.createElement('button');
      b.type = 'button'; b.className = 'cookie-settings'; b.textContent = TEXT.settings;
      b.addEventListener('click', function () { show(true); });
      nav.appendChild(b);
    }
    if (!read()) {
      // The language dialog (lang-prompt.js) goes first; the cookie banner appears once it is closed.
      if (window.roddiLangPending) window.addEventListener('roddi:lang-done', function () { if (!read()) show(false); });
      else show(false);
    }
  }
  if (l.readyState === 'loading') l.addEventListener('DOMContentLoaded', ready); else ready();
})(window, document, 'clarity', 'script', 'zah0cbuajb');
