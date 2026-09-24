#!/usr/bin/env python3
"""Conservative timeline classifier. It never upgrades a case without sufficient dates/evidence."""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
import yaml

VALID={'confirmed_zero_day','likely_zero_day','publicly_disclosed_before_exploitation','exploited_vulnerability_timeline_unknown','not_zero_day','excluded'}

def parse(x, field):
    if x is None or x == '':
        return None
    try:
        return date.fromisoformat(x)
    except (TypeError, ValueError):
        raise ValueError(f'invalid {field}: {x!r}')

def classify(c):
    tl=c.get('timeline',{})
    try:
        disc=parse(tl.get('discovery_date'),'discovery date')
        exp=parse(tl.get('exploit_date'),'exploit date')
        patch=parse(tl.get('patch_date'),'patch date')
        public=parse(tl.get('public_disclosure_date'),'public disclosure date')
    except ValueError as e:
        return 'exploited_vulnerability_timeline_unknown',str(e)
    grade=c.get('evidence_grade')
    if disc and exp and disc > exp:
        return 'exploited_vulnerability_timeline_unknown','discovery date is after exploitation date'
    if not exp: return 'exploited_vulnerability_timeline_unknown','missing exploit date'
    if exp and public and public < exp: return 'publicly_disclosed_before_exploitation','public disclosure predates exploitation'
    if exp and patch and exp < patch and grade in {'A','B'}: return 'confirmed_zero_day','exploitation predates patch with strong evidence'
    if exp and patch and exp < patch and grade=='C': return 'likely_zero_day','exploitation predates patch but evidence is incomplete'
    if exp and patch and exp < patch and grade in {'D',None}: return 'exploited_vulnerability_timeline_unknown','exploitation predates patch but evidence grade is insufficient'
    if exp and patch and exp >= patch: return 'not_zero_day','exploitation after remediation date'
    return 'exploited_vulnerability_timeline_unknown','insufficient timeline evidence'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('case'); a=ap.parse_args()
    p=Path(a.case); c=yaml.safe_load(p.read_text()); cls,reason=classify(c)
    print(f'{c["case_id"]}: {cls} — {reason}')
if __name__=='__main__': main()
