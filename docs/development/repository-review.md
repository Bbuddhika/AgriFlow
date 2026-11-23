# Repository review for the implementation guide

Original review date: 16 November 2026. Follow-up: 21 November 2026. Scope: the local Dambulla AgriFlow workspace.
This is a source/documentation review, not a new runtime acceptance test.

## Restructuring follow-up — 21 November 2026

[ADR 003](../architecture/003-separate-backend-services.md) supersedes the
single-backend decision in this historical review. The catalog source, migration
and test class moved intact to `backend/market-core-service/`. A Maven parent,
gateway and three closed service scaffolds now provide separate builds and
database ownership. No new business feature is claimed complete.

R03 is updated: local `main` exists, with no commit or remote. R13 is addressed
by `.browser-profile/`, `.chrome-profile/` and `.cache/` exclusions. The
[Stage 00 evidence](../testing/evidence/stage-00.md) records current checks.
The original findings below remain the historical review rather than current
deployment instructions. Runtime, dependency locking and feature gaps remain
Stage 01 and later work.

## What was reviewed

- Current consolidated v1.5 requirements, historical v1.4/v1.5 amendments,
  requirements review and system-design supplement.
- The original v1.3 DOCX text, confirming an individual student project with a
  provisional 22-week horizon; its older conflicting rules are superseded.
- All present Java, SQL, TypeScript/TSX, CSS, application/build configuration,
  Dockerfiles, Compose, CI, OpenAPI and smoke-check source files.
- Documentation/build tooling, UI generator, manifest and layout-check script.
- All 25 prototype HTML pages through their markup/text and local-link metadata;
  generated diagram XML and documentation output references.
- Existing generated/binary artifacts were inventoried. The editable sources,
  rather than an independent visual audit of every PDF/image, determine the plan.

See [the file inventory](file-inventory.csv) for per-file classification.
Dependency caches, browser profiles, private `.env` files and empty `.gitkeep`
placeholders are excluded from source review. Browser profile storage is not
application code or project evidence; it may contain personal browsing state.

## Source precedence

| Source | Treatment |
|---|---|
| Explicit current user choices | One modular backend, one PostgreSQL database, RabbitMQ required, project-named images |
| `docs/project-documentation-v1.5.md` | Current functional/business baseline, except superseded broker deferral |
| Architecture ADR 001 and ADR 002 | Current deployment and RabbitMQ decisions |
| Application code/configuration | Evidence of what is present; code presence does not establish tested completion |
| v1.4/v1.5 amendments and system-design supplement | Supporting history, cross-checked against the consolidated source |
| Original v1.3 DOCX and historical requirements review | Context; do not reinstate five roles or the old two-hour reservation proposal |
| Screenshot examples | Guide structure only; delivery roles, ports, tables and customer-only chatbot are unrelated |

## Current implementation map

| Area | Present | Remaining |
|---|---|---|
| Backend entry/build | One Spring Boot entry point and Maven manifest | Resolve dependencies and prove compilation/tests |
| Catalog | Controller → service → domain interface → JDBC adapter; V1 creates six produce types | Grade management, administrative mutations and authenticated business use |
| Identity/security | Empty in-memory identity directory, explicit public foundation GETs, remaining routes denied, CSRF retained | Registration/login/recovery, persistent sessions, roles, ownership and suspension |
| API errors | Database exceptions mapped to safe 503 ProblemDetail | Distinguish invalid input/conflicts/outages and add code/trace contract |
| Frontend | Public server-rendered catalog page, root layout/CSS, health route and server-only read helper | Authenticated routes, mutation client/CSRF forwarding, operational feature screens |
| Domain modules | Package scaffolds for the planned domains | Harvests, lots, stock, offers, reservations, visits, inspection, finance, reports, assistant |
| Database | One produce catalog migration | All business tables, constraints and transactional audit/idempotency/outbox persistence |
| RabbitMQ | AMQP dependency/config, exchanges, notification/DLQ topology and broker service | Event envelopes, outbox writer/dispatcher, business publishers, deduplicating consumers and replay operations |
| Docker | Four project-named images, colocated Dockerfiles, health checks, named data volumes, loopback app/UI ports | Successful image build/start, release digest pinning and hosted HTTPS/secrets |
| Tests | Five backend integration methods and HTTP smoke script | Actual execution evidence and the complete FR/NFR suites |
| CI | Backend verify, frontend build/typecheck and Compose smoke jobs | Remote Git setup, successful runs, locked dependency installation |
| UI prototypes | 25 static screens; 46 saved viewport checks | Functional React journeys and missing authentication/admin/report/audit/assistant states |
| Recovery | Example local backup/restore commands | Timed rehearsal, scheduled encrypted off-host backups, retention/replay and operational evidence |

