import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / 'scripts' / 'lint_report.py'


def test_lint_detects_forbidden_word():
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
        f.write('<html><body><p>Bu kesin olarak yapılmalıdır, hata vardır.</p></body></html>')
        path = f.name
    r = subprocess.run(['python3', str(SCRIPT), '--file', path], capture_output=True, text=True)
    assert r.returncode != 0
    assert 'kesin' in r.stdout
    assert 'hata' in r.stdout


def test_lint_passes_clean_content():
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
        f.write('<html><body><p>Bu konu değerlendirilebilir ve geliştirme alanı sunabilir.</p></body></html>')
        path = f.name
    r = subprocess.run(['python3', str(SCRIPT), '--file', path], capture_output=True, text=True)
    assert r.returncode == 0


def test_lint_detects_imperative():
    with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
        f.write('<html><body><p>Title etiketini düzeltiniz.</p></body></html>')
        path = f.name
    r = subprocess.run(['python3', str(SCRIPT), '--file', path], capture_output=True, text=True)
    assert r.returncode != 0
    assert 'düzeltiniz' in r.stdout or 'emir' in r.stdout.lower()
