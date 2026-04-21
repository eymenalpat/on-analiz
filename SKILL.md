---
name: on-analiz
description: Yeni müşteri ön analizi — marka (+ isteğe bağlı rakip) alıp odağa göre tek bir veri kaynağından çalışır. Teknik → Ahrefs Site Audit MCP. Keyword → keywords-explorer + gsc. Backlink → Site Explorer backlink ailesi. Rakip → organic-competitors. Genel → geniş set. Her odakta sadece kendi tool ailesi çağrılır; diğerleri çağrılmaz. Pitch/onboarding modları, Inbound brand kit'li HTML rapor, Türkçe çıktı. Triggers: /on-analiz, ön analiz, yeni müşteri analizi, domain denetimi, SEO+GEO denetimi, keyword research raporu, backlink profil raporu, rakip analiz raporu, teknik audit raporu, Ahrefs Site Audit raporu.
version: 1.3.0
---

# /on-analiz — Yeni Müşteri Ön Analizi

**Announce at start:** "I'm using the on-analiz skill to prepare the new customer preliminary analysis."

## Çalışma Akışı Genel Bakış

1. **Setup kontrolü** — `.env` var mı? Yoksa setup wizard yönlendir.
2. **Input formu** — AskUserQuestion ile 8 alan (7 zorunlu + 5 opsiyonel).
3. **Checkpoint #1: Scope onayı** — domain erişim, rakip önerisi, checklist eşleme, süre tahmini.
4. **Veri toplama** — Ahrefs MCP + DataForSEO (Bash curl) + WebFetch paralel. raw-data.json biriktirilir.
5. **Checkpoint #2: Bulgu özeti onayı** — finding-synthesis.md prompt çalışır.
6. **Rapor üretimi** — report-writing.md'ye göre bölüm bölüm HTML yazılır, template'e enjekte edilir.
7. **Checkpoint #3: Rapor draft onayı** — kullanıcı önizleme alır, "yaz + deploy / tekrar yaz / iptal".
8. **Local save + opsiyonel Railway deploy** — HTML yazılır, RAILWAY_TOKEN varsa deploy.py çağrılır.

**Dizin yapısı:** `./cikti/{marka-slug}/{YYYY-MM-DD}/` altında `raw-data.json`, `findings.json`, `rapor.html`, `meta.json`.

**Modlar:**
- `pitch` (10-15 dk): 3 rakip, top 20 keyword, 5 WebFetch, 100 backlink örneklem, 8-12 aksiyon
- `onboarding` (45-60 dk): 5 rakip, top 100 keyword, 20 WebFetch, full backlink, CWV ölçümü, 20-30 aksiyon

**Kapsam:** `seo` / `geo` / `seo+geo` (kullanıcı seçer).

**Odak:** `genel` / `keyword` / `backlink` / `rakip` / `teknik` — raporun hangi eksende derinleşeceğini belirler. Detay için aşağıda "Rapor Odağı Sistemi" bölümüne bakılır.

---

## Yardımcı Dosyalar (her çağrıda okunmalı)

- `assets/prompts/language-rules.md` — dil kuralları, self-check
- `assets/prompts/sector-detection.md` — Checkpoint #1 sektör doğrulama
- `assets/prompts/finding-synthesis.md` — Checkpoint #2 özet
- `assets/prompts/report-writing.md` — bölüm bazında HTML yazımı
- `assets/checklists/*.json` — sektöre göre seçilir
- `assets/glossary.json` — tooltip terim listesi
- `assets/brand.css` — template içine enjekte edilir
- `assets/report-template.html` — `{{SLOT}}` placeholder'lı iskelet

---

## Argüman Parsing

Skill iki şekilde tetiklenir:

1. **Tek komut:** `/on-analiz` → AskUserQuestion ile 8 alan sorulur.
2. **Flagged:**
   - `--setup` → setup wizard çalışır (scripts/setup.py)
   - `--setup --reset` → mevcut .env silinir, yeniden kurulur
   - `--resume <marka-slug>` → en son `cikti/<marka-slug>/` run'ını devam ettir
   - `--refresh-report <marka-slug>` → ham veri kullanılır, sadece HTML yeniden üretilir

**Kısa form:** `/on-analiz ornekmarka.com.tr vs rakip-a.com.tr,rakip-b.com mod=pitch kapsam=seo+geo odak=genel sektor=lokal ulke=TR dil=tr`

`odak` parametresi verilmezse Adım 2'de sorulur. Değerleri: `genel` (varsayılan davranış), `keyword`, `backlink`, `rakip`, `teknik`.

---

## Adım 1: Setup Kontrolü (Claude-native, Python gerektirmez)

Claude önce `.env` dosyasının varlığını kontrol eder. **Hiç terminal komutu çalıştırmaz; tüm işlem AskUserQuestion + Write + Bash tool ile yapılır.**

### 1.1 .env kontrolü

```bash
test -f ~/.claude/skills/on-analiz/.env && echo exists || echo missing
```

Eğer `missing` dönerse, setup akışına gir. `exists` dönerse Adım 2'ye geç.

### 1.2 API key'leri AskUserQuestion ile iste

Claude şu mesajı verir ve AskUserQuestion tool'unu kullanır:

> "İlk kurulumda gerekli API key'lerini sorayım. DataForSEO zorunlu (SERP verisi için), PageSpeed ve Railway opsiyonel. Her birini tek tek soracağım — boş bırakabilirsin."

Sorular (ayrı mesajlarda, tek tek):
1. "DataForSEO Login?" — serbest metin (Other seçeneği ile)
2. "DataForSEO Password?" — serbest metin
3. "PageSpeed API Key? (opsiyonel, onboarding modunda CWV için)" — boş geçilebilir
4. "Railway Token? (opsiyonel, public URL deploy için)" — boş geçilebilir
5. "Railway Project ID? (Railway kullanacaksan)" — boş geçilebilir

