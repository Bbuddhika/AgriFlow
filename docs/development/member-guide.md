# Project member: Dambulla AgriFlow — implementation and delivery guide

> Prepared from this workspace on 16 November 2026. This is your individual-development guide, using the scope/steps/commit/done format of the supplied screenshots. It does not assign an invented team number or copy the delivery-system requirements shown in those examples.

> Stages 00 and 01 are complete with recorded evidence; continue at Stage 02. The repository contains a verified foundation, not a finished application. All nine backend tests, frontend build/typecheck, eleven-container health and catalog smoke/outage/recovery checks pass. Later stages remain planned until their evidence is recorded.

## 0. Your scope at a glance

| Item | Your AgriFlow responsibility |
|---|---|
| Delivery model | One developer owns the complete system; use the work packages below as suggested PR groupings |
| Roles | FARMER, BUYER, ADMINISTRATOR only |
| Main workflow | Account → harvest → lot → offer → reservation → visit → inspection → sale → settlement → payment evidence |
| Backend | `backend/` Maven aggregator; five Java 21 Spring Boot services; domain packages in `backend/market-core-service/src/main/java/lk/agriflow/` |
| Backend port | Host `8080` by default; container `8080` |
| Frontend | `frontend/`, Next.js App Router, React and TypeScript; host/container `3000` by default |
| Database | Four service-owned PostgreSQL stores; existing market `database` retained; no host SQL ports |
| Messaging | Compose service `rabbitmq`, RabbitMQ 4; vhost `agriflow`; AMQP `5672` private to Compose; management `localhost:15672` |
| Images | `dambulla-agriflow-frontend`, `dambulla-agriflow-<service>`, `dambulla-agriflow-database`, `dambulla-agriflow-rabbitmq`; default tag `0.1.0` |
| Dockerfiles | `frontend/Dockerfile`, `backend/<service>/Dockerfile`, `infrastructure/postgres/Dockerfile`, `infrastructure/rabbitmq/Dockerfile` |
| Migrations | `backend/market-core-service/src/main/resources/db/migration/`; V1 creates only the produce catalog |
| API contract | `contracts/openapi/agriflow.yaml`; currently foundation endpoints only |
| Existing backend test | `backend/market-core-service/src/test/java/lk/agriflow/CatalogIntegrationTest.java`; five integration methods passed in Stage 01, alongside four gateway tests |
| Existing smoke check | `scripts/development/smoke_check.py`; requires a running stack |
| UI references | `ui-design/index.html` and `ui-design/screens/`; 25 static prototypes, not functional application routes |
| Working convention | Suggested branch `feature/agriflow-sNN-short-topic`; use the actual repository base branch once Git is initialized |
| Evidence | `docs/testing/`; update the traceability CSV and progress tracker after each stage |

As of 23 November 2026, baseline `1418bfd` is published to `Bbuddhika/AgriFlow`. Use `main` for release baselines, `dev` for integration and feature branches from `dev`. Stage 01 runs on `feature/agriflow-s01-foundation-verification`. [ADR 003](../architecture/003-separate-backend-services.md) supersedes the original single-backend plan. See the [work board](work-board.csv), [decision register](decision-register.md) and [state review](state-transition-review.md).

## 1. Read these sources in order

1. [Current requirements](../project-documentation-v1.5.md): business scope, FR01–FR22, NFR-01–10 and selected rules.
2. [Application decision](../architecture/001-application-foundation.md) and [RabbitMQ decision](../architecture/002-rabbitmq.md): historical foundation decisions; ADR 003 now defines separate services with owned databases and a broker.
3. [Repository review](repository-review.md): what actually exists and where the remaining gaps are.
4. [Folder responsibilities](../folder-structure.md) and [local setup](../operations/local-development.md).
5. [UI prototype guide](../../ui-design/README.md) and screen manifest, then the stage you are implementing.

Newer explicit user decisions take precedence over historical documents. In particular, three roles replace the older five-role model; 24-hour reservations replace the old two-hour proposal; RabbitMQ is now required despite its deferred status in the older consolidated scope paragraph. The screenshots supply a guide format, not AgriFlow's roles, ports, tables or AI permissions.

## 2. Rules to preserve throughout development

- Services own their databases (ADR 003). Market-core domains share one transaction; use explicit application interfaces internally and authorized APIs/events across service boundaries.
- Farmers accept offers and approve deductions. Buyers consent to shortages and confirm purchases. Administrators cannot act as those participants.
- Pending offers hold no stock. Acceptance freezes the buyer's offered price and creates one 24-hour reservation.
- Use decimal kg to three places and LKR to two places. Keep stock adjustments, sales, active reservations and correction holds distinct.
- Record real inspection shortages even when they reveal an allocation deficit; block trading while reconciliation is unresolved.
- Buyer collections and farmer payouts are separate. Payment records are evidence of external payments; the application does not transfer money.
- Business changes, audit records and outbox records commit atomically. RabbitMQ delivery failure must not roll back an already committed trade.
- The assistant is available within each signed-in role's authorized scope. Unlike the screenshot's delivery project, it is not customer-only. It cannot write business records.
- Write tests, authorization, migration changes and API documentation with each feature. Do not leave them for the final stage.

