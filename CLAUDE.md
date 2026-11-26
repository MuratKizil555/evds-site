# EVDS Pano — proje notları

Bu dosya projenin kalıcı hafızasıdır; değişiklik yaptıkça güncel tut.


# EVDS Dinamik Ekonomi Sitesi

## 1. Amaç
TCMB EVDS'te yayımlanan verileri **bir çırpıda anlaşılacak şekilde** görselleştirmek. Proje EVDS'teki pek çok veri grubunu kapsayacak şekilde zamanla büyür.
- Her gösterge için tek bakışta: son değer, önceki döneme göre değişim, yön (↑/↓) ve kısa bir grafik.
- Teknik terimler bir cümlelik sade açıklamayla verilir.
- Her grafiğin altında son veri tarihi, kaynak seri kodları ve (varsa) uygulanan formül yer alır.
- Göstergeler EVDS kategorilerine göre bölümlere ayrılır (fiyatlar, döviz, TCMB bilançosu, dış istatistikler, parasal/finansal, reel sektör, beklentiler…).

## 2. Yayın: herkese açık internet sitesi
- **Prototip:** Claude artifact'i; sayfa `mcp` capability ile TCMB EVDS bağlantısını canlı çağırır. Görüntüleyenin kendi bağlantısı gerektiğinden yalnızca tasarım ve formül doğrulaması içindir.
- **Nihai yayın:** GitHub deposu + GitHub Actions (günlük cron) + GitHub Pages veya Vercel. Actions EVDS API'den veriyi çeker, formülleri uygular ve JSON üretir; site bu JSON'u okur. Ziyaretçinin hesap veya anahtarı gerekmez.
- EVDS API anahtarı yalnızca repo secret olarak tutulur ve istek başlığında `key` olarak gönderilir; koda veya sayfaya asla yazılmaz.
- Gösterge tanımları ve formüller tek modülde tutulur; prototipten nihai siteye değişmeden taşınır.

## 3. Hesaplanan göstergeler (formülasyon)
Bazı göstergeler EVDS'te hazır yayımlanmaz; birden çok kalemin toplanıp çıkarılması, oranlanması veya dönüştürülmesiyle elde edilir.

### Formülü bulma sırası
1. **Kullanıcının kaynak dokümanları:** Masaüstündeki "Pertavsız" klasörü proje kaynak kütüphanesidir. Önce oraya bakılır. Örnek: *Bilanco_ve_AB_Kitap.pdf* (TCMB, 2016) TCMB bilançosu ve analitik bilanço kalemlerini ve bunlardan türetilen büyüklükleri tanımlar.
2. **TCMB'nin resmi metaveri ve metodoloji belgeleri** (EVDS seri açıklamaları, istatistik sayfaları, IMF kılavuzları).
3. **Güncel piyasa uygulaması:** Kaynak doküman eskiyse veya kavramı kapsamıyorsa web'den doğrulanır. Bu durumda kaynak açıkça yazılır.

Claude'un bulduğu veya önerdiği her formül, kaynak ve kalem eşleştirmesiyle birlikte kullanıcıya gösterilir. **Kullanıcı onaylamadan siteye konmaz.**

### Gösterge tanımı
Her türetilmiş gösterge şu alanlarla tanımlanır: `id`, `ad`, `sade açıklama`, `girdiler` (EVDS seri kodları), `formül`, `birim`, `frekans`, `kaynak` (doküman ve sayfa ya da URL).

### Kurallar
- Ham seriler değiştirilmez; hesaplama ayrı bir katmanda yapılır.
- **Frekans uyumu açık yazılır:** farklı frekanstaki seriler birleşecekse dönem sonu mu ortalama mı kullanıldığı tanımda belirtilir.
- **Birim dönüşümü formülün parçasıdır:** bin TL → milyar TL, TL → USD (aynı tarihin TCMB kuruyla) gibi.
- Eksik veri uydurulmaz. Ara doldurma yapılırsa grafikte işaretlenir. Yıllık değişim için karşılaştırma dönemi yoksa sonuç boş kalır.
- Muhasebe denkliği olan yerlerde (ör. analitik bilançoda aktif = pasif) denklik her güncellemede otomatik test edilir. Tutmuyorsa seri eşleştirmesi yanlıştır.
- Mümkünse hesaplanan değer, aynı kavramın resmi veya kamuoyunda yayımlanmış değeriyle karşılaştırılır.

### Gösterim
Kullanıcı tüm işlemlerin **dikey kesir** formatında gösterilmesini istiyor. Sohbette ve sitede (KaTeX) `\frac{}{}` kullanılır. Örnek:
$$\left(\frac{X_t}{X_{t-12}} - 1\right) \times 100$$

## Veri bulma (TCMB MCP)
Akış: `list_categories` → `list_datagroups(category_id, keywords)` → `list_series(datagroup_code, keywords)` → `get_series_data(series_code, start_date, end_date)`.
- Spesifik terimler (USD, EUR, kalem adları) seri düzeyinde aranır.
- Bulunan her seri kodu adı, frekansı, birimi ve yayım sıklığıyla birlikte bir seri kataloğuna kaydedilir; aynı arama tekrarlanmaz.
- Yeni bir veri grubu incelenirken önce serilerin listesi ve tanımları kullanıcıyla gözden geçirilir; hangilerinin gösterileceğine ve hangilerinin hesaplamaya gireceğine birlikte karar verilir.