### 1.3 .env dosyasını yaz

Claude Write tool ile `~/.claude/skills/on-analiz/.env` dosyasını oluşturur:

```
DATAFORSEO_LOGIN=<kullanıcının yazdığı>
DATAFORSEO_PASSWORD=<kullanıcının yazdığı>
PAGESPEED_API_KEY=<opsiyonel>
RAILWAY_TOKEN=<opsiyonel>
RAILWAY_PROJECT_ID=<opsiyonel>
DEFAULT_LANG=tr
OUTPUT_DIR=./cikti
```

Ardından Bash ile dosya iznini güvenli hale getirir:
```bash
chmod 600 ~/.claude/skills/on-analiz/.env
```

### 1.4 .env'den değerleri yükle

Her API çağrısı öncesi değerler shell ortamına yüklenir:
```bash
set -a && source ~/.claude/skills/on-analiz/.env && set +a
```
Böylece `$DATAFORSEO_LOGIN`, `$RAILWAY_TOKEN` vb. Bash komutlarında kullanılabilir hale gelir.

### 1.5 Key güncelleme

Kullanıcı `/on-analiz --setup` derse: `.env` dosyasını oku, mevcut değerleri göster (mask'lı), değiştirmek istediklerini sor, yeniden yaz.

---

## Adım 2: Input Formu

**Odak önce sorulur** — rakip alanının zorunlu olup olmadığını odak belirler. AskUserQuestion max 4 seçenek sınırı nedeniyle form birkaç mesajda alınır:

**Soru 1 (tek soru):** odak (5 seçenek → 2×3 split: "Genel / Özelleştirilmiş" sonra 4 spesifik)

**Soru 2 (batch, 4 alan):** marka, (rakip — sadece odak ∈ {genel, rakip} ise), sektör, ülke

**Soru 3 (batch, 3-4 alan):** dil, mod, kapsam, (opsiyonel: öncelikli kategoriler varsa)

Teknik / keyword / backlink odaklarında **rakip alanı sorulmaz** — çünkü rakip verisi kullanılmayacak.

### Zorunlu alan seti:

AskUserQuestion `questions` dizisi:
```
[
  {
    question: "Marka domain'i nedir?",
    header: "Marka",
    multiSelect: false,
    options: [
      { label: "Yaz", description: "Örnek: ornekmarka.com.tr" }
    ]
  },
  {
    question: "Rakip domainleri (virgülle ayır, 3-5 adet)?",
    header: "Rakipler",
    multiSelect: false,
    options: [
      { label: "Yaz", description: "Örnek: rakip-a.com.tr, rakip-b.com, rakip-c.com.tr" }
    ]
  },
  {
    question: "Sektör?",
    header: "Sektör",
    multiSelect: false,
    options: [
      { label: "E-ticaret", description: "Ürün satan site" },
      { label: "Hizmet", description: "B2B/B2C hizmet sağlayıcı" },
      { label: "Lokal", description: "Restoran/mağaza/klinik" },
      { label: "B2B SaaS", description: "Yazılım ürünü" }
    ]
  },
  { ... ulke ... },
  { ... dil ... },
  { ... mod: pitch / onboarding ... },
  { ... kapsam: seo / geo / ikisi ... },
  {
    question: "Rapor odağı?",
    header: "Odak",
    multiSelect: false,
    options: [
      { label: "Genel",             description: "Tüm bölümler dengeli — klasik ön analiz" },
      { label: "Keyword Research",  description: "Keyword evreni, fırsatlar, SERP derinleşir; diğerleri özet" },
      { label: "Backlink Profili",  description: "Backlink, referring domains, anchor, broken link derinleşir" },
      { label: "Rakip Analizi",     description: "Rakip kıyası, keyword gap, content gap, SERP overlap derinleşir" },
      { label: "Teknik Audit",      description: "Teknik bulgular, CWV, schema, crawl, indexability derinleşir" }
    ]
  }
]
```

Yukarıdaki "Yaz" seçenekleri için kullanıcı "Other" seçerek serbest metin girer.

**Odak seçimi Checkpoint #1, veri toplama ve rapor üretimini doğrudan etkiler** — detay "Rapor Odağı Sistemi" bölümünde.

### Opsiyonel alanlar (ayrı mesaj, atlanabilir):

Mod=onboarding ise sorulur. Pitch'te atlanır.

- Öncelikli kategoriler
- Marka brief'i
- Hedef kitle
- Bilinen dert noktaları
- GSC erişimi (Var/Yok)
- Ahrefs projesi (Var/Yok)

---

## Adım 3: Checkpoint #1 — Scope Onayı

### 3.1 Domain erişim kontrolü

Her domain için WebFetch HEAD request:
```
for domain in [marka_domain] + rakip_domains:
    r = WebFetch(f"https://{domain}", "HEAD request to verify reachability")
    if r.status >= 400:
        flag(domain, 'unreachable')
```

Marka erişilemezse → **dur**, kullanıcıya sor. Rakip erişilemezse → notla devam.

### 3.2 Sektör doğrulama

WebFetch ile marka anasayfasından ilk 5000 karakter çekilir. `sector-detection.md` prompt'u Claude'un kendisine uygulanır. Çıktı JSON:
```
{
  "sektor": "e-ticaret",
  "sektor_kullanici_secimi_ile_uyumlu": true,
  "aktif_checklist_dosyalari": ["seo-ecommerce.json", "geo-eticaret.json"],
  "uyum_notu": "..."
}
```

### 3.3 Rakip önerisi — **sadece odak ∈ {genel, rakip}**

Teknik / keyword / backlink odaklarında bu adım tamamen atlanır. Rakip çağrısı yapılmaz.

Genel veya rakip odağında: `mcp__ahrefs__site-explorer-organic-competitors` marka domain'i için çağrılır. Kullanıcının verdiği rakiplerle karşılaştırılır. Ahrefs'in verdiği ilk 5'te olup kullanıcı listesinde olmayan varsa:
> "Ahrefs'in önerdiği güçlü rakipler: X, Y. Listeye eklemek ister misin?"

### 3.4 Süre ve tool call tahmini

**Odak = genel:**
| Mod | Rakip | Ahrefs call | DataForSEO call | WebFetch | Toplam |
|---|---|---|---|---|---|
| pitch | 3 | 4 + 9 | 20 | 5 + 2 | ~40 / 10-15 dk |
| onboarding | 5 | 4 + 15 | 100 | 20 + 2 | ~140 / 45-60 dk |

**Odak = teknik:**
| Mod | Site Audit call | WebFetch fallback | PageSpeed | Toplam |
|---|---|---|---|---|
| pitch | projects + issues + page-explorer + 5×page-content = ~8 | yok (Site Audit varsa) | 1 | ~10 / 8-12 dk |
| onboarding | projects + issues + page-explorer + 20×page-content = ~23 | yok (Site Audit varsa) | 2 | ~25 / 20-30 dk |
| onboarding + fallback | — | 60 | 2 | ~62 / 40-55 dk |

**Odak = keyword:**
| Mod | Ahrefs call | DataForSEO call | Toplam |
|---|---|---|---|
| pitch | organic-keywords 50 + keywords-explorer 5 = ~8 | 40 | ~50 / 10-15 dk |
| onboarding | organic-keywords 300 + keywords-explorer 20 = ~25 | 200 | ~225 / 45-60 dk |

**Odak = backlink:**
| Mod | Ahrefs call | Toplam |
|---|---|---|
| pitch | 6 (stats + RD50 + anchors + all-BL 100 + broken + linked-anchors) | ~7 / 8-12 dk |
| onboarding | 9 (stats + RD300 + anchors full + all-BL 500 + broken + linked-anchors + linked-domains) | ~10 / 20-30 dk |

**Odak = rakip:**
| Mod | Ahrefs call | Toplam |
|---|---|---|
| pitch | marka 4 + 3 rakip × 5 = 19 | ~25 / 15-20 dk |
| onboarding | marka 4 + 5 rakip × 5 = 29 | ~40 / 40-55 dk |

### 3.4.1 Odak özeti (her zaman göster)

Scope özetine odak satırı eklenir:
> "Odak: **{odak}** — {1 cümle: bu odağın nereleri derinleştirip nereleri özetleyeceği}. Tahmini süre ve call sayısı yukarıdaki tabloda odağa göre revize edildi."

Call sayısı tahmini odağa göre farklıdır — "Rapor Odağı Sistemi → 10.3" tablosundan türetilir.

### 3.5 Checkpoint #1 onay sorusu

AskUserQuestion:
```
[{
  question: "Scope onayı — devam edelim mi?",
  header: "Scope",
  options: [
    { label: "Evet, başla", description: "Veri toplama başlar." },
    { label: "Rakip listesini düzelt", description: "Önceki adıma dön." },
    { label: "Sektörü değiştir", description: "Önceki adıma dön." },
    { label: "İptal", description: "Şimdilik durdur." }
  ]
}]
```

---

## Adım 4: Veri Toplama

Çıktı dizinini oluştur: `./cikti/{marka-slug}/{YYYY-MM-DD}/`
- slug: marka-domain'den `.` ve `/` kaldırılır, küçük harf

**Odak gating:** Aşağıdaki çağrı listesi `odak=genel` için baseline'dır. Diğer odaklar için çağrı genişler/daralır — bkz. **"Rapor Odağı Sistemi → 10.3 Veri toplama deltaları"**. Her odak, N (top keyword sayısı), WebFetch sayfa sayısı ve ek tool call'ları farklı şekilde ölçekler. Veri toplama başlatmadan önce Claude aktif odağa göre çağrı listesini finalize eder ve Checkpoint #1'de kullanıcıya gösterir.

### 4.1 Marka için Ahrefs çağrıları (paralel batch, tek mesaj)

Aşağıdaki tool'lar **aynı mesajda** çağrılır:
- `mcp__ahrefs__site-explorer-metrics` (marka)
- `mcp__ahrefs__site-explorer-domain-rating` (marka)
- `mcp__ahrefs__site-explorer-top-pages` (marka)
- `mcp__ahrefs__site-explorer-organic-keywords` (marka, top N)
  - pitch: N=20, onboarding: N=100
- `mcp__ahrefs__site-explorer-organic-competitors` (marka)
- `mcp__ahrefs__site-explorer-backlinks-stats` (marka)
- `mcp__ahrefs__site-explorer-anchors` (marka)
- `mcp__ahrefs__site-explorer-referring-domains` (marka)

### 4.2 Her rakip için (paralel batch, tek mesaj)

Her rakip için 3 paralel call:
- site-explorer-metrics
- site-explorer-top-pages
- site-explorer-organic-keywords (top 20)

Yani 3 rakip × 3 = 9 paralel call.

### 4.3 WebFetch — site crawl

Paralel WebFetch:
- `https://{marka}` — anasayfa
- `https://{marka}/robots.txt`
- `https://{marka}/sitemap.xml`
- `https://{marka}/llms.txt`
- + mod=pitch: top 4 sayfa (top_pages'ten); onboarding: top 19 sayfa
- Her rakip için anasayfa (kısa crawl)

### 4.4 DataForSEO SERP (Bash curl)

DATAFORSEO_LOGIN ve DATAFORSEO_PASSWORD env'den gelir. Top keyword'ler için SERP overview:
```bash
curl -s -u "$DATAFORSEO_LOGIN:$DATAFORSEO_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '[{"keyword":"KELIME","location_code":2792,"language_code":"tr","depth":20}]' \
  https://api.dataforseo.com/v3/serp/google/organic/live/advanced
```
(location_code 2792 = Turkey, değiştirilebilir)

Pitch: top 20 keyword × 1 call (batch destekler mi? yok, tek tek). Onboarding: top 100.

### 4.5 PageSpeed (opsiyonel, onboarding modunda)

```bash
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://{marka}&key=$PAGESPEED_API_KEY&strategy=mobile"
```

### 4.6 raw-data.json biriktirme

Her tool call sonucu `raw-data.json` içinde ilgili key'e yazılır:
```json
{
  "meta": { "marka": "...", "tarih": "...", "mod": "...", "kapsam": "..." },
  "marka_metrikler": { ... },
  "marka_top_pages": [ ... ],
  "marka_organic_keywords": [ ... ],
  "marka_backlinks": { ... },
  "rakipler": { "rakip-a.com.tr": { ... }, "rakip-b.com": { ... } },
  "opportunity_keywords": [ ... ],
  "serp_snapshots": { "kelime-1": { ... } },
  "teknik_bulgular": [ ... ],
  "cwv": { ... },
  "veri_eksikleri": [ { "kaynak": "rakip-c robots", "neden": "403" } ]
}
```

### 4.7 opportunity_keywords hesaplama

Rakip keyword'leri + marka keyword'leri set-diff:
```
for each rakip:
    rakip_kw_set = set of (keyword, url) from rakip_organic_keywords
    marka_kw_set = set of keywords from marka_organic_keywords
    opportunity = rakip_kw_set - marka_kw_set
    filter: position <= 30 (rakip ilk 30'da), volume >= 100
```
Top 30-50 fırsat keyword seçilir.

### 4.8 Teknik bulgular hesaplama

WebFetch ile çekilen sayfaların HTML'ine şu checkler:
- `<title>` var mı, uzunluğu 30-60 karakter mi, dup mu?
- `<meta name="description">` var mı, uzunluğu 120-160 mı?
- `<h1>` kaç tane? İdeal: 1.
- `<link rel="canonical">` var mı, self-referencing mi?
- `<meta name="robots">` noindex içeriyor mu?
- JSON-LD `<script type="application/ld+json">` var mı, hangi @type'lar?
- `robots.txt` içerik — Disallow path'ler?
- `sitemap.xml` erişilebilir + valid XML mi?
- `llms.txt` var mı?

Her bulgu:
```json
{
  "category": "title | meta | h1 | canonical | schema | robots | sitemap",
  "page": "URL",
  "severity": "critical | high | medium | low",
  "detail": "açıklama"
}
```

Severity mapping:
- Title yok / H1 yok → critical
- Meta description eksik / dup title → high
- Canonical self-ref değil / schema yok → medium
- llms.txt yok → low

---

## Adım 5: Checkpoint #2 — Bulgu Özeti Onayı

`finding-synthesis.md` prompt'u Claude'un kendisine uygulanır. Girdi: `raw-data.json`. Çıktı: kullanıcıya gösterilecek Markdown özet.

Üretilen `findings.json` olarak kaydedilir:
```json
{
  "metrikler_ozet": "Marka DR 18 (rakip ort. ~34)...",
  "teknik_ozet": "5 öncelikli, 12 orta, 8 takip edilebilir",
  "keyword_firsatlar_ozet": "87 rakip-özel keyword, ~12K/ay potansiyel",
  "oncelikli_bulgular": [ ... 5 madde ... ],
  "veri_eksikleri": [ ... ]
}
```

Kullanıcıya Markdown preview gösterilir + AskUserQuestion:
```
[{
  question: "Bulgu özeti — raporu bu yönde yazalım mı?",
  header: "Bulgu",
  options: [
    { label: "Rapora geç", description: "HTML üretilecek." },
    { label: "Ek bulgu ekle", description: "Serbest metin input'u alınır, findings'e eklenir." },
    { label: "Şu bölümü tekrar tara", description: "Belirli bir kaynağın verisi yenilenir." },
    { label: "İptal", description: "Şimdilik dur. findings.json korunur." }
  ]
}]
```

---

## Adım 6: Rapor Üretimi — Bölüm Bazında

`report-writing.md` dosyası her bölüm için ayrı prompt sağlar. Claude her bölümü ayrı bir LLM çağrısında yazar.

**Odak bazlı derinlik:** Her bölümün derinliği `odak` değerine göre belirlenir (●/○/◐/—). Matris için **"Rapor Odağı Sistemi → 10.2 Bölüm derinlik matrisi"** bölümüne bakılır. `—` işaretli bölümler HTML'de üretilmez ve sidebar nav'dan silinir; `◐` işaretli bölümler 1 paragraf + tek scorecard ile kısaltılır; `●` işaretli bölümler için `report-writing.md` içindeki "Odak Bazlı Derinlik" alt başlığındaki genişletilmiş şablon kullanılır.

### 6.1 Yazım sırası

1. Bölüm 1 — Yönetici Özeti
2. Bölüm 2 — Temel Metrikler
3. Bölüm 3 — Teknik SEO
4. Bölüm 4 — Keyword Evreni
5. Bölüm 5 — Fırsat Keyword'leri
6. Bölüm 6 — SERP Analizi
7. Bölüm 7 — Rakip Kıyası
8. Bölüm 8 — GEO/AEO (kapsamda varsa; yoksa slot atlanır + sidebar nav güncellenir)
9. Bölüm 9 — İçerik/Backlink Snapshot
10. Bölüm 10 — Aksiyon Planı
11. Bölüm 11 — Yöntem ve Notlar

### 6.2 Her bölüm için süreç

1. `language-rules.md` + `report-writing.md` + `raw-data.json` (ilgili slice) + `glossary.json` promptta toplanır.
2. Claude HTML parçasını üretir (sadece section içeriği, wrapper YOK).
3. Çıktı `lint_report.py` mantığına göre self-check: yasaklı kelime / emir kipi / Türkçe karakter?
4. Uyarı varsa → rewrite.
5. Temiz HTML `sections` dict'ine kaydedilir.

### 6.3 Template'e enjekte

```python
template = Path('assets/report-template.html').read_text()
brand_css = Path('assets/brand.css').read_text()
glossary_json = Path('assets/glossary.json').read_text()

rapor = (template
    .replace('{{BRAND_CSS}}', brand_css)
    .replace('{{GLOSSARY_JSON}}', glossary_json)
    .replace('{{MARKA_ADI}}', marka_adi)
    .replace('{{MARKA_DOMAIN}}', marka_domain)
    .replace('{{TARIH}}', tarih)
    .replace('{{MOD_ROZET}}', f"{mod.upper()} · {kapsam.upper()}")
    .replace('{{YONETICI_OZETI}}', sections['ozet'])
    .replace('{{METRIKLER}}', sections['metrikler'])
    .replace('{{TEKNIK}}', sections['teknik'])
    .replace('{{KEYWORDS}}', sections['keywords'])
    .replace('{{FIRSATLAR}}', sections['firsatlar'])
    .replace('{{SERP}}', sections['serp'])
    .replace('{{RAKIPLER}}', sections['rakipler'])
    .replace('{{GEO}}', sections.get('geo', ''))
    .replace('{{BACKLINK}}', sections['backlink'])
    .replace('{{AKSIYON}}', sections['aksiyon'])
    .replace('{{YONTEM}}', sections['yontem'])
)
```

GEO kapsamda yoksa: hem slot boş bırakılır hem sidebar'dan `#geo` nav item'ı silinir (string replace).

**Odak bazlı slot atlama:** `— (skip)` işaretli bölümlerin slot'u boş bırakılır ve sidebar nav'dan ilgili `<li>` string replace ile silinir. Bu mekanizma GEO'nun kapsam dışı davranışıyla birebir aynı. Örn: `odak=keyword` için Bölüm 9 (Backlink) HTML üretilmez, `{{BACKLINK}}` → `""` ve sidebar'dan `<li><a href="#backlink">` satırı silinir. Template hero bölümünde ek olarak `{{ODAK_ROZET}}` doldurulur: `<span class="odak-badge odak-{tip}">{label}</span>`.

### 6.4 Local save

```python
out_dir = f'./cikti/{marka_slug}/{tarih}'
os.makedirs(out_dir, exist_ok=True)
# Odak=genel ise rapor.html, diğer odaklarda rapor-{odak}.html
dosya_adi = 'rapor.html' if odak == 'genel' else f'rapor-{odak}.html'
Path(f'{out_dir}/{dosya_adi}').write_text(rapor, encoding='utf-8')
```

### 6.5 Lint pass (Claude-native, Grep ile)

Üretilen rapor HTML'ini Claude kendi Grep tool'u ile tarar — ayrı Python scripti gerekmez.

Yasaklı kelime taraması:
```
Grep pattern: \b(kesin|mutlaka|garanti|garantiliyoruz|hata|kötü|berbat|yanlış|başarısız)\b
path: {out_dir}/rapor.html
-i: true (case insensitive)
```

Emir kipi taraması (Türkçe -iniz/-ınız/-unuz/-ünüz + bariz emir formları):
```
Grep pattern: \b\w+(iniz|ınız|unuz|ünüz)\b|\b(yapın|edin|kurun|ekleyin|düzeltin|düzeltiniz)\b
path: {out_dir}/rapor.html
-i: true
```

Uyarı sayısını topla. Checkpoint #3'te kullanıcıya göster: *"N dil uyarısı bulundu, şu bölümlerde: ..."*. Tek tuşla o bölümü tekrar yazabilir.

Allowlist (false positive): "değerlendirilebiliniz", "kullanılabiliniz" gibi nadir edilgen kullanımlar uyarı olarak gelmez — Claude grep sonucunu filtreleyerek karar verir.

---

## Adım 7: Checkpoint #3 — Rapor Draft Onayı

Kullanıcıya özet:
- Dosya yolu
- Bölüm preview (her bölümün ilk 100 karakteri)
- Toplam kelime sayısı
- Lint uyarıları (varsa)
- Tahmini okuma süresi

AskUserQuestion:
```
[{
  question: "Rapor hazır — bitiş aksiyonu?",
  header: "Rapor",
  options: [
    { label: "Bitti, aç", description: "Browser'da aç, Railway deploy varsa yap." },
    { label: "Şu bölümü tekrar yaz", description: "Belirli bir bölüm yeniden üretilir." },
    { label: "Tüm raporu farklı tonla yeniden yaz", description: "Tüm bölümler yeniden." },
    { label: "İptal (local sakla)", description: "HTML dosyası dursun, deploy yapma." }
  ]
}]
```

"Bitti, aç" seçilirse:
```bash
open {out_dir}/rapor.html  # macOS
```

---

## Adım 8: Opsiyonel Railway Deploy (Claude-native, Bash ile)

`.env`'de `RAILWAY_TOKEN` ve `RAILWAY_PROJECT_ID` tanımlı değilse bu adım atlanır. Tanımlıysa:

### 8.1 Kullanıcıya sor

AskUserQuestion:
> "Bu raporu public linke dönüştürelim mi? Müşteriye gönderebileceğin bir URL üretilecek."

"Hayır" derse adımı atla, skill kapanır.

### 8.2 Railway CLI kurulu mu kontrol et

```bash
command -v railway >/dev/null 2>&1 && echo installed || echo missing
```

`missing` ise Claude kuruluma yardım eder:
```bash
# Homebrew varsa:
brew install railway
# yoksa npm:
npm install -g @railway/cli
# hiçbiri yoksa: kullanıcıya nazik bir mesaj, deploy atlanır
```

### 8.3 Raporu workspace'e kopyala + index yeniden üret

Claude Write tool ile, hiç Python gerektirmeden:

```bash
# Dosya kopyala
cp {out_dir}/rapor.html ~/.claude/skills/on-analiz/railway-workspace/reports/{marka-slug}-{tarih}.html
```

`railway-workspace/index.html` dosyasını Claude kendisi Write ile yeniden üretir. İçerik:
- Inbound brand kit'li minimal HTML (mevcut `railway-workspace/index.html` template'inden türetilir)
- `reports/*.html` dosyalarının listesi `ls` ile alınır, `<a>` linkleri oluşturulur:

```bash
ls -1 ~/.claude/skills/on-analiz/railway-workspace/reports/*.html 2>/dev/null | xargs -n1 basename
```

Sonuç Claude tarafından `<ul><li><a href="reports/...">...</a></li></ul>` olarak Write edilir.

### 8.4 Railway'e deploy

```bash
cd ~/.claude/skills/on-analiz/railway-workspace
set -a && source ~/.claude/skills/on-analiz/.env && set +a
railway link --project "$RAILWAY_PROJECT_ID" 2>/dev/null || true  # idempotent
railway up --service on-analiz-reports --detach
```

### 8.5 URL'yi kullanıcıya ver

Deploy logundan URL'yi yakala veya `railway domain` ile öğren:

```bash
railway domain --service on-analiz-reports 2>/dev/null || railway status
```

Public URL formatı: `https://<service>.up.railway.app/reports/{marka-slug}-{tarih}.html`

Clipboard'a kopyala (macOS):
```bash
echo -n "https://..." | pbcopy
```

Kullanıcıya mesaj:
> "✓ Rapor yayında: <URL> (clipboard'a kopyalandı)"

### 8.6 Hata yönetimi

Deploy fail olursa (quota, token geçersiz, vs.): local HTML duruyor, kullanıcıya nazik uyarı, skill başarıyla kapanır.

---

## Adım 9: Final Özet

Kullanıcıya son mesaj:
```
✓ Rapor üretildi: {out_dir}/rapor.html
✓ Veri yedeği: {out_dir}/raw-data.json
✓ Bulgu özeti: {out_dir}/findings.json
{+ varsa:}
✓ Public URL: https://...
✓ Clipboard'a kopyalandı.

Yeniden çalıştırmak için:
/on-analiz --resume {marka-slug}        (veri yenile)
/on-analiz --refresh-report {marka-slug} (sadece HTML yeniden)
```

---

## Resume Modu

`/on-analiz --resume {marka-slug}`:
1. `./cikti/{marka-slug}/` altında en son tarih bulunur
2. `meta.json` okunur → form değerleri yeniden
3. `raw-data.json` varsa: "Var olan veriden devam? veya yenile?" sorulur
4. Seçime göre Adım 5 (Checkpoint #2) veya Adım 4 (Veri toplama) baştan

## Refresh-Report Modu

`/on-analiz --refresh-report {marka-slug}`:
1. Son run'un raw-data.json + findings.json okunur
2. Sadece Adım 6 (HTML üretim) ve sonrası çalışır
3. API çağrısı YOK — dil/ton iterasyonu için hızlı

---

## Hata Yönetimi Kısa Referans

| Hata | Aksiyon |
|---|---|
| .env yok | setup.py yönlendir |
| Marka domain erişilemiyor | Dur, kullanıcıya sor |
| Rakip erişilemiyor | Devam, kısmi veri işareti |
| Ahrefs rate limit | 3x retry (30/60/120s), fail → null |
| DataForSEO fail | SERP bölümü atlanır |
| WebFetch timeout | 2 retry, atla |
| Railway fail | Local HTML kalır, uyarı |
| LLM context overflow | Bölüm bağımsız yazılır, sadece o bölüm rewrite |

---

## Rapor Odağı Sistemi

`odak` alanı iki şeyi aynı anda belirler:

1. **Veri kaynağı filtresi** — her odak yalnızca kendi tool ailesine gider. Diğer tool'lar çağrılmaz. Örn. `odak=teknik` → **Ahrefs Site Audit MCP** kullanılır; `organic-competitors`, `organic-keywords`, rakip analiz call'ları hiç yapılmaz. Kullanıcı "teknik" dediyse skill sadece teknik veri toplar.
2. **Bölüm derinliği** — raporda hangi bölümler ● (derin) / ○ (normal) / ◐ (özet) / — (atla) olarak yazılır.

Mod (pitch/onboarding) derinlik ekseniyken, odak **içerik ekseni**dir — ikisi birbirinden bağımsız. Örn: `pitch + keyword` = hızlı keyword tarama raporu; `onboarding + teknik` = derin teknik audit dosyası.

**Kritik kural:** Form alanları ve Checkpoint #1 adımları da odağa göre koşullanır. Teknik/keyword/backlink odaklarında rakip alanı opsiyoneldir, rakip önerisi adımı atlanır.

### 10.1 Odak tipleri ve amacı

| Odak | Rapor karakteri | Tipik kullanım |
|---|---|---|
| **genel** | Mevcut davranış — tüm bölümler dengeli | Klasik ön analiz, yeni müşteri pitch'i |
| **keyword** | Keyword evreni, fırsatlar, SERP derin | Content strategy hazırlığı, keyword research brief |
| **backlink** | Backlink profili, anchor, referring domains derin | Link building proposal, off-site durum tespiti |
| **rakip** | Rakip kıyası, gap analizi derin | Rakip savunma raporu, pozisyonlama analizi |
| **teknik** | Teknik bulgular, CWV, schema, indexability derin | Teknik audit teslimi, dev ekibi brief'i |

### 10.2 Bölüm derinlik matrisi

Her odak, raporun 11 bölümünü farklı ağırlıkla işler:

- ● **Derin (primary)** — bölüm 2-3 alt başlıkla genişler, SVG/tablo + detaylı yorum, 200+ kelime
- ○ **Normal (secondary)** — standart yazım, mevcut şablonla uyumlu
- ◐ **Özet (minimal)** — 1 paragraf + tek scorecard/istatistik; "bağlam için" notuyla
- — **Atla (skip)** — bölüm raporda görünmez, sidebar nav'dan da silinir

| Bölüm | genel | keyword | backlink | rakip | teknik |
|---|---|---|---|---|---|
| 1 Yönetici Özeti | ○ | ○ | ○ | ○ | ○ |
| 2 Temel Metrikler | ○ | ◐ | ◐ | ○ | ◐ |
| 3 Teknik SEO | ○ | ◐ | ◐ | ◐ | ● |
| 4 Keyword Evreni | ○ | ● | ◐ | ○ | ◐ |
| 5 Fırsat Keyword | ○ | ● | — | ● | — |
| 6 SERP Analizi | ○ | ● | — | ○ | — |
| 7 Rakip Kıyası | ○ | ○ | ○ | ● | ◐ |
| 8 GEO/AEO | kapsam | kapsam | kapsam | kapsam | kapsam |
| 9 Backlink Snapshot | ○ | — | ● | ○ | — |
| 10 Aksiyon Planı | ○ | ○ (kw eksenli) | ○ (link eksenli) | ○ (rakip eksenli) | ○ (teknik eksenli) |
| 11 Yöntem ve Notlar | ○ | ○ | ○ | ○ | ○ |

**Kurallar:**
- `—` işaretli bölüm HTML'de üretilmez, template slotu boş bırakılır, sidebar nav'dan `<li>` silinir (GEO yoksa uygulanan aynı mekanizma).
- `●` bölümünün yazımı `report-writing.md` içinde "Odak Bazlı Derinlik" altında tanımlanmıştır — o odakta bölüm farklı alt başlıklarla açılır.
- Bölüm 1 (Özet) her zaman `○`, ama içeriği odağa göre tonlanır: "Bu rapor keyword araştırması odağındadır; backlink ve teknik kısımlar bağlam için özetlenmiştir" gibi bir framing cümlesi eklenir.
- Bölüm 10 (Aksiyon) her odakta üretilir, ama aksiyon maddeleri o odağın kategorisiyle filtrelenir. Pitch: 5-8 madde, Onboarding: 12-20 madde.

### 10.3 Veri kaynağı & çağrı matrisi

Her odak **yalnızca kendi tool ailesine** gider. `—` işaretli çağrı yapılmaz, yok sayılır. Skill başka odakların tool'larına "bağlam için minimal" dahi çağırmaz.

| Tool ailesi | genel | keyword | backlink | rakip | teknik |
|---|---|---|---|---|---|
| **Ahrefs Site Audit** (projects/issues/page-explorer/page-content) | — | — | — | — | **● PRIMARY** |
| `site-explorer-metrics` + `-domain-rating` | ✓ | ✓ | ✓ | ✓ | ◐ (sadece özet için) |
| `site-explorer-top-pages` | 20 | 20 | — | 50 | — |
| `site-explorer-organic-keywords` | pitch 20 / onb 100 | **pitch 50 / onb 300** | — | pitch 30 / onb 150 | — |
| `site-explorer-organic-competitors` | ✓ | — | — | **✓** | — |
| `site-explorer-backlinks-stats` | ✓ | — | ✓ | ✓ | — |
| `site-explorer-referring-domains` | ilk 50 | — | **ilk 300 + delta** | ilk 100 | — |
| `site-explorer-anchors` | ✓ | — | **✓ full** | ✓ | — |
| `site-explorer-all-backlinks` sample | 100 | — | **500 + segment** | 100 | — |
| `site-explorer-broken-backlinks` | — | — | **✓** | — | — |
| `site-explorer-linked-anchors-external` | — | — | **✓** | — | — |
| `site-explorer-linked-domains` | — | — | ✓ | — | — |
| `keywords-explorer-*` (overview, related, matching, suggestions) | — | **✓** | — | ◐ gap için | — |
| `gsc-keywords` + `gsc-keyword-history` (varsa) | ✓ | **✓** | — | ✓ | — |
| DataForSEO SERP batch | pitch 20 / onb 100 | **pitch 40 / onb 200** | — | pitch 20 / onb 100 | — |
| WebFetch sayfa sayısı | pitch 5 / onb 20 | pitch 5 / onb 20 | 5 | 10 | **Site Audit başarısızsa fallback: pitch 15 / onb 60** |
| PageSpeed (CWV) | onb opsiyonel | — | — | — | **Site Audit'te yoksa marka + top 1 rakip zorunlu** |
| Schema/JSON-LD extraction | homepage | — | — | — | **Site Audit page-content'ten** |
| Rakip detay: her rakip için | 3 call | — | — | **5 call** | — |
| Rakip önerisi (Checkpoint #1) | ✓ | — | — | ✓ | — |

**Özel notlar:**
- Teknik odakta **rakip bilgisi sıfırdır** — form'da rakip girilmemişse skill hiç sormaz. Rakip girilmişse yok sayılır.
- Keyword odağında rakip keyword gap çıkarmak istiyorsa minimal `organic-keywords` top 20 her rakip için çağrılır — başka rakip call yok.
- Backlink odağında keyword call yok — opportunity keyword üretilmez.
- Rakip odağında backlink ailesi ortak RD tespiti için `referring-domains` ilk 100 ile sınırlı; keyword gap birincil veri.

### 10.3.1 Teknik odak — Ahrefs Site Audit akışı

Teknik odak Site Audit MCP'yi birincil kaynak kabul eder. Akış:

**1. Proje tespiti**
```
mcp__ahrefs__site-audit-projects (filtre: marka domain)
```
Dönen listede `project_id` ve `last_crawl_date` aranır. 3 durum:

- **A) Proje var, son crawl 30 günden yeni** → `project_id` ile devam et, yeni crawl talep etme.
- **B) Proje var, son crawl 30 günden eski** → Kullanıcıya AskUserQuestion: "Son audit X gün eski. Mevcut veriyle devam mı, manuel yeni crawl bekleyelim mi, direct crawl fallback mı?" (skill crawl tetikleyemez).
- **C) Proje yok** → Kullanıcıya bildir: "Ahrefs'te bu domain için aktif Site Audit projesi yok. Fallback: WebFetch + curl ile direct crawl (sınırlı veri)."

