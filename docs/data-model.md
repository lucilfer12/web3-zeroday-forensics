# Data Model

The project deliberately separates **discovery metadata** from **forensic evidence**.

`corpus/discovery_queue.yaml` contains leads discovered from public incident indexes. It is not a claim that every lead is a zero-day.

`cases/*.yaml` contains curated records that have a contract-level root cause, source provenance, and explicit classification.

A future promotion should not overwrite the original lead. The lead remains the discovery provenance; the case is the reviewed analytical record.
