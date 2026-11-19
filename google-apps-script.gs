/**
 * @OnlyCurrentDoc
 *
 * Roddi Health — receives sign-ups and survey answers from the website and
 * stores them in this Google Sheet ("Emails" and "Survey" tabs).
 *
 * Setup (once, about 5 minutes):
 *  1. Create a Google Sheet, e.g. "Roddi Health — заявки".
 *  2. Extensions → Apps Script. Replace the code with this file and save.
 *  3. Deploy → New deployment → type "Web app".
 *     Execute as: Me. Who has access: Anyone. Deploy and allow access.
 *  4. Copy the Web app URL (…/exec) and paste it into FORMS_ENDPOINT at the
 *     top of assets/forms.js.
 * After changing this code, use Deploy → Manage deployments → Edit → New
 * version, so the same URL keeps working.
 *
 * Emails to the waitlist (sent from the Google account that owns this script):
 *  - A short welcome letter goes out right after someone ticks the consent box and signs up.
 *  - Every letter has an unsubscribe link (this web app, ?unsub=…). It sets "Підписка" to
 *    "unsubscribed" and that address is skipped from then on.
 *  - Newsletters: write a row on the "Розсилка" tab (subject and text in Ukrainian and English),
 *    then run sendNewsletter() from the editor. It sends to everyone active, each in their own
 *    language, and writes the result in the "Статус" column.
 *  First run needs one extra permission (sending mail): the editor will ask once.
 */

var MAIL_NAME = 'Roddi Health';
var MAIL_REPLY_TO = 'roddihealth@gmail.com';

var HEADERS = {
  Emails: ['Дата', 'Email', 'Форма', 'Сторінка', 'Мова', 'Згода', 'Джерело', 'Кампанія', 'Підписка', 'Вітальний лист'],
  'Розсилка': ['Тема (uk)', 'Текст (uk)', 'Тема (en)', 'Текст (en)', 'Статус'],
  Survey: ['Дата', 'Email', 'Тварини', 'Скільки', 'Останні ліки', 'Телефон', 'Бета', 'Коментар', 'Мова']
};

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var data = JSON.parse(e.postData.contents);
    var email = String(data.email || '').trim().toLowerCase().slice(0, 254);
    if (data.type === 'signup') {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return reply('invalid');
      var emails = sheet('Emails');
      // One row per address: a repeat sign-up is ignored.
      var known = emails.getLastRow() > 1 ? emails.getRange(2, 2, emails.getLastRow() - 1, 1).getValues() : [];
      if (known.some(function (r) { return String(r[0]).toLowerCase() === email; })) return reply('duplicate');
      var consent = clean(data.consent);
      emails.appendRow([new Date(), clean(email), clean(data.form), clean(data.page), lang(data), consent, clean(data.source), clean(data.campaign), consent ? 'active' : '', '']);
      if (consent) {
        // The sign-up is already saved; a mail problem must not make the form fail.
        try { emails.getRange(emails.getLastRow(), 10).setValue(sendWelcome(email, lang(data)) ? new Date() : 'не надіслано'); } catch (err) {}
      }
      return reply('ok');
    }
    if (data.type === 'email-change') {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return reply('invalid');
      var old = String(data.oldEmail || '').trim().toLowerCase();
      var list = sheet('Emails');
      var rows = list.getLastRow() > 1 ? list.getRange(2, 2, list.getLastRow() - 1, 1).getValues() : [];
      for (var i = 0; i < rows.length; i++) {
        if (String(rows[i][0]).toLowerCase() === old) {
          list.getRange(i + 2, 2).setValue(clean(email));
          return reply('ok');
        }
      }
      list.appendRow([new Date(), clean(email), 'email-change', clean(data.page), lang(data)]);
      return reply('ok');
    }
    if (data.type === 'survey') {
      sheet('Survey').appendRow([new Date(), clean(email), clean(data.pets), clean(data.count), clean(data.lastMeds),
                                 clean(data.phone), clean(data.beta), clean(data.note), lang(data)]);
      return reply('ok');
    }
    return reply('unknown type');
  } finally {
    lock.releaseLock();
  }
}

function sheet(name) {
  var book = SpreadsheetApp.getActiveSpreadsheet();
  var s = book.getSheetByName(name);
  if (!s) {
    s = book.insertSheet(name);
    s.appendRow(HEADERS[name]);
    s.setFrozenRows(1);
  } else {
    // A tab made before a column was added gets the missing header.
    var want = HEADERS[name], have = s.getRange(1, 1, 1, want.length).getValues()[0];
    for (var i = 0; i < want.length; i++) if (!have[i]) s.getRange(1, i + 1).setValue(want[i]);
  }
  return s;
}

