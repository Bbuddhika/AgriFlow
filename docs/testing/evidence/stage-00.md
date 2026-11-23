# Stage 00 evidence — baseline and service restructuring

Date: 21 November 2026, Asia/Colombo. Operator: Codex in the local workspace.
Source snapshot: uncommitted working tree; local `main` has no commits or remote.
No deployed image digests, runtime fixture or business completion is claimed.

Environment used: Windows/PowerShell, Maven 3.9.11, installed JDK 25.0.5 with
compiler release 21, Spring Boot 3.5.16 from the existing dependency baseline.
Frontend toolchain was not exercised in this stage. No provider credentials
were used. Compose checks used process-local placeholders rather than writing `.env`.

## Scope

- Recovered the prior separate-service instruction and inspected SwiftDrop's
  Maven aggregator/service directories as a structural reference.
- Preserved catalog source, V1 migration and five integration test methods in
  market core; added independent service builds and owned database configuration.
- Recorded decisions, critical state transitions and a story for each of the
  41 traced requirements, with expected behavior, service owner and proposed tests.
- Excluded browser and Chrome profiles, secrets, caches and generated build files.

## Acceptance checks

| Check | Observed result |
|---|---|
| Static baseline checker | PASS — five services plus common contracts; five preserved integration methods; all 41 requirements mapped; planning links and private/generated exclusions |
| Compose interpolation/configuration | PASS — eleven containers; exclusive database networks; correct build contexts/Dockerfiles; loopback ports; no public SQL/AMQP |
| Maven reactor packaging | PASS — parent, common-contracts and all five services; tests skipped; finished 12:23:38 +05:30 |
| Gateway routing/security tests | PASS — four tests, zero failures/errors/skips; finished 12:25:12 +05:30 |
| Docker engine availability | Engine pipe `dockerDesktopLinuxEngine` absent; `docker info` failed |
| Runtime Compose, preserved integration tests and smoke journey | NOT RUN; require Docker Desktop Linux engine |
| Git | Existing local `main`, no commits/remote; scoped safe.directory used due differing owner |

## Reproduction

```powershell
python scripts/development/check_baseline.py --compose
mvn -B -f backend/pom.xml -DskipTests package
mvn -B -f backend/pom.xml -pl api-gateway -am test
```

The `--compose` option checks Docker CLI configuration without contacting the
engine. It supplies process-local placeholder passwords and checks the resolved
configuration without printing secrets. Standalone `docker compose config --quiet`
also completed without validation errors with process-local placeholders.

Observed summaries:

```text
PASS: 5 services + common contracts; 5 preserved integration methods; 41 requirements mapped to stories, services and proposed tests; planning links; private/generated exclusions
PASS: Compose configuration; 11 containers; owned database networks; service Dockerfiles; loopback host ports
Maven reactor: parent and all six children SUCCESS
Gateway tests run: 4, Failures: 0, Errors: 0, Skipped: 0
```

Gateway tests exercised HTTP calls to a synthetic local upstream: catalog/system
forwarding, safe 503 for upstream errors and redirects, and protected GET/POST
denial before upstream access. Public responses did not forward upstream cookies
or redirect headers. The preserved market test methods were not executed.

The initial exclusion checker failed with Windows line-oriented subprocess
input. It was corrected to NUL-delimited Git input/output; all six paths passed
on rerun. No ignore rule was weakened to make the check pass.

The Windows sandbox could not start the shell (`setup refresh had errors`).
Commands ran through explicit approved escalation. Git commands use a
command-scoped safe.directory exception; no global trust or ownership change.

## Remaining work

Stage 00 planning exit conditions are satisfied. See the decision register for external inputs; their dependent releases remain
gated. An initial commit/remote is still pending. Stage 01 must establish real
frontend builds, locked installation, all-container health and catalog/outage
integration evidence. No identity, notification delivery, chat, reservation,
inspection or finance behavior is implemented by this restructuring.
