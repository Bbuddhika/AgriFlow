# Dambulla AgriFlow — system design supplement

## Detailed design decisions

### Identity and access
Public self-registration creates a farmer or buyer profile; staff roles are provisioned by an administrator. The role catalog contains FARMER, BUYER and ADMINISTRATOR only; each action checks role and ownership. An actor cannot accept their own buyer offer through another role. Administrators do not bypass inspection or buyer consent. Suspended accounts cannot sign in or perform normal mutations; authorized staff resolve their existing commitments without impersonating them. Use expiring sessions, credential hashing, revocation and a verified recovery mechanism. The exact authentication library and recovery delivery mechanism are implementation selections.

| Action | Farmer | Buyer | Administrator |
|---|---|---|---|
| Publish lot / edit asking price | Own | No | No impersonation |
| Submit price offer | No | Own | No impersonation |
| Accept/reject offer | Own lot | No | No impersonation |
| Shortage consent / purchase confirmation | No | Own | Coordinate only |
| Approve deductions | Own | View agreement | Propose / record |
| Book visit | Own | No | Rebook with reason |
| Slots / check-in / call / unload | No | No | Yes, audited |
| Inspection / reinspection / verify stock | No | No | Yes, audited |
| Payments / corrections | No | No | Yes, audited |
| Accounts / catalog / source prices | No | No | Yes |
| Reports / audit | Own history | Own history | Market-wide |
| Assistant / chat | Own scope | Own scope | Authorized scope |

### Additional MVP policies
These are design defaults selected to complete the documentation, not claims of validated market practice. Review them during stakeholder walkthroughs.

- Offers use PENDING → ACCEPTED, REJECTED or CANCELLED. Buyer cancellation is allowed before acceptance. Acceptance creates one reservation; accepted quantities/prices change only through the documented shortage amendment or a new offer.
- Unit prices must be greater than zero, resolving the earlier positive/nonnegative inconsistency. LKR values use NUMERIC(16,2); kg uses NUMERIC(14,3). Reject excessive precision and out-of-range values at the API boundary.
- Farmers select an available slot; the UI suggests the earliest suitable slot. Slot times are half-open intervals [start,end). Booking checks capacity transactionally. Early check-in waits for slot eligibility; arrivals later than slot start plus 15 minutes require an administrator's audited rebooking. Mark a still-booked vehicle no-show after slot end plus 15 minutes. These timings remain configurable operational defaults.
- A lot can be attached to only one nonterminal visit at a time. Later visits may carry unsold stock after the earlier visit completes. Visits require one or more owned lots. Each visit belongs to one farmer and vehicle; mixed-owner transport is deferred.
- Lot states: DRAFT → REGISTERED → INSPECTED → CLOSED. Rejection uses REJECTED; only audited reinspection can reopen. Reconciliation and correction holds block relevant stock independently of the lifecycle state. Close only when no stock or unresolved allocation remains.
- Grades are configured per produce type and selected by administrators; rejection requires a reason. Actual grade thresholds require stakeholder input and are not invented by this document.
- Reference-price CSV fields: produce code, market, unit (kg), effective date/time, source, price or minimum/maximum. Require nonnegative values and min ≤ max; reject rows with both single price and range. Preview errors before atomic import; duplicate source/date/type/market/unit records require an explicit audited replacement. Staleness is age greater than 48 hours, using source effective time.
- Notifications persist from committed domain events and deduplicate on event/recipient/type. Delivery failure retries without undoing a trade. Users can read/mark only their own notifications.
- Daily reports use Asia/Colombo calendar dates and an exclusive next-day end. Sales use confirmation time, payments use actual payment time and reversals use correction effective time. Store recording time separately for audit.
- No personal bank account details are needed in the MVP. Keep contact data access restricted. Chat retention is seven days; transactional/audit retention requires an explicit deployment policy before real use. Account deletion must not erase linked financial history.

### API contract inventory
All endpoints are under /api/v1 and require authentication except the explicitly selected registration/login/recovery endpoints. IDs never grant authority. Use 400 validation, 401 unauthenticated, 403 forbidden, 404 absent/inaccessible where appropriate, 409 state conflict, 429 rate limit and 503 unavailable. List endpoints use bounded limit/offset. Errors contain code, message, safe details and traceId.

