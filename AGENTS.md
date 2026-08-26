# DevOrbit - AI Coding Agent Development Specification

> **This file is the source of truth for an AI coding agent working on the DevOrbit project.**
>
> The agent must use this document as the project's development contract. Do not treat DevOrbit as a generic CRUD application. The main objective is to build a small application whose entire software delivery lifecycle demonstrates Cloud + DevOps concepts.

---

## 1. Project Identity

**Project name:** DevOrbit

**Tagline:** The entire DevOps lifecycle revolving around one platform.

**Project type:** Cloud-Native DevOps / Cloud Computing academic project

**Team size:** 3

**Development duration:** Approximately 1 month

**Primary goal:**

Build a small, reliable application and surround it with an automated DevOps lifecycle:

```text
Developer
    ↓
GitHub
    ↓
Jenkins
    ↓
Maven Build
    ↓
Automated Tests
    ↓
Docker Image
    ↓
Container Registry
    ↓
Kubernetes
    ↓
AWS
    ↓
CloudWatch
```

Infrastructure lifecycle:

```text
Terraform
    ↓
AWS Infrastructure
    ↓
Ansible
    ↓
Configured Linux Environment
```

The final project must demonstrate that application delivery can be:

- Repeatable
- Automated
- Version controlled
- Containerized
- Orchestrated
- Observable
- Reproducible

---

# 2. CRITICAL AGENT INSTRUCTIONS

The AI coding agent MUST follow these rules.

## 2.1 Do not over-engineer

This is a one-month academic project.

Do NOT introduce:

- unnecessary microservices
- complex event-driven architecture
- dozens of AWS services
- service meshes
- advanced distributed systems
- unnecessary databases
- unnecessary authentication systems
- unnecessary frontend complexity

A simple working system is preferred over a complex incomplete system.

---

## 2.2 DevOps is the primary project

The application is intentionally small.

Do not spend most of the development effort making the UI impressive.

The project should prioritize:

1. Application reliability
2. Dockerization
3. Kubernetes deployment
4. Terraform
5. Ansible
6. Jenkins CI/CD
7. Monitoring
8. Documentation
9. Reproducibility

---

## 2.3 Never fake infrastructure

The agent must never pretend that:

- AWS infrastructure exists when it does not
- Kubernetes is running when it is not
- Jenkins executed a pipeline when it did not
- Docker images were pushed when they were not
- CloudWatch metrics exist when they were not configured

If infrastructure cannot be executed in the current environment, create the configuration and clearly document the required execution step.

---

## 2.4 Never expose secrets

NEVER commit or generate real:

- AWS access keys
- AWS secret keys
- SSH private keys
- passwords
- API tokens
- registry passwords
- Jenkins secrets
- Kubernetes credentials
- private certificates

Use:

- environment variables
- `.env.example`
- Jenkins Credentials
- Kubernetes Secrets
- AWS IAM roles
- secret managers where appropriate

---

## 2.5 Prefer official tooling and documentation

When implementing infrastructure, use current official documentation for:

- AWS
- Terraform
- Ansible
- Docker
- Kubernetes
- Jenkins
- Maven
- Spring Boot

Do not blindly rely on outdated tutorials.

---

# 3. Application Definition

## 3.1 Application name

The demo application is:

**DevOrbit Campus Issue Management**

It exists primarily to provide a realistic workload for the DevOps pipeline.

---

## 3.2 Application purpose

Students can report campus-related issues.

Examples:

- Projector not working
- Lab computer issue
- Classroom equipment issue
- Wi-Fi issue
- Facility issue

The application should support a minimal issue lifecycle.

```text
OPEN
  ↓
IN_PROGRESS
  ↓
RESOLVED
```

---

# 4. Recommended Technology Stack

## Backend

Use:

- Java
- Spring Boot
- Spring Web
- Spring Boot Actuator
- Maven

Recommended Java version:

- Java 21, unless compatibility constraints require another supported LTS version.

---

## Frontend

A frontend is optional in the first implementation.

Preferred approach:

- Build a REST API first.
- Add a minimal frontend only after the backend and DevOps pipeline are stable.

If a frontend is added:

- React
- Vite
- Simple clean interface

