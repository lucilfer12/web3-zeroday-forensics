# Web3 ZeroDay Forensics

**Web3 ZeroDay Forensics** is a defensive research corpus and analysis framework for publicly documented smart-contract vulnerabilities, exploited DeFi logic failures, bridge verification failures, and related Web3 security events.

The project is intentionally forensic rather than exploit-oriented. Its purpose is to answer:

- What exact contract condition failed?
- Which security invariant should have held?
- What trust boundary was crossed?
- What evidence establishes reachability and impact?
- Was the defect exploited before remediation was available?
- Did the patch remove the root cause or only the observed trigger?
- Does the same invariant failure appear in other protocols?

## Research pipeline

```text
Public incident / disclosure
            |
            v
      Source provenance
            |
            v
 Contract-level verification
            |
            v
      Timeline analysis
            |
            v
    ZeroDay classification
            |
            v
 Invariant / boundary model
            |
            +------> Patch-diff fingerprint
            |
            +------> Variant relationships
            |
            +------> Safe regression property
            |
            v
      Research reports
```

## Scope

Included:

- EVM smart contracts
- Solidity/Vyper contract systems
- DeFi protocols and vaults
- Bridges and cross-chain message contracts
- On-chain governance
- Oracle-dependent contracts
- Tokens with security-relevant custom logic
- Upgradeable proxies and initialization flows
- Contract-based signature and authorization logic

Excluded from the core corpus when no contract defect is the primary cause:

- stolen or leaked private keys
- phishing and social engineering
- DNS/frontend compromise
- malicious insider actions without a contract vulnerability
- ordinary market losses without a contract-level security defect

## Zero-Day rule

The repository does **not** equate "public exploit" with "zero-day". A case is only promoted to `confirmed_zero_day` when public evidence supports a timeline in which the relevant contract vulnerability was exploited before a practical remediation or effective mitigation was available.

Every case carries a classification and evidence grade. Uncertain cases remain visible as research leads instead of being silently promoted.

## Safety boundary

This repository contains normalized facts, high-level root-cause analysis, invariants, provenance, patch observations, and safe local regression models. It does not contain weaponized exploit automation, live-target attack scripts, private credentials, or instructions for attacking deployed systems.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m tools.zdf validate
python -m tools.zdf stats
python -m tools.zdf report
pytest -q
python -m tools.research audit
python -m tools.research coverage
python -m tools.research report
python tools/build_site.py
```

## Research and search

The project now has a read-only research layer for querying the curated corpus, measuring missing evidence, checking taxonomy and case relationships, and generating a deterministic static search page.

```bash
python -m tools.research search --query Euler
python -m tools.research search --bug-class oracle_manipulation
python -m tools.research search --classification confirmed_zero_day --grade A
python -m tools.research coverage
python -m tools.research audit
```

`site/index.html` is generated from the curated corpus. It contains no backend and makes no claims beyond the committed case records.

## Refreshing the public Web3 incident index

`tools/sync_defihacklabs.py` pulls the public DeFiHackLabs README/archive index and normalizes incident metadata without importing exploit code into this project.

```bash
python -m tools.sync_defihacklabs --out corpus/upstream/defihacklabs_index.jsonl
```

## Repository layout

```text
corpus/       normalized records and upstream indices
cases/        curated forensic case files
schemas/      JSON schema and data contracts
taxonomy/     bug classes, trust boundaries, impacts
analysis/     generated statistics, similarities, timelines
lab/          safe abstract regression models
tools/        ingestion, validation, promotion, reporting
docs/         methodology and contribution guidance
tests/        corpus and tool tests
```

## Provenance

Primary sources are preferred. Technical analyses, protocol post-mortems, auditor write-ups, public transaction references, and incident indexes may be linked as secondary evidence. The project stores references and extracted structured facts rather than republishing copyrighted reports.
