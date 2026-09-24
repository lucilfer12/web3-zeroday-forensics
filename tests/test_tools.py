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


def _sample_case(**timeline_overrides):
    case = {
        'case_id': 'test-date-contract',
        'protocol': 'Example',
        'scope': 'defi',
        'classification': 'likely_zero_day',
        'evidence_grade': 'C',
        'timeline': {
            'discovery_date': None,
            'exploit_date': '2023-01-01',
            'patch_date': '2023-01-02',
            'public_disclosure_date': None,
        },
        'root_cause': {
            'bug_class': 'access_control',
            'vulnerable_condition': 'test',
            'violated_invariant': 'test',
        },
        'impact': {'impact_type': 'loss'},
        'sources': [{'url': 'https://example.com/source', 'role': 'primary'}],
    }
    case['timeline'].update(timeline_overrides)
    return case


def test_validator_rejects_malformed_date(monkeypatch, capsys):
    import tools.zdf as zdf
    case = _sample_case(exploit_date='2023/01/01')
    monkeypatch.setattr(zdf, 'load_cases', lambda: [(Path('bad-date.yaml'), case)])
    assert zdf.validate() == 1
    output = capsys.readouterr().out
    assert "'2023/01/01' is not a 'date'" in output


def test_timeline_handles_malformed_date():
    from tools.timeline import classify
    case = _sample_case(exploit_date='2023/01/01')
    cls, reason = classify(case)
    assert cls == 'exploited_vulnerability_timeline_unknown'
    assert reason == "invalid exploit date: '2023/01/01'"


def test_timeline_reports_insufficient_grade():
    from tools.timeline import classify
    case = _sample_case()
    case['evidence_grade'] = 'D'
    cls, reason = classify(case)
    assert cls == 'exploited_vulnerability_timeline_unknown'
    assert reason == 'exploitation predates patch but evidence grade is insufficient'




def test_timeline_rejects_discovery_after_exploitation():
    from tools.timeline import classify
    case = _sample_case(discovery_date='2023-01-03')
    cls, reason = classify(case)
    assert cls == 'exploited_vulnerability_timeline_unknown'
    assert reason == 'discovery date is after exploitation date'


def test_timeline_uses_public_disclosure_date():
    from tools.timeline import classify
    case = _sample_case(public_disclosure_date='2022-12-01')
    cls, reason = classify(case)
    assert cls == 'publicly_disclosed_before_exploitation'
    assert reason == 'public disclosure predates exploitation'

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