**2. Veri çekme (proje varsa, A/B seçimi sonrası)**

Paralel batch:
- `site-audit-issues` — aktif tüm issue'lar (severity, category, affected_pages_count ile)
- `site-audit-page-explorer` — top 200 sayfa (metrics: status_code, depth, word_count, title, h1, internal_linkrank, crawl_date)
- `site-audit-page-content` — top 5-20 öncelikli sayfa (full HTML + schema + meta çekimi)
  - pitch: 5 sayfa, onboarding: 20 sayfa

**3. Fallback (C) — Site Audit yok**

Skill direct crawl modunda çalışır:
- Marka anasayfası + robots.txt + sitemap.xml + llms.txt
- Sitemap'ten ilk 60 URL (onboarding) veya 15 URL (pitch) WebFetch
- Her sayfa için on-page check (title/meta/h1/canonical/schema/noindex)
- PageSpeed API ile marka anasayfa CWV
- Site Audit-benzeri findings dict'i inşa edilir, rapor aynı şablonda yazılır

Fallback kullanıldığında raporda belirgin bir `<div class="partial-data-notice">` ile "Veri kaynağı: direct crawl — Ahrefs Site Audit projesi olmadığı için sınırlı teknik bulgu" notu görünür.

**4. raw-data.json içinde teknik slice**
```json
"teknik": {
  "veri_kaynagi": "ahrefs_site_audit | direct_crawl",
  "proje_id": "...",
  "son_crawl": "YYYY-MM-DD",
  "issues": [ { category, severity, message, affected_pages } ],
  "pages": [ { url, status_code, title, h1_count, schema_types, word_count, internal_rank } ],
  "cwv": { lcp, inp, cls, tbt },
  "schema_coverage": { "Product": 432, "BreadcrumbList": 512, ... },
  "indexability_summary": { noindex_count, canonical_mismatches, robots_blocked },
  "bozuk_linkler": [ ... ],
  "veri_eksikleri": [ ... ]
}
```

