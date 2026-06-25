#!/usr/bin/env python3
"""Enrich Segment I places with Wikipedia URLs via Wikipedia search API.

For each Seg I record without a wiki_url:
  1. Search Wikipedia for the latin name (as Roman place)
  2. Search for modern name if known
  3. Accept if Wikipedia article coordinates are within MAX_DIST_KM of our DB coords

Usage:
  python scripts/enrich_seg1_wiki.py [--dry-run] [--limit N]
"""
import json, sys, io, math, re, time, urllib.parse, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

DB_PATH = "public/data/review_places_db.json"
DRY_RUN = "--dry-run" in sys.argv
LIMIT = next((int(sys.argv[sys.argv.index("--limit") + 1])
              for i, a in enumerate(sys.argv) if a == "--limit"), None)
MAX_DIST_KM = 80
UA = "TabulaPeutingerianaEnricher/1.0 (tabula-peutingeriana.com)"

COUNTRY_LANGS = {
    "GB": ["en"],
    "ES": ["es", "en"],
    "PT": ["pt", "en"],
    "MA": ["fr", "en"],
    "DZ": ["fr", "en"],
    "FR": ["fr", "en"],
}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d = math.radians
    dlat, dlon = d(lat2 - lat1), d(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(d(lat1)) * math.cos(d(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 * (attempt + 1))
            else:
                return None
        except Exception:
            time.sleep(1)
    return None


def wiki_lookup(lang, title):
    """Return (lat, lng, url) or None."""
    params = urllib.parse.urlencode({
        "action": "query", "titles": title,
        "prop": "coordinates|pageprops", "redirects": 1, "format": "json",
    })
    data = http_get(f"https://{lang}.wikipedia.org/w/api.php?{params}")
    if not data:
        return None
    for pid, page in data.get("query", {}).get("pages", {}).items():
        if pid == "-1":
            continue
        coords = page.get("coordinates", [])
        if not coords:
            continue
        actual = page.get("title", title)
        url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(actual.replace(' ', '_'))}"
        return (coords[0]["lat"], coords[0]["lon"], url)
    return None


def wiki_search(lang, query):
    """Full-text search, return (lat, lng, url) for first hit with coords."""
    params = urllib.parse.urlencode({
        "action": "query", "list": "search",
        "srsearch": query, "srlimit": 3, "format": "json",
    })
    data = http_get(f"https://{lang}.wikipedia.org/w/api.php?{params}")
    if not data:
        return None
    for hit in data.get("query", {}).get("search", []):
        r = wiki_lookup(lang, hit["title"])
        if r:
            return r
    return None


def find_wiki(record):
    lat, lng = float(record["lat"]), float(record["lng"])
    country = (record.get("country") or "").split("|")[0].strip()
    langs = COUNTRY_LANGS.get(country, ["en"])
    latin = re.sub(r"\s*\(.*\)", "", record.get("latin_std") or record.get("latin") or "").strip()
    modern = record.get("modern_preferred") or ""

    candidates = []
    # Strategy 1: direct Latin name lookup
    for lang in langs:
        r = wiki_lookup(lang, latin)
        if r:
            candidates.append(r)
    # Strategy 2: search "Latin ancient <modern country>"
    for lang in langs[:1]:
        r = wiki_search(lang, f"{latin} Roman ancient")
        if r:
            candidates.append(r)
    # Strategy 3: modern name
    if modern and modern not in ("?", ""):
        for lang in langs[:1]:
            r = wiki_lookup(lang, modern)
            if r:
                candidates.append(r)

    for wlat, wlng, url in candidates:
        dist = haversine(lat, lng, wlat, wlng)
        if dist <= MAX_DIST_KM:
            return url, dist
    return None, None


def main():
    data = json.loads(open(DB_PATH, encoding="utf-8").read())
    records = data["records"]

    seg1 = [r for r in records if r.get("tabula_segment") == 1 and not r.get("wiki_url")
            and r.get("lat") and r.get("lng")]
    print(f"Seg I records without wiki_url: {len(seg1)}")
    if LIMIT:
        seg1 = seg1[:LIMIT]

    found = 0
    for i, r in enumerate(seg1):
        name = r.get("latin_std") or r.get("latin") or "?"
        url, dist = find_wiki(r)
        if url:
            print(f"  [{i+1}/{len(seg1)}] {name:35s} → {url}  ({dist:.1f} km)")
            if not DRY_RUN:
                r["wiki_url"] = url
                r["wiki_confidence"] = 2
            found += 1
        else:
            print(f"  [{i+1}/{len(seg1)}] {name:35s} → (no match)")
        time.sleep(0.3)  # polite rate limiting

    if not DRY_RUN and found:
        open(DB_PATH, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        )
    print(f"\nDone. {found}/{len(seg1)} wiki URLs found and written.")


if __name__ == "__main__":
    main()
