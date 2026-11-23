# Dambulla AgriFlow — requirements review and documentation plan

Historical version notice: [v1.5 roles and negotiation](srs-v1.5-roles-and-negotiation.md) supersedes earlier five-role and price-listing clauses. Use the v1.5 PDF as the current consolidated baseline.

Review date: 3 November 2026  
Source: `Dambulla_AgriFlow_Complete_Requirements_v1.3 (1).docx`, version 1.3, draft dated 31 October 2026.  
Status: review proposal; business decisions and supervisor approval remain pending.

Update, 3 November 2026: the user selected a reservation period of at least one day, assigned payment handling to administration, and delegated the remaining principal business-rule choices. See [SRS v1.4 business-rule amendments](srs-v1.4-business-rules.md) for the resulting 24-hour policy and decisions D01–D06. This review remains a historical analysis of v1.3; its two-hour references and pending P0 recommendations are superseded by that amendment.

## 1. Review conclusion

The SRS provides a strong starting point for an individual project. It already includes role boundaries, FR01–FR22, a 22-week delivery plan, concurrency rules, a logical data model, sample APIs, and a constrained read-only AI assistant. Keep this overall scope. Update the document before treating it as an implementation baseline: several operational and financial exceptions do not yet have deterministic rules or sufficient acceptance criteria.

Only the supplied DOCX exists in the project folder at review time. No source code, separate implementation plan, prior SRS, hospitality reference, tests, or deployment configuration were available. References to earlier documents were reviewed as statements in v1.3, not independently verified. This review evaluates the supplied requirements; it does not validate market practices, external APIs, current dependency versions, legal compliance, or feasibility against an actual deadline.

The original DOCX has not been edited. Recommendations below are not automatically new approved requirements.

## 2. Product understanding

AgriFlow coordinates a single agricultural wholesale market through a responsive web application. Farmers register produce; buyers make offers; farmers accept offers to reserve stock; operators coordinate vehicle visits and unloading; inspectors establish physical quality and weight; buyers confirm purchases; administrators record payment evidence. The software records trades and settlements but does not transfer money.

The main journey is:

`Account → harvest → lot → offer → reservation → vehicle visit → inspection → sale → settlement → payment evidence`

Visits can be booked without a reservation. A lot can have multiple buyers and partial sales. The model assistant reads authorized application information and approved help; it has no authority to change business records.

### Actors

| Actor | Required capabilities | Main boundary |
|---|---|---|
| Farmer | Own profile, harvests, lots, offers, reservations, visit bookings, queue, receipts and payment status | Cannot change inspected grades or payment entries |
| Buyer | Profile, search, offers, reservations, inspected purchase confirmation and purchase history | Own transactions only |
| Operator | Capacity, slots, gate check-in, queues and unloading | No payment confirmation |
| Inspector | Weight, grades, damage, inspection history and reinspection | No sale/payment override |
| Administrator | Accounts/roles, catalog, prices, reports, audit and authorized payment records | Privileged changes audited; exact operational access needs a matrix |
| AI assistant | Six read-only question types | Inherits caller permissions; not an additional privileged role |

Trader/commission-agent workflows are deferred. Whether a person can hold multiple active roles, and any separation-of-duty constraints, still needs a decision.

## 3. Functional requirement inventory

IDs below preserve the source numbering. These are condensed requirements, not replacements for the original detailed clauses.

