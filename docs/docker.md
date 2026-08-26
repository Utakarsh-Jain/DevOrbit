# Docker Containerization Guide

## Image vs Container
- **Image**: An immutable template containing the application code, runtime libraries, and environment dependencies.
- **Container**: An isolated, lightweight running process instance of an image.

## Commands
```bash
# Build multi-stage image
docker build -t devorbit-app:1.0.0 app/

# Run container locally
docker run -d -p 8080:8080 --name devorbit devorbit-app:1.0.0

# Inspect logs
docker logs -f devorbit

# Verify health endpoint
curl -s http://localhost:8080/health

# Stop and clean container
docker stop devorbit && docker rm devorbit
```
