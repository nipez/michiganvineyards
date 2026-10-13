#!/usr/bin/env python3
"""Rewrite internal links + canonicals to clean absolute-path URLs (no .html, no trailing slash)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://michiganvineyards.com"
TODAY = date.today().isoformat()

# Pages that exist as *.html (relative to site root, without .html)
EXISTING = set()
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts:
        continue
    rel = p.relative_to(ROOT).as_posix()
    if rel == "404.html":
        continue
    if rel == "index.html":
        EXISTING.add("/")
    else:
        EXISTING.add("/" + rel[:-5])  # strip .html

WINERY_SLUGS = {
    p.stem for p in (ROOT / "wineries").glob("*.html")
}

# Broken wine-trails "region" links that incorrectly used winery-detail?w=
REGION_LINK_FIXES = {
    "old-mission": "/directory?region=old-mission",
    "leelanau": "/directory?region=leelanau",
    "petoskey": "/directory?region=tip-of-the-mitt",
    "river-raisin": "/directory?region=southeast",
    "upper-peninsula": "/directory?region=upper-peninsula",
}

HREF_RE = re.compile(
    r"""(?P<prefix>(?:href|action)=["'])(?P<url>[^"']+)(?P<suffix>["'])""",
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r"""(<link\s+[^>]*rel=["']canonical["'][^>]*href=["'])([^"']+)(["'][^>]*>)""",
    re.IGNORECASE,
)
CANONICAL_RE2 = re.compile(
    r"""(<link\s+[^>]*href=["'])([^"']+)(["'][^>]*rel=["']canonical["'][^>]*>)""",
    re.IGNORECASE,
)
OG_URL_RE = re.compile(
    r"""(<meta\s+[^>]*property=["']og:url["'][^>]*content=["'])([^"']+)(["'][^>]*>)""",
    re.IGNORECASE,
)
OG_URL_RE2 = re.compile(
    r"""(<meta\s+[^>]*content=["'])([^"']+)(["'][^>]*property=["']og:url["'][^>]*>)""",
    re.IGNORECASE,
)
JSON_URL_RE = re.compile(
    r"""("url"\s*:\s*")(https://michiganvineyards\.com[^"]*)(")""",
)


def page_canonical_path(html_path: Path) -> str:
    rel = html_path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel == "directory.html":
        return "/directory"
    if rel == "winery-detail.html":
        # Template is a duplicate; default canonical points at directory.
        # JS / Function will redirect when ?w= is present.
        return "/directory"
    return "/" + rel[:-5]


def absolutize_clean(path: str) -> str:
    if path == "/":
        return ORIGIN + "/"
    return ORIGIN + path.rstrip("/")


def rewrite_internal_url(url: str, file_path: Path) -> str:
    """Return cleaned URL for an internal href/action value."""
    if not url or url.startswith(
        ("mailto:", "tel:", "javascript:", "data:", "#", "{{")
    ):
        return url
    if url.startswith("//"):
        return url

    # Absolute external
    if re.match(r"^https?://", url, re.I):
        if not url.lower().startswith(ORIGIN):
            return url
        # Same-origin absolute → normalize path form
        parts = urlsplit(url)
        path = parts.path or "/"
        # Convert .html paths
        if path.endswith(".html"):
            path = path[:-5] or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        # /wineries alone → /directory
        if path in ("/wineries",):
            path = "/directory"
        return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))

    # Relative / root-relative
    raw = url
    fragment = ""
    query = ""
    if "#" in raw:
        raw, fragment = raw.split("#", 1)
        fragment = "#" + fragment
    if "?" in raw:
        raw, query = raw.split("?", 1)
        query = "?" + query

    # Resolve relative to file directory
    if raw.startswith("/"):
        path = raw
    elif raw == "" or raw == ".":
        # query/fragment only on current page — leave
        return url
    else:
        base_dir = file_path.parent.relative_to(ROOT).as_posix()
        if base_dir == ".":
            joined = raw
        else:
            # naive join then normalize ..
            joined = f"{base_dir}/{raw}"
        parts = []
        for seg in joined.split("/"):
            if seg in ("", "."):
                continue
            if seg == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(seg)
        path = "/" + "/".join(parts)

    # Special: winery-detail query handling
    leaf = path.rsplit("/", 1)[-1]
    if leaf in ("winery-detail", "winery-detail.html") or path.endswith(
        "/winery-detail.html"
    ) or path == "/winery-detail.html" or path == "/winery-detail":
        qs = query[1:] if query.startswith("?") else ""
        params = dict(parse_qsl(qs, keep_blank_values=True))
        w = params.get("w", "")
        # Broken pattern: ?w=?region=old-mission (literal)
        if w.startswith("?region=") or w.startswith("region="):
            region = w.split("=", 1)[-1]
            return REGION_LINK_FIXES.get(region, "/directory") + fragment
        # Also handle query like ?w=&region= or malformed from wine-trails
        if not w and "region" in params:
            region = params["region"]
            return REGION_LINK_FIXES.get(region, f"/directory?region={region}") + fragment
        if w and re.fullmatch(r"[a-z0-9-]+", w):
            if w in WINERY_SLUGS:
                return f"/wineries/{w}" + fragment
            return "/directory" + fragment
        # No slug → directory
        return "/directory" + fragment

    # Strip .html
    if path.endswith(".html"):
        path = path[:-5] or "/"

    # Prefer /directory over phantom /wineries index
    if path in ("/wineries", "/wineries/"):
        path = "/directory"

    # Drop trailing slash (except root)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Keep query (also used for the-vine?a= and directory filters)
    return path + query + fragment


