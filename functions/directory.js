/**
 * Cloudflare Pages Function: /directory
 *
 * Soft-404 mitigation for Google Search Console URLs like
 * /directory?q={search_term_string} (literal SearchAction template crawl).
 *
 * When ?q= is present, serve the static directory page with
 * X-Robots-Tag: noindex, follow. The HTML canonical already points at the
 * clean /directory URL. Without ?q=, pass through unchanged.
 *
 * `_headers` cannot match on query strings; a Pages Function is required.
 * `_routes.json` limits Function invocation to this path (and related SEO routes).
 */

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const response = await context.next();

  if (!url.searchParams.has("q")) {
    return response;
  }

  const headers = new Headers(response.headers);
  headers.set("X-Robots-Tag", "noindex, follow");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export function onRequestHead(context) {
  return onRequestGet(context);
}
