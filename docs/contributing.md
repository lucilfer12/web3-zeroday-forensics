# Contributing

## Case requirements

A new case should contain:

- stable `case_id`
- protocol and chain
- exact component or subsystem
- contract-level root cause
- violated invariant
- impact
- source provenance
- timeline fields when known
- evidence grade
- current zero-day classification

## Source quality

Prefer:

1. protocol post-mortems and official advisories
2. original technical researchers
3. reputable security firms and auditor reports
4. public on-chain references
5. incident indexes as discovery aids

Avoid making incident indexes the sole source for a zero-day claim.

## Safe reproduction

Use abstract state machines or toy contracts. Do not add code that attacks live deployments or contains operational exploit transactions.
