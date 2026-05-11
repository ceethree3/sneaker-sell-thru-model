import csv
import random
from datetime import date, timedelta

random.seed(99)

# --- CONFIG ---
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 6, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days

SIZES = [7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13, 14, 15]

SIZE_WEIGHTS = {
    7.5: 2, 8: 4, 8.5: 5, 9: 7, 9.5: 9, 10: 12, 10.5: 12,
    11: 11, 11.5: 8, 12: 7, 13: 5, 14: 3, 15: 2
}

TIER_CONFIG = {
    "hot":      {"sell_through": (0.82, 0.98), "units_range": (60, 90),  "markdown_pct": 0.03},
    "moderate": {"sell_through": (0.52, 0.78), "units_range": (36, 60),  "markdown_pct": 0.15},
    "slow":     {"sell_through": (0.28, 0.50), "units_range": (24, 48),  "markdown_pct": 0.35},
    "dead":     {"sell_through": (0.04, 0.22), "units_range": (18, 36),  "markdown_pct": 0.60},
}

# Randomized tier pool across 500 SKUs
TIER_POOL = (
    ["hot"] * 120 +
    ["moderate"] * 160 +
    ["slow"] * 140 +
    ["dead"] * 80
)
random.shuffle(TIER_POOL)

# --- PRODUCT TEMPLATES ---
# (vendor_style_prefix, brand_desc, department, sku_desc_base, vendor, retail_price)