// Plain text only, capped in length; a leading = + - @ would make Sheets treat it as a formula.
function clean(v) {
  var s = String(v == null ? '' : v).slice(0, 1000);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

// Emails column G "Джерело" = utm_source or the referring site (or "direct"), H "Кампанія" = utm_campaign / utm_medium (assets/forms.js).
// Emails column F "Згода": the version of the consent text the visitor ticked (assets/forms.js CONSENT_VERSION), empty if none.
// "uk" or "en": the form's page language; older pages send no lang, so fall back to the /en/ path.
function lang(data) {
  if (data.lang === 'en' || data.lang === 'uk') return data.lang;
  return /^\/en(\/|$)/.test(String(data.page || '')) ? 'en' : 'uk';
}

// One-time setup, run from the Apps Script editor: adds the "Мова" header to
// existing tabs and fills it for old rows (from the page path on Emails, from
// Cyrillic in the answers on Survey). Safe to run again.
function addLangColumn() {
  ['Emails', 'Survey'].forEach(function (name) {
    var s = sheet(name);
    var col = HEADERS[name].length;
    s.getRange(1, col).setValue('Мова');
    var n = s.getLastRow() - 1;
    if (n < 1) return;
    var rows = s.getRange(2, 1, n, col).getValues();
    var out = rows.map(function (r) {
      if (r[col - 1] === 'uk' || r[col - 1] === 'en') return [r[col - 1]];
      if (!r[1]) return [''];
      if (name === 'Emails') return [lang({ page: r[3] })];
      return [/[А-Яа-яІіЇїЄєҐґ]/.test(r.slice(2, col - 1).join(' ')) ? 'uk' : 'en'];
    });
    s.getRange(2, col, n, 1).setValues(out);
  });
}

function reply(status) {
  return ContentService.createTextOutput(JSON.stringify({ status: status })).setMimeType(ContentService.MimeType.JSON);
}


// ---------------------------------------------------------------------------
// Mail to the waitlist
// ---------------------------------------------------------------------------

// A secret kept in Script Properties; unsubscribe links are a hash of the address and this secret.
function secret() {
  var props = PropertiesService.getScriptProperties();
  var v = props.getProperty('MAIL_SECRET');
  if (!v) { v = Utilities.getUuid() + Utilities.getUuid(); props.setProperty('MAIL_SECRET', v); }
  return v;
}

function token(email) {
  var bytes = Utilities.computeHmacSha256Signature(String(email).toLowerCase(), secret());
  return Utilities.base64EncodeWebSafe(bytes).slice(0, 22);
}

function unsubUrl(email) {
  return ScriptApp.getService().getUrl() + '?unsub=' + token(email) + '&e=' + encodeURIComponent(email);
}

var TEXT = {
  uk: {
    subject: 'Ви в списку очікування Roddi Health',
    hi: 'Дякуємо, що приєдналися!',
    body: ['Ви в списку очікування Roddi Health, додатку, який допомагає не пропускати ліки, стежити за вагою й станом гризунів та приходити до ветеринара з готовою історією.',
           'Спершу ми напишемо про запуск і запросимо до раннього доступу.',
           'Іноді надсилатимемо листи про застосунок і корисні теми для власників гризунів, щоб ви не забули про нас. Без спаму, лише по суті.'],
    foot: 'Ви отримали цей лист, бо залишили email на roddihealth.app. Якщо це були не ви або передумали,',
    unsub: 'відпишіться одним кліком'
  },
  en: {
    subject: 'You’re on the Roddi Health waitlist',
    hi: 'Thanks for joining!',
    body: ['You’re on the Roddi Health waitlist, an app that helps you never miss a dose, track your rodent’s weight and condition, and arrive at the vet with the history ready.',
           'First, we’ll let you know when we launch and invite you to early access.',
           'From time to time we’ll also send emails about the app and useful topics for rodent owners, so you don’t forget about us. No spam, only what matters.'],
    foot: 'You got this email because you left your address at roddihealth.app. If that wasn’t you or you’ve changed your mind,',
    unsub: 'unsubscribe in one click'
  }
};

function esc(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

// One layout for every letter: blue header, white card, unsubscribe line.
function wrap(lang, title, paragraphsHtml, email) {
  var t = TEXT[lang === 'en' ? 'en' : 'uk'];
  return '<div style="background:#eef2fb;padding:24px 12px;font-family:Arial,Helvetica,sans-serif">' +
    '<div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:20px;overflow:hidden">' +
    '<div style="background:#3172c8;padding:22px 28px;color:#ffffff;font-size:18px;font-weight:bold">Roddi Health</div>' +
    '<div style="padding:28px;color:#16244d;font-size:16px;line-height:1.55">' +
    '<h1 style="margin:0 0 14px;font-size:24px;line-height:1.2">' + esc(title) + '</h1>' + paragraphsHtml + '</div>' +
    '<div style="padding:16px 28px 24px;color:#6b7494;font-size:12.5px;line-height:1.5">' + esc(t.foot) + ' <a href="' + unsubUrl(email) + '" style="color:#3172c8">' + esc(t.unsub) + '</a>.</div>' +
    '</div></div>';
}

function send(email, subject, html, plain) {
  // Відправник — roddihealth@gmail.com: адреса додана в Gmail як «Send mail as» (alias) на акаунті, де розгорнуто скрипт.
  GmailApp.sendEmail(email, subject, plain, { htmlBody: html, name: MAIL_NAME, from: MAIL_REPLY_TO, replyTo: MAIL_REPLY_TO });
}

function sendWelcome(email, lang) {
  var t = TEXT[lang === 'en' ? 'en' : 'uk'];
  var html = wrap(lang, t.hi, t.body.map(function (p) { return '<p style="margin:0 0 14px">' + esc(p) + '</p>'; }).join(''), email);
  send(email, t.subject, html, t.hi + '\n\n' + t.body.join('\n\n') + '\n\n' + t.unsub + ': ' + unsubUrl(email));
  return true;
}

// Run from the editor: sends the newest unsent row of the "Розсилка" tab to every active subscriber.
function sendNewsletter() {
  var tab = sheet('Розсилка');
  var last = tab.getLastRow();
  if (last < 2) throw new Error('Додайте рядок на вкладці «Розсилка»: теми й тексти (uk, en).');
  var row = tab.getRange(last, 1, 1, 5).getValues()[0];
  if (row[4]) throw new Error('Останній рядок уже надіслано: ' + row[4]);
  var list = sheet('Emails'), n = list.getLastRow() - 1;
  if (n < 1) throw new Error('У вкладці Emails нікого немає.');
  var rows = list.getRange(2, 1, n, 9).getValues();
  var people = rows.filter(function (r) { return r[1] && r[5] && r[8] === 'active'; });
  if (MailApp.getRemainingDailyQuota() < people.length) throw new Error('Денний ліміт пошти: залишилось ' + MailApp.getRemainingDailyQuota() + ', потрібно ' + people.length + '. Запустіть завтра.');
  var sent = 0;
  people.forEach(function (r) {
    var l = r[4] === 'en' ? 'en' : 'uk';
    var subject = l === 'en' ? row[2] : row[0], text = l === 'en' ? row[3] : row[1];
    if (!subject || !text) return;
    var paras = String(text).split(/\n\s*\n/).map(function (p) { return '<p style="margin:0 0 14px">' + esc(p).replace(/\n/g, '<br>') + '</p>'; }).join('');
    send(r[1], subject, wrap(l, subject, paras, r[1]), text + '\n\n' + TEXT[l].unsub + ': ' + unsubUrl(r[1]));
    sent++;
  });
  tab.getRange(last, 5).setValue('надіслано ' + Utilities.formatDate(new Date(), 'Europe/Kyiv', 'dd.MM.yyyy HH:mm') + ' · ' + sent + ' листів');
}

// The unsubscribe link in every letter opens this web app with ?unsub=<token>&e=<email>.
function doGet(e) {
  var p = (e && e.parameter) || {};
  var email = String(p.e || '').trim().toLowerCase();
  var ok = false;
  if (p.unsub && email && p.unsub === token(email)) {
    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      var list = sheet('Emails'), n = list.getLastRow() - 1;
      var emails = n > 0 ? list.getRange(2, 2, n, 1).getValues() : [];
      for (var i = 0; i < emails.length; i++) {
        if (String(emails[i][0]).toLowerCase() === email) { list.getRange(i + 2, 9).setValue('unsubscribed'); ok = true; }
      }
    } finally { lock.releaseLock(); }
  }
  var msg = ok ? 'Готово, ви відписалися від листів Roddi Health. / Done, you’re unsubscribed from Roddi Health emails.'
               : 'Посилання недійсне. Напишіть нам на ' + MAIL_REPLY_TO + ', і ми видалимо вашу адресу. / This link isn’t valid. Email ' + MAIL_REPLY_TO + ' and we’ll remove your address.';
  return HtmlService.createHtmlOutput('<div style="font-family:Arial,sans-serif;max-width:480px;margin:15vh auto;padding:0 20px;color:#16244d;text-align:center"><h2>Roddi Health</h2><p>' + msg + '</p></div>')
    .setTitle('Roddi Health').addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// One-time, from the editor: marks everyone who already gave consent as "active", so they get the newsletters
// (older rows have an empty "Підписка"). Does not send anything.
function markExistingActive() {
  var list = sheet('Emails'), n = list.getLastRow() - 1;
  if (n < 1) return;
  var rows = list.getRange(2, 1, n, 9).getValues();
  var out = rows.map(function (r) { return [r[1] && r[5] && !r[8] ? 'active' : r[8]]; });
  list.getRange(2, 9, n, 1).setValues(out);
}