### 10.4 Checkpoint #1'de odak özeti

Scope onay mesajına odak ekleniyor — kullanıcı hangi çağrıların çalışacağını şeffaf görür:

> "Odak: **keyword** — Ahrefs organic-keywords top 300, DataForSEO SERP 200 batch, backlink ve teknik veriler özet için toplanacak. Tahmini süre: ~50 dk (onboarding)."

### 10.5 Aksiyon planı filtresi (Bölüm 10)

`aksiyon_maddeleri` her bulgudan türetilir; her maddenin `kategori` alanı vardır: `keyword | content | onpage | technical | backlink | competitor | geo`. Odağa göre filtre:

| Odak | Dahil edilen kategoriler |
|---|---|
| genel | hepsi |
| keyword | `keyword, content, onpage` |
| backlink | `backlink, competitor` |
| rakip | `competitor, keyword, content` |
| teknik | `technical, onpage` |

Filtreden sonra eğer toplam madde sayısı hedefin altındaysa (pitch 5 / onb 12), komşu kategorilerden tamamlanır ve sonda "bağlam aksiyonları" alt başlığında verilir.

### 10.6 Resume / refresh-report ile uyum

- `--resume` modunda eski `meta.json` içinde `odak` alanı varsa, "Aynı odakta devam / odağı değiştir" seçeneği sunulur.
- `--refresh-report` modunda odak değiştirilebilir; API çağrısı yapılmaz, var olan `raw-data.json` üzerinden sadece bölüm filtresi ve yazım tekrar işletilir. Eksik veri varsa (ör. eski run'da odak=genel iken şimdi backlink isteniyor ve `broken-backlinks` çağrılmamış) kullanıcı uyarılır: "Bu odak için veri eksikleri: X, Y. Ekstra çağrı yapayım mı?"

### 10.7 Rapor başlığında odak rozet'i

Template'e `{{ODAK_ROZET}}` placeholder'ı eklenir. Hero bölümünde mod rozet'inin yanında odak rozet'i gösterilir:

```html
<span class="mod-badge">PITCH · SEO+GEO</span>
<span class="odak-badge odak-keyword">Keyword Research</span>
```

CSS sınıfı `odak-{tip}` her odak için farklı renk: `odak-genel` (nötr), `odak-keyword` (mavi), `odak-backlink` (mor), `odak-rakip` (turuncu), `odak-teknik` (yeşil). Stil `brand.css`'e eklenir.

### 10.8 Dosya adlandırma

Çıktı dosyası adı odak ile zenginleşir:
```
./cikti/{marka-slug}/{YYYY-MM-DD}/rapor-{odak}.html
```
Genel odak için geriye dönük uyumluluk: `rapor.html` (odak yoksa veya `genel` ise).

---

## Mod Detay Tablosu

| Boyut | Pitch | Onboarding |
|---|---|---|
| Süre | 10-15 dk | 45-60 dk |
| Rakip sayısı | 3 | 5 |
| Top keyword (SERP) | 20 | 100 |
| WebFetch sayfa | 5 | 20 |
| Backlink örneklem | 100 en güçlü | Full |
| CWV ölçümü | Yok | Var (PageSpeed) |
| Aksiyon maddesi | 8-12 | 20-30 |
| Rapor bölüm sayısı | 8-9 | 11-12 |
| Opsiyonel form alanları | Atlanır | Sorulur |
