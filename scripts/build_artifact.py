"""Rezerv sayfasının Claude artifact sürümünü üretir (artifact/rezerv.html).

Site sürümü veriyi data/rezerv.json'dan okur; artifact sürümü aynı sayfayı
görüntüleyenin TCMB EVDS bağlantısıyla canlı çalıştırır. Tasarım ve hesaplar
tek kaynaktan (rezerv/index.html) gelir; yalnızca veri yükleyici ve menü değişir.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
page = open(os.path.join(ROOT, "rezerv", "index.html"), encoding="utf-8").read()
loader = open(os.path.join(ROOT, "scripts", "artifact_loader.js"), encoding="utf-8").read()
nav = open(os.path.join(ROOT, "assets", "nav.js"), encoding="utf-8").read()

page = re.sub(r"/\*LOADER-START\*/.*?/\*LOADER-END\*/\n", lambda m: loader, page, flags=re.S)
nav = nav.replace("href: '../rezerv/'", "href: '#'").replace("if (here.includes(s.id))", "if (s.id === 'rezerv')")
page = page.replace('<script src="../assets/nav.js"></script>', "<script>\n" + nav + "\n</script>")
assert "watchTool" in page and "data/rezerv.json" not in page and "nav.js" not in page
os.makedirs(os.path.join(ROOT, "artifact"), exist_ok=True)
open(os.path.join(ROOT, "artifact", "rezerv.html"), "w", encoding="utf-8").write(page)
print("artifact/rezerv.html yazıldı")
