"""
Third batch of AI+WebSearch geocoding for review_places_db.json.
Session 2026-06-09 — covers Turkey (segs 9-11), Armenia/AZ/GE, Iran (seg 12),
Algeria, Tunisia, and Italy unlocated road_stations with country codes.

Confidence conventions:
  gc=3: confirmed identification (named modern place, multiple sources)
  gc=2: interpolated between known neighbor stations, or Miller/Barrington hint
  gc=1: very rough area estimate only (ARM stations with no specific anchors)
"""
import json, sys, io, shutil, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

DB_PATH = "public/data/review_places_db.json"
DRY_RUN = "--dry-run" in sys.argv

# fmt: data_id -> (lat, lng, geocoding_confidence, wiki_url, note)
FINDS = {

    # ── Turkey seg 9 ────────────────────────────────────────────────────────
    # 2102 Cereas = Cerasus = Giresun (classical Cerasus on Black Sea coast)
    2102: (40.919, 38.389, 3, "https://en.wikipedia.org/wiki/Giresun", "Giresun/Cerasus, Turkey"),

    # ── Turkey seg 10 col1a ─────────────────────────────────────────────────
    # 2259 Rogmorum: Black Sea coast, between Helega (Bafra, 41.571°N 35.894°E)
    # and Navtagino (41.498°N, 36.117°E); Samsun area
    2259: (41.286, 36.330, 2, None, "Samsun area, Black Sea coast, Turkey"),

    # ── Turkey seg 10 col1b ─────────────────────────────────────────────────
    # Cappadocia route west of Kırşehir; known anchors: Congvsso 38.308N 32.869E,
    # Corvevnte 39.695N 32.874E
    2143: (39.200, 32.500, 2, None, "Haymana area, Cappadocia, Turkey"),   # Stabiv
    2265: (38.500, 33.700, 2, None, "central Cappadocia route, Turkey"),   # Tomba
    2266: (39.000, 33.000, 2, None, "Kırşehir/Ankara area, Cappadocia"),  # Evgoni
    2275: (38.800, 33.200, 2, None, "central Cappadocia route, Turkey"),   # Evagina
    2276: (38.600, 33.500, 2, None, "Aksaray area, Cappadocia, Turkey"),   # Saralio

    # ── Turkey seg 10 col2b ─────────────────────────────────────────────────
    # Route Kırşehir (Aqvas Aravenas 39.146N 34.160E) → Sivas (Siva 39.748N 37.016E)
    # Known: Cambe 38.801N 35.024E, Comaralis 39.002N 36.655E, Comassa 39.846N 37.401E
    2281: (39.748, 37.016, 3, "https://en.wikipedia.org/wiki/Sivas", "Sivas/Sebasteia, Turkey"),  # Siva
    2263: (39.350, 35.500, 2, None, "between Kırşehir and Sivas, Turkey"),   # Stabvlvm
    2267: (38.970, 34.600, 2, None, "between Aqvas Aravenas and Cambe, Turkey"),  # Ad stabvlvm
    2268: (38.900, 35.900, 2, None, "between Cambe and Comaralis, Turkey"),  # Mesyla
    2299: (38.600, 35.000, 2, None, "south of Kırşehir–Cambe route, Turkey"),  # Scolla

    # ── Turkey seg 10 col3b ─────────────────────────────────────────────────
    # Known: Armaza 39.185N 36.075E, Sinispora 38.625N 38.132E,
    # Evdagina 38.522N 36.012E, Foroba 39.683N 35.413E
    2306: (38.900, 37.100, 2, None, "Divriği area, eastern Turkey"),        # Incilissa
    2284: (39.100, 35.700, 2, None, "between Evdagina and Foroba, Turkey"), # Sorpara
    2326: (38.000, 35.800, 2, None, "Taurus mt route, central Turkey"),     # Inmonte
    # 2336 Fines cilicie = Gülek Pass (Cilician Gates), confirmed boundary marker
    2336: (37.287, 34.824, 2, None, "Gülek Pass / Cilician Gates, Turkey"),

    # ── Turkey seg 10 col5b ─────────────────────────────────────────────────
    # Known: Megalasso 40.197N 37.980E, Mesorome/Suşehri 40.177N 38.088E,
    # Pagrvm/Elbistan 38.239N 37.302E
    2313: (39.200, 37.700, 2, None, "between Sivas and Suşehri, Turkey"),   # Salandona

    # ── Turkey seg 11 col1b ─────────────────────────────────────────────────
    # Route Elbistan → Malatya → east Armenia
    # Known: Singa/Elbistan 38.203N 37.196E, Nocotesso 38.35N 38.25E,
    # Elegarsina 38.890N 38.971E, Saba 39.114N 38.595E, Vereisso 39.251N 38.496E
    2568: (38.000, 37.700, 2, None, "between Elbistan and SW Malatya, Turkey"),  # Thanna
    2542: (38.500, 38.500, 2, None, "Kılınçlar area, NE of Malatya, Turkey"),    # Oleoberda
    2330: (38.950, 38.800, 2, None, "east of Elegarsina, Malatya area, Turkey"),  # Incomacenis
    # Metridatis regnvm = Pontic kingdom boundary label, roughly near Saba
    2567: (39.100, 38.550, 2, None, "Mithridates kingdom boundary marker, E Turkey"),  # Metridatis regnvm

    # ── Turkey seg 11 col2a ─────────────────────────────────────────────────
    # Erzurum cluster: Calcidava/Ilıca 39.945N 41.108E, Tharsidarate 39.974N 41.490E
    2651: (39.960, 41.300, 2, None, "between Ilıca and Ezirmik, Erzurum, Turkey"),  # Hostra

    # ── Turkey seg 11 col2b ─────────────────────────────────────────────────
    # Known: Sama/Pınarbaşı 38.385N 38.255E, Metita 38.161N 39.144E
    2534: (38.300, 38.700, 2, None, "between Sama and Metita, SE Turkey"),   # Thirtonia

    # ── Turkey seg 11 col3b ─────────────────────────────────────────────────
    # Route Batnae/Sürüç → Harran → Ergani; known: Batnis 36.975N 38.425E,
    # Charris/Harran 36.864N 39.024E, Arsinia/Ergani 38.267N 39.767E
    2630: (37.000, 38.700, 2, None, "E of Batnae/Sürüç toward Harran, SE Turkey"),  # Simitta
    2633: (37.400, 39.400, 2, None, "between Harran and Ergani, SE Turkey"),         # Thalama

    # ── Armenia (ARM) col4a seg11 ───────────────────────────────────────────
    # Known anchors: Hariza 39.697N 43.800E, Coloceia 39.961N 44.208E
    # Rough area estimates only (gc=1)
    2462: (39.800, 44.000, 1, None, "between Hariza and Coloceia, Armenia area"),   # Condeso
    2461: (40.000, 43.700, 1, None, "near Hariza/Aruch area, Armenia"),              # Misivm
    2463: (40.050, 44.100, 1, None, "near Coloceia, eastern Turkey/Armenia"),        # Strangira

    # ── Armenia (ARM) col5a seg11 ───────────────────────────────────────────
    # Near Yerevan area; Catispi (IR) at 39.360N 44.666E for context
    2467: (40.200, 44.500, 1, None, "Yerevan area, Armenia (col5a seg11)"),          # Lalla

    # ── Azerbaijan (AZ) col5a seg11 ─────────────────────────────────────────
    # 2465 Gelvina = Ganja (ancient Gandzak/Ganzak), confirmed
    2465: (40.683, 46.356, 3, "https://en.wikipedia.org/wiki/Ganja,_Azerbaijan", "Ganja/Gandzak, Azerbaijan"),
    # 2472 Philado: east of Ganja on col5a route
    2472: (40.700, 47.000, 2, None, "east of Ganja, Azerbaijan"),                   # Philado

    # ── Georgia (GE) col4a seg11 ────────────────────────────────────────────
    # Known: Ad fontem felicem (GE col3a) 41.833N 43.377E = Borjomi
    # col4a = east of Borjomi → Gori/Uplistsikhe area
    2459: (41.990, 44.100, 2, None, "Gori/Uplistsikhe area, Georgia"),              # Pagas

    # ── Iran (IR) col5a seg11 ───────────────────────────────────────────────
    # NW Iran near Lake Urmia; Catispi at 39.360N 44.666E, Gobdi at 38.553N 44.948E
    2473: (39.000, 44.800, 2, None, "NW Iran near Lake Urmia (Catispi area)"),       # Bvstica

    # ── Iran (IR) seg12 col1b/col1c ─────────────────────────────────────────
    # Route from Rvtarata/Qasr-e Shirin (34.516N 45.578E) eastward
    # Berdanna/Behistun 34.388N 47.432E, Concobas/Kangavar 34.503N 47.956E
    2775: (34.450, 46.300, 2, None, "between Qasr-e Shirin and Behistun, Iran"),     # Siacvs col1b
    2720: (34.480, 48.200, 2, None, "east of Kangavar, western Iran"),               # onoadas col1c

    # ── Iran (IR) seg12 col2b ────────────────────────────────────────────────
    # "Daras Kuh between Onoadas and Concobas" per modern_preferred
    2721: (34.500, 47.700, 2, None, "Daras Kuh area, between Kangavar and onoadas, Iran"),  # Darathe

    # ── Iran (IR) seg12 col2b (Qumis route) ────────────────────────────────
    # "in Cumis" per Miller; Qumis/Hecatompylos = Shahr-i Qumis area
    # Spane/Semnan at 35.572N 53.396E, Hecatompylos at 35.962N 54.037E
    2726: (35.700, 53.700, 2, None, "Qumis region, near Semnan, northern Iran"),    # Pascara

    # ── Iran (IR) seg12 col2c ────────────────────────────────────────────────
    # Between Rapsa/Karaj (35.829N 50.968E) and Europus/Ray (35.580N 51.443E)
    2774: (35.700, 51.200, 2, None, "between Europus/Ray and Karaj, northern Iran"), # Bregnana

    # ── Italy ────────────────────────────────────────────────────────────────
    # 1363 Icentie = Picentia = Pontecagnano Faiano (confirmed by DNP, Barrington;
    # Roman colony established 268 BC near Salerno, Campania)
    1363: (40.625, 14.874, 3, "https://en.wikipedia.org/wiki/Pontecagnano_Faiano",
           "Picentia/Pontecagnano Faiano, Campania, Italy"),
    # 1091 In Portu: "at the harbor" near Populonium (42.989N 10.490E = Piombino area)
    # → Baratti Bay / ancient Porto Baratti
    1091: (42.982, 10.480, 2, None, "Baratti Bay / Porto Baratti near Populonia, Italy"),
    # 1314 Inmonte grani: "perhaps on Via Valeria" (Barrington), near Inmonte carbonario
    # (Roccacerro, 42.066N 13.209E) and Lamnas (42.050N 12.962E) in Lazio/Abruzzo
    1314: (42.100, 13.100, 2, None, "Via Valeria, Lazio/Abruzzo Apennines, Italy"),

    # ── Algeria (DZ) ─────────────────────────────────────────────────────────
    # 154 Adoculum Marinum: "34 miles W of Zarai (Zraia 35.801N 5.679E)" → ~35.80N, 5.10E
    154:  (35.800, 5.100, 2, None, "34 miles W of Zarai/Zraia, Algeria"),
    # 164 Lampsilii: "near Macomades/Milevum (Mila 36.450N 6.267E)", col3c seg3
    164:  (36.400, 6.300, 2, None, "near Milevum/Mila, Algeria"),
    # 113 Vico Iuliani: "between Tipasa/Tifech (36.133N 7.7E) and Hippo Regius/Annaba (36.897N 7.756E)"
    113:  (36.500, 7.730, 2, None, "between Tifech and Hippo Regius/Annaba, Algeria"),
    # 177 Ruglata: "H. Kemeltel near Odiana (36.624N 8.176E) and Thibili (36.367N 7.250E)"
    177:  (36.600, 7.900, 2, None, "H. Kemeltel near Odiana, Algeria"),

    # ── Tunisia (TN) ─────────────────────────────────────────────────────────
    # 220 Prėsididiolele: "H. Soma" in col1c seg5 range
    220:  (35.900, 9.100, 2, None, "H. Soma area, col1c seg5, Tunisia"),
    # 224 AveResvos: "Mehamla am Sebkret Sidi Mansur", near Thasarte (34.067N 9.567E)
    224:  (33.950, 9.450, 2, None, "Mehamla / Sebkret Sidi Mansur area, Tunisia"),
    # 236 Pvteo: "Bir Abd Allah", NE Tunisia route
    236:  (36.350, 10.600, 2, None, "Bir Abd Allah area, NE Tunisia"),
    # 197 Terento: "at Zeroud river crossing" near Kairouan
    197:  (35.750, 10.100, 2, None, "Zeroud river crossing, central Tunisia"),
}