Do not let frontend work delay the DevOps pipeline.

---

## Infrastructure

- AWS
- EC2
- Linux
- IAM
- Security Groups
- S3 where useful
- CloudWatch

---

## Infrastructure as Code

- Terraform

---

## Configuration Management

- Ansible

---

## Containers

- Docker

---

## Container Orchestration

- Kubernetes

For a resource-constrained academic environment, a lightweight Kubernetes distribution such as k3s may be considered.

The agent must not assume that a full production Kubernetes cluster is available.

---

## CI/CD

- GitHub
- Jenkins
- Maven
- Docker
- Kubernetes

---

## Artifact Management

Optional:

- JFrog Artifactory

Container registry:

- Use a suitable accessible registry.

---

# 5. Application Requirements

## 5.1 Health endpoint

Implement:

```text
GET /health
```

Expected response:

```json
{
  "status": "UP"
}
```

This endpoint must remain lightweight and reliable.

Kubernetes readiness/liveness checks may use this endpoint.

---

## 5.2 Root endpoint

Implement:

```text
GET /
```

Example response:

```json
{
  "application": "DevOrbit Campus Issue Management",
  "version": "1.0.0",
  "status": "running"
}
```

The version must be easy to change because it will be used during the CI/CD demonstration.

---

## 5.3 Issues API

Implement:

```text
GET /api/issues
POST /api/issues
GET /api/issues/{id}
PATCH /api/issues/{id}
```

Minimal issue model:

```text
id
title
description
status
createdAt
updatedAt
```

---

# 6. Data Storage Strategy

## Initial implementation

Use in-memory storage if it keeps development simple.

The project does NOT require a sophisticated database unless explicitly added later.

Possible implementation:

```text
ConcurrentHashMap
```

or a simple service/repository abstraction.

---

## Optional database

Only add PostgreSQL if:

- core application is already working
- Docker Compose/local development is stable
- Kubernetes persistence is understood
- the team has enough time

Do not make database infrastructure a blocker for the DevOps project.

---

# 7. Backend Architecture

Use a clean but small layered architecture:

```text
Controller
    ↓
Service
    ↓
Repository / In-memory storage
    ↓
Model
```

Suggested package structure:

```text
com.devorbit
│
├── controller
├── service
├── repository
├── model
├── dto
├── exception
└── config
```

Avoid unnecessary design patterns.

---

# 8. API Design Rules

The API must:

- validate inputs
- return meaningful HTTP status codes
- return consistent JSON
- provide useful error messages
- avoid exposing internal stack traces
- remain simple enough to understand in a viva

Examples:

```text
200 OK
201 CREATED
400 BAD REQUEST
404 NOT FOUND
500 INTERNAL SERVER ERROR
```

---

# 9. Testing Requirements

The project must include automated tests.

Minimum:

- health endpoint test
- root endpoint test
- issue creation test
- issue retrieval test
- issue-not-found test
- validation/error test

The command:

```bash
mvn test
```

must be the authoritative local test command.

A failing test must cause CI to fail.

---

# 10. Maven Requirements

The project must use Maven.

The root backend build file:

```text
pom.xml
```

Expected commands:

```bash
mvn clean
mvn test
mvn package
```

The agent must ensure:

```bash
mvn clean test
```

works before modifying CI.

---

# 11. Docker Requirements

Create:

```text
app/Dockerfile
```

The Docker image should:

- use a supported Java runtime
- run as a non-root user where practical
- expose the application port
- contain only required runtime files
- avoid embedding secrets
- use deterministic/versioned image tags

Preferred conceptual flow:

```text
Maven
  ↓
JAR
  ↓
Docker build
  ↓
Docker image
```

---

# 12. Docker Security Rules

Avoid:

```dockerfile
USER root
```

for the running application unless technically required.

Do not:

```text
COPY .env .
COPY credentials .
COPY private keys .
```

Use `.dockerignore`.

Recommended exclusions:

```text
.git
.idea
.env
target
*.log
docs
```

The exact exclusions may be adjusted.

---

# 13. Docker Local Development

The agent should make it possible to run:

```bash
mvn clean package
docker build -t devorbit-app:local .
docker run -p 8080:8080 devorbit-app:local
```