## 3. Stage order and suggested work packages

Work packages group related review work. Split a large package into smaller PRs without changing the dependencies. Stage numbers are not week numbers.

| Package | Stages | Result |
|---|---|---|
| WP01 — Foundation | 00–02 | Reviewed baseline, running stack and transaction/security primitives |
| WP02 — Identity | 03 | Three roles with owned, authenticated access |
| WP03 — Produce | 04–06 | Harvests, published lots, stock/QR and buyer offers |
| WP04 — Reservations | 07–08 | Atomic acceptance, expiry and safe cancellation |
| WP05 — Market operations | 09–10 | Capacity-safe visits and unloading |
| WP06 — Inspection | 11–12 | Measured stock and consented reconciliation |
| WP07 — Finance | 13–15 | Sale confirmation, settlement, payments and corrections |
| WP08 — Messaging | 16–17 | Reliable outbox delivery and owned notifications |
| WP09 — Administration | 18–19 | Source prices, administration, reports and audit views |
| WP10 — Assistant | 20–21 | Authorized read tools, chat, source cards and fallback |
| WP11 — Acceptance | 22 | Recorded integrated, security, load and AI evaluation |
| WP12 — Release | 23–24 | Demonstrated deployment/recovery and assessment handover |

Stages 03–21 are not implemented. Stage 00 planning and Stage 01 foundation verification are complete. Stage 02 has partial supporting configuration and open exit checks. Use [the tracker](progress.md) for actual status.

Service ownership overrides shorthand domain paths in stages below:
Stage 03 belongs in `backend/auth-iam-service/`, Stages 17 and notification
inbox APIs in `backend/notification-service/`, and Stages 20–21 in
`backend/analytics-ai-service/`. Stage 02 market audit/idempotency/outbox and
Stages 04–16/18–19 authoritative market workflows remain in market core.
Enable protected gateway routes only after the Stage 03 identity boundary passes.

## WP01. Foundation

### Stage 00: Review the baseline and prepare the work board

**Objective:** Start from one consistent scope and an honest implementation baseline.

**Work in:** `docs/development/`, `docs/architecture/`, `docs/testing/`, current SRS and prototype references.

**Steps:**

1. Read the source order above and the repository review. Identify existing code versus proposed files.
2. Record stakeholder decisions still needed: actual grade thresholds, late-arrival policy validation, price-source access, recovery delivery method, retention and assessment constraints. Resolve each before its dependent feature is released.
3. Create stories from the traceability CSV. Assign the stage, expected behavior and acceptance evidence to each story.
4. Review stock, reservation, visit and financial state transitions before designing their schemas.
5. Exclude browser profiles/private generated state before staging files, then initialize/connect Git if this remains a plain folder. Select the real base branch and create a first planning branch; do not fabricate a remote URL or assume `dev`.

**Suggested commit:** `docs(plan): establish AgriFlow stages and acceptance tracking`

**Done when:** You can identify the scope, owning module and expected test for every requirement, and unresolved external decisions are explicitly recorded.

### Stage 01: Run and verify the existing foundation

**Objective:** Prove that the code already present can build and run before adding business features.

**Work in:** `.env.example`, `compose.yaml`, service and infrastructure Dockerfiles, `backend/pom.xml`, `frontend/package.json`, CI and existing tests.

**Steps:**

1. Follow the setup commands in section 5 below. Confirm Docker engine access and npm/Maven registry access.
2. Install frontend dependencies, review and commit the generated `package-lock.json`; resolve build failures from actual output. Check the configured Java/Maven and package compatibility through successful builds.
3. Run the five existing backend integration tests against disposable PostgreSQL/RabbitMQ containers.
4. Build/start all eleven Compose containers. Run the HTTP smoke check and inspect logs without committing secrets.
5. Verify the catalog renders all six types and that stopping the backend yields the frontend's unavailable state. Restart it afterward.
6. Record commands, environment and real results. Only after the lockfile exists, make CI and the frontend Docker build require `npm ci` instead of falling back to an unlocked install.

**Suggested commit:** `chore(foundation): verify builds and lock frontend dependencies`

**Done when:** Backend verification, frontend build/typecheck and Compose smoke checks actually pass, with evidence. Compose syntax validation alone does not complete this stage.

### Stage 02: Establish shared transaction and security primitives

**Objective:** Give later features consistent errors, audit, idempotency and committed-event recording.

**Depends on:** Stage 01.

**Work in:** market-core `shared/`, `audit/`, `config/`, migrations and the API contract. Market domain paths hereafter are under `backend/market-core-service/src/main/java/lk/agriflow/`; identity, notification and assistant work belongs in the corresponding separate service.

**Steps:**