def rewrite_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    original = text
    link_changes = 0

    def href_sub(m: re.Match) -> str:
        nonlocal link_changes
        old = m.group("url")
        new = rewrite_internal_url(old, path)
        if new != old:
            link_changes += 1
        return f'{m.group("prefix")}{new}{m.group("suffix")}'

    text = HREF_RE.sub(href_sub, text)

    canon = absolutize_clean(page_canonical_path(path))

    def canon_sub(m: re.Match) -> str:
        return f"{m.group(1)}{canon}{m.group(3)}"

    text, n1 = CANONICAL_RE.subn(canon_sub, text)
    text, n2 = CANONICAL_RE2.subn(canon_sub, text)
    if n1 + n2 == 0 and path.name != "404.html":
        # Insert canonical after <title>…</title> or charset meta
        insert = f'<link rel="canonical" href="{canon}"/>\n'
        if re.search(r"</title>", text, re.I):
            text = re.sub(r"(</title>\s*)", r"\1" + insert, text, count=1, flags=re.I)
        else:
            text = re.sub(
                r"(<head[^>]*>)",
                r"\1\n" + insert,
                text,
                count=1,
                flags=re.I,
            )

    # Fix og:url when it points at michiganvineyards.com
    def og_sub(m: re.Match) -> str:
        old = m.group(2)
        if "michiganvineyards.com" in old:
            return f"{m.group(1)}{canon}{m.group(3)}"
        return m.group(0)

    text = OG_URL_RE.sub(og_sub, text)
    text = OG_URL_RE2.sub(og_sub, text)

    def json_url_sub(m: re.Match) -> str:
        old = m.group(2)
        # Only rewrite site URLs that look like page URLs
        if old.startswith(ORIGIN):
            return f"{m.group(1)}{canon}{m.group(3)}"
        return m.group(0)

    text = JSON_URL_RE.sub(json_url_sub, text)

    # Directory JS templates: wineries/${w.slug}.html → /wineries/${w.slug}
    if path.name == "directory.html":
        text2 = text.replace("wineries/${w.slug}.html", "/wineries/${w.slug}")
        if text2 != text:
            link_changes += text.count("wineries/${w.slug}.html")
            text = text2

    if text != original:
        path.write_text(text, encoding="utf-8")
    return link_changes, (1 if text != original else 0)


def build_sitemap() -> int:
    # Indexable pages: exclude 404, winery-detail (duplicate/noindex)
    skip = {"/winery-detail", "/404"}
    # Include sitemap.html as /sitemap? optional — it's indexable utility; include it
    paths = sorted(
        p for p in EXISTING if p not in skip
    )
    # Ensure /directory present (maps from directory.html)
    assert "/directory" in paths

    # Priority heuristics
    def priority(p: str) -> str:
        if p == "/":
            return "1.0"
        if p in ("/directory", "/regions", "/fennville"):
            return "0.9"
        if p.startswith("/wineries/"):
            return "0.7"
        if p in ("/wine-trails", "/plan-your-visit", "/events", "/the-vine"):
            return "0.8"
        if p.startswith("/the-vine/"):
            return "0.6"
        return "0.5"

    def changefreq(p: str) -> str:
        if p == "/":
            return "daily"
        if p.startswith("/wineries/"):
            return "monthly"
        return "weekly"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for p in paths:
        loc = absolutize_clean(p)
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{changefreq(p)}</changefreq>")
        lines.append(f"    <priority>{priority(p)}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
    return len(paths)


def main() -> None:
    files = [
        p
        for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and p.name != "404.html"
    ]
    total_links = 0
    changed_files = 0
    for f in files:
        links, changed = rewrite_file(f)
        total_links += links
        changed_files += changed
    n = build_sitemap()
    print(f"Updated {changed_files} HTML files; {total_links} href/action rewrites")
    print(f"Wrote sitemap.xml with {n} URLs (no trailing slash)")
    print(f"Existing page paths: {len(EXISTING)}")


if __name__ == "__main__":
    main()
