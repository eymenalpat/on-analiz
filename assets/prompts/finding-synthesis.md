# Bulgu Sentezi Promptu — Checkpoint #2

Ham veri toplandıktan sonra, HTML rapor yazılmadan ÖNCE bu prompt çalışır. Amaç: kullanıcıya raporun taslak ana başlıklarını göstermek, onay almak.

## Girdi

`cikti/{marka-slug}/{tarih}/raw-data.json` dosyası. İçerik:
- `marka`: domain, sektör, ülke, dil
- `metrikler`: DR, organic_traffic, organic_keywords, referring_domains
- `top_pages`: sayfa listesi + trafik
- `organic_keywords`: keyword listesi + pozisyon + hacim
- `rakipler`: her rakip için metrikler
- `opportunity_keywords`: rakiplerde olan markada olmayan keyword'ler
- `serp_snapshots`: top keyword'ler için SERP verisi
- `teknik_bulgular`: WebFetch'ten gelen title/H1/meta/canonical/schema/robots.txt durumu
- `backlink_profile`: anchor dağılımı, RD tier dağılımı
- `geo_durumu`: GEO checklist eşlemesi + AI görünürlük sinyalleri
- `veri_eksikleri`: hangi kaynaklardan ne çekilemedi

## Görev

Aşağıdaki bölümler için **kısa (1-2 cümle) özet + öncelik** üret:

1. **Metrikler özeti** — "DR X, rakip ort. Y; trafik Z/ay, rakip ort. W/ay"
2. **Teknik durum** — kaç kritik, kaç orta, en dikkat çeken 2 bulgu
3. **Keyword fırsatı** — rakiplerde var markada yok keyword sayısı + tahmini potansiyel trafik
4. **Rakip portresi** — en güçlü 1, en hızlı büyüyen 1
5. **GEO snapshot** — AI platformlarında marka anılma sinyalleri (varsa sayı, yoksa "ilk ölçüm")
6. **En güçlü 3-5 "öncelikli bulgu"** — raporun ana mesajı olacak

## Dil

`language-rules.md` kurallarına tabi. Özet Türkçe, nazik ton, kesin vaat yok. Rakamları aralık ile ver.

## Çıktı Formatı (kullanıcıya gösterilir)

```markdown
## Bulgu Özeti (Checkpoint #2)

**Metrikler:**
- Marka DR 18 (rakip ortalaması ~34 civarı)
- Organik trafik ~2.1K/ay (rakip ortalaması ~18K/ay)

**Teknik durum:**
- 5 öncelikli, 12 orta, 8 takip edilebilir bulgu
- En dikkat çekenler: Ana sayfa H1 konumlandırması, title yapısındaki tekrarlar

**Keyword fırsatı:**
- 87 rakip-özel keyword (markada henüz yok), tahmini potansiyel ~12K/ay

**Rakip portresi:**
- En güçlü profil: rakip-a.com.tr (DR 52, 45K trafik)
- En hızlı büyüyen: rakip-b.com (son 6 ayda %+38)

**GEO snapshot:**
- AI Overview'da marka anılmıyor (ilk ölçüm); rakip-a test sorguların 3'ünde görünüyor

**Öncelikli Bulgular (raporun ana odağı):**
1. Teknik altyapıda ele alınabilecek 5 nokta (öncelikli)
2. Lokal SEO tarafında GMB profillerinin derinleştirilmesi fırsat sunabilir
3. 87 fırsat keyword içinden 20 tanesi yüksek niyet taşıyor
4. GEO tarafında içerik formatı ve schema derinliği değerlendirilebilir
5. Backlink profilinde tematik çeşitliliğin artırılması fayda sağlayabilir

**Veri eksikleri:** rakip-c.com robots.txt 403 → o rakip için kısmi veri

---

**Onay seçenekleri:**
- Rapora geç
- Ek bulgu ekle
- Şu bölümü tekrar tara
- İptal
```
