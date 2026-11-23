# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY . .
RUN --mount=type=cache,target=/root/.m2 mvn -B -pl market-core-service -am -DskipTests package
FROM eclipse-temurin:21-jre-alpine AS runtime
LABEL org.opencontainers.image.title="Dambulla AgriFlow market-core-service"
RUN addgroup -S agriflow && adduser -S agriflow -G agriflow
WORKDIR /app
COPY --from=build --chown=agriflow:agriflow /workspace/market-core-service/target/market-core-service-0.1.0-SNAPSHOT.jar app.jar
USER agriflow
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
