/* Roddi Health — email sign-up + survey.
 *
 * Where data goes: set FORMS_ENDPOINT to the URL of the Google Apps Script web
 * app from google-apps-script.gs (it writes to a Google Sheet with two tabs,
 * "Emails" and "Survey"). While it is empty, submissions are kept in this
 * browser's localStorage only, so the flow can be tried locally.
 */
var FORMS_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwV8yi4dIDTwzk0D9J8BdZtBD7E0UUmvbaG2zolA2Aix3fpQPzN3P4qlX44SsiL4ua_dg/exec';

var RoddiForms = (function () {
  var EMAIL_KEY = 'roddi:email';

  /* ---------- storage ---------- */
  function send(type, data) {
    if (window.clarity) window.clarity('event', type);
    var payload = Object.assign({ type: type, page: location.pathname, sentAt: new Date().toISOString() }, data);
    if (!FORMS_ENDPOINT) {
      try {
        var all = JSON.parse(localStorage.getItem('roddi:outbox') || '[]');
        all.push(payload);
        localStorage.setItem('roddi:outbox', JSON.stringify(all));
      } catch (e) {}
      console.info('[Roddi] FORMS_ENDPOINT is not set; saved locally:', payload);
      return Promise.resolve();
    }
    // text/plain avoids a CORS preflight, which Apps Script can't answer.
    return fetch(FORMS_ENDPOINT, {
      method: 'POST', mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload)
    });
  }

  /* ---------- email checks ---------- */
  var EMAIL_RE = /^[^\s@"(),:;<>[\]\\]+@[^\s@"(),:;<>[\]\\]+\.[a-zЀ-ӿ]{2,}$/i;
  var DOMAINS = ['gmail.com', 'ukr.net', 'i.ua', 'icloud.com', 'outlook.com', 'hotmail.com',
                 'yahoo.com', 'meta.ua', 'proton.me', 'protonmail.com', 'live.com', 'me.com', 'bigmir.net'];

  function distance(a, b) {
    var d = [], i, j;
    for (i = 0; i <= a.length; i++) d[i] = [i];
    for (j = 0; j <= b.length; j++) d[0][j] = j;
    for (i = 1; i <= a.length; i++)
      for (j = 1; j <= b.length; j++)
        d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    return d[a.length][b.length];
  }

  // Returns an error text, or null if the address looks valid.
  function problem(email) {
    if (!email) return 'Введіть email, щоб ми могли вам написати.';
    if (/[Ѐ-ӿ]/.test(email.split('@')[0])) return 'Схоже, частина адреси набрана кирилицею. Перевірте розкладку.';
    if (!EMAIL_RE.test(email) || /\.\./.test(email) || /^\.|\.@|@\./.test(email))
      return 'Перевірте адресу: вона має виглядати як name@gmail.com.';
    return null;
  }

  // "name@gmial.com" → "name@gmail.com"; null when nothing looks mistyped.
  function suggestion(email) {
    var at = email.lastIndexOf('@');
    if (at < 1) return null;
    var domain = email.slice(at + 1).toLowerCase();
    if (DOMAINS.indexOf(domain) !== -1) return null;
    var best = null, bestD = 3;
    DOMAINS.forEach(function (d) {
      var dist = distance(domain, d);
      if (dist < bestD && dist <= (d.length > 6 ? 2 : 1)) { best = d; bestD = dist; }
    });
    return best ? email.slice(0, at + 1) + best : null;
  }

  /* ---------- sign-up forms ---------- */
  function initSignup(form) {
    var input = form.querySelector('input[type="email"]');
    var consent = form.querySelector('input[type="checkbox"]');
    var msg = form.querySelector('.form-msg');
    var button = form.querySelector('button');
    var confirmed = null; // a mistyped-looking address the user chose to keep

    function show(html, kind) {
      kind = kind || 'error';
      msg.innerHTML = html;
      msg.dataset.kind = kind;
      msg.hidden = !html;
      input.setAttribute('aria-invalid', html && kind === 'error' ? 'true' : 'false');
    }

    input.addEventListener('input', function () { if (!msg.hidden) show(''); });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.website && form.website.value) return; // spam bot filled the honeypot
      var email = input.value.trim();
      var err = problem(email);
      if (err) { show(err); input.focus(); return; }

      var fix = suggestion(email);
      if (fix && confirmed !== email) {
        confirmed = email;
        show('Можливо, ви мали на увазі <button type="button" class="form-fix">' + fix + '</button>? ' +
             'Якщо адреса правильна, натисніть кнопку ще раз.', 'hint');
        msg.querySelector('.form-fix').addEventListener('click', function () {
          input.value = fix; show(''); input.focus();
        });
        return;
      }
      if (consent && !consent.checked) { show('Поставте позначку, що погоджуєтесь отримувати листи.'); consent.focus(); return; }

      button.disabled = true;
      send('signup', { email: email, form: form.dataset.form || '' }).then(function () {
        try { sessionStorage.setItem(EMAIL_KEY, email); } catch (e) {}
        location.href = 'thank-you.html';
      }, function () {
        button.disabled = false;
        show('Не вдалося надіслати. Перевірте інтернет і спробуйте ще раз.');
      });
    });
  }

  function storedEmail() {
    try { return sessionStorage.getItem(EMAIL_KEY) || ''; } catch (e) { return ''; }
  }

  function setStoredEmail(email) {
    try { sessionStorage.setItem(EMAIL_KEY, email); } catch (e) {}
  }

  document.querySelectorAll('form[data-signup]').forEach(initSignup);

  return { send: send, storedEmail: storedEmail, setStoredEmail: setStoredEmail, problem: problem, suggestion: suggestion };
})();