| Resource / operations | Authorization and transactional rule |
|---|---|
| /auth/register, /auth/login, /auth/logout, /auth/recovery | Vetted identity workflow; rate limit; staff cannot self-enrol |
| GET/PATCH /me; /admin/users and role/status actions | Own profile; privileged admin lifecycle |
| POST/GET /harvests; POST /harvests/{id}/lots | Farmer ownership; positive quantity |
| GET /lots and /lots/{id}; GET /lots/{id}/qr | Listing visibility and private field filtering |
| POST /lots/{id}/offers; POST /offers/{id}/accept or /reject or /cancel | Ownership; lock offer/lot on acceptance |
| GET /reservations; POST /reservations/{id}/cancel or /confirm | Participant view; buyer confirms; idempotency required |
| GET /slots; POST /visits; POST /visits/{id}/cancel or /rebook | Owned lots; capacity locks; rebooking administrator audit |
| POST /visits/{id}/check-in, /call, /start-unloading, /complete, /recall, /ready, /depart | Administrator; bay allocation and state checks |
| POST /lots/{id}/inspections; GET inspection history | Administrator; immutable measurements and adjustments |
| GET /reconciliations/{id}; POST proposals; POST proposal /accept or /cancel | Admin coordinates; buyer consent only |
| POST /lots/{id}/deduction-proposals; POST /deduction-proposals/{id}/approve | Admin proposes; farmer approves before confirmation |
| GET /sales/{id}/receipt; POST /settlements/{id}/payments | Participants read; administrator records directional payment |
| POST /payments/{id}/reversals; POST /sales/{id}/correction-cases | Admin only; linked evidence and idempotency |
| POST /correction-cases/{id}/verify-stock or /resolve | Administrator verifies; administrator resolves under correction policy |
| GET /market/prices; POST /admin/prices/import-preview or /import | Dated public-to-signed-in prices; admin imports |
| GET /notifications; PATCH /notifications/{id}/read | Recipient ownership |
| GET /reports/daily; GET /admin/audit | Authorized admin; consistent date filters |
| POST /assistant/chat; GET/DELETE /assistant/sessions/{id}/messages | Owned session; deletion API may clear messages; session deletion also supported |
| DELETE /assistant/sessions/{id} | Delete own retained session/history |

Final machine-readable OpenAPI schemas remain an implementation deliverable. This inventory establishes coverage, not a claim that endpoints exist.

### Data dictionary and relationship supplement
All primary IDs are immutable UUIDs. Timestamps use timezone-aware database values. Foreign keys must not cascade-delete financial or audit history. Store status values as constrained enums/checks; expose no mass-assignment of privileged fields.

| Entity | Required fields / relationship and constraints |
|---|---|
| users, roles, user_roles | Identity/contact/status; composite user/role uniqueness; protected credential hash |
| farmer_profiles, buyer_profiles | Unique user FK; minimum role-specific profile fields |
| produce_types, grades | Produce code unique; grade belongs to produce; disable used catalog entries instead of deletion |
| harvests | Farmer and produce FKs; expected kg >0; planned arrival |
| lots | Harvest FK; asking_price_per_kg >0 on publish; price_version/published_at; opaque lookup token; state; stock basis |
| offers | Lot/buyer FKs; quantity and offered price >0; asking-price snapshot/version; status and acceptance time |
| reservations | Unique offer FK; agreed kg; accepted/expires timestamps; terminal state |
| reservation_amendments | Reservation and proposal FKs; old/new kg, buyer, consent time; immutable |
| inspections | Lot/administrator FKs; total/saleable/excluded kg; grade; damage 0..100; optional superseded inspection FK |
| stock_adjustments | Lot/actor FKs; signed kg, kind, reason; inspection/correction reference; immutable |
| reconciliation_cases | Lot/inspection FKs; coordinator, state, deficit; at most one active case per lot |
| reconciliation_proposals | Case/reservation FKs; original/proposed kg, response and time; no revival after expiry |
| deduction_proposals | Lot/reservation reference; category, amount, purpose; farmer approval/version |
| sales, settlements, settlement_deductions | Unique reservation→sale→settlement chain; frozen kg/price/gross/net; deduction snapshots |
| payment_entries | Settlement FK; direction, amount, payer/payee, method, evidence, times, actor; optional reversal FK |
| sale_correction_cases, sale_reversals | Sale FK, reason, financial resolution, status; one full reversal maximum |
| stock_correction_holds | Reversal/lot FKs; kg held, inspection verification and resolution; no automatic availability |
| vehicles | Registration identifier normalized/unique; display registration |
| zones, slots | Zone FK; starts/ends, booking limit; end > start; nonnegative capacities |
| visits, visit_lots | Farmer/vehicle/slot FKs; lifecycle timestamps; composite visit/lot key; owned-lot validation |
| unloading_bays, bay_allocations | Zone FK; bay/visit FKs; allocation/release timestamps; partial uniqueness for active allocation |
| market_prices | Produce/source/market/unit/effective date key; price or range; imported_at and revision audit |
| notifications, domain_events | Recipient/event/type deduplication; read time; retry metadata for committed events |
| audit_events | Actor, entity, action, reason, recorded time, safe change summary; append-only application permissions |
| idempotency_records | Actor/operation/key unique; request hash, outcome, response; financial keys retained with records |
| chat_sessions, chat_messages | User→session→messages; expiry and clear history; parent ownership checked |
| assistant_runs, help_articles | Redacted usage/latency/model/prompt metadata; versioned published role-visible help |

