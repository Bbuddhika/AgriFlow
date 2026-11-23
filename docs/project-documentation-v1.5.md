<!-- SECTION: scope | Current scope: three roles and price negotiation -->
# SRS v1.5 — three roles and negotiated lot prices

Status: user-requested scope update. This amendment supersedes conflicting role and pricing clauses in v1.3, the historical requirements review and v1.4 business rules. Unchanged inventory, reservation, reconciliation, payment and correction rules still apply.

## Three application roles

The MVP has exactly three roles: FARMER, BUYER and ADMINISTRATOR. Separate operator and inspector accounts are deferred. Administrator responsibilities include gate check-in, slots, queues, unloading bays, physical inspection records, reinspection, shortage coordination, payment records and corrections, alongside account/catalog/price/report management.

The administrator records actual measured quality and weight; the application does not perform physical inspection. Every such action identifies the administrator and records time, reason and history. Farmers retain offer acceptance and deduction approval. Buyers retain shortage consent and purchase confirmation. Administrator access cannot substitute for either party's consent.

## Published asking price and buyer offers — FR02–FR05

1. A farmer creates a draft lot with produce type, available kg, declared grade, expected arrival and a strictly positive asking price in LKR/kg. Publishing makes the lot visible in buyer search. Draft, rejected, closed or fully unavailable lots cannot receive new offers.
2. The buyer sees the farmer's asking price, current available kg and declared/inspected grade. A separately labelled dated market reference price is informational and must never replace the farmer's asking price.
3. A **Make an offer** action lets the buyer enter a positive quantity and positive offered LKR/kg price, including a price below the asking price. Show asking price, offered price, requested kg and offered total before submission.
4. Pending offers do not reserve stock. Several buyers may submit offers for the same lot. Validate current availability on submission for useful feedback, then check it again transactionally on farmer acceptance.
5. The farmer sees their incoming offers with buyer display identity, kg, offered price, total and status, and accepts or rejects each offer. This is private price negotiation, not an auction: there is no automatic highest-bid winner, bid ranking or disclosure of other buyers' prices.
6. Acceptance freezes the offered unit price as the agreed unit price and creates a 24-hour reservation if sufficient stock remains. A price equal to the asking price still requires farmer acceptance. A farmer cannot alter the buyer's submitted price during acceptance.
7. A farmer may edit the asking price for unreserved stock, with audit history. This does not change existing pending offers or accepted reservations. Store asking_price_at_submission and listing version on each offer so both parties can see its original context.
8. A pending offer can be cancelled by its buyer. After rejection/cancellation, the buyer may submit a new offer. Direct farmer counter-offers, free-text messaging and automatic bidding are deferred; repeated offers support the basic negotiation journey.
9. Accepted offers are immutable except the already-defined consented shortage quantity amendment. Final sale gross uses the agreed offer price, never the current listing or reference price. Reject acceptance of rejected, closed or ineligible lots; insufficient stock returns a conflict.
10. Notify the farmer when a new offer arrives and the buyer when it is accepted/rejected. Both parties can view their own offer history; other buyers' private offers remain hidden.

## Example

A farmer publishes 100 kg of potatoes at **LKR 200/kg**. A buyer offers **LKR 195/kg for 50 kg**, a total of **LKR 9,750**. If the farmer accepts, 50 kg is reserved for 24 hours at LKR 195/kg and 50 kg remains available. After satisfactory inspection and buyer confirmation, the gross sale is LKR 9,750. If the farmer rejects, no stock is reserved and the buyer can submit another offer. Updating the listing to LKR 205/kg does not change the accepted LKR 195/kg agreement.

## Data, API and screen changes

