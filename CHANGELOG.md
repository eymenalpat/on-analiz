# Changelog

## [1.3.0] — 2026-04-21

### Changed — BREAKING: Odak artık veri kaynağı filtresi

Önceki 1.2.0 sürümünde odak yalnızca bölüm derinliğini etkiliyordu; skill tüm odaklarda geniş veri topluyor, derinlik matrisiyle bölümleri seçiyordu. Bu yaklaşım kullanıcı beklentisine aykırıydı: "teknik odak" denince rakip çağrısı yapılması kafa karıştırıcıydı.

1.3.0 itibarıyla **her odak yalnızca kendi tool ailesine gider.** Diğer tool çağrıları hiç yapılmaz.

- **teknik** → Ahrefs Site Audit MCP birincil: `site-audit-projects` → `site-audit-issues` → `site-audit-page-explorer` → `site-audit-page-content`. Proje yoksa fallback direct crawl. `organic-competitors`, `organic-keywords`, rakip tool'ları **hiç çağrılmaz**.
- **keyword** → `keywords-explorer-*` ailesi + `gsc-keywords` + DataForSEO SERP. Rakip/backlink çağrısı yok.
- **backlink** → Site Explorer backlink ailesi (stats, RD, anchors, all-backlinks, broken, linked-anchors). Keyword/rakip çağrısı yok.
- **rakip** → `organic-competitors` + her rakip için 5 call. Teknik/backlink minimum.
- **genel** → 1.2'deki geniş set (değişmedi).

### Added
- **Teknik odak için Site Audit akışı** (SKILL.md → 10.3.1): proje tespit, 3 senaryo (güncel/eski/yok), veri çekme paralel batch, fallback direct crawl, `raw-data.teknik` schema.
- **Checkpoint #1 odak-koşullu adımlar:** rakip önerisi (3.3) sadece `odak ∈ {genel, rakip}` çalışır. Diğer odaklarda tamamen atlanır.
- **Süre ve call tahmini** odak başına ayrı tablolarla revize edildi (SKILL.md → 3.4).
- **Adım 2 input formu** yeniden kurgulandı: odak önce sorulur, sonra odağa göre rakip alanı zorunlu/opsiyonel belirlenir.
- **report-writing.md Bölüm 3** Site Audit versiyonu + fallback direct crawl versiyonu ayrı şablonlarla tanımlandı.

### Removed
- 1.2'de tabloda ◐ (minimal) ile işaretli "bağlam için çağrı" yaklaşımı — artık ya çağrılır ya çağrılmaz. Yarı yolda kalan call yok.

## [1.2.0] — 2026-04-21

### Added — Rapor Odağı Sistemi
- Yeni `odak` alanı: `genel` / `keyword` / `backlink` / `rakip` / `teknik`. Adım 2'de AskUserQuestion ile sorulur, kısa formda `odak=` parametresi ile verilebilir.
- **Bölüm derinlik matrisi** — 11 bölüm × 5 odak için `●/○/◐/—` ağırlık haritası. Skip işaretli bölümler HTML'de üretilmez, sidebar nav'dan silinir.
- **Veri toplama deltaları** — her odak için Ahrefs/DataForSEO/WebFetch/PageSpeed call listesi genişler veya daralır. Checkpoint #1'de kullanıcıya şeffaf gösterilir.
- **Primary bölüm şablonları** — Teknik/Keyword/Rakip/Backlink odaklı Bölüm 3, 4, 5, 6, 7, 9, 10 için genişletilmiş alt başlık setleri (`report-writing.md` → "Odak Bazlı Derinlik").
- **Aksiyon planı filtresi** — odağa göre kategori bazlı filtre (keyword/content/onpage/technical/backlink/competitor).
- **Odak rozeti** — rapor hero'sunda renkli badge (`{{ODAK_ROZET}}`); her odak için ayrı CSS sınıfı.
- **Dosya adlandırma** — genel dışı odaklarda `rapor-{odak}.html`, genel odakta geriye dönük `rapor.html`.
- **Resume/refresh-report uyumu** — eski run'da odak varsa korunur, `--refresh-report` ile odak değiştirilebilir (veri eksikliği uyarısıyla).

### Use case örnekleri
- `pitch + keyword` → 10 dk'lık keyword research brief
- `onboarding + teknik` → 60 dk'lık teknik audit dosyası
- `onboarding + backlink` → link building proposal
- `pitch + rakip` → rakip savunma pitch deck'i

## [1.1.0] — 2026-04-19

### Changed — Python runtime bağımlılığı kaldırıldı
- `install.sh` artık sadece `git clone` + opsiyonel Railway CLI kurulumu yapar. Son kullanıcıda Python çalıştırılmaz.
- Setup (API key girişi) Claude AskUserQuestion + Write + Bash chmod ile yapılır — `scripts/setup.py` silindi.
- Railway deploy Claude tarafından doğrudan Bash ile yönetilir (`cp`, `railway up`) — `scripts/deploy.py` silindi.
- Dil lint'i Claude Grep tool'u ile yapılır — `scripts/lint_report.py` silindi.
- SEO + GEO checklist Excel'leri repo'ya gömüldü (`assets/source/`). JSON çıktıları `assets/checklists/` altında pre-built commit'lenir, son kullanıcı parse etmez.
- `scripts/parse_checklists.py` sadece maintainer için kalır — Excel güncellenince çalıştırılır, üretilen JSON'lar commit edilir.

### Net sonuç
- Son kullanıcı tarafında Python gerektirmez.
- Tek adım kurulum: `curl -sSL .../install.sh | bash`
- İlk `/on-analiz` çağrısında Claude tüm konfigürasyonu interaktif olarak halleder.

## [1.0.0] — 2026-04-19

### Added
- İlk sürüm — `/on-analiz` user-level skill
- Pitch ve onboarding modu
- SEO + GEO checklist birleşik denetimi (kullanıcı seçimli)
- Ahrefs MCP + DataForSEO REST + WebFetch + PageSpeed entegrasyonu
- 3 checkpoint'li akış (scope / bulgu / rapor onayı)
- Inbound brand kit'li interaktif HTML rapor (sol sidebar, Bricolage Grotesque + Outfit)
- 36 terimli glossary + hover tooltip
- Railway deploy opsiyonu — public URL üretimi
- Resume ve refresh-report modları

### Bilinçli YAGNI'ler
- Multi-agent paralel dispatch
- Ayrı Python CLI katmanı
- Screaming Frog entegrasyonu
- GSC/GA OAuth
- PDF export
- Rapor kıyaslama (önceki run diff)
- Çoklu dil çıktı (sadece Türkçe v1)
