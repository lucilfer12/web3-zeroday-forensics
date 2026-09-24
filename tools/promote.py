#!/usr/bin/env python3
"""Promote a discovery lead into a forensic case only after supplying evidence-backed fields."""
from pathlib import Path
import argparse
import yaml

ROOT=Path(__file__).resolve().parents[1]

CLASSIFICATIONS=[
    'confirmed_zero_day',
    'likely_zero_day',
    'publicly_disclosed_before_exploitation',
    'exploited_vulnerability_timeline_unknown',
    'not_zero_day',
    'excluded',
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('lead')
    ap.add_argument('--classification',required=True,choices=CLASSIFICATIONS)
    ap.add_argument('--grade',required=True,choices=['A','B','C','D'])
    args=ap.parse_args()

    q=yaml.safe_load((ROOT/'corpus/discovery_queue.yaml').read_text())
    hit=next((x for x in q if x['lead_id']==args.lead),None)
    if not hit:
        raise SystemExit('unknown lead')

    if args.classification=='confirmed_zero_day' and args.grade not in {'A','B'}:
        raise SystemExit('confirmed_zero_day requires grade A or B')

    print(f"Lead {hit['lead_id']} is eligible for curation as {args.classification} with evidence grade {args.grade}.")
    print('Create a case file with complete sources, timeline, invariant, and patch fields before promotion.')

if __name__=='__main__':
    main()