- Lots: required asking_price_per_kg for publication, price_version, published_at and listing state. Use positive NUMERIC(16,2) prices; retain immutable price-change audit history.
- Offers: offered_price_per_kg, quantity_kg, asking_price_at_submission, listing_price_version, buyer/lot references and existing offer states. Reservations/sales retain agreed unit price through the accepted offer and immutable sale snapshot.
- Inspections: recorded_by_admin_id replaces the separate inspector-role reference; the physical measurement fields and history stay unchanged. Bay/queue actions record their administrator actor.
- POST /harvests/{id}/lots creates a draft; POST /lots/{id}/publish requires a valid asking price. PATCH /lots/{id}/asking-price updates an owned eligible lot with version checking. POST /lots/{id}/offers accepts quantityKg and offeredPricePerKg; accept/reject routes remain farmer-owned. Stale price edits conflict; price edits never rewrite offers.
- Farmer lot form/list/detail: asking price, publish action, incoming offers with accept/reject and agreed-price history.
- Buyer search/detail: asking price, available kg, Make an offer, offer form/total, submitted offers and reservation expiry.
- Administrator dashboard groups Market Operations, Inspections, Payments and Administration; these are sections of one role, not separate roles.

## Acceptance criteria and traceability

| Test | Requirements | Expected result |
|---|---|---|
| NEG01 | FR02–03 | Publication without positive asking price fails; valid published lot is discoverable |
| NEG02 | FR04 | LKR 195/kg offer against LKR 200/kg asking price is accepted as a pending offer; no stock held |
| NEG03 | FR05/09 | Farmer acceptance reserves requested kg for 24 hours at LKR 195/kg; sale retains that price |
| NEG04 | FR05 | Rejection/cancellation creates no hold; buyer can submit a new offer |
| NEG05 | FR03–05/09 | Asking-price changes do not mutate pending or accepted offer prices or old receipts |
| NEG06 | FR04/05 | Buyers cannot view another buyer's private offer; cannot accept their own offer as farmer |
| NEG07 | FR05 | Two acceptances exceeding remaining kg cannot both commit |
| ROLE01 | FR01/06–08/10/14 | Only administrator performs operational, inspection and financial actions; all are audited |
| ROLE02 | FR01/05/09 | Administrator cannot impersonate farmer acceptance/deduction approval or buyer consent/confirmation |

## Plan and version changes

Weeks 3–4 now establish three demo roles and their permission tests. Weeks 5–6 include publishable asking-priced lots; weeks 7–8 include buyer price offers and farmer decisions. Operations, inspection and financial workflows remain required but share the administrator dashboard. Keep the 22-week plan provisional rather than claiming an unmeasured schedule reduction.

The v1.5 PDF and this consolidated source are the current documentation baseline. Implementation and test outcomes remain pending.


<!-- SECTION: overview | Project requirements -->
## 2. Product understanding

AgriFlow coordinates a single agricultural wholesale market through a responsive web application. Farmers register produce; buyers make offers; farmers accept offers to reserve stock; administrators coordinate vehicle visits and unloading; administrators establish physical quality and weight; buyers confirm purchases; administrators record payment evidence. The software records trades and settlements but does not transfer money.

The main journey is:

`Account → harvest → lot → offer → reservation → vehicle visit → inspection → sale → settlement → payment evidence`

Visits can be booked without a reservation. A lot can have multiple buyers and partial sales. The model assistant reads authorized application information and approved help; it has no authority to change business records.

### Actors

| Actor | Responsibilities | Boundary |
|---|---|---|
| Farmer | Publish asking-priced lots, accept/reject offers, book visits, approve deductions, view own sales | Own records; cannot inspect or record payments |
| Buyer | Search lots, propose price/kg and quantity, consent to shortages, confirm purchase | Own offers/transactions; no other buyer's private offers |
| Administrator | Operations, inspections, shortages, payments, corrections, accounts, prices, reports | Audited actions; cannot impersonate farmer or buyer consent |

The assistant is a read-only feature, not an additional role. Separate operations and inspection staff accounts are future extensions.

## 3. Functional requirement inventory

IDs below preserve the source numbering. These are condensed requirements, not replacements for the original detailed clauses.

