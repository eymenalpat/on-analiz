#!/usr/bin/env python3
"""on-analiz skill için setup wizard. API key'leri toplar, .env'e yazar (chmod 600)."""
import argparse
import os
import sys
from pathlib import Path

FIELDS = [
    ('DATAFORSEO_LOGIN', 'DataForSEO Login', True, False),
    ('DATAFORSEO_PASSWORD', 'DataForSEO Password', True, True),
    ('PAGESPEED_API_KEY', 'Google PageSpeed API Key (opsiyonel)', False, False),
    ('RAILWAY_TOKEN', 'Railway Token (opsiyonel, deploy için)', False, True),
    ('RAILWAY_PROJECT_ID', 'Railway Project ID (opsiyonel)', False, False),
    ('DEFAULT_LANG', 'Varsayılan dil (tr/en)', False, False),
    ('OUTPUT_DIR', 'Çıktı klasörü', False, False),
]

DEFAULTS = {
    'DEFAULT_LANG': 'tr',
    'OUTPUT_DIR': './cikti',
}


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        out[k.strip()] = v.strip()
    return out


def write_env(path: Path, values: dict):
    lines = ["# on-analiz skill credentials — auto-generated", ""]
    for key, label, required, _ in FIELDS:
        val = values.get(key, DEFAULTS.get(key, ''))
        lines.append(f"# {label}")
        lines.append(f"{key}={val}")
        lines.append("")
    path.write_text("\n".join(lines))
    path.chmod(0o600)


def prompt_value(label: str, required: bool, masked: bool, existing: str) -> str:
    hint = f" [{existing[:4]}...]" if existing else ""
    prompt_str = f"{label}{hint}: "
    if masked and sys.stdin.isatty():
        import getpass
        try:
            val = getpass.getpass(prompt_str)
        except EOFError:
            val = ''
    else:
        try:
            val = input(prompt_str).strip()
        except EOFError:
            val = ''
    if not val and existing:
        return existing
    if not val and required and not existing:
        print(f"⚠ {label} boş bırakıldı. Skill çalıştığında bu kaynak atlanacak.", file=sys.stderr)
    return val


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env-path', default=str(Path(__file__).parent.parent / '.env'))
    ap.add_argument('--non-interactive', action='store_true', help='Test için — tüm input stdin\'den satır satır okunur')
    ap.add_argument('--reset', action='store_true', help='Mevcut .env\'i sil ve baştan kur')
    args = ap.parse_args()

    env_path = Path(args.env_path)
    if args.reset and env_path.exists():
        env_path.unlink()
        print(f"Silindi: {env_path}")

    existing = load_existing(env_path)
    values = dict(existing)

    if not args.non_interactive:
        print("=" * 60)
        print("on-analiz skill — ilk kurulum")
        print("Boş bırakırsanız mevcut değer korunur (varsa).")
        print("=" * 60)

    for key, label, required, masked in FIELDS:
        values[key] = prompt_value(label, required, masked, existing.get(key, ''))

    write_env(env_path, values)
    print(f"\n✓ .env yazıldı: {env_path} (chmod 600)")


if __name__ == '__main__':
    main()
