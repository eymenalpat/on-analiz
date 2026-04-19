import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / 'scripts' / 'deploy.py'


def test_deploy_copies_report_and_regenerates_index():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'rapor.html'
        src.write_text('<html><body>test report</body></html>')
        workspace = Path(tmp) / 'railway-workspace'
        (workspace / 'reports').mkdir(parents=True)
        (workspace / 'index.html').write_text('<html></html>')

        r = subprocess.run(
            ['python3', str(SCRIPT), '--skip-deploy',
             '--report', str(src),
             '--marka-slug', 'ornekmarka',
             '--tarih', '2026-04-19',
             '--workspace', str(workspace)],
            capture_output=True, text=True
        )
        assert r.returncode == 0, r.stderr
        dest = workspace / 'reports' / 'ornekmarka-2026-04-19.html'
        assert dest.exists()
        assert 'test report' in dest.read_text()
        index = (workspace / 'index.html').read_text()
        assert 'ornekmarka-2026-04-19.html' in index


def test_deploy_requires_railway_token_env():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'rapor.html'
        src.write_text('<html></html>')
        workspace = Path(tmp) / 'railway-workspace'
        (workspace / 'reports').mkdir(parents=True)
        r = subprocess.run(
            ['python3', str(SCRIPT),
             '--report', str(src),
             '--marka-slug', 'x',
             '--tarih', '2026-04-19',
             '--workspace', str(workspace)],
            capture_output=True, text=True, env={'PATH': '/usr/bin:/bin'}
        )
        assert r.returncode != 0
        assert 'RAILWAY_TOKEN' in r.stderr or 'railway' in r.stderr.lower()