Then:

```text
http://localhost:8080/
http://localhost:8080/health
```

must work.

---

# 14. Kubernetes Requirements

Create:

```text
k8s/
├── namespace.yaml
├── deployment.yaml
├── service.yaml
├── configmap.yaml
└── ingress.yaml
```

`ingress.yaml` is optional depending on the cluster setup.

---

## 14.1 Namespace

Use:

```text
devorbit
```

---

## 14.2 Deployment

The Deployment should specify:

- application name
- container image
- container port
- replicas
- resource requests/limits where practical
- readiness probe
- liveness probe
- environment configuration

Start with:

```text
replicas: 2
```

only if the available infrastructure supports it.

---

## 14.3 Service

Use a Kubernetes Service to provide stable access to the application.

Do not rely on direct Pod IP addresses.

---

## 14.4 Health checks

Use:

```text
/health
```

for appropriate readiness/liveness configuration.

Avoid extremely aggressive probe timings.

---

# 15. Kubernetes Resource Discipline

For an academic cluster, define reasonable resource requests and limits.

Example conceptual requirement:

```text
CPU request
Memory request
CPU limit
Memory limit
```

The exact values must be chosen according to the available EC2/k3s environment.

Do not blindly copy production-sized resources.

---

# 16. Kubernetes Deployment Commands

The repository should document:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verification:

```bash
kubectl get pods -n devorbit
kubectl get deployment -n devorbit
kubectl get service -n devorbit
```

---

# 17. Kubernetes Demonstration Requirements

The final system must demonstrate:

## Scaling

```text
2 replicas
    ↓
3 replicas
```

---

## Self-healing

Delete a Pod:

```bash
kubectl delete pod <pod-name> -n devorbit
```

Kubernetes should recreate it.

---

## Rolling deployment

A new image version should be deployable without manually starting containers.

---

# 18. Terraform Requirements

Terraform code must be placed under:

```text
terraform/
```

Recommended structure:

```text
terraform/
├── versions.tf
├── providers.tf
├── variables.tf
├── main.tf
├── outputs.tf
├── terraform.tfvars.example
└── README.md
```

---

## 18.1 Terraform responsibilities

Terraform should manage appropriate infrastructure such as:

- VPC/networking
- subnets
- security groups
- EC2 instances
- relevant IAM configuration
- tags

The exact infrastructure should remain small.

---

# 19. Terraform Rules

The agent must support:

```bash
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy
```

Terraform should be idempotent.

Running:

```bash
terraform apply
```

twice should not continuously create duplicate resources.

---

# 20. Terraform Variables

Use variables for:

```text
AWS region
project name
environment
instance type
allowed CIDR where required
```

Example:

```text
terraform.tfvars.example
```

must contain placeholders only.

Never commit:

```text
terraform.tfvars
```

if it contains sensitive values.

---

# 21. Terraform Outputs

Expose useful outputs such as:

```text
instance IDs
public/private IPs where appropriate
resource names
```

Do not output secrets.

---

# 22. Ansible Requirements

Create:

```text
ansible/
├── inventory/
├── playbooks/
└── roles/
```

Use Ansible to configure Linux machines after Terraform creates them.

Possible tasks:

```text
Install Docker
Install Java
Install utilities
Configure services
Start services
```

---

# 23. Ansible Rules

Ansible playbooks should be:

- idempotent
- readable
- documented
- separated into logical roles where useful

Avoid giant shell scripts.

Prefer Ansible modules over:

```yaml
shell:
```

when a proper module exists.

Use shell/command only when appropriate.

---

# 24. Jenkins Requirements

Jenkins is the CI/CD engine.

Repository location:

```text
jenkins/Jenkinsfile
```

The Jenkins pipeline must eventually implement:

```text
Checkout
    ↓
Build
    ↓
Test
    ↓
Package
    ↓
Docker Build
    ↓
Docker Push
    ↓
Kubernetes Deploy
```

---

# 25. Jenkins Pipeline Stages

Required stages:

```text
Checkout
Build
Test
Package
Docker Build
Docker Push
Deploy
Verify
```

Possible final pipeline:

```text
stage('Checkout')
stage('Build')
stage('Test')
stage('Package')
stage('Docker Build')
stage('Docker Push')
stage('Deploy')
stage('Verify')
```

---

# 26. Jenkins Failure Behavior

If:

```text
mvn test
```

fails:

```text
Pipeline MUST stop.
```

Docker image should not be promoted as a valid release.

Deployment should not happen after a failed test stage.

---

# 27. Jenkins Credentials

Use Jenkins Credentials for:

- container registry
- deployment credentials
- SSH credentials where necessary

Do not put secrets directly in:

```text
Jenkinsfile
GitHub
Dockerfile
Kubernetes YAML
Terraform source
```

---

# 28. Image Tagging Strategy

Avoid relying only on:

```text
latest
```

Use:

```text
devorbit-app:<version>
```

or:

```text
devorbit-app:<git-sha>
```

or:

```text
devorbit-app:<jenkins-build-number>
```

The final project should be able to identify which application version is running.

---

# 29. CI/CD Trigger

Preferred:

```text
GitHub
   ↓
Webhook
   ↓
Jenkins
```

If webhook configuration is difficult in the academic environment, a controlled polling/manual trigger can be used temporarily.

The final documentation must state which trigger is implemented.

---

# 30. CloudWatch Requirements

Use CloudWatch for monitoring AWS resources.

At minimum:

- EC2 CPU metric
- relevant instance monitoring
- one useful dashboard or metric view
- one alarm where practical

The project should explain:

```text
Metric
Log
Alarm
Dashboard
```

---

# 31. Monitoring Philosophy

Do not claim:

> "CloudWatch monitors everything."

Clearly define what is actually monitored.

For example:

```text
EC2 CPU utilization
EC2 status
Application logs where configured
Deployment health through Kubernetes
```

Kubernetes status and CloudWatch monitoring are complementary.

---

# 32. GitHub Repository Rules

The repository should remain clean.

Required:

```text
README.md
.gitignore
LICENSE (optional)
app/
terraform/
ansible/
k8s/
jenkins/
docs/
```

README must contain:

1. Project title
2. Project description
3. Architecture
4. Features
5. Technology stack
6. Local setup
7. Docker setup
8. Kubernetes deployment
9. Terraform instructions
10. Ansible instructions
11. Jenkins pipeline
12. Monitoring
13. Team
14. Known limitations

---

# 33. Git Commit Convention

Use readable commits.

Examples:

```text
feat: add issue creation endpoint
fix: correct issue validation
test: add health endpoint tests
build: add Dockerfile
ci: add Jenkins pipeline
infra: add Terraform EC2 configuration
infra: add Ansible Docker setup
k8s: add application deployment
docs: update deployment instructions
```

Avoid:

```text
final
final2
final-final
changes
stuff
test
asdf
```

---

# 34. Branching Strategy

Recommended:

```text
main
│
├── feature/app
├── feature/docker
├── feature/terraform
├── feature/ansible
├── feature/kubernetes
├── feature/jenkins
└── feature/monitoring
```

Rules:

- no direct development on `main`
- pull requests for major features
- teammate review before merge
- small commits
- resolve conflicts deliberately

---

# 35. Development Order

The agent must implement in this order unless there is a strong reason not to:

```text
Phase 1
Application skeleton

Phase 2
Application API

Phase 3
Tests

Phase 4
Docker

Phase 5
Linux/EC2

Phase 6
Terraform

Phase 7
Ansible

Phase 8
Kubernetes

Phase 9
Jenkins CI

Phase 10
Docker registry integration

Phase 11
Kubernetes CD

Phase 12
CloudWatch

Phase 13
Security hardening

Phase 14
Documentation

Phase 15
Final demo preparation
```

---

# 36. Phase 1 — Repository Bootstrap

Agent tasks:

- create application directory
- initialize Spring Boot project
- create README
- create `.gitignore`
- add Maven configuration
- create basic controller
- create health endpoint
- add tests
- verify local build

Definition of done:

```bash
mvn clean test
```

passes.

---

# 37. Phase 2 — Application

Implement:

```text
GET /
GET /health
GET /api/issues
GET /api/issues/{id}
POST /api/issues
PATCH /api/issues/{id}
```

