# Stage NN evidence — replace with the implemented stage title

Copy this template into `docs/testing/evidence/stage-NN.md` when recording an
actual stage run. The example destination is not existing completion evidence.
Use synthetic data and redact credentials, tokens and unnecessary personal data.

## Scope and environment

| Field | Actual value |
|---|---|
| Stage and requirement IDs | Fill in |
| Date/time and timezone | Fill in |
| Operator | Fill in |
| Commit SHA / source snapshot | Fill in; record no Git SHA if not using Git |
| Application image tags/digests | Fill in |
| OS, Java, Maven, Node and Docker versions | Fill in |
| Database/broker versions and fixture | Fill in |
| Provider/model/prompt version, if applicable | Fill in |

## Acceptance scenarios

| Scenario/test name | Requirement | Expected | Observed | Result | Evidence path |
|---|---|---|---|---|---|
| Replace with an actual scenario | FRxx/NFR-xx | Fill in | Fill in after execution | NOT RUN | Fill in |

Record commands exactly, with sanitized output or a linked retained log. Include
wrong-owner/role cases and relevant duplicate, expiry, conflict/outage and
concurrency behavior. Distinguish tests that exist from tests actually run.

## Reproduction

```text
Replace with actual commands, fixture setup and input values.
```

## Results and remaining work

- Passing checks: fill in after execution.
- Failures or blocked checks: record the concrete cause and the rerun needed.
- Changed behavior/API/migration: summarize the implemented result.
- Unresolved risks or external decisions: fill in.
- Tracker/traceability updates: link the changed stage and requirement rows.

Do not mark this document PASS or a stage COMPLETE without observed results.
Performance/recovery claims need measured workload/environment/timing; screenshots
alone cannot prove transaction correctness, throughput or backup restorability.
