# DevOrbit Jenkins CI/CD Automation

This directory contains the Jenkins Pipeline definition (`Jenkinsfile`) implementing the automated continuous integration and continuous deployment lifecycle.

## Pipeline Lifecycle Stages

```text
[1. Checkout] ──> [2. Build] ──> [3. Test] ──> [4. Package] ──> [5. Docker Build] ──> [6. Docker Push] ──> [7. Deploy] ──> [8. Verify]
```

1. **Checkout**: Pulls the triggered commit or feature branch from GitHub.
2. **Build**: Compiles Java source code using Maven.
3. **Test**: Executes automated JUnit 5 test suite. If any test fails, the pipeline aborts immediately.
4. **Package**: Builds the production JAR artifact (`target/devorbit.jar`).
5. **Docker Build**: Packages the JAR into a versioned container image tagged with `${BUILD_NUMBER}-${GIT_COMMIT}`.
6. **Docker Push**: Securely logs into Docker Hub / Registry using Jenkins credentials and pushes the image.
7. **Deploy**: Applies Kubernetes manifests to the `devorbit` namespace and updates the container image.
8. **Verify**: Monitors the rolling update rollout and queries `/health` to confirm cluster readiness.

## Required Jenkins Credentials Setup

1. **`docker-hub-credentials`**:
   - Type: **Username with password**
   - Username: Your Docker Hub username
   - Password: Docker Hub Personal Access Token (PAT)
2. **`k8s-kubeconfig`**:
   - Type: **Secret file**
   - File: Upload the `~/.kube/config` file generated during k3s installation on your server.
