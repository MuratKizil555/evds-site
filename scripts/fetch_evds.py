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
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(t, fmt).date()
        except ValueError:
            pass
    if item.get("UNIXTIME"):
        u = item["UNIXTIME"]
        u = u.get("$numberLong", u) if isinstance(u, dict) else u
        return dt.datetime.utcfromtimestamp(int(u)).date()
    return None


def series(code, start, end, chunk_years=8):
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
    data = {}
    for k, code in WEEKLY.items():
        data[k] = series(code, START, today)
    for k, code in DAILY_TO_WEEKLY.items():
        w = to_friday_weekly(series(code, START, today))
        data[k] = {d: v for d, v in w.items() if d <= today}
    for k, code in DAILY.items():
        data[k] = series(code, PX_START, today)
    for k, v in data.items():
        if not v:
            raise RuntimeError(f"{k} boş geldi")
        print(f"{k}: {len(v)} gözlem, son {max(v)}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z",
                   "series": {k: pairs(v) for k, v in data.items()}}, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
