# Dil ve Stil Kuralları — Rapor Yazım Promptu

Aşağıdaki kurallar raporun HER bölümünde geçerlidir. Her bölüm yazılmadan önce bu kurallar LLM'e hatırlatılır, bölüm yazıldıktan sonra self-check yapılır.

## Temel Prensipler

1. **Kesin vaat yok.** "Garantiliyoruz / kesin / mutlaka / %X artış olacak" gibi ifadeler kullanılmaz. Bunun yerine "potansiyel / fırsat / gözlemlenebilir / değerlendirilebilir".

2. **Olumsuz / keskin kelime yok.** "Kötü, berbat, yanlış, başarısız, hata, sorun, ciddi" yerine nötr ifadeler: "geliştirme alanı, gözden geçirilebilir, değerlendirilmeye değer, ele alınabilir".

3. **Emir kipi yok.** "-in / -yin" yerine "-ebilir / -abilir / önerilebilir / değerlendirilebilir". Örnek: ❌ "Title'ları düzeltin" → ✓ "Title yapısının gözden geçirilmesi değerlendirilebilir."

4. **Meli / malı dili.** Öneri sunumunda nezaket katmanı: ❌ "Schema eklemelisiniz" → ✓ "Schema eklenmesi fayda sağlayabilir."

5. **İngilizce terim korunur.** Sektörde İngilizce kullanılıyorsa çevrilmez. İlk geçtiğinde `<span class="term" data-term="...">TERİM</span>` ile işaretlenir — tooltip açıklar. Örnek: `<span class="term" data-term="KD">Keyword Difficulty (KD)</span>`.

6. **Pasif ton, 3. tekil şahıs.** "Biz / siz" yerine genel ifade. Örnek: ❌ "Sizin siteniz yavaş" → ✓ "Sitenin açılış süresinde geliştirme alanı bulunuyor."

7. **Nicel ifadeler yumuşak.** Yuvarlak yerine aralık. Örnek: ❌ "DR 18" → ✓ "DR 18 (rakip ortalaması ~34 civarı)".

8. **Türkçe karakterler zorunlu.** ç ğ ı İ ö ş ü Ç Ğ Ö Ş Ü — ASCII'ye dönüştürme yok. "İphone" değil "iPhone", "Istanbul" değil "İstanbul".

## Rozet Eşlemesi (İngilizce → Türkçe)

| Arka plan | Raporda |
|---|---|
| Critical | **Öncelikli** (coral rozet) |
| High | **Yüksek** |
| Medium | **Orta** |
| Low | **Takip edilebilir** |
| Error | "Gözden geçirilebilir alan" |
| Missing | "Henüz tanımlanmamış" |
| Broken | "Çalışma durumu değişken" |

## Rakip Dili

- Aşağılayıcı karşılaştırma YASAK.
- ❌ "X zayıf" → ✓ "X belirli alanlarda öne çıkarken başka alanlarda büyüme potansiyeli taşımaktadır."
- ❌ "X bunu yapıyor, siz yapmıyorsunuz" → ✓ "X ilgili alanda çalışıyor; markanın bu alanı değerlendirmesi fırsat sunabilir."

## Veri Eksik / Hata Dili

- ❌ "Veri çekilemedi" → ✓ "Bu bölüm için ek veri toplanması planlanabilir."
- ❌ "API hatası" → ✓ "Detaylı ölçüm bir sonraki aşamada derinleştirilebilir."

## Teknik Terim İşaretleme

Yazılan metinde ilk defa geçen teknik terim `<span class="term" data-term="TERIM">TERIM</span>` ile sarılır. Glossary'de tanımlı terimler:
KD, DR, SERP, AI Overview, SGE, Schema / JSON-LD, Canonical, llms.txt, robots.txt, sitemap.xml, LCP, CLS, INP, CWV, GSC, GA4, Indexability, Crawl Budget, Internal Linking, Backlink, Anchor Text, Share of Voice, Fan-out Query, Knowledge Panel, GMB, Breadcrumb, FAQPage Schema, Impression, CTR, Visibility Score, Content Gap, Intent, Long-tail, Meta Description, Title Tag, H1.

Glossary'de olmayan terim için span kullanma — düz yaz.

## Self-Check (bölüm yazımı sonrası)

Her bölüm yazıldığında şu kontroller otomatik yapılır:
- [ ] Yasaklı kelime var mı? (kesin, mutlaka, garanti, hata, kötü, yapın, yapınız)
- [ ] Emir kipi var mı? ("-in", "-yin", "-iniz", "-ınız" bitişleri)
- [ ] İngilizce terim yanlışlıkla çevrildi mi?
- [ ] Türkçe karakter ASCII'ye çevrildi mi?
- [ ] Her teknik terim .term span'ı ile işaretlendi mi?

Eğer bir kural ihlal edildiyse bölüm yeniden yazılır.

## Örnekler (iyi / kötü)

**Yönetici Özeti girişi:**
- ❌ "Sitenizin SEO puanı 28/100 ile düşük. Hemen müdahale edilmeli."
- ✓ "ornekmarka.com.tr üzerinde yürütülen ön denetimde, marka organik görünürlüğünün rakiplere kıyasla gelişim alanına sahip olduğu gözlemlenmektedir. Teknik altyapıda belirgin iyileştirme fırsatları, içerik tarafında ise değerlendirilmeyi bekleyen keyword alanları tespit edilmiştir."

**Teknik bulgu:**
- ❌ "Ana sayfada H1 yok, büyük hata."
- ✓ "Ana sayfada <span class=\"term\" data-term=\"H1\">H1</span> etiketinin konumlandırılmasında ele alınabilecek bir nokta öne çıkmaktadır. Arama motoru anlama katmanında öne çıkarılması için H1 yapısının yeniden düzenlenmesi değerlendirilebilir."

**Aksiyon maddesi:**
- ✓ "<strong>Title ve Meta Description optimizasyonu</strong> — öncelikli 20 sayfa için. Tahmini süre: 1 hafta. Potansiyel etki: orta-yüksek."
