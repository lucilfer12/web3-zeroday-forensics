#!/usr/bin/env python3
"""Triage the discovery queue without auto-promoting research leads."""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_queue():
    return yaml.safe_load((ROOT / 'corpus/discovery_queue.yaml').read_text(encoding='utf-8')) or []

def normalize_label(value):
    value = re.sub(r'[-_/]+', ' ', str(value or '').strip().casefold())
    return re.sub(r'\s+', ' ', value)

def matches(row, args):
    q = (args.query or '').casefold()
    blob = json.dumps(row, ensure_ascii=False).casefold()
    return ((not q or q in blob) and
            (not args.status or row.get('status') == args.status) and
            (not args.reported_class or normalize_label(row.get('reported_class')) == normalize_label(args.reported_class)))

def summary():
    rows = load_queue()
    classes = Counter(normalize_label(x.get('reported_class')) for x in rows)
    years = Counter(str(x.get('incident_date',''))[:4] for x in rows)
    statuses = Counter(x.get('status') for x in rows)
    print(json.dumps({'leads': len(rows), 'statuses': dict(statuses), 'years': dict(sorted(years.items())), 'reported_classes': dict(classes.most_common())}, indent=2, ensure_ascii=False))
def search(args):
    rows = [r for r in load_queue() if matches(r, args)][:args.limit]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    print('lead_id | incident_date | name | reported_class | status')
    print('-' * 110)
    for r in rows:
        print('{} | {} | {} | {} | {}'.format(r.get('lead_id'), r.get('incident_date'), r.get('name'), r.get('reported_class'), r.get('status')))
    print('found {}'.format(len(rows)))

def report():
    rows = load_queue()
    statuses = Counter(x.get('status') for x in rows)
    classes = Counter(normalize_label(x.get('reported_class')) for x in rows)
    out = ROOT / 'analysis/reports/discovery-triage.md'
    lines = ['# Discovery Triage', '', 'Leads remain unverified until source, contract condition, impact, and timeline evidence are reviewed.', '', '## Queue', '']
    for k, v in statuses.most_common(): lines.append('- {}: {}'.format(k, v))
    lines += ['', '## Reported classes', '']
    for k, v in classes.most_common(): lines.append('- {}: {}'.format(k, v))
    lines += ['', '## Review order', '', '1. Verify the exact affected contract or subsystem.', '2. Establish the root cause from technical evidence.', '3. Establish exploit and remediation dates separately.', '4. Check whether evidence supports the proposed classification.', '5. Preserve the original lead when creating a curated case.', '']
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(out)

def main():
    ap = argparse.ArgumentParser(prog='triage')
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('summary'); sp.add_parser('report')
    se = sp.add_parser('search'); se.add_argument('--query'); se.add_argument('--status'); se.add_argument('--reported-class'); se.add_argument('--limit', type=int, default=50); se.add_argument('--json', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'summary': return summary() or 0
    if a.cmd == 'report': return report() or 0
    if a.cmd == 'search': return search(a) or 0
    return 2

if __name__ == '__main__': raise SystemExit(main())