1. Specify errors with a safe code, message, details and trace ID. Map invalid input, ownership denial, missing records, state conflicts and outages separately; the current handler maps every database exception to 503 and must become more precise.
2. Add reusable quantity/money validation, UTC-aware timestamps, Asia/Colombo display/report boundaries and an injectable test clock. After locking, expiry-sensitive decisions must use fresh database time.
3. Add append-only application audit writes and actor/operation/key-scoped idempotency with request hashes and stored outcomes.
4. Define the authentication/session/CSRF contract for Stage 03 and the frontend's authenticated server/client API boundary. The present `apiRead` helper is server-only and does not forward user identity.
5. Add versioned event envelopes and a transactional outbox writer. Record domain mutations and outbox rows together as later stages are implemented; do not publish directly before commit.
6. Test rollback, repeated keys, changed-payload conflicts, precision rejection and safe error output. Add each migration once; never edit applied V1.

**Suggested commit:** `feat(core): add audit idempotency and transactional event records`

**Done when:** A synthetic transactional fixture proves failed work leaves no audit/outbox side effects, and a repeated idempotent request cannot perform a second mutation.

## WP02. Identity

### Stage 03: Implement accounts, roles and owned sessions

**Objective:** Implement FR01 and establish the authority used by every subsequent API.

**Depends on:** Stage 02.

**Work in:** `backend/auth-iam-service/` (identity), `config/SecurityConfiguration.java`, `frontend/src/features/identity/`, auth route group, migrations and OpenAPI.

**Steps:**

1. Add users, role membership and farmer/buyer profiles. Public registration can create Farmer or Buyer only. Provision the first administrator through an explicit controlled setup process.
2. Replace the empty in-memory directory with persistent identity, password hashing and the selected expiring/revocable session design.
3. Implement login/logout, own profile, verified recovery and account suspension. Add rate limits and prevent privilege fields from being mass-assigned.
4. Create real auth pages and role layouts. Implement session/CSRF forwarding appropriate to the chosen browser/backend boundary without exposing secrets.
5. Replace blanket `denyAll()` only for implemented routes with explicit rules and server-side ownership checks. Keep unimplemented APIs closed.
6. Test all three roles, wrong-owner access, suspension, session expiry/logout/recovery and administrator self-registration denial. Treat existing unknown-route tests as regression tests, not proof of full authorization.

**Suggested commit:** `feat(identity): add owned accounts and three-role access control`

**Done when:** Three test accounts can sign in with the intended permissions, and role/ownership denials pass through the real HTTP boundary.

## WP03. Produce and offers

### Stage 04: Complete the catalog and register harvests

**Objective:** Implement FR02 with valid produce/grade references and farmer ownership.

**Depends on:** Stage 03.

**Work in:** `catalog/`, `produce/`, frontend produce/administration features; reference `farmer-create.html`.

**Steps:**

1. Extend the existing catalog with grades tied to produce types and administrator-managed enable/disable behavior. Use stakeholder-supplied grade definitions.
2. Add owned harvest records with produce type, positive expected kg and planned arrival.
3. Implement harvest create/list/detail validation and cross-owner denial.
4. Build the farmer harvest form with labelled errors, pending state, empty history and retry behavior.
5. Test disabled catalog entries and decimal bounds. Keep catalog seed data separate from fabricated transaction data.

**Suggested commit:** `feat(produce): add owned harvest registration and grade catalog`

**Done when:** Farmer A can create/read their harvest and Farmer B cannot mutate it; invalid quantities and grades are rejected.

### Stage 05: Publish lots, maintain stock and add QR lookup

**Objective:** Implement FR03 and the authoritative stock basis.

**Depends on:** Stage 04.

**Work in:** `produce/`, frontend produce feature and farmer routes; reference `farmer-lots.html`.

**Steps:**

1. Add harvest-to-lot relationships, lifecycle state, positive asking LKR/kg, listing version and publication time.
2. Implement draft creation, publish and version-checked asking-price edits. Preserve immutable price history.
3. Add signed stock adjustments. Availability must subtract net sold kg, unexpired reservations and correction holds without subtracting allocations twice.
4. Generate an opaque QR lookup token and manual lookup; a QR grants no private-record authority.
5. Build lot list/detail/QR views and test hidden draft/rejected/closed lots, stale edits and stock arithmetic.

**Suggested commit:** `feat(produce): add published lots stock ledger and QR lookup`

**Done when:** An eligible published lot is discoverable, stock has one consistent calculation, and changing an asking price retains its history.

### Stage 06: Search lots and submit private buyer offers

**Objective:** Implement FR04 and basic private price negotiation.

**Depends on:** Stage 05.

**Work in:** `trading/`, produce read interfaces, frontend trading feature and buyer routes; reference `buyer-explore.html`, `buyer-lot.html`, `buyer-offer.html`, `buyer-offers.html`.

**Steps:**

1. Add bounded search filters for produce, kg, grade and arrival; distinguish declared from inspected grade and filter private fields.
2. Add pending offers with buyer, lot, quantity, offered price, asking-price snapshot and listing version.
3. Show offered total before submit. Allow a positive offer below the asking price; do not implement bidding ranks or auctions.
4. Support own pending-offer cancellation and farmer rejection. Pending offers must not hold stock.
5. Record new/rejected offer outbox events and test privacy, self-trade denial, ineligible lots and subsequent asking-price edits.

