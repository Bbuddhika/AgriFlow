# Dambulla AgriFlow

Agricultural market coordination system under development.

- [Member implementation guide](docs/development/member-guide.md)
- [Current progress and Stage 00 evidence](docs/development/progress.md)
- [Service boundaries and architecture decision](docs/architecture/003-separate-backend-services.md)
- [Folder structure](docs/folder-structure.md)
- [Local setup](docs/operations/local-development.md)
- [Current functional requirements](docs/project-documentation-v1.5.md)
- [UI prototypes](ui-design/README.md)

The backend follows a Maven multi-module service layout: API gateway, identity,
market core, notifications and assistant, plus a common-contracts library.
Each stateful service owns a separate PostgreSQL store. RabbitMQ supports
asynchronous messaging. Stock, reservations, inspection and finance stay inside
market core so critical changes can share a transaction.

Only the original public catalog, system metadata, health endpoints and narrow
gateway forwarding are implemented. Identity, trading, operational workflows,
notification delivery and assistant business features remain planned. Static
HTML prototypes are design references, not functional application screens.

## Local start

Requires Docker Desktop with the Linux engine running.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Set all five password variables in .env to distinct local values.
docker compose up --build --wait
python scripts/development/smoke_check.py
```

Frontend: http://localhost:3000. Gateway: http://localhost:8080.
RabbitMQ management: http://localhost:15672. Internal applications and databases
have no host ports. Service Dockerfiles live in `backend/<service>/Dockerfile`
and use `backend/` as build context. Do not overwrite an existing `.env`.

Run `python scripts/development/check_baseline.py` for static layout and planning
checks. Runtime/build results and limitations are recorded in the progress tracker.
