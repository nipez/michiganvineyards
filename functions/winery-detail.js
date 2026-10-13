/**
 * Cloudflare Pages Function: /winery-detail
 *
 * Host-level 301 from the legacy query-string template to the static winery page.
 * Cloudflare Pages `_redirects` cannot match query strings, so this Function is required
 * for a real HTTP 301. winery-detail.html also has noindex + client redirect as fallback.
 *
 * `_routes.json` limits Function invocation to this path only.
 */

const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function onRequestGet(context) {
  const url = new URL(context.request.url);
  const slug = (url.searchParams.get("w") || "").trim().toLowerCase();

  if (slug && SLUG_RE.test(slug)) {
    return Response.redirect(new URL(`/wineries/${slug}`, url.origin).toString(), 301);
  }

  return Response.redirect(new URL("/directory", url.origin).toString(), 301);
}

export function onRequestHead(context) {
  return onRequestGet(context);
}
