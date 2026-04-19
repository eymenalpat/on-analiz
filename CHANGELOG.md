# Changelog

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
