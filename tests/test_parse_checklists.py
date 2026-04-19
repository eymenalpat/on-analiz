import json
import subprocess
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parent.parent / 'scripts' / 'parse_checklists.py'
OUT_DIR = Path(__file__).parent.parent / 'assets' / 'checklists'
SEO_XLSX = '/Users/eymenalpat/domain-audit/SEO Checklist & Roadmap - Masterpiece v2021 (1).xlsx'
GEO_XLSX = '/Users/eymenalpat/domain-audit/GEO-AEO-Checklist Inbound (1).xlsx'


def test_script_runs_without_error():
    r = subprocess.run(['python3', str(SCRIPT), '--seo', SEO_XLSX, '--geo', GEO_XLSX, '--out', str(OUT_DIR)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_expected_files_produced():
    expected = ['seo-ecommerce.json', 'seo-local.json', 'seo-enterprise.json',
                'seo-international.json', 'seo-blog.json', 'geo-eticaret.json', 'geo-hizmet.json']
    for name in expected:
        p = OUT_DIR / name
        assert p.exists(), f"missing {name}"
        d = json.loads(p.read_text())
        assert 'items' in d and isinstance(d['items'], list)


def test_seo_ecommerce_has_content():
    data = json.loads((OUT_DIR / 'seo-ecommerce.json').read_text())
    assert len(data['items']) >= 25, f"e-commerce checklist should have >=25 items, got {len(data['items'])}"
    first = data['items'][0]
    for key in ['type', 'task', 'questions']:
        assert key in first


def test_geo_eticaret_has_phases():
    data = json.loads((OUT_DIR / 'geo-eticaret.json').read_text())
    phases = {item.get('phase') for item in data['items']}
    assert 'Faz 1' in phases, f"expected Faz 1 in phases, got {phases}"


def test_idempotency():
    first_run = (OUT_DIR / 'geo-eticaret.json').read_text()
    subprocess.run(['python3', str(SCRIPT), '--seo', SEO_XLSX, '--geo', GEO_XLSX, '--out', str(OUT_DIR)], capture_output=True, text=True)
    second_run = (OUT_DIR / 'geo-eticaret.json').read_text()
    assert first_run == second_run, "output should be idempotent"