PRODUCT_TEMPLATES = [

    # ── RETRO BASKETBALL ──────────────────────────────────────────
    ("FD2596", "NIKE AIR JORDAN 1 RETRO HIGH OG",   "RETRO BASKETBALL", "AJ1 HIGH OG",            "NIKE",        180.00),
    ("DZ5485", "NIKE AIR JORDAN 4 RETRO",            "RETRO BASKETBALL", "AJ4 RETRO",              "NIKE",        210.00),
    ("CT8527", "NIKE AIR JORDAN 1 LOW",              "RETRO BASKETBALL", "AJ1 LOW",                "NIKE",        110.00),
    ("DH8049", "NIKE AIR JORDAN 3 RETRO",            "RETRO BASKETBALL", "AJ3 RETRO",              "NIKE",        200.00),
    ("FQ6855", "NIKE AIR JORDAN 11 RETRO",           "RETRO BASKETBALL", "AJ11 RETRO",             "NIKE",        225.00),
    ("DX4326", "NIKE AIR JORDAN 1 MID",              "RETRO BASKETBALL", "AJ1 MID",                "NIKE",        125.00),
    ("DQ8426", "NIKE AIR JORDAN 6 RETRO",            "RETRO BASKETBALL", "AJ6 RETRO",              "NIKE",        190.00),
    ("CT4481", "NIKE AIR JORDAN 5 RETRO",            "RETRO BASKETBALL", "AJ5 RETRO",              "NIKE",        200.00),
    ("DV1748", "NIKE AIR JORDAN 13 RETRO",           "RETRO BASKETBALL", "AJ13 RETRO",             "NIKE",        185.00),
    ("HF4314", "NIKE AIR JORDAN 2 RETRO",            "RETRO BASKETBALL", "AJ2 RETRO",              "NIKE",        175.00),
    ("DH7139", "NIKE AIR JORDAN 7 RETRO",            "RETRO BASKETBALL", "AJ7 RETRO",              "NIKE",        190.00),
    ("GX4513", "NIKE AIR JORDAN 8 RETRO",            "RETRO BASKETBALL", "AJ8 RETRO",              "NIKE",        190.00),
    ("FB9929", "NIKE AIR JORDAN 9 RETRO",            "RETRO BASKETBALL", "AJ9 RETRO",              "NIKE",        185.00),
    ("HF1234", "NIKE AIR JORDAN 12 RETRO",           "RETRO BASKETBALL", "AJ12 RETRO",             "NIKE",        200.00),
    ("GV7003", "NIKE AIR JORDAN 14 RETRO",           "RETRO BASKETBALL", "AJ14 RETRO",             "NIKE",        190.00),
    ("FD4269", "ADIDAS FORUM LOW",                   "RETRO BASKETBALL", "FORUM LOW",              "ADIDAS",      100.00),
    ("GY5576", "ADIDAS FORUM 84 HIGH",               "RETRO BASKETBALL", "FORUM 84 HIGH",          "ADIDAS",      110.00),
    ("EF2103", "ADIDAS DAME 8",                      "RETRO BASKETBALL", "DAME 8",                 "ADIDAS",      120.00),
    ("GX9265", "ADIDAS MARQUEE BOOST",               "RETRO BASKETBALL", "MARQUEE BOOST",          "ADIDAS",      105.00),
    ("GW6172", "ADIDAS FORUM MID",                   "RETRO BASKETBALL", "FORUM MID",              "ADIDAS",      100.00),
    ("HQ8812", "NEW BALANCE BB550",                  "RETRO BASKETBALL", "BB550",                  "NEW BALANCE", 110.00),
    ("GX4321", "ADIDAS CROSS EM UP 5",               "RETRO BASKETBALL", "CROSS EM UP 5",          "ADIDAS",       90.00),
    ("FY7757", "PUMA MB.01",                         "RETRO BASKETBALL", "MB.01",                  "PUMA",        125.00),
    ("HQ5599", "PUMA MB.02",                         "RETRO BASKETBALL", "MB.02",                  "PUMA",        130.00),
    ("FZ8811", "ADIDAS HARDEN VOL 7",                "RETRO BASKETBALL", "HARDEN VOL 7",           "ADIDAS",      130.00),
    ("HQ2277", "NIKE AIR JORDAN 37",                 "RETRO BASKETBALL", "AJ37",                   "NIKE",        185.00),
    ("GX6644", "NIKE AIR JORDAN 38",                 "RETRO BASKETBALL", "AJ38",                   "NIKE",        185.00),
    ("HQ3388", "ADIDAS DAME 9",                      "RETRO BASKETBALL", "DAME 9",                 "ADIDAS",      120.00),

    # ── PERFORMANCE BASKETBALL ────────────────────────────────────
    ("DV3001", "NIKE LEBRON 21",                     "PERFORMANCE BASKETBALL", "LEBRON 21",          "NIKE",        200.00),
    ("HQ4401", "NIKE LEBRON 20",                     "PERFORMANCE BASKETBALL", "LEBRON 20",          "NIKE",        185.00),
    ("FN7201", "NIKE KD 16",                         "PERFORMANCE BASKETBALL", "KD 16",              "NIKE",        150.00),
    ("GX8801", "NIKE KD 15",                         "PERFORMANCE BASKETBALL", "KD 15",              "NIKE",        140.00),
    ("DZ4401", "NIKE GIANNIS IMMORTALITY 3",         "PERFORMANCE BASKETBALL", "GIANNIS IMMO 3",     "NIKE",        100.00),
    ("HQ6601", "NIKE ZOOM FREAK 5",                  "PERFORMANCE BASKETBALL", "ZOOM FREAK 5",       "NIKE",        120.00),
    ("FZ3301", "ADIDAS TRAE YOUNG 3",                "PERFORMANCE BASKETBALL", "TRAE YOUNG 3",       "ADIDAS",      120.00),
    ("GX9901", "ADIDAS TRAE YOUNG 2",                "PERFORMANCE BASKETBALL", "TRAE YOUNG 2",       "ADIDAS",      110.00),
    ("HQ7701", "ADIDAS EXHIBIT B",                   "PERFORMANCE BASKETBALL", "EXHIBIT B",          "ADIDAS",       90.00),
    ("FY3301", "NEW BALANCE TWO WXY V3",             "PERFORMANCE BASKETBALL", "TWO WXY V3",         "NEW BALANCE", 130.00),
    ("GV8801", "NEW BALANCE TWO WXY V4",             "PERFORMANCE BASKETBALL", "TWO WXY V4",         "NEW BALANCE", 140.00),
    ("HQ1101", "PUMA STEWIE 2",                      "PERFORMANCE BASKETBALL", "STEWIE 2",           "PUMA",        110.00),
    ("GX3301", "PUMA COURT RIDER 3",                 "PERFORMANCE BASKETBALL", "COURT RIDER 3",      "PUMA",         95.00),
    ("FZ1101", "NIKE AIR ZOOM G.T. CUT 3",           "PERFORMANCE BASKETBALL", "GT CUT 3",           "NIKE",        160.00),
    ("HQ9901", "NIKE AIR ZOOM G.T. JUMP 2",          "PERFORMANCE BASKETBALL", "GT JUMP 2",          "NIKE",        150.00),
    ("GX5501", "ADIDAS CROSS EM UP SELECT",          "PERFORMANCE BASKETBALL", "CROSS EM UP SELECT", "ADIDAS",       85.00),
    ("FY8801", "NIKE PRECISION 6",                   "PERFORMANCE BASKETBALL", "PRECISION 6",        "NIKE",         75.00),
    ("HQ4411", "NIKE LEBRON WITNESS 8",              "PERFORMANCE BASKETBALL", "WITNESS 8",          "NIKE",         90.00),
    ("GX2201", "ADIDAS OWNTHEGAME 2",                "PERFORMANCE BASKETBALL", "OWNTHEGAME 2",       "ADIDAS",       70.00),
    ("FZ6601", "PUMA PLAYMAKER PRO",                 "PERFORMANCE BASKETBALL", "PLAYMAKER PRO",      "PUMA",         85.00),
    ("HQ3311", "NIKE G.T. CUT ACADEMY",              "PERFORMANCE BASKETBALL", "GT CUT ACADEMY",     "NIKE",        100.00),
    ("GX7711", "ADIDAS PRO BOUNCE 2019",             "PERFORMANCE BASKETBALL", "PRO BOUNCE 2019",    "ADIDAS",       85.00),
    ("FZ4411", "NEW BALANCE DEFENDER",               "PERFORMANCE BASKETBALL", "DEFENDER",           "NEW BALANCE",  80.00),

    # ── RUNNING ───────────────────────────────────────────────────
    ("DV3853", "NIKE PEGASUS 40",                    "RUNNING", "PEGASUS 40",          "NIKE",        130.00),
    ("FN6338", "NIKE INVINCIBLE 3",                  "RUNNING", "INVINCIBLE 3",        "NIKE",        180.00),
    ("DX2498", "NIKE REVOLUTION 7",                  "RUNNING", "REVOLUTION 7",        "NIKE",         75.00),
    ("GV7750", "NIKE REACT INFINITY 4",              "RUNNING", "REACT INFINITY 4",    "NIKE",        160.00),
    ("HQ1234", "NIKE AIR ZOOM PEGASUS 39",           "RUNNING", "ZOOM PEG 39",         "NIKE",        120.00),
    ("DX9876", "NIKE AIR ZOOM VOMERO 17",            "RUNNING", "ZOOM VOMERO 17",      "NIKE",        170.00),
    ("FZ2043", "NIKE STRUCTURE 25",                  "RUNNING", "STRUCTURE 25",        "NIKE",        130.00),
    ("GX7722", "NIKE ZOOM FLY 5",                    "RUNNING", "ZOOM FLY 5",          "NIKE",        150.00),
    ("HQ1119", "ADIDAS ULTRABOOST 23",               "RUNNING", "ULTRABOOST 23",       "ADIDAS",      190.00),
    ("HQ3790", "ADIDAS RUNFALCON 3",                 "RUNNING", "RUNFALCON 3",         "ADIDAS",       70.00),
    ("IF2384", "ADIDAS SUPERNOVA RISE",              "RUNNING", "SUPERNOVA RISE",      "ADIDAS",      120.00),
    ("GX3210", "ADIDAS SOLAR GLIDE 6",               "RUNNING", "SOLAR GLIDE 6",       "ADIDAS",      130.00),
    ("GX5544", "ADIDAS ADIZERO ADIOS 7",             "RUNNING", "ADIZERO ADIOS 7",     "ADIDAS",      140.00),
    ("GX7788", "ADIDAS DURAMO SL 2",                 "RUNNING", "DURAMO SL 2",         "ADIDAS",       65.00),
    ("HQ2233", "ADIDAS BOSTON 12",                   "RUNNING", "BOSTON 12",           "ADIDAS",      140.00),
    ("FZ2044", "NEW BALANCE 860V13",                 "RUNNING", "860V13",              "NEW BALANCE", 140.00),
    ("ML998F", "NEW BALANCE FRESH FOAM 1080V12",     "RUNNING", "FF 1080V12",          "NEW BALANCE", 165.00),
    ("HQ3416", "NEW BALANCE FRESH FOAM X 1080V13",   "RUNNING", "FF X 1080V13",        "NEW BALANCE", 175.00),
    ("GX9871", "NEW BALANCE FUEL CELL REBEL V4",     "RUNNING", "FC REBEL V4",         "NEW BALANCE", 140.00),
    ("FY1123", "NEW BALANCE 880V14",                 "RUNNING", "880V14",              "NEW BALANCE", 135.00),
    ("HQ5567", "ASICS GEL-NIMBUS 26",               "RUNNING", "GEL-NIMBUS 26",       "ASICS",       160.00),
    ("GX4423", "ASICS GEL-KAYANO 31",               "RUNNING", "GEL-KAYANO 31",       "ASICS",       165.00),
    ("FY3312", "ASICS GEL-CUMULUS 26",              "RUNNING", "GEL-CUMULUS 26",      "ASICS",       130.00),
    ("HQ8834", "ASICS GT-2000 13",                  "RUNNING", "GT-2000 13",          "ASICS",       120.00),
    ("GX6623", "ASICS GEL-TRABUCO 12",              "RUNNING", "GEL-TRABUCO 12",      "ASICS",       130.00),
    ("FZ4412", "ON CLOUDSURFER",                     "RUNNING", "CLOUDSURFER",         "ON",          170.00),
    ("HQ7723", "ON CLOUDMONSTER",                    "RUNNING", "CLOUDMONSTER",        "ON",          170.00),
    ("GX8834", "ON CLOUD 5",                         "RUNNING", "CLOUD 5",             "ON",          140.00),
    ("FY6612", "ON CLOUDSTRATUS 3",                  "RUNNING", "CLOUDSTRATUS 3",      "ON",          180.00),
    ("HQ3345", "ON CLOUDGO",                         "RUNNING", "CLOUDGO",             "ON",          150.00),
    ("GX1123", "SAUCONY KINVARA 14",                 "RUNNING", "KINVARA 14",          "SAUCONY",     110.00),
    ("FZ8823", "SAUCONY RIDE 17",                    "RUNNING", "RIDE 17",             "SAUCONY",     130.00),
    ("HQ5534", "SAUCONY GUIDE 17",                   "RUNNING", "GUIDE 17",            "SAUCONY",     140.00),
    ("GX3345", "SAUCONY TRIUMPH 22",                 "RUNNING", "TRIUMPH 22",          "SAUCONY",     165.00),
    ("FY9912", "SAUCONY ENDORPHIN SPEED 4",          "RUNNING", "ENDORPHIN SPEED 4",   "SAUCONY",     160.00),
    ("HQ1156", "HOKA CLIFTON 9",                     "RUNNING", "CLIFTON 9",           "HOKA",        145.00),
    ("GX4467", "HOKA BONDI 8",                       "RUNNING", "BONDI 8",             "HOKA",        165.00),
    ("FZ2234", "HOKA ARAHI 7",                       "RUNNING", "ARAHI 7",             "HOKA",        140.00),
    ("HQ9945", "HOKA MACH 6",                        "RUNNING", "MACH 6",              "HOKA",        140.00),
    ("GX7756", "HOKA RINCON 3",                      "RUNNING", "RINCON 3",            "HOKA",        125.00),
    ("FY4423", "ASICS GEL-EXCITE 10",               "RUNNING", "GEL-EXCITE 10",       "ASICS",        70.00),
    ("HQ6634", "ASICS GEL-PULSE 15",               "RUNNING", "GEL-PULSE 15",        "ASICS",        90.00),
    ("GX2245", "NEW BALANCE FRESH FOAM ARISHI V4",   "RUNNING", "FF ARISHI V4",        "NEW BALANCE",  70.00),
    ("FZ1123", "SAUCONY COHESION 17",                "RUNNING", "COHESION 17",         "SAUCONY",      75.00),
    ("HQ8845", "HOKA GAVIOTA 5",                     "RUNNING", "GAVIOTA 5",           "HOKA",        165.00),

    # ── LIFESTYLE ─────────────────────────────────────────────────
    ("CW2288", "NIKE AIR FORCE 1 LOW",               "LIFESTYLE", "AF1 LOW",             "NIKE",        115.00),
    ("FZ5808", "NIKE DUNK LOW",                      "LIFESTYLE", "DUNK LOW",            "NIKE",        115.00),
    ("DH2987", "NIKE AIR MAX 90",                    "LIFESTYLE", "AIR MAX 90",          "NIKE",        130.00),
    ("DH8010", "NIKE AIR MAX 97",                    "LIFESTYLE", "AIR MAX 97",          "NIKE",        175.00),
    ("GX1235", "NIKE AIR MAX PLUS",                  "LIFESTYLE", "AIR MAX PLUS",        "NIKE",        165.00),
    ("DZ2629", "NIKE BLAZER MID 77",                 "LIFESTYLE", "BLAZER MID 77",       "NIKE",        105.00),
    ("GX5679", "NIKE AIR MAX 270",                   "LIFESTYLE", "AIR MAX 270",         "NIKE",        150.00),
    ("FZ3345", "NIKE CORTEZ",                        "LIFESTYLE", "CORTEZ",              "NIKE",         85.00),
    ("HQ8900", "NIKE AIR MAX EXCEE",                 "LIFESTYLE", "AIR MAX EXCEE",       "NIKE",         95.00),
    ("GX9913", "NIKE AIR MAX SC",                    "LIFESTYLE", "AIR MAX SC",          "NIKE",         85.00),
    ("FY4424", "NIKE AIR MAX 1",                     "LIFESTYLE", "AIR MAX 1",           "NIKE",        130.00),
    ("HQ2289", "NIKE WAFFLE DEBUT",                  "LIFESTYLE", "WAFFLE DEBUT",        "NIKE",         75.00),
    ("FY3313", "NIKE AIR FORCE 1 HIGH",              "LIFESTYLE", "AF1 HIGH",            "NIKE",        120.00),
    ("GX7757", "NIKE DUNK HIGH",                     "LIFESTYLE", "DUNK HIGH",           "NIKE",        120.00),
    ("B37295", "ADIDAS SAMBA OG",                    "LIFESTYLE", "SAMBA OG",            "ADIDAS",      100.00),
    ("GY3437", "ADIDAS GAZELLE",                     "LIFESTYLE", "GAZELLE",             "ADIDAS",      100.00),
    ("GY0027", "ADIDAS STAN SMITH",                  "LIFESTYLE", "STAN SMITH",          "ADIDAS",       90.00),
    ("FZ5922", "ADIDAS NMD R1",                      "LIFESTYLE", "NMD R1",              "ADIDAS",      140.00),
    ("FY5457", "ADIDAS OZELIA",                      "LIFESTYLE", "OZELIA",              "ADIDAS",      100.00),
    ("GY4321", "ADIDAS CAMPUS 00S",                  "LIFESTYLE", "CAMPUS 00S",          "ADIDAS",       95.00),
    ("GX3346", "ADIDAS LITE RACER 3.0",              "LIFESTYLE", "LITE RACER 3.0",      "ADIDAS",       65.00),
    ("HQ7655", "ADIDAS ULTRABOOST 1.0",              "LIFESTYLE", "ULTRABOOST 1.0",      "ADIDAS",      180.00),
    ("GX6678", "ADIDAS GAZELLE BOLD",                "LIFESTYLE", "GAZELLE BOLD",        "ADIDAS",      110.00),
    ("FY2234", "ADIDAS HANDBALL SPEZIAL",            "LIFESTYLE", "HANDBALL SPEZIAL",    "ADIDAS",      100.00),
    ("HQ5534", "ADIDAS SAMBA ADV",                   "LIFESTYLE", "SAMBA ADV",           "ADIDAS",      110.00),
    ("GV7624", "NEW BALANCE 550",                    "LIFESTYLE", "550",                 "NEW BALANCE", 110.00),
    ("ML574F", "NEW BALANCE 574",                    "LIFESTYLE", "574",                 "NEW BALANCE",  90.00),
    ("HQ3417", "NEW BALANCE 327",                    "LIFESTYLE", "327",                 "NEW BALANCE", 100.00),
    ("ML998G", "NEW BALANCE 998",                    "LIFESTYLE", "998 MADE IN USA",     "NEW BALANCE", 185.00),
    ("GX9872", "NEW BALANCE 2002R",                  "LIFESTYLE", "2002R",               "NEW BALANCE", 115.00),
    ("FY8845", "NEW BALANCE 1906R",                  "LIFESTYLE", "1906R",               "NEW BALANCE", 150.00),
    ("HQ6689", "NEW BALANCE 9060",                   "LIFESTYLE", "9060",                "NEW BALANCE", 150.00),
    ("GX3356", "NEW BALANCE 530",                    "LIFESTYLE", "530",                 "NEW BALANCE",  90.00),
    ("FZ7712", "ASICS GEL-1130",                     "LIFESTYLE", "GEL-1130",            "ASICS",       110.00),
    ("HQ4423", "ASICS GEL-KAYANO 14",               "LIFESTYLE", "GEL-KAYANO 14",       "ASICS",       120.00),
    ("GX8845", "ASICS GEL-NYC",                     "LIFESTYLE", "GEL-NYC",             "ASICS",       120.00),
    ("FY5567", "ON CLOUD X 3",                       "LIFESTYLE", "CLOUD X 3",           "ON",          150.00),
    ("HQ1178", "ON CLOUDNOVA",                       "LIFESTYLE", "CLOUDNOVA",           "ON",          150.00),
    ("GX2289", "SAUCONY JAZZ ORIGINAL",              "LIFESTYLE", "JAZZ ORIGINAL",       "SAUCONY",      80.00),
    ("FZ9934", "SAUCONY SHADOW 6000",                "LIFESTYLE", "SHADOW 6000",         "SAUCONY",      90.00),
    ("HQ6656", "HOKA CLIFTON L",                     "LIFESTYLE", "CLIFTON L",           "HOKA",        155.00),
    ("GX5567", "HOKA TRANSPORT",                     "LIFESTYLE", "TRANSPORT",           "HOKA",        130.00),
    ("FY7778", "NEW BALANCE 1080V13",                "LIFESTYLE", "1080V13",             "NEW BALANCE", 165.00),
    ("HQ3322", "ASICS GEL-LYTE III",               "LIFESTYLE", "GEL-LYTE III",        "ASICS",       100.00),

    # ── SEASONAL ──────────────────────────────────────────────────
    ("FD3001", "NIKE AIR MAX 90 WINTER",             "SEASONAL", "AM90 WINTER PRM",      "NIKE",        150.00),
    ("HQ5001", "NIKE MANOA LEATHER",                 "SEASONAL", "MANOA LEATHER BOOT",   "NIKE",        110.00),
    ("GX7001", "NIKE REACT WR ISPA",                 "SEASONAL", "REACT WR ISPA",        "NIKE",        160.00),
    ("FZ1002", "NIKE ACG LOWCATE",                   "SEASONAL", "ACG LOWCATE",          "NIKE",        100.00),
    ("HQ3002", "NIKE PEGASUS TRAIL 5 GTX",           "SEASONAL", "PEG TRAIL 5 GTX",      "NIKE",        165.00),
    ("GX1002", "ADIDAS TERREX SWIFT R3 GTX",         "SEASONAL", "TERREX SWIFT R3 GTX",  "ADIDAS",      160.00),
    ("FY5002", "ADIDAS NMD W1",                      "SEASONAL", "NMD W1",               "ADIDAS",      140.00),
    ("HQ7002", "ADIDAS ULTRABOOST COLD RDY",         "SEASONAL", "UB COLD RDY",          "ADIDAS",      200.00),
    ("GX9002", "ADIDAS TERREX TRAILMAKER 2",         "SEASONAL", "TERREX TRAILMKR 2",    "ADIDAS",      130.00),
    ("FZ3002", "NEW BALANCE 1000 GORE-TEX",          "SEASONAL", "1000 GTX",             "NEW BALANCE", 175.00),
    ("HQ1002", "NEW BALANCE FRESH FOAM 1080 WX",     "SEASONAL", "FF 1080 WX",           "NEW BALANCE", 165.00),
    ("GX3002", "ASICS GEL-SONOMA 7 GTX",            "SEASONAL", "GEL-SONOMA 7 GTX",     "ASICS",       120.00),
    ("FY7002", "ASICS GEL-VENTURE 9 AWL",           "SEASONAL", "GEL-VENTURE 9 AWL",    "ASICS",        80.00),
    ("HQ5012", "ON CLOUDWANDER WATERPROOF",          "SEASONAL", "CLOUDWANDER WP",       "ON",          160.00),
    ("GX7012", "ON CLOUDVENTURE WATERPROOF",         "SEASONAL", "CLOUDVENTURE WP",      "ON",          150.00),
    ("FZ5012", "SAUCONY PEREGRINE 14 GTX",           "SEASONAL", "PEREGRINE 14 GTX",     "SAUCONY",     145.00),
    ("HQ3012", "SAUCONY KINVARA TR",                 "SEASONAL", "KINVARA TR",           "SAUCONY",     120.00),
    ("GX1012", "HOKA ANACAPA 2 GTX",                 "SEASONAL", "ANACAPA 2 GTX",        "HOKA",        185.00),
    ("FY9002", "HOKA KAWAIKINI 8",                   "SEASONAL", "KAWAIKINI 8",          "HOKA",        160.00),
    ("HQ7012", "NIKE DOWNSHIFTER 13",                "SEASONAL", "DOWNSHIFTER 13",       "NIKE",         70.00),
    ("GX5012", "ADIDAS TERREX AX4 GTX",              "SEASONAL", "TERREX AX4 GTX",       "ADIDAS",      130.00),
    ("FZ8012", "NEW BALANCE HIERRO V7 GTX",          "SEASONAL", "HIERRO V7 GTX",        "NEW BALANCE", 155.00),
    ("HQ2012", "ASICS GEL-QUANTUM 360 VII",         "SEASONAL", "GEL-QUANTUM 360 VII",  "ASICS",       160.00),
    ("GX4012", "ON CLOUDULTRA 2",                    "SEASONAL", "CLOUDULTRA 2",         "ON",          170.00),
    ("FY6012", "SAUCONY XODUS ULTRA 2",              "SEASONAL", "XODUS ULTRA 2",        "SAUCONY",     160.00),
    ("HQ9012", "HOKA SPEEDGOAT 5 GTX",               "SEASONAL", "SPEEDGOAT 5 GTX",      "HOKA",        175.00),
    ("GX2012", "NIKE ACG MOUNTAIN FLY 2 LOW GTX",    "SEASONAL", "ACG MTN FLY 2 LO GTX", "NIKE",       175.00),
    ("FZ6012", "ADIDAS FIVE TEN TRAILCROSS GTX",     "SEASONAL", "TRAILCROSS GTX",       "ADIDAS",      140.00),
]

