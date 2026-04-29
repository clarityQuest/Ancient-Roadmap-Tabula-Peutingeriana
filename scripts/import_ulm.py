#!/usr/bin/env python3
"""
Import ULM DB data into review_places_db.json.

1. HIGH/MEDIUM matches — enrich existing DB records:
   - Always write correct ulm_id
   - Overwrite modern_preferred if ULM has a modern name
   - Overwrite latin (and latin_std) when normalised forms differ
   - Write vignette field

2. LOW matches — add as new DB records (source='ulm').

3. Vignette imported for all entries.

Run: python scripts/import_ulm.py
"""
import sys, json, re, unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH      = Path(__file__).parent.parent / "public" / "data" / "review_places_db.json"
ULM_PATH     = Path(__file__).parent.parent / "public" / "data" / "ulm_db.json"
MATCHES_PATH = Path(__file__).parent.parent / "public" / "data" / "ulm_matches.json"

# ── Normalisation (mirrors match_ulm.py) ─────────────────────────────────────

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def norm_latin(s):
    if not s:
        return ''
    s = strip_accents(s.lower())
    s = re.sub(r'[··⋅]', '', s)
    s = s.replace('v', 'u').replace('j', 'i')
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'[^a-z\s]', '', s)
    return ' '.join(s.split())

# ── Type mapping ──────────────────────────────────────────────────────────────

TYPUS_MAP = {
    'Fluss':                        'river',
    'Insel':                        'island',
    'Wasser (ohne Flussname)':      'water',
    'Berg/Gebirge':                 'mountain',
    'Ethnikon':                     'people',
    'Region':                       'region',
    'chorographische Information':  'region',
    'Itinerareintrag/via publica':  'road_station',
    'Ortsname mit Symbol':          'road_station',
    'Ortsname ohne Symbol':         'road_station',
    'isolierter Name':              'road_station',
    'isoliertes Symbol mit Name':   'road_station',
    'isoliertes Symbol ohne Name':  'road_station',
    'Symbol ohne Name':             'road_station',
}

VIGNETTE_TYPE_MAP = {
    'A Doppelturm':      'city',
    'B Haus':            'road_station',
    'C Gehöft':          'road_station',
    'D Halle':           'spa',
    'E Stadt mit Mauer': 'city',
    'F Großvignette':    'major_city',
    'G Sondervignette':  'temple',
}

def ulm_type(entry):
    vig = entry.get('vignette', '')
    if vig in VIGNETTE_TYPE_MAP:
        return VIGNETTE_TYPE_MAP[vig]
    return TYPUS_MAP.get(entry.get('typus', ''), 'road_station')

# ── Helpers ───────────────────────────────────────────────────────────────────

def tabula_location(seg, row, col):
    if seg is not None and row and col is not None:
        return f"Seg {seg} {row}{col}"
    if seg is not None:
        return f"Seg {seg}"
    return ''