Add:

- validation
- error handling
- tests

Definition of done:

```text
All API endpoints work locally.
Tests pass.
```

---

# 38. Phase 3 — Docker

Agent tasks:

- create Dockerfile
- create `.dockerignore`
- build image
- run locally
- test health endpoint inside container
- document commands

Definition of done:

```bash
docker build ...
docker run ...
```

works.

---

# 39. Phase 4 — AWS + Linux

Agent should document:

- chosen AWS Region
- EC2 architecture
- networking
- security groups
- SSH method
- Linux distribution
- server responsibilities

Do not hardcode a user's personal IP or credentials into source files.

---

# 40. Phase 5 — Terraform

Implement:

```text
Provider
Networking
Security Group
EC2
Outputs
Variables
```

Definition of done:

```bash
terraform validate
terraform plan
```

works, and approved infrastructure can be created/destroyed predictably.

---

# 41. Phase 6 — Ansible

Implement:

```text
Inventory
Playbook
Roles if needed
```

Automate server setup.

Definition of done:

Running the playbook on a newly created supported machine results in the required software/configuration being present.

---

# 42. Phase 7 — Kubernetes

Implement:

```text
Namespace
Deployment
Service
ConfigMap
Health probes
```

Definition of done:

```bash
kubectl get pods -n devorbit
```

shows healthy application Pods.

---

# 43. Phase 8 — Jenkins CI

First implement only:

```text
GitHub
 ↓
Jenkins
 ↓
Maven Build
 ↓
Tests
```

Definition of done:

- successful commit passes
- intentionally failing test fails the pipeline
- fixed code passes again

---

# 44. Phase 9 — Docker CI

Add:

```text
Docker build
```

Then:

```text
Docker push
```

Definition of done:

A successful Jenkins run produces a uniquely identifiable image in the configured registry.

---

# 45. Phase 10 — Kubernetes CD

Add:

```text
Jenkins
 ↓
kubectl / deployment mechanism
 ↓
Kubernetes
```

Definition of done:

A successful pipeline can deploy a new application image/version.

---

# 46. Phase 11 — Monitoring

Add:

- CloudWatch metrics
- dashboard where practical
- alarm where practical
- application/Kubernetes troubleshooting documentation

Definition of done:

The team can show a real monitoring view during the final presentation.

---

# 47. Phase 12 — Security

Review:

- Git secrets
- Docker image
- Kubernetes permissions
- AWS security groups
- Jenkins credentials
- SSH configuration
- exposed ports
- IAM permissions

The agent must explicitly flag risky configurations rather than silently accepting them.

---

# 48. Phase 13 — Documentation

The agent must update documentation whenever an implementation decision changes.

Do not wait until the final day.

Required documents:

```text
docs/
├── architecture.md
├── aws.md
├── linux.md
├── terraform.md
├── ansible.md
├── docker.md
├── kubernetes.md
├── jenkins.md
├── cicd.md
├── monitoring.md
├── troubleshooting.md
└── demo-script.md
```

---

# 49. Architecture Documentation

`docs/architecture.md` must explain:

```text
Developer
   ↓
GitHub
   ↓
Jenkins
   ↓
Maven
   ↓
Docker
   ↓
Registry
   ↓
Kubernetes
   ↓
AWS
   ↓
CloudWatch
```

And:

```text
Terraform
   ↓
AWS Infrastructure
   ↓
Ansible
   ↓
Configured Linux
```

---

# 50. Environment Strategy

Keep environments simple.

Recommended:

```text
local
dev
```

A production environment is not required.

If a staging environment is added, document exactly why.

Do not create multiple AWS environments unless necessary.

---

# 51. Configuration Strategy

Configuration must not be hardcoded.

Use:

```text
Environment variables
ConfigMap
Kubernetes Secret
Jenkins Credentials
Terraform variables
```

Choose the appropriate mechanism based on whether a value is:

- normal configuration
- sensitive
- infrastructure-specific
- CI-specific

---

# 52. Logging Requirements

Application logs should be useful.

Include:

- startup
- request-related important events
- errors
- important state changes

Do not log:

- passwords
- access tokens
- private keys
- unnecessary personal data

