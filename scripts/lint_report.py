#!/usr/bin/env python3
"""Üretilen HTML raporu yasaklı kelime ve emir kipi için tarar."""
import argparse
import re
import sys
from pathlib import Path

FORBIDDEN_WORDS = [
    'kesin', 'mutlaka', 'garanti', 'garantiliyoruz',
    'hata', 'kötü', 'berbat', 'yanlış', 'başarısız',
    'ciddi problem', 'büyük sorun',
]

IMPERATIVE_SUFFIXES = [
    r'\b\w+iniz\b',
    r'\b\w+ınız\b',
    r'\b\w+unuz\b',
    r'\b\w+ünüz\b',
    r'\byapın\b', r'\bedin\b', r'\bkurun\b', r'\bekleyin\b',
    r'\bdüzeltin\b', r'\bdüzeltiniz\b',
]

ALLOWLIST_IMPERATIVE = {
    'kullanılabiliniz', 'değerlendirilebiliniz',
}


def strip_html(html: str) -> str:
    # Crude: tag'leri sil
    text = re.sub(r'<script.*?</script>', '', html, flags=re.S | re.I)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.S | re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return text


def lint(text: str):
    issues = []
    for w in FORBIDDEN_WORDS:
        for m in re.finditer(rf'\b{re.escape(w)}\b', text, re.I):
            issues.append(('YASAKLI_KELIME', w, m.start()))
    for pat in IMPERATIVE_SUFFIXES:
        for m in re.finditer(pat, text, re.I):
            word = m.group(0).lower()
            if word in ALLOWLIST_IMPERATIVE:
                continue
            issues.append(('EMIR_KIPI_OLABILIR', word, m.start()))
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True)
    args = ap.parse_args()

    html = Path(args.file).read_text()
    text = strip_html(html)
    issues = lint(text)

    if not issues:
        print("✓ Dil lint temiz.")
        sys.exit(0)

    print(f"⚠ {len(issues)} uyarı bulundu:\n")
    for kind, word, pos in issues:
        ctx = text[max(0, pos-40):pos+len(word)+40].replace('\n', ' ')
        print(f"  [{kind}] '{word}' — ... {ctx} ...")
    sys.exit(1)


if __name__ == '__main__':
    main()
