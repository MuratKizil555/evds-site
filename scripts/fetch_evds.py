"""TCMB EVDS'ten Rezerv sayfasının verilerini çekip data/rezerv.json dosyasına yazar.

API anahtarı EVDS_API_KEY ortam değişkeninden okunur ve istek başlığında
`key` olarak gönderilir; asla koda ya da çıktıya yazılmaz.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request

BASES = [
    "https://evds3.tcmb.gov.tr/igmevdsms-dis/",
    "https://evds2.tcmb.gov.tr/service/evds/",
]
KEY = os.environ.get("EVDS_API_KEY", "").strip()
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "rezerv.json")
OUT_LIK = os.path.join(os.path.dirname(__file__), "..", "data", "likidite.json")
# Likidite: TCMB net fonlaması ve AOFM (iş günü, milyon TL ve %)
LIKIDITE = {"A": "TP.APIFON1.TOP", "B": "TP.APIFON2.TOP", "N": "TP.APIFON3", "R": "TP.APIFON4"}
LIK_START = dt.date(2011, 1, 1)
OUT_CEK = os.path.join(os.path.dirname(__file__), "..", "data", "cek.json")
# Çek: takas odasında işlem gören çekler (aylık; adet ve bin TL)
CEK = {"ta": "TP.BTO1", "tt": "TP.BTO2", "ka": "TP.BTO3", "kt": "TP.BTO4"}
CEK_START = dt.date(2008, 1, 1)
OUT_ALTIN = os.path.join(os.path.dirname(__file__), "..", "data", "altin.json")
# Altın ithalatı (BİST, aylık kg). Ons fiyatı ve USD/TL kuru günlük verinin aylık ortalaması.
ALTIN_KG = "TP.GOLDIMPRT.V1"
ALTIN_START = dt.date(1995, 7, 1)
OUT_KUR = os.path.join(os.path.dirname(__file__), "..", "data", "kur.json")
# Rezerv kaynakları: analitik bilanço kalemleri ve TCMB taraflı swap stokları (iş günü)
OUT_KAYNAK = os.path.join(os.path.dirname(__file__), "..", "data", "kaynak.json")
KAYNAK_START = dt.date(2015, 1, 1)
KAYNAK_EXTRA = {"A11": "TP.AB.A11", "A13": "TP.AB.A13", "A14": "TP.AB.A14"}
SWAP = {"swA": "TP.SWAPTEKTAR.TOTALSTOKALIMYONLU", "swS": "TP.SWAPTEKTAR.TOTALSTOKSATIMYONLU"}
SWAP_START = dt.date(2021, 1, 1)
OUT_SWAPBIST = os.path.join(os.path.dirname(__file__), "..", "data", "swapbist.json")


def monthly_avg(daily):
    groups = {}
    for d, v in daily.items():
        groups.setdefault(dt.date(d.year, d.month, 1), []).append(v)
    return {m: sum(v) / len(v) for m, v in groups.items()}

# Seri kodları (skill: onaylanmış formüller)
WEEKLY = {"tot": "TP.AB.TOPLAM", "gold": "TP.AB.C1", "fx": "TP.AB.C2"}  # haftalık (Cuma), milyon $
DAILY_TO_WEEKLY = {"A02": "TP.AB.A02", "A10": "TP.AB.A10", "usd": "TP.DK.USD.A.YTL"}  # iş günü -> haftanın son değeri, Cuma etiketli
DAILY = {"px": "TP.ALTINPIYASA.KAP03"}  # BİST altın USD/ons, iş günü

START = dt.date(1987, 12, 1)
PX_START = dt.date(2018, 7, 1)


def fetch(code, start, end):
    q = f"series={code}&startDate={start:%d-%m-%Y}&endDate={end:%d-%m-%Y}&type=json"
    last_err = None
    for base in BASES:
        req = urllib.request.Request(base + q, headers={"key": KEY, "User-Agent": "evds-site"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    body = r.read().decode("utf-8")
                return json.loads(body).get("items", [])
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{code} alınamadı: {last_err}")


def parse_date(item):
    t = str(item.get("Tarih", ""))
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m"):
        try:
            return dt.datetime.strptime(t, fmt).date()
        except ValueError:
            pass
    if item.get("UNIXTIME"):
        u = item["UNIXTIME"]
        u = u.get("$numberLong", u) if isinstance(u, dict) else u
        return dt.datetime.utcfromtimestamp(int(u)).date()
    return None


def series(code, start, end, chunk_years=2):
    # EVDS bir istekte en fazla ~1000 gözlem döndürüyor; günlük seriler 2 yıllık parçalarla çekilir.
    col = code.replace(".", "_")
    out = {}
    s = start
    while s <= end:
        e = min(dt.date(s.year + chunk_years, s.month, 1) - dt.timedelta(days=1), end)
        for it in fetch(code, s, e):
            d, v = parse_date(it), it.get(col)
            if d is None or v in (None, "", "null"):
                continue
            try:
                out[d] = float(v)
            except ValueError:
                pass
        s = e + dt.timedelta(days=1)
    return out


def to_friday_weekly(daily):
    """Her ISO haftasının son gözlemini o haftanın Cuma tarihiyle etiketler."""
    weeks = {}
    for d in sorted(daily):
        fri = d + dt.timedelta(days=(4 - d.weekday()))
        weeks[fri] = daily[d]
    return weeks


def pairs(m):
    return [[d.isoformat(), round(v, 4)] for d, v in sorted(m.items())]


def main():
    if not KEY:
        print("EVDS_API_KEY tanımlı değil; veri çekilmedi.", file=sys.stderr)
        sys.exit(2)
    today = dt.date.today()
    # TCMB kurları bir gün önceden ilan edilir ve Actions UTC saatinde çalışır; bitişi ileri al ki en son tarih kaçmasın
    end = today + dt.timedelta(days=7)
    data = {}
    for k, code in WEEKLY.items():
        data[k] = series(code, START, today, chunk_years=15)
    raw_daily = {}
    for k, code in DAILY_TO_WEEKLY.items():
        raw_daily[k] = series(code, START, end)
        w = to_friday_weekly(raw_daily[k])
        data[k] = {d: v for d, v in w.items() if d <= today}
    for k, code in DAILY.items():
        data[k] = series(code, PX_START, end)
    for k, v in data.items():
        if not v:
            raise RuntimeError(f"{k} boş geldi")
        print(f"{k}: {len(v)} gözlem, son {max(v)}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in data.items()}}, f, separators=(",", ":"))
    lik = {k: series(code, LIK_START, end) for k, code in LIKIDITE.items()}
    for k, v in lik.items():
        if not v:
            raise RuntimeError(f"likidite {k} boş geldi")
        print(f"likidite {k}: {len(v)} gözlem, son {max(v)}")
    with open(OUT_LIK, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in lik.items()}}, f, separators=(",", ":"))
    cek = {k: series(code, CEK_START, today, chunk_years=15) for k, code in CEK.items()}
    for k, v in cek.items():
        if not v:
            raise RuntimeError(f"cek {k} boş geldi")
        print(f"cek {k}: {len(v)} gözlem, son {max(v)}")
    with open(OUT_CEK, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in cek.items()}}, f, separators=(",", ":"))
    altin = {
        "kg": series(ALTIN_KG, ALTIN_START, today, chunk_years=15),
        "px": monthly_avg(data["px"]),
        "usd": monthly_avg(raw_daily["usd"]),
    }
    for k, v in altin.items():
        if not v:
            raise RuntimeError(f"altin {k} boş geldi")
        print(f"altin {k}: {len(v)} gözlem, son {max(v)}")
    with open(OUT_ALTIN, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in altin.items()}}, f, separators=(",", ":"))
    # Kur: USD/TRY günlük (TCMB döviz alış); yıllıklandırma sayfada hesaplanır
    with open(OUT_KUR, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {"usd": pairs(raw_daily["usd"])}}, f, separators=(",", ":"))
    print(f"kur usd: {len(raw_daily['usd'])} gözlem, son {max(raw_daily['usd'])}")
    kay = {k: {d: v for d, v in raw_daily[k].items() if KAYNAK_START <= d <= today} for k in ("A02", "A10", "usd")}
    for k, code in KAYNAK_EXTRA.items():
        kay[k] = series(code, KAYNAK_START, today)
    for k, code in SWAP.items():
        kay[k] = series(code, SWAP_START, today)
    for k, v in kay.items():
        if not v:
            raise RuntimeError(f"kaynak {k} boş geldi")
        print(f"kaynak {k}: {len(v)} gözlem, son {max(v)}")
    with open(OUT_KAYNAK, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in kay.items()}}, f, separators=(",", ":"))
    # BIST swap piyasası stoku (milyon $, iş günü)
    sb = series("TP.SWAPTEKTAR.BISWAPSTOKUSDTUTAR", SWAP_START, today)
    if not sb:
        raise RuntimeError("swap-bist stok boş geldi")
    print(f"swap-bist stok: {len(sb)} gözlem, son {max(sb)}")
    with open(OUT_SWAPBIST, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z", "series": {"stk": pairs(sb)}}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
