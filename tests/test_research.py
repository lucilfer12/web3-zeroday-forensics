import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


def test_research_search_json():
    r = run('-m', 'tools.research', 'search', '--bug-class', 'oracle_manipulation', '--json')
    assert r.returncode == 0
    rows = json.loads(r.stdout)
    assert rows
    assert all(x['bug_class'] == 'oracle_manipulation' for x in rows)


def test_research_coverage_reports_known_gaps():
    r = run('-m', 'tools.research', 'coverage')
    assert r.returncode == 0
    assert '"curated_cases": 20' in r.stdout
    assert '"discovery_leads": 108' in r.stdout
def test_research_audit_allows_documented_warnings():
    r = run('-m', 'tools.research', 'audit')
    assert r.returncode == 0
    assert 'AUDIT OK: 20 case records' in r.stdout
    assert 'missing primary source' in r.stdout


def test_build_site_contains_curated_records():
    r = run('tools/build_site.py')
    assert r.returncode == 0
    html = (ROOT / 'site/index.html').read_text(encoding='utf-8')
    assert 'Web3 ZeroDay Forensics' in html
    assert 'euler-v1-2023' in html
    assert 'pancakebunny-oracle-variant' in html
    assert 'const CASES=' in html
