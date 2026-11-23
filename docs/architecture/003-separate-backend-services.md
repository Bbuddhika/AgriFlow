# ADR 003: Separate backend services

Status: selected by the user; service scaffold implemented 21 November 2026.
Build and runtime evidence are recorded separately in Stage 00/01 evidence.

This supersedes ADR 001's single-deployment decision and ADR 002's single-backend
assumption. RabbitMQ remains required. The structural reference is the local
BitCraft_SwiftDrop backend: Maven aggregator, independently executable Spring
Boot children, per-service Dockerfiles, configuration and database ownership.
AgriFlow retains Java 21 and its own requirements and service boundaries.

| Module | Owns | Database | Current behavior |
|---|---|---|---|
| `api-gateway` | External API entry, future authenticated routing | None | Two public foundation GET routes to market core; other routes denied |
| `auth-iam-service` | Accounts, roles, sessions, recovery | `agriflow_identity` | Health and closed security scaffold |
| `market-core-service` | Catalog, harvests, lots, offers, reservations, visits, inspection, sales, finance, reference prices, reports, audit/outbox | Existing `agriflow` database | Original catalog, migration, topology and five integration test methods |
| `notification-service` | Event delivery, deduplication, owned notification inbox | `agriflow_notifications` | Health, database connection and RabbitMQ topology; no consumer |
| `analytics-ai-service` | Owned chat, approved help, provider adapters, authorized read tools | `agriflow_assistant` | Health and closed security scaffold; no model integration |
| `common-contracts` | Versioned transport DTOs only | None | Non-deployable library namespace; no shared business implementation |

Each database has its own PostgreSQL container, owner, password, volume and
network. Only its owning application joins that data network. Services must
not use another service's SQL, migrations or repositories. Market core keeps
the existing `database` Compose service and `postgres-data` volume; no destructive
database conversion is performed. New stores initialize separately. Do not
rename the market volume or replay its V1 migration into a different existing store.

The gateway is the only backend with a host port (`BACKEND_PORT`, default 8080).
The frontend uses `http://api-gateway:8080` inside Compose. Every application
listens on container port 8080; native runs need distinct `SERVER_PORT` values.
Dockerfiles use `backend/` as build context and select one Maven child with `-pl`.
No child is packaged into another service's executable.

## Transaction boundary

Stock, reservation expiry, inspection reconciliation, buyer confirmation,
settlement and corrections require atomic database changes. They stay inside
market core. Separating these packages into services would require a new
distributed consistency design and revised acceptance tests; this scaffold
does not replace the existing guarantees with cross-service database writes.

Market mutations must commit audit, idempotency and outbox records together.
Notification delivery follows committed events through RabbitMQ with stable
event IDs and persistent recipient deduplication. No outbox or consumer is
implemented yet. Both market and notification declare the same durable topology
for the existing foundation tests; move topology contract ownership and broaden
event schemas in Stages 02/16/17 before adding business consumers.

Identity must provide a vetted authentication boundary before protected routes
are enabled. Each service must verify trusted identity and enforce ownership;
caller-supplied identity headers cannot grant access. Identity outages must fail
closed. Assistant tools call authorized service APIs and never query market SQL.
Reports of stock and finance remain authoritative market-core queries.

## Verification and rollout

Stage 00 verifies layout, ownership planning, traceability and exclusions.
Stage 01 must verify the Maven reactor, gateway outage/security tests, preserved
catalog integration tests, frontend, all eleven Compose containers and the smoke
journey. Health in new services establishes dependency readiness only; it does
not establish completed identity, notifications or assistant functionality.

The gateway readiness probe describes the gateway process. Market dependency
readiness is checked by Compose and the smoke catalog request. Broker/core
readiness policy remains a Stage 16 decision. Later routing and service auth
need explicit timeout, error, retry and revocation tests.