The only explicit business API currently implemented is public catalog taxonomy.
`/api/v1/system` and health endpoints are foundation metadata. Draft API inventory
entries in the SRS are not implemented endpoints.

## Existing tests: source present, results not established

File: `backend/src/test/java/lk/agriflow/CatalogIntegrationTest.java`.

| Test method | What it is intended to prove |
|---|---|
| `notificationQueuesAreDeclaredOnTheBroker` | Notification and dead-letter queue declarations |
| `confirmedMessagesRouteAndRejectedMessagesReachTheDeadLetterQueue` | Confirmed synthetic routing, explicit rejection and dead-letter delivery |
| `migrationsAndCatalogReadWorkAgainstPostgres` | V1 migration and ordered six-item catalog API |
| `unknownProtectedResourcesAreNotPublic` | Unknown protected GET and unauthenticated mutation denial |
| `readinessIncludesDatabaseAndRabbitMq` | Readiness with both test dependencies available |

These tests use disposable PostgreSQL/RabbitMQ containers. No existing test
establishes account lifecycle, reservation correctness, financial rules or AI
behavior. The synthetic RabbitMQ message does not execute a real trade.

## Findings to address in stage order

| Finding | Evidence / implication | Follow-up |
|---|---|---|
| R01 — Builds not demonstrated | Earlier npm/Maven attempts were denied network access; Docker engine access was denied. No new runtime test was run for this guide. | Stage 01: establish access and record real builds/tests |
| R02 — Unlocked frontend | `frontend/package-lock.json` is absent; Docker/CI permit `npm install` fallback. | Stage 01: resolve/review/commit the lock, then require `npm ci` |
| R03 — No Git repository | No `.git` directory was present in this snapshot. | Stage 00: initialize/connect Git and define the real base branch; no assumed `dev` |
| R04 — Auth is a closed foundation | No registered accounts, no login flow and no authenticated request forwarding in the server-only read helper. | Stages 02–03: choose the session boundary and implement server-side ownership |
| R05 — Errors are too coarse | `ApiExceptionHandler` maps all `DataAccessException` subclasses to 503, including potential integrity conflicts. | Stage 02: map validation/conflict/outage separately and add safe traceable responses |
| R06 — RabbitMQ topology is partial | Five existing event bindings omit new/rejected offers and some shortage outcomes required by the SRS. No producer/consumer runs yet. | Stages 02, 16–17: outbox, complete contracts, dispatch and idempotent consumption |
| R07 — Broker is part of global readiness | Startup waits for RabbitMQ and backend readiness includes `rabbit`. A broker outage can mark the whole backend unready even when synchronous database work could continue. | Stage 16: explicitly decide core-versus-messaging readiness and prove notification failure does not undo trades |
| R08 — Public catalog is an explicit exception | ADR 001 permits nonprivate taxonomy/metadata reads while the SRS normally requires sign-in. | Stages 00/03: retain/document the narrow exception; no public lots/private records by accident |
| R09 — Old scope defers RabbitMQ | The final consolidated deferred-scope paragraph predates the user's broker decision. | Use ADR 002; Stage 24 updates the released SRS/diagrams rather than silently reverting the decision |
| R10 — Prototype counts differ | The manifest has 9 Farmer, 11 Buyer and 5 Administrator screens. | UI README counts corrected in this guide change; distinguish prototypes from app routes |
| R11 — Prototype rebuild overwrites metadata | `ui-design/build.py` rewrites `screen-manifest.json` with a generic no-Figma-file status and can drop the current target Figma key/URL. | Preserve target metadata before any rebuild; fix generator preservation in a future design task |
| R12 — Historical patch utility | `docs/tools/update_v15.py` mutates the documentation generator using text replacements. | Do not run it as routine setup; use the current builder only when regenerating intended outputs |
| R13 — Browser/profile artifacts | `docs/.browser-profile/` contains generated browser state and is not covered by the root ignore entries. | Stage 00: exclude these artifacts before staging files; never include profile databases in commits/evidence |
| R14 — Smoke test assumes initial fixtures | Smoke check expects exactly six produce types and `stage=foundation`. | Keep a dedicated baseline fixture or revise checks when catalog administration/release stage changes |
| R15 — Operational settings are not policies | Queue retention/replay, off-host backup, grading thresholds, provider settings and transactional retention are not completed by Compose health checks. | Review before dependent features/release; Stages 04, 16–17, 21 and 23 |

