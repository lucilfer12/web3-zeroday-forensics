#!/usr/bin/env python3
"""Refresh public DeFiHackLabs incident metadata without importing exploit code."""
from __future__ import annotations
import argparse, json, re, urllib.request
from pathlib import Path

BASE='https://raw.githubusercontent.com/SunWeb3Sec/DeFiHackLabs/main/'
FILES=['README.md']+[f'past/{y}/README.md' for y in range(2020,2026)]
PAT=re.compile(r'^###\s+(\d{8})\s+(.+?)(?:\s+-\s+(.+?))?\s*$',re.M)

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Web3-ZeroDay-Forensics/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r:
        return r.read().decode('utf-8','replace')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='corpus/upstream/defihacklabs_index.jsonl'); args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; out=root/args.out; out.parent.mkdir(parents=True,exist_ok=True)
    rows={}
    for name in FILES:
        try: text=fetch(BASE+name)
        except Exception as e:
            print(f'warning: {name}: {e}')
            continue
        for m in PAT.finditer(text):
            key=(m.group(1),re.sub(r'\s+',' ',m.group(2).strip()))
            rows[key]={'date':m.group(1),'name':key[1],'reported_class':(m.group(3).strip() if m.group(3) else 'unclassified'),'upstream':'DeFiHackLabs','source_file':name}
    with out.open('w',encoding='utf-8') as f:
        for row in sorted(rows.values(),key=lambda x:(x['date'],x['name'])):
            f.write(json.dumps(row,ensure_ascii=False)+'\n')
    print(f'wrote {len(rows)} upstream records to {out}')
if __name__=='__main__': main()
