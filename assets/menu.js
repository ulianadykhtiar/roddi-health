/* Phone side menu. Links live in the <dialog id="site-menu"> markup on each page. */
(function () {
  var menu = document.getElementById('site-menu');
  var opener = document.querySelector('[data-menu-open]');
  if (!menu || !opener) return;
  opener.addEventListener('click', function () { menu.showModal(); });
  menu.addEventListener('click', function (e) {
    // The content fills the dialog, so a click on the dialog itself is the backdrop.
    if (e.target === menu || e.target.closest('[data-menu-close]')) menu.close();
  });
})();