**Suggested commit:** `feat(trading): add private buyer offers and market search`

**Done when:** A 50 kg offer at LKR 195/kg against a LKR 200/kg listing is pending at LKR 9,750, leaves stock unchanged and is invisible to other buyers.

## WP04. Reservation correctness

### Stage 07: Accept offers and reserve stock atomically

**Objective:** Implement acceptance under FR05 without overselling.

**Depends on:** Stage 06.

**Work in:** `trading/`, produce stock interface, audit/outbox writes, migrations; reference `farmer-offers.html`, `farmer-accepted.html`, `buyer-reservation.html`.

**Steps:**

1. Lock the offer and lot using a documented deterministic order, verify farmer ownership and recheck live availability.
2. Freeze the offered price and create one reservation per accepted offer. Set expiry to acceptance plus 24 hours.
3. Make repeated acceptance return the existing result; use constraints in addition to application checks.
4. Save acceptance, audit and `reservation.accepted.v1` outbox data together.
5. Test two simultaneous 80 kg acceptances against 100 kg: exactly one may commit. Test that changing the asking price never changes the accepted LKR 195/kg price.

**Suggested commit:** `feat(trading): reserve stock atomically on farmer acceptance`

**Done when:** Competing acceptance cannot overallocate stock, and repeated acceptance creates exactly one reservation.

### Stage 08: Implement expiry and reservation cancellation

**Objective:** Finish FR05 and prepare confirmation's expiry boundary under FR09.

**Depends on:** Stage 07.

**Work in:** `trading/application/`, reservation APIs/UI and concurrency tests; reference `buyer-expired.html`, `buyer-cancelled.html`.

**Steps:**

1. Exclude expired holds immediately in stock queries, even when the cleanup job has not run.
2. Add bounded expiry processing and permitted cancellation with audit/outbox records, releasing the hold once.
3. Use fresh database time after acquiring the relevant locks. At `now == expires_at`, the reservation is expired.
4. Show date/time and remaining time to participants. Visits and inspections do not extend a reservation.
5. Test before/at/after expiry, cancellation-versus-expiry and repeated processing; add the real confirmation race once Stage 13 exists.

**Suggested commit:** `feat(trading): enforce reservation expiry and safe cancellation`

**Done when:** Expired holds never reduce displayed availability and every race releases or consumes an allocation at most once.

## WP05. Vehicle visits and unloading

### Stage 09: Book capacity-safe market visits

**Objective:** Implement FR06 independently of whether a buyer reservation exists.

**Depends on:** Stages 05 and 08.

**Work in:** `visits/`, farmer booking pages, administrator capacity settings and migrations; reference `farmer-visit.html`, extending its incomplete booking design.

**Steps:**

1. Add vehicles, zones, half-open slots `[start,end)`, visits and owned visit-lot links.
2. Check booking capacity transactionally and prevent the same lot joining two nonterminal visits.
3. Allow booking without a reservation. Warn when a selected slot ends after a reservation expires.
4. Implement allowed cancellation, audited rebooking and configurable late/no-show rules from the reviewed baseline.
5. Test the last slot under concurrent bookings, mixed ownership, early/late arrivals and repeat visits after completion.

**Suggested commit:** `feat(visits): add owned vehicle bookings and slot capacity checks`

**Done when:** Two concurrent requests cannot book the last available place, and a farmer can book their own lots without a buyer.

### Stage 10: Implement gate check-in and bay allocation

**Objective:** Implement FR07 with explicit unloading occupancy.

**Depends on:** Stage 09.

**Work in:** `visits/`, administrator desktop/mobile routes; reference `admin-queue.html`, `admin-mobile.html`.

**Steps:**

1. Add enabled bays and active allocations with uniqueness constraints for bay and visit.
2. Implement check-in, call, start unloading, complete, recall, ready and departure transitions.
3. Call the earliest eligible visit by check-in time then ID. Calling acquires the bay; both CALLED and UNLOADING occupy it.
4. Require reasons for overrides/recall. Recall releases occupancy once and makes the visit unready until explicitly restored.
5. Add queue refresh and status-change outbox events. Preserve occupancy across restarts and document physical-site reconciliation.
6. Test one bay/two callers, invalid transitions, recall/restart and separate completion/departure times.

**Suggested commit:** `feat(visits): add audited queue dispatch and atomic bay allocation`

**Done when:** Exactly one caller acquires a free bay; completion/recall release it correctly, and committed queue changes are measurable within the five-second target.

## WP06. Inspection and shortage consent

### Stage 11: Record inspection and adjust stock once

**Objective:** Implement the physical inspection record under FR08.

**Depends on:** Stages 08 and 10.

**Work in:** `inspection/`, produce stock interfaces, administrator inspection UI; reference `admin-inspection.html`.

**Steps:**