---

# 53. Error Handling

Implement a centralized exception handling mechanism where appropriate.

Return clean JSON errors.

Example:

```json
{
  "error": "Issue not found",
  "status": 404
}
```

Do not return stack traces to users.

---

# 54. API Documentation

Optional but recommended:

- OpenAPI/Swagger

Only add it after the core application is stable.

---

# 55. Frontend Rules

If a frontend is added:

Keep it intentionally small.

Required:

- issue list
- create issue
- update status
- application version/status

Do not spend excessive time on animations or visual polish.

The frontend exists to make the final deployment demo understandable.

---

# 56. Agent Working Style

When asked to implement a feature, the agent should:

1. Inspect the existing repository.
2. Identify affected files.
3. Explain the planned change briefly.
4. Implement the smallest correct solution.
5. Run relevant tests/checks.
6. Report what changed.
7. Report any commands that could not be executed.
8. Update documentation if the behavior or architecture changed.

Do not rewrite unrelated files.

---

# 57. Before Editing

The agent should inspect:

```text
README.md
project structure
pom.xml
existing tests
Dockerfile
Kubernetes manifests
Terraform
Ansible
Jenkinsfile
```

before making architectural changes.

Do not assume the repository is empty.

---

# 58. Definition of Done for Code Changes

A feature is not complete merely because the code compiles.

For a typical change:

```text
[ ] Code implemented
[ ] Tests added/updated
[ ] Existing tests still pass
[ ] API behavior documented if applicable
[ ] Docker impact considered
[ ] Kubernetes impact considered if applicable
[ ] CI impact considered
[ ] Security impact considered
[ ] README/docs updated where needed
```

---

# 59. Testing Before Commit

At minimum:

```bash
mvn clean test
```

If Docker changed:

```bash
docker build ...
```

If Kubernetes manifests changed:

```bash
kubectl apply --dry-run=client -f ...
```

where supported and appropriate.

If Terraform changed:

```bash
terraform fmt -check
terraform validate
```

If Ansible changed:

```bash
ansible-playbook --syntax-check ...
```

Use the correct environment-specific validation.

---

# 60. Never Ignore Errors

Bad agent behavior:

```text
Command failed
→ continue anyway
```

Good behavior:

```text
Command failed
→ inspect error
→ determine cause
→ fix if possible
→ rerun
→ document if unresolved
```

---

# 61. Dependency Management

Keep dependencies minimal.

Before adding a library, ask:

```text
Do we really need it?
Is there already a Spring/JDK feature that solves this?
Does it add security/maintenance complexity?
```

Do not add libraries just because they are popular.

---

# 62. Database Rule

If a database is added later:

- use PostgreSQL
- use Docker locally
- document connection configuration
- never commit credentials
- consider Kubernetes persistence carefully

But the first milestone must work without a database.

---

# 63. Advanced Feature Gate

The agent MUST NOT implement advanced features until this checklist is complete:

```text
[ ] App works
[ ] Tests work
[ ] Docker works
[ ] Kubernetes works
[ ] Terraform works
[ ] Ansible works
[ ] Jenkins CI works
[ ] Docker image push works
[ ] Kubernetes CD works
[ ] Monitoring works
[ ] Demo works
```

Only then consider:

```text
Artifactory
SonarQube
Trivy
Autoscaling
Blue/green
Canary
EKS
Argo CD
```

---

# 64. Final Demo Requirements

The final system must support this story:

```text
1. Developer changes application version.
2. Change is committed to Git.
3. GitHub receives it.
4. Jenkins starts.
5. Maven builds.
6. Tests pass.
7. Docker image is built.
8. Image is pushed.
9. Kubernetes deploys the new version.
10. Application becomes healthy.
11. Browser/API shows new version.
12. Kubernetes scales.
13. Pod is deleted.
14. Kubernetes recreates it.
15. CloudWatch shows monitoring information.
```

The agent should preserve this path throughout development.

---

# 65. Final Repository Checklist