## Kontrol
- Yayın öncesi sayfa açılır; grafiklerin dolu, tarihlerin güncel ve sayıların makul olduğu kontrol edilir.
- Her yeni formül ilk kez eklendiğinde birkaç tarih için elle hesaplanarak karşılaştırılır.

## Site yapısı ve mevcut sayfalar
Site sol tarafta bir menüyle bölümlere ayrılır. Her bölüm bir sayfadır.

### Canlı site (asıl çalışma yeri)
- Adres: https://muratkizil555.github.io/evds-site/ — GitHub deposu: MuratKizil555/evds-site (add_repo ile bağlan, push erişimi).
- Yapı: `assets/nav.js` (sol menü; yeni bölüm = SECTIONS listesine satır), `rezerv/index.html` (Rezerv sayfası), `scripts/fetch_evds.py` (EVDS'ten veri → `data/rezerv.json`), `.github/workflows/deploy.yml` (push'ta ve hafta içi 16:37/19:37 TR'de veri çek + Pages'e yayınla).
- EVDS anahtarı repo secret `EVDS_API_KEY`. EVDS bir istekte ~1000 gözlem döndürür: günlük seriler 2 yıllık, haftalık 15 yıllık parçalarla çekilir.
- Değişiklik akışı: depoda düzenle → commit → push → 2–3 dk içinde sitede. Yayını `gh api repos/MuratKizil555/evds-site/actions/runs` ile takip et.
- **Claude artifact sürümü (kullanıcı burada görmeyi tercih ediyor):** https://claude.ai/artifact/A7nL8d26HsA2VptJCKMDS5 (slug 49d4a565-13ab-48c7-a104-0f98a491fc3e). Sitedeki sayfanın aynısı; veriyi görüntüleyenin TCMB EVDS bağlantısından canlı çeker.
- **Her değişiklikte iki yere yayınla:** `rezerv/index.html` düzenle → `python3 scripts/build_artifact.py` (artifact/rezerv.html üretir; veri yükleyici `scripts/artifact_loader.js`, /*LOADER-START*/…/*LOADER-END*/ bloğunun yerine geçer) → artifact'i publish_files ile güncelle (as: index.html) → commit + push (GitHub sitesi).

### Artifact'ler (sayfa başına bir tane; menü bağlantıları birbirine gider)
- Rezerv: https://claude.ai/artifact/A7nL8d26HsA2VptJCKMDS5 (slug 49d4a565-13ab-48c7-a104-0f98a491fc3e)
- Likidite: https://claude.ai/artifact/JMkyzuvXxi3eBdbDdC3nE6 (slug 8c915683-5b5f-4dee-ae3a-4a0a19e90ccb)
- Çek: https://claude.ai/artifact/LGLoTiPtShNDNXLzqTAq2y (slug 9c01fe71-58df-460e-b42f-76b80570c7fa)
- Altın: https://claude.ai/artifact/QZK3PkxNXgnW3XNqkqoKqS (slug bec51bae-a7ea-40dc-8755-88921ff0e611)
- `scripts/build_artifact.py` PAGES listesindeki her sayfa için artifact/<sayfa>.html üretir. Yeni sayfa: PAGES'e ekle, yeni artifact oluştur, mcp yeteneğini declare_capabilities ile tanımla.

### Likidite bölümü — sayfa özellikleri
- Seriler (bie_apifon, iş günü, milyon TL / %): TP.APIFON1.TOP (fonlama), TP.APIFON2.TOP (sterilizasyon), TP.APIFON3 (net fonlama = A−B, TCMB yayımlar), TP.APIFON4 (AOFM). 2011'den beri.
- Üstte net fonlama ve AOFM kutuları; tarih kontrolleri Rezerv'le aynı (1W…Tümü, varsayılan YTD).
- Grafik 1: yalnızca net fonlama çubukları (pozitif koyu mavi, negatif kırmızı), sıfır çizgisi. Grafik 2: AOFM düz çizgi grafiği.
- Grafikler tam genişlikte; x ekseni yalnızca veri olan iş günlerinden oluşur (tatil/hafta sonu boşluğu yok), çubuk en fazla 18 px. Tooltip: tarih, net fonlama, AOFM. Özet paneli ve gün seçimi kullanıcı isteğiyle kaldırıldı. Grafiklerin altında kaynak olarak yalnızca "Kaynak: EVDS" yazar.

