# AgriFlow backend

`pom.xml` aggregates independently executable Java 21 Spring Boot services:

| Module | Responsibility |
|---|---|
| `api-gateway` | Public API entry; only catalog/system forwarding enabled |
| `auth-iam-service` | Accounts, sessions and roles; closed scaffold |
| `market-core-service` | Catalog and atomic stock, trading, visits, inspection, finance, reports and audit |
| `notification-service` | RabbitMQ topology and future notification delivery; no consumer yet |
| `analytics-ai-service` | Future authorized assistant and owned chat; closed scaffold |
| `common-contracts` | Non-deployable transport-contract namespace |

Every stateful service owns its own database and Flyway migration folder.
Never share SQL repositories or copy entities through common contracts.
The catalog V1 migration and five integration test methods moved intact into
market core. The new gateway has routing, unavailable and denial tests.

```powershell
mvn -B -f backend/pom.xml verify
mvn -B -f backend/pom.xml -pl api-gateway -am test
```

Full verification needs Docker for market-core integration tests. Build individual
images with context `backend/`, for example:

```powershell
docker build -f backend/market-core-service/Dockerfile backend
```

See [ADR 003](../docs/architecture/003-separate-backend-services.md) and
[local setup](../docs/operations/local-development.md).
