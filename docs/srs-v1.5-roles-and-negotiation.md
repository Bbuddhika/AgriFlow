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

The original Word document and v1.4 PDF are historical snapshots. The v1.5 PDF and this amendment are the current documentation baseline. Implementation and test outcomes remain pending.