### Çek bölümü — sayfa özellikleri
- Seriler (bie_btocek, aylık, 2008'den): TP.BTO1 toplam ibraz edilen çek adedi, TP.BTO2 toplam ibraz edilen çek tutarı (bin TL), TP.BTO3 karşılıksız çek adedi, TP.BTO4 karşılıksız çek tutarı (bin TL). Tutarlar milyar TL gösterilir (÷10⁶), nominal.
- **Adet / Tutar** düğmeleri tüm sayfayı değiştirir. Üstte üç kutu: karşılıksız, toplam ibraz, karşılıksız oranı (son ay).
- Tek grafik: karşılıksız çek (adet ya da tutar) açık altın/kum rengi çubuklar (--bar), sol eksen sıfırdan + karşılıksız oranı (karşılıksız ÷ toplam ibraz × 100) koyu petrol yeşili düz çizgi (--rate), sağ eksen. Formül sayfada gösterilmez (kullanıcı isteği).
- Tarih: ay seçici + YTD · 1Y · 3Y · 5Y · 10Y · Tümü; varsayılan 3Y. Grafik altında "Kaynak: EVDS".

### Altın bölümü — sayfa özellikleri
- Seri: TP.GOLDIMPRT.V1 (BİST altın ithalatı, kg, aylık, Temmuz 1995'ten). Fiyat: TP.ALTINPIYASA.KAP03 (BİST USD/ons, Temmuz 2018'den), kur: TP.DK.USD.A.YTL; ikisi de aylık ortalama (site: günlük verinin aylık ortalaması; artifact: EVDS frequency 5 + avg).
- Formül (Claude önerisi, kullanıcı onayı bekliyor): USD karşılığı = kg × 32,1507466 × ons fiyatı; TL karşılığı = USD karşılığı × USD/TL. 2018-07 öncesi karşılıklar boş.
- Üstte üç kutu: son ay ithalat (kg), USD karşılığı (milyon $), TL karşılığı (milyar TL). Grafik: aylık kg çubukları (altın rengi). Altında tablo: ay, kg, ons, ons fiyatı, USD karşılığı, USD/TL, TL karşılığı. Tablo yalnızca seçili ayı gösterir: varsayılan son ay, grafikte tıklanan ay seçilir (çubuk çerçevelenir; diğer çubuklar soluklaşmaz). Tüm aylar ve aralık toplamı gösterilmez.

### Rezerv bölümü — sayfa özellikleri
- **Brüt / Net** düğmeleriyle iki görünüm. Üstte yalnızca son değer ve tarih; değişim pencereleri (1W/1M/YTD/1Y kutuları) ve alt bölümler kullanıcı isteğiyle kaldırıldı.
- Tarih: başlangıç/bitiş seçimi + kısayollar 1W · 1M · YTD · 1Y · 3Y · 5Y · 10Y · Tümü. Varsayılan YTD. Grafiğin ilk çubuğu her zaman referans (başlangıç) haftasıdır; panel ile grafik aynı tarihleri kullanır.
- **Brüt görünüm:** haftalık yığılmış çubuk (altın altta, döviz koyu mavi üstte), çubuk toplamlarından geçen pürüzsüz kırmızı toplam çizgisi. Kısa aralıkta çubuklar en fazla 16 px, eksen en az ~4 ay (sağ boş kalabilir). İmleç normal ok. Tooltip: tarih, toplam, altın (%pay), döviz (%pay).
- **Sağ panel (brüt):** seçili aralık ya da tıklanan hafta için üç dilimli pasta + dikey çizginin yanında alt alta toplanan liste: Altın fiyat etkisi + Altın miktar değişimi + Döviz değişimi = Brüt rezerv değişimi (milyar $, oran yok). Aynı haftaya ikinci tıklama seçimi kaldırır ve aralığa döner.
- **Net görünüm:** haftalık net rezerv çubukları (pozitif koyu mavi, negatif kırmızı), sıfır çizgisi her zaman görünür. Tooltip yalnızca net rezerv. Panel: Dış varlıklardaki değişim + Döviz yükümlülüklerindeki değişim (−) = Net rezerv değişimi.

### Onaylanmış formüller
- Haftalık altın miktarı: $$Q_t = \frac{\text{Altın rezervi}_t}{\text{Altın fiyatı}_t}$$ (TP.AB.C1 ÷ TP.ALTINPIYASA.KAP03, Cuma veya önceki son kapanış; fiyat Temmuz 2018'de başlar).
- Fiyat etkisi = Σ Q_{k−1}(P_k − P_{k−1}); miktar değişimi = Σ (Q_k − Q_{k−1})P_k — haftalık hesaplanıp toplanır (zincirleme). "Miktar değişimi" net satış/alım, altın swapları, altın zorunlu karşılıkları vb. kapsar; "rezerv satışı" denmez.
- Net rezerv (PDF s.48): $$\frac{\text{TP.AB.A02} - \text{TP.AB.A10}}{\text{TP.DK.USD.A.YTL} \times 1000}$$ milyon $; seriler haftalık (frequency 3, aggregation last → Cuma).

### Açık konular
- Basındaki net rezerv rakamları bizimkinden ~4,8 milyar $ yüksek (yöntem yayımlanmamış). Hakan Kara ve "507" hesaplarının yöntemi araştırılacak; kullanıcı onaylamadan formül değiştirilmez.
- Bu aşamada sayfada veri yorumu yapılmaz, yalnızca görselleştirilir.
