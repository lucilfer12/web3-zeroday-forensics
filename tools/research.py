#!/usr/bin/env python3
"""Research and corpus-quality utilities for Web3 ZeroDay Forensics."""
from __future__ import annotations
import argparse, json
from collections import Counter
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATE_FIELDS = ("discovery_date", "exploit_date", "patch_date", "public_disclosure_date")
CLASSIFICATIONS = (
    "confirmed_zero_day", "likely_zero_day",
    "publicly_disclosed_before_exploitation",
    "exploited_vulnerability_timeline_unknown", "not_zero_day", "excluded",
)

def load_cases():
    return [(p, yaml.safe_load(p.read_text(encoding="utf-8")))
            for p in sorted((ROOT / "cases").glob("*.yaml"))]

def load_index():
    return yaml.safe_load((ROOT / "corpus/cases.yaml").read_text(encoding="utf-8")) or []

def load_queue():
    return yaml.safe_load((ROOT / "corpus/discovery_queue.yaml").read_text(encoding="utf-8")) or []

def date_value(value):
    return date.fromisoformat(value) if value else None
def case_text(c):
    return " ".join([
        str(c.get("case_id", "")), str(c.get("protocol", "")),
        str(c.get("component", "")), str(c.get("chain", "")),
        str(c.get("scope", "")), str(c.get("classification", "")),
        str(c.get("evidence_grade", "")),
        str(c.get("root_cause", {}).get("bug_class", "")),
        str(c.get("root_cause", {}).get("vulnerable_condition", "")),
        str(c.get("root_cause", {}).get("violated_invariant", "")),
    ]).casefold()

def search(args):
    q = (args.query or "").casefold()
    rows = []
    for _, c in load_cases():
        if q and q not in case_text(c): continue
        if args.bug_class and c["root_cause"]["bug_class"] != args.bug_class: continue
        if args.classification and c["classification"] != args.classification: continue
        if args.scope and c["scope"] != args.scope: continue
        if args.grade and c.get("evidence_grade") != args.grade: continue
        if args.chain and args.chain.casefold() not in str(c.get("chain", "")).casefold(): continue
        rows.append(c)
    rows = rows[:args.limit]
    data = [{
        "case_id": c["case_id"], "protocol": c["protocol"],
        "chain": c.get("chain"), "scope": c["scope"],
        "classification": c["classification"],
        "evidence_grade": c.get("evidence_grade"),
        "bug_class": c["root_cause"]["bug_class"],
        "timeline": c.get("timeline", {}),
    } for c in rows]
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    print("case_id | protocol | classification | grade | bug_class")
    print("-" * 95)
    for c in data:
        print("{} | {} | {} | {} | {}".format(
            c["case_id"], c["protocol"], c["classification"],
            c["evidence_grade"] or "-", c["bug_class"]))
    print("found {}".format(len(data)))

def coverage():
    cases = [c for _, c in load_cases()]
    fields = {f: sum(bool(c.get("timeline", {}).get(f)) for c in cases) for f in DATE_FIELDS}
    source_roles = Counter(s.get("role") for _, c in load_cases() for s in c.get("sources", []))
    complete = sum(all(c.get("timeline", {}).get(f) for f in DATE_FIELDS) for c in cases)
    print(json.dumps({
        "curated_cases": len(cases), "discovery_leads": len(load_queue()),
        "timeline_present": fields,
        "timeline_missing": {f: len(cases) - n for f, n in fields.items()},
        "complete_timelines": complete,
        "evidence_grades": dict(Counter(c.get("evidence_grade") for c in cases)),
        "source_roles": dict(source_roles),
        "primary_source_cases": sum(
            any(s.get("role") == "primary" for s in c.get("sources", [])) for c in cases
        ),
    }, indent=2, ensure_ascii=False))

