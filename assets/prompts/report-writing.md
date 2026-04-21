# Rapor Yazım Promptu — Bölüm Bazında

Checkpoint #2 onayından sonra her rapor bölümü ayrı prompt çağrısıyla üretilir. Her çağrının girdisi:
1. `language-rules.md` içeriği (sistem prompta enjekte)
2. `raw-data.json` (ilgili bölümün verisi)
3. `glossary.json` (terim listesi, referans)
4. Aktif `odak` değeri (genel / keyword / backlink / rakip / teknik)
5. Bölüm-specific talimat (aşağıda)

Çıktı: sadece o bölümün **HTML parçası** (section içeriği — `<section>` dış sarıcı yazma, template'te var).

---

## Odak Bazlı Derinlik

Her bölümün bu promptta tanımlı "standart" davranışı `odak=genel` içindir. Diğer odaklarda:

- **●  Derin (primary):** Bölüm baseline'dan 2-3 alt başlığa genişler. SVG görsel zenginleşir. Yorum 200+ kelime. Alt başlık şablonları aşağıda bölüm bazında verilmiştir.
- **○  Normal (secondary):** Standart yazım, aşağıdaki talimatla birebir.
- **◐  Özet (minimal):** Bölüm 1 paragrafa + tek scorecard/tek istatistiğe indirgenir. İlk cümle "Bu raporun odağı [odak] olduğundan bu bölüm bağlam için özetlenmiştir." olur. SVG/tablo yok.
- **—  Atla (skip):** Bölüm HTML üretilmez, section tamamen boş string döner. Template'te slot `""` ile doldurulur, sidebar nav'dan ilgili `<li>` silinir.

Derinlik matrisi `SKILL.md → Rapor Odağı Sistemi → 10.2` altındadır. Claude her bölüm yazımına başlamadan önce o bölümün aktif odak için hangi harfe denk geldiğini bu matristen okur.

### Primary (●) için alt başlık şablonları

#### Bölüm 3 — Teknik SEO (odak=teknik)

**Veri kaynağı:** `raw-data.teknik.veri_kaynagi` = `ahrefs_site_audit` veya `direct_crawl`.

- **Site Audit kaynaklıysa:** `raw-data.teknik.issues[]` birincil veri. Her issue kategori + severity + affected_pages_count ile gelir. Öncelik sırası: **critical > high > medium > low**. Bölüm başında bir veri kaynağı rozet'i: `<span class="source-badge">Kaynak: Ahrefs Site Audit · Son crawl: {son_crawl}</span>`.
- **Direct crawl fallback ise:** `raw-data.teknik.pages[]` + `indexability_summary` kullanılır. Veri kaynağı rozet'i: `<span class="source-badge partial">Kaynak: Direct crawl (Site Audit projesi yok)</span>`.

**Rakip verisi bu bölümde yoktur.** Teknik audit odağı rakip kıyas yapmaz — sadece markanın teknik durumunu raporlar.

**Alt başlıklar (Site Audit versiyonu):**
1. **Sağlık Özeti** — Issue sayısı scorecard'ı (critical/high/medium/low) + toplam etkilenen sayfa sayısı (SVG bar)
2. **Crawlability & Indexability** — `indexability_summary`'den: noindex, canonical mismatch, robots-blocked, redirect chain sayıları; kritik issue örnekleri finding-card
3. **Core Web Vitals** — `cwv.lcp/inp/cls/tbt` mobile + desktop; Good/Needs Improvement/Poor threshold çizgili SVG bar
4. **On-page Temelleri** — title/description/h1 ilgili Site Audit issue kategorileri (missing title, long title, duplicate h1 vs.): affected_pages sayısı + top 3 örnek URL
5. **Yapısal İşaretleme** — `schema_coverage` dict'inden @type dağılımı + JSON-LD error issue'ları
6. **İç Linkleme & Derinlik** — `page-explorer` internal_linkrank + depth dağılımı; "derin ama internal link almayan" sayfalar
7. **Bozuk Linkler & Redirect'ler** — `bozuk_linkler` listesi top 10 + 3xx zinciri uzun olan sayfalar

Her alt başlık: kısa bulgu + finding-card + öneri cümlesi. Finding-card içeriği Site Audit'in kendi mesajından doğrudan alınabilir (Türkçe'ye çevirerek, language-rules'a uyarak).

**Direct crawl versiyonu** için alt başlık 6-7 atlanır (veri yok), Site Audit score scorecard'ı yerine manuel hesaplanan kısa bulgu sayısı gösterilir. Bölüm başında belirgin uyarı: *"Bu rapor Ahrefs Site Audit projesi bulunmadığı için sınırlı teknik bulgu içerir. Tam kapsamlı teknik audit için Ahrefs Site Audit projesi kurulması önerilir."*

#### Bölüm 4 — Keyword Evreni (odak=keyword)
1. **Pozisyon dağılımı** (mevcut SVG) + trend
2. **Intent dağılımı** — bilgilendirici / ticari / navigasyonel / işlemsel
3. **Tematik kümeler** — top 300 keyword'den otomatik cluster (top 5-8 küme)
4. **Yüksek potansiyelli top 30 tablosu** (mevcut top 20 yerine)
5. **Düşüşte olan keyword'ler** — son 3 ay -5+ pozisyon kaybı

#### Bölüm 5 — Fırsat Keyword (odak=keyword veya rakip)
- Standart tabloya ek: **Cluster başlığı**, **Rakip ortalama pozisyon**, **Tahmini content effort (düşük/orta/yüksek)**, **SERP özellikleri**
- Kategori pie chart'a ek: intent × effort matrisi (2x2 SVG)

#### Bölüm 6 — SERP Analizi (odak=keyword)
- Standart 5 kart yerine **top 10 keyword kart**
- Her kartta ek: SERP özellik sayısı, AI Overview varlığı, domain çeşitliliği skoru, organic CTR tahmini

#### Bölüm 7 — Rakip Kıyası (odak=rakip)
1. **Çok boyutlu radar** (mevcut)
2. **Keyword overlap matrisi** — N×N Jaccard benzerlik (SVG heatmap)
3. **Content gap** — rakiplerde ortak, markada yok (top 20 tema)
4. **Backlink overlap** — ortak referring domain'ler, markanın erişmediği otoritelere sahip RD listesi
5. **SERP co-occurrence** — top 20 keyword'de birlikte görünme sıklığı
6. **Büyüme trendi** — son 6 ay traffic delta karşılaştırması (SVG line)

#### Bölüm 9 — Backlink Snapshot (odak=backlink)
1. **DR dağılımı** — RD'lerin DR tier histogramı (SVG)
2. **Anchor kompozisyonu** — branded / exact / partial / generic / naked URL pie
3. **Yeni & kayıp linkler** — son 90 gün delta (SVG bar)
4. **Bozuk backlinks** — 404/410 dönen URL'leri hedefleyen backlink'ler (yönlendirme fırsatı)
5. **Link intersect** — rakiplerde var markada yok otoriter domain'ler (top 30 tablo)
6. **Toksik sinyal taraması** — nazik yorum (yüksek risk yoksa pas geç)

#### Bölüm 10 — Aksiyon Planı (her odakta)
- `odak=keyword` → Faz 1 = içerik briefleri + mevcut sayfa optimize; Faz 2 = yeni cluster sayfası; Faz 3 = izleme
- `odak=backlink` → Faz 1 = bozuk link kurtarma + unlinked mention; Faz 2 = link intersect outreach; Faz 3 = tier-1 PR
- `odak=rakip` → Faz 1 = content gap kapatma; Faz 2 = SERP overlap optimize; Faz 3 = rakip izleme panosu
- `odak=teknik` → Faz 1 = critical teknik fix; Faz 2 = CWV iyileştirme; Faz 3 = schema + i18n

### Minimal (◐) şablonu

1-2 cümlelik giriş + tek `.scorecard` veya tek satırlık istatistik + bir cümle "tam derinlik için `odak=X` ile rapor alınabilir" yönlendirmesi.

```html
<p><em>Bu rapor {odak} odağındadır; {bölüm_adı} bölümü bağlam için özetlenmiştir.</em></p>
<div class="scorecard mini">
  <div class="label">{tek_etiket}</div>
  <div class="value">{tek_değer}</div>
  <div class="trend">{tek_yorum}</div>
</div>
```

### Skip (—) davranışı

Bölüm fonksiyonu boş string döner. Ana renderer `sections[key] = ""` olarak kaydeder ve nav'dan `<li><a href="#{slot_id}">` satırını string replace ile siler.

---

## Bölüm 1: Yönetici Özeti

**Girdi:** tüm raw-data özeti
**Uzunluk:** 3 paragraf, toplam 180-250 kelime
**Yapı:**
- Paragraf 1: Mevcut durum snapshot'ı (domain, sektör, marka, rakip pozisyonu). Rakamları "~" ile ver.
- Paragraf 2: Öne çıkan 3-5 fırsat alanı — bullet değil akıcı anlatım.
- Paragraf 3: Önerilen odak ve sonraki adım. Vaatsiz dil.

**HTML:**
```html
<p>...</p>
<p>...</p>
<p>...</p>
<div class="callout">
  <strong>Önerilen odak:</strong> [bir cümle]
</div>
```

---

## Bölüm 2: Temel Metrikler

**Girdi:** `raw-data.metrikler` + `raw-data.rakipler[].metrikler`
**Yapı:** 4 scorecard'lı `.kpi-strip`
- Scorecard 1: DR (marka + rakip ort.)
- Scorecard 2: Organic Traffic (aylık, rakip ort.)
- Scorecard 3: Organic Keywords (toplam, ilk 10'daki sayı)
- Scorecard 4: Referring Domains (toplam, son 3 ay delta)

**HTML:**
```html
<div class="kpi-strip">
  <div class="scorecard">
    <div class="label"><span class="term" data-term="DR">DR</span></div>
    <div class="value">18</div>
    <div class="trend">Rakip ort. ~34</div>
  </div>
  <!-- ... 3 tane daha -->
</div>
<div class="callout">
  Metriklerin [kısa yorum — 1-2 cümle].
</div>
```

---

## Bölüm 3: Teknik SEO Durumu

**Girdi:** `raw-data.teknik_bulgular` (listesi: finding per sayfa/element) + checklist eşlemesi
**Yapı:**
- Üstte basit skor çubuğu (SVG): "Teknik SEO Puanı: X/100"
- Altında 3 rozetli özet: "N öncelikli / M orta / K takip edilebilir"
- Altında top 5-8 finding-card (öncelik sırasına göre)

**Finding card örneği:**
```html
<div class="finding-card priority-critical">
  <div class="priority-badge critical">Öncelikli</div>
  <h3>Ana Sayfa <span class="term" data-term="H1">H1</span> Konumlandırması</h3>
  <p>Ana sayfada H1 etiketinin konumlandırılmasında ele alınabilecek bir nokta öne çıkmaktadır. ...</p>
  <p><strong>Önerilen yaklaşım:</strong> ...</p>
</div>
```

**Önemli:** "Hata" demek yerine "gözden geçirilebilir alan". Bkz: language-rules.md rozet eşlemesi.

---

## Bölüm 4: Organik Keyword Evreni

**Girdi:** `raw-data.organic_keywords`
**Yapı:**
- Üstte bar chart (SVG): pozisyon dağılımı (1-3 / 4-10 / 11-20 / 21+)
- Altında top 20 keyword'lik tablo: keyword, pozisyon, hacim, potansiyel trafik, hedef sayfa
- En altında 1-2 cümle yorum

**HTML:** renderBarChart inline SVG helper'ı + `.comparison-table`

---

## Bölüm 5: Fırsat Keyword'leri

**Girdi:** `raw-data.opportunity_keywords`
**Yapı:**
- Üstte tek cümle: "Rakiplerde sıralama alan, henüz markada öne çıkmayan ~N keyword belirlenmiştir"
- Tablo: keyword, mevcut pozisyon (varsa), KD, hacim, potansiyel trafik, öneri
- Kategori dağılımı SVG pie/bar (bilgilendirici/ticari/işlem intent)

---

## Bölüm 6: SERP Analizi

**Girdi:** `raw-data.serp_snapshots` (top 5 öncelikli keyword için)
**Yapı:** her keyword için mini kart:
```html
<div class="finding-card">
  <h3>"kelime örneği" — ~3.200 arama/ay</h3>
  <p>İlk 5'te: rakip-a, rakip-b, [3 başka site]. SERP özellikleri: PAA (5 soru), <span class="term" data-term="AI Overview">AI Overview</span>, video karuseli.</p>
  <p><strong>Değerlendirme:</strong> ...</p>
</div>
```

---

## Bölüm 7: Rakip Kıyası

**Girdi:** tüm rakiplerin metrikleri
**Yapı:**
- Üstte radar chart (SVG): 5-6 boyut (DR, Traffic, Keywords, Backlinks, Content Volume, GEO Visibility)
- Altında karşılaştırma tablosu

---

## Bölüm 8: GEO / AEO Durumu (kapsama GEO dahilse)

**Girdi:** `raw-data.geo_durumu` + GEO checklist eşlemesi
**Yapı:**
- AI platform scorecard'ları (ChatGPT / Perplexity / Gemini / AI Overview)
- Checklist tamamlanma oranı (SVG bar): "X/N task uygulanmış"
- Öncelikli GEO task'ları (finding-card formatında)

**Kapsama GEO yoksa:** bu bölüm tamamen atlanır, sidebar nav'ından da kaldırılır.

---

## Bölüm 9: İçerik ve Backlink Snapshot

**Girdi:** `raw-data.content_gap` + `raw-data.backlink_profile`
**Yapı:**
- İçerik: rakiplerde var markada yok tematik alan listesi (3-5 madde)
- Backlink: anchor dağılımı özeti + RD tier dağılımı + nazik toxic signal yorumu (varsa)

---

## Bölüm 10: Aksiyon Planı

**Girdi:** tüm bölümlerden çıkan aksiyon maddeleri + checklist task'ları
**Yapı:** Fazlı (Faz 1 / Faz 2 / Faz 3) task-card grid'i
- Pitch modu: 8-12 task
- Onboarding modu: 20-30 task

**Task card:**
```html
<div class="task-card">
  <div><strong>Title ve Meta Description optimizasyonu</strong> — öncelikli 20 sayfa</div>
  <div class="priority-badge high">Yüksek</div>
  <div><small>~1 hafta</small></div>
  <div><small>Potansiyel etki: orta-yüksek</small></div>
</div>
```

---

## Bölüm 11: Yöntem ve Notlar

**Yapı:** Kısa meta bölüm:
- Kullanılan veri kaynakları (Ahrefs, DataForSEO, site denetimi)
- Rapor tarihi
- Veri eksikleri (varsa)
- "Bu rapor ön analiz niteliğindedir; detaylandırma sonraki aşamalarda yapılandırılabilir."

---

## Genel Kurallar (her bölümde)

1. Section sarıcısını YAZMA, template'te var (`{{YONETICI_OZETI}}` gibi slot'lara girecek).
2. Sadece bölüm içeriğini üret.
3. Teknik terimleri `.term` span ile işaretle.
4. Türkçe karakter koruma.
5. Self-check: bölüm yazımı sonrası yasaklı kelime taraması.
6. Veri eksiği varsa `<span class="partial-data-badge">⚑ kısmi veri</span>` ile işaretle.