Index active reservations by lot/expiry, visits by slot/state, sales by date, and payment entries by settlement. Use deterministic lock ordering for lot/reservation/payment operations. Exact migration DDL and query plans are verified during implementation.

### Screen and interaction specification
Farmer: dashboard, profile, harvest form, lot detail/QR, offers, visit booking/queue, shortage outcomes, deduction approval and receipts. Buyer: search/filter, lot details, offer form, reservations/expiry, shortage consent, purchase confirmation and purchase history. Administrator: slot capacity, arrivals, check-in/manual lookup, bay board, departure, lot lookup, measurement form, inspection history, correction-stock verification, accounts/catalog, source prices/import preview, reconciliation, collections/payouts, corrections, reports and audit. Shared: login, notifications and source-backed chat with clear-history control.

Every form needs labelled fields, error summary, pending/submitted state and safe retry. Show empty, unavailable, expired, conflict and denied states. Always distinguish declared vs inspected grade and buyer collection vs farmer payout status. Provide keyboard focus and non-colour status labels at 360 px and desktop widths.

### Security and privacy design
Enforce server-side roles and ownership on every route and tool. Parameterize queries; validate DTOs; restrict CORS; protect cookie-authenticated writes against CSRF. Escape user/model content and disable raw HTML chat rendering. Keep secrets outside source and browser bundles. Use TLS, encrypted backups, controlled contact-data access and redacted logs. QR identifiers convey lookup identity only. Explain model-provider disclosure; clearing local chat does not delete provider logs. Evaluate with synthetic data until data-use settings and operational retention are agreed.

### Verification and acceptance evidence
All tests currently have status NOT RUN: documentation is not implementation evidence. For each FR01–FR22 map its row in the requirement inventory to a named integration/E2E test, actual result and evidence path. Run ownership denial cases as well as normal paths.

| Test group | Coverage / expected result |
|---|---|
| T01 Identity | FR01–03: own registration/harvest/QR; cross-owner and disabled-account denial |
| T02 Trade | FR04–05: competing 80 kg holds on 100 kg, positive price, repeated acceptance, 24-hour boundary |
| T03 Operations | FR06–07: last slot conflict, one bay/two callers, late/no-show/rebooking, recall and restart |
| T04 Inspection | FR08: reject, 100→70 kg shortage, 60/40→48/32 consent, cancellation/expiry during reconciliation |
| T05 Finance | FR09–10/14: one sale per reservation, idempotency, approved deductions, directional payments, reversals and stock hold |
| T06 Administration | FR11–14: invalid/duplicate CSV, stale source, own notifications, signed report correction totals and audit |
| T07 Assistant | FR15–22: 40 functional questions plus at least 12 permission/adversarial cases; zero unauthorized reads/writes |
| T08 Quality | NFR-01–10: load, keyboard/mobile journeys, network retry, backup restore and graceful AI outage |

AI functional set: 8 help, 6 price, 6 queue, 6 produce, 4 reservation, 4 trade and 6 ambiguous/unavailable questions. Require ≥36 appropriate/correct outcomes from 40, with all permission/write-prevention tests passing. Record model, prompt version, latency, tokens, sources and expected fixture facts. Test provider outage, stale prices, injected instructions and changed stock.

For API load use a documented endpoint mix, seeded identities and hardware, 25 concurrent users for 10 minutes and 10,000 lots. Report p95 and error rates, with model latency separately. Declare the mix and allowable error threshold before measurement; do not present an invented benchmark.

### Deployment and recovery plan
Use local Docker Compose, versioned database migrations and CI builds/tests. Deploy a single-host demonstration environment with HTTPS, restricted database access, secrets, health endpoints and structured logs. Back up daily to encrypted off-host storage; demonstrate restore to a clean database and verify record counts and sample balances. Target ≤4-hour restoration and ≤24-hour data loss. Keep prior application images and migration compatibility notes; do not promise destructive migration rollback. Record actual commands, environment and timings when implementation exists.

### Risks and remaining validation
The 22-week duration depends on actual weekly hours and submission date. Validate market grading rules, late-arrival policy, 24-hour travel feasibility and administrator payment responsibilities with stakeholders. Confirm assessment architecture/language expectations. Price source access/reuse, hosted-model settings/budget and transaction retention remain external decisions. No production SLA, verified congestion reduction or legal compliance is claimed.
