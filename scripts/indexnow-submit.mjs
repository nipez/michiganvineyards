#!/usr/bin/env node
/**
 * Submit URLs to IndexNow (https://www.indexnow.org/).
 *
 * Usage:
 *   node scripts/indexnow-submit.mjs                  # changed/new vs previous sitemap, else all
 *   node scripts/indexnow-submit.mjs --all             # every sitemap URL
 *   node scripts/indexnow-submit.mjs /the-vine/foo path/or/url...
 *
 * Env:
 *   INDEXNOW_HOST              default michiganvineyards.com
 *   INDEXNOW_ENDPOINT          default https://api.indexnow.org/indexnow
 *   INDEXNOW_KEY               optional; otherwise discovered from /<32-hex>.txt in repo root
 *   INDEXNOW_KEY_LOCATION      optional absolute URL of the key file
 *   INDEXNOW_SITEMAP           path to sitemap.xml (default ./sitemap.xml)
 *   INDEXNOW_PREVIOUS_SITEMAP  path or https URL of the prior sitemap for diffing
 *   INDEXNOW_GIT_BASE          git ref to diff against (default HEAD^ when available)
 *
 * IndexNow HTTP errors are logged and do not fail the process (exit 0).
 */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { resolve, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const ROOT = resolve(fileURLToPath(new URL("..", import.meta.url)));
const HOST = process.env.INDEXNOW_HOST || "michiganvineyards.com";
const ENDPOINT = process.env.INDEXNOW_ENDPOINT || "https://api.indexnow.org/indexnow";
const SITEMAP_PATH = resolve(ROOT, process.env.INDEXNOW_SITEMAP || "sitemap.xml");
const MAX_URLS = 10_000;
const KEY_FILE_RE = /^[a-f0-9]{32}\.txt$/i;

function log(...args) {
  console.log("[indexnow]", ...args);
}

function warn(...args) {
  console.warn("[indexnow]", ...args);
}

function discoverKey() {
  if (process.env.INDEXNOW_KEY) {
    const key = process.env.INDEXNOW_KEY.trim();
    return {
      key,
      keyLocation:
        process.env.INDEXNOW_KEY_LOCATION || `https://${HOST}/${key}.txt`,
    };
  }

  const matches = readdirSync(ROOT).filter((name) => KEY_FILE_RE.test(name));
  if (matches.length === 0) {
    throw new Error(`No IndexNow key file matching /[a-f0-9]{32}.txt in ${ROOT}`);
  }
  if (matches.length > 1) {
    warn(`Multiple key files found (${matches.join(", ")}); using ${matches[0]}`);
  }
  const file = matches[0];
  const key = readFileSync(resolve(ROOT, file), "utf8").trim();
  const expected = file.replace(/\.txt$/i, "");
  if (key !== expected) {
    throw new Error(`Key file ${file} body (${key}) does not match filename`);
  }
  return {
    key,
    keyLocation: process.env.INDEXNOW_KEY_LOCATION || `https://${HOST}/${file}`,
  };
}

function parseSitemap(xml) {
  const entries = new Map(); // loc -> lastmod|null
  const urlBlocks = xml.match(/<url\b[\s\S]*?<\/url>/gi) || [];
  for (const block of urlBlocks) {
    const loc = (block.match(/<loc>\s*([^<\s]+)\s*<\/loc>/i) || [])[1];
    if (!loc) continue;
    const lastmod = (block.match(/<lastmod>\s*([^<\s]+)\s*<\/lastmod>/i) || [])[1] || null;
    entries.set(loc.trim(), lastmod ? lastmod.trim() : null);
  }
  return entries;
}

function readSitemapFile(path) {
  return parseSitemap(readFileSync(path, "utf8"));
}

async function readSitemapSource(source) {
  if (!source) return null;
  if (/^https?:\/\//i.test(source)) {
    const res = await fetch(source);
    if (!res.ok) {
      warn(`Failed to fetch previous sitemap ${source}: HTTP ${res.status}`);
      return null;
    }
    return parseSitemap(await res.text());
  }
  const path = resolve(ROOT, source);
  if (!existsSync(path)) {
    warn(`Previous sitemap not found: ${path}`);
    return null;
  }
  return readSitemapFile(path);
}

function gitShow(refPath) {
  const result = spawnSync("git", ["show", refPath], {
    cwd: ROOT,
    encoding: "utf8",
    maxBuffer: 20 * 1024 * 1024,
  });
  if (result.status !== 0) return null;
  return result.stdout;
}

function gitDiffNames(base) {
  const result = spawnSync("git", ["diff", "--name-only", "--diff-filter=AM", base, "HEAD"], {
    cwd: ROOT,
    encoding: "utf8",
  });
  if (result.status !== 0) return [];
  return result.stdout.split("\n").map((l) => l.trim()).filter(Boolean);
}

function gitBaseAvailable(base) {
  const result = spawnSync("git", ["rev-parse", "--verify", base], {
    cwd: ROOT,
    encoding: "utf8",
  });
  return result.status === 0;
}

function toSiteUrl(input) {
  const raw = input.trim();
  if (!raw) return null;
  if (/^https?:\/\//i.test(raw)) return raw;
  let path = raw.replace(/\\/g, "/");
  if (path.endsWith(".html")) path = path.slice(0, -5);
  if (path === "index" || path === "/index") path = "/";
  if (!path.startsWith("/")) path = `/${path}`;
  if (path !== "/" && path.endsWith("/")) path = path.slice(0, -1);
  return path === "/" ? `https://${HOST}/` : `https://${HOST}${path}`;
}

function filePathToUrl(relPath) {
  const norm = relPath.split(sep).join("/");
  if (!norm.endsWith(".html")) return null;
  if (norm === "404.html" || norm === "winery-detail.html") return null;
  if (norm.startsWith("winery-detail-images/")) return null;
  return toSiteUrl(norm);
}

function diffSitemaps(current, previous) {
  const changed = [];
  for (const [loc, lastmod] of current) {
    if (!previous.has(loc)) {
      changed.push(loc);
      continue;
    }
    if ((lastmod || "") !== (previous.get(loc) || "")) {
      changed.push(loc);
    }
  }
  return changed;
}

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

async function submitBatch({ host, key, keyLocation, urlList }) {
  const body = JSON.stringify({ host, key, keyLocation, urlList });
  const res = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body,
  });
  const text = await res.text().catch(() => "");
  log(`POST ${ENDPOINT} → HTTP ${res.status} (${urlList.length} URL${urlList.length === 1 ? "" : "s"})`);
  if (text) log(text.slice(0, 500));
  return res.status;
}

