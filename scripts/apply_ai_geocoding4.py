"""
Fourth batch of AI geocoding for review_places_db.json.
Session 2026-06-12 — covers Turkey seg 9-11 (remaining), Italy seg 4-7,
Greece seg 7-8, Tunisia, Libya, Algeria, Syria, Egypt, Iran, and misc countries.

Confidence conventions:
  gc=3: confirmed identification (named modern place, multiple sources)
  gc=2: interpolated from known neighbors or strong Miller/Barrington hint
  gc=1: rough area estimate only
"""
import json, sys, io, shutil, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

DB_PATH = "public/data/review_places_db.json"
DRY_RUN = "--dry-run" in sys.argv

# fmt: data_id -> (lat, lng, geocoding_confidence, wiki_url, note)
FINDS = {

    # ── Turkey seg 8-9 (Black Sea coast and NW Anatolia) ────────────────────
    # 1970 Bvatico: hints "Brodolovo? Urdovica? Ahtopol?" — Black Sea coast near BG/TR border
    1970: (41.88, 27.97, 1, None, "Black Sea coast near Bulgarian-Turkish border, Turkey"),
    # 2101 Tycae: "? Bürnük ?" near Kastamonu, N Turkey
    2101: (41.40, 33.75, 1, None, "Bürnük / Kastamonu province, Turkey"),
    # 2103 Mileto: "? Kabalı bei Sinop ?" — near Sinop on Black Sea
    2103: (42.00, 35.25, 1, None, "near Sinop (Kabalı area), Black Sea coast, Turkey"),
    # 2111 Lateas: "beim Sapanca Gölü" — Sapanca Lake, NW Turkey, on Bithynia road
    2111: (40.68, 30.27, 2, None, "Sapanca Lake area, NW Turkey (between Nicomedia and Bithynium)"),
    # 2112 Demetriv: "in der Gegend von Hendek" — Hendek, Sakarya province
    2112: (40.80, 30.75, 2, None, "Hendek, Sakarya province, NW Turkey"),
    # 2120 Otresa: "??? bei Tosya ?" — Tosya, Kastamonu
    2120: (41.02, 34.03, 2, None, "Tosya, Kastamonu province, N Turkey"),
    # 2140 Acitoriziaco: "? bei Elecik oder Kalecik ?" — Kalecik, Ankara province
    2140: (40.10, 33.42, 2, None, "Kalecik, Ankara province, Turkey (on Ankara–Amasya route)"),
    # 2158 Abrostola (1): "? Veletler am Fluss Sakya ?" — Sakarya river area NW Turkey
    2158: (40.77, 30.55, 2, None, "Sakarya (Sakya) river area near Adapazarı, NW Turkey"),
    # 2169 Ivllae: "? Çay/Tshai ?" — Çay, Afyonkarahisar province
    2169: (38.60, 31.02, 2, None, "Çay, Afyonkarahisar province, Turkey"),
    # 2171 Asynnade: "? Kınık, 3 km nördl. von Tatarlı ?" — near Sandıklı, Afyonkarahisar
    2171: (38.50, 30.25, 2, None, "Kınık (~3 km N Tatarlı), near Sandıklı, Afyonkarahisar, Turkey"),

    # ── Turkey seg 10 (Cappadocia and Taurus routes) ────────────────────────
    # 2250 Tonea: "Boğazkale ?" — ancient Hattusa site, Çorum province
    2250: (40.02, 34.62, 2, None, "Boğazkale (ancient Hattusa), Çorum province, Turkey"),
    # 2260 Aegonne: "??? Sorgun ???" — Sorgun, Yozgat province
    2260: (39.81, 35.18, 2, None, "Sorgun, Yozgat province, central Turkey"),
    # 2296 Tracias: "? Kinikören / Kınık Höyük" — archaeological site near Niğde
    2296: (37.99, 34.52, 2, None, "Kınık Höyük (archaeological site), Niğde area, Turkey"),
    # 2308 Asarino: "? bei Keklikoluk, Göksün ?" — near Göksun, Kahramanmaraş
    2308: (38.04, 36.52, 2, None, "Keklikoluk area near Göksun, Kahramanmaraş, Turkey"),
    # 2309 Castabola: "? Kanlıkavak bei Göksun ?" — near Göksun
    2309: (38.05, 36.55, 2, None, "Kanlıkavak near Göksun, Kahramanmaraş, Turkey"),
    # 2311 Arcilapopoli: "Ruinen von Karaelbistan ?" — near Elbistan
    2311: (38.20, 37.20, 1, None, "Karaelbistan ruins area, near Elbistan, Kahramanmaraş, Turkey"),
    # 2312 Catara: "??? Bozhüyük, Göksun/Kahramanmaraş ???" — near Göksun
    2312: (38.10, 36.60, 1, None, "Bozhüyük area near Göksun, Kahramanmaraş, Turkey"),
    # 2337 In monte tavro: "??? Namrun Kalesi / Çamlıyayla?" — Taurus mountain pass
    2337: (37.10, 34.58, 2, None, "Çamlıyayla (Namrun), Taurus Mountains, Mersin, Turkey"),
    # 2355 Temissonio: "wahrscheinl. Karahüyük in der Ebene von Acıpayam" — Acıpayam, Denizli
    2355: (37.43, 29.36, 2, None, "Karahüyük in the plain of Acıpayam, Denizli province, Turkey"),

    # ── Turkey seg 11 (Eastern Anatolia) ────────────────────────────────────
    # 2519 Cvnissa: "irgendwo westl. von Satala" — W of Satala (Sadak, Gümüşhane)
    2519: (39.80, 38.50, 1, None, "west of Satala, eastern Turkey (Erzincan/Sivas area)"),
    # 2529 Hispa: "? Kangal ?" — Kangal, Sivas province
    2529: (39.00, 37.38, 2, None, "Kangal, Sivas province, eastern Turkey"),
    # 2545 Singa: "??? Sevdilli Hanı, Elbistan" — near Elbistan, Kahramanmaraş
    2545: (38.20, 37.30, 2, None, "Sevdilli Hanı area near Elbistan, Kahramanmaraş, Turkey"),
    # 2547 Nocotesso: "südwestl. v. Melitene/Eski Malatya" — SW of Malatya
    2547: (38.20, 38.15, 2, None, "SW of Melitene (Eski Malatya), Malatya province, Turkey"),
    # 2552 Glavdia: "? Tillo oder Kerar Kale ?" — Tillo near Siirt, SE Turkey
    2552: (37.74, 41.74, 1, None, "Tillo (Aydınlar) area near Siirt, SE Turkey"),

    # ── Italy (seg 4 — Tuscany / Etruria roads) ─────────────────────────────
    # 1060 Qvadrata: "St. Colombano südl. von Graffignano" — S of Graffignano, Lazio
    1060: (42.53, 12.09, 2, None, "S of Graffignano (St. Colombano area), Lazio, Italy"),
    # 1093 Ad Aqvileia: "Mugnana? (Greve in Chianti) / bei Figline Valdarno"
    1093: (43.57, 11.28, 2, None, "Mugnana di Greve (Greve in Chianti), Tuscany, Italy"),
    # 1097 Ad Ioglandem: "Ciggiano" — hamlet near Monte San Savino, Arezzo
    1097: (43.34, 11.72, 2, None, "Ciggiano (Monte San Savino), Arezzo province, Tuscany, Italy"),
    # 1099 Ad Grecos: "Sinalunga / Bettolle" — between Florence and Chiusi
    1099: (43.20, 11.79, 2, None, "Sinalunga/Bettolle area on Via Cassia, Siena province, Italy"),
    # 1102 Piscinas: "nördlich von Marmigliaio" — near Piansano, Lazio
    1102: (42.54, 11.60, 1, None, "N of Marmigliaio area, near Piansano, Lazio, Italy"),
    # 1110 Ad sextum: "between Populonium and Saena" — Via Aurelia/Cassia, Grosseto area
    1110: (42.95, 11.10, 1, None, "road station between Populonia and Siena, Grosseto area, Italy"),
    # 1158 Ad Pirum Filumeni: "am Flusse Cesano, östlich von Mondolfo" — Via Flaminia, Marche
    1158: (43.66, 12.90, 2, None, "Via Flaminia crossing of Cesano river E of Mondolfo, Marche, Italy"),
    # 1160 Sestias: "Charavalle, östlich von Iesi" — Chiaravalle, Marche
    1160: (43.60, 13.33, 3, "https://it.wikipedia.org/wiki/Chiaravalle_(AN)", "Chiaravalle (Charavalle), Ancona province, Marche, Italy"),
    # 1205 Aeqvo Falsico: "on Via Flaminia near Falerii" — near Civita Castellana
    1205: (42.29, 12.40, 2, None, "Via Flaminia near Falerii Novi (Civita Castellana area), Lazio, Italy"),
    # 1213 Ad Tine Recine: "Via Flaminia between Tres Tabernae and Fanum Fugitivi"
    1213: (42.90, 12.70, 1, None, "Via Flaminia between Tres Tabernae and Fanum Fugitivi, Umbria, Italy"),
    # 1238 Ad novas: "Ponte delle Carozze / Tolfa" — Tolfa, Lazio
    1238: (42.15, 11.93, 2, None, "Tolfa area (Ponte delle Carozze), Lazio, Italy"),
    # 1325 Melfel: "am Melfa-Fluss" — Melfa valley, Lazio/Campania border
    1325: (41.56, 13.83, 2, None, "Melfa river (Melfel), Via Latina, Lazio/Campania border, Italy"),
    # 1486 Temsa: "Sant'Eufemia Vetere" — Sant'Eufemia d'Aspromonte, Calabria
    1486: (38.27, 15.80, 3, "https://it.wikipedia.org/wiki/Sant%27Eufemia_d%27Aspromonte", "Sant'Eufemia d'Aspromonte (Temsa/Teuranum), Reggio Calabria, Italy"),

    # ── Greece (seg 7-8) ─────────────────────────────────────────────────────
    # 1868 Sabativm: "nördlich von Platamona/Polykastro" — N of Polykastro, Macedonia
    1868: (41.08, 22.62, 2, None, "N of Polykastro (Platamona area), Central Macedonia, Greece"),
    # 1913 Melena: "Arcadia: city NW Megalopolis" — NW of Megalopolis, Peloponnese
    1913: (37.48, 21.98, 2, None, "NW of Megalopolis, Arcadia, Peloponnese, Greece"),
    # 2031 Hatera: "bei Katerini ?" — Katerini, Pieria, Macedonia
    2031: (40.27, 22.50, 2, None, "near Katerini, Pieria, Central Macedonia, Greece"),
    # 2032 Anamo: "? bei Louloudies" — Louloudies village, Pieria
    2032: (40.25, 22.36, 2, None, "Louloudies/Louloudes area, Pieria, Central Macedonia, Greece"),
    # 2043 [ - ? - ]o[ - ? - ]: "3 km östl. von Nea Karvali" — near Kavala
    2043: (40.95, 24.08, 2, None, "3 km E of Nea Karvali, Kavala prefecture, Greece"),
    # 2053 Sarxa: "Sárres" — Serres, Central Macedonia
    2053: (41.09, 23.55, 3, "https://en.wikipedia.org/wiki/Serres", "Serres (Σέρρες/Sárres), Central Macedonia, Greece"),
    # 2058 Trinlo: "bei Aidonochori/Αηδονοχώρι" — near Kavala
    2058: (40.97, 24.32, 2, None, "Aidonochori (Αηδονοχώρι), near Kavala, Eastern Macedonia, Greece"),

    # ── Tunisia (seg 5-7) ─────────────────────────────────────────────────────
    # 190 Seggo: "between Uzappa and Zama Regia" — central Tunisia
    190:  (36.00, 9.20, 1, None, "between Uzappa and Zama Regia, central Tunisia"),
    # 191 Avvla: "Kasrel Hadid oder Hr. el Chima" — near Maktar, central Tunisia
    191:  (35.87, 9.22, 1, None, "Kasrel Hadid / Hr. el Chima area near Maktar, central Tunisia"),
    # 192 Avtipsidam: "Kebēr el Gut / between Zama Regia and Uzappa" — central Tunisia
    192:  (36.00, 9.30, 1, None, "Kebēr el Gut area, between Zama Regia and Uzappa, Tunisia"),
    # 235 Agarsel: "el Douz" — El Douz, Kebili governorate
    235:  (33.46, 9.02, 2, None, "El Douz (ancient Agarsel?), Kebili governorate, southern Tunisia"),
    # 237 Mazatanzvr: "S Djebel Tebaga" — south of Tebaga ridge
    237:  (33.35, 9.58, 1, None, "S of Djebel Tebaga, southern Tunisia"),
    # 238 Tinzvnedo: "S Djebel Tebaga" — south of Tebaga ridge
    238:  (33.40, 9.52, 1, None, "S of Djebel Tebaga, southern Tunisia"),
    # 269 Presidio Silvani: "36 miles N Gabes on coast" — La Skhira area
    269:  (34.37, 10.41, 2, None, "36 Roman miles N of Gabes on coast (La Skhira/Sidi Bouzid area), Tunisia"),
    # 270 Lacene: "bei La Skirra" — La Skhira, Gulf of Gabes
    270:  (34.30, 10.09, 3, None, "La Skhira (La Skirra), Gulf of Gabes, Sfax governorate, Tunisia"),

    # ── Libya / Tripolitania (seg 6-9) ─────────────────────────────────────
    # 296 Flacci Taberna: "SE of Oea (Tripoli)" — SE Tripoli
    296:  (32.75, 13.35, 1, None, "SE of Oea (Tripoli), Tripolitania, Libya"),
    # 312 Chosol: "Bu Njem? (Barrington)" — Bu Njem fort, Fezzan
    312:  (29.54, 15.41, 2, None, "Bu Njem (Gholaia), Roman fort, Fezzan, Libya"),
    # 313 Mvsvla: "S side of Sebkha Tauorgha" — near Tauorgha, NW Libya
    313:  (31.90, 15.15, 1, None, "S side of Sebkha Tauorgha, Tripolitania, Libya"),
    # 356 Nemeseo: "between Catabathmus Maior and Antipyrgos" — Libya/Egypt border coast
    356:  (31.90, 24.50, 1, None, "between Catabathmus Maior (Sollum) and Antipyrgos (Bardia), Libya coast"),

    # ── Algeria (seg 2-4) ─────────────────────────────────────────────────────
    # 38 Nedibvs: "SE Rusicade / Bu Maiza am Ostende des See Fetzara"
    38:   (36.75, 7.10, 2, None, "Bu Maiza at E end of Lake Fetzara, SE of Rusicade (Skikda), Algeria"),
    # 40 Ad plvmbaria: "SW Hippo Regius (Annaba)"
    40:   (36.80, 7.60, 2, None, "SW of Hippo Regius (Annaba), Algeria"),
    # 41 Ad villam Sele: "between Cirta (Constantine) and Rusicade (Skikda)"
    41:   (36.55, 7.00, 2, None, "between Cirta (Constantine) and Rusicade (Skikda), Algeria"),
    # 98 Capvt Bvdelli: "7 miles E Cuicul (Djemila)"
    98:   (36.33, 5.90, 2, None, "7 Roman miles E of Cuicul (Djemila), Algeria"),
    # 99 Modolana: "between Milev (Mila) and Cuicul (Djemila)"
    99:   (36.40, 6.00, 2, None, "between Milev (Mila) and Cuicul (Djemila), Algeria"),
    # 100 Berzeo: "between Milev and Cuicul / Fedj Mzala"
    100:  (36.42, 6.10, 2, None, "between Milev (Mila) and Cuicul (Djemila), Fedj Mzala area, Algeria"),
    # 110 Capraria: "Hr. Bu Atfân / near Hippo Regius"
    110:  (36.85, 7.70, 2, None, "Hr. Bu Atfân near Hippo Regius (Annaba), Algeria"),
    # 165 Adlali: "between Diana Veteranorum and Theveste"
    165:  (35.65, 6.80, 1, None, "between Diana Veteranorum (Aïn Zana) and Theveste (Tébessa), Algeria"),
    # 172 Popleto: "9 miles E Thamugadi (Timgad)"
    172:  (35.50, 6.68, 2, None, "9 Roman miles E of Thamugadi (Timgad), Algeria"),
    # 173 Liviana: "13 miles E Thamugadi"
    173:  (35.50, 6.80, 2, None, "13 Roman miles E of Thamugadi (Timgad), Algeria"),
    # 174 Zyrnas maseli: "45 miles E Thamugadi / Ksar el Hamar"
    174:  (35.50, 7.80, 2, None, "45 Roman miles E of Thamugadi (Ksar el Hamar area), Algeria"),
    # 176 Ad germani: "near Thubursicum Numidarium (Khamissa)"
    176:  (36.23, 7.66, 2, None, "near Thubursicum Numidarium (Khamissa), Souk Ahras province, Algeria"),
    # 3512 Baccarvs: "between Sitifis and Sigus"
    3512: (36.15, 5.75, 2, None, "between Sitifis (Sétif) and Sigus, Sétif province, Algeria"),
    # 3513 Ad Stvrnos: "between Sitifis and Sigus / H. Ksaria"
    3513: (36.12, 5.65, 2, None, "between Sitifis (Sétif) and Sigus (H. Ksaria area), Algeria"),
    # 3516 Lvcvllianis: "26 miles W Sigus"
    3516: (36.12, 5.47, 2, None, "26 Roman miles W of Sigus, near Sétif, Algeria"),
    # 3518 Bvdvxi: "5 miles W Sigus"
    3518: (36.10, 6.02, 2, None, "5 Roman miles W of Sigus, Algeria"),
    # 3522 Ad Centenarium: "between Tigisis (Ain Tounga) and Gadiaufala"
    3522: (36.35, 8.58, 2, None, "between Tigisis (Ain Tounga) and Gadiaufala (Ksar Sbahi), Algeria/Tunisia border"),
    # 3526 Fonte Potamiano: "near Gadiaufala (Ksar Sbahi)"
    3526: (36.10, 8.45, 2, None, "near Gadiaufala (Ksar Sbahi), NE Algeria"),
    # 3527 Magri: "near Gadiaufala"
    3527: (36.12, 8.43, 2, None, "near Gadiaufala (Ksar Sbahi), NE Algeria"),
    # 3528 Rvstici: "SE Gadiaufala"
    3528: (36.05, 8.52, 2, None, "SE of Gadiaufala (Ksar Sbahi), NE Algeria"),

    # ── Syria (seg 10-11) ────────────────────────────────────────────────────
    # 507 Demetri: "S Raphaneai (Barrington)" — S of Raphaneai (Rafniye/Arafa)
    507:  (35.15, 36.85, 2, None, "S of Raphaneai (Rafniye/Arafa), Hama governorate, Syria"),

    # ── Egypt (seg 9) ────────────────────────────────────────────────────────
    # 358 Aratv: "between Paraetonium and Catabathmus" — N African coastal road
    358:  (31.50, 26.15, 1, None, "between Paraetonium (Marsa Matruh) and Catabathmus, N Africa coast"),
    # 362 Philiscv: "between Paraetonium and Caportis"
    362:  (31.40, 26.90, 1, None, "between Paraetonium (Marsa Matruh) and Caportis, Libya/Egypt border area"),
    # 417 Tasdri: "Atfih (Miller) / Memphites Nomos" — Atfih on the Nile, Egypt
    417:  (29.42, 31.26, 2, None, "Atfih, Memphites Nomos, Nile, Egypt"),

    # ── Iran (seg 11-12) ─────────────────────────────────────────────────────
    # 2704 Rvtarata: "Ruinen in Kasri Chirin und Hauch-Kerck oder Chankin"
    2704: (34.43, 45.48, 2, None, "Qasr-i Shirin / Khanaqin area, Kermanshah province, Iran"),
    # 2748 Sevavicina: "Sewah (Miller)" — Saveh (Sāveh), Tehran province
    2748: (35.02, 50.36, 2, None, "Saveh (Sāveh/Sewah), Tehran province, Iran"),
    # 2749 Thermantica: "Ardistan (Miller)" — Ardestan, Isfahan province
    2749: (33.38, 52.37, 2, None, "Ardestan (Ardistan), Isfahan province, Iran"),
    # 2776 Nisaci: "Abadah (Miller)" — Abadeh, Fars province
    2776: (31.16, 52.67, 2, None, "Abadeh (Abadah), Fars province, Iran"),

    # ── Various other countries ──────────────────────────────────────────────
    # 1969 Thera [BG]: "? Ahtopol ?" — Ahtopol, Bulgarian Black Sea coast
    1969: (42.10, 27.94, 2, None, "Ahtopol area, Southern Black Sea coast, Bulgaria"),
    # 1599 Bolentio [HR]: "area of Moslavina" — Moslavina region, central Croatia
    1599: (45.50, 16.80, 1, None, "Moslavina region (near Kutina/Sisak), Croatia"),
    # 1514 Elegio [A]: "Bei Strengberg, near Adiuvense (Wallsee), Austria"
    1514: (48.12, 14.68, 3, "https://de.wikipedia.org/wiki/Strengberg", "Strengberg (near Adiuvense/Wallsee), Lower Austria"),
    # 1823 Praesidium [MK]: "17 m.p. SE Scupi (Skopje)" — 25 km SE of Skopje
    1823: (41.87, 21.58, 2, None, "17 Roman miles SE of Scupi (Skopje), North Macedonia"),
    # 481 Rhose [JOR]: "near Bostra (Barrington)" — near Bosra, S Syria/N Jordan border
    481:  (32.45, 36.50, 2, None, "near Bostra (Bosra), Hauran region, Syria/Jordan border"),
    # 1647 Confluentibus [YU]: "Beograd Novi?" — Belgrade (Sava-Danube confluence)
    1647: (44.82, 20.46, 2, None, "Belgrade area (Confluentes = Sava-Danube confluence), Serbia"),
    # 1963 Stratonis [RO]: "between Tomis (Constanța) and Callatis (Mangalia)"
    1963: (44.00, 28.60, 2, None, "between Tomis (Constanța) and Callatis (Mangalia), Black Sea coast, Romania"),
}

