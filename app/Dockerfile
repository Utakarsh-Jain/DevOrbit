# ==============================================================================
# DevOrbit - Production Multi-Stage Dockerfile
# Stage 1: Build the React/Vite frontend with Node 20
# Stage 2: Build the Spring Boot JAR with Maven and Temurin JDK 21
# Stage 3: Minimal JRE 21 runtime running as a non-root user
# ==============================================================================

# Stage 1: Frontend builder
FROM node:20-alpine AS frontend
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend builder
FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build

# Cache dependencies first
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy backend source and the built frontend assets
COPY src ./src
COPY --from=frontend /frontend/dist ./src/main/resources/static/ui

# Package the executable JAR
RUN mvn clean package -DskipTests -B

# Stage 3: Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Install curl for the container health check before dropping privileges
RUN apk add --no-cache curl

# Create unprivileged application user
RUN addgroup -g 1001 -S devorbit && \
    adduser -u 1001 -S devorbit -G devorbit

# Copy the generated JAR from the builder stage
COPY --from=builder --chown=devorbit:devorbit /build/target/devorbit.jar /app/devorbit.jar

# Configure unprivileged user
USER devorbit

# Expose standard application port
EXPOSE 8080

# Environment defaults
ENV SERVER_PORT=8080 \
    APP_ENVIRONMENT=production \
    JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/devorbit.jar"]
