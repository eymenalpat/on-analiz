---
name: on-analiz
description: Yeni müşteri ön analizi — marka + rakip domainleri alıp Ahrefs/DataForSEO/crawl verisi ile SEO+GEO denetimi yapar, Inbound brand kit'li interaktif HTML rapor üretir. Pitch ve onboarding modları. Türkçe çıktı. Triggers: /on-analiz, ön analiz, yeni müşteri analizi, domain denetimi, SEO+GEO denetimi.
version: 1.0.0
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

**Kısa form:** `/on-analiz ornekmarka.com.tr vs rakip-a.com.tr,rakip-b.com mod=pitch kapsam=seo+geo sektor=lokal ulke=TR dil=tr`

---

## Adım 1: Setup Kontrolü

```
if not os.path.exists('~/.claude/skills/on-analiz/.env'):
    print("Setup henüz yapılmamış. Wizard başlatılıyor...")
    subprocess.run(['python3', '~/.claude/skills/on-analiz/scripts/setup.py'])
```

.env'den değişkenler `python-dotenv` ile yüklenir:
```bash
source ~/.claude/skills/on-analiz/.env
```

---

## Adım 2: Input Formu

AskUserQuestion tool'u ile 7 zorunlu alan tek mesajda sorulur. Opsiyoneller ayrı soru.

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
  { ... kapsam: seo / geo / ikisi ... }
]
```

Yukarıdaki "Yaz" seçenekleri için kullanıcı "Other" seçerek serbest metin girer.

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

### 3.3 Rakip önerisi

Ahrefs MCP tool: `mcp__ahrefs__site-explorer-organic-competitors` marka domain'i için çağrılır. Kullanıcının verdiği rakiplerle karşılaştırılır. Ahrefs'in verdiği ilk 5'te olup kullanıcı listesinde olmayan varsa:
> "Ahrefs'in önerdiği güçlü rakipler: X, Y. Listeye eklemek ister misin?"

### 3.4 Süre ve tool call tahmini

| Mod | Rakip | Ahrefs call | DataForSEO call | WebFetch | Toplam tahmin |
|---|---|---|---|---|---|
| pitch 3 rakip | 3 | 4 + 9 | 20 | 5 + 2 | ~40 call / ~10-15 dk |
| onboarding 5 rakip | 5 | 4 + 15 | 100 | 20 + 2 | ~140 call / ~45-60 dk |

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
