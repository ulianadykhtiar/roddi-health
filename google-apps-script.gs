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
 */

var HEADERS = {
  Emails: ['Дата', 'Email', 'Форма', 'Сторінка'],
  Survey: ['Дата', 'Email', 'Тварини', 'Скільки', 'Останні ліки', 'Телефон', 'Бета', 'Коментар']
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
      emails.appendRow([new Date(), clean(email), clean(data.form), clean(data.page)]);
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
      list.appendRow([new Date(), clean(email), 'email-change', clean(data.page)]);
      return reply('ok');
    }
    if (data.type === 'survey') {
      sheet('Survey').appendRow([new Date(), clean(email), clean(data.pets), clean(data.count), clean(data.lastMeds),
                                 clean(data.phone), clean(data.beta), clean(data.note)]);
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
  }
  return s;
}

// Plain text only, capped in length; a leading = + - @ would make Sheets treat it as a formula.
function clean(v) {
  var s = String(v == null ? '' : v).slice(0, 1000);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function reply(status) {
  return ContentService.createTextOutput(JSON.stringify({ status: status })).setMimeType(ContentService.MimeType.JSON);
}
