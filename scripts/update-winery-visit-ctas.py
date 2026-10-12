#!/usr/bin/env python3
"""Normalize tasting / hours CTAs on all wineries/*.html detail pages.

Idempotent. Run from repo root:
  python3 scripts/update-winery-visit-ctas.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINERIES = ROOT / "wineries"

VAGUE_HOURS = {
    "seasonal",
    "seasonal hours",
    "by appointment",
    "call for hours",
    "varies",
    "n/a",
    "—",
    "-",
    "",
}

VISIT_HOURS_CSS = """
.visit-hours{margin:0 0 18px;padding:14px 16px;background:rgba(245,240,232,0.08);border:1px solid rgba(201,169,110,0.28);border-radius:6px;text-align:left;}
.visit-hours-label{display:block;font-size:.68rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:6px;}
.visit-hours-value{display:block;font-size:.9rem;color:var(--cream);line-height:1.5;font-weight:500;}
.visit-hours-note{display:block;margin-top:6px;font-size:.78rem;color:rgba(245,240,232,0.55);line-height:1.45;}
.visit-hours.is-fallback .visit-hours-value{color:rgba(245,240,232,0.9);}
""".strip()

# Legacy action-card (pre-normalization)
LEGACY_ACTION_RE = re.compile(
    r'<div class="action-card">\s*'
    r"<h3>(.*?)</h3>\s*"
    r"<p>(.*?)</p>\s*"
    r'<a href="(https://www\.google\.com/search\?q=[^"]+)" class="action-btn gold"([^>]*)>(.*?)</a>\s*'
    r'<a href="(https://maps\.google\.com/maps\?q=[^"]+)" class="action-btn outline"([^>]*)>(.*?)</a>\s*'
    r"</div>",
    re.S,
)

# Already-normalized action-card (may still need hours refresh)
NORMALIZED_ACTION_RE = re.compile(
    r'<div class="action-card">\s*'
    r"<h3>Plan Your Visit</h3>\s*"
    r"<p>(.*?)</p>\s*"
    r'<div class="visit-hours[^"]*">.*?</div>\s*'
    r'<a href="(https://www\.google\.com/search\?q=[^"]+)" class="action-btn gold"([^>]*)>Find Tasting Info</a>\s*'
    r'<a href="(https://maps\.google\.com/maps\?q=[^"]+)" class="action-btn outline"([^>]*)>Get Directions</a>\s*'
    r"</div>",
    re.S,
)

HOURS_CARD_RE = re.compile(
    r'<div class="hours-card">\s*'
    r"<h4>Hours</h4>\s*"
    r'<div class="hours-text">(.*?)</div>\s*'
    r"</div>",
    re.S,
)

HOURS_FROM_CTA_RE = re.compile(
    r'<span class="visit-hours-value">(.*?)</span>'
    r'(?:<span class="visit-hours-note">(.*?)</span>)?',
    re.S,
)

CSS_ANCHOR_RE = re.compile(
    r"(\.action-btn\.outline:hover\{border-color:var\(--gold\);\})",
)

LEAD = "Find the winery’s official site for tasting details and reservations."


def hours_block(raw_hours: str) -> str:
    hours = (raw_hours or "").strip()
    key = hours.lower()
    # If we already stored the fallback label, keep any prior note context.
    if hours == "Confirm hours before you go" or key in VAGUE_HOURS or not hours:
        if key == "by appointment":
            note = "By appointment — contact the winery to schedule a tasting."
        elif key.startswith("seasonal"):
            note = "Seasonal — check the winery’s site for current tasting times."
        else:
            note = "Hours aren’t listed yet — confirm before you go."
        return (
            '<div class="visit-hours is-fallback">'
            '<span class="visit-hours-label">Hours</span>'
            '<span class="visit-hours-value">Confirm hours before you go</span>'
            f'<span class="visit-hours-note">{note}</span>'
            "</div>"
        )
    return (
        '<div class="visit-hours">'
        '<span class="visit-hours-label">Hours</span>'
        f'<span class="visit-hours-value">{hours}</span>'
        "</div>"
    )


def build_action_card(
    search_href: str,
    search_attrs: str,
    maps_href: str,
    maps_attrs: str,
    hours_html: str,
) -> str:
    return (
        '<div class="action-card">\n'
        "<h3>Plan Your Visit</h3>\n"
        f"<p>{LEAD}</p>\n"
        f"{hours_html}\n"
        f'<a href="{search_href}" class="action-btn gold"{search_attrs}>Find Tasting Info</a>\n'
        f'<a href="{maps_href}" class="action-btn outline"{maps_attrs}>Get Directions</a>\n'
        "</div>"
    )


def extract_hours(text: str) -> str | None:
    hours_match = HOURS_CARD_RE.search(text)
    if hours_match:
        return hours_match.group(1).strip()
    cta = HOURS_FROM_CTA_RE.search(text)
    if not cta:
        return None
    value = cta.group(1).strip()
    note = (cta.group(2) or "").strip()
    if value == "Confirm hours before you go":
        if note.lower().startswith("by appointment"):
            return "By appointment"
        if note.lower().startswith("seasonal"):
            return "Seasonal"
        return ""
    return value


def ensure_css(text: str) -> str:
    if ".visit-hours{" in text:
        return text
    if not CSS_ANCHOR_RE.search(text):
        return text
    return CSS_ANCHOR_RE.sub(r"\1\n" + VISIT_HOURS_CSS, text, count=1)


def update_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    raw_hours = extract_hours(text)
    if raw_hours is None:
        print(f"skip (no hours source): {path.name}")
        return False

    legacy = LEGACY_ACTION_RE.search(text)
    normalized = NORMALIZED_ACTION_RE.search(text)
    if legacy:
        _h3, _lead, search_href, search_attrs, _old_gold, maps_href, maps_attrs, _old_outline = (
            legacy.groups()
        )
        new_action = build_action_card(
            search_href, search_attrs, maps_href, maps_attrs, hours_block(raw_hours)
        )
        text = LEGACY_ACTION_RE.sub(new_action, text, count=1)
    elif normalized:
        lead, search_href, search_attrs, maps_href, maps_attrs = normalized.groups()
        new_action = build_action_card(
            search_href, search_attrs, maps_href, maps_attrs, hours_block(raw_hours)
        )
        text = NORMALIZED_ACTION_RE.sub(new_action, text, count=1)
    else:
        print(f"skip (no action-card pattern): {path.name}")
        return False

    text = HOURS_CARD_RE.sub("", text, count=1)
    text = ensure_css(text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(WINERIES.glob("*.html")):
        if update_file(path):
            changed += 1
    print(f"Updated {changed} winery pages.")


if __name__ == "__main__":
    main()
