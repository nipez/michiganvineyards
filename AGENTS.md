# Michigan Vineyards

Static Michigan wine-country guide (plain HTML/CSS/JS, no build step). See `README.md` for the page layout and design system.

## Cursor Cloud specific instructions

- This is a fully static site — there is **no build step, no bundler, no automated tests, and no lint tooling**. Page data (winery list, articles) is inlined into the HTML, so pages also work without a running server, but browse it over HTTP to match the production Cloudflare Pages behavior.
- Run the dev server with `serve . -l 3000` (the `serve` package is installed globally under `~/.npm-global`, which the update script keeps refreshed and `~/.bashrc` adds to `PATH`). The README's `npx serve .` also works. A zero-dependency fallback is `python3 -m http.server 3000`.
- `serve` issues `301` redirects from `/page.html` to the clean URL `/page` (e.g. `/directory.html` → `/directory`); both resolve to `200`. `python3 -m http.server` instead serves the `.html` paths directly. Internal links use explicit `.html` paths plus `/` for the homepage, so both servers work.
- Dynamic pages read query params client-side: winery pages are `winery-detail.html?w=<slug>` and there are also pre-rendered per-winery pages under `wineries/<slug>.html`. Editorial articles are `the-vine.html?a=<slug>`.
