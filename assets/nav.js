{
  // Sitenin sol menüsü. Yeni bölüm eklemek için SECTIONS listesine bir satır ekle.
  const SECTIONS = [
    { id: 'rezerv', title: 'Rezerv', href: '../rezerv/' },
    { id: 'kaynak', title: 'Rezerv kaynakları', href: '../kaynak/' },
    { id: 'swap', title: 'Swap', href: '../swap/' },
    { id: 'swap-bist', title: 'BIST Swap Piyasası', href: '../swap-bist/', sub: true },
    { id: 'likidite', title: 'Likidite', href: '../likidite/' },
    { id: 'cek', title: 'Çek', href: '../cek/' },
    { id: 'altin', title: 'Altın', href: '../altin/' },
    { id: 'kur', title: 'Kur', href: '../kur/' }
  ];
  const SOON = ['Fiyatlar', 'Parasal', 'Dış istatistikler'];
  const here = location.pathname.split('/').filter(Boolean);
  const nav = document.getElementById('nav');
  if (nav) {
    const brand = document.createElement('p'); brand.className = 'brand'; brand.textContent = 'EVDS Pano';
    const tag = document.createElement('p'); tag.className = 'tag'; tag.textContent = 'TCMB istatistikleri, her gün güncel';
    nav.append(brand, tag);
    for (const s of SECTIONS) {
      const a = document.createElement('a'); a.href = s.href; a.textContent = s.sub ? '· ' + s.title : s.title;
      if (s.sub) { a.style.paddingLeft = '26px'; a.style.fontSize = '14px'; a.style.minHeight = '36px'; a.style.paddingTop = '7px'; a.style.paddingBottom = '7px'; }
      if (here.includes(s.id)) a.setAttribute('aria-current', 'page');
      nav.append(a);
    }
    for (const t of SOON) { const sp = document.createElement('span'); sp.className = 'soon'; sp.textContent = t + ' · yakında'; nav.append(sp); }
  }
}
