/**
 * Cloudflare Pages Function: /wineries (exact path only — not /wineries/<slug>)
 *
 * Owns the /wineries → /directory redirect previously in `_redirects`.
 * Pages `_redirects` are not applied when a Function serves the route, and
 * `_redirects` cannot attach query-conditioned headers anyway.
 *
 * Soft-404 mitigation: when ?q= is present (including Google's literal
 * {search_term_string} SearchAction template), add X-Robots-Tag: noindex, follow
 * on the 301 so the template URL is not indexed.
 */

export function onRequestGet(context) {
  const url = new URL(context.request.url);
  const dest = new URL("/directory", url.origin);
  dest.search = url.search;

  const headers = {
    Location: `${dest.pathname}${dest.search}`,
  };

  if (url.searchParams.has("q")) {
    headers["X-Robots-Tag"] = "noindex, follow";
  }

  return new Response(null, { status: 301, headers });
}

export function onRequestHead(context) {
  return onRequestGet(context);
}
