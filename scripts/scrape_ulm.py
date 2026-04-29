#!/usr/bin/env python3
"""
Scrape all 3772 ULM DB detail pages and save to public/data/ulm_db.json.
Run: python scripts/scrape_ulm.py [--resume]
"""
import sys, re, json, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

OUT_PATH   = Path(__file__).parent.parent / "public" / "data" / "ulm_db.json"
BASE_URL   = "https://tp-online.ku.de/trefferanzeige.php?id="
WORKERS    = 20
TIMEOUT    = 12
TOTAL_IDS  = 3772


def clean(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&nbsp;?', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&lt;', '<', s)
    s = re.sub(r'&gt;', '>', s)
    return ' '.join(s.split()).strip()


def parse_field(html, *labels):
    """Extract value for the first matching label in the detail table."""
    for label in labels:
        pattern = (
            r'<td>\s*' + re.escape(label) + r'\s*</td>\s*'
            r'<td[^>]*>\s*<p[^>]*>\s*(.*?)\s*</p>'
        )
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            val = clean(m.group(1))
            if val and val not in ('&nbsp', '---', '-'):
                return val
    return ''


def parse_link_field(html, *labels):
    """Extract href from a link cell (e.g. Pleiades, Wikipedia)."""
    for label in labels:
        pattern = (
            r'<td>\s*' + re.escape(label) + r'\s*</td>\s*'
            r'<td[^>]*>.*?<a\s+href="([^"]+)"'
        )
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ''


def parse_planquadrat(pq_str):
    """Parse '3A1' or '3A1-3A2' into {segment, row, col} using first cell.
    ULM segment is 1-indexed but shifted -1 vs our DB (DB = ULM+1).
    Row letter: A→a, B→b, C→c (ULM uses uppercase).
    """
    if not pq_str:
        return None, None, None
    m = re.match(r'^(\d+)([ABC])(\d+)', pq_str.strip().upper())
    if not m:
        return None, None, None
    seg_ulm = int(m.group(1))
    row = m.group(2).lower()
    col = int(m.group(3))
    return seg_ulm, row, col


def fetch_page(ulm_id):
    url = BASE_URL + str(ulm_id)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        return ulm_id, html, None
    except Exception as e:
        return ulm_id, None, str(e)


def parse_entry(ulm_id, html):
    # Extract inset image filename
    img_m = re.search(r'insetimages/(TPPlace\d+insetneu[^"\'<\s]*)', html)
    img_url = f"https://tp-online.ku.de/insetimages/{img_m.group(1)}" if img_m else ''

    # Planquadrat
    pq_raw = parse_field(html, 'Planquadrat:')
    seg_ulm, row, col = parse_planquadrat(pq_raw)

    return {
        "ulm_id":        ulm_id,
        "latin":         parse_field(html, 'Toponym TP (aufgelöst):', 'Toponym TP (aufgelöst)'),
        "latin_tp":      parse_field(html, 'Toponym TP:'),
        "modern":        parse_field(html, 'Name (modern):'),
        "planquadrat":   pq_raw,
        "ulm_segment":   seg_ulm,          # ULM segment (DB segment = ulm_segment + 1)
        "ulm_row":       row,
        "ulm_col":       col,
        "grossraum":     parse_field(html, 'Großraum:'),
        "typus":         parse_field(html, 'Toponym Typus:'),
        "farbe":         parse_field(html, 'Farbe des Toponyms:'),
        "vignette":      parse_field(html, 'Vignette Typus :', 'Vignette Typus:'),
        "datierung":     parse_field(html, 'Datierung des Toponyms auf der TP:'),
        "pleiades":      parse_link_field(html, 'Pleiades:'),
        "img_url":       img_url,
    }


def main():
    resume = '--resume' in sys.argv

    # Load existing results if resuming
    existing = {}
    if resume and OUT_PATH.exists():
        data = json.loads(OUT_PATH.read_text(encoding='utf-8'))
        existing = {e['ulm_id']: e for e in data.get('entries', [])}
        print(f"Resuming — {len(existing)} already fetched")

    remaining = [i for i in range(1, TOTAL_IDS + 1) if i not in existing]
    print(f"Fetching {len(remaining)} pages with {WORKERS} workers…")

    results = dict(existing)
    errors = {}
    done = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(fetch_page, i): i for i in remaining}
        for fut in as_completed(futures):
            ulm_id, html, err = fut.result()
            done += 1
            if html:
                results[ulm_id] = parse_entry(ulm_id, html)
            else:
                errors[ulm_id] = err
            if done % 100 == 0 or done == len(remaining):
                elapsed = time.time() - t0
                rate = done / elapsed
                eta = (len(remaining) - done) / rate if rate > 0 else 0
                print(f"  {done}/{len(remaining)} done  errors={len(errors)}  {rate:.1f}/s  ETA={eta:.0f}s")

    # Sort by ulm_id and save
    entries = [results[i] for i in sorted(results)]
    out = {
        "meta": {
            "description": "ULM Tabula Peutingeriana Database",
            "source": "https://tp-online.ku.de/",
            "total": len(entries),
            "errors": len(errors),
            "error_ids": sorted(errors.keys()),
        },
        "entries": entries,
    }

    tmp = OUT_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(OUT_PATH)
    print(f"Saved {len(entries)} entries to {OUT_PATH}  ({len(errors)} errors)")
    if errors:
        print("Error IDs:", sorted(errors.keys())[:20])


if __name__ == '__main__':
    main()
