{
  // Sitenin sol menüsü. Yeni bölüm eklemek için SECTIONS listesine bir satır ekle.
  const SECTIONS = [
    { id: 'rezerv', title: 'Rezerv', href: '../rezerv/' }
  ];
  const SOON = ['Fiyatlar', 'Döviz', 'Parasal', 'Dış istatistikler'];
  const here = location.pathname.split('/').filter(Boolean);
  const nav = document.getElementById('nav');
  if (nav) {
    const brand = document.createElement('p'); brand.className = 'brand'; brand.textContent = 'EVDS Pano';
    const tag = document.createElement('p'); tag.className = 'tag'; tag.textContent = 'TCMB istatistikleri, her gün güncel';
    nav.append(brand, tag);
    for (const s of SECTIONS) {
      const a = document.createElement('a'); a.href = s.href; a.textContent = s.title;
      if (here.includes(s.id)) a.setAttribute('aria-current', 'page');
      nav.append(a);
    }
    for (const t of SOON) { const sp = document.createElement('span'); sp.className = 'soon'; sp.textContent = t + ' · yakında'; nav.append(sp); }
  }
}
