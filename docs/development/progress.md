# Implementation progress

Snapshot updated: 23 November 2026. This tracker begins from reviewed source presence,
not assumed successful runtime behavior. Update it after each verified stage.

| Stage | Work | Current status | Completion evidence |
|---|---|---|---|
| 00 | Baseline/work board | COMPLETE — scope, service ownership, decisions, state review and requirement stories recorded | [Stage 00 evidence](../testing/evidence/stage-00.md); static baseline and Compose configuration checks passed |
| 01 | Existing stack/build verification | COMPLETE — nine backend tests, locked frontend install/build/typecheck, eleven healthy containers, smoke and outage/recovery pass | [Stage 01 evidence](../testing/evidence/stage-01.md) and [runtime artifact](../testing/evidence/stage-01-runtime.json) |
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
| 16 | Reliable outbox publication | Foundation topology verified; business outbox/dispatcher not implemented | Stage 01 broker tests pass; no business publication completion |
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
- [x] Inspect Git and exclude browser/profile/generated private state.
- [x] Establish initial commit `1418bfd`, publish to `Bbuddhika/AgriFlow`, create `dev` and the Stage 01 feature branch.
- [x] Configure blank local secrets while preserving existing nonempty settings.
- [x] Obtain Docker engine and dependency registry access.
- [x] Resolve/install dependencies and include the reviewed frontend lockfile in the Stage 01 changes.
- [x] Run all nine backend tests, frontend build/typecheck, Compose smoke and outage/recovery verification.
- [x] Save Stage 01 evidence. Next implementation stage: Stage 02.