| ID | Required behavior | Acceptance emphasis |
|---|---|---|
| FR01 | Accounts, sign-in, account status, roles and access control | Restricted actions denied server-side; session expiry/revocation |
| FR02 | Farmer profile and harvest registration | Ownership, produce type, positive kg, planned arrival and validation |
| FR03 | Traceable lots and QR lookup | Immutable unique IDs; QR grants no private-data access; manual lookup |
| FR04 | Buyer search and offers | Type/kg/grade/arrival filters; positive quantity and proposed price |
| FR05 | Farmer acceptance/rejection and reservations | Atomic availability check; two-hour expiry in current baseline; release once |
| FR06 | Vehicle visits and slots | Owned lots, vehicle identity, capacity safety, booking without a buyer |
| FR07 | Gate and unloading queue | Valid transitions, FIFO within eligible zone/slot, dispatch capacity, late/no-show handling |
| FR08 | Quality inspection | Actual kg, grade, damage/time, declared grade retained, rejection and correction history |
| FR09 | Buyer purchase confirmation | Valid unexpired reservation plus inspection; exactly one sale; partial lot sales |
| FR10 | Settlements, receipts and payment entries | Decimal gross/deductions/net; unpaid by default; partial payments; idempotency and reversals |
| FR11 | Reference prices | Manual/CSV entry, produce/market/unit/source/date, missing/stale indication |
| FR12 | In-app notifications | Own unread events; accepted offers, expiry, visit changes, inspection and sale; independent of trade success |
| FR13 | Administration and daily reports | Account/catalog/zone management; sold kg, gross, payments and visits reconcile with records |
| FR14 | Audit and corrections | Actor/time/entity/action/reason; completed financial records corrected through linked reversals |
| FR15 | AI system help | Approved role-visible articles with title/link and version provenance |
| FR16 | AI reference-price lookup | Stored price, source, effective date, unit and freshness; no invented values |
| FR17 | AI own queue status | Authorized visit only; clarify multiple matches; current facts |
| FR18 | AI produce search | Validated bounded filters, visible lots, declared/inspected distinction |
| FR19 | AI own reservations | Fresh owner-authorized status and expiry |
| FR20 | AI own trade summary | Participant-authorized backend totals; receipt never implies payment |
| FR21 | AI controlled tool execution | Allowlisted schemas/tools, identity derived from authentication, no writes or arbitrary execution |
| FR22 | AI failure/session control | Session ownership, history clearing, provider fallback and no fabricated data |

### Supporting requirements that must not be lost

- Several lots may originate from one harvest; several lots may travel in one visit; one lot may support several reservations and sales.
- Availability excludes sold, reserved and lost stock. Expired reservations must not consume availability even before cleanup runs.
- Inspection rejection blocks sale. Inspected shortages require explicit reconciliation with affected buyers before confirmation.
- Quantity and money use decimal arithmetic. Currency is LKR; quantity unit is kg. Final money rounds to two decimal places.
- Store agreed prices, deduction amounts and applied rates historically so configuration changes cannot change receipts.
- Reject deductions above gross; do not count the same wastage as both reduced weight and a deduction.
- Confirmation/payment retries use actor-scoped idempotency and request hashes; changed input with the same key conflicts.
- Reference prices are informative, not the sale price. Proposed staleness threshold is 48 hours.
- Queue uses check-in order within eligible zone and slot, with visit ID as tie-breaker. Proposed late grace is 15 minutes.
- Transactions, locks/version checks, foreign keys and uniqueness constraints protect stock, slots, sales and occupancy.
- APIs use `/api/v1`, validated JSON, pagination, consistent errors and authorization. Appendix C is illustrative, not complete OpenAPI.
- Audit information is application append-only unless stronger tamper protection is actually implemented.
- AI source cards come from backend facts; changing facts are retrieved again. Invalid numeric/status output falls back to deterministic text.
- AI starts in English; translation keys are prepared. Sinhala/Tamil implementation and evaluation are deferred unless explicitly required.
- Proposed AI limits: 1,000 input characters, 10 requests/minute/user, four tool executions and three model calls per turn, 20-second deadline, bounded context/output/retries and configured daily budget.
- Proposed chat retention is seven days, with deletion and clear-history controls. Provider disclosure and retention settings need review before real personal data use.

## 4. Quality and delivery requirements

Review IDs below are new tracking labels, not original SRS identifiers.

