# syntax=docker/dockerfile:1
FROM node:22-alpine AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM dependencies AS build
ENV NEXT_TELEMETRY_DISABLED=1
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
LABEL org.opencontainers.image.title="Dambulla AgriFlow Frontend"
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
RUN addgroup -S agriflow && adduser -S agriflow -G agriflow
COPY --from=build --chown=agriflow:agriflow /app/.next/standalone ./
COPY --from=build --chown=agriflow:agriflow /app/.next/static ./.next/static
COPY --from=build --chown=agriflow:agriflow /app/public ./public
USER agriflow
EXPOSE 3000
CMD ["node", "server.js"]
