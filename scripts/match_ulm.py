#!/usr/bin/env python3
"""
Match ULM DB entries against review_places_db.json with confidence scoring.
Outputs public/data/ulm_matches.json — one entry per ULM record with
the best-scoring main DB match (if any) and confidence breakdown.

Run: python scripts/match_ulm.py

Scoring strategy (max ≈ 113):
  Location:  exact(seg+row+col)=45  seg+row=20  seg=8
  Latin:     exact(compact)=40  contains=24  token≥60%=14
  Modern:    exact=28  contains(min 5ch)=12  token≥60%=8

  HIGH ≥ 70, MEDIUM ≥ 42, LOW < 42

Key normalisation rules:
  - Latin: lowercase, v→u, j→i, strip dots/parens/punctuation
  - Compact Latin: additionally strip all spaces ("Ad Fines" → "adfines")
  - Modern: lowercase, strip accents, take first "/" alternative
  - "contains" for modern requires the shorter string ≥ 5 chars to avoid
    spurious sub-word matches (e.g. "var" inside "chiavari")
"""
import sys, json, re, unicodedata, difflib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ULM_PATH = Path(__file__).parent.parent / "public" / "data" / "ulm_db.json"
DB_PATH  = Path(__file__).parent.parent / "public" / "data" / "review_places_db.json"
OUT_PATH = Path(__file__).parent.parent / "public" / "data" / "ulm_matches.json"

# ── Normalisation ─────────────────────────────────────────────────────────────

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def norm_latin(s):
    """Normalised Latin with spaces preserved (for token splitting)."""
    if not s:
        return ''
    s = strip_accents(s.lower())                    # ē→e, ā→a, v̄→v, etc.
    s = re.sub(r'[··⋅]', '', s)                    # middle dots
    s = s.replace('v', 'u').replace('j', 'i')       # V/U, J/I equivalence
    s = re.sub(r'\([^)]*\)', '', s)                 # drop parenthesised alternates
    s = re.sub(r'[^a-z\s]', '', s)                  # keep only letters + spaces
    s = ' '.join(s.split())
    # Canonicalise synonyms so matching is not blocked by word choice
    s = re.sub(r'\bflumen\b', 'fluuius', s)         # flumen ≡ fluuius (both = river)
    s = re.sub(r'\bins\b', 'insula', s)             # ins → insula
    s = re.sub(r'\bin\b', 'insula', s)              # in  → insula (island abbreviation)
    return s

def compact(s):
    """Remove all spaces from a normalised string: "ad fines" → "adfines"."""
    return ''.join(s.split())

def norm_modern_one(s):
    """Normalise a single modern name string."""
    if not s:
        return ''
    s = strip_accents(s.lower())
    s = re.sub(r'\([^)]*\)', '', s)   # (parenthesised notes)
    s = re.sub(r'\[.*?\]', '', s)     # [bracketed references like [4]]
    s = re.sub(r'\d+\s*(km|mi).*', '', s)  # "7 km. nördlich von …"
    s = re.sub(r'[^a-z\s]', '', s)
    return ' '.join(s.split())

def norm_modern_variants(s):
    """Return all '/' alternatives as normalised strings (non-empty)."""
    if not s:
        return []
    return [v for part in s.split('/') if (v := norm_modern_one(part))]

def norm_modern(s):
    """Backwards-compat: first non-empty variant."""
    vs = norm_modern_variants(s)
    return vs[0] if vs else ''

def token_overlap(a_set, b_set):
    """Jaccard-ish: shared / max(|A|, |B|)."""
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / max(len(a_set), len(b_set))

# ── Score constants ───────────────────────────────────────────────────────────

# Location scores are intentionally modest: the planquadrat grid is coarse
# (several places per cell) so a location-only hit is genuinely ambiguous.
# Name matching carries more weight.
SCORE_LOC_EXACT   = 35   # seg + row + col all match
SCORE_LOC_ROW     = 18   # seg + row match (col unknown or wrong)
SCORE_LOC_SEG     = 7    # segment only

SCORE_LAT_EXACT   = 45   # compact Latin strings equal  ← primary signal
SCORE_LAT_CONTAIN = 26   # one compact Latin contains the other
SCORE_LAT_SIMILAR = 20   # compact forms ≥ 85 % character similarity (e.g. -is/-as variants)
SCORE_LAT_TOKEN   = 16   # token overlap ≥ 60 %

SCORE_MOD_EXACT   = 30   # modern strings equal
SCORE_MOD_CONTAIN = 14   # one contains the other (min 5 chars)
SCORE_MOD_TOKEN   = 9    # token overlap ≥ 60 %

