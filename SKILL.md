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
