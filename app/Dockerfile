# ==============================================================================
# DevOrbit - Production Multi-Stage Dockerfile
# Stage 1: Build JAR with Maven & Eclipse Temurin JDK 21
# Stage 2: Minimal Distroless / JRE 21 Runtime as Non-Root User
# ==============================================================================

# Stage 1: Builder
FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder
WORKDIR /build

# Cache dependencies first
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code and package
COPY src ./src
RUN mvn clean package -DskipTests -B

# Stage 2: Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Create unprivileged application user
RUN addgroup -g 1001 -S devorbit && \
    adduser -u 1001 -S devorbit -G devorbit

# Copy the generated JAR from builder stage
COPY --from=builder --chown=devorbit:devorbit /build/target/devorbit.jar /app/devorbit.jar

# Install curl for container health check
RUN apk add --no-cache curl

# Configure unprivileged user
USER devorbit

# Expose standard application port
EXPOSE 8080

# Environment defaults
ENV SERVER_PORT=8080 \
    APP_ENVIRONMENT=production \
    JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/devorbit.jar"]
