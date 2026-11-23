# Local development and Docker

## First start

Use Docker Desktop in Linux container mode. From the repository root:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `POSTGRES_PASSWORD`, `RABBITMQ_PASSWORD`, `IDENTITY_DB_PASSWORD`,
`NOTIFICATION_DB_PASSWORD` and `ASSISTANT_DB_PASSWORD` in `.env` to distinct local values, then run:

```powershell
docker compose config --quiet
docker compose up --build --wait
docker compose ps
python scripts/development/smoke_check.py
```

The frontend serves at http://localhost:3000 and the backend at
http://localhost:8080. Override `FRONTEND_PORT` and `BACKEND_PORT` in `.env` if
those ports are occupied. For custom ports, set `FRONTEND_URL` and `BACKEND_URL`
before running the smoke check. PostgreSQL is accessible only inside Compose.
The built images are `dambulla-agriflow-frontend:0.1.0`,
`dambulla-agriflow-<service>:0.1.0` for each backend service, `dambulla-agriflow-database:0.1.0` and
`dambulla-agriflow-rabbitmq:0.1.0`.
Set `IMAGE_TAG` in `.env` to change their shared release tag. The database image
inherits the official PostgreSQL 17 Alpine image without changing its behavior.
RabbitMQ inherits the RabbitMQ 4 management Alpine image. Its management UI is
at http://localhost:15672; sign in using `RABBITMQ_USER` and `RABBITMQ_PASSWORD`.
The default virtual host is `agriflow`. The AMQP port is private to the Compose
network. Override `RABBITMQ_MANAGEMENT_PORT` if the UI port is occupied.
Do not copy `.env` into Git.

`docker compose stop` pauses the services. `docker compose down` removes the
containers and preserves the named database and broker volumes. Do not use `down --volumes`
unless intentionally discarding the database and queued messages. Changing the database password in
`.env` does not change the password in an already initialized PostgreSQL volume;
rotate it in PostgreSQL and then update application configuration.
Likewise, RabbitMQ default credentials and the virtual host initialize a new
broker volume only. Update existing users with RabbitMQ administration tools
when rotating credentials; editing `.env` alone does not rotate them.

The first startup applies `V1__create_produce_catalog.sql`. It inserts six produce
types, without sample offers, stock, sales, users or prices. Never edit an
already-applied migration; add a new numbered migration.

## Separate service deployment

The gateway is the external backend at port 8080; market core and the other
services have no host ports. Five backend services, four PostgreSQL stores,
one RabbitMQ broker and one frontend make eleven containers. New service health
does not imply implemented business features. See ADR 003 for database ownership.

The existing `database` service and `postgres-data` volume retain market data.
Identity, notifications and assistant initialize separate stores and volumes.
Changing an environment password does not rotate an initialized database user.
Rehearse backup/restore for each store independently before deployment; the
market example below covers only catalog data. Do not delete existing volumes.

## Native application development

Use Node.js 22, Java 21 and Maven 3.9+. The checked-in frontend configuration
expects the backend on localhost:8080 unless `API_BASE_URL` is changed.

```powershell
cd frontend
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm.cmd ci
npm.cmd run dev
```

The committed lockfile fixes dependency resolution. Use `npm.cmd ci`; Docker
and CI also require the lockfile. To run market core outside Docker,
provide a reachable PostgreSQL database with `DB_URL`, `DB_USERNAME` and
`DB_PASSWORD` in the terminal environment. Also provide a reachable RabbitMQ
broker with `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`,
`RABBITMQ_PASSWORD` and `RABBITMQ_VHOST`. Compose does not publish AMQP; a native
backend needs a separately reachable broker or a local Compose override that
binds port 5672 to loopback. For market core set `SERVER_PORT=8082`; the gateway defaults to
`MARKET_CORE_URL=http://localhost:8082` and listens on port 8080. Then run:

```powershell
mvn -f backend/pom.xml -pl market-core-service spring-boot:run
```

## Build and verify

```powershell
mvn -B -f backend/pom.xml verify
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run typecheck
```

Backend integration tests require Docker and use disposable PostgreSQL 17 and
RabbitMQ 4 Testcontainers instances. They verify migrations, catalog reads,
denied protected routes, queue declarations, confirmed message routing,
dead-letter delivery and dependency readiness. CI additionally builds and starts the complete
stack, then runs Python smoke and outage checks against real HTTP responses.

```powershell
python scripts/development/check_baseline.py --compose
python scripts/development/smoke_check.py
python tests/e2e/catalog_outage.py
```

The outage check deliberately stops only `market-core-service`, checks the
gateway's safe 503 and frontend unavailable screen, then restores the service
and verifies all six types. Run it against the local development stack. It does
not remove volumes or alter catalog data.

## Local backup and restore rehearsal

Use a new file path for each backup. Keep backups outside source control.
The following avoids piping binary archives through Windows PowerShell:

```powershell
docker compose exec -T database sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/agriflow.dump'
docker compose cp database:/tmp/agriflow.dump ./agriflow-local.dump
```

To rehearse restore without replacing the working database, copy the archive
back to the database container and create a separate database:

```powershell
docker compose cp ./agriflow-local.dump database:/tmp/restore.dump
docker compose exec -T database sh -c 'createdb -U "$POSTGRES_USER" agriflow_restore_check'
docker compose exec -T database sh -c 'pg_restore -U "$POSTGRES_USER" -d agriflow_restore_check --no-owner --exit-on-error /tmp/restore.dump'
docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d agriflow_restore_check -c "SELECT count(*) FROM produce_types;"'
```

The initial catalog count should be six. This local rehearsal does not implement
scheduled encrypted off-host backups or prove the recovery objectives.

## Historical verification recorded during initialization

Current verified foundation results are recorded in
`docs/testing/evidence/stage-01.md`; all nine backend tests, frontend build,
eleven-container health and smoke/outage/recovery passed locally on 23 November 2026.
The following is historical and does not establish verification of the new layout.

- Passed: Docker Compose configuration validation.
- Passed: source JSON/XML parsing and Python syntax checks.
- Passed after RabbitMQ addition: Compose validation and project image-name checks.
- Blocked: npm installation; registry requests rejected with `EACCES`.
- Blocked: Maven build; dependency resolution unavailable in this restricted environment.
- Blocked: Docker builds, PostgreSQL/RabbitMQ integration tests, HTTP smoke check
  and browser QA; access to the Docker engine is denied and dependencies could
  not be installed.
- Not run: CI workflow and backup/restore rehearsal.

These are explicit limits, not passing build or production readiness claims.
