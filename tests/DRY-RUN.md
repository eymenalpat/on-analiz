# Dry-Run Test Prosedürü

Skill tamamlandıktan sonra gerçek API çağrısı yapmadan uçtan uca doğrulama.

## Ön koşul

- Skill `~/.claude/skills/on-analiz/` altına kurulmuş
- `python3 scripts/parse_checklists.py` bir kez çalıştırılmış, JSON'lar var
- `.env` örnek değerlerle dolu (gerçek key şart değil, dry-run için)

## Adımlar

1. **Setup testi:**

   ```bash
   python3 scripts/setup.py --env-path /tmp/test.env --non-interactive <<< $'loginX\npassX\n\n\n\n\n\n'
   cat /tmp/test.env
   ```

   Beklenen: `DATAFORSEO_LOGIN=loginX` satırı.

2. **Parse checklist:**

   ```bash
   ls assets/checklists/*.json | wc -l
   ```

   Beklenen: `7`

3. **Stil referansını aç:**

   ```bash
   open assets/examples/stil-referansi.html
   ```

   Beklenen: Sol sidebar, koyu yeşil + coral, Bricolage Grotesque / Outfit fontlar, tooltip hover çalışıyor.

4. **Template + fixture birleştirme (manuel):**

   Python ile örnek bir birleştirme yap:

   ```python
   from pathlib import Path
   import json
   base = Path('~/.claude/skills/on-analiz').expanduser()
   template = (base / 'assets/report-template.html').read_text()
   brand = (base / 'assets/brand.css').read_text()
   gloss = (base / 'assets/glossary.json').read_text()
   data = json.loads((base / 'tests/fixtures/raw-data-ornek.json').read_text())

   out = (template
       .replace('{{BRAND_CSS}}', brand)
       .replace('{{GLOSSARY_JSON}}', gloss)
       .replace('{{MARKA_ADI}}', data['meta']['marka'])
       .replace('{{MARKA_DOMAIN}}', data['meta']['marka'])
       .replace('{{TARIH}}', data['meta']['tarih'])
       .replace('{{MOD_ROZET}}', 'PITCH · SEO+GEO')
       .replace('{{YONETICI_OZETI}}', '<p>Örnek özet paragrafı — dry-run placeholder.</p>')
       .replace('{{METRIKLER}}', '<p>Örnek metrikler.</p>')
       .replace('{{TEKNIK}}', '<p>Örnek teknik.</p>')
       .replace('{{KEYWORDS}}', '<p>Örnek keyword.</p>')
       .replace('{{FIRSATLAR}}', '<p>Örnek fırsat.</p>')
       .replace('{{SERP}}', '<p>Örnek SERP.</p>')
       .replace('{{RAKIPLER}}', '<p>Örnek rakip.</p>')
       .replace('{{GEO}}', '<p>Örnek GEO.</p>')
       .replace('{{BACKLINK}}', '<p>Örnek backlink.</p>')
       .replace('{{AKSIYON}}', '<p>Örnek aksiyon.</p>')
       .replace('{{YONTEM}}', '<p>Örnek yöntem.</p>'))

   Path('/tmp/dry-run-rapor.html').write_text(out)
   print('yazıldı')
   ```

   Beklenen: `/tmp/dry-run-rapor.html` browser'da açılır, tüm bölümler ve sol sidebar görünür.

5. **Lint test:**

   ```bash
   python3 scripts/lint_report.py --file /tmp/dry-run-rapor.html
   ```

   Beklenen: `✓ Dil lint temiz.` (dry-run placeholder'lar nötr)

6. **Deploy test (skip-deploy modunda):**

   ```bash
   python3 scripts/deploy.py --skip-deploy --report /tmp/dry-run-rapor.html \
     --marka-slug ornekmarka --tarih 2026-04-19 \
     --workspace railway-workspace
   ```

   Beklenen: `railway-workspace/reports/ornekmarka-2026-04-19.html` var, `index.html` güncellendi.

## Hepsi geçiyorsa → skill kullanıma hazır.