def in_bounds(lat, lng):
    return 5.0 <= lat <= 65.0 and -20.0 <= lng <= 105.0


with open(DB_PATH, encoding='utf-8') as f:
    raw = json.load(f)

data = raw['records']
by_id = {r['data_id']: r for r in data}

hits = 0
skipped = 0
for data_id, (lat, lng, conf, url, note) in FINDS.items():
    rec = by_id.get(data_id)
    if rec is None:
        print(f"  WARN: data_id={data_id} not found in DB")
        continue
    if rec.get('lat'):
        print(f"  SKIP: {data_id} {rec.get('latin_std', rec.get('latin', ''))[:28]} already located")
        skipped += 1
        continue
    if not in_bounds(lat, lng):
        print(f"  SKIP: {data_id} out of bounds {lat},{lng}")
        continue

    print(f"  SET:  {str(data_id):10} {rec.get('latin_std', rec.get('latin', ''))[:28]:28s} -> {lat},{lng}  gc={conf}  [{note}]")
    if not DRY_RUN:
        rec['lat'] = lat
        rec['lng'] = lng
        rec['geocoding_confidence'] = conf
        if url:
            rec['wiki_url'] = url
    hits += 1

print(f"\nTotal: {hits} records to update, {skipped} skipped (already located)")

if not DRY_RUN and hits > 0:
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    backup = DB_PATH.replace('.json', f'_backup_{ts}_pre_ai3.json')
    shutil.copy(DB_PATH, backup)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"DB written. Backup: {backup}")
else:
    print("DRY RUN — no changes written." if DRY_RUN else "Nothing to write.")