| ID | Required behavior | Acceptance emphasis |
|---|---|---|
| FR01 | Accounts, sign-in, account status, roles and access control | Restricted actions denied server-side; session expiry/revocation |
| FR02 | Farmer profile and harvest registration | Ownership, produce type, positive kg, planned arrival and validation |
| FR03 | Published asking-priced lots and QR lookup | Immutable unique IDs; QR grants no private-data access; manual lookup |
| FR04 | Buyer search and negotiated price offers | Type/kg/grade/arrival filters; positive quantity and proposed price |
| FR05 | Farmer acceptance/rejection and reservations | Atomic availability check; 24-hour expiry; release once |
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
- Availability excludes sold, reserved, lost, withdrawn and correction-held stock. Expired reservations must not consume availability even before cleanup runs.
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
| NFR-03 | No overselling, excess slot bookings or duplicate confirmed sales; recorded inspection deficits block trading | Concurrent reservation/booking/expiry/confirmation tests |
| NFR-04 | AI p95 ≤15 seconds with five concurrent chats; fallback by 20 seconds | Latency and provider-failure results |
| NFR-05 | AI ≥36/40 correct or appropriate clarifications; no permission/write-prevention failures | Fixed evaluation set plus at least 12 adversarial/permission cases |
| NFR-06 | Daily encrypted off-host backup; restore ≤4 hours; potential data loss ≤24 hours | Backup configuration and timed restore record |
| NFR-07 | Responsive at 360 px and desktop; keyboard, labels, focus, readable errors and non-colour status cues | Journey-based accessibility/usability checks |
| NFR-08 | Credential protection, minimal personal data, owned chats, redacted logs | Permission tests and configuration review |
| NFR-09 | Connectivity required for writes; safe retry without duplication | Failed-network/repeated-submit demonstrations |
| NFR-10 | Single-host deployment with HTTPS, health checks, secrets and rollback instructions | Deployment walkthrough; no production HA claim |

The SRS also requires migrations, CI, setup documentation, user guidance and a demonstration. These are delivery requirements even though they do not all have FR IDs.



<!-- SECTION: rules | Selected business rules -->
## 1. Decision record

| Decision | Selected rule | Basis |
|---|---|---|
| D01 Reservation period | 24 hours from farmer acceptance | User requested at least one day; exact 24-hour duration selected for a clear MVP rule |
| D02 Inventory basis | Auditable quantity adjustments with one authoritative stock balance | User delegated design choice |
| D03 Inspection shortage | Proportional proposed reductions, explicit buyer consent, no silent quantity changes | User delegated design choice |
| D04 Payments | Administrator records buyer collections and farmer payouts separately | User assigned payment handling to administration and delegated details |
| D05 Corrections | Linked reversing records; physical stock restored only after verification | User delegated design choice |
| D06 Unloading capacity | Explicit unloading bays reserved atomically when a visit is called | User delegated design choice |

These decisions do not add a payment gateway, automated bank transfer, trader role or physical-return workflow.

## 2. Reservation timing — FR05 and FR09

- On acceptance, `expires_at = accepted_at + 24 hours`, using server timestamps. Store timestamps consistently and display in Asia/Colombo time.
- An active reservation is valid only while server time is strictly earlier than `expires_at`. At or after that instant, confirmation fails with an expiry conflict.
- Show the expiry date/time and remaining time to both parties. Acceptance and expiry generate in-app notifications.
- Check-in, inspection, reconciliation and application downtime do not automatically extend the reservation. The MVP does not support extensions; after expiry the buyer submits a new offer and the farmer accepts subject to current availability.
- Warn at booking if the selected arrival slot ends after reservation expiry. A slot is not a promise that unloading and inspection will finish before expiry.
- Booking a visit without any reservation remains allowed. Reserving produce does not automatically book a vehicle slot.
- Expired stock holds stop affecting availability immediately, regardless of cleanup-job timing. Expiry, cancellation and confirmation must not release or consume the same quantity twice.
- Confirmation and expiry serialize on the same reservation/lot records. Use a fresh database time check after acquiring locks; a request that waited beyond expiry must fail.
- One accepted offer creates at most one reservation. Repeated acceptance returns the existing result rather than creating another hold.