```text
devorbit/
│
├── app/
│   ├── src/
│   ├── pom.xml
│   ├── Dockerfile
│   └── .dockerignore
│
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── ingress.yaml
│
├── terraform/
│   ├── versions.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
│
├── ansible/
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
│
├── jenkins/
│   └── Jenkinsfile
│
├── docs/
│   ├── architecture.md
│   ├── aws.md
│   ├── linux.md
│   ├── terraform.md
│   ├── ansible.md
│   ├── docker.md
│   ├── kubernetes.md
│   ├── jenkins.md
│   ├── cicd.md
│   ├── monitoring.md
│   ├── troubleshooting.md
│   └── demo-script.md
│
├── .gitignore
└── README.md
```

---

# 66. Final Quality Checklist

## Application

- [ ] Application starts
- [ ] API works
- [ ] Health endpoint works
- [ ] Tests pass
- [ ] Error handling works

## Git

- [ ] Repository clean
- [ ] Branching workflow used
- [ ] Pull requests used
- [ ] No secrets committed

## Docker

- [ ] Image builds
- [ ] Container starts
- [ ] Health endpoint works
- [ ] Image has identifiable version

## AWS

- [ ] Infrastructure documented
- [ ] Security groups reviewed
- [ ] IAM reviewed
- [ ] Costs controlled

## Terraform

- [ ] Format passes
- [ ] Validate passes
- [ ] Plan works
- [ ] Apply works in approved environment
- [ ] Destroy works where appropriate

## Ansible

- [ ] Inventory works
- [ ] Playbook works
- [ ] Configuration is repeatable

## Kubernetes

- [ ] Pods healthy
- [ ] Deployment works
- [ ] Service works
- [ ] Probes work
- [ ] Scaling demonstrated
- [ ] Self-healing demonstrated

## Jenkins

- [ ] Pipeline starts
- [ ] Build works
- [ ] Tests work
- [ ] Failed tests stop pipeline
- [ ] Docker image builds
- [ ] Image pushes
- [ ] Deployment works

## Monitoring

- [ ] CloudWatch configured
- [ ] Metrics visible
- [ ] Logs available where intended
- [ ] Alarm/dashboard demonstrated

## Documentation

- [ ] README complete
- [ ] Architecture documented
- [ ] Setup documented
- [ ] Troubleshooting documented
- [ ] Demo script prepared

---

# 67. Agent Priority Order

When requirements conflict, prioritize:

```text
1. Security
2. Correctness
3. Working end-to-end pipeline
4. Reproducibility
5. Simplicity
6. Testability
7. Documentation
8. Advanced features
9. UI polish
```

---

# 68. Project Success Criteria

DevOrbit succeeds if a reviewer can understand:

```text
Why are we using AWS?
Why EC2?
Why Linux?
Why Terraform?
Why Ansible?
Why Docker?
Why Kubernetes?
Why Git?
Why Jenkins?
Why Maven?
Why CI/CD?
Why CloudWatch?
```

and the team can demonstrate the answers through a working system.

The project should communicate one central idea:

> **DevOrbit turns application delivery from a sequence of manual steps into a repeatable automated lifecycle.**

---

# 69. Final Agent Instruction

You are the development agent for **DevOrbit**.

Treat this file as the project specification.

When implementing anything:

- preserve the DevOrbit architecture
- keep the application simple
- prioritize the DevOps lifecycle
- never expose secrets
- never fake infrastructure results
- validate changes
- keep the repository organized
- document meaningful decisions
- avoid unnecessary complexity
- make the final system demonstrable
- ensure the three-person team can understand what the code does

The target is not "maximum technology."

The target is:

```text
A small application
        +
Real cloud infrastructure
        +
Infrastructure as Code
        +
Configuration automation
        +
Containerization
        +
Kubernetes orchestration
        +
CI/CD
        +
Monitoring
        =
DevOrbit
```

---

# 70. First Task for the Agent

When this repository is first opened, do NOT immediately implement everything.

First perform a project audit.

Return:

```text
1. Current repository structure
2. Existing technologies
3. What is already implemented
4. What is missing compared with this specification
5. Any architecture conflicts
6. Any security concerns
7. Recommended implementation order
8. First 3 concrete tasks
```

Then wait for the next development instruction.

Do not create AWS resources, deploy infrastructure, or consume paid cloud resources without explicit authorization.
