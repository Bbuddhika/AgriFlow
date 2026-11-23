# Stage 00 transaction and state review

Reviewed against the consolidated v1.5 business rules on 21 November 2026.
This is schema-design guidance; no business state machine is implemented yet.
All rows below are owned by `market-core-service` and require server-side
actor/ownership checks, fresh database time where relevant, audit and outbox
writes in the same transaction as the business change.

| Aggregate | Transition / actor | Guard and atomic effect | Proposed evidence |
|---|---|---|---|
| Lot | DRAFT → REGISTERED; owning farmer | Positive published price, valid kg and owned harvest; immutable price history | LotPublicationTest; AskingPriceDoesNotRewriteAgreementsTest |
| Offer | PENDING → ACCEPTED; lot's farmer | Lock lot/offer, reject self-trade, check available stock, snapshot offered price, create at most one reservation | AcceptanceConcurrencyTest; RepeatAcceptanceTest |
| Offer | PENDING → REJECTED by farmer or CANCELLED by buyer | Check owner and pending state; pending offers hold no stock | RejectedCancelledOfferNoHoldTest |
| Reservation | Active → confirmed / expired / cancelled | Serialize on lot/reservation; fresh time strictly before expiry to confirm; release or consume once; no automatic extension | ExpiryConfirmationRaceTest; ReservationExpiryTest |
| Lot / inspection | REGISTERED → INSPECTED or REJECTED; administrator | Record real accepted saleable kg, apply measurement difference once; rejection cancels unsold active reservations; audited reinspection to reopen | InspectionAdjustmentTest; RejectionTest |
| Reconciliation | Deficit → pending proposals → resolved | Block new reservations/confirmations; proportional 0.001 kg allocation with deterministic rounding; buyer consent only, or cancel/expire; never revive expired holds | ReconciliationConsentTest; InspectionDeficitBlocksTradeTest |
| Visit | Booked → ARRIVED → CALLED → UNLOADING → complete; administrator operates queue | Owned lots and slot capacity at booking; eligible check-in order; CALLED atomically occupies exactly one bay; completion frees bay; departure separate | SlotCapacityConcurrencyTest; BayAllocationConcurrencyTest |
| Visit recall | CALLED → ARRIVED; administrator with reason | Release bay atomically; temporarily ineligible until marked ready; preserve original arrival time; persist across restart | QueueRecallRestartTest |
| Sale / settlement | Active reservation → one full agreed-quantity sale; buyer confirms | Valid inspection, no deficit/hold, unexpired reservation, approved deductions ≤ gross; atomically consume stock and snapshot agreed price/deductions | SaleConfirmationTest; ConfirmationOwnershipTest |
| Payment evidence | No entry → directional collection or payout; administrator | Record actual external movement; independent balances; no overpayment; idempotency key and immutable evidence; zero net payout NOT_DUE | DirectionalPaymentTest; PaymentIdempotencyTest |
| Correction | Open case → linked corrections → full reversal when eligible | Freeze payments; true movement needs external resolution; preserve originals and correction date; reversed sale creates stock verification hold | LinkedReversalTest; CorrectionReportDateTest |
| Correction stock | Held → verified available or absent/loss; administrator | Release hold once; no second stock addition; absent goods need loss and hold release together | CorrectionStockHoldTest |
| Lot close | INSPECTED → CLOSED | No remaining stock or unresolved allocation/hold | StockLedgerTest |

Use decimal kg with three places and LKR with two places. Availability is stock
basis minus net sold, unexpired reservation holds and correction holds. A genuine
inspection deficit is recorded and blocked, never hidden by invented stock.
Expired holds stop reducing availability even before scheduled cleanup runs.

These transition descriptions do not choose new enum spellings for states whose
names are not fixed in the SRS. Confirm exact persistence states and constraints
in the dependent stage before migration design. Administrator authority never
substitutes for farmer deduction approval or buyer shortage/purchase consent.
