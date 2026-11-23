# ADR 001: One application with explicit business boundaries

> Historical architecture. [ADR 003](003-separate-backend-services.md) supersedes
> the single-backend deployment/database assumption. Retained rules apply within
> market core; current runtime verification belongs to Stage 01.

Status: implemented foundation; messaging decision amended by
[ADR 002](002-rabbitmq.md). Business workflows pending.

Use a Next.js App Router frontend, one Java 21 Spring Boot backend and PostgreSQL
17. This follows the existing design baseline and keeps stock, reservations,
inspection and finance able to share a database transaction. The user selected
one modular backend and added RabbitMQ for asynchronous messaging. Microservices,
Redis and Kubernetes remain outside this foundation.

The initial catalog feature exercises the complete route → application service
→ domain interface → JDBC adapter → PostgreSQL flow. Flyway owns schema history.
The frontend fetches through server components with a five-second timeout and
no cached operational data. It renders an explicit failure state on API failure.

The browser connects to Next.js; only Next.js knows the Docker backend address.
No cross-origin browser API calls are needed at this stage. Public catalog
taxonomy is an explicit foundation exception to the signed-in business API
baseline: it exposes no lots, accounts, private offers or transactions.

Spring Security denies every route except the specific read-only foundation and
health endpoints. CSRF protection remains enabled. Future identity work must add
the real authentication/session lifecycle and ownership checks before enabling
business APIs. An empty user directory prevents generated default accounts;
there is no login flow or temporary development password.

Containers run application processes without root, drop Linux capabilities,
use read-only filesystems with temporary scratch space and rotate logs.
PostgreSQL uses a persistent volume and an internal network without a published
port. Local HTTP ports bind to loopback. This Compose configuration is for local
development/demo use. Public hosting still needs HTTPS, managed secrets,
off-host backups, retention decisions and operational verification.

Dependency manifests use the Spring Boot dependency BOM and compatible npm
version ranges. Registry access was denied during initialization, so there is
no generated npm lockfile yet. Run `npm install` once with registry access,
review and commit `package-lock.json`, then use `npm ci`. Docker and CI prefer
`npm ci` when the lockfile exists. Image tags must also be pinned to reviewed
digests before a reproducible release is claimed.

Baseline compatibility references:

- [Next.js installation requirements](https://nextjs.org/docs/app/getting-started/installation)
- [Spring Boot 3.5 system requirements](https://docs.spring.io/spring-boot/3.5/system-requirements.html)