## Prototype-to-stage map

| Existing prototype keys | Implementation stage |
|---|---|
| `farmer-home`, `farmer-create` | 03–05: role home, harvest and lot forms |
| `farmer-lots` | 05: lot list/detail/QR |
| `farmer-offers`, `farmer-accepted`, `farmer-rejected` | 06–08: offers and decisions |
| `farmer-visit` | 09–10: booking and queue visibility |
| `farmer-settlement`, `farmer-paid` | 13–14: deductions and independent collection/payout states |
| `buyer-explore`, `buyer-lot`, `buyer-offer`, `buyer-offers`, `buyer-cancelled` | 05–08: market search, negotiation and cancellation |
| `buyer-reservation`, `buyer-expired` | 07–08: reservation and expiry |
| `buyer-shortage`, `buyer-shortage-agreed` | 12: shortage consent |
| `buyer-confirm`, `buyer-receipt` | 13–14: purchase confirmation and payment-evidence visibility |
| `admin-queue`, `admin-mobile` | 09–10: gate/queue/unloading |
| `admin-inspection` | 11–12: inspection and reconciliation |
| `admin-payments` | 14–15: collections/payouts/corrections |
| `admin-overview` | 19: authoritative reporting |

Still design and implement login/recovery/profiles, detailed booking, notification
inboxes, catalog/prices/imports, correction cases, audit/report filters and
role-scoped chat. Review missing empty/loading/error/denied states alongside each
feature. A prototype labelled approved/paid must not substitute for a recorded
external payment and the correct independently derived payout state.

## Recorded verification boundaries

### Stage 01 follow-up — 23 November 2026

[Stage 01 evidence](../testing/evidence/stage-01.md) supersedes the original
registry/Docker blockers and the missing-lockfile finding: registry access is
available, the frontend lock is resolved, and Docker/CI require `npm ci`.
All nine backend test methods (four gateway and five catalog/broker integration)
passed, along with the frontend production build and explicit TypeScript check.
Live Compose and outage/recovery status is recorded in that evidence, rather
than inferred from these build results. Identity, business workflows, an outbox
dispatcher, notification consumption and assistant functionality remain pending.

### Original guide verification boundary

Previous work recorded passing Compose configuration/path/name checks and
source-format checks. This documentation task checks guide links, stage/trace
coverage and inventory consistency. It does not rerun application builds,
Docker integration tests, browser tests, benchmarks, model evaluation or recovery.
Use Stage 01 and later stage evidence to replace historical blockers with actual
observed results. Do not mark failures resolved solely because this plan exists.
