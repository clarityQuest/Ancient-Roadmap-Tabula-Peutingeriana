#!/usr/bin/env python3
"""
Remove duplicate records flagged as 'certain' or 'very_likely' from review_places_db.json.

Reads public/data/duplicate_report.json, collects the 'remove' record_ids
from groups with confidence in {certain, very_likely}, then deletes those
records from review_places_db.json and writes the file back atomically.

Run: python scripts/apply_duplicates.py
"""
import sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH     = Path(__file__).parent.parent / "public" / "data" / "review_places_db.json"
REPORT_PATH = Path(__file__).parent.parent / "public" / "data" / "duplicate_report.json"

APPLY_TIERS = {'certain', 'very_likely'}


def main():
    db_data = json.loads(DB_PATH.read_text(encoding='utf-8'))
    report  = json.loads(REPORT_PATH.read_text(encoding='utf-8'))

    to_remove = set()
    for group in report['groups']:
        if group['confidence'] not in APPLY_TIERS:
            continue
        for rid in group['remove']:
            to_remove.add(rid)

    print(f"Groups to apply: {sum(1 for g in report['groups'] if g['confidence'] in APPLY_TIERS)}")
    print(f"Records to remove: {len(to_remove)}")

    before = len(db_data['records'])
    db_data['records'] = [r for r in db_data['records']
                          if r['record_id'] not in to_remove]
    after = len(db_data['records'])
    actually_removed = before - after

    # Warn about any IDs not found in DB
    found_ids = {r['record_id'] for r in db_data['records']}
    missing = to_remove - {r['record_id'] for orig in [json.loads(DB_PATH.read_text(encoding='utf-8'))['records']]
                           for r in orig}
    # Simpler: just check before vs after
    if actually_removed != len(to_remove):
        not_found = len(to_remove) - actually_removed
        print(f"Warning: {not_found} record_id(s) in 'remove' list were not found in DB")

    print(f"Records before: {before}")
    print(f"Records after:  {after}")
    print(f"Removed:        {actually_removed}")

    tmp = DB_PATH.with_suffix('.tmp')
    tmp.write_text(json.dumps(db_data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(DB_PATH)
    print(f"Written → {DB_PATH.name}")

    # Print what was removed for review
    print("\nRemoved record_ids:")
    for rid in sorted(to_remove):
        print(f"  {rid}")


if __name__ == '__main__':
    main()
