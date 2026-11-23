# ADR 002: RabbitMQ alongside one modular backend

> Historical architecture. [ADR 003](003-separate-backend-services.md) supersedes
> the single-backend deployment/database assumption. Retained rules apply within
> market core; current runtime verification belongs to Stage 01.

Status: selected by the user and configured; runtime verification blocked.

The user explicitly selected: "Keep one modular backend and add RabbitMQ".
This amends the earlier design baseline that deferred a message broker. Keep
one Spring Boot application, one PostgreSQL database, and package-level business
boundaries. A module is not a separate deployable service or database. Do not
create one backend service for every database table.

## Deployment and ownership

| Component | Dockerfile | Responsibility |
|---|---|---|
| Backend | `backend/Dockerfile` | Business modules, APIs, database access and AMQP connection |
| Frontend | `frontend/Dockerfile` | Server-rendered UI |
| PostgreSQL | `infrastructure/postgres/Dockerfile` | Authoritative transactional records and Flyway history |
| RabbitMQ | `infrastructure/rabbitmq/Dockerfile` | Durable event routing for asynchronous work |

Compose assigns all four images a `dambulla-agriflow-` prefix and shared
`IMAGE_TAG`. PostgreSQL and RabbitMQ have separate persistent volumes. The
backend waits for both dependencies. RabbitMQ's management UI is published only
on localhost; AMQP is available to the backend through the messaging network.
Backend readiness includes PostgreSQL and RabbitMQ. Liveness remains independent
of those external dependencies.

## Configured messaging foundation

- Durable topic exchange: `agriflow.events`.
- Durable notification queue: `agriflow.notifications.v1`.
- Routing keys: `reservation.accepted.v1`, `reservation.expired.v1`,
  `visit.status-changed.v1`, `inspection.completed.v1`, `sale.confirmed.v1`.
- Durable dead-letter exchange: `agriflow.dead-letters`.
- Durable dead-letter queue: `agriflow.notifications.dlq.v1`.
- Correlated publisher confirms, returned unroutable messages, mandatory
  publishing and a bounded retry configuration for future listeners.

Spring AMQP declares this topology when the backend first establishes a broker
connection. Listener retry configuration applies when listeners are implemented;
there is currently no business-event publisher or notification consumer.

The integration test uses disposable PostgreSQL and RabbitMQ containers. It
checks queue declarations, confirmed routing, explicit rejection to the
dead-letter queue, catalog migration, protected routes and readiness. Synthetic
broker test messages do not create real reservations.

## Rules for implementing business events

Write an outbox record in the same PostgreSQL transaction as the domain change.
A retrying dispatcher must publish persistent messages and check both broker
confirms and returned-message outcomes before marking the outbox record sent.
Keep the original event ID during retries. Consumers must validate event schemas
and deduplicate by event ID and recipient in their own persistence transaction.
This handles redelivery without assuming exactly-once transport.

Use versioned, bounded JSON envelopes and minimal recipient data. Do not send
passwords, chat histories or unnecessary personal details. Configure a monitored
dead-letter retention and replay policy before real use; durable queues can grow
without bound if there are no consumers. Keep stock, consent, sale confirmation
and payment invariants in the database transaction, with notifications following
committed outcomes. The outbox, dispatcher, inbox deduplication, notification
consumer and operational replay tooling are not implemented in this foundation.

Official implementation references:

- [Spring Boot AMQP configuration](https://docs.spring.io/spring-boot/reference/messaging/amqp.html)
- [Publisher confirms and returns](https://docs.spring.io/spring-amqp/reference/3.2/amqp/connections.html)
- [RabbitMQ monitoring and health checks](https://www.rabbitmq.com/docs/monitoring)
