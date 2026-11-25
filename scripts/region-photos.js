/** Region scenic photos for directory cards + optional winery photo override.
 *  Photos illustrate each Michigan wine region — not a specific winery.
 *  Attribution: /images/credits.json (and About → Photo Credits).
 *  Optional per-winery fields in wineries data: photo, photo_credit.
 */
(function (global) {
  const REGION_KEYS = {
    'Old Mission': 'old-mission',
    'Leelanau': 'leelanau',
    'Lake Michigan Shore': 'lake-michigan-shore',
    'Fennville': 'fennville',
    'Tip of the Mitt': 'tip-of-the-mitt',
    'Southeast Michigan': 'southeast-michigan',
    'Upper Peninsula': 'upper-peninsula',
    'Central Michigan': 'central-michigan',
    'Northeast Michigan': 'northeast-michigan',
    'West Michigan': 'west-michigan',
    'Thumb & Sunrise Coast': 'thumb-sunrise-coast'
  };

  const REGION_PHOTOS = {
    'central-michigan': ['/images/regions/central-michigan-1.webp', '/images/regions/central-michigan-2.webp', '/images/regions/central-michigan-3.webp'],
    'fennville': ['/images/regions/fennville-1.webp', '/images/regions/fennville-2.webp', '/images/regions/fennville-3.webp'],
    'lake-michigan-shore': ['/images/regions/lake-michigan-shore-1.webp', '/images/regions/lake-michigan-shore-2.webp', '/images/regions/lake-michigan-shore-3.webp', '/images/regions/lake-michigan-shore-4.webp'],
    'leelanau': ['/images/regions/leelanau-1.webp', '/images/regions/leelanau-2.webp', '/images/regions/leelanau-3.webp', '/images/regions/leelanau-4.webp'],
    'northeast-michigan': ['/images/regions/northeast-michigan-1.webp', '/images/regions/northeast-michigan-2.webp', '/images/regions/northeast-michigan-3.webp'],
    'old-mission': ['/images/regions/old-mission-1.webp', '/images/regions/old-mission-2.webp', '/images/regions/old-mission-3.webp', '/images/regions/old-mission-4.webp'],
    'southeast-michigan': ['/images/regions/southeast-michigan-1.webp', '/images/regions/southeast-michigan-2.webp', '/images/regions/southeast-michigan-3.webp'],
    'thumb-sunrise-coast': ['/images/regions/thumb-sunrise-coast-1.webp', '/images/regions/thumb-sunrise-coast-2.webp', '/images/regions/thumb-sunrise-coast-3.webp'],
    'tip-of-the-mitt': ['/images/regions/tip-of-the-mitt-1.webp', '/images/regions/tip-of-the-mitt-2.webp', '/images/regions/tip-of-the-mitt-3.webp'],
    'upper-peninsula': ['/images/regions/upper-peninsula-1.webp', '/images/regions/upper-peninsula-2.webp', '/images/regions/upper-peninsula-3.webp', '/images/regions/upper-peninsula-4.webp'],
    'west-michigan': ['/images/regions/west-michigan-1.webp', '/images/regions/west-michigan-2.webp', '/images/regions/west-michigan-3.webp'],
  };

  function hashSlug(slug) {
    var s = String(slug || '');
    var h = 0;
    for (var i = 0; i < s.length; i++) {
      h = ((h << 5) - h) + s.charCodeAt(i);
      h |= 0;
    }
    return Math.abs(h);
  }

  function regionKey(region) {
    return REGION_KEYS[region] || String(region || '')
      .toLowerCase()
      .replace(/&/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  }

  /** Deterministic scenic photo for a winery's region (varies across neighboring cards). */
  function regionPhotoFor(region, slug) {
    var key = regionKey(region);
    var set = REGION_PHOTOS[key];
    if (!set || !set.length) return null;
    return set[hashSlug(slug) % set.length];
  }

  /**
   * Prefer winery-specific photo when set; otherwise region scenic photo.
   * Returns { src, isWineryPhoto } or null.
   */
  function cardPhotoFor(winery) {
    if (!winery) return null;
    if (winery.photo) {
      return { src: winery.photo, isWineryPhoto: true, credit: winery.photo_credit || '' };
    }
    var src = regionPhotoFor(winery.region, winery.slug || winery.name || '');
    if (!src) return null;
    return { src: src, isWineryPhoto: false, credit: '' };
  }

  global.MV_REGION_PHOTOS = {
    REGION_KEYS: REGION_KEYS,
    REGION_PHOTOS: REGION_PHOTOS,
    hashSlug: hashSlug,
    regionKey: regionKey,
    regionPhotoFor: regionPhotoFor,
    cardPhotoFor: cardPhotoFor
  };
})(typeof window !== 'undefined' ? window : globalThis);
