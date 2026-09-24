# Zero-Day Definition

A **zero-day** in this corpus is a contract-level vulnerability that was exploited before an effective remediation or mitigation was available to the defender, supported by public evidence.

The incident date alone is not enough.

The record must distinguish, where known:

- first discovery
- internal awareness, if publicly documented
- first exploitation
- first public disclosure
- patch or mitigation availability

## Allowed classifications

- `confirmed_zero_day`
- `likely_zero_day`
- `publicly_disclosed_before_exploitation`
- `exploited_vulnerability_timeline_unknown`
- `not_zero_day`
- `excluded`

## Promotion rule

No case is promoted to `confirmed_zero_day` merely because:

- funds were stolen;
- a PoC exists;
- an incident was called "zero-day" on social media; or
- a CVE exists.

The repository requires a defensible timeline and evidence grade.
