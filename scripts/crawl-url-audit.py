#!/usr/bin/env python3
"""
Crawl the local static site: walk sitemap.xml + internal links.

Checks:
  - every sitemap URL returns HTTP 200
  - self-referencing <link rel="canonical"> matches the sitemap entry
  - no internal links to .html, winery-detail?w=, or trailing-slash variants

Usage:
  python3 scripts/crawl-url-audit.py --base http://127.0.0.1:3000
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://michiganvineyards.com"
HREF_RE = re.compile(r"""(?:href|action)=["']([^"']+)["']""", re.I)
CANON_RE = re.compile(
    r"""<link[^>]+rel=["']canonical["'][^>]*href=["']([^"']+)["']"""
    r"""|<link[^>]+href=["']([^"']+)["'][^>]*rel=["']canonical["']""",
    re.I,
)


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in ("a", "link", "area", "form"):
            return
        attr = dict(attrs)
        for key in ("href", "action"):
            if key in attr and attr[key]:
                self.hrefs.append(attr[key])


def fetch(url: str, method: str = "GET") -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            body = resp.read().decode("utf-8", errors="replace") if method == "GET" else ""
            return resp.status, body, headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if method == "GET" else ""
        headers = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
        return e.code, body, headers


def normalize_site_path(path: str) -> str:
    if not path or path == "/":
        return "/"
    if path.endswith(".html"):
        path = path[:-5] or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path


def is_internal(href: str, base_netloc: str) -> bool:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return False
    parts = urlsplit(href)
    if parts.scheme in ("http", "https"):
        return parts.netloc == base_netloc or parts.netloc == "michiganvineyards.com"
    return True


def bad_internal_href(href: str, page_url: str) -> str | None:
    """Return reason if href is a non-preferred internal form."""
    if not is_internal(href, urlsplit(page_url).netloc):
        return None
    parts = urlsplit(urljoin(page_url, href))
    path = parts.path or "/"
    # image/asset paths ok
    if re.search(r"\.(svg|png|jpg|jpeg|gif|webp|css|js|json|xml|ico|map)$", path, re.I):
        return None
    if path.endswith(".html"):
        return ".html link"
    if "winery-detail" in path and ("w=" in parts.query or parts.query.startswith("w=")):
        return "winery-detail?w= link"
    if "winery-detail" in path and "w=" in href:
        return "winery-detail?w= link"
    if path != "/" and path.endswith("/"):
        return "trailing-slash link"
    return None


def load_sitemap_paths() -> list[str]:
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    paths = []
    for loc in locs:
        p = urlsplit(loc).path or "/"
        paths.append(normalize_site_path(p))
    return paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:3000")
    ap.add_argument("--max-pages", type=int, default=500)
    args = ap.parse_args()
    base = args.base.rstrip("/")
    base_parts = urlsplit(base)

    sitemap_paths = load_sitemap_paths()
    print(f"Sitemap URLs: {len(sitemap_paths)}")

    sitemap_ok = 0
    sitemap_fail: list[str] = []
    canon_mismatch: list[str] = []

    for path in sitemap_paths:
        url = base + ("" if path == "/" else path)
        status, body, _ = fetch(url)
        if status != 200:
            sitemap_fail.append(f"{path} → HTTP {status}")
            continue
        m = CANON_RE.search(body)
        if not m:
            canon_mismatch.append(f"{path} → missing canonical")
            continue
        canon = m.group(1) or m.group(2)
        expected = ORIGIN + ("" if path == "/" else path)
        # homepage canonical is ORIGIN + "/"
        if path == "/":
            expected = ORIGIN + "/"
        if canon.rstrip("/") != expected.rstrip("/") and canon != expected:
            # allow exact match only
            if canon != expected:
                canon_mismatch.append(f"{path} → canonical {canon!r} expected {expected!r}")
                continue
        sitemap_ok += 1

    # Crawl internal links from homepage + sitemap seeds
    seen: set[str] = set()
    queue: deque[str] = deque()
    for path in ["/"] + sitemap_paths:
        queue.append(base + ("" if path == "/" else path))

    bad_links: list[str] = []
    pages_crawled = 0
    while queue and pages_crawled < args.max_pages:
        url = queue.popleft()
        path = normalize_site_path(urlsplit(url).path or "/")
        key = path
        if key in seen:
            continue
        seen.add(key)
        status, body, _ = fetch(url)
        pages_crawled += 1
        if status != 200:
            continue
        for href in HREF_RE.findall(body):
            reason = bad_internal_href(href, url)
            if reason:
                bad_links.append(f"{path}: {href} ({reason})")
            if not is_internal(href, base_parts.netloc or "127.0.0.1"):
                continue
            abs_url = urljoin(url, href)
            parts = urlsplit(abs_url)
            # stay on local base host
            if parts.netloc and parts.netloc != base_parts.netloc:
                # michiganvineyards.com absolute links → map to local
                if parts.netloc == "michiganvineyards.com":
                    abs_url = urlunsplit(
                        (base_parts.scheme, base_parts.netloc, parts.path, parts.query, "")
                    )
                else:
                    continue
            next_path = normalize_site_path(urlsplit(abs_url).path or "/")
            if next_path not in seen and not re.search(
                r"\.(svg|png|jpg|jpeg|gif|webp|css|js|json|xml|ico)$", next_path, re.I
            ):
                # only enqueue HTML-like paths
                queue.append(
                    base + ("" if next_path == "/" else next_path)
                )

    # 404 page file exists
    has_404 = (ROOT / "404.html").exists()

    print()
    print("=== RESULTS ===")
    print(f"sitemap_200_with_matching_canonical: {sitemap_ok}/{len(sitemap_paths)}")
    print(f"sitemap_failures: {len(sitemap_fail)}")
    for x in sitemap_fail[:20]:
        print("  -", x)
    print(f"canonical_mismatches: {len(canon_mismatch)}")
    for x in canon_mismatch[:20]:
        print("  -", x)
    print(f"pages_crawled: {pages_crawled}")
    print(f"bad_internal_links: {len(bad_links)}")
    for x in bad_links[:30]:
        print("  -", x)
    print(f"404.html_present: {has_404}")

    ok = (
        sitemap_ok == len(sitemap_paths)
        and not sitemap_fail
        and not canon_mismatch
        and not bad_links
        and has_404
    )
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
