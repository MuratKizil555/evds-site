"""Sayfaların Claude artifact sürümlerini üretir (artifact/<sayfa>.html).

Site sürümü veriyi data/*.json'dan okur; artifact sürümü aynı sayfayı görüntüleyenin
TCMB EVDS bağlantısıyla canlı çalıştırır. Tasarım ve hesaplar tek kaynaktan gelir;
yalnızca veri yükleyici (LOADER bloğu) ve menü bağlantıları değişir.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
# sayfa -> (artifact yükleyicisi, artifact adresi)
PAGES = {
    "rezerv": ("artifact_loader.js", "https://claude.ai/artifact/A7nL8d26HsA2VptJCKMDS5"),
    "kaynak": ("artifact_loader_kaynak.js", "https://claude.ai/artifact/HtQNrqBE3Bre4y2wbVEa5h"),
    "swap": (None, "https://claude.ai/artifact/QAB9sc1EuL6LyJSzPJeb7g"),  # henüz veri yok (yer tutucu sayfa)
    "swap-bist": (None, "https://claude.ai/artifact/MQ3tBnXDdCKRH8P4Zk45SZ"),  # yer tutucu
    "likidite": ("artifact_loader_likidite.js", "https://claude.ai/artifact/JMkyzuvXxi3eBdbDdC3nE6"),
    "cek": ("artifact_loader_cek.js", "https://claude.ai/artifact/LGLoTiPtShNDNXLzqTAq2y"),
    "altin": ("artifact_loader_altin.js", "https://claude.ai/artifact/QZK3PkxNXgnW3XNqkqoKqS"),
    "kur": ("artifact_loader_kur.js", "https://claude.ai/artifact/1fnytfkzMBygSbW9XF5Teq"),
}
nav_src = open(os.path.join(ROOT, "assets", "nav.js"), encoding="utf-8").read()
os.makedirs(os.path.join(ROOT, "artifact"), exist_ok=True)
for page, (loader_file, _) in PAGES.items():
    html = open(os.path.join(ROOT, page, "index.html"), encoding="utf-8").read()
    if loader_file:
        loader = open(os.path.join(ROOT, "scripts", loader_file), encoding="utf-8").read()
        html = re.sub(r"/\*LOADER-START\*/.*?/\*LOADER-END\*/\n", lambda m: loader, html, flags=re.S)
    nav = nav_src
    for p, (_, url) in PAGES.items():
        nav = nav.replace(f"href: '../{p}/'", f"href: '{url}'")
    nav = nav.replace("if (here.includes(s.id))", f"if (s.id === '{page}')")
    html = html.replace('<script src="../assets/nav.js"></script>', "<script>\n" + nav + "\n</script>")
    assert (not loader_file or "watchTool" in html) and "data/" not in html.split("<script>")[-1] and "nav.js" not in html
    open(os.path.join(ROOT, "artifact", page + ".html"), "w", encoding="utf-8").write(html)
    print(f"artifact/{page}.html yazıldı")