Twenty-four hours is the project default, not a claim that it covers every journey. Validate it with realistic travel, queue and inspection scenarios during user evaluation.

## 3. Stock and inspection reconciliation — FR03, FR05, FR08 and FR09

### Authoritative quantities

Use kg with three decimal places and decimal arithmetic. Trade quantities must be strictly positive.

Maintain an auditable stock ledger containing initial registered quantity, signed inspection corrections, subsequent loss/withdrawal adjustments and verified restoration adjustments. Sold quantities and reservation holds are separate allocations, not duplicate stock-ledger deductions.

`stock_basis = initial_kg + sum(valid signed stock adjustments)`  
`unallocated_kg = stock_basis − net_sold_kg − unexpired_held_kg − correction_held_kg`

Correction-held kg is stock quarantined after sale reversal pending physical verification. Releasing a verified hold does not also add a positive stock adjustment, which would count the restored quantity twice. Resolving absent goods records a loss/withdrawal and releases the hold in the same transaction.

Normally `unallocated_kg` must be nonnegative. A genuine inspection shortage may expose an allocation deficit. Record the measured fact accurately, set `RECONCILIATION_REQUIRED`, display zero available for purchase and block new reservations and confirmations until the deficit is resolved. Never fabricate stock or reject a genuine measurement just to preserve the allocation invariant. Keep the raw deficit visible to authorized staff.

Inspection weight means accepted saleable weight for the entire lot before its first sale. The administrator records total measured weight, excluded/unsaleable kg, saleable kg, grade and damage percentage. Damage percentage is descriptive; it does not automatically trigger another stock deduction or monetary charge. Reject invalid measurements, including saleable weight exceeding total weight.

Example: registered 100 kg, inspected saleable 70 kg. Append a −30 kg correction; stock basis becomes 70 kg. Do not subtract the same 30 kg again as wastage. Reinspection before sales applies only the difference from the previous effective measurement. After any sale, record changes to remaining stock as explicit adjustments; do not reinterpret a measurement of remaining goods as the whole original lot weight.

### Shortage process

1. Administrator records the measurement and reason. Inspection rejection blocks all sales and cancels unsold active reservations with a notification and audit entry; reopening requires audited reinspection.
2. For accepted quality with insufficient saleable stock, place the lot on reconciliation hold. Only administrators may coordinate reconciliation; they cannot rewrite the administrator's measurement or impersonate buyer consent.
3. Calculate a proposed proportional allocation across all active reservations using their current agreed kg. Round down to 0.001 kg and distribute remaining 0.001 kg increments by acceptance time then reservation ID, without exceeding any original quantity. A zero allocation is cancelled with a reason.
4. Each affected buyer explicitly accepts the proposed reduced quantity at the existing unit price or cancels. No response leaves the original hold pending until normal expiry; the lot remains blocked. The farmer sees the changes and receives notifications. Farmer acceptance of the original offer includes this disclosed shortage policy; no price renegotiation is implied.
5. Record each accepted reduction as an immutable amendment to the reservation. Recompute deficits transactionally. Expiry/cancellation releases holds normally, and a reconciliation proposal cannot revive an expired reservation.
6. Clear the hold when commitments fit the measured stock and no outstanding proposal still requires consent. Any freed surplus becomes available for new offers; do not silently increase a buyer's accepted reduced allocation.

Example: reservations of 60 kg and 40 kg against a lot measured at 80 saleable kg produce proposals of 48 kg and 32 kg. Both buyers must agree, cancel or expire before unresolved proposals stop blocking the lot. If both agree, 80 kg is allocated. If the second cancels and the first agrees, 48 kg remains reserved and 32 kg becomes available.