| Review ID | Source target | Required evidence |
|---|---|---|
| NFR-01 | Common API p95 <1 second, 25 concurrent users, 10 minutes, 10,000 seeded lots; model requests excluded | Load script, environment, endpoint mix and latency/error results |
| NFR-02 | 200 active seeded visits; committed queue changes visible within five seconds | Contention and refresh tests |
| NFR-03 | No negative stock, excess slot bookings or duplicate confirmed sales | Concurrent reservation/booking/expiry/confirmation tests |
| NFR-04 | AI p95 ≤15 seconds with five concurrent chats; fallback by 20 seconds | Latency and provider-failure results |
| NFR-05 | AI ≥36/40 correct or appropriate clarifications; no permission/write-prevention failures | Fixed evaluation set plus at least 12 adversarial/permission cases |
| NFR-06 | Daily encrypted off-host backup; restore ≤4 hours; potential data loss ≤24 hours | Backup configuration and timed restore record |
| NFR-07 | Responsive at 360 px and desktop; keyboard, labels, focus, readable errors and non-colour status cues | Journey-based accessibility/usability checks |
| NFR-08 | Credential protection, minimal personal data, owned chats, redacted logs | Permission tests and configuration review |
| NFR-09 | Connectivity required for writes; safe retry without duplication | Failed-network/repeated-submit demonstrations |
| NFR-10 | Single-host deployment with HTTPS, health checks, secrets and rollback instructions | Deployment walkthrough; no production HA claim |

The SRS also requires migrations, CI, setup documentation, user guidance and a demonstration. These are delivery requirements even though they do not all have FR IDs.

## 5. Required clarifications and proposed SRS amendments

Priority P0 means resolve before the affected schema/state machine is implemented. P1 means specify before the feature is implemented. None of the proposed resolutions below is an approved market policy.

| Priority / reference | Gap or conflict | Recommended amendment |
|---|---|---|
| P0 D01 — §6.4, App. A | Two-hour reservation begins at acceptance, potentially before travel; purchase requires inspection | Choose a policy after checking travel/queue times. Retain two hours as the current draft rule until changed explicitly. Specify boundary timing and whether any extension is allowed |
| P0 D02 — §4.2.4, App. A/B | Confirmed/provisional/measured kg and loss adjustments could double-subtract an inspection shortage | Define a single inventory ledger or authoritative quantity basis, adjustment signs and which weight supersedes which. Specify withdrawal handling, which is mentioned at closure but absent from the availability formula |
| P0 D03 — App. A | Reconciliation is required but no actor, allocation order or consent process is specified | Define who proposes reduced/cancelled allocations, how buyers agree, transaction locking and when sales become eligible again |
| P0 D04 — §4.2.5, App. A | Payer/payee, payment amount basis and deduction authority are unclear | Define whether recorded payments settle buyer gross debt or farmer net entitlement, who authorizes each deduction, required evidence, overpayment handling and reversal limits |
| P0 D05 — FR14, App. B | Completed sale reversal is required but only payment reversal has explicit model support | Specify sale/settlement reversal linkage and effects on stock, reservations, receipts and reports. Distinguish erroneous records from physical returns |
| P0 D06 — §4.2.3, App. A | CALLED may not occupy capacity yet; simultaneous dispatch can exceed unloading capacity | Define capacity acquisition/release, atomic dispatch, skip/recall transitions and treatment of occupied bays after failures |
| P1 D07 — FR04, App. B | FR04 requires a positive price while data guidance allows nonnegative prices | Choose whether zero-price trades are permitted; align validation, constraints and acceptance tests |
| P1 D08 — FR09, App. A | Partial lot sales are clear; partial confirmation of one reservation is not | Recommended simple rule: one reservation confirms its entire agreed quantity once; a changed quantity requires an explicit amendment/replacement policy |
| P1 D09 — App. A | Offer states are incomplete; repeated acceptance/rejection/cancellation is unspecified | Define offer state machine, actor permissions, one reservation per accepted offer and retry responses |
| P1 D10 — FR06/07 | Booking appears both farmer-selected and automatically earliest-eligible; early arrivals and no-show cutoff unclear | Specify booking selection, slot eligibility, time boundaries, departure status, rebooking history and release of capacity |
| P1 D11 — App. B | A lot can be linked to multiple visits without eligibility rules | Decide whether repeat trips are allowed; prevent incompatible simultaneous active visits; require ownership consistency |
| P1 D12 — FR08 | Grade catalog, reject criteria, damage treatment and inspection timing undefined | Define allowed grades per produce, authority for reinspection, damaged-weight meaning and restrictions after sales |
| P1 D13 — FR01 | Registration, verification, recovery, staff provisioning and suspension effects underspecified | Specify account lifecycle and whether suspended actors' active commitments can still be resolved by authorized staff |
| P1 D14 — §4.1/4.2.6 | Operator configures capacity while admin also manages zones/settings | Create action-by-role/ownership matrix; explicitly decide shared privileges rather than assuming admin bypass |
| P1 D15 — FR11 | Import validation and duplicates only partly specified | Define CSV columns, price vs range rules, row-level errors, duplicate/revision policy and stale-date calculation |
| P1 D16 — FR12/13 | Notifications and reports lack full event/date semantics | Define recipients, read status, deduplication/retry, reporting timezone, sales/payment date basis and reversal treatment |
| P1 D17 — §9/App. B/D | Retention and evidence handling remain proposals | Specify data categories, retention decisions, deletion/anonymization interaction with audit, and whether payment evidence is text/reference or an uploaded file |
| P1 D18 — §4.3/App. D | Performance workload and AI scoring are not fully reproducible | Define endpoint mix, hardware, error threshold, evaluation fixtures/rubric, timeout measurement and daily AI budget behavior |
| P1 D19 — §5/6.4 | 22 weeks is not tied to available hours or an actual submission date | Confirm dates, weekly hours, assessor requirements, languages and architecture constraints before committing |

