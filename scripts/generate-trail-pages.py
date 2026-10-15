#!/usr/bin/env python3
"""Generate individual Michigan wine-trail landing pages from wineries_data.json."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "wineries_data.json").read_text())
BY_SLUG = {w["slug"]: w for w in DATA}
OUT = ROOT / "wine-trails"

# Trail accent colors (match wine-trails.html)
TRAILS = [
    {
        "slug": "river-raisin",
        "name": "River Raisin Wine Trail",
        "h1": "River Raisin Wine Trail",
        "h1_em": "Southeast Michigan",
        "title": "River Raisin Wine Trail — Southeast Michigan Wineries | MichiganVineyards.com",
        "meta": "Plan a River Raisin Wine Trail day trip through Lenawee and the Irish Hills. Four member wineries near Detroit, Ann Arbor, and Toledo — with links to each tasting room.",
        "og_title": "River Raisin Wine Trail — Southeast Michigan | MichiganVineyards.com",
        "tag": "Southeast Michigan · Est. 2023",
        "hero_desc": "Michigan’s newest wine trail links four tasting rooms across Brooklyn, Onsted, Adrian, and Tecumseh — an easy afternoon from Detroit, Ann Arbor, or Toledo.",
        "accent": "#7A5A3A",
        "hero_img": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Southeast Michigan",
        "directory_href": "/directory?region=southeast",
        "plan_href": "/plan-your-visit?trail=river-raisin",
        "intro_title": "Irish Hills tasting, close to the cities",
        "intro_subtitle": "Named for the River Raisin — French for “river of grapes” — this self-guided trail stays compact so you can visit every stop in one day.",
        "intro_paras": [
            "The River Raisin Wine Trail launched in 2023 and unites four southeastern Michigan wineries in Lenawee County and the rolling Irish Hills. It is Michigan’s newest organized wine trail and a quieter alternative to the Grand Traverse and southwest shore routes.",
            "Base in Tecumseh, Brooklyn, or Adrian. Confirm hours before you go — several rooms lean weekend-focused — and keep a designated driver for the US-12 / country-road loop.",
        ],
        "best_for": "Day trips from Detroit, Ann Arbor, or Toledo",
        "base_city": "Tecumseh / Brooklyn / Adrian",
        "known_for": "Small-batch Michigan wines, fruit wines, personal tasting rooms",
        "members": [
            "cherry-creek-cellars",
            "chateau-aeronautique-winery",
            "flying-otter-winery",
            "pentamere-winery",
        ],
        "member_note": "Official River Raisin Wine Trail members with pages on this site (Visit Lenawee / member winery listings).",
        "extra_links": [
            ("All Southeast Michigan wineries", "/directory?region=southeast"),
            ("Plan your visit", "/plan-your-visit"),
        ],
    },
    {
        "slug": "lake-michigan-shore",
        "name": "Lake Michigan Shore Wine Trail",
        "h1": "Lake Michigan Shore Wine Trail",
        "h1_em": "Southwest Michigan",
        "title": "Southwest Michigan Wine Trail — Lake Michigan Shore | MichiganVineyards.com",
        "meta": "Explore the Lake Michigan Shore Wine Trail in southwest Michigan. Official trail members from St. Joseph to Paw Paw and Fennville — with directory and trip-planning links.",
        "og_title": "Southwest Michigan / Lake Michigan Shore Wine Trail | MichiganVineyards.com",
        "tag": "Southwest Michigan · Lake Michigan Shore AVA",
        "hero_desc": "Southwest Michigan’s organized wine trail through the Lake Michigan Shore AVA — locally grown grapes, longer-season reds, and tasting rooms from St. Joseph to Fennville.",
        "accent": "#3A5A7A",
        "hero_img": "https://images.unsplash.com/photo-1516594915697-87eb3b1c14ea?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Lake Michigan Shore",
        "directory_href": "/directory?region=Lake%20Michigan%20Shore",
        "plan_href": "/plan-your-visit",
        "intro_title": "Southwest Michigan’s red-wine country",
        "intro_subtitle": "The Lake Michigan Shore Wine Trail is the organized route often searched as the Southwest Michigan wine trail — member wineries dedicated to locally grown fruit in the LMS AVA.",
        "intro_paras": [
            "Sitting near the 42nd parallel along Michigan’s southwest shore, this trail runs through the Lake Michigan Shore American Viticultural Area, where Lake Michigan’s lake effect lengthens the growing season. It is the state’s densest vineyard country and a natural weekend from Chicago or Grand Rapids.",
            "Official trail members below are listed on the Lake Michigan Shore Wine Trail (miwinetrail.com) and already have winery pages here. Fenn Valley sits in the nested Fennville AVA — pair this page with our Fennville region guide when you want Saugatuck–Holland lodging.",
        ],
        "best_for": "Red wine weekends, Chicago day trips, food-and-wine loops",
        "base_city": "St. Joseph / Baroda / Paw Paw",
        "known_for": "Cabernet Franc, Merlot, Riesling, estate reds, locally grown fruit",
        "members": [
            "12-corners-vineyards",
            "baroda-founders-wine-cellar",
            "cody-kresta-vineyard-and-winery",
            "contessa-wine-cellars",
            "domaine-berrien-cellars",
            "filkins-vineyards",
            "fenn-valley-vineyards",
            "golden-muse-winery",
            "hickory-creek-winery",
            "lake-michigan-vintners",
            "lawton-ridge-winery",
            "lemon-creek-winery",
            "solasta-winery",
            "white-pine-winery",
        ],
        "member_note": "Current Lake Michigan Shore Wine Trail members with pages on this site (miwinetrail.com member directory).",
        "extra_links": [
            ("Fennville region guide", "/fennville"),
            ("All Lake Michigan Shore wineries", "/directory?region=Lake%20Michigan%20Shore"),
            ("Plan your visit", "/plan-your-visit"),
        ],
    },
    {
        "slug": "old-mission",
        "name": "Old Mission Peninsula Wine Trail",
        "h1": "Old Mission Peninsula Wine Trail",
        "h1_em": "Traverse City",
        "title": "Old Mission Peninsula Wine Trail — Traverse City Wineries | MichiganVineyards.com",
        "meta": "Drive the Old Mission Peninsula Wine Trail outside Traverse City. Ten trail wineries along M-37 with bay views, Riesling, and links to each tasting-room page.",
        "og_title": "Old Mission Peninsula Wine Trail | MichiganVineyards.com",
        "tag": "Grand Traverse Bay · M-37",
        "hero_desc": "A compact peninsula trail north of Traverse City — bay views on both sides, cool-climate wines, and enough stops for a full afternoon without leaving M-37.",
        "accent": "#8B5E3C",
        "hero_img": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Old Mission",
        "directory_href": "/directory?region=old-mission",
        "plan_href": "/plan-your-visit?trail=old-mission",
        "intro_title": "Where Michigan’s modern wine story started",
        "intro_subtitle": "Old Mission Peninsula splits Grand Traverse Bay. Chateau Grand Traverse planted early Riesling vines here in 1974; today the official wine trail lists ten tasting rooms along the peninsula.",
        "intro_paras": [
            "The trail is short enough that many visitors taste four or five rooms in one day, then return for the rest. Base downtown Traverse City or overnight on the peninsula — Mission Point Lighthouse marks the north tip.",
            "Member list below follows the Old Mission Peninsula Wine Trail (ompwinetrail.com). Hours come from our directory data; always confirm before you drive.",
        ],
        "best_for": "First-time Traverse City visitors, couples weekends, Riesling lovers",
        "base_city": "Traverse City",
        "known_for": "Riesling, Pinot Noir, Chardonnay, Cabernet Franc, bay-view tasting rooms",
        "members": [
            "2-lads-winery",
            "black-star-farms-old-mission",
            "bowers-harbor-vineyards",
            "brys-estate-vineyard-and-winery",
            "chateau-chantal",
            "chateau-grand-traverse",
            "hawthorne-vineyards",
            "mari-vineyards",
            "peninsula-cellars",
            "tabone-vineyards",
        ],
        "member_note": "Old Mission Peninsula Wine Trail members with pages on this site (ompwinetrail.com).",
        "extra_links": [
            ("All Old Mission wineries", "/directory?region=old-mission"),
            ("Old Mission vs Leelanau guide", "/the-vine/old-mission-vs-leelanau"),
            ("Plan your visit", "/plan-your-visit?trail=old-mission"),
        ],
    },
    {
        "slug": "leelanau",
        "name": "Leelanau Peninsula Wine Trail",
        "h1": "Leelanau Peninsula Wine Trail",
        "h1_em": "Sleeping Bear country",
        "title": "Leelanau Peninsula Wine Trail — Michigan Wine Country | MichiganVineyards.com",
        "meta": "Explore the Leelanau Peninsula Wine Trail near Traverse City and Sleeping Bear Dunes. Member wineries with tasting-room pages, map filters, and trip-planning links.",
        "og_title": "Leelanau Peninsula Wine Trail | MichiganVineyards.com",
        "tag": "Leelanau Peninsula · 45th Parallel",
        "hero_desc": "Michigan’s most prolific peninsula wine trail — rolling hills, lakeside bluffs, and tasting rooms from Suttons Bay to Lake Leelanau beside Sleeping Bear Dunes.",
        "accent": "#3A6B4A",
        "hero_img": "https://images.unsplash.com/photo-1474979266404-7ea332dc14a4?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Leelanau",
        "directory_href": "/directory?region=leelanau",
        "plan_href": "/plan-your-visit?trail=leelanau",
        "intro_title": "Michigan’s most celebrated wine peninsula",
        "intro_subtitle": "The Leelanau Peninsula Wine Trail gathers member tasting rooms across a peninsula moderated by Lake Michigan — the same latitude band as Bordeaux’s 45th parallel.",
        "intro_paras": [
            "Plan at least two days if you want more than a highlight reel. Base in Traverse City, Suttons Bay, or Glen Arbor, and leave room for Sleeping Bear Dunes National Lakeshore between flights.",
            "Members listed here appear on the Leelanau Peninsula Wine Trail site (lpwines.com) and have winery pages in our directory. The peninsula has additional tasting rooms beyond formal trail membership — use the Leelanau directory filter for the full map.",
        ],
        "best_for": "Multi-day wine trips, groups, dune-and-vineyard weekends",
        "base_city": "Traverse City / Suttons Bay",
        "known_for": "Riesling, Pinot Noir, sparkling, Cabernet Franc, lakeside views",
        "members": [
            "45-north-vineyard-and-winery",
            "amoritas-vineyards",
            "aurora-cellars",
            "bel-lago-vineyards-and-winery",
            "black-star-farms-leelanau",
            "blustone-vineyards",
            "boathouse-vineyards",
            "chateau-fontaine",
            "ciccone-vineyard-and-winery",
            "french-valley-vineyard",
            "gilchrist-farm-winery",
            "good-harbor-vineyards",
            "laurentide-winery",
            "leelanau-cellars",
            "rove-estate",
            "shady-lane-cellars",
            "silver-leaf-vineyard-and-winery",
            "verterra-winery",
        ],
        "member_note": "Leelanau Peninsula Wine Trail members with pages on this site (lpwines.com/wineries). Not every Leelanau tasting room is a formal trail member.",
        "extra_links": [
            ("All Leelanau wineries", "/directory?region=leelanau"),
            ("Old Mission vs Leelanau guide", "/the-vine/old-mission-vs-leelanau"),
            ("Plan your visit", "/plan-your-visit?trail=leelanau"),
        ],
    },
    {
        "slug": "petoskey",
        "name": "Petoskey Wine Region",
        "h1": "Petoskey Wine Region",
        "h1_em": "Tip of the Mitt",
        "title": "Petoskey Wine Region & Tip of the Mitt Wine Trail | MichiganVineyards.com",
        "meta": "Tour the Petoskey Wine Region in Michigan’s Tip of the Mitt AVA. Cold-hardy wines around Petoskey, Harbor Springs, and Little Traverse Bay — with member tasting-room links.",
        "og_title": "Petoskey Wine Region — Tip of the Mitt | MichiganVineyards.com",
        "tag": "Tip of the Mitt AVA · Little Traverse Bay",
        "hero_desc": "Northern Lower Peninsula wine country around Petoskey and Little Traverse Bay — cold-hardy grapes, farm tasting rooms, and an Up North vacation pairing.",
        "accent": "#5A7A5A",
        "hero_img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Tip of the Mitt",
        "directory_href": "/directory?region=tip-of-the-mitt",
        "plan_href": "/plan-your-visit?trail=petoskey",
        "intro_title": "Northern frontier wines in the Tip of the Mitt",
        "intro_subtitle": "The Petoskey Wine Region sits inside the Tip of the Mitt AVA (est. 2016). Hybrids like Marquette and La Crescent thrive where many vinifera vines struggle.",
        "intro_paras": [
            "Spread tasting stops across Petoskey, Harbor Springs, Alanson, Boyne City, and nearby lake towns. Between pours, add Little Traverse Bay, the Tunnel of Trees, or a downtown Petoskey walk.",
            "Wineries below appear on the Petoskey Wine Region site (petoskey.wine) and have pages here. Some Tip of the Mitt directory listings are nearby but not current Petoskey Wine Region members — use the region filter for the wider map.",
        ],
        "best_for": "Up North vacations, adventurous palates, unique cold-climate wines",
        "base_city": "Petoskey / Harbor Springs",
        "known_for": "Marquette, La Crescent, Frontenac Gris, maple wine, hard cider",
        "members": [
            "crooked-vine-winery",
            "seasons-of-the-north",
            "maple-moon-sugarbush-and-winery",
            "petoskey-farms-vineyard-and-winery",
            "mackinaw-trail-winery",
            "boyne-valley-vineyards",
            "walloon-lake-winery",
            "rudbeckia-winery",
            "royal-farms",
            "cellar-1914-winery",
        ],
        "member_note": "Petoskey Wine Region wineries with pages on this site (petoskey.wine). Other Tip of the Mitt AVA tasting rooms may appear in the directory without formal region membership.",
        "extra_links": [
            ("All Tip of the Mitt wineries", "/directory?region=tip-of-the-mitt"),
            ("Plan your visit", "/plan-your-visit?trail=petoskey"),
        ],
    },
    {
        "slug": "upper-peninsula",
        "name": "U.P. Wine Trail",
        "h1": "U.P. Wine Trail",
        "h1_em": "Upper Peninsula",
        "title": "Upper Peninsula Wine Trail — U.P. Michigan Wineries | MichiganVineyards.com",
        "meta": "Follow the U.P. Wine Trail across Michigan’s Upper Peninsula. Cold-climate and fruit wines from Sault Ste. Marie to Menominee — with tasting-room pages and trip links.",
        "og_title": "Upper Peninsula Wine Trail | MichiganVineyards.com",
        "tag": "Upper Peninsula · Uncork the North",
        "hero_desc": "Seven stops stretched across Michigan’s Upper Peninsula — less a single afternoon loop than an epic Great Lakes road trip between forests, shorelines, and small-town tasting rooms.",
        "accent": "#4A6A6A",
        "hero_img": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600&h=900&fit=crop&q=80",
        "directory_region": "Upper Peninsula",
        "directory_href": "/directory?region=upper-peninsula",
        "plan_href": "/plan-your-visit?trail=upper-peninsula",
        "intro_title": "One epic road trip, not a single afternoon",
        "intro_subtitle": "The U.P. Wine Trail connects tasting rooms across the Upper Peninsula. Distances are large — plan overnight stays and check seasonal hours carefully.",
        "intro_paras": [
            "Expect cold-climate grape wines, fruit wines, and brewery-winery hybrids more often than classic vinifera portfolios. Pair the trail with Lake Superior or Lake Michigan shore drives, waterfalls, and small U.P. towns.",
            "Stops below are Upper Peninsula tasting rooms in our directory that align with published U.P. Wine Trail coverage (Michigan Wine Country / Up North Wineries). We only list pages we can verify in our dataset — confirm current trail participation with each winery.",
        ],
        "best_for": "Road-trip adventurers, U.P. vacationers, unique cold-climate pours",
        "base_city": "Sault Ste. Marie / Escanaba / Menominee",
        "known_for": "Cold-hardy wines, fruit wines, cherry wine, Marquette, road-trip pacing",
        "members": [
            "1668-winery-and-soo-brewing",
            "yooper-winery",
            "northern-sun-winery",
            "leighs-garden-winery",
            "threefold-vine-winery",
            "mackinac-trail-winery-st-ignace",
            "mackinac-trail-winery-manistique",
        ],
        "member_note": "Upper Peninsula tasting rooms on this site associated with U.P. Wine Trail coverage. Membership can change — verify before traveling.",
        "extra_links": [
            ("All Upper Peninsula wineries", "/directory?region=upper-peninsula"),
            ("Plan your visit", "/plan-your-visit?trail=upper-peninsula"),
        ],
    },
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def known_str(w: dict) -> str:
    k = w.get("known") or []
    if isinstance(k, list):
        return " · ".join(k[:4])
    return str(k)


def winery_tile(w: dict, accent: str) -> str:
    badge = w.get("badge") or "Member"
    known = known_str(w)
    hours = w.get("hours") or "Check winery page"
    return f"""    <a class="winery-tile" href="/wineries/{esc(w['slug'])}">
      <div class="wt-meta"><span class="wt-badge">{esc(badge)}</span><span class="wt-city">{esc(w['city'])}</span></div>
      <h3>{esc(w['name'])}</h3>
      <div class="wt-type">{esc(w.get('type') or 'Winery')}</div>
      <div class="wt-known">{esc(known)}</div>
      <div class="wt-hours">{esc(hours)}</div>
      <span class="wt-go">Winery page <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
    </a>"""


def render(trail: dict) -> str:
    members = []
    for slug in trail["members"]:
        if slug not in BY_SLUG:
            raise SystemExit(f"Missing winery slug: {slug}")
        members.append(BY_SLUG[slug])
    count = len(members)
    tiles = "\n".join(winery_tile(w, trail["accent"]) for w in members)
    extra = "\n".join(
        f'      <a class="btn-secondary" href="{esc(href)}" style="color:var(--forest);border-color:rgba(27,58,45,0.25);">{esc(label)}</a>'
        for label, href in trail["extra_links"]
    )
    url = f"https://michiganvineyards.com/wine-trails/{trail['slug']}"
    accent = trail["accent"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JGRE0QBWPF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-JGRE0QBWPF');
</script>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
<title>{esc(trail['title'])}</title>
<meta content="{esc(trail['meta'])}" name="description"/>
<link rel="canonical" href="{esc(url)}"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
:root{{
  --forest:#1B3A2D;--forest-deep:#0F2419;--forest-light:#2A5040;
  --gold:#C9A96E;--gold-light:#D4BC8B;--gold-warm:#B8943F;
  --cream:#F5F0E8;--cream-dark:#EDE6D8;
  --sage:#8FA68F;--sage-light:#B8CCB0;
  --charcoal:#2C2420;--text:#3A3330;--text-light:#7A7068;--white:#FEFCF9;
  --trail:{accent};
}}
html{{scroll-behavior:smooth;font-size:17px;}}
body{{font-family:'Outfit',sans-serif;color:var(--text);background:var(--white);overflow-x:hidden;}}
svg{{flex-shrink:0;}}
[id]{{scroll-margin-top:96px;}}

.top-bar{{background:var(--forest-deep);color:var(--sage-light);font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;padding:9px 0;text-align:center;}}
.top-bar a{{color:var(--gold-light);text-decoration:none;}}.top-bar a:hover{{text-decoration:underline;}}

nav{{position:sticky;top:0;z-index:100;background:rgba(254,252,249,0.96);backdrop-filter:blur(12px);border-bottom:1px solid rgba(27,58,45,0.06);transition:box-shadow 0.3s;}}
nav.scrolled{{box-shadow:0 2px 30px rgba(27,58,45,0.08);}}
.nav-inner{{max-width:1340px;margin:0 auto;padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:72px;}}
.logo{{display:flex;align-items:center;gap:12px;text-decoration:none;}}
.logo-icon{{width:36px;height:36px;background:var(--forest);border-radius:50%;display:flex;align-items:center;justify-content:center;}}
.logo-icon::after{{content:'🍇';font-size:17px;}}
.logo-text{{display:flex;flex-direction:column;line-height:1;}}
.logo-main{{font-family:'Playfair Display',serif;font-size:1.35rem;font-weight:600;color:var(--forest);letter-spacing:-0.01em;}}
.logo-sub{{font-family:'Outfit',sans-serif;font-size:0.56rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold-warm);margin-top:2px;}}
.nav-links{{display:flex;gap:28px;list-style:none;align-items:center;}}
.nav-links a{{text-decoration:none;font-size:0.78rem;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;color:var(--text);position:relative;padding:4px 0;transition:color 0.3s;}}
.nav-links a::after{{content:'';position:absolute;bottom:-2px;left:0;width:0;height:1.5px;background:var(--gold);transition:width 0.3s;}}
.nav-links a:hover{{color:var(--forest);}}.nav-links a:hover::after{{width:100%;}}
.nav-links a.active{{color:var(--forest);}}.nav-links a.active::after{{width:100%;}}
.nav-cta{{background:var(--forest)!important;color:var(--cream)!important;padding:10px 22px!important;border-radius:4px;font-size:0.74rem!important;letter-spacing:0.06em!important;transition:background 0.3s!important;}}
.nav-cta:hover{{background:var(--forest-light)!important;}}.nav-cta::after{{display:none!important;}}
.nav-toggle{{display:none;background:none;border:none;cursor:pointer;padding:8px;}}

.page-hero{{position:relative;min-height:52vh;display:flex;align-items:flex-end;overflow:hidden;}}
.page-hero-bg{{position:absolute;inset:0;background:url('{esc(trail['hero_img'])}') center/cover no-repeat;background-color:{accent};transform:scale(1.02);animation:heroDrift 18s ease-in-out infinite alternate;}}
.page-hero-bg::before{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,36,25,0.35) 0%,rgba(15,36,25,0.55) 38%,rgba(15,36,25,0.92) 100%);}}
.page-hero-bg::after{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 45% at 70% 20%,color-mix(in srgb, var(--trail) 35%, transparent) 0%,transparent 55%);}}
.page-hero-content{{position:relative;z-index:2;max-width:1340px;width:100%;margin:0 auto;padding:90px 40px 56px;}}
.page-hero-brand{{font-family:'Outfit',sans-serif;font-size:0.68rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold-light);margin-bottom:14px;opacity:0;animation:fadeUp .7s .1s forwards;}}
.page-hero-tag{{display:inline-flex;align-items:center;gap:12px;font-size:0.66rem;letter-spacing:0.28em;text-transform:uppercase;color:var(--gold);margin-bottom:16px;opacity:0;animation:fadeUp .7s .2s forwards;}}
.page-hero-tag::before,.page-hero-tag::after{{content:'';width:28px;height:1px;background:var(--gold);opacity:.5;}}
.page-hero h1{{font-family:'Playfair Display',serif;font-size:clamp(2.2rem,4.8vw,3.4rem);font-weight:500;line-height:1.1;color:var(--cream);max-width:820px;opacity:0;animation:fadeUp .7s .35s forwards;}}
.page-hero h1 em{{font-style:italic;color:var(--gold-light);}}
.page-hero-desc{{font-family:'Cormorant Garamond',serif;font-size:clamp(1.05rem,1.8vw,1.25rem);line-height:1.65;color:rgba(245,240,232,0.72);margin-top:16px;max-width:580px;opacity:0;animation:fadeUp .7s .5s forwards;}}
.hero-cta{{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px;opacity:0;animation:fadeUp .7s .65s forwards;}}
.btn-primary,.btn-secondary{{display:inline-flex;align-items:center;gap:8px;padding:13px 24px;border-radius:4px;font-family:'Outfit',sans-serif;font-size:0.78rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;text-decoration:none;transition:all .25s;}}
.btn-primary{{background:var(--gold);color:var(--forest-deep);}}
.btn-primary:hover{{background:var(--gold-light);transform:translateY(-1px);}}
.btn-secondary{{background:transparent;color:var(--cream);border:1px solid rgba(245,240,232,0.35);}}
.btn-secondary:hover{{border-color:var(--gold);color:var(--gold-light);}}

.breadcrumbs{{max-width:1340px;margin:0 auto;padding:14px 40px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:0.76rem;color:var(--text-light);}}
.breadcrumbs a{{color:var(--text-light);text-decoration:none;transition:color .3s;}}.breadcrumbs a:hover{{color:var(--forest);}}
.breadcrumbs .sep{{opacity:.4;}}.breadcrumbs .current{{color:var(--forest);font-weight:500;}}

.section{{max-width:1340px;margin:0 auto;padding:64px 40px;}}
.section-tag{{font-size:.66rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--gold-warm);margin-bottom:10px;}}
.section-title{{font-family:'Playfair Display',serif;font-size:clamp(1.55rem,2.6vw,2.15rem);font-weight:500;color:var(--forest);line-height:1.2;margin-bottom:10px;}}
.section-subtitle{{font-family:'Cormorant Garamond',serif;font-size:1.12rem;color:var(--text-light);line-height:1.65;max-width:680px;}}
.section-header{{margin-bottom:36px;}}

.story-grid{{display:grid;grid-template-columns:1.2fr 0.8fr;gap:40px;align-items:start;}}
.story-copy p{{font-size:0.98rem;line-height:1.8;color:var(--text);margin-bottom:16px;}}
.story-copy p:last-child{{margin-bottom:0;}}
.story-copy a{{color:var(--forest);font-weight:600;text-decoration:none;border-bottom:1px solid rgba(27,58,45,0.2);}}
.story-copy a:hover{{border-bottom-color:var(--gold);}}
.meta-panel{{background:linear-gradient(160deg,color-mix(in srgb, var(--trail) 10%, transparent) 0%,rgba(27,58,45,0.04) 100%);border:1px solid rgba(27,58,45,0.08);padding:28px;}}
.meta-panel .nest-label{{font-size:0.66rem;letter-spacing:0.16em;text-transform:uppercase;color:var(--trail);font-weight:600;margin-bottom:14px;}}
.meta-list{{list-style:none;display:flex;flex-direction:column;gap:14px;}}
.meta-list li{{display:flex;flex-direction:column;gap:2px;}}
.meta-list .ml{{font-size:0.62rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-light);}}
.meta-list .mv{{font-size:0.9rem;color:var(--text);line-height:1.45;}}

.winery-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}}
.winery-tile{{display:flex;flex-direction:column;gap:8px;padding:22px 22px 20px;text-decoration:none;color:inherit;border-bottom:1px solid rgba(27,58,45,0.1);transition:background .25s,transform .25s,border-color .25s;}}
.winery-tile:hover{{background:rgba(27,58,45,0.03);transform:translateY(-2px);border-bottom-color:var(--gold);}}
.winery-tile .wt-meta{{display:flex;justify-content:space-between;gap:10px;align-items:center;}}
.winery-tile .wt-badge{{font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--gold-warm);font-weight:600;}}
.winery-tile .wt-city{{font-size:0.72rem;color:var(--text-light);letter-spacing:0.04em;}}
.winery-tile h3{{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:600;color:var(--forest);line-height:1.25;}}
.winery-tile .wt-type{{font-size:0.82rem;color:var(--text-light);}}
.winery-tile .wt-known{{font-size:0.84rem;color:var(--text);line-height:1.5;margin-top:4px;}}
.winery-tile .wt-hours{{font-size:0.76rem;color:var(--text-light);margin-top:auto;padding-top:10px;}}
.winery-tile .wt-go{{font-size:0.74rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:var(--forest);display:inline-flex;align-items:center;gap:6px;margin-top:10px;}}
.winery-tile:hover .wt-go{{color:var(--trail);}}
.member-note{{font-size:0.86rem;color:var(--text-light);line-height:1.6;margin-bottom:22px;max-width:720px;}}
.more-link-row{{margin-top:28px;display:flex;flex-wrap:wrap;gap:12px;}}

.cta-band{{padding:70px 40px;background:linear-gradient(135deg,color-mix(in srgb, var(--trail) 12%, transparent) 0%,rgba(27,58,45,0.08) 100%);}}
.cta-inner{{max-width:900px;margin:0 auto;text-align:center;}}
.cta-inner h2{{font-family:'Playfair Display',serif;font-size:clamp(1.7rem,3vw,2.3rem);color:var(--forest);margin-bottom:12px;}}
.cta-inner p{{font-family:'Cormorant Garamond',serif;font-size:1.15rem;color:var(--text-light);line-height:1.65;margin-bottom:28px;}}
.cta-actions{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;}}
.cta-actions .btn-primary{{background:var(--forest);color:var(--cream);}}
.cta-actions .btn-primary:hover{{background:var(--forest-light);}}
.cta-actions .btn-secondary{{color:var(--forest);border-color:rgba(27,58,45,0.25);}}
.cta-actions .btn-secondary:hover{{border-color:var(--forest);color:var(--forest);}}

.other-trails{{max-width:1340px;margin:0 auto;padding:48px 40px 64px;}}
.other-trails h2{{font-family:'Playfair Display',serif;font-size:1.4rem;color:var(--forest);margin-bottom:18px;}}
.other-grid{{display:flex;flex-wrap:wrap;gap:10px;}}
.other-grid a{{padding:10px 16px;border:1px solid rgba(27,58,45,0.1);text-decoration:none;color:var(--forest);font-size:0.82rem;font-weight:500;transition:all .2s;}}
.other-grid a:hover{{border-color:var(--trail);background:rgba(27,58,45,0.03);}}

footer{{background:var(--charcoal);padding:70px 40px 36px;color:rgba(245,240,232,0.6);}}
.footer-inner{{max-width:1340px;margin:0 auto;}}
.footer-grid{{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:50px;margin-bottom:50px;}}
.footer-brand p{{font-size:.92rem;line-height:1.7;margin-top:14px;color:rgba(245,240,232,0.4);}}
.footer-col h4{{font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:18px;}}
.footer-col ul{{list-style:none;}}.footer-col li{{margin-bottom:9px;}}
.footer-col a{{font-size:.92rem;color:rgba(245,240,232,0.4);text-decoration:none;transition:color .3s;}}.footer-col a:hover{{color:var(--gold-light);}}
.footer-bottom{{border-top:1px solid rgba(245,240,232,0.07);padding-top:28px;display:flex;justify-content:space-between;align-items:center;font-size:.76rem;}}
.footer-bottom a{{color:rgba(245,240,232,0.35);text-decoration:none;transition:color .3s;}}.footer-bottom a:hover{{color:var(--gold-light);}}

@keyframes fadeUp{{from{{opacity:0;transform:translateY(18px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes heroDrift{{from{{transform:scale(1.02) translateY(0);}}to{{transform:scale(1.06) translateY(-1.5%);}}}}
.reveal{{opacity:0;transform:translateY(22px);transition:opacity .65s ease,transform .65s ease;}}
.reveal.in{{opacity:1;transform:translateY(0);}}

@media(max-width:1024px){{
  .story-grid{{grid-template-columns:1fr;}}
  .winery-grid{{grid-template-columns:repeat(2,1fr);}}
  .footer-grid{{grid-template-columns:1fr 1fr;gap:36px;}}
}}
@media(max-width:768px){{
  .nav-links{{display:none;position:absolute;top:72px;left:0;right:0;background:var(--white);flex-direction:column;padding:20px 40px;gap:14px;border-bottom:1px solid rgba(27,58,45,0.08);box-shadow:0 8px 30px rgba(27,58,45,0.08);}}
  .nav-links.show{{display:flex;}}.nav-toggle{{display:block;}}
  .page-hero{{min-height:70vh;}}
  .page-hero-content{{padding:70px 20px 44px;}}
  .section,.other-trails{{padding-left:20px;padding-right:20px;}}
  .breadcrumbs{{padding:10px 20px;}}
  .winery-grid{{grid-template-columns:1fr;}}
  .cta-band{{padding:50px 20px;}}
  .footer-grid{{grid-template-columns:1fr;gap:28px;}}
  .footer-bottom{{flex-direction:column;gap:10px;text-align:center;}}
}}
@media(prefers-reduced-motion:reduce){{
  .page-hero-bg{{animation:none;}}
  .page-hero-brand,.page-hero-tag,.page-hero h1,.page-hero-desc,.hero-cta{{opacity:1;animation:none;}}
  .reveal{{opacity:1;transform:none;transition:none;}}
}}
</style>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="MichiganVineyards.com"/>
<meta property="og:title" content="{esc(trail['og_title'])}"/>
<meta property="og:description" content="{esc(trail['meta'])}"/>
<meta property="og:url" content="{esc(url)}"/>
<meta property="og:image" content="{esc(trail['hero_img'].replace('w=1600&h=900','w=1200&h=630'))}"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{esc(trail['og_title'])}"/>
<meta name="twitter:description" content="{esc(trail['meta'])}"/>
<meta name="twitter:image" content="{esc(trail['hero_img'].replace('w=1600&h=900','w=1200&h=630'))}"/>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": {json.dumps(trail['name'])},
  "description": {json.dumps(trail['meta'])},
  "url": {json.dumps(url)},
  "isPartOf": {{"@id": "https://michiganvineyards.com/#website"}},
  "about": {{"@type": "TouristTrip", "name": {json.dumps(trail['name'])}}},
  "breadcrumb": {{
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://michiganvineyards.com"}},
      {{"@type": "ListItem", "position": 2, "name": "Wine Trails", "item": "https://michiganvineyards.com/wine-trails"}},
      {{"@type": "ListItem", "position": 3, "name": {json.dumps(trail['name'])}}}
    ]
  }}
}}
</script>
</head>
<body>

<div class="top-bar">
  Michigan wine trails · <a href="/wine-trails">{count} stops on this route</a> · <a href="/plan-your-visit">Plan your visit</a>
</div>

<nav id="mainNav">
  <div class="nav-inner">
    <a class="logo" href="/">
      <div class="logo-icon"></div>
      <div class="logo-text">
        <span class="logo-main">Michigan Vineyards</span>
        <span class="logo-sub">Wine Country Guide</span>
      </div>
    </a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav-links').classList.toggle('show')">
      <svg width="22" height="22" fill="none" stroke="#1B3A2D" stroke-width="2"><path d="M3 6h16M3 11h16M3 16h16"/></svg>
    </button>
    <ul class="nav-links">
      <li><a href="/directory">Wineries</a></li>
      <li><a href="/regions">Regions</a></li>
      <li><a class="active" href="/wine-trails">Wine Trails</a></li>
      <li><a href="/the-vine">The Vine</a></li>
      <li><a href="/events">Events</a></li>
      <li><a class="nav-cta" href="/plan-your-visit">Plan Your Visit</a></li>
    </ul>
  </div>
</nav>

<section class="page-hero">
  <div class="page-hero-bg" aria-hidden="true"></div>
  <div class="page-hero-content">
    <div class="page-hero-brand">Michigan Vineyards</div>
    <div class="page-hero-tag">{esc(trail['tag'])}</div>
    <h1>{esc(trail['h1'])}<br/><em>{esc(trail['h1_em'])}</em></h1>
    <p class="page-hero-desc">{esc(trail['hero_desc'])}</p>
    <div class="hero-cta">
      <a class="btn-primary" href="#members">Browse {count} tasting rooms</a>
      <a class="btn-secondary" href="{esc(trail['directory_href'])}">Open directory map</a>
    </div>
  </div>
</section>

<div class="breadcrumbs">
  <a href="/">Home</a><span class="sep">›</span>
  <a href="/wine-trails">Wine Trails</a><span class="sep">›</span>
  <span class="current">{esc(trail['name'])}</span>
</div>

<section class="section" id="about">
  <div class="section-header reveal">
    <div class="section-tag">About This Trail</div>
    <h2 class="section-title">{esc(trail['intro_title'])}</h2>
    <p class="section-subtitle">{esc(trail['intro_subtitle'])}</p>
  </div>
  <div class="story-grid reveal">
    <div class="story-copy">
      {''.join(f'<p>{esc(p)}</p>' for p in trail['intro_paras'])}
      <p>Ready for logistics? Jump to <a href="{esc(trail['plan_href'])}">Plan Your Visit</a> or open the <a href="{esc(trail['directory_href'])}">directory filtered to this region</a>.</p>
    </div>
    <aside class="meta-panel">
      <div class="nest-label">Trail snapshot</div>
      <ul class="meta-list">
        <li><span class="ml">Member pages here</span><span class="mv">{count} tasting rooms</span></li>
        <li><span class="ml">Best for</span><span class="mv">{esc(trail['best_for'])}</span></li>
        <li><span class="ml">Base city</span><span class="mv">{esc(trail['base_city'])}</span></li>
        <li><span class="ml">Known for</span><span class="mv">{esc(trail['known_for'])}</span></li>
      </ul>
    </aside>
  </div>
</section>

<section class="section" id="members" style="padding-top:12px;">
  <div class="section-header reveal">
    <div class="section-tag">Tasting Rooms</div>
    <h2 class="section-title">Wineries on this trail</h2>
    <p class="section-subtitle">Every stop links to a live winery page on MichiganVineyards.com. Hours and known-for notes come from our directory data.</p>
  </div>
  <p class="member-note reveal">{esc(trail['member_note'])}</p>
  <div class="winery-grid reveal">
{tiles}
  </div>
  <div class="more-link-row reveal">
    <a class="btn-primary" href="{esc(trail['directory_href'])}" style="background:var(--trail);color:#fff;">Map &amp; filter this region</a>
{extra}
  </div>
</section>

<section class="cta-band">
  <div class="cta-inner reveal">
    <h2>Build the rest of the trip</h2>
    <p>Load an itinerary, compare nearby trails, or open the full statewide directory map.</p>
    <div class="cta-actions">
      <a class="btn-primary" href="{esc(trail['plan_href'])}">Plan your visit</a>
      <a class="btn-secondary" href="{esc(trail['directory_href'])}">Directory map</a>
      <a class="btn-secondary" href="/wine-trails">All wine trails</a>
    </div>
  </div>
</section>

<section class="other-trails">
  <h2 class="reveal">More Michigan wine trails</h2>
  <div class="other-grid reveal">
    <a href="/wine-trails/river-raisin">River Raisin</a>
    <a href="/wine-trails/lake-michigan-shore">Lake Michigan Shore</a>
    <a href="/wine-trails/old-mission">Old Mission Peninsula</a>
    <a href="/wine-trails/leelanau">Leelanau Peninsula</a>
    <a href="/wine-trails/petoskey">Petoskey / Tip of the Mitt</a>
    <a href="/wine-trails/upper-peninsula">Upper Peninsula</a>
    <a href="/fennville">Fennville region guide</a>
  </div>
</section>

<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-brand">
        <div style="display:flex;flex-direction:column;">
          <span class="logo-main" style="font-family:'Playfair Display',serif;font-weight:600;color:var(--cream);">Michigan Vineyards</span>
          <span class="logo-sub" style="font-size:0.58rem;letter-spacing:0.28em;text-transform:uppercase;margin-top:2px;color:var(--gold);">Wine Country Guide</span>
        </div>
        <p>Your complete guide to Michigan wine country — wineries, regions, wine trails, and trip planning across the state.</p>
      </div>
      <div class="footer-col">
        <h4>Wine Trails</h4>
        <ul>
          <li><a href="/wine-trails/old-mission">Old Mission Peninsula</a></li>
          <li><a href="/wine-trails/leelanau">Leelanau Peninsula</a></li>
          <li><a href="/wine-trails/lake-michigan-shore">Lake Michigan Shore</a></li>
          <li><a href="/wine-trails/petoskey">Petoskey Wine Region</a></li>
          <li><a href="/wine-trails/river-raisin">River Raisin</a></li>
          <li><a href="/wine-trails/upper-peninsula">Upper Peninsula</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="/directory">All Wineries</a></li>
          <li><a href="/wine-trails">Wine Trails</a></li>
          <li><a href="/fennville">Fennville</a></li>
          <li><a href="/the-vine">The Vine</a></li>
          <li><a href="/plan-your-visit">Plan Your Visit</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <ul>
          <li><a href="/about">About Us</a></li>
          <li><a href="/advertise">Advertise</a></li>
          <li><a href="/contact">Contact</a></li>
          <li><a href="/sitemap">Sitemap</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 MichiganVineyards.com · All Rights Reserved</span>
      <div style="display:flex;gap:24px;">
        <a href="/sitemap">Sitemap</a>
        <a href="https://traversecitywinetour.com">Traverse City Wine Tours</a>
      </div>
    </div>
  </div>
</footer>

<script>
const nav=document.getElementById('mainNav');
window.addEventListener('scroll',()=>{{nav.classList.toggle('scrolled',window.scrollY>10);}});
const obs=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('in');obs.unobserve(e.target);}}}});
}},{{threshold:0.12}});
document.querySelectorAll('.reveal').forEach(el=>obs.observe(el));
</script>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for trail in TRAILS:
        path = OUT / f"{trail['slug']}.html"
        path.write_text(render(trail))
        print(f"Wrote {path.relative_to(ROOT)} ({len(trail['members'])} members)")


if __name__ == "__main__":
    main()