COLORWAYS = [
    "BLK/WHT", "WHT/BLK", "GRY/BLK", "NVY/WHT", "RED/BLK",
    "GRN/WHT", "BLU/WHT", "TAN/GUM", "OLV/BLK", "PNK/WHT",
    "ONG/BLK", "BRN/GLD", "CRM/GLD", "SLT/GRY", "CBT/WHT",
    "PRP/GLD", "YLW/BLK", "TRQ/WHT", "BRG/TAN", "GRN/GLD",
    "BLK/RED", "WHT/GLD", "GRY/WHT", "NVY/RED", "BLU/GLD",
]


def build_sku_catalog(target=500):
    catalog = []
    sku_counter = 1
    tier_index = 0
    used_combos = set()

    attempts = 0
    while len(catalog) < target and attempts < 5000:
        attempts += 1
        template = random.choice(PRODUCT_TEMPLATES)
        vs_prefix, brand_desc, dept, sku_desc_base, vendor, retail_price = template
        colorway = random.choice(COLORWAYS)

        combo = (sku_desc_base, colorway)
        if combo in used_combos:
            continue
        used_combos.add(combo)

        tier = TIER_POOL[tier_index % len(TIER_POOL)]
        tier_index += 1

        dept_code = {
            "RETRO BASKETBALL": "20",
            "PERFORMANCE BASKETBALL": "25",
            "RUNNING": "30",
            "LIFESTYLE": "40",
            "SEASONAL": "50"
        }[dept]

        sku = f"30-{dept_code}-{sku_counter:06d}-0-10"
        vendor_style = f"{vs_prefix}-{random.randint(100, 999)}"
        sku_desc = f"{sku_desc_base} {colorway}"

        catalog.append((sku, vendor_style, brand_desc, dept, sku_desc, vendor, retail_price, tier))
        sku_counter += 1

    return catalog[:target]


