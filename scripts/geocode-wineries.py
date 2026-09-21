#!/usr/bin/env python3
"""
Regenerate city-level lat/lng for the winery directory.

Usage (from repo root):
  python3 scripts/geocode-wineries.py

Reads city centers from city_coords.json (add new cities there, or leave
missing to fall back to Nominatim). Applies a small deterministic jitter
so co-located pins do not stack, and nudges Old Mission / Traverse City
entries onto the peninsula.

Does not rewrite directory.html — copy lat/lng into the inline wineries
array (or re-run the apply helper in this script with --apply-directory).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CITY_COORDS = ROOT / "city_coords.json"
DATA_JSON = ROOT / "wineries_data.json"
DIRECTORY = ROOT / "directory.html"

REGION_FALLBACK = {
    "Old Mission": (44.90, -85.52),
    "Leelanau": (45.02, -85.75),
    "Lake Michigan Shore": (42.05, -86.40),
    "Fennville": (42.60, -86.10),
    "Tip of the Mitt": (45.30, -84.95),
    "Southeast Michigan": (42.35, -83.20),
    "West Michigan": (43.00, -85.90),
    "Central Michigan": (43.50, -84.70),
    "Northeast Michigan": (44.80, -83.90),
    "Thumb & Sunrise Coast": (43.70, -82.90),
    "Upper Peninsula": (46.50, -87.40),
}

UA = {
    "User-Agent": "MichiganVineyardsMap/1.0 (directory geocoding; https://michiganvineyards.com)"
}


def parse_directory_wineries(html: str) -> list[dict]:
    start = html.find("const wineries = [")
    if start < 0:
        raise SystemExit("const wineries = [ not found in directory.html")
    i = start + len("const wineries = ")
    depth = 0
    for j, c in enumerate(html[i:]):
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                raw = html[i : i + j + 1]
                break
    else:
        raise SystemExit("Could not parse wineries array")
    js = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', raw)
    return json.loads(js)


def nominatim(query: str):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1, "countrycodes": "us"}
    )
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None


def jitter(slug: str, index_in_city: int, n_in_city: int):
    h = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16)
    angle = (h % 360) * math.pi / 180
    radius_deg = 0.008 + (index_in_city % max(n_in_city, 1)) * 0.004
    if n_in_city > 8:
        radius_deg = 0.006 + (index_in_city % 12) * 0.005
    return radius_deg * math.cos(angle), radius_deg * math.sin(angle) * 0.7


def ensure_city_coords(cities: list[str], known: dict) -> dict:
    out = dict(known)
    for city in cities:
        if city in out:
            continue
        print(f"Geocoding {city}…")
        try:
            res = nominatim(f"{city}, Michigan, USA")
            if res:
                out[city] = {"lat": round(res[0], 5), "lng": round(res[1], 5)}
                print(f"  -> {out[city]}")
            else:
                print(f"  -> not found")
        except Exception as e:
            print(f"  -> error {e}")
        time.sleep(1.1)
    return out


def assign_coords(wineries: list[dict], known: dict) -> list[dict]:
    by_city = defaultdict(list)
    for w in wineries:
        by_city[w["city"]].append(w)

    out = []
    for w in wineries:
        city, region = w["city"], w["region"]
        if city in known:
            lat, lng = known[city]["lat"], known[city]["lng"]
        else:
            lat, lng = REGION_FALLBACK.get(region, (44.3, -85.5))

        if city == "Traverse City" and region == "Old Mission":
            lat += 0.14
            lng += 0.10
        elif city == "Suttons Bay" and region == "Old Mission":
            lat, lng = 44.90, -85.54

        city_list = by_city[city]
        idx = next(i for i, x in enumerate(city_list) if x["slug"] == w["slug"])
        jlat, jlng = jitter(w["slug"], idx, len(city_list))
        lat += jlat
        lng += jlng

        if not (41.5 <= lat <= 48.3 and -90.5 <= lng <= -82.0):
            lat, lng = REGION_FALLBACK.get(region, (44.3, -85.5))

        row = dict(w)
        row["lat"] = round(lat, 5)
        row["lng"] = round(lng, 5)
        out.append(row)
    return out


def to_js_array(wineries: list[dict]) -> str:
    def js_val(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in v) + "]"
        return json.dumps(v, ensure_ascii=False)

    keys = ["name", "slug", "region", "type", "featured", "known", "hours", "city", "badge", "img", "lat", "lng"]
    lines = []
    for w in wineries:
        parts = [f"{k}:{js_val(w[k])}" for k in keys]
        lines.append("  {" + ",".join(parts) + "}")
    return "const wineries = [\n" + ",\n".join(lines) + "\n];"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-directory", action="store_true", help="Rewrite directory.html wineries array")
    ap.add_argument("--fetch-missing", action="store_true", help="Call Nominatim for cities not in city_coords.json")
    args = ap.parse_args()

    html = DIRECTORY.read_text()
    wineries = parse_directory_wineries(html)
    cities = sorted({w["city"] for w in wineries})

    known = {}
    if CITY_COORDS.exists():
        known = json.loads(CITY_COORDS.read_text())

    if args.fetch_missing:
        known = ensure_city_coords(cities, known)
        CITY_COORDS.write_text(json.dumps(dict(sorted(known.items())), indent=2) + "\n")
        print(f"Wrote {CITY_COORDS}")

    missing = [c for c in cities if c not in known]
    if missing:
        print("Missing city coords (run with --fetch-missing):", missing, file=sys.stderr)
        sys.exit(1)

    assigned = assign_coords(wineries, known)

    # Sync into wineries_data.json by name
    if DATA_JSON.exists():
        data = json.loads(DATA_JSON.read_text())
        by_name = {w["name"]: w for w in assigned}
        for row in data:
            if row["name"] in by_name:
                src = by_name[row["name"]]
                row["lat"] = src["lat"]
                row["lng"] = src["lng"]
                row.setdefault("slug", src["slug"])
        DATA_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Updated {DATA_JSON}")

    if args.apply_directory:
        snippet = to_js_array(assigned)
        start = html.find("const wineries = [")
        end = html.find("];", start) + 2
        DIRECTORY.write_text(html[:start] + snippet + html[end:])
        print(f"Updated {DIRECTORY}")
    else:
        print(f"Assigned coords to {len(assigned)} wineries. Re-run with --apply-directory to write directory.html.")


if __name__ == "__main__":
    main()
