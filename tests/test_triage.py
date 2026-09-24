import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)


def test_triage_summary():
    r = run('-m', 'tools.triage', 'summary')
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data['leads'] == 108
    assert data['statuses']['unverified_lead'] == 108


def test_triage_search_filter():
    r = run('-m', 'tools.triage', 'search', '--reported-class', 'Access Control', '--json')
    assert r.returncode == 0
    rows = json.loads(r.stdout)
    assert rows
    assert all('access control' in str(x.get('reported_class')).casefold() for x in rows)


def test_triage_report_is_generated():
    r = run('-m', 'tools.triage', 'report')
    assert r.returncode == 0
    assert (ROOT / 'analysis/reports/discovery-triage.md').exists()
