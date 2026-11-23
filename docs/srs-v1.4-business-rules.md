# Dambulla AgriFlow — SRS v1.4 business-rule amendments

Historical version notice: [v1.5 roles and negotiation](srs-v1.5-roles-and-negotiation.md) supersedes earlier five-role and price-listing clauses. Use the v1.5 PDF as the current consolidated baseline.

Date: 3 November 2026  
Status: project design baseline based on the user's direction and delegated implementation choices; stakeholder validation remains pending.  
Scope: resolves review decisions D01–D06. This is an amendment to v1.3, not a complete replacement SRS. Where these rules conflict with v1.3, these amendments take precedence. The original DOCX is retained unchanged.

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

Inspection weight means accepted saleable weight for the entire lot before its first sale. The inspector records total measured weight, excluded/unsaleable kg, saleable kg, grade and damage percentage. Damage percentage is descriptive; it does not automatically trigger another stock deduction or monetary charge. Reject invalid measurements, including saleable weight exceeding total weight.

Example: registered 100 kg, inspected saleable 70 kg. Append a −30 kg correction; stock basis becomes 70 kg. Do not subtract the same 30 kg again as wastage. Reinspection before sales applies only the difference from the previous effective measurement. After any sale, record changes to remaining stock as explicit adjustments; do not reinterpret a measurement of remaining goods as the whole original lot weight.

### Shortage process

1. Inspector records the measurement and reason. Inspection rejection blocks all sales and cancels unsold active reservations with a notification and audit entry; reopening requires audited reinspection.
2. For accepted quality with insufficient saleable stock, place the lot on reconciliation hold. Only administrators may coordinate reconciliation; they cannot rewrite the inspector's measurement or impersonate buyer consent.
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
- Reversing the sale does not reactivate its reservation or automatically return stock to availability. Move the reversed quantity to a correction hold. An inspector verifies whether it is physically present and saleable; the administrator releases verified stock or records the corresponding loss/withdrawal. This prevents phantom stock after goods have left.
- Reports retain originals and show signed corrections by their effective correction date, with links to the original transaction. Show gross sales, reversals and net sales separately; do not silently rewrite historical daily totals.

## 6. Unloading-bay allocation — FR06 and FR07

- Model each zone's unloading capacity as explicit enabled bays. Booking capacity per slot is a separate limit from simultaneous unloading capacity.
- The operator calls the earliest eligible checked-in visit by check-in timestamp, then visit ID. Any permitted priority override requires a reason and audit entry.
- Calling a visit atomically reserves one free bay and changes the visit from `ARRIVED` to `CALLED`. Enforce at most one active visit per bay and one bay per visit at database level.
- `CALLED` and `UNLOADING` both occupy the bay. Moving to `UNLOADING` records actual unloading start without acquiring a second bay.
- Completion releases the bay and records unloading completion. Departure is a separate timestamp after completion and does not keep the bay occupied.
- If a called vehicle does not respond, the operator may explicitly recall it to `ARRIVED`, release the bay and record a reason. Set it temporarily ineligible until the operator marks it ready, preserving its original arrival timestamp for ordering once ready. No automatic timeout releases a potentially occupied bay.
- Do not cancel, disable or reassign an occupied bay without an explicit audited operational resolution. Application restarts preserve occupancy; the operator reconciles it with the physical site.
- Use a transaction and database constraints/locks for allocation, release and recall. A losing concurrent call receives a conflict and refreshed availability.

## 7. Required design and acceptance updates

Add to the ERD/data dictionary: stock adjustments, reconciliation cases/proposals, immutable reservation amendments, approved deduction snapshots, directional payment entries, payment reversals, sale correction cases, stock correction holds, unloading bays and active allocations. Store authoritative balances or derive them consistently; cached totals must not become independent sources of truth.

Add corresponding APIs, screens, permissions and audit events. Farmers see revised stock and deduction proposals; buyers see shortage consent and 24-hour expiry; administrators see separate collections/payouts and correction cases; operators see reserved/occupied bays.

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
10. Farmers, buyers and inspectors cannot record administrator-only financial corrections or payments.

## 8. Documentation and schedule consequences

Update SRS sections 4, 8, 10 and Appendices A–D to reference these rules. Replace all normative two-hour reservation references with 24 hours; retain old references only in revision history. Amend the previous no-negative-stock target to distinguish prohibited overselling from a legitimately recorded inspection deficit that blocks trading until reconciled.

Re-estimate weeks 11–12 for consent, directional payments and correction holds. These rules resolve ambiguity within the existing scope but require additional screens and tests. The 22-week schedule remains provisional until weekly effort and the submission deadline are known. Remaining review decisions D07–D19 still require tracking; this amendment also resolves D08 and the repeated-acceptance part of D09.
