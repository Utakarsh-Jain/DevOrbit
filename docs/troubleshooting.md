# DevOrbit Troubleshooting Guide

## Common Issues and Diagnostic Steps

### 1. Pods in `CrashLoopBackOff` or `Pending`
```bash
# Check pod status and events
kubectl describe pod <pod-name> -n devorbit

# Inspect container startup logs
kubectl logs <pod-name> -n devorbit
```
*Likely cause*: Insufficient memory limit or misconfigured `/health` initial delay.

### 2. Jenkins Pipeline Fails at Test Stage
```bash
# Run tests locally to reproduce exact error
cd app
mvn test
```
*Likely cause*: Assertion failure in unit tests or malformed JSON DTO payload.

### 3. Docker Push Fails (401 / 403 Unauthorized)
*Fix*: Verify `docker-hub-credentials` in Jenkins Credentials manager and verify Personal Access Token permissions.

### 4. Terraform Apply Fails (Authorization / Network Error)
*Fix*: Check that AWS IAM credentials have EC2 and VPC management permissions, and verify that the default AWS region is active.
