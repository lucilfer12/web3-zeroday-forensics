#!/usr/bin/env python3
"""Command-line interface for Web3 ZeroDay Forensics."""
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT/'schemas/case.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
ALLOWED = set(SCHEMA['properties']['classification']['enum'])


def load_cases():
    out=[]
    for p in sorted((ROOT/'cases').glob('*.yaml')):
        out.append((p,yaml.safe_load(p.read_text(encoding='utf-8'))))
    return out


def validate(verbose=False):
    errors=[]
    seen=set()
    for path,case in load_cases():
        cid=case.get('case_id')
        if cid in seen: errors.append(f'{path}: duplicate case_id {cid}')
        seen.add(cid)
        for e in VALIDATOR.iter_errors(case):
            errors.append(f'{path}: {e.message}')
        urls=[s.get('url','') for s in case.get('sources',[])]
        if not urls: errors.append(f'{path}: no sources')
        for u in urls:
            try:
                q=urlparse(u)
                if q.scheme!='https' or not q.netloc: errors.append(f'{path}: invalid source URL {u}')
            except Exception:
                errors.append(f'{path}: invalid source URL {u}')
        cls=case.get('classification')
        if cls=='confirmed_zero_day':
            tl=case.get('timeline',{})
            if not tl.get('exploit_date') or not tl.get('patch_date'):
                errors.append(f'{path}: confirmed_zero_day requires exploit_date and patch_date')
            if case.get('evidence_grade') not in {'A','B'}:
                errors.append(f'{path}: confirmed_zero_day requires evidence grade A or B')
    if errors:
        print('VALIDATION FAILED')
        print('\n'.join(errors))
        return 1
    print(f'VALIDATION OK: {len(seen)} case records')
    return 0


def stats():
    cases=load_cases()
    by=defaultdict(Counter)
    for _,c in cases:
        by['classification'][c['classification']]+=1
        by['scope'][c['scope']]+=1
        by['bug_class'][c['root_cause']['bug_class']]+=1
        by['evidence_grade'][c.get('evidence_grade')]+=1
    print(json.dumps({k:dict(v.most_common()) for k,v in by.items()},indent=2,ensure_ascii=False))


def export_csv(path):
    rows=[]
    for _,c in load_cases():
        rows.append({'case_id':c['case_id'],'protocol':c['protocol'],'chain':c.get('chain'),'scope':c['scope'],'classification':c['classification'],'evidence_grade':c.get('evidence_grade'),'bug_class':c['root_cause']['bug_class'],'impact':c['impact']['impact_type']})
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(path)


def report():
    cases=load_cases(); out=ROOT/'analysis/reports/corpus-status.md'
    lines=['# Corpus Status','',f'Curated records: **{len(cases)}**','', '## Classification']
    cc=Counter(c['classification'] for _,c in cases)
    for k,v in cc.most_common(): lines.append(f'- `{k}`: {v}')
    lines += ['', '## Evidence grade']
    eg=Counter(c.get('evidence_grade') for _,c in cases)
    for k,v in eg.most_common(): lines.append(f'- `{k}`: {v}')
    lines += ['', '## Scope']
    sc=Counter(c['scope'] for _,c in cases)
    for k,v in sc.most_common(): lines.append(f'- `{k}`: {v}')
    out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(out)


def main():
    p=argparse.ArgumentParser(prog='zdf')
    sp=p.add_subparsers(dest='cmd',required=True)
    sp.add_parser('validate')
    sp.add_parser('stats')
    sp.add_parser('report')
    ex=sp.add_parser('export-csv'); ex.add_argument('path')
    a=p.parse_args()
    if a.cmd=='validate': return validate()
    if a.cmd=='stats': return stats() or 0
    if a.cmd=='report': return report() or 0
    if a.cmd=='export-csv': return export_csv(a.path) or 0

if __name__=='__main__': raise SystemExit(main())
