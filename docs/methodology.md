# Methodology

## Evidence hierarchy

**A — Primary confirmation**

A protocol/vendor first-party report or another authoritative technical source explicitly connects the contract defect to the incident and gives enough timeline detail to establish exploitation relative to remediation.

**B — Corroborated**

Multiple independent technical sources agree on the contract defect and material timeline facts.

**C — Credible but incomplete**

A strong source describes the defect, but an important timeline or contract detail remains uncertain.

**D — Research lead**

The case is useful for discovery or comparison but is not sufficiently evidenced for a defensible zero-day classification.

## Review order

1. Identify the exact contract, library, compiler-generated behavior, or contract subsystem.
2. Establish the vulnerable condition from public technical evidence.
3. State the security invariant that should have held.
4. Describe the trust boundary and permission model.
5. Establish a source-backed timeline.
6. Classify the zero-day status narrowly.
7. Record the patch strategy.
8. Determine whether the patch removes the root cause or only a trigger.
9. Link variants and repeated invariant failures.
10. Derive a safe regression property.

## Important distinction

A contract exploit can be real and severe without being a zero-day. Likewise, a bug can be publicly discussed without the public having enough evidence to establish when defenders knew about it. This project preserves those distinctions.