MOD_CONTAIN_MIN   = 5    # minimum length for "contains" modern match

# Thresholds (max ≈ 35+45+30 = 110):
#   HIGH   needs at least loc_exact + lat_exact (80) or equivalent strong combo
#   MEDIUM a meaningful but uncertain match — loc_exact + partial name, or name alone
#   LOW    only location overlap, no name support
THRESH_HIGH   = 70
THRESH_MEDIUM = 42


# ── Pair scorer ───────────────────────────────────────────────────────────────

def score_pair(ulm, db):
    score = 0
    bk = {}

    # ── Location ──────────────────────────────────────────────────────────────
    db_seg  = db.get('tabula_segment')
    db_row  = db.get('tabula_row')
    db_col  = db.get('tabula_col')

    # Parse ALL cells from planquadrat (e.g. "5A3 / 5B3" → [(5,'a',3),(5,'b',3)])
    # and take the best location score across all cells.
    pq_raw = ulm.get('planquadrat', '') or ''
    pq_cells = [(int(m.group(1)), m.group(2).lower(), int(m.group(3)))
                for m in re.finditer(r'(\d+)([A-Ca-c])(\d+)', pq_raw)]

    if not pq_cells:
        # Fall back to pre-parsed fields (may be None)
        ulm_seg = ulm.get('ulm_segment')
        if ulm_seg is not None:
            pq_cells = [(ulm_seg, ulm.get('ulm_row'), ulm.get('ulm_col'))]

    best_loc_score = 0
    best_loc_label = 'unknown'

    if db_seg is not None and pq_cells:
        for (ulm_seg, ulm_row, ulm_col) in pq_cells:
            if (db_seg - 1) != ulm_seg:           # DB segment = ULM segment + 1
                continue
            best_loc_label = 'none'               # at least segment tried
            row_ok = db_row and ulm_row and db_row == ulm_row
            col_ok = db_col is not None and ulm_col is not None and db_col == ulm_col
            if row_ok and col_ok:
                s = SCORE_LOC_EXACT; lbl = 'exact'
            elif row_ok:
                s = SCORE_LOC_ROW;   lbl = 'seg+row'
            else:
                s = SCORE_LOC_SEG;   lbl = 'seg'
            if s > best_loc_score:
                best_loc_score = s
                best_loc_label = lbl

        if best_loc_score == 0 and best_loc_label == 'unknown':
            best_loc_label = 'none'

    elif db_seg is None or not pq_cells:
        best_loc_label = 'unknown'

    score += best_loc_score
    bk['loc'] = best_loc_label

    # ── Latin name ────────────────────────────────────────────────────────────
    # Try both ULM resolved latin and latin_tp; use the better match.
    # DB may have the name in 'latin' or 'latin_std'.
    raw_db_lat = db.get('latin', '') or db.get('latin_std', '') or ''
    nl_db  = norm_latin(raw_db_lat)
    cp_db  = compact(nl_db)

    def score_latin_one(raw_ulm):
        nl_ulm = norm_latin(raw_ulm)
        cp_ulm = compact(nl_ulm)
        if not cp_db or not cp_ulm:
            return 0, 'missing'
        if cp_db == cp_ulm:
            return SCORE_LAT_EXACT, 'exact'
        if cp_db in cp_ulm or cp_ulm in cp_db:
            return SCORE_LAT_CONTAIN, 'contains'
        sim = difflib.SequenceMatcher(None, cp_db, cp_ulm, autojunk=False).ratio()
        if sim >= 0.85:
            return SCORE_LAT_SIMILAR, f'similar({sim:.0%})'
        tok_db  = set(nl_db.split())
        tok_ulm = set(nl_ulm.split())
        ov = token_overlap(tok_db, tok_ulm)
        if ov >= 0.6:
            return SCORE_LAT_TOKEN, f'tokens({ov:.0%})'
        return 0, f'low({ov:.0%})' if ov > 0 else 'low(0%)'

    lat_score_a, lat_bk_a = score_latin_one(ulm.get('latin', '') or '')
    lat_score_b, lat_bk_b = score_latin_one(ulm.get('latin_tp', '') or '')
    if lat_score_a >= lat_score_b:
        score += lat_score_a; bk['latin'] = lat_bk_a
    else:
        score += lat_score_b; bk['latin'] = lat_bk_b + '(tp)'

    # ── Modern name ───────────────────────────────────────────────────────────
    # ULM modern can have multiple '/' alternatives — try each against DB.
    nm_db   = norm_modern(db.get('modern_preferred', '') or db.get('modern', '') or '')
    ulm_mods = norm_modern_variants(ulm.get('modern', '') or '')

    def score_modern_one(nm_ulm):
        if not nm_db or not nm_ulm:
            return 0, 'missing'
        if nm_db == nm_ulm:
            return SCORE_MOD_EXACT, 'exact'
        shorter = nm_db if len(nm_db) <= len(nm_ulm) else nm_ulm
        if len(shorter) >= MOD_CONTAIN_MIN and (nm_db in nm_ulm or nm_ulm in nm_db):
            return SCORE_MOD_CONTAIN, 'contains'
        tok_db  = set(nm_db.split())
        tok_ulm = set(nm_ulm.split())
        ov = token_overlap(tok_db, tok_ulm)
        if ov >= 0.6:
            return SCORE_MOD_TOKEN, f'tokens({ov:.0%})'
        return 0, f'low({ov:.0%})' if ov > 0 else 'low(0%)'

    if ulm_mods:
        best_mod_score, best_mod_bk = max(
            (score_modern_one(m) for m in ulm_mods), key=lambda x: x[0]
        )
        score += best_mod_score
        bk['modern'] = best_mod_bk
    else:
        bk['modern'] = 'missing'

    return score, bk


