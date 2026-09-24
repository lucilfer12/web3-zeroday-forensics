from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True)

def test_validator():
    r=run('-m','tools.zdf','validate')
    assert r.returncode==0, r.stdout+r.stderr

def test_stats():
    r=run('-m','tools.zdf','stats')
    assert r.returncode==0


def test_sync_parser_accepts_unsuffixed_entries():
    import re

    pattern = re.compile(
        r'^###\s+(\d{8})\s+(.+?)(?:\s+-\s+(.+?))?\s*$',
        re.M,
    )

    text = """### 20260414 MONA LisaVault
### 20240610 UwuLend - Price Manipulation
"""

    matches = list(pattern.finditer(text))
    assert len(matches) == 2
    assert matches[0].group(1) == "20260414"
    assert matches[0].group(2).strip() == "MONA LisaVault"
    assert matches[0].group(3) is None
    assert matches[1].group(3).strip() == "Price Manipulation"


def test_export_csv_empty_corpus(tmp_path, monkeypatch):
    import tools.zdf as zdf

    monkeypatch.setattr(zdf, "load_cases", lambda: [])
    out = tmp_path / "empty.csv"

    zdf.export_csv(out)

    assert not out.exists() or out.read_text() == ""


def test_promote_rejects_invalid_classification():
    r = run(
        '-m', 'tools.promote',
        'defihacklabs-20251201-001',
        '--classification', 'not_a_real_classification',
        '--grade', 'C'
    )
    assert r.returncode != 0
    assert 'invalid choice' in r.stderr


def test_promote_accepts_valid_classification():
    r = run(
        '-m', 'tools.promote',
        'defihacklabs-20251201-001',
        '--classification', 'likely_zero_day',
        '--grade', 'C'
    )
    assert r.returncode == 0
    assert 'eligible for curation' in r.stdout