### Examples to add to acceptance criteria

1. Inspection reconciliation: provisional 100 kg, 80 kg reserved, measured 70 kg. No sale confirms until an explicit permitted reconciliation resolves the shortage; the 30 kg reduction is applied once.
2. Withdrawal: withdrawing 10 kg from an otherwise free 100 kg lot yields 90 kg available and an auditable reason, under the approved withdrawal policy.
3. Dispatch race: two operators call different visits when one bay is free; only one capacity allocation commits.
4. Sale correction: a reversed sale affects sold kg, payment balance and daily report totals according to the agreed correction policy without deleting history.
5. Boundary expiry: confirmation at the defined expiry instant has one deterministic outcome; retry cannot recreate a sale or release stock twice.
6. Repeat offer acceptance: the same accepted offer cannot create a second reservation.
7. Payment correction: a reversal cannot reverse more than the eligible original amount; remaining balance is recomputed correctly.
8. Account suspension: existing reservations and future login/access follow the explicitly agreed lifecycle policy.

## 6. Documentation to prepare first

| Order | Deliverable | Contents / completion condition |
|---|---|---|
| 1 | Project charter and validation notes | Problem evidence vs assumptions, users, objectives, scope, constraints, deadline and available hours |
| 2 | Decision register | D01–D19, owner, options, decision, rationale, date and affected requirements; unresolved items remain visibly pending |
| 3 | SRS v1.4 | Preserve FR IDs; add clause-level sub-IDs, glossary, permissions matrix, exception rules, NFR IDs, verification methods and revision record |
| 4 | Use cases and workflow/state diagrams | Five roles, normal/alternate paths; offers, lots, reservations, visits, inspections and financial corrections |
| 5 | ERD and field dictionary | Cardinalities, ownership, units, precision, nullability, constraints, indexes, history, retention and ledger rules |
| 6 | Wireframes | Login/profile, harvest/lot, buyer offers/reservations, operator queue, inspection, payments/reports and chat; empty/error/expired/conflict states |
| 7 | Architecture and sequence diagrams | Browser/API/database, domain modules, transaction boundaries, expiry jobs, authorization, AI/tool boundary and backup/deployment topology |
| 8 | OpenAPI contract | All required operations, request/response schemas, auth, errors, pagination, transitions, timestamps and idempotency |
| 9 | Requirements traceability and test plan | Each FR/sub-clause/NFR → use case → screen/API → data rule → test → evidence/status |
| 10 | Delivery backlog and milestone plan | Dependency-ordered stories tied to requirements, estimates, risks and completion evidence |
| Ongoing | Operational and assessment documents | Setup, deploy/rollback, backup/restore, user guide, test reports, AI evaluation, demo script and final report |

Create requirements and designs before their implementation, but fill observed results only after execution. Avoid writing a complete speculative API specification before the P0 rules are settled.

Suggested traceability columns: `Requirement ID | Source clause | Priority | Decision dependency | Use case | UI/API | Entity/rule | Test ID | Status | Evidence`.