def confidence_label(score):
    if score >= THRESH_HIGH:   return 'high'
    if score >= THRESH_MEDIUM: return 'medium'
    return 'low'


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ulm_data = json.loads(ULM_PATH.read_text(encoding='utf-8'))
    db_data  = json.loads(DB_PATH.read_text(encoding='utf-8'))

    ulm_entries = ulm_data['entries']
    db_records  = db_data['records']

    # Candidates: any record with a segment or a Latin name
    db_candidates = [r for r in db_records
                     if r.get('tabula_segment') is not None or r.get('latin')]

    print(f"ULM entries:   {len(ulm_entries)}")
    print(f"DB candidates: {len(db_candidates)}")

    results = []
    stats = {'high': 0, 'medium': 0, 'low': 0}

    for ulm in ulm_entries:
        ulm_seg = ulm.get('ulm_segment')
        db_seg_expected = (ulm_seg + 1) if ulm_seg is not None else None

        # Pre-filter: collect all expected DB segments from multi-cell planquadrat
        pq_raw = ulm.get('planquadrat', '') or ''
        pq_segs = {int(m.group(1)) + 1
                   for m in re.finditer(r'(\d+)[A-Ca-c]\d+', pq_raw)}
        if ulm_seg is not None:
            pq_segs.add(ulm_seg + 1)

        if pq_segs:
            candidates = [r for r in db_candidates
                          if r.get('tabula_segment') is None
                          or any(abs((r.get('tabula_segment') or 0) - s) <= 1
                                 for s in pq_segs)]
        else:
            candidates = db_candidates

        best_score = -1
        best_db    = None
        best_bk    = {}

        for r in candidates:
            s, bk = score_pair(ulm, r)
            if s > best_score:
                best_score = s
                best_db    = r
                best_bk    = bk

        label = confidence_label(best_score)
        stats[label] += 1

        entry = {
            'ulm_id':           ulm['ulm_id'],
            'ulm_latin':        ulm.get('latin', ''),
            'ulm_modern':       ulm.get('modern', ''),
            'ulm_planquadrat':  ulm.get('planquadrat', ''),
            'confidence':       best_score,
            'confidence_label': label,
            'match_breakdown':  best_bk,
        }

        if best_db and best_score >= THRESH_MEDIUM:
            entry['db_record_id'] = best_db.get('record_id', '')
            entry['db_data_id']   = best_db.get('data_id')
            entry['db_latin']     = best_db.get('latin', '')
            entry['db_modern']    = (best_db.get('modern_preferred', '')
                                     or best_db.get('modern', ''))
            entry['db_segment']   = best_db.get('tabula_segment')
            entry['db_location']  = best_db.get('tabula_location', '')
        else:
            entry['db_record_id'] = None
            entry['db_data_id']   = None
            entry['db_latin']     = None
            entry['db_modern']    = None
            entry['db_segment']   = None
            entry['db_location']  = None

        results.append(entry)

    out = {
        'meta': {
            'description': 'ULM DB → review_places_db.json match results',
            'total': len(results),
            'stats': stats,
        },
        'matches': results,
    }

    tmp = OUT_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(OUT_PATH)
    print(f"Saved {len(results)} match results → {OUT_PATH.name}")
    print(f"Confidence: high={stats['high']}, medium={stats['medium']}, low={stats['low']}")


if __name__ == '__main__':
    main()
