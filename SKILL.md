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

### 6.4 Local save

```python
out_dir = f'./cikti/{marka_slug}/{tarih}'
os.makedirs(out_dir, exist_ok=True)
Path(f'{out_dir}/rapor.html').write_text(rapor, encoding='utf-8')
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