Suggested story completion rule: acceptance criteria satisfied, ownership/role checks verified, relevant failure paths demonstrated, migration/API/design documents updated and actual evidence linked. No current requirement should be marked implemented or passed.

## 7. Suggested updates to the 22-week plan

Keep the source schedule as a provisional baseline. Improve its exit conditions rather than adding more features.

| Weeks | Focus | Exit condition |
|---|---|---|
| 1–2 | Validation, policy decisions, SRS/design foundation and backlog | P0 decisions resolved; MVP boundary, permissions, state diagrams, ERD and core wireframes reviewed |
| 3–4 | Identity, profiles, migrations and CI | Five demo roles; role/ownership denial and account lifecycle checks |
| 5–6 | Harvests, lots, QR and buyer search | Farmer-created lot discoverable under visibility rules |
| 7–8 | Offers, reservations, expiry and inventory | Competing reservation, repeated acceptance and expiry races verified |
| 9–10 | Visits, slots, queue and unloading | Slot and bay concurrency, late/no-show/rebooking cases verified |
| 11–12 | Inspection, reconciliation, sale, settlement and payments | Full journey plus shortage/rejection/correction/partial-payment cases verified |
| 13–14 | Prices, notifications, reports and admin | Import behavior, notification ownership and financial/report reconciliation verified |
| 15–16 | Read-only assistant | Six question types with validated tools, sources, isolation and fallback |
| 17–18 | Integrated acceptance and measured quality | Core tests, security, load, accessibility and AI evaluation results recorded |
| 19–20 | Deployment and operational readiness | Repeatable deployment, restore evidence, rollback instructions and user guide |
| 21–22 | Contingency and assessment | Defects resolved, demo rehearsed and final report complete |

Start audit instrumentation, authorization and tests with each feature, not at the end. Run a minimal deployment early, then complete production-like demonstration configuration in weeks 19–20. Maintain documentation every week rather than postponing it to the delivery phase.

Weeks 11–12 carry substantial risk because inspection discrepancies, financial reversal and payment behavior are complex. Re-estimate after the decisions; use contingency if needed rather than quietly dropping required features. Optional CSV report export, richer charts and downloadable labels can be postponed. The read-only AI assistant remains required in the supplied baseline.

The existing proposed modular Spring Boot backend, Next.js frontend and PostgreSQL database can remain the planning baseline, subject to the assessment constraint already noted in the SRS. This review does not select dependency versions or verify current vendor compatibility.

## 8. Scope boundaries to preserve

Required: the five roles, complete produce-to-payment-record journey, safe reservations and capacity, inspection, dated prices, notifications, reports, audit, six read-only AI question types, deployment and restore demonstration.

Optional: CSV report export, dedicated demo mode, richer charts and downloadable lot labels. Reference-price CSV import is already part of the baseline and must not be confused with optional report export.

Deferred: trader/stall workflows, counter-offers, broadcast matching, SMS/push, mobile apps, full localization, offline writes, forecasting, payment gateways, multiple markets, microservices, message broker and Kubernetes.

## 9. Editorial improvements for v1.4

- Correct repeated section 4.2 headings and provide a consistent numbered hierarchy and generated table of contents.
- Add definitions for allocation, withdrawal, reconciliation, reversal, provisional weight, unloading occupancy and payment evidence.
- Separate normative requirements from architecture recommendations and implementation examples.
- Link every business-rule clause and delivery requirement to a testable ID; FR01–FR22 alone are too broad for complete coverage.
- Record decisions explicitly rather than leaving defaults described as both proposals and acceptance obligations.
- Preserve the distinction between hypotheses, pilot goals, prototype targets and measured outcomes. The 40% wait reduction and 80% coverage are not proven results.
- Add document owner, revision history and actual review status; do not imply supervisor sign-off.

## 10. Immediate next step

Use this review as the documentation backlog. Resolve reservation timing, inventory/reconciliation, settlement/payment meaning, reversal effects and queue capacity first. Then prepare SRS v1.4, permissions/state diagrams and ERD as a consistent design set before creating the application schema. The developer/supervisor must supply the actual deadline, weekly effort and assessment constraints; market stakeholders should validate queue and inspection policies.
