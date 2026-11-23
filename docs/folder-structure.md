# Folder structure

Current layout after the separate-service restructuring. See
[ADR 003](architecture/003-separate-backend-services.md) for ownership and
transaction boundaries. Domain scaffolds are planned structure, not completed features.

```text
Dambulla AgriFlow/
|-- compose.yaml
|-- frontend/                      Next.js application, Dockerfile and tests
|-- backend/
|   |-- pom.xml                    Maven aggregator, Java 21
|   |-- .dockerignore              Shared backend build-context exclusions
|   |-- common-contracts/          Library: transport DTOs only
|   |-- api-gateway/               Public foundation forwarding and security tests
|   |-- auth-iam-service/          Accounts, roles, sessions, recovery scaffold
|   |-- market-core-service/       Preserved catalog and transaction-owning domains
|   |-- notification-service/      Broker topology and future inbox/delivery
|   `-- analytics-ai-service/      Future authorized assistant and chat
|-- contracts/openapi/             Public API contract
|-- infrastructure/
|   |-- postgres/Dockerfile        Image reused by four isolated PostgreSQL stores
|   |-- rabbitmq/                  Broker image and configuration
|   |-- proxy/                     Future HTTPS configuration
|   `-- monitoring/                Future operational monitoring
|-- scripts/development/           Smoke and static baseline checks
|-- scripts/database/              Future database maintenance
|-- scripts/operations/            Future backup/deployment helpers
|-- tests/                         Cross-system e2e, concurrency, security, AI and load
|-- docs/
|   |-- architecture/              Current ADR 003; ADRs 001/002 retained as history
|   |-- development/               Member guide, progress, work board and decisions
|   |-- testing/                   Traceability and actual stage evidence
|   |-- operations/                Setup and recovery guides
|   |-- tools/                     Documentation generators
|   |-- diagrams/                  Editable design sources
|   `-- output/                    Historical generated design documents
`-- ui-design/                     25 static screen prototypes and generator
```

Each executable service contains its own `pom.xml`, `Dockerfile`,
`src/main/java/`, `src/main/resources/application.yml` and README. Tests belong
in the service's `src/test/java/`. Stateful services own migrations under
`src/main/resources/db/migration/`. Docker builds use `backend/` as context so
the parent and selected child can be built together.

Market domain packages live in
`backend/market-core-service/src/main/java/lk/agriflow/`: catalog, produce,
trading, visits, inspection, finance, marketprices, reporting, audit and shared
technical configuration. Use `api/`, `application/`, `domain/` and
`infrastructure/` inside each business module. Keep atomic stock, reservation,
inspection and financial changes in this service's transaction. Identity,
notification and assistant domain implementation belongs in its own service.

The frontend retains route groups under `src/app/`, business UI in `src/features/`,
shared controls/layout in `src/components/`, and HTTP helpers in `src/lib/`.
Role routes and empty test folders are scaffolds, not implemented functionality.

Production schemas belong only in the owning service's Flyway folder. Put
synthetic scenarios in test fixtures. Exclude secrets, browser profiles, caches,
runtime logs and database dumps from Git. Generated PDF/HTML files remain
historical design artifacts; current ADRs and implementation evidence govern
deployment instructions.
