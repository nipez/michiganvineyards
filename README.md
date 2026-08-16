# Michigan Vineyards

Michigan wine country guide — wineries, regions, wine trails, and trip-planning pages across the state.

This is a **static site**, recovered from the live Cloudflare Pages direct-upload deployment (`michiganvineyards`, production domain [michiganvineyards.com](https://michiganvineyards.com)). It was not previously on Git, so the published files are the source of truth.

## Run locally

```bash
npx serve .
```

Then open the URL `serve` prints (usually http://localhost:3000).

## Layout

- `index.html` — homepage
- `directory.html` — filterable winery directory
- `regions.html`, `wine-trails.html`, `plan-your-visit.html` — planning pages
- `the-vine.html` — editorial / blog template
- `events.html`, `about.html`, `advertise.html`, `contact.html`
- `winery-detail.html` — winery detail template
- `wineries/` — 163 individual winery pages
- `winery-detail-images/` — 8 placeholder photos
- `wineries_data.json` — winery dataset (name, region, type, hours, city)
- `sitemap.xml`, `sitemap.html`, `robots.txt`

## Design system

- **Primary:** Forest Green `#1B3A2D`
- **Accent:** Gold `#C9A96E`
- **Background:** Cream `#F5F0E8`
- **Fonts:** Playfair Display (headings), Cormorant Garamond (editorial), Outfit (body)

## Cloudflare Pages

- **Project name:** `michiganvineyards`
- **Production domain:** https://michiganvineyards.com
- **Pages.dev:** https://michiganvineyards.pages.dev

Direct Upload originally (not Git-connected). Re-deploy from this repo after connecting the project to GitHub if you want Git-based deploys.