async function main() {
  const args = process.argv.slice(2);
  const forceAll = args.includes("--all");
  const positional = args.filter((a) => a !== "--all");

  const { key, keyLocation } = discoverKey();
  if (!existsSync(SITEMAP_PATH)) {
    throw new Error(`sitemap not found: ${SITEMAP_PATH}`);
  }
  const current = readSitemapFile(SITEMAP_PATH);
  const allUrls = [...current.keys()];
  log(`Loaded ${allUrls.length} URLs from ${relative(ROOT, SITEMAP_PATH) || "sitemap.xml"}`);
  log(`keyLocation=${keyLocation}`);

  let urls = [];
  let reason = "";

  if (positional.length) {
    urls = [...new Set(positional.map(toSiteUrl).filter(Boolean))];
    reason = "cli arguments";
  } else if (forceAll) {
    urls = allUrls;
    reason = "--all";
  } else {
    const selected = new Set();

    const previous = await readSitemapSource(process.env.INDEXNOW_PREVIOUS_SITEMAP);
    if (previous) {
      for (const loc of diffSitemaps(current, previous)) selected.add(loc);
      log(`Sitemap diff vs INDEXNOW_PREVIOUS_SITEMAP → ${selected.size} changed/new`);
    } else {
      const base = process.env.INDEXNOW_GIT_BASE || "HEAD^";
      if (gitBaseAvailable(base)) {
        const prevXml = gitShow(`${base}:sitemap.xml`);
        if (prevXml) {
          for (const loc of diffSitemaps(current, parseSitemap(prevXml))) selected.add(loc);
          log(`Sitemap diff vs ${base}:sitemap.xml → ${selected.size} changed/new`);
        }
        for (const file of gitDiffNames(base)) {
          const loc = filePathToUrl(file);
          if (loc) selected.add(loc);
        }
        log(`After git path diff vs ${base} → ${selected.size} candidate URL(s)`);
      } else {
        warn(`Git base ${base} unavailable; cannot diff`);
      }
    }

    urls = [...selected];
    reason = "changed/new detection";
    if (urls.length === 0) {
      urls = allUrls;
      reason = "fallback: all sitemap URLs (nothing changed could be determined)";
    }
  }

  // Prefer sitemap membership, but keep explicitly requested / git-mapped host URLs.
  urls = [...new Set(urls)].filter((u) => {
    try {
      return new URL(u).hostname === HOST;
    } catch {
      return false;
    }
  });

  if (urls.length === 0) {
    log("No URLs to submit.");
    return;
  }

  log(`Submitting ${urls.length} URL(s) (${reason})`);

  for (const batch of chunk(urls, MAX_URLS)) {
    try {
      await submitBatch({ host: HOST, key, keyLocation, urlList: batch });
    } catch (err) {
      warn(`Request failed: ${err && err.message ? err.message : err}`);
    }
  }
}

main().catch((err) => {
  warn(`Fatal (non-deploy-blocking): ${err && err.message ? err.message : err}`);
  process.exitCode = 0;
});
