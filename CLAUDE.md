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
- Kur: https://claude.ai/artifact/1fnytfkzMBygSbW9XF5Teq (slug 056a9998-6a00-4908-b34c-29a9e42e70fa)
- Rezerv kaynakları: https://claude.ai/artifact/HtQNrqBE3Bre4y2wbVEa5h (slug 88bf8eae-2be7-4968-af65-eae9db0151bc)
- `scripts/build_artifact.py` PAGES listesindeki her sayfa için artifact/<sayfa>.html üretir. Yeni sayfa: PAGES'e ekle, yeni artifact oluştur, mcp yeteneğini declare_capabilities ile tanımla.

### Rezerv kaynakları bölümü — sayfa özellikleri (menüde Rezerv'in altında; Rezerv sayfasına dokunulmaz — kullanıcı isteği)
- Başlık: "Net rezerv değişimi ve kaynakları" (kullanıcı onaylı; "döviz alım-satımı" denmez, TCMB bunu yayımlamaz).
- Düğmeler: **Günlük / Haftalık** (varsayılan günlük; haftalık = haftanın son iş günü) ve **Swap dahil / Swap hariç** (varsayılan dahil). Üstte iki kutu: net rezerv, önceki güne/haftaya göre değişim.
- Grafik: net rezerv **stoku** çubukları (pozitif koyu mavi, negatif kırmızı, sıfır çizgisi; kullanıcı isteği: değişim değil stok), ilk çubuk referans günü/haftası, x ekseni yalnızca veri olan günler. Değişim sağ panelde (Rezerv bölümündeki gibi). Tooltip: net rezerv + önceki güne/haftaya göre değişim. Tarih: 1W…Tümü, varsayılan YTD; veri 2015'ten.
- Sağ panel: seçili aralık ya da tıklanan çubuk için pasta + liste: Dış varlıklar (A02) + Dış yükümlülükler (−, A11) + Kamu ve diğer döviz mevduatı (−, A13) + Bankalar döviz mevduatı (−, A14) [+ swap hariçte: Alım yönlü swap stoku (−) + Satım yönlü swap stoku (+)] = Net rezerv değişimi. Kalemler aynı günün kuruyla $'a çevrilir. Denklik A10 = A11 + A13 + A14 (kontrol edildi, ±1 bin TL). İkinci tıklama aralığa döner.
- Swap hariç (Claude önerisi, onay bekliyor): net rezerv − (TP.SWAPTEKTAR.TOTALSTOKALIMYONLU − TP.SWAPTEKTAR.TOTALSTOKSATIMYONLU), milyon $, bie_swaptektarf (TCMB taraflı swap işlemleri, iş günü, 04.01.2021'den; yurt içi piyasa swapları, merkez bankalarıyla swaplar dahil değil).
- Veri: site data/kaynak.json (fetch_evds.py); artifact scripts/artifact_loader_kaynak.js (önce son 2 yıl, eski tarih seçilince 2 yıllık parçalarla 2015'e kadar).

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
- Üstte üç kutu: son ay ithalat (kg), USD karşılığı (milyon $), TL karşılığı (milyar TL). Grafik: aylık kg çubukları (altın rengi). Altında tablo: ay, kg, ons, ons fiyatı, USD karşılığı, USD/TL, TL karşılığı. Tablo tek satır: varsayılan seçili tarih aralığının toplamı (kg, USD ve TL toplamı; ons miktarı sütunu yok; ons fiyatı = ΣUSD÷Σons, kur = ΣTL÷ΣUSD, ithalat ağırlıklı). Her ay kendi ayının aylık ortalama fiyatı ve kuruyla hesaplanıp toplanır. Grafikte bir aya tıklanınca tablo o ayı gösterir (çubuk çerçevelenir, diğerleri soluklaşmaz); aynı aya ikinci tıklama aralık toplamına döner.

### Kur bölümü — sayfa özellikleri
- Seri: TP.DK.USD.A.YTL (USD/TRY, TCMB döviz alış, günlük; sitede 1987'den). Üstte iki kutu: son kur; önceki iş gününe göre fark (büyük: bps = kur farkı × 10.000, ör. 50,5866 − 50,5531 = 335 bps; altında % ve yıllıklandırılmış %; pozitif yeşil, negatif kırmızı).
- Üstte **Kur / Yıllıklandırılmış değişim** düğmeleri tek grafiği değiştirir. Kur: USD/TRY çizgi (iş günü ekseni). Yıllıklandırılmış: her gün için kayan pencere değişiminin yıllıklandırılmış hali, çizgi, sıfır çizgisi; pencere düğmeleri 1 hafta · 1 ay · 3 ay (varsayılan 3 ay) ve Basit / Bileşik yöntem düğmeleri (varsayılan basit; Claude önerisi 3 ay + bileşik).
- Formül (Claude önerisi, onay bekliyor): günlük değişim % = (K_t ÷ K_önceki − 1) × 100; bps = (K_t − K_önceki) × 10.000 (kullanıcı tanımı); yıllıklandırılmış % = pencere değişimi % (K_t ÷ pencere başındaki ya da öncesindeki son iş günü kuru − 1) × 365 ÷ aradaki takvim günü (basit) ya da (1 + r)^(365 ÷ gün) − 1 (bileşik). Kullanıcı isteği: günlük yerine haftalık (günlük grafik kötüydü); bileşik sürüm de yanlış bulundu.
- Tarih kontrollerinin sağında küçük kutu: seçili aralığın ilk ve son iş günü arasındaki fark (bps = kur farkı × 10.000, altında %; ilk gün = başlangıç tarihindeki ya da öncesindeki son iş günü). Her iki görünümde de görünür.
- Eksen %1–%99 dilimiyle sınırlanır; dışarıda kalan değerler eksen sınırında kesilir, tooltip'te tam değer.
- Tarih: EVDS tarihleri kullanılır (TCMB kuru bir gün önce 15:30'da ilan edilir; EVDS'te uygulanacağı günün tarihini taşır). Kullanıcı ilan gününü kastedebilir.
- Tarih kontrolleri: 1W…Tümü, varsayılan YTD. "Kaynak: EVDS".

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

### Seri kataloğu — bulunan ama henüz kullanılmayan veri grupları
- **Özel sektör borçlanma senetleri** (EVDS Tüm Seriler: Parasal ve Finansal İstatistikler → Menkul Kıymet İstatistikleri (TCMB) → Genel Yönetim Dışı Sektörlerin Yurt İçi / Yurt Dışı Borçlanma Senedi İhraçları). Haftalık (Cuma, aggregation last), Eylül 2020'den.
  - Yurt içi (milyon TL): bie_yiosbayazdeg (yazılı değer/stok), bie_yiosbapiydeg (piyasa değeri), bie_yiosbavade (vade dağılımı).
  - Yurt dışı / Eurobond (milyon $): bie_ydosbayazdeg, bie_ydosbapiydeg, bie_ydosbavade (vade ve para dağılımı).
  - ÇSY (yeşil/sürdürülebilir, Eylül 2023'ten): bie_yiesgyazdeg (yurt içi, milyon TL), bie_ydesgyazdeg (yurt dışı, milyon $).
  - Yazılı değer gruplarında 80'er seri; kırılım ihraççı (finansal olmayan / finansal kuruluşlar) × elinde tutan sektör. Toplamlar: TP.YIOSBAYAZDEG.S11T, TP.YDOSBAYAZDEG.S11T. Seri listesinin tamamı kullanıcıyla henüz gözden geçirilmedi.
  - Öneri (onay bekliyor): "Özel sektör borçlanma" bölümü — toplam stok kutuları (TL, $), ihraççıya göre yığılmış çubuk, vade dağılımı.

### Açık konular
- **Rezerv kaynakları bölümü yarım kaldı:** kullanıcı 27.11.2026'da "doğru yapmadın, tekrar döneceğiz" dedi; neyin yanlış olduğu henüz konuşulmadı. Döndüğümüzde önce kullanıcının beklentisi sorulacak, sonra değişiklik yapılacak. O zamana kadar sayfaya dokunulmaz.
- Basındaki net rezerv rakamları bizimkinden ~4,8 milyar $ yüksek (yöntem yayımlanmamış). Hakan Kara ve "507" hesaplarının yöntemi araştırılacak; kullanıcı onaylamadan formül değiştirilmez.
- Bu aşamada sayfada veri yorumu yapılmaz, yalnızca görselleştirilir.
- Kur – yıllıklandırma: kullanıcı haftalık değişimin yıllıklandırılmasını istedi (uygulandı); daha da pürüzsüz istenirse aylık pencere ya da hareketli ortalama seçenekleri var.
- Altın ve Kur formülleri (Claude önerisi) henüz açıkça onaylanmadı.