1. Add immutable inspection records: actor/time, total measured kg, saleable/excluded kg, grade, damage percentage and reason.
2. Retain declared grade. Validate saleable kg against total kg and approved catalog grades.
3. Apply the signed difference to the lot's stock basis once. Reinspection before sales uses only the change from the previous effective measurement.
4. Keep genuine allocation deficits visible to administrators; show zero tradable availability and set a reconciliation hold.
5. Rejection blocks sale and cancels unsold active reservations with audit/events. Reopening requires audited reinspection.
6. Test 100→70 kg, repeated request/reinspection, rejection and post-sale remaining-stock adjustments.

**Suggested commit:** `feat(inspection): record measured quality and auditable stock adjustments`

**Done when:** A 30 kg shortage is applied once, cannot become an extra automatic damage deduction and blocks overallocated trades.

### Stage 12: Resolve shortages through buyer consent

**Objective:** Complete FR08 reconciliation without silently changing agreements.

**Depends on:** Stage 11.

**Work in:** `inspection/`, reservation application interfaces, farmer/buyer shortage views; reference `buyer-shortage.html`, `buyer-shortage-agreed.html`.

**Steps:**

1. Add reconciliation cases/proposals and immutable reservation amendments.
2. Calculate proportional reductions, round down to 0.001 kg and distribute remaining increments by acceptance time then reservation ID.
3. Let only the affected buyer accept or cancel; administrators coordinate and cannot consent on the buyer's behalf.
4. Recheck expiry and holds under locks. A proposal cannot revive an expired reservation or silently increase a previously reduced quantity.
5. Clear the hold only when allocations fit measured stock and no proposal still requires consent. Test cancellation/expiry during reconciliation.

**Suggested commit:** `feat(inspection): add explicit buyer consent for shortage allocations`

**Done when:** 60/40 kg reservations become 48/32 kg against 80 kg only through the required responses, without overallocating or reviving expired commitments.

## WP07. Sale and financial records

### Stage 13: Approve deductions and confirm one sale

**Objective:** Implement FR09 and the immutable settlement part of FR10.

**Depends on:** Stage 12.

**Work in:** `finance/`, trading confirmation coordinator, inspection/produce read interfaces; reference `farmer-settlement.html`, `buyer-confirm.html`, `buyer-receipt.html`.

**Steps:**

1. Add deduction proposals with category, amount, purpose and farmer approval. Default deductions to zero and reject totals above gross.
2. Buyer confirmation verifies participant ownership, fresh unexpired reservation, accepted inspection, stock and absence of unresolved holds.
3. Confirm the full currently agreed reservation quantity into exactly one sale/settlement. Partial lot sales use multiple reservations.
4. Freeze kg, agreed price, approved deductions, gross and net using decimal half-up money rounding. Changed deduction amounts require reapproval.
5. Save sale, stock allocation, audit, idempotency response and `sale.confirmed.v1` outbox row in one transaction.
6. Test duplicate confirmations, expiry-versus-confirmation, insufficient stock and inspection/consent bypass attempts. Receipts start unpaid.

**Suggested commit:** `feat(finance): confirm inspected reservations with approved settlement snapshots`

**Done when:** Repeated confirmation yields one sale; unapproved deductions and expired/blocked reservations cannot produce a receipt.

### Stage 14: Record buyer collections and farmer payouts

**Objective:** Implement directional payment evidence under FR10.

**Depends on:** Stage 13.

**Work in:** `finance/`, administrator payment UI and participant histories; reference `admin-payments.html`, `farmer-paid.html` with reviewed status labels.

**Steps:**

1. Add positive manual payment entries with direction, payer/payee, method, actual time, recording time, actor and mandatory external evidence/reference.
2. Derive collection and payout states separately from valid entries; never implement a paid toggle.
3. Allow partial collections and payouts. Require full buyer collection before a farmer payout; reject overcollection and overpayment.
4. Treat zero-net settlement as NOT_DUE without a fictitious payout. Use actor-scoped idempotency and settlement locking.
5. Test LKR 67,500 gross, LKR 1,500 approved deductions and a LKR 30,000 payout after full collection: the remaining farmer balance is LKR 36,000.

**Suggested commit:** `feat(finance): record separate buyer collections and farmer payouts`

**Done when:** Buyer paid status cannot imply farmer paid status, and duplicate/excess entries cannot change balances twice.

### Stage 15: Correct payments and sales without deleting history

**Objective:** Implement FR14 financial corrections and correction-held stock.

**Depends on:** Stage 14.

**Work in:** `finance/`, `audit/`, produce/inspection interfaces and new correction screens.

**Steps:**

1. Add linked payment reversals capped by the unreversed amount, with reason, actor, evidence and idempotency.
2. Open sale correction cases and freeze further payments. Preserve genuine external payment movements; unresolved real money cannot be erased to cancel a sale.
3. Permit one full erroneous-sale reversal only when policy allows. Do not reactivate the old reservation.
4. Place reversed kg on a correction hold; release only after administrator physical verification, or record absent goods as loss/withdrawal.
5. Preserve original records and signed report corrections by effective date. Test concurrent reversals and every unauthorized role.

