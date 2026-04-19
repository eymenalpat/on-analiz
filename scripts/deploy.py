#!/usr/bin/env python3
"""on-analiz raporunu Railway'e deploy eder, public URL döndürür."""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def rebuild_index(workspace: Path):
    reports_dir = workspace / 'reports'
    reports = sorted([p for p in reports_dir.glob('*.html') if p.name != 'index.html'], reverse=True)
    items_html = ""
    for r in reports:
        name = r.stem
        items_html += f'      <li><a href="reports/{r.name}">{name}</a></li>\n'
    if not items_html:
        items_html = "      <li>Henüz rapor yayınlanmamış.</li>\n"
    index_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <title>Inbound — Ön Analiz Raporları</title>
  <style>
    body {{ font-family: sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; background: #FEFFFA; color: #10332F; }}
    h1 {{ font-weight: 800; }}
    a {{ color: #FF7B52; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ padding: 12px; border-bottom: 1px solid #E3E9E7; }}
    .meta {{ color: #6E6C83; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>Ön Analiz Raporları</h1>
  <p class="meta">Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
  <ul>
{items_html}  </ul>
</body>
</html>
"""
    (workspace / 'index.html').write_text(index_html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', required=True, help='Kaynak rapor HTML dosyası')
    ap.add_argument('--marka-slug', required=True)
    ap.add_argument('--tarih', required=True, help='YYYY-MM-DD')
    ap.add_argument('--workspace', required=True, help='railway-workspace/ dizini')
    ap.add_argument('--service', default='on-analiz-reports')
    ap.add_argument('--skip-deploy', action='store_true', help='Test için — dosya kopyala, railway up atma')
    args = ap.parse_args()

    src = Path(args.report)
    if not src.exists():
        sys.exit(f"Rapor bulunamadı: {src}")

    workspace = Path(args.workspace)
    reports_dir = workspace / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)

    dest_name = f"{args.marka_slug}-{args.tarih}.html"
    dest = reports_dir / dest_name
    shutil.copy2(src, dest)
    print(f"✓ kopyalandı: {dest}")

    rebuild_index(workspace)
    print("✓ index yeniden üretildi")

    if args.skip_deploy:
        return

    token = os.environ.get('RAILWAY_TOKEN')
    if not token:
        sys.exit("RAILWAY_TOKEN env değişkeni bulunamadı. Setup wizard'ı çalıştırın.")

    if not shutil.which('railway'):
        sys.exit("railway CLI bulunamadı. Kurulum: brew install railway")

    print("railway up çağırılıyor...")
    proc = subprocess.run(
        ['railway', 'up', '--service', args.service],
        cwd=workspace.parent, env={**os.environ, 'RAILWAY_TOKEN': token},
        capture_output=True, text=True
    )
    if proc.returncode != 0:
        sys.exit(f"railway up fail:\n{proc.stderr}")

    for line in proc.stdout.splitlines():
        if 'up.railway.app' in line or 'https://' in line:
            print(line)
    print(f"\n✓ Deploy tamamlandı. Rapor: https://<service>.up.railway.app/reports/{dest_name}")
    try:
        subprocess.run(['pbcopy'], input=f"https://<service>.up.railway.app/reports/{dest_name}", text=True)
        print("(URL clipboard'a kopyalandı)")
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    main()
