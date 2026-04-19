# Changelog

## [1.0.0] — 2026-04-19

### Added
- İlk sürüm — `/on-analiz` user-level skill
- Pitch ve onboarding modu
- SEO + GEO checklist birleşik denetimi (kullanıcı seçimli)
- Ahrefs MCP + DataForSEO REST + WebFetch + PageSpeed entegrasyonu
- 3 checkpoint'li akış (scope / bulgu / rapor onayı)
- Inbound brand kit'li interaktif HTML rapor (sol sidebar, Bricolage Grotesque + Outfit)
- 36 terimli glossary + hover tooltip
- Setup wizard (setup.py) — API key'ler .env'e (chmod 600)
- Railway deploy opsiyonu — public URL üretimi
- Excel→JSON checklist parser (parse_checklists.py)
- Dil kuralı lint (lint_report.py) — kesin vaat / emir kipi taraması
- TDD kapsamı: parse_checklists, setup, deploy, lint için toplam 13 test
- Resume ve refresh-report modları

### Bilinçli YAGNI'ler
- Multi-agent paralel dispatch
- Ayrı Python CLI katmanı
- Screaming Frog entegrasyonu
- GSC/GA OAuth
- PDF export
- Rapor kıyaslama (önceki run diff)
- Çoklu dil çıktı (sadece Türkçe v1)
