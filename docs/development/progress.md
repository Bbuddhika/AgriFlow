# Implementation progress

Snapshot updated: 21 November 2026. This tracker begins from reviewed source presence,
not assumed successful runtime behavior. Update it after each verified stage.

| Stage | Work | Current status | Completion evidence |
|---|---|---|---|
| 00 | Baseline/work board | COMPLETE — scope, service ownership, decisions, state review and requirement stories recorded | [Stage 00 evidence](../testing/evidence/stage-00.md); static baseline and Compose configuration checks passed |
| 01 | Existing stack/build verification | IN PROGRESS — reactor packages and four gateway tests pass; runtime unverified | [Recorded checks](../testing/evidence/stage-00.md); Docker Linux engine unavailable; frontend and container integration checks pending |
| 02 | Shared transactions/security primitives | Partial error/security config only; audit/idempotency/outbox not implemented | None |
| 03 | Identity/accounts/roles | NOT STARTED | None |
| 04 | Catalog administration/harvests | Read-only catalog source only; stage not complete | None |
| 05 | Lots/stock/QR | NOT STARTED | None |
| 06 | Search/private offers | NOT STARTED | None |
| 07 | Atomic acceptance/reservations | NOT STARTED | None |
| 08 | Expiry/cancellation | NOT STARTED | None |
| 09 | Vehicle visit booking | NOT STARTED | None |
| 10 | Check-in/queue/bays | NOT STARTED | None |
| 11 | Inspection/stock adjustments | NOT STARTED | None |
| 12 | Shortage consent | NOT STARTED | None |
| 13 | Deductions/sale/settlement | NOT STARTED | None |
| 14 | Collections/payouts | NOT STARTED | None |
| 15 | Financial/stock corrections | NOT STARTED | None |
| 16 | Reliable outbox publication | Broker config/topology source only; dispatcher not implemented | Existing broker test source, not passing runtime evidence |
| 17 | Idempotent notifications | NOT STARTED | None |
| 18 | Prices/admin settings | NOT STARTED | None |
| 19 | Reports/history/audit views | NOT STARTED | None |
| 20 | Authorized assistant tools | NOT STARTED | None |
| 21 | Controlled chat/sessions/UI | NOT STARTED | None |
| 22 | Integrated/NFR/AI acceptance | NOT STARTED | None |
| 23 | Hosted deployment/recovery | NOT STARTED | None |
| 24 | Final guides/demo/handover | NOT STARTED | None |

Use `IN PROGRESS`, `BLOCKED — <concrete reason>`, `READY FOR REVIEW` and
`COMPLETE — <evidence link>` as work proceeds. A stage is complete only when its
"done when" conditions and relevant requirement tests pass. A blocked check
remains blocked until a rerun establishes the result.

## Current work

[ADR 003](../architecture/003-separate-backend-services.md) replaces the original
single-backend deployment with five backend services and four owned stores.
The [work board](work-board.csv) covers all 41 traced requirements. Open external
decisions and their release gates are in the [decision register](decision-register.md).
Critical market state transitions remain in the transaction-owning market core.
Only foundation catalog behavior and the gateway are implemented; new identity,
notification and assistant services remain closed scaffolds.

## First work session checklist

- [x] Read the member guide and repository review.
- [x] Record outstanding stakeholder decisions; deadline and weekly effort remain explicitly open.
- [x] Inspect existing local Git (`main`, no commits/remote) and exclude browser/profile/generated private state.
- [ ] Establish the reviewed initial commit and connect the actual remote when available.
- [ ] Configure local secrets without overwriting an existing `.env`.
- [ ] Obtain Docker engine and dependency registry access.
- [ ] Resolve/install dependencies and commit the reviewed frontend lockfile.
- [ ] Run backend tests, frontend build/typecheck and Compose smoke verification.
- [ ] Save Stage 01 evidence, then start Stage 02.
