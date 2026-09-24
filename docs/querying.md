# Querying the Corpus

`tools/research.py` is the read-only research interface over curated case files.

## Search

Use one or more filters. Search text scans the case identifier, protocol, component, chain, classification, evidence grade, bug class, vulnerable condition, and invariant.

```bash
python -m tools.research search --query Euler
python -m tools.research search --bug-class oracle_manipulation
python -m tools.research search --classification publicly_disclosed_before_exploitation --grade A
python -m tools.research search --chain Ethereum --scope defi
```

Add `--json` for machine-readable output.

## Coverage

`coverage` reports how much of the corpus has source-backed timeline fields, complete four-field timelines, evidence grades, and source-role coverage.

```bash
python -m tools.research coverage
```

The current corpus intentionally keeps unknown dates as `null`. Missing values are a research backlog, not values to infer from incident-day timestamps.
## Audit

`audit` checks relationships between curated files and the compact index, verifies taxonomy references, checks chronology when dates exist, and flags cases without a primary source.

```bash
python -m tools.research audit
```

Warnings are printed for evidence-quality gaps that do not invalidate the schema.

## Generated artifacts

`python -m tools.research report` updates:

- `analysis/reports/timeline-coverage.md`
- `analysis/reports/evidence-gaps.md`
- `analysis/generated/search-index.json`

`python tools/build_site.py` regenerates `site/index.html`, a dependency-free search UI that embeds the committed metadata snapshot.
