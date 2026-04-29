#!/usr/bin/env python3
"""
Find duplicate records in review_places_db.json.

Three confidence tiers:
  certain    — same ulm_id on ≥ 2 records from DIFFERENT sources
  very_likely — same segment+row+col + normalised Latin identical, different sources
  likely      — same segment + normalised Latin SequenceMatcher ≥ 0.85 (len ≥ 5),
                at least one pair from different sources

Groups are deduplicated (same normalised name across N records → one group, not N² pairs).
Tier 1 groups are excluded from tiers 2 & 3.

Run:    python scripts/find_duplicates.py
Output: public/data/duplicate_report.json
"""
import sys, json, re, unicodedata, difflib
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH  = Path(__file__).parent.parent / "public" / "data" / "review_places_db.json"
OUT_PATH = Path(__file__).parent.parent / "public" / "data" / "duplicate_report.json"

# ── Normalisation ─────────────────────────────────────────────────────────────

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def norm(s):
    if not s:
        return ''
    s = strip_accents(s.lower())
    s = re.sub(r'\([^)]*\)', '', s)
    s = s.replace('v', 'u').replace('j', 'i')
    s = re.sub(r'[^a-z]', '', s)
    return s

# ── Keep-rule ─────────────────────────────────────────────────────────────────

SOURCE_RANK = {'tabula': 0, 'omnesviae': 1, 'ulm': 2, 'tabula_runtime': 3}

def keep_rank(r):
    return (SOURCE_RANK.get(r.get('source', ''), 9),
            0 if r.get('ulm_id') else 1)

def best_record(records):
    return min(records, key=keep_rank)['record_id']

def has_cross_source(records):
    sources = {r.get('source') for r in records}
    return len(sources) > 1

# ── Record summary ─────────────────────────────────────────────────────────────

def rec_summary(r):
    return {
        'record_id': r.get('record_id'),
        'source':    r.get('source'),
        'latin':     r.get('latin', ''),
        'modern':    r.get('modern_preferred') or r.get('modern_tabula') or '',
        'segment':   r.get('tabula_segment'),
        'row':       r.get('tabula_row'),
        'col':       r.get('tabula_col'),
        'ulm_id':    r.get('ulm_id'),
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    db      = json.loads(DB_PATH.read_text(encoding='utf-8'))
    records = db['records']

    groups   = []
    seen_ids = set()   # record_ids already in a certain group

    # ── Tier 1: same ulm_id, cross-source ────────────────────────────────────
    by_ulm = defaultdict(list)
    for r in records:
        uid = r.get('ulm_id')
        if uid is not None:
            by_ulm[uid].append(r)

    for uid, grp in sorted(by_ulm.items()):
        if len(grp) < 2:
            continue
        if not has_cross_source(grp):
            continue          # same source with same ulm_id — data quirk, not dup
        keep = best_record(grp)
        rids = [r['record_id'] for r in grp]
        for rid in rids:
            seen_ids.add(rid)
        groups.append({
            'confidence': 'certain',
            'ulm_id':     uid,
            'keep':       keep,
            'remove':     [rid for rid in rids if rid != keep],
            'records':    [rec_summary(r) for r in grp],
        })

    # ── Tiers 2 & 3: group by (segment, norm_latin) ──────────────────────────
    # Group all records per segment by normalised Latin name
    # key = (segment, norm_name)
    name_groups = defaultdict(list)
    for r in records:
        if r['record_id'] in seen_ids:
            continue
        seg = r.get('tabula_segment')
        if seg is None:
            continue
        n = norm(r.get('latin') or r.get('latin_std') or '')
        if not n or len(n) < 4:
            continue
        name_groups[(seg, n)].append(r)

    # Tier 2: identical normalised name, cross-source required
    for (seg, n), grp in sorted(name_groups.items()):
        if len(grp) < 2:
            continue
        if not has_cross_source(grp):
            continue
        keep = best_record(grp)
        rids = [r['record_id'] for r in grp]
        groups.append({
            'confidence': 'very_likely',
            'ulm_id':     None,
            'keep':       keep,
            'remove':     [rid for rid in rids if rid != keep],
            'records':    [rec_summary(r) for r in grp],
        })

    # Tier 3: ≥0.85 similarity, cross-source, len≥5, pairwise across different names
    # Build per-segment list of (norm_name, record) for cross-name fuzzy matching
    seg_index = defaultdict(list)   # seg → list of (norm_name, record)
    for (seg, n), grp in name_groups.items():
        for r in grp:
            seg_index[seg].append((n, r))

    already_paired = set()   # frozenset of record_id pairs

    for seg, items in seg_index.items():
        for i in range(len(items)):
            na, a = items[i]
            for j in range(i + 1, len(items)):
                nb, b = items[j]
                if na == nb:
                    continue   # already handled in tier 2
                if a.get('source') == b.get('source'):
                    continue   # require cross-source for fuzzy
                if len(na) < 5 or len(nb) < 5:
                    continue
                pair_key = frozenset([a['record_id'], b['record_id']])
                if pair_key in already_paired:
                    continue
                ratio = difflib.SequenceMatcher(None, na, nb, autojunk=False).ratio()
                if ratio < 0.85:
                    continue
                already_paired.add(pair_key)
                grp = [a, b]
                keep = best_record(grp)
                rids = [r['record_id'] for r in grp]
                groups.append({
                    'confidence': 'likely',
                    'ulm_id':     None,
                    'similarity': round(ratio, 3),
                    'keep':       keep,
                    'remove':     [rid for rid in rids if rid != keep],
                    'records':    [rec_summary(r) for r in grp],
                })

    # ── Stats ─────────────────────────────────────────────────────────────────
    counts = {'certain': 0, 'very_likely': 0, 'likely': 0}
    for g in groups:
        counts[g['confidence']] += 1

    total_remove = sum(len(g['remove']) for g in groups)

    print(f"Duplicate groups found:")
    print(f"  certain:     {counts['certain']:4d}  (same ulm_id, cross-source)")
    print(f"  very_likely: {counts['very_likely']:4d}  (same segment, identical normalised Latin, cross-source)")
    print(f"  likely:      {counts['likely']:4d}  (same segment, ≥85% similar Latin, cross-source)")
    print(f"  total:       {sum(counts.values()):4d}  groups  |  {total_remove} records recommended for removal")

    out = {
        'meta': {
            'total_groups': len(groups),
            'total_remove': total_remove,
            'counts': counts,
        },
        'groups': groups,
    }

    tmp = OUT_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(OUT_PATH)
    print(f"Written → {OUT_PATH.name}")


if __name__ == '__main__':
    main()
