#!/usr/bin/env python3
"""Fix duplicate data_ids and fill missing ulm_img_url in review_places_db.json."""

import json, sys, io, os
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RDB  = os.path.join(BASE, "public", "data", "review_places_db.json")

with open(RDB, 'r', encoding='utf-8') as f:
    rraw = json.load(f)

db = rraw['records']

# ── Build data_id collision map ───────────────────────────────────────────────
did_map = defaultdict(list)
for p in db:
    did = p.get('data_id')
    if did is not None:
        did_map[did].append(p)

colliding_dids = {k for k, v in did_map.items() if len(v) > 1}
print(f"data_ids with >1 record: {len(colliding_dids)}")

# ── Fix 1: Re-assign colliding ulm_only data_ids ─────────────────────────────
reassigned = 0
for p in db:
    if p.get('match_status') != 'ulm_only':
        continue
    did = p.get('data_id')
    if did not in colliding_dids:
        continue
    uid = p.get('ulm_id')
    if not uid:
        print(f"  WARN: ulm_only record data_id={did} has no ulm_id, skipping")
        continue
    new_did = 3_000_000 + uid
    p['data_id'] = new_did
    # Update record_id to reflect new data_id namespace
    old_rid = p.get('record_id', '')
    if old_rid.startswith('ULM:'):
        p['record_id'] = f"ULM:3{uid:07d}"
    reassigned += 1
    print(f"  {p.get('latin', '')[:40]:40s}  data_id {did} → {new_did}")

print(f"\nReassigned: {reassigned} ulm_only records")

# ── Verify: no duplicates remain ─────────────────────────────────────────────
did_map2 = defaultdict(list)
for p in db:
    did = p.get('data_id')
    if did is not None:
        did_map2[did].append(p)
remaining_dups = {k: v for k, v in did_map2.items() if len(v) > 1}
if remaining_dups:
    print(f"\nWARN: {len(remaining_dups)} duplicate data_ids still remain:")
    for did, recs in list(remaining_dups.items())[:10]:
        print(f"  data_id={did}: {[(r.get('source'), r.get('latin','')[:30]) for r in recs]}")
else:
    print("✓ No duplicate data_ids remain")

# ── Fix 2: Fill missing ulm_img_url ──────────────────────────────────────────
filled = 0
for p in db:
    uid = p.get('ulm_id')
    if not uid:
        continue
    if p.get('ulm_img_url'):
        continue
    p['ulm_img_url'] = f"https://tp-online.ku.de/insetimages/TPPlace{uid}insetneu.png"
    filled += 1

print(f"\nFilled ulm_img_url for {filled} records")

# ── Write back ────────────────────────────────────────────────────────────────
rraw['records'] = db
tmp = RDB + ".tmp"
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(rraw, f, ensure_ascii=False, indent=2)
os.replace(tmp, RDB)
print(f"\nWrote {RDB}")
