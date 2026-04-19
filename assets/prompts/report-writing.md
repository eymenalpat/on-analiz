# Rapor Yazım Promptu — Bölüm Bazında

Checkpoint #2 onayından sonra her rapor bölümü ayrı prompt çağrısıyla üretilir. Her çağrının girdisi:
1. `language-rules.md` içeriği (sistem prompta enjekte)
2. `raw-data.json` (ilgili bölümün verisi)
3. `glossary.json` (terim listesi, referans)
4. Bölüm-specific talimat (aşağıda)

Çıktı: sadece o bölümün **HTML parçası** (section içeriği — `<section>` dış sarıcı yazma, template'te var).

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
