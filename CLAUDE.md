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
- Prototip artifact (yalnızca yedek, canlı veri bağlantısıyla): https://claude.ai/artifact/A7nL8d26HsA2VptJCKMDS5

### Rezerv bölümü — sayfa özellikleri
- **Brüt / Net** düğmeleriyle iki görünüm. Üstte yalnızca son değer ve tarih; değişim pencereleri (1W/1M/YTD/1Y kutuları) ve alt bölümler kullanıcı isteğiyle kaldırıldı.
- Tarih: başlangıç/bitiş seçimi + kısayollar 1M · YTD · 1Y · 3Y · 5Y · 10Y · Tümü. Varsayılan YTD. Grafiğin ilk çubuğu her zaman referans (başlangıç) haftasıdır; panel ile grafik aynı tarihleri kullanır.
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
