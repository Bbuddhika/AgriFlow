# analytics-ai-service

Independent Spring Boot service scaffold. Health is public; business routes are denied.
No account, notification, chat or provider workflow is implemented yet.
Build from `backend/` with `mvn -pl analytics-ai-service -am package`.
Docker build context is `backend/`, Dockerfile `analytics-ai-service/Dockerfile`.
See [service boundaries](../../docs/architecture/003-separate-backend-services.md).