One reservation confirms its full currently agreed quantity into exactly one sale. Partial lot sales remain supported through multiple reservations. Arbitrary partial confirmation of a single reservation is outside the MVP.

## 4. Administrator-managed payment records — FR10, FR13 and FR14

The application records manual financial activity. Authorized administrators record collections, payouts and corrections after the actual external payment occurs. The application does not initiate money movement.

### Separate collection from payout

- Buyer obligation is the sale gross: sold kg × agreed price/kg.
- Farmer entitlement is the sale net: gross minus approved deductions.
- Track buyer collections and farmer payouts separately. A buyer having paid does not mean the farmer has been paid.
- Default deductions to zero. Each deduction needs a category, amount, recipient/purpose and farmer approval before sale confirmation. A commission is not inferred from the existence of the platform; it is allowed only when an explicitly agreed fee exists.
- Snapshot approved deductions and unit price at confirmation. Sum of deductions cannot exceed gross. Reduced sale quantities require reapproval of any changed deduction amounts.
- For the MVP, record farmer payouts only after buyer gross collection is complete, and never above the remaining net entitlement. Partial buyer collections and partial farmer payouts are supported.
- A zero-net settlement has payout state `NOT_DUE`; do not create a fictitious payment.

Each entry includes settlement, direction (`BUYER_COLLECTION` or `FARMER_PAYOUT`), positive LKR amount, method (cash/bank/other), actual payment time, recording time, actor, payer/payee, reference/evidence note and idempotency key. Bank payments require an external reference; cash requires a receipt/reference number. File uploads are deferred; evidence references and notes are mandatory.

Compute each direction's status independently as unpaid, partially paid or paid from valid entries less linked reversals. Reject overcollection and overpayment; administrators cannot mark a settlement paid using a status toggle. Snapshot money to two decimal places using a documented decimal half-up rounding rule.

Keep these report values distinct: gross trade value, buyer collections, approved deductions, farmer payouts and outstanding balances. Deductions are not automatically platform revenue.

Example: 1,500 kg × LKR 45 = LKR 67,500 gross. Approved deductions of LKR 1,500 yield LKR 66,000 net. Once LKR 67,500 is collected, a LKR 30,000 farmer payout leaves LKR 36,000 payable. The buyer side is paid; the farmer side is partially paid.

## 5. Corrections and reversals — FR09, FR10 and FR14

- Never delete or overwrite completed sales, settlements, inspections or payment entries. Link correction entries to originals and preserve actor, time, reason and evidence.
- Payment-entry reversals correct incorrectly recorded evidence; they do not prove that money was refunded or recovered. A true refund or physical return requires a separately approved future workflow. Do not describe a correction as an actual transfer.
- Reversals cannot exceed the unreversed amount of their original entry. Concurrent corrections serialize on the settlement. Repeated requests with the same idempotency key return the original correction result.
- For an erroneous sale, an administrator opens a correction case. Freeze further payments on that sale. If valid money movement already occurred, leave the case unresolved for external resolution; never erase true collections/payouts merely to enable cancellation.
- If financial entries themselves were erroneous, correct them through linked entries. Only when no valid payment movement remains may the administrator fully reverse the erroneous sale and settlement, then create a new correctly agreed transaction if necessary. Partial sale reversals are deferred for MVP simplicity.
- Reversing the sale does not reactivate its reservation or automatically return stock to availability. Move the reversed quantity to a correction hold. An administrator physically verifies whether it is physically present and saleable; the administrator releases verified stock or records the corresponding loss/withdrawal. This prevents phantom stock after goods have left.
- Reports retain originals and show signed corrections by their effective correction date, with links to the original transaction. Show gross sales, reversals and net sales separately; do not silently rewrite historical daily totals.

## 6. Unloading-bay allocation — FR06 and FR07

