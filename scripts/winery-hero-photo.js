/** If a winery listing has an optional `photo` field, use it on the detail hero.
 *  Requires /scripts/wineries-data.js (window.MICHIGAN_WINERIES).
 */
(function () {
  function slugFromPath() {
    var m = (location.pathname || '').match(/\/wineries\/([^\/\.]+)/);
    if (m) return m[1];
    try {
      return new URLSearchParams(location.search).get('w') || '';
    } catch (e) {
      return '';
    }
  }

  function apply() {
    var list = window.MICHIGAN_WINERIES;
    if (!list || !list.length) return;
    var slug = slugFromPath();
    if (!slug) return;
    var w = list.find(function (x) { return x.slug === slug; });
    if (!w || !w.photo) return;
    var bg = document.querySelector('.winery-hero-bg');
    if (!bg) return;
    bg.style.backgroundImage = "url('" + String(w.photo).replace(/'/g, '%27') + "')";
    bg.style.backgroundSize = 'cover';
    bg.style.backgroundPosition = 'center';
    if (w.photo_credit) {
      bg.setAttribute('data-photo-credit', w.photo_credit);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
})();
