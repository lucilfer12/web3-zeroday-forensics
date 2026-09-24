#!/usr/bin/env python3
"""Find related cases by invariant tags and bug classes; purely descriptive, no exploit generation."""
from __future__ import annotations
import json
from pathlib import Path
import yaml

def load(root):
    rows=[]
    for p in sorted((root/'cases').glob('*.yaml')):
        c=yaml.safe_load(p.read_text())
        tags=set(c.get('research',{}).get('invariant_tags',[]))
        tags.add(c['root_cause']['bug_class'])
        rows.append((c,tags))
    return rows

def main():
    root=Path(__file__).resolve().parents[1]
    rows=load(root); result=[]
    for i,(a,ta) in enumerate(rows):
        for b,tb in rows[i+1:]:
            inter=len(ta&tb); union=len(ta|tb)
            score=inter/union if union else 0
            if score>=0.34:
                result.append({'a':a['case_id'],'b':b['case_id'],'score':round(score,3),'shared':sorted(ta&tb)})
    result.sort(key=lambda x:x['score'],reverse=True)
    out=root/'analysis/generated/similarity.json'
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(out)
if __name__=='__main__': main()