**Suggested commit:** `feat(finance): add linked reversals and verified correction stock holds`

**Done when:** A reversed sale never creates phantom available stock or silently erases genuine payments, and the history remains auditable.

## WP08. Reliable messaging and notifications

### Stage 16: Deliver committed outbox events through RabbitMQ

**Objective:** Turn the configured broker into a reliable committed-event delivery path.

**Depends on:** Stages 02 and 15 for the complete journey; a dispatcher can be developed earlier once its prerequisites exist.

**Work in:** shared messaging adapters, outbox persistence, `config/MessagingConfiguration.java`, `application.yml`, event contracts and RabbitMQ tests.

**Steps:**

1. Inventory events written by Stages 06–15. Extend the current five routing-key bindings to cover new/rejected offers and other required notifications such as shortage decisions; current topology is not complete FR12 coverage.
2. Implement bounded outbox polling with atomic claim/lease semantics, stable event IDs, attempt/backoff metadata and recovery after worker failure.
3. Publish persistent, schema-validated JSON; check correlated confirms and returned-message outcomes before marking sent.
4. Retry after outages without undoing trades. Test the crash window after broker acceptance but before the outbox update; redelivery must remain possible.
5. Verify rollback sends no event, missing bindings return messages, outages retain unsent rows and broker restart preserves durable messages.
6. Review core-versus-messaging readiness: the foundation currently includes RabbitMQ in global readiness. Ensure a notification outage does not unnecessarily remove healthy synchronous trade APIs from service.

**Suggested commit:** `feat(messaging): publish transactional outbox events with confirmed delivery`

**Done when:** A committed event survives a broker outage/restart and eventually delivers, while a rolled-back trade never appears as an event. Confirms alone are not end-to-end exactly-once processing.

### Stage 17: Persist and display owned notifications

**Objective:** Implement FR12 using idempotent consumption.

**Depends on:** Stage 16.

**Work in:** `backend/notification-service/` (notifications), notifications migration, frontend notifications feature and shared role layouts.

**Steps:**

1. Add validated event handling and a database uniqueness rule on event/recipient/type.
2. Commit processed-event state and notification writes atomically. Acknowledge only after success so broker redelivery is safe.
3. Implement bounded retry and dead-letter handling. Add monitored retention/replay procedures without endlessly requeueing poison messages.
4. Add owned list/unread/read APIs and UI. Determine recipients from trusted domain context, not caller-supplied identity.
5. Deliver the same event twice and verify one notification per recipient/type. Test interrupted processing, stale events, DLQ replay and cross-owner access.

**Suggested commit:** `feat(notifications): add deduplicated event consumption and owned inboxes`

**Done when:** Duplicate deliveries do not duplicate notifications; marking one user's notification cannot affect another user's inbox.

## WP09. Prices, administration and reporting

### Stage 18: Manage reference prices and administrative settings

**Objective:** Implement FR11 and remaining account/catalog/zone administration under FR13.

**Depends on:** Stages 03, 04, 09 and 17.

**Work in:** `marketprices/`, relevant owning modules, frontend administration feature and new administrator screens.

**Steps:**

1. Add dated/source-labelled reference prices with kg units and either one price or a valid min/max range.
2. Implement manual entry and CSV preview followed by atomic import. Validate all rows and require an explicit audited replacement for duplicates.
3. Flag missing data and source-effective ages greater than 48 hours as stale. Keep reference prices separate from asking and agreed prices.
4. Complete account suspension, catalog/grade and zone/bay settings through their owning modules. Used catalog records are disabled rather than deleted.
5. Test invalid CSV, duplicate/replacement behavior, stale boundaries and attempts to disable occupied bays or bypass participant decisions.

**Suggested commit:** `feat(admin): add audited reference-price imports and market settings`

**Done when:** Bad imports change nothing; source/freshness is visible; administration cannot overwrite agreements or operational occupancy.

### Stage 19: Build reports, histories and audit views

**Objective:** Complete FR13/FR14 visibility from authoritative records.

**Depends on:** Stages 15 and 18.

**Work in:** `reporting/`, `audit/`, authorized read interfaces and new report/history screens; reference `admin-overview.html` as layout inspiration only.

**Steps:**

1. Add bounded date-filtered daily queries using Asia/Colombo dates with an exclusive next-day end.
2. Keep sold kg, gross sales, signed reversals/net sales, buyer collections, deductions, farmer payouts and outstanding balances distinct.
3. Use confirmation time for sales, actual payment time for payments and effective correction time for reversals; preserve recording time for audit.
4. Provide participant-owned histories and administrator market-wide reports/audit filters without leaking contact/payment details.
5. Reconcile a seeded day's totals against underlying records, including midnight boundaries and later corrections. If adding projections, keep them rebuildable and deduplicate events.

**Suggested commit:** `feat(reporting): add reconciled daily totals and audited participant histories`

**Done when:** Every displayed total can be traced to records; correction dates and collection/payout balances reconcile independently.

## WP10. Read-only assistant