def audit():
    errors = []
    warnings = []
    paths = {p.stem: p for p in (ROOT / "cases").glob("*.yaml")}
    index = {x["case_id"] for x in load_index()}
    if set(paths) != index:
        errors.append("case index mismatch")
    tax = yaml.safe_load((ROOT / "taxonomy/bug-classes.yaml").read_text(encoding="utf-8")) or {}
    known = {x for values in tax.values() for x in values}
    boundaries = set(yaml.safe_load(
        (ROOT / "taxonomy/trust-boundaries.yaml").read_text(encoding="utf-8")) or [])
    for path, c in load_cases():
        bug = c["root_cause"]["bug_class"]
        if bug not in known: errors.append("{}: unknown bug_class {}".format(path, bug))
        boundary = c.get("root_cause", {}).get("trust_boundary")
        if boundary and boundary not in boundaries: errors.append("{}: unknown trust_boundary {}".format(path, boundary))
        if not any(s.get("role") == "primary" for s in c.get("sources", [])):
            warnings.append("{}: missing primary source".format(path))
        tl = c.get("timeline", {})
        try:
            disc = date_value(tl.get("discovery_date")); exp = date_value(tl.get("exploit_date"))
            patch = date_value(tl.get("patch_date")); public = date_value(tl.get("public_disclosure_date"))
        except ValueError as e:
            errors.append("{}: {}".format(path, e)); continue
        if disc and exp and disc > exp: errors.append("{}: discovery after exploit".format(path))
        if exp and patch and exp > patch and c["classification"] in {"confirmed_zero_day", "likely_zero_day"}:
            errors.append("{}: zero-day classification conflicts with exploit after patch".format(path))
        if public and exp and public < exp and c["classification"] == "not_zero_day":
            errors.append("{}: not_zero_day conflicts with prior disclosure".format(path))
        for rel in c.get("relations", {}).get("related_cases", []) or []:
            if rel not in paths: errors.append("{}: missing related case {}".format(path, rel))
        variant = c.get("relations", {}).get("variant_of")
        if variant and variant not in paths: errors.append("{}: missing variant case {}".format(path, variant))
    if errors:
        print("AUDIT FAILED"); print("\n".join(errors)); return 1
    print("AUDIT OK: {} case records".format(len(paths)))
    for warning in warnings:
        print("WARNING: " + warning)
    return 0

def build_index():
    rows = []
    for _, c in load_cases():
        rows.append({
            "case_id": c["case_id"], "protocol": c["protocol"], "chain": c.get("chain"),
            "scope": c["scope"], "classification": c["classification"],
            "evidence_grade": c.get("evidence_grade"), "bug_class": c["root_cause"]["bug_class"],
            "timeline": c.get("timeline", {}),
            "invariant_tags": sorted(c.get("research", {}).get("invariant_tags", [])),
            "sources": [s.get("url") for s in c.get("sources", [])],
        })
    out = ROOT / "analysis/generated/search-index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out)

def write_reports():
    cases = [c for _, c in load_cases()]
    out = ROOT / "analysis/reports/timeline-coverage.md"
    lines = ["# Timeline Coverage", "", "| Field | Present | Missing |", "| --- | ---: | ---: |"]
    for f in DATE_FIELDS:
        n = sum(bool(c.get("timeline", {}).get(f)) for c in cases)
        lines.append("| {} | {} | {} |".format(f, n, len(cases) - n))
    complete = sum(all(c.get("timeline", {}).get(f) for f in DATE_FIELDS) for c in cases)
    lines += ["", "Complete four-field timelines: **{}**".format(complete), ""]
    out.write_text("\n".join(lines), encoding="utf-8")

    gap = ROOT / "analysis/reports/evidence-gaps.md"
    lines = ["# Evidence Gaps", "", "This report records missing evidence fields; it never invents values.", ""]
    for c in cases:
        missing = [f for f in DATE_FIELDS if not c.get("timeline", {}).get(f)]
        primary = any(s.get("role") == "primary" for s in c.get("sources", []))
        if missing or not primary:
            notes = []
            if missing: notes.append("missing: " + ", ".join(missing))
            if not primary: notes.append("no primary source")
            lines.append("- {}: {}".format(c["case_id"], "; ".join(notes)))
    gap.write_text("\n".join(lines) + "\n", encoding="utf-8")
    build_index()
    print(out); print(gap)
def main():
    ap = argparse.ArgumentParser(prog="research")
    sp = ap.add_subparsers(dest="cmd", required=True)
    se = sp.add_parser("search")
    se.add_argument("--query"); se.add_argument("--bug-class")
    se.add_argument("--classification", choices=CLASSIFICATIONS)
    se.add_argument("--scope"); se.add_argument("--chain")
    se.add_argument("--grade", choices=["A", "B", "C", "D"])
    se.add_argument("--limit", type=int, default=50); se.add_argument("--json", action="store_true")
    sp.add_parser("coverage"); sp.add_parser("audit"); sp.add_parser("build-index"); sp.add_parser("report")
    a = ap.parse_args()
    if a.cmd == "search": return search(a) or 0
    if a.cmd == "coverage": return coverage() or 0
    if a.cmd == "audit": return audit()
    if a.cmd == "build-index": return build_index() or 0
    if a.cmd == "report": return write_reports() or 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
