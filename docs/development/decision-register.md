# Stage 00 decision register

Reviewed 21 November 2026. Open decisions are release gates, not invented answers.
Owner of stakeholder follow-up: project developer. Record date, evidence and
consequences here when resolving a row.

| ID | Decision / current position | Status | Resolve before |
|---|---|---|---|
| D01 | Separate Spring Boot services following SwiftDrop's layout; service ownership in ADR 003 | SELECTED by prior user instruction | Applied scaffold |
| D02 | FARMER, BUYER, ADMINISTRATOR only; no participant impersonation | BASELINE | Stage 03 permissions |
| D03 | Atomic stock/reservation/inspection/finance operations stay in market core | DESIGN recorded in ADR 003 | Stage 02 transaction design |
| D04 | Reservation duration 24 hours, no extensions; validate travel/queue feasibility with stakeholders | DEFAULT; validation open | Stages 07–09 release |
| D05 | Grade definitions/thresholds by produce type | OPEN; do not invent numeric thresholds | Stage 04 administration / Stage 11 inspection |
| D06 | Late arrival and no-show default 15-minute grace, audited rebooking | DEFAULT; market validation open | Stages 09–10 release |
| D07 | Reference-price provider, access/reuse rights and refresh method; 48-hour freshness default | OPEN provider/access | Stage 18 integration |
| D08 | Authentication/session implementation, service verification/revocation and verified recovery delivery | OPEN | Stage 03 protected routing |
| D09 | Audit/transaction retention, encrypted backup destination, retention and restore target | OPEN | Stage 23 real deployment |
| D10 | Chat provider/model, disclosure/data-use settings, cost ceiling; seven-day app retention default | OPEN provider/settings | Stages 20–21 real data |
| D11 | RabbitMQ retry/DLQ retention, monitoring, replay authority and core readiness during outage | OPEN | Stages 16–17 release |
| D12 | Submission deadline, weekly hours, assessment language/architecture expectations | OPEN; historical 22-week estimate is provisional | Re-estimate delivery plan before committing dates |
| D13 | Baseline `1418bfd` published to `Bbuddhika/AgriFlow`; `main` → `dev` → `feature/agriflow-s01-foundation-verification` | OBSERVED 23 November 2026 | Feature PRs target `dev`; release PRs target `main` |
| D14 | Public exception limited to foundation taxonomy, system metadata and health | RETAINED from baseline | Revisit at Stage 03; no public lots or private records |
| D15 | Payments record external collections/payouts separately; no money movement or automatic commission | BASELINE | Stages 13–15 |

An open external decision does not block unrelated scaffold work. Record the
decision before releasing its dependent behavior. No remote URL, deadline,
grade threshold, recovery provider or retention agreement has been assumed.
