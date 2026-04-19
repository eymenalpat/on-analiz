import os
import subprocess
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / 'scripts' / 'setup.py'


def test_setup_writes_env_with_stdin_input():
    with tempfile.TemporaryDirectory() as tmp:
        env_path = Path(tmp) / '.env'
        stdin = "mylogin\nmypass\n\n\n\n\n\n"
        r = subprocess.run(
            ['python3', str(SCRIPT), '--non-interactive', '--env-path', str(env_path)],
            input=stdin, capture_output=True, text=True
        )
        assert r.returncode == 0, r.stderr
        content = env_path.read_text()
        assert 'DATAFORSEO_LOGIN=mylogin' in content
        assert 'DATAFORSEO_PASSWORD=mypass' in content


def test_setup_sets_permissions_600():
    with tempfile.TemporaryDirectory() as tmp:
        env_path = Path(tmp) / '.env'
        stdin = "a\nb\n\n\n\n\n\n"
        subprocess.run(['python3', str(SCRIPT), '--non-interactive', '--env-path', str(env_path)], input=stdin, text=True)
        mode = oct(env_path.stat().st_mode & 0o777)
        assert mode == '0o600', f"expected 0o600, got {mode}"


def test_setup_preserves_existing_values_on_update():
    with tempfile.TemporaryDirectory() as tmp:
        env_path = Path(tmp) / '.env'
        env_path.write_text("DATAFORSEO_LOGIN=oldlogin\nDATAFORSEO_PASSWORD=oldpass\nPAGESPEED_API_KEY=keepme\n")
        env_path.chmod(0o600)
        stdin = "\n\n\n\n\n\n\n"
        subprocess.run(['python3', str(SCRIPT), '--non-interactive', '--env-path', str(env_path)], input=stdin, text=True)
        content = env_path.read_text()
        assert 'DATAFORSEO_LOGIN=oldlogin' in content
        assert 'PAGESPEED_API_KEY=keepme' in content
