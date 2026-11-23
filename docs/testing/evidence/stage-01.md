# Stage 01 evidence — foundation verification

Run date: 23 November 2026, Asia/Colombo. Operator: Codex in the local workspace.
Branch: `feature/agriflow-s01-foundation-verification`, based on `dev` at `1418bfd`.
Snapshot: that baseline plus the Stage 01 changes committed with this evidence.
Scope: dependency locking, builds, topology/readiness, closed-route security,
and catalog connected/unavailable behavior. No completed identity, trading,
notification delivery or assistant functionality is claimed.

## Environment

| Component | Observed |
|---|---|
| Host | Windows 11 amd64; PowerShell |
| Node / npm | 22.15.1 / 11.10.1 |
| Native Java / Maven | Temurin 25.0.5 / Maven 3.9.11; compiler release 21 |
| Container Java / Node | Temurin 21.0.13.1 / Node 22.23.5 |
| Docker Engine | 29.8.1, Linux engine; 7532 MB available to Docker |
| Spring Boot / Testcontainers | 3.5.16 / 1.21.4 |
| Locked frontend | Next.js 16.4.6, React/React DOM 19.3.1, server-only 0.0.1 |
| Data | Synthetic six-type taxonomy from the original V1 migration |
| Database / broker | PostgreSQL 17.12 / RabbitMQ 4.4.1 |

Docker Desktop was initially stopped and was started for this run. Five blank
password settings in the ignored local `.env` were filled independently with
random values without displaying them; existing nonempty settings were preserved.
No secret file is committed. Shell commands required approved execution outside
the sandbox because Windows sandbox setup fails before commands run.

## Results

| Check | Result | Evidence |
|---|---|---|
| Initial dependency resolution | PASS | 30 packages installed; npm reported zero vulnerabilities |
| Lockfile review | PASS | Direct versions above; zero nonstandard package registries |
| Clean `npm ci` | PASS | Successful locked reinstall |
| Frontend production build | PASS | Compiled, typechecked and generated standalone output |
| Explicit TypeScript check | PASS | `tsc --noEmit` exited successfully |
| Backend reactor verify | PASS | Four gateway tests and five PostgreSQL/RabbitMQ integration tests; zero failures/errors/skips; reactor finished 08:48:37 +05:30 |
| Eleven-container build/start/health | PASS | All eleven running and healthy, including after recovery; eight unique image IDs in the runtime artifact |
| HTTP smoke | PASS | Gateway readiness, six catalog types, kg units and all six names rendered by frontend |
| Outage/recovery | PASS | Stopped market core: gateway 503 and frontend unavailable with no catalog cards; restarted market core: all six types rendered again |
| Static baseline / Compose ownership | PASS | Service layout, all 41 requirement mappings, private-artifact exclusions, build paths and isolated database networks |

Stage 01 exit conditions are satisfied. The stack was left running and healthy.
See [runtime metadata](stage-01-runtime.json) for the observation time, service
health and eight local image IDs. IDs identify the tested local artifacts;
this does not publish images or establish reviewed release-digest pinning.

```text
Backend: tests run 9, failures 0, errors 0, skipped 0; reactor BUILD SUCCESS
Frontend: npm ci, production build and tsc --noEmit PASS
Compose: 11/11 containers running and healthy
PASS: gateway readiness, catalog API and frontend integration
PASS: stopped market -> gateway 503 and frontend unavailable without catalog cards
PASS: market restored -> all six catalog types render again
```

These are local executed results. The updated GitHub Actions workflow is prepared
to run the same checks; a successful hosted CI run is not inferred from local tests.

## Reproduction

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend run typecheck
$env:DOCKER_HOST='npipe:////./pipe/dockerDesktopLinuxEngine'
mvn -B -f backend/pom.xml verify
docker compose --parallel 1 up --build --wait --wait-timeout 600
python scripts/development/check_baseline.py --compose
python scripts/development/smoke_check.py
python tests/e2e/catalog_outage.py
docker compose ps
```

Create `.env` from `.env.example` only if absent and configure five passwords.
Native Windows Maven may need `DOCKER_HOST` above; Linux CI uses its normal socket.

## Changes and boundaries

- Locked dependencies; Docker and CI require `npm ci` with no unlocked fallback.
- CI caches npm by lockfile and runs real catalog outage/recovery acceptance.
- Next regenerated its TypeScript environment file for the installed version.
- The setup guide's malformed `.env.local` copy example was corrected.
- The outage script always attempts restart in `finally`; it checks actual HTTP
  responses and absence of rendered catalog cards during the outage.
- Reviewed release digests, hosted TLS, backup restoration and business acceptance
  remain later stage work. No production readiness is claimed.

Local command logs are ignored under `.cache/stage01-*.log`; commands and sanitized
summaries are retained here rather than private runtime logs.

The initial RabbitMQ image fetch hit a Docker Hub TLS handshake timeout.
Testcontainers retried and completed successfully; no integration test was skipped
or disabled to bypass the download. The five integration methods exercised queue
declaration, confirmed routing/dead-letter delivery, V1 catalog reads, protected
route denial and database/broker readiness.

The first Compose image build stalled on one Maven base-image layer. Only this
task's build process tree was canceled; no Docker data or volumes were removed.
The Maven image completed through a targeted pull, and the Compose build resumed
using the retained cache. This was an environment recovery, not a skipped check.
