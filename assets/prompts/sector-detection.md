# Sektör Tespiti Promptu

Bu prompt Checkpoint #1'de kullanılır. Kullanıcının verdiği marka domain'inden anasayfa WebFetch ile çekilir, aşağıdaki sınıflandırma yapılır.

## Girdi
- Marka anasayfa HTML (ilk 5000 karakter)
- Marka domain'i
- Kullanıcının checkpoint #1'de seçtiği sektör (override)

## Görev
Anasayfa içeriğinden şu sınıflandırma yapılır:

**sektor:** bir tanesi seçilir:
- `e-ticaret` — ürün listeleme, sepet, kategoriler görünüyor
- `hizmet` — B2B veya B2C hizmet sunumu (ajans, danışmanlık, ustalık)
- `lokal` — adres, telefon, harita, şube bilgisi öne çıkıyor (restoran, mağaza, klinik)
- `saas` — yazılım ürünü, fiyatlama tabloları, "pricing / plans"
- `publisher` — blog / haber / içerik ağırlıklı
- `enterprise` — kurumsal site, yatırımcı ilişkileri, multi-bölüm
- `diger` — yukarıdaki hiçbirine uymuyor

**aktif_checklist_dosyalari:**
- `e-ticaret` → `seo-ecommerce.json` + `geo-eticaret.json`
- `hizmet` → `seo-ecommerce.json` + `geo-hizmet.json` (fallback)
- `lokal` → `seo-local.json` + `geo-hizmet.json`
- `saas` → `seo-ecommerce.json` + `geo-hizmet.json`
- `publisher` → `seo-blog.json` + `geo-hizmet.json`
- `enterprise` → `seo-enterprise.json` + `geo-hizmet.json`
- `diger` → `seo-ecommerce.json` + `geo-hizmet.json` (generic)

**Önemli:** Kullanıcının seçtiği sektör her zaman ÖNCELİKLİDİR. Bu prompt sadece **öneri/doğrulama** amaçlı, kullanıcı override edebilir.

## Çıktı Formatı

JSON:
```json
{
  "sektor": "e-ticaret",
  "sektor_kullanici_secimi_ile_uyumlu": true,
  "aktif_checklist_dosyalari": ["seo-ecommerce.json", "geo-eticaret.json"],
  "uyum_notu": "Anasayfada ürün listeleme, sepet ve kategori yapısı gözlemleniyor; e-ticaret sınıflandırması kullanıcı seçimi ile uyumlu."
}
```