# ─────────────────────────────────────────────────────────────────────────────

def main():
    db_text = open(DB_PATH, encoding="utf-8").read()
    db = json.loads(db_text)
    records = db["records"]
    id_map = {r["data_id"]: r for r in records}

    updated = 0
    skipped = 0
    for data_id, (lat, lng, gc, wiki, note) in sorted(FINDS.items()):
        r = id_map.get(data_id)
        if r is None:
            print(f"  MISS: {data_id} not found in DB")
            continue
        if r.get("lat") is not None and r.get("lng") is not None:
            print(f"  SKIP: {data_id:5d}  {r.get('latin',''):32s} already located")
            skipped += 1
            continue
        latin = r.get("latin") or r.get("latin_std") or ""
        print(f"  SET:  {data_id:5d}  {latin:32s} -> {lat},{lng}  gc={gc}  [{note}]")
        if not DRY_RUN:
            r["lat"] = lat
            r["lng"] = lng
            r["geocoding_confidence"] = gc
            if wiki:
                r["wiki_url"] = wiki
                r["wiki_confidence"] = 3
        updated += 1

    print(f"\nTotal: {updated} records to update, {skipped} skipped (already located)")
    if DRY_RUN:
        print("Dry run — no changes written.")
        return

    backup = DB_PATH.replace(".json", f"_backup_{datetime.date.today()}_pre_ai4.json")
    import shutil
    shutil.copy(DB_PATH, backup)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"DB written. Backup: {backup}")


if __name__ == "__main__":
    main()
