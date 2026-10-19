

## Slide 1: Title Slide

- **Project Title:** **DEVORBIT**
- **Primary Goal:** Transform fragile manual application delivery into an automated, repeatable, version-controlled, and observable lifecycle.

---

## Slide 2: Abstract (Executive Summary)

- **Problem:** Traditional software deployments rely on manual server setups, untracked configurations, environment discrepancies (*"it works on my machine"*), lack of automated quality gates, and downtime during updates.
- **Our Solution:** **DevOrbit** establishes a unified, cloud-native DevOps pipeline wrapping a Spring Boot application.
- **Core Pillars:**
  - **Infrastructure as Code (IaC):** AWS infrastructure provisioned declaratively via **Terraform**.
  - **Configuration Automation:** Server environment, Docker, and k3s Kubernetes configured idempotently using **Ansible**.
  - **Containerization & Orchestration:** Lightweight, unprivileged container packaging via **Docker** and zero-downtime rolling updates via **Kubernetes (k3s)**.
  - **Automated CI/CD:** 8-stage automated build, test, and release cycle managed by **Jenkins**.
  - **Cloud Observability:** Real-time metrics and threshold alerts via **AWS CloudWatch**.

---

## Slide 3: End-to-End DevOps Workflow Architecture

```text
+------------------------------------------------------------------------------------+
|                                 DEVELOPER WORKFLOW                                 |
|                                                                                    |
|   [Developer]  ───> (Git Feature Branch) ───> [GitHub PR / Main]                   |
|                                                      │                             |
|                                              (Webhook Trigger)                     |
|                                                      ▼                             |
|   +--------------------------------------- [Jenkins] --------------------------+  |
|   |  1. Checkout   2. Maven Build & Tests   3. Package JAR   4. Build Docker   |  |
|   +----------------------------------------------------------------------------+  |
|                                                      │                             |
|                                                      ▼                             |
|                                              [Amazon ECR Registry]                  |
|                                                      │                             |
+------------------------------------------------------|-----------------------------+
                                                       ▼
+---------------------------------------- [AWS CLOUD] -------------------------------+
|                                                                                    |
|   [Terraform] ═════ provisions ════>  [3 VPCs + Peering / 3 EC2 / IAM / SGs]        |
|                                                      │                             |
|   [Ansible]   ═════ configures ═════>  [Docker + Java + k3s Kubernetes]            |
|                                                      │                             |
|   [Jenkins CD] ═════ deploys ═══════>  [Kubernetes (k3s)]                          |
|                                            ├── Namespace: devorbit                 |
|                                            ├── Service: NodePort (30080)           |
|                                            └── Deployment (2 Replicas, Probes)     |
|                                                      │                             |
|                                                      ▼                             |
|                                           [DevOrbit Spring Boot App]               |
|                                                      │                             |
|                                           (Metrics & Logs)                         |
|                                                      ▼                             |
|                                              [AWS CloudWatch]                      |
+------------------------------------------------------------------------------------+
```

---

## Slide 4: DevOps Toolchain Matrix & Roles

| DevOps Layer | Technology Used | Role & Responsibility in DevOrbit |
| :--- | :--- | :--- |
| **Application Layer** | **Java 21 / Spring Boot 3** | Lightweight REST API for Campus Issue Management with Actuator. |
| **Version Control** | **Git & GitHub** | Branching strategy, collaborative code reviews, and webhook triggers. |
| **Build & Test** | **Apache Maven & JUnit 5** | Automated dependency management, testing gate, and JAR compilation. |
| **Containerization** | **Docker** | Multi-stage, unprivileged non-root container packaging (`devorbit-app`). |
| **Orchestration** | **Kubernetes (k3s)** | Zero-downtime rolling updates, automated pod self-healing, and scaling. |
| **Infra as Code (IaC)** | **Terraform** | Declarative provisioning of 3 peered VPCs, subnets, security groups, IAM, ECR, and EC2. |
| **Config Management** | **Ansible** | Automated configuration of packages, Docker runtime, and k3s cluster. |
| **CI/CD Pipeline** | **Jenkins** | 8-stage continuous integration and continuous deployment engine. |
| **Observability** | **AWS CloudWatch** | Real-time EC2 CPU metrics, threshold monitoring, and automated alerts. |

---

## Slide 5: Continuous Delivery Pipeline (The 8 Stages)

1. **Stage 1: Checkout** — Clones source code dynamically from GitHub repository upon push/merge.
2. **Stage 2: Build** — Maven clean compile checks for syntactic correctness and resolves dependencies.
3. **Stage 3: Automated Test Gate** — Executes unit and integration test suite (`mvn test`); halts pipeline if any test fails.
4. **Stage 4: Package** — Builds the optimized standalone executable JAR (`target/devorbit.jar`).
5. **Stage 5: Container Build** — Builds a hardened Docker image tagged with dynamic `${BUILD_NUMBER}-${GIT_COMMIT}`.
6. **Stage 6: Registry Push** — Authenticates to Amazon ECR through the Jenkins EC2 IAM role and pushes the versioned image.
7. **Stage 7: Cluster Deploy** — Applies declarative Kubernetes manifests (`k8s/`) with rolling update strategy.
8. **Stage 8: Verification** — Verifies rolling update rollout status and queries `/health` probe.

## Slide 6: Conclusion & Summary

- **Core Philosophy:** DevOrbit transforms software delivery from a fragile sequence of manual steps into a **repeatable, version-controlled, and automated cloud-native lifecycle**.
- **Key Takeaway:** *"It is not just an application hosted on AWS; it is the entire automated delivery machine revolving around modern DevOps practices."*
