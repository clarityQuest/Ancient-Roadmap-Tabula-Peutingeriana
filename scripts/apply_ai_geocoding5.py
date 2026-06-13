"""
Apply AI-researched geocoding for batch 5: 26 unlocated road stations.
Methods: pixel interpolation between located neighbors, modern hints from
Miller (1916), Barrington Atlas, and OmnesViae modern_omnesviae fields.
gc=3: confirmed; gc=2: strong candidate; gc=1: rough area estimate.
"""
import json
import shutil
from datetime import datetime

DB_PATH = "public/data/review_places_db.json"
BACKUP_PATH = f"public/data/review_places_db_backup_{datetime.now().strftime('%Y-%m-%d')}_pre_geocode5.json"

# data_id -> {lat, lng, gc, note}
FINDS = {
    # ── ITALY ──────────────────────────────────────────────────────────────
    # Tinna [Flumen] = River Tenna (ancient Tinna/Tinnia), Marche region.
    # Flows into the Adriatic at Porto San Giorgio. Well-established identification.
    1180: {"lat": 43.183, "lng": 13.789, "gc": 3,
           "note": "Fl. Tinna = River Tenna; mouth near Porto San Giorgio, Marche, Italy"},

    # ── TURKEY ─────────────────────────────────────────────────────────────
    # Aspasi: Galatia province. Pixel (mpx=32309) between Acitoriziaco
    # (40.10,33.42) and Bagrvm (39.03,32.05); mpy=1306 ≈ Aspona latitude.
    # Likely W Galatia near Sivrihisar/Polatlı area.
    2146: {"lat": 39.55, "lng": 32.20, "gc": 2,
           "note": "Galatia; pixel between Acitoriziaco (40.10,33.42) and Bagrvm (39.03,32.05); W Galatia area"},

    # Garmias: Cappadocia province. Pixel closest to Egdava (38.62,32.55);
    # mpy=1311 slightly N of Egdava (mpy=1394). Kırşehir/Nevşehir area.
    2148: {"lat": 39.25, "lng": 32.65, "gc": 2,
           "note": "Cappadocia; pixel nearest Egdava (38.62,32.55); slightly N; Kırşehir region"},

    # Doganis: Cappadocia. Between Comassa (39.85,37.40 mpx=36141) and
    # Megalasso (40.20,37.98 mpx=36454). Miller suggests Devekse/Ekinli or Demiryurt.
    2292: {"lat": 40.00, "lng": 37.66, "gc": 2,
           "note": "Cappadocia; pixel between Comassa (39.85,37.40) and Megalasso (40.20,37.98); Miller: Devekse/Ekinli"},

    # Ad vicvm: Asia province. Generic route marker between Carvra/Hierapolis
    # (37.94,28.82) and Apameia Ciboton (38.07,30.17). Afyon/Sandıklı area.
    2348: {"lat": 37.98, "lng": 29.25, "gc": 2,
           "note": "Asia province; pixel between Carvra (37.94,28.82) and Apameia Ciboton (38.07,30.17)"},

    # Caleorsissa: Cappadocia. Pixel (mpx=37205) near Oleoberda (38.50,38.50)
    # and Arianodvm (38.02,37.67). Miller suggests Babsu. Darende/Gürün area.
    2543: {"lat": 38.50, "lng": 38.45, "gc": 2,
           "note": "Cappadocia; pixel near Oleoberda (38.50,38.50); Miller: ? Babsu; Darende/Gürün area"},

    # ── GEORGIA ────────────────────────────────────────────────────────────
    # Apvlvm: Armenia/Caucasus province, country GE. Pixel (mpx=39569, mpy=811)
    # between Ad mercvrivm [GE] (41.75,42.78) and Pagas [GE] (41.99,44.10).
    # Near Borjomi/Gori, western Georgia.
    2458: {"lat": 41.88, "lng": 43.60, "gc": 2,
           "note": "Armenia/Caucasus; pixel between Ad mercvrivm GE (41.75,42.78) and Pagas GE (41.99,44.10); Gori area"},

    # ── GREECE ─────────────────────────────────────────────────────────────
    # Thapedon: Achaea province. Pixel (mpx=24499, mpy=1428) between Falera
    # (38.92,22.63) and Thermopylas (38.80,22.54). Central Greece/Boeotia.
    1871: {"lat": 38.86, "lng": 22.59, "gc": 1,
           "note": "Achaea; pixel between Falera (38.92,22.63) and Thermopylas (38.80,22.54); central Greece"},

    # Bada: Macedonia province, 'Macedonia, s. Kommentar'. Pixel (mpx=25170)
    # between Cellis (40.79,21.69) and Arvlos (40.59,22.60). Emathia area.
    2033: {"lat": 40.70, "lng": 22.10, "gc": 1,
           "note": "Macedonia; pixel between Cellis (40.79,21.69) and Arvlos (40.59,22.60); Miller: Macedonia"},

    # Consinto: Thrace province, '[near Xanthe?]'. Pixel (mpx=27310, mpy=1543)
    # between Topiro (41.08,24.77) and Porsvlis (41.14,25.33). Near Xanthi (41.13,24.89).
    2045: {"lat": 41.11, "lng": 25.02, "gc": 2,
           "note": "Thrace; pixel between Topiro (41.08,24.77) and Porsvlis (41.14,25.33); matches 'near Xanthi'"},

    # Micolito: Thrace province, '[near Drys; unlocated]'. Pixel (mpx=27818)
    # between Brenzici (41.08,25.55) and Dymis (40.89,26.17). Komotini area.
    2048: {"lat": 40.98, "lng": 25.87, "gc": 1,
           "note": "Thrace; pixel between Brenzici (41.08,25.55) and Dymis (40.89,26.17); Komotini direction"},

    # ── CROATIA ────────────────────────────────────────────────────────────
    # Lorano: Dalmatia province, 's. Kommentar'. Pixel (mpx=17672, mpy=1009)
    # at same mpx as Magno (43.80,16.32, mpy=964). Slightly S of Magno.
    1711: {"lat": 43.72, "lng": 16.33, "gc": 1,
           "note": "Dalmatia; pixel co-located with Magno (43.80,16.32); slightly S; Sinj/Duvno area"},

    # ── EGYPT ──────────────────────────────────────────────────────────────
    # Monogami: Barrington: el-Qasaba el-Garbiya? Pixel (mpx=30790, mpy=2046)
    # between Comarv (30.97,28.73) and Tapostri (30.95,29.52). W Nile Delta.
    365: {"lat": 30.97, "lng": 29.15, "gc": 2,
          "note": "Aegyptus; Barrington: el-Qasaba el-Garbiya; pixel between Comarv (30.97,28.73) and Tapostri (30.95,29.52)"},

    # Senphv: Miller: 'el Tawileh bei el Korein'. Pixel (mpx=31709, mpy=2100)
    # between Subasto (30.57,31.51) and Phacusi (30.73,31.80). E Nile Delta/canal zone.
    428: {"lat": 30.55, "lng": 31.65, "gc": 2,
          "note": "Aegyptus; Miller: el Tawileh bei el Korein; pixel between Subasto (30.57,31.51) and Phacusi (30.73,31.80)"},

    # ── ALGERIA ────────────────────────────────────────────────────────────
    # Aqvartille: Numidia. Between Cirta (Constantine, 36.36,6.61) and
    # Numituriana; Miller: 'bei Ruffac'. NE of Constantine.
    106: {"lat": 36.42, "lng": 6.90, "gc": 2,
          "note": "Numidia; between Cirta/Constantine (36.36,6.61) and Numituriana; Miller: bei Ruffac"},

    # Ad lapidem Baivm: Numidia. Barrington: between Gadiaufala (Ksar Sbahi)
    # and Thibilis (Announa, 36.43,7.08). Souk Ahras area.
    3525: {"lat": 36.18, "lng": 7.42, "gc": 2,
           "note": "Numidia; Barrington: between Gadiaufala (Ksar Sbahi) and Thibilis/Announa (36.43,7.08)"},

    # Mova: Numidia. Miller: 'Hr. Kissa (?)'. Henchir Kissa, near Timgad/Tebessa.
    3538: {"lat": 35.80, "lng": 7.85, "gc": 1,
           "note": "Numidia; Miller: Hr. Kissa (?); Henchir ruin near Timgad/Tebessa area"},

    # ── LIBYA ──────────────────────────────────────────────────────────────
    # Ad cisternas: Tripolitania coast. Miller: 'bei Karrah'. Pixel (mpx=23981)
    # between Casa Rimoniana (32.14,14.95) and Ad ficvm (31.40,15.73).
    # Coast E of Leptis Magna, near Khoms-Misrata.
    309: {"lat": 32.05, "lng": 15.08, "gc": 2,
          "note": "Tripolitania coast; Miller: bei Karrah; pixel interpolation between Casa Rimoniana (32.14,14.95) and Ad ficvm (31.40,15.73)"},

    # Naladus: Libya coast. Miller: 'bei En Nemua'. Slightly E of Ad cisternas.
    310: {"lat": 31.90, "lng": 15.22, "gc": 2,
          "note": "Libya coast E of Misrata; Miller: bei En Nemua; pixel interpolation"},

    # Dissio Aqva Amara: Libya coast ('Bitter Water Station'). Miller: 'bei Mellafah'.
    # Further E, Gulf of Sirte direction.
    311: {"lat": 31.65, "lng": 15.43, "gc": 2,
          "note": "Libya coast; Miller: bei Mellafah; pixel interpolation; E of Gulf of Sirte"},

    # ── SYRIA ──────────────────────────────────────────────────────────────
    # Bersera: Syria province. Pixel (mpx=37087, mpy=2160) near Theleda
    # (35.14,37.10) and Hierapoli-Syria (36.52,37.95). N Syrian interior.
    2436: {"lat": 35.50, "lng": 37.00, "gc": 1,
           "note": "Syria; pixel near Theleda (35.14,37.10) and Hierapoli-Syria (36.52,37.95); N Syrian interior"},

    # Bannis: Syria province. Pixel (mpx=37135, mpy=2032) slightly N of Bersera.
    2444: {"lat": 35.90, "lng": 37.20, "gc": 1,
           "note": "Syria; pixel (37135,2032) N of Bersera; Hierapoli-Syria (36.52,37.95) area"},

    # Thiltavri: Syria province. Pixel (mpx=37272, mpy=2098) between Bersera and Bannis.
    2445: {"lat": 35.65, "lng": 37.40, "gc": 1,
           "note": "Syria; pixel (37272,2098) between Bersera and Bannis in N Syrian interior"},

    # Rene: Mesopotamia province. Pixel (mpx=39890, mpy=1566) near Ressaina
    # (36.85,40.06) and Barbare (37.26,39.29). Upper Khabur/Jaghjagh area.
    2622: {"lat": 36.95, "lng": 40.40, "gc": 1,
           "note": "Mesopotamia; pixel near Ressaina/Ras al-Ayn (36.85,40.06); upper Khabur area"},

    # ── TUNISIA ────────────────────────────────────────────────────────────
    # Pvtea: Africa Proconsularis. Barrington: SE of Augemmi. Pixel (mpx=21201,
    # mpy=2338) near Pisida Municipio (33.07,11.77). SE Tunisia coastal area.
    277: {"lat": 33.10, "lng": 11.60, "gc": 2,
          "note": "Africa; Barrington: SE of Augemmi; pixel near Pisida Municipio (33.07,11.77)"},

    # ── IRAQ ───────────────────────────────────────────────────────────────
    # Abdeae: Mesopotamia. Pixel (mpx=40830, mpy=1877) between Ad pontem
    # (36.37,42.44, mpx=40820) and Adfl. Tigrim (37.33,42.20, mpx=40776).
    # NW Iraq, Sinjar/Tigris area.
    2657: {"lat": 36.70, "lng": 42.40, "gc": 1,
           "note": "Mesopotamia; pixel between Ad pontem (36.37,42.44) and Adfl. Tigrim (37.33,42.20); NW Iraq"},

    # ── ISRAEL ─────────────────────────────────────────────────────────────
    # Rasa: Arabia province. Pixel (mpx=32354, mpy=2184) near Praesidio
    # (29.68,35.24) and Haila (29.56,35.00). Wadi Arabah / Negev area.
    453: {"lat": 29.90, "lng": 35.40, "gc": 1,
          "note": "Arabia province; pixel near Praesidio (29.68,35.24) and Haila (29.56,35.00); Wadi Arabah"},
}


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)

    shutil.copy(DB_PATH, BACKUP_PATH)
    print(f"Backup: {BACKUP_PATH}")

    records = db["records"]
    by_id = {r["data_id"]: r for r in records if "data_id" in r}

    updated = 0
    for data_id, info in FINDS.items():
        r = by_id.get(data_id)
        if not r:
            print(f"  MISSING id={data_id}")
            continue
        if r.get("lat"):
            print(f"  SKIP id={data_id} {r.get('latin','')} — already has lat={r['lat']}")
            continue
        r["lat"] = info["lat"]
        r["lng"] = info["lng"]
        r["gc"] = info["gc"]
        r["geocoding_notes"] = info["note"]
        r["geocoding_status"] = "ai_batch5"
        r["geocoding_timestamp"] = datetime.utcnow().isoformat() + "+00:00"
        name = r.get("latin", "") or r.get("latin_std", "")
        country = r.get("country", "")
        print(f"  SET  id={data_id} [{country}] {name:30s} -> lat={info['lat']:.3f} lng={info['lng']:.3f} gc={info['gc']}")
        updated += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nUpdated {updated}/{len(FINDS)} records -> {DB_PATH}")


if __name__ == "__main__":
    main()