### Stage 20: Implement authorized tools before connecting a model

**Objective:** Establish the deterministic data boundary for FR15–FR21.

**Depends on:** Stage 19 and the underlying business read APIs.

**Work in:** `backend/analytics-ai-service/` (assistant), approved help resources and direct tool tests; frontend assistant feature later consumes these results.

**Steps:**

1. Implement six tool categories: approved system help, dated source prices, own queue status, visible produce search, own reservations and own trade summary.
2. Define allowlisted tool schemas with bounded filters. Derive identity/roles from the authenticated request; never accept a model's user ID as authority.
3. Call existing authorized application interfaces, never arbitrary SQL, URLs or mutation use cases.
4. Return structured facts and source identifiers with freshness and scope. Clarify multiple possible visits instead of guessing.
5. Test each tool directly for Farmer, Buyer and Administrator, plus cross-owner and unavailable-data cases. Keep the assistant API closed until its permissions pass.

**Suggested commit:** `feat(assistant): add scoped read-only tools and approved help sources`

**Done when:** Each answerable category returns the correct authorized facts without any model, and every forbidden identity/tool/write attempt is denied.

### Stage 21: Add chat orchestration, owned sessions and source-backed UI

**Objective:** Complete FR15–FR22 with controlled model use and graceful failure.

**Depends on:** Stage 20.

**Work in:** `backend/analytics-ai-service/` (assistant), session/message/run migrations, versioned prompts/help, `frontend/src/features/assistant/` and shared signed-in layouts.

**Steps:**

1. Add a server-only provider adapter and environment template; choose the provider/model and budget explicitly. Store no provider secret in the browser.
2. Orchestrate only allowlisted tools. Apply the reviewed limits: 1,000 input characters, 10 requests/minute/user, four tools, three model calls and a 20-second deadline, with bounded context/output/retries and daily spending controls.
3. Add owned sessions/history, clear/delete controls and seven-day chat expiry. Explain provider disclosure separately from application deletion.
4. Render source cards from verified backend facts, distinguish stale/missing data and use deterministic fallback for unverifiable numeric/status output or provider outage.
5. Add authenticated role-scoped chat with loading/retry/denied states. Escape model text and disable raw HTML rendering.
6. Test injection, fabricated tool names, cross-session access, changed stock, provider timeouts and no-write enforcement. Record redacted model/prompt/latency/token/source metadata.

**Suggested commit:** `feat(assistant): add controlled chat sessions sources and outage fallback`

**Done when:** The assistant answers using current authorized facts, clears only owned history and cannot create offers, reservations, inspections or payments.

## WP11. Acceptance and measured quality

### Stage 22: Demonstrate the full system against requirements

**Objective:** Produce evidence for FR01–FR22, NEG01–07, ROLE01–02 and NFR-01–10.

**Depends on:** Stage 21. Feature-specific tests should already exist.

**Work in:** backend/frontend tests, root `tests/` groups, traceability CSV and `docs/testing/` evidence.

**Steps:**

1. Run a real three-role journey from harvest to payment evidence, then repeat with rejection, shortage, expiry, cancellation and corrections.
2. Run stock/reservation/slot/bay concurrency tests and failed-network retries through actual API boundaries.
3. Check keyboard/focus/forms and 360 px/desktop application journeys. Existing prototype layout results do not verify the React application.
4. Measure the documented API workload: 25 concurrent users, 10 minutes, 10,000 lots, with declared hardware/mix/error threshold and p95 target below one second. Check 200 visits and five-second queue updates.
5. Evaluate 40 AI functional cases: 8 help, 6 price, 6 queue, 6 produce, 4 reservation, 4 trade and 6 ambiguous/unavailable; require at least 36 appropriate/correct outcomes. Run at least 12 permission/adversarial cases, all passing.
6. Measure five concurrent chats against p95 ≤15 seconds and fallback by 20 seconds. Test provider failure and broker restart. Record all failures and rerun affected checks after fixes.

**Suggested commit:** `test(acceptance): verify market journeys concurrency and assistant safety`

**Done when:** Every requirement has actual result/evidence or an explicitly unresolved failure; no required security/consent/write-prevention test is waived or relabelled passed.

## WP12. Release and handover

### Stage 23: Deploy and rehearse backup, restore and rollback

**Objective:** Complete NFR-06/NFR-10 with measured operational evidence.

**Depends on:** Stage 22; a minimal demo deployment should have been exercised earlier.

**Work in:** `infrastructure/proxy/`, `infrastructure/monitoring/`, `scripts/operations/`, deployment configuration and operations docs.

**Steps:**

1. Configure single-host HTTPS, secrets, restricted database/broker management access, health monitoring and redacted structured logs.
2. Build reviewed release images, pin dependency/image inputs and retain prior versions with migration compatibility notes. Avoid destructive schema rollback promises.
3. Add scheduled encrypted off-host PostgreSQL backups. Define broker persistence/recovery, outbox replay, DLQ retention and notification deduplication procedures.
4. Restore to a clean environment. Verify record counts, sample stock allocations and financial balances; measure restoration time and backup age against ≤4-hour recovery and ≤24-hour data-loss targets.
5. Rehearse application rollback using a schema-compatible previous image. Document commands, environment, ownership and actual timing.
6. Finalize transactional/audit retention and provider data-use decisions before using real personal data.

