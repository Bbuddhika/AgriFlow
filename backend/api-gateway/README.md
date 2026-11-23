# api-gateway

Independent Spring Boot service scaffold. Health is public; business routes are denied.
No account, notification, chat or provider workflow is implemented yet.
Build from `backend/` with `mvn -pl api-gateway -am package`.
Docker build context is `backend/`, Dockerfile `api-gateway/Dockerfile`.
See [service boundaries](../../docs/architecture/003-separate-backend-services.md).