def first_pq_cell(pq_raw):
    """Return (ulm_seg, row, col) from the first planquadrat cell, or (None,None,None)."""
    m = re.search(r'(\d+)([A-Ca-c])(\d+)', pq_raw or '')
    if m:
        return int(m.group(1)), m.group(2).lower(), int(m.group(3))
    return None, None, None

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    db_data  = json.loads(DB_PATH.read_text(encoding='utf-8'))
    ulm_data = json.loads(ULM_PATH.read_text(encoding='utf-8'))
    m_data   = json.loads(MATCHES_PATH.read_text(encoding='utf-8'))

    records  = db_data['records']
    ulm_idx  = {e['ulm_id']: e for e in ulm_data['entries']}
    matches  = m_data['matches']

    db_by_id = {r['record_id']: r for r in records}

    stats = {
        'enriched':       0,
        'ulm_id_fixed':   0,
        'modern_updated': 0,
        'latin_updated':  0,
        'vignette_set':   0,
        'new_records':    0,
    }

    # ── 1. Enrich high / medium matches ──────────────────────────────────────

    for m in matches:
        if m['confidence_label'] not in ('high', 'medium'):
            continue
        db_rid = m.get('db_record_id')
        if not db_rid or db_rid not in db_by_id:
            continue

        rec = db_by_id[db_rid]
        uid = m['ulm_id']
        ulm = ulm_idx.get(uid, {})
        changed = False

        # Always write the correct ulm_id
        if rec.get('ulm_id') != uid:
            rec['ulm_id'] = uid
            stats['ulm_id_fixed'] += 1
            changed = True

        # Modern: overwrite if ULM has a value
        ulm_modern = (ulm.get('modern') or '').strip()
        if ulm_modern and rec.get('modern_preferred') != ulm_modern:
            rec['modern_preferred'] = ulm_modern
            stats['modern_updated'] += 1
            changed = True

        # Latin: overwrite when normalised forms differ
        ulm_latin = (ulm.get('latin') or '').strip()
        db_latin  = (rec.get('latin') or '').strip()
        if ulm_latin and norm_latin(ulm_latin) != norm_latin(db_latin):
            rec['latin'] = ulm_latin
            ulm_latin_tp = (ulm.get('latin_tp') or '').strip()
            if ulm_latin_tp:
                rec['latin_std'] = ulm_latin_tp
            stats['latin_updated'] += 1
            changed = True

        # Vignette
        ulm_vig = (ulm.get('vignette') or '').strip()
        if ulm_vig and rec.get('vignette') != ulm_vig:
            rec['vignette'] = ulm_vig
            stats['vignette_set'] += 1
            changed = True

        # Image URL — always write the exact URL from ULM DB so calibrate can use it directly
        ulm_img = (ulm.get('img_url') or '').strip()
        if ulm_img and rec.get('ulm_img_url') != ulm_img:
            rec['ulm_img_url'] = ulm_img
            changed = True
        elif not ulm_img and 'ulm_img_url' in rec:
            del rec['ulm_img_url']

        if changed:
            stats['enriched'] += 1

    # ── 2. Add low matches as new DB records ─────────────────────────────────

    existing_ulm_ids = {r.get('ulm_id') for r in records}

    for m in matches:
        if m['confidence_label'] != 'low':
            continue
        uid = m['ulm_id']
        if uid in existing_ulm_ids:
            continue

        ulm = ulm_idx.get(uid, {})
        if not ulm:
            continue

        pq = ulm.get('planquadrat', '') or ''
        ulm_seg, ulm_row, ulm_col = first_pq_cell(pq)
        # Fall back to pre-parsed fields
        if ulm_seg is None:
            ulm_seg = ulm.get('ulm_segment')
            ulm_row = ulm.get('ulm_row')
            ulm_col = ulm.get('ulm_col')

        db_seg  = (ulm_seg + 1) if ulm_seg is not None else None
        tab_loc = tabula_location(db_seg, ulm_row, ulm_col)

        ulm_latin  = (ulm.get('latin') or '').strip()
        ulm_lat_tp = (ulm.get('latin_tp') or '').strip()
        ulm_modern = (ulm.get('modern') or '').strip()
        ulm_vig    = (ulm.get('vignette') or '').strip()
        ulm_img    = (ulm.get('img_url') or '').strip()

        new_rec = {
            'record_id':        f'ULM:{uid}',
            'source':           'ulm',
            'data_id':          uid,
            'latin':            ulm_latin,
            'latin_std':        ulm_lat_tp or ulm_latin,
            'modern_preferred': ulm_modern,
            'type':             ulm_type(ulm),
            'ulm_id':           uid,
            'tabula_segment':   db_seg,
            'tabula_row':       ulm_row,
            'tabula_col':       ulm_col,
            'grid_row':         ulm_row,
            'grid_col':         ulm_col,
            'tabula_location':  tab_loc,
            'match_status':     'ulm_only',
        }
        if ulm_vig:
            new_rec['vignette'] = ulm_vig
        if ulm_img:
            new_rec['ulm_img_url'] = ulm_img

        records.append(new_rec)
        existing_ulm_ids.add(uid)
        stats['new_records'] += 1

    # ── 3. Backfill ulm_img_url for any record with ulm_id not yet covered ──────
    img_backfilled = 0
    for rec in records:
        uid = rec.get('ulm_id')
        if not uid:
            continue
        ulm = ulm_idx.get(uid, {})
        ulm_img = (ulm.get('img_url') or '').strip()
        if ulm_img and rec.get('ulm_img_url') != ulm_img:
            rec['ulm_img_url'] = ulm_img
            img_backfilled += 1
        elif not ulm_img and 'ulm_img_url' in rec:
            del rec['ulm_img_url']

    # ── Report & write ────────────────────────────────────────────────────────

    print(f"Enriched records:     {stats['enriched']}")
    print(f"  img_url backfilled: {img_backfilled}")
    print(f"  ulm_id corrected:   {stats['ulm_id_fixed']}")
    print(f"  modern updated:     {stats['modern_updated']}")
    print(f"  latin updated:      {stats['latin_updated']}")
    print(f"  vignette set:       {stats['vignette_set']}")
    print(f"New ULM records:      {stats['new_records']}")
    print(f"Total records now:    {len(records)}")

    tmp = DB_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(db_data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(DB_PATH)
    print(f"Written → {DB_PATH.name}")


if __name__ == '__main__':
    main()
