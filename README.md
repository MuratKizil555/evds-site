# EVDS Pano

TCMB EVDS istatistiklerini her gün güncellenen görsel sayfalara dönüştüren site.

- **Rezerv** (`rezerv/`): TCMB brüt ve net rezervleri, haftalık; altın fiyat etkisi / miktar değişimi / döviz ayrıştırması.
- Veri: `scripts/fetch_evds.py` her iş günü GitHub Actions ile EVDS'ten çekilir (`EVDS_API_KEY` repo secret'ı gerekir), `data/rezerv.json` olarak siteyle birlikte yayınlanır.
- Yayın: GitHub Pages (Settings → Pages → Source: GitHub Actions).

Kaynak: TCMB Elektronik Veri Dağıtım Sistemi (EVDS).
