#!/usr/bin/env python3
"""Build a dependency-free static search page from the curated case corpus."""
from __future__ import annotations
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_cases():
    return [yaml.safe_load(p.read_text(encoding="utf-8"))
            for p in sorted((ROOT / "cases").glob("*.yaml"))]


def build():
    cases = []
    for c in load_cases():
        cases.append({
            "case_id": c["case_id"],
            "protocol": c["protocol"],
            "chain": c.get("chain"),
            "scope": c["scope"],
            "classification": c["classification"],
            "evidence_grade": c.get("evidence_grade"),
            "bug_class": c["root_cause"]["bug_class"],
            "condition": c["root_cause"].get("vulnerable_condition"),
            "invariant": c["root_cause"].get("violated_invariant"),
            "timeline": c.get("timeline", {}),
        })
    payload = json.dumps(cases, ensure_ascii=False).replace("</", "<\\/")
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Web3 ZeroDay Forensics — Search</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;background:#0b1020;color:#eef2ff}main{max-width:1100px;margin:auto;padding:28px}
input,select{padding:10px;border-radius:8px;border:1px solid #34405f;background:#121a30;color:#eef2ff;width:100%}
.controls{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:10px;margin:18px 0}
.card{background:#11182b;border:1px solid #283453;border-radius:12px;padding:16px;margin:10px 0}.meta{color:#aab5d1;font-size:.9rem}
.badge{display:inline-block;padding:3px 7px;border-radius:999px;background:#26324f;margin-right:5px;font-size:.78rem}.empty{padding:30px;text-align:center;color:#aab5d1}
@media(max-width:800px){.controls{grid-template-columns:1fr 1fr}.controls input{grid-column:1/-1}}
</style></head><body><main>
<h1>Web3 ZeroDay Forensics</h1><p>Search the curated forensic corpus. Classifications are evidence-backed and intentionally conservative.</p>
<div class="controls"><input id="q" placeholder="protocol, invariant, bug class…"><select id="classification"><option value="">All classifications</option></select><select id="grade"><option value="">All evidence grades</option></select><select id="scope"><option value="">All scopes</option></select><select id="bug"><option value="">All bug classes</option></select></div>
<div id="summary" class="meta"></div><div id="results"></div>
<script>const CASES=DATA;
const $=id=>document.getElementById(id);
function opts(id,key){const vals=[...new Set(CASES.map(x=>x[key]).filter(Boolean))].sort();for(const v of vals){const o=document.createElement('option');o.value=v;o.textContent=v;$(id).appendChild(o)}}
opts('classification','classification');opts('grade','evidence_grade');opts('scope','scope');opts('bug','bug_class');
function esc(s){return String(s??'').replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[m]))}
function render(){const q=$("q").value.toLowerCase().trim();const cls=$("classification").value,g=$("grade").value,scope=$("scope").value,bug=$("bug").value;
const rows=CASES.filter(c=>(!q||JSON.stringify(c).toLowerCase().includes(q))&&(!cls||c.classification===cls)&&(!g||c.evidence_grade===g)&&(!scope||c.scope===scope)&&(!bug||c.bug_class===bug));
$("summary").textContent=rows.length+" of "+CASES.length+" curated cases";
$("results").innerHTML=rows.length?rows.map(c=>`<article class="card"><h2>${esc(c.protocol)}</h2><div class="meta">${esc(c.case_id)} · ${esc(c.chain||"chain unknown")}</div><p><span class="badge">${esc(c.classification)}</span><span class="badge">Grade ${esc(c.evidence_grade||"-")}</span><span class="badge">${esc(c.bug_class)}</span><span class="badge">${esc(c.scope)}</span></p><p>${esc(c.condition||"")}</p><p><strong>Invariant:</strong> ${esc(c.invariant||"")}</p></article>`).join(""):"<div class='empty'>No matching cases.</div>"}
["q","classification","grade","scope","bug"].forEach(id=>$(id).addEventListener("input",render));render();</script></main></body></html>"""
    html = html.replace("DATA", payload)
    out = ROOT / "site/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out)

if __name__ == "__main__":
    build()