- Model each zone's unloading capacity as explicit enabled bays. Booking capacity per slot is a separate limit from simultaneous unloading capacity.
- The administrator calls the earliest eligible checked-in visit by check-in timestamp, then visit ID. Any permitted priority override requires a reason and audit entry.
- Calling a visit atomically reserves one free bay and changes the visit from `ARRIVED` to `CALLED`. Enforce at most one active visit per bay and one bay per visit at database level.
- `CALLED` and `UNLOADING` both occupy the bay. Moving to `UNLOADING` records actual unloading start without acquiring a second bay.
- Completion releases the bay and records unloading completion. Departure is a separate timestamp after completion and does not keep the bay occupied.
- If a called vehicle does not respond, the administrator may explicitly recall it to `ARRIVED`, release the bay and record a reason. Set it temporarily ineligible until the administrator marks it ready, preserving its original arrival timestamp for ordering once ready. No automatic timeout releases a potentially occupied bay.
- Do not cancel, disable or reassign an occupied bay without an explicit audited operational resolution. Application restarts preserve occupancy; the administrator reconciles it with the physical site.
- Use a transaction and database constraints/locks for allocation, release and recall. A losing concurrent call receives a conflict and refreshed availability.

## 7. Required design and acceptance updates

Add to the ERD/data dictionary: stock adjustments, reconciliation cases/proposals, immutable reservation amendments, approved deduction snapshots, directional payment entries, payment reversals, sale correction cases, stock correction holds, unloading bays and active allocations. Store authoritative balances or derive them consistently; cached totals must not become independent sources of truth.

Add corresponding APIs, screens, permissions and audit events. Farmers see revised stock and deduction proposals; buyers see shortage consent and 24-hour expiry; administrators see separate collections/payouts and correction cases; administrators see reserved/occupied bays.

Required tests:

1. Reservation accepted at 10:00 expires at 10:00 the next day; confirmation just before expiry may succeed, at expiry must fail.
2. Concurrent expiry and confirmation commit one outcome with no duplicate stock effect.
3. A 100-to-70 kg inspection correction applies once and blocks overallocated sales without hiding the measured deficit.
4. The 60/40-to-48/32 shortage example requires consent and handles cancellation, expiry and rounding without overallocating stock.
5. Buyer collection does not change farmer payout status; duplicate and excess payments are rejected.
6. Unapproved deductions cannot enter a confirmed settlement; no deduction exceeds gross.
7. Sale reversal never automatically makes absent goods available and never silently cancels real payments.
8. Two simultaneous calls for one free bay produce exactly one allocation; restart preserves occupancy.
9. Recall releases one allocation once and prevents immediate redispatch while the visit is marked unready.
10. Farmers and buyers cannot record administrator-only financial corrections or payments.



<!-- SECTION: design | System design and verification -->
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


<!-- SECTION: plan | Implementation and delivery plan -->
## 7. Suggested updates to the 22-week plan

Keep the source schedule as a provisional baseline. Improve its exit conditions rather than adding more features.

| Weeks | Focus | Exit condition |
|---|---|---|
| 1–2 | Validation, policy decisions, SRS/design foundation and backlog | Selected business rules reviewed; MVP boundary, permissions, state diagrams, ERD and core wireframes reviewed |
| 3–4 | Identity, profiles, migrations and CI | Three demo roles; role/ownership denial and account lifecycle checks |
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

Required: the three roles, complete produce-to-payment-record journey, safe reservations and capacity, inspection, dated prices, notifications, reports, audit, six read-only AI question types, deployment and restore demonstration.

Optional: CSV report export, dedicated demo mode, richer charts and downloadable lot labels. Reference-price CSV import is already part of the baseline and must not be confused with optional report export.

Deferred: trader/stall workflows, counter-offers, broadcast matching, SMS/push, mobile apps, full localization, offline writes, forecasting, payment gateways, multiple markets, microservices, message broker and Kubernetes.