**Suggested commit:** `chore(release): add verified HTTPS deployment and recovery procedures`

**Done when:** The hosted demo works, recovery has actually been demonstrated and compatible application rollback is documented with evidence.

### Stage 24: Prepare user guidance and final demonstration

**Objective:** Deliver a system you can operate, demonstrate and explain.

**Depends on:** Stage 23.

**Work in:** final report, three role guides, demo script, architecture/API/ERD documentation and release notes.

**Steps:**

1. Write Farmer, Buyer and Administrator instructions from implemented screens, including consent, payment-state and correction explanations.
2. Update diagrams, API schemas, data dictionary and traceability to match released code, including RabbitMQ. Do not edit generated SVG/HTML as the source of truth.
3. Rehearse the main journey and at least shortage, expiry, safe retry and provider-outage demonstrations using synthetic accounts/data.
4. Assemble evidence, known limitations, restore results and the release identifier; separate measured outcomes from project targets.
5. Freeze the demonstration build and record actual remaining work. Update the progress tracker and final report without claiming supervisor approval or production compliance.

**Suggested commit:** `docs(handover): add role guides final evidence and demonstration script`

**Done when:** A reviewer can set up the system, follow the journeys and trace every completion claim to evidence.

## 4. How to work on each stage

1. Read the stage and confirm its dependencies are complete or explicitly accommodated.
2. Choose one small acceptance scenario; create a branch after the Git setup exists.
3. Write the migration and API/event contract for that scenario, then backend rules and authorization.
4. Build the corresponding frontend interaction and its loading/empty/error/denied states.
5. Run meaningful success, wrong-owner, duplicate/retry and concurrency tests where applicable.
6. Save redacted evidence using [the evidence template](../testing/stage-evidence-template.md); update [traceability](../testing/requirements-traceability.csv) and [progress](progress.md).
7. Review the diff, commit the concrete result and open a PR if using remote Git. Do not mark the stage complete just because a class, page or queue exists.

Suggested commands once Git is initialized:

```powershell
git status --short
git switch -c feature/agriflow-s03-identity
# Implement the selected scenario and run relevant checks.
git diff --check
git diff
```

Commit names in each stage are examples, not shell commands executed by this guide. For SQL, choose the next unused Flyway version at implementation time; the guide does not reserve conflicting migration numbers.

## 5. Your first practical session

Run from `C:\Dambulla AgriFlow`. Do not overwrite an existing `.env`.

```powershell
if (-not (Test-Path -LiteralPath .env)) { if (-not (Test-Path .env)) { Copy-Item .env.example .env } }
# Edit .env: set all five password variables from .env.example to distinct values.
docker info
docker compose config --quiet
docker compose up --build --wait
docker compose ps
python scripts/development/smoke_check.py
```

Open `http://localhost:3000` and RabbitMQ management at `http://localhost:15672`.
Check backend readiness at `http://localhost:8080/actuator/health/readiness`.
Use the existing native setup instructions if developing outside containers;
PostgreSQL and AMQP are not published by default, and `.env` is not automatically
loaded into a native Java process.

Then install and verify native build inputs where access is available:

```powershell
npm.cmd --prefix frontend install
mvn -B -f backend/pom.xml verify
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run typecheck
```

Do not skip Stage 01 when these fail. Capture the error, resolve the access or
build issue and rerun the affected check. The review did not install packages,
change machine permissions, start Docker or execute the future stages.

## 6. Provisional 22-week alignment

| Existing planning window | Corresponding stages | Exit evidence |
|---|---|---|
| Weeks 1–2 | 00–02 | Baseline and running foundation; shared primitives |
| Weeks 3–4 | 03 | Three-role identity and denial tests |
| Weeks 5–6 | 04–06 | Harvest → published lot → buyer offer |
| Weeks 7–8 | 07–08 | Reservation concurrency and expiry |
| Weeks 9–10 | 09–10 | Capacity-safe booking and unloading |
| Weeks 11–12 | 11–15 | Inspection → consent → sale → payments/corrections |
| Weeks 13–14 | 16–19 | Reliable notifications, prices and reconciled reporting |
| Weeks 15–16 | 20–21 | Scoped tools and controlled assistant |
| Weeks 17–18 | 22 | Recorded functional/security/load/AI results |
| Weeks 19–20 | 23 | Demonstrated deployment and recovery |
| Weeks 21–22 | 24 and contingency | Rehearsed demo, final docs and defect fixes |

This is the SRS planning horizon mapped to dependencies, not a guaranteed
schedule. Inspection/finance work in weeks 11–12 is especially dense. Re-estimate
using actual hours and the submission date rather than dropping mandatory rules.
Start audit/outbox writes and tests with each feature, and rehearse a minimal
deployment early instead of waiting until Stage 23.
