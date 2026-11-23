# Market core service

Preserves the existing catalog, V1 migration, security configuration and five
integration test methods. Owns catalog, produce, trading, visits, inspection,
finance, prices, reporting and transactional audit/outbox. Only the foundation
catalog is implemented. No other service may query or mutate its database.

Build context: `backend/`; Dockerfile: `market-core-service/Dockerfile`.