# --- SIZE DISTRIBUTION ---
def get_size_units(total_units):
    weights = [SIZE_WEIGHTS[s] for s in SIZES]
    total_weight = sum(weights)
    size_units = {}
    allocated = 0
    for i, size in enumerate(SIZES[:-1]):
        units = round(total_units * weights[i] / total_weight)
        size_units[size] = max(1, units)
        allocated += size_units[size]
    size_units[SIZES[-1]] = max(1, total_units - allocated)
    return size_units


# --- DATE HELPERS ---
def receive_date_for_sku(tier):
    if tier == "hot":
        return START_DATE + timedelta(days=random.randint(0, 30))
    elif tier == "moderate":
        return START_DATE + timedelta(days=random.randint(0, 60))
    elif tier == "slow":
        return START_DATE + timedelta(days=random.randint(14, 90))
    else:
        return START_DATE + timedelta(days=random.randint(30, 120))


# --- GENERATE ---
SKU_CATALOG = build_sku_catalog(500)

inventory_rows = []
sales_rows = []
sale_id_counter = 1

for sku_data in SKU_CATALOG:
    sku, vendor_style, brand_desc, department, sku_desc, vendor, retail_price, tier = sku_data
    config = TIER_CONFIG[tier]

    total_units = random.randint(*config["units_range"])
    size_units = get_size_units(total_units)
    recv_date = receive_date_for_sku(tier)
    sell_through_rate = random.uniform(*config["sell_through"])

    for size, units in size_units.items():
        size_str = str(int(size)) if size == int(size) else str(size)

        inventory_rows.append({
            "receive_date": recv_date.strftime("%Y-%m-%d"),
            "sku": sku,
            "vendor_style": vendor_style,
            "brand_desc": brand_desc,
            "department": department,
            "sku_desc": sku_desc,
            "vendor": vendor,
            "size": size_str,
            "units_received": units,
            "retail_price": f"{retail_price:.2f}",
        })

        units_to_sell = round(units * sell_through_rate)
        size_modifier = SIZE_WEIGHTS[size] / 12.0
        units_to_sell = min(units, round(units_to_sell * size_modifier + random.uniform(-0.5, 0.5)))
        units_to_sell = max(0, units_to_sell)

        markdown_threshold = round(units_to_sell * (1 - config["markdown_pct"]))

        for i in range(units_to_sell):
            days_offset = int((i / max(units_to_sell, 1)) * TOTAL_DAYS * random.uniform(0.6, 1.0))
            sale_date = recv_date + timedelta(days=days_offset)
            if sale_date > END_DATE:
                sale_date = END_DATE

            is_markdown = i >= markdown_threshold
            sale_type = "markdown" if is_markdown else "full_price"
            sale_price = round(retail_price * random.uniform(0.70, 0.85), 2) if is_markdown else retail_price

            sales_rows.append({
                "sale_id": f"S-{sale_id_counter:05d}",
                "sku": sku,
                "size": size_str,
                "sale_date": sale_date.strftime("%Y-%m-%d"),
                "quantity_sold": 1,
                "retail_price": f"{retail_price:.2f}",
                "sale_price": f"{sale_price:.2f}",
                "sale_type": sale_type,
            })
            sale_id_counter += 1

# --- WRITE ---
inv_fields = ["receive_date","sku","vendor_style","brand_desc","department","sku_desc","vendor","size","units_received","retail_price"]
sales_fields = ["sale_id","sku","size","sale_date","quantity_sold","retail_price","sale_price","sale_type"]

with open("inventory.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=inv_fields)
    writer.writeheader()
    writer.writerows(inventory_rows)

with open("sales.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=sales_fields)
    writer.writeheader()
    writer.writerows(sales_rows)

from collections import Counter
tiers = [row[7] for row in SKU_CATALOG]
tier_counts = Counter(tiers)
depts = Counter(row[3] for row in SKU_CATALOG)
vendors = Counter(row[5] for row in SKU_CATALOG)

print(f"Done.")
print(f"inventory.csv  — {len(inventory_rows):,} rows")
print(f"sales.csv      — {len(sales_rows):,} rows")
print(f"SKUs: {len(SKU_CATALOG)}")
print(f"\nTier distribution: {dict(tier_counts)}")
print(f"\nDepartments: {dict(depts)}")
print(f"\nVendors: {dict(vendors)}")
