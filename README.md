# /on-analiz — Yeni Müşteri Ön Analiz Skill'i

Inbound için hazırlanmış Claude Code user-level skill. Marka + rakip domainleri alıp Ahrefs, DataForSEO ve site crawl verisi ile SEO+GEO ön denetimi yapar, Inbound brand kit'li HTML rapor üretir.

## Kurulum

1. **Skill'i indir:** Bu klasör `~/.claude/skills/on-analiz/` altında olmalı.

2. **Bağımlılıklar:**
   ```bash
   pip3 install openpyxl
   ```
   (`pytest` gerekiyor test'ler için; Python 3.11+ stdlib yeterli kalan her şey için.)

3. **Checklist JSON'larını üret:**
   ```bash
   python3 scripts/parse_checklists.py \
     --seo '/path/SEO Checklist & Roadmap - Masterpiece v2021 (1).xlsx' \
     --geo '/path/GEO-AEO-Checklist Inbound (1).xlsx' \
     --out assets/checklists
   ```

4. **Setup wizard:**
   ```bash
   python3 scripts/setup.py
   ```
   API key'ler sorulur. `.env` dosyasına yazılır (chmod 600).

5. **(Opsiyonel) Railway CLI kurulumu:**
   ```bash
   brew install railway           # macOS
   # veya: npm i -g @railway/cli
   railway login                  # tarayıcıda OAuth açar
   ```
   Railway web UI'da yeni bir proje oluştur (boş bir Empty Service), ardından:
   ```bash
   cd ~/.claude/skills/on-analiz
   railway link                   # listeden projeyi seç
   # PROJECT_ID'yi öğrenmek için: railway status
   ```
   Çıkan `Project ID`'yi ve önceden oluşturduğun token'ı `setup.py` wizard'a gir.

## Kullanım

Claude Code içinde:
- `/on-analiz` — interaktif form başlar
- `/on-analiz --setup` — API key'leri güncelle
- `/on-analiz --resume ornekmarka.com.tr` — önceki run'ı devam ettir
- `/on-analiz --refresh-report ornekmarka.com.tr` — rapor dil/ton iterasyonu

## Kısa komut

```
/on-analiz ornekmarka.com.tr vs rakip-a.com.tr,rakip-b.com mod=pitch kapsam=seo+geo sektor=lokal ulke=TR dil=tr
```

## Çıktılar

`./cikti/{marka-slug}/{YYYY-MM-DD}/`:
- `raw-data.json` — tüm toplanan ham veri
- `findings.json` — Checkpoint #2 bulgu özeti
- `rapor.html` — final standalone HTML rapor
- `meta.json` — form cevapları + mod + kapsam

## Modlar

| | Pitch | Onboarding |
|---|---|---|
| Süre | 10-15 dk | 45-60 dk |
| Rakip | 3 | 5 |
| Keyword (SERP) | 20 | 100 |
| Crawl sayfa | 5 | 20 |
| Aksiyon | 8-12 | 20-30 |

## Troubleshooting

**"Setup henüz yapılmamış" uyarısı:** `python3 scripts/setup.py` çalıştır.

**DataForSEO 401:** Login/password yanlış → `/on-analiz --setup`.

**Railway up fail:** `railway login` yap, `RAILWAY_TOKEN` env geçerli mi kontrol et. Deploy atlansa bile rapor local'de durur.

**WebFetch 403 (marka domain):** Bazı siteler user-agent blokluyor — o bölüm kısmi veri ile üretilir, skill devam eder.

**Lint uyarıları:** Üretilen rapor yasaklı kelime içeriyorsa `lint_report.py` uyarır. Bölümü tekrar yazma seçeneği Checkpoint #3'te.

## Test

```bash
python3 -m pytest tests/ -v
```

## Bakım

- Excel checklist güncellenirse → `parse_checklists.py` yeniden çalıştır
- Glossary'ye yeni terim ekle → `assets/glossary.json` düzenle
- Brand kit değişirse → `assets/brand.css` güncelle

## Lisans

Inbound iç kullanım.
