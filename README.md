# /on-analiz — Yeni Müşteri Ön Analiz Skill'i

Inbound için hazırlanmış Claude Code skill'i. Marka + rakip domainlerini alıp Ahrefs, DataForSEO ve site crawl verisi ile SEO + GEO ön denetimi yapar, Inbound brand kit'li HTML raporu üretir. İstenirse Railway üzerinden public link olarak yayınlar.

## Kurulum (tek komut)

Terminali aç, şunu yapıştır:

```bash
curl -sSL https://raw.githubusercontent.com/eymenalpat/on-analiz/main/install.sh | bash
```

Bu komut:
- Skill dosyalarını `~/.claude/skills/on-analiz/` dizinine indirir
- Railway CLI yüklü değilse kurmayı teklif eder (opsiyonel)

**Başka komut yazmana gerek yok.** API key'leri Claude ilk çağrıda sorar.

## Kullanım

1. Claude Code'u aç (veya yeniden başlat)
2. Yeni konuşma başlat
3. Şunu yaz:

```
/on-analiz
```

İlk çağrıda Claude sana şu API key'leri soracak:
- **DataForSEO Login + Password** (zorunlu — SERP verisi için)
- **PageSpeed API Key** (opsiyonel — onboarding modunda hız metrikleri için)
- **Railway Token + Project ID** (opsiyonel — public link üretmek istiyorsan)

Sonra form açılır, marka + rakip domainlerini girersin, skill çalışmaya başlar.

## Nasıl çalışır

Skill 3 checkpoint'li akışla ilerler:

1. **Scope onayı** — marka + rakip + sektör + mod seçildikten sonra Claude domainleri kontrol edip Ahrefs önerilerini gösterir. "Başla" deyince veri toplama başlar.
2. **Bulgu özeti onayı** — tüm veri toplandıktan sonra ana bulgular Markdown olarak gösterilir. Onay verince HTML rapor yazılmaya başlar.
3. **Rapor draft onayı** — HTML hazırlanınca önizleme gösterilir. "Bitti" deyince tarayıcıda açılır, (varsa) Railway'e deploy olur.

## Modlar

| | Pitch | Onboarding |
|---|---|---|
| Süre | 10-15 dk | 45-60 dk |
| Rakip sayısı | 3 | 5 |
| SERP keyword | 20 | 100 |
| Sayfa crawl | 5 | 20 |
| Aksiyon maddesi | 8-12 | 20-30 |

## Çıktılar

Her çalıştırma `./cikti/{marka-slug}/{YYYY-MM-DD}/` altında dört dosya bırakır:
- `rapor.html` — standalone HTML rapor (direkt müşteriye gönderilebilir)
- `raw-data.json` — tüm ham veri (tekrar rapor üretmek için)
- `findings.json` — bulgu özeti
- `meta.json` — form cevapları

Railway kurulumu varsa HTML ayrıca public linke dönüşür.

## Flags

- `/on-analiz --setup` — API key'leri güncelle
- `/on-analiz --resume ornekmarka.com.tr` — önceki run'ı devam ettir
- `/on-analiz --refresh-report ornekmarka.com.tr` — rapor dil/ton iterasyonu (API çağrısı yok)

## Sorun çıkarsa

**DataForSEO 401:** Login/password yanlış → `/on-analiz --setup`

**Railway up fail:** `railway login` yapılmış mı kontrol et. Deploy atlansa bile rapor local'de durur.

**WebFetch 403:** Bazı siteler bot'u blokluyor → o bölüm kısmi veri işaretiyle üretilir, skill devam eder.

**Checklist güncellenmesi gerekiyor:** Repo sahibi (Inbound) Excel'leri güncelleyip JSON'ları yeniden üretir. Sen `curl | bash` komutunu tekrar çalıştırırsın — `.env` ve `cikti/` korunur.

## Lisans

Inbound iç kullanım.
