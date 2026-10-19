# Docker Containerization Guide

## Image vs container

- **Image**: immutable template with the application, runtime and dependencies.
- **Container**: an isolated running instance of that image.

## DevOrbit image

`app/Dockerfile` is a 3-stage build:

1. `node:20-alpine` builds the React UI.
2. `maven:3.9.9-eclipse-temurin-21-alpine` compiles and packages the JAR with
   the UI copied to `src/main/resources/static/ui`.
3. `eclipse-temurin:21-jre-alpine` runs the JAR as the non-root user `devorbit`
   (uid 1001), exposing port 8080 with a `/health` healthcheck.

## Where Docker runs

Docker runs on the AWS hosts, not on a laptop:

- **Jenkins host (VPC-C)**: builds and pushes the image to Amazon ECR.
- **k3s host (VPC-B)**: k3s pulls the image from ECR and runs it.

## Build and push (executed by Jenkins)

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.ap-south-1.amazonaws.com"

aws ecr get-login-password --region ap-south-1 \
  | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

docker build -t devorbit-app:1.0.0 .
docker tag devorbit-app:1.0.0 "${ECR_REGISTRY}/devorbit-app:1.0.0"
docker push "${ECR_REGISTRY}/devorbit-app:1.0.0"
```

## Run on the k3s host for a manual check

```bash
docker run --rm -p 8080:8080 \
  -e APP_ENVIRONMENT=aws \
  <ECR_REGISTRY>/devorbit-app:1.0.0
curl -s http://localhost:8080/health
```

Use this only as a manual sanity check on the AWS host; the normal path is the
Kubernetes Deployment.

## Security notes

- The container runs as uid 1001, never root.
- `.dockerignore` excludes `.git`, `.env`, `target`, `node_modules` and `dist`.
- Images are tagged with the Jenkins build number and Git SHA, never only
  `latest`.
