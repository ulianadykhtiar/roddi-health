/* Phone side menu. Links live in the <dialog id="site-menu"> markup on each page. */
(function () {
  var menu = document.getElementById('site-menu');
  var opener = document.querySelector('[data-menu-open]');
  if (!menu || !opener) return;
  menu.tabIndex = -1;
  opener.addEventListener('click', function () {
    menu.showModal();
    menu.focus(); // otherwise the logo, the first link, opens with a focus ring
  });
  menu.addEventListener('click', function (e) {
    // The content fills the dialog, so a click on the dialog itself is the backdrop.
    if (e.target === menu || e.target.closest('[data-menu-close]')) menu.close();
  });
})();
