# Jenkins CI/CD Automation Guide

## Pipeline Architecture
Jenkins serves as the central automation engine executing the 8 continuous delivery stages defined in `jenkins/Jenkinsfile`.

```text
[Checkout] ──> [Build] ──> [Test] ──> [Package] ──> [Docker Build] ──> [Docker Push] ──> [Deploy] ──> [Verify]
```

## Failure Gate Discipline
If `mvn test` encounters any test failure, the Jenkins pipeline triggers a non-zero exit code, aborting the build immediately before any Docker image is published or deployed.

## Secret Management
Credentials (`docker-hub-credentials`, `k8s-kubeconfig`) are managed securely inside Jenkins' encrypted credential store and injected as scoped environment variables only inside authenticated pipeline steps.
