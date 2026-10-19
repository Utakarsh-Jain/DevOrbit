# DevOrbit Project Audit, VPC Decision, and 3-Person Work Plan

> This document records the current repository audit, identified gaps, the VPC architecture decision, the complete implementation plan, and the task division for a 3-person team.
>
> No application code was changed and no AWS resource was created/applied while preparing this audit.

---

## 1. Codebase Audit

### 1.1 Current structure

```text
DevOrbit/
├── app/            Spring Boot 3.3.4, Java 21, Maven
├── terraform/      VPC, subnet, IGW, SG, EC2, CloudWatch CPU alarm
├── ansible/        common + docker + k3s roles
├── k8s/            namespace, configmap, deployment, NodePort service
├── jenkins/        Jenkinsfile + README
├── docs/           12 docs + PPT content
├── README.md
├── AGENTS.md
└── .gitignore
```

### 1.2 Verification performed

| Check | Result |
|---|---|
| `terraform fmt -check` | PASS |
| `terraform init -backend=false` | PASS |
| `terraform validate` | PASS |
| `terraform plan` | PASS — **8 resources to add**, no resource created |
| AWS CLI identity | Working (`terraform-user`) |
| Existing AWS resources | **1 running `t3.medium` = `Jenkins-Maven-Lab`** in default VPC; a manually created `Dev-VPC` (`10.0.0.0/16`) also exists |
| `mvn` | **NOT FOUND** on PATH |
| Docker daemon | Installed but **not running** |
| Ansible | **NOT FOUND** |
| `mvn clean test` | Could not verify on this machine |
| `docker build/run` | Could not verify |
| `ansible-playbook` | Could not verify |

Important: The AWS account already has a running EC2 instance. Terraform does not manage it. Running `apply` blindly would create a **duplicate VPC + duplicate EC2** and double the cost.

### 1.3 Already implemented

**Application**
- `GET /`, `GET /health`, `GET /api/issues`, `GET /api/issues/{id}`, `POST /api/issues`, `PATCH /api/issues/{id}`
- DTO validation, global exception handler, 404/400 JSON errors
- In-memory `ConcurrentHashMap` repository with sample data
- 5 test classes
- Spring Actuator enabled

**Docker**
- Multi-stage Dockerfile, Temurin JRE 21 Alpine, non-root user `1001`, healthcheck, `.dockerignore`

**Kubernetes**
- Namespace `devorbit`, ConfigMap, Deployment 2 replicas, readiness/liveness probes, resources, rolling update, NodePort `30080`

**Terraform**
- VPC, public subnet, IGW, route table, security group, key pair, EC2 Ubuntu 22.04, CloudWatch CPU alarm

**Ansible**
- Common packages, Docker CE, k3s single-node install

**Jenkins**
- 8-stage declarative pipeline: Checkout → Build → Test → Package → Docker Build → Docker Push → Deploy → Verify

**Docs**
- README + 12 docs + demo script + PPT content

### 1.4 Critical gaps and bugs

1. **Maven wrapper missing**
   `app/` has no `mvnw` or `mvnw.cmd`. Builds are not reproducible across 3 machines. `mvn` is not installed, so local and CI builds are blocked.

2. **Shared-state test flakiness risk**
   `IssueControllerTest` shares one Spring context/repository. `shouldUpdateIssueStatusSuccessfully` (`IssueControllerTest.java:88`) changes `ISSUE-101` to `RESOLVED`, while `shouldGetIssueById` (`:40`) expects `OPEN`. If test order changes, the suite can fail. Tests must be isolated.

3. **Version duplicated in 4 places**
   `pom.xml:16`, `application.properties:7`, `k8s/deployment.yaml:9`, and `RootEndpointTest.java:26`. Bumping the version for the demo will break the test. Use a single source of truth.

4. **K8s image and Jenkins registry mismatch**
   `k8s/deployment.yaml:32` uses local `devorbit-app:1.0.0`, but `jenkins/Jenkinsfile:6-7` pushes to Docker Hub `devorbit/devorbit-app`. The first `kubectl apply` can result in `ImagePullBackOff`. There is also no `imagePullSecret`.

5. **Jenkins is not automated**
   Terraform/Ansible do not install Jenkins. The existing `Jenkins-Maven-Lab` appears manually created. The Jenkinsfile has never actually run on a real Jenkins instance.

6. **CloudWatch is incomplete**
   Only a CPU alarm exists. There are no `alarm_actions`/SNS, dashboard, log group, or CloudWatch agent. Docs claim "container status monitoring" and logs that are not implemented.

7. **Terraform is not team-safe**
   State is local; there is no S3 backend + DynamoDB lock. Three people running `apply` will corrupt/conflict state. IAM instance profile, SSM, EBS encryption, and IMDSv2 are also missing.

8. **Security issues**
   - `allowed_ssh_cidr` defaults to `0.0.0.0/0` (`terraform/variables.tf:31-35`)
   - Entire NodePort range `30000-32767` is open to the internet (`main.tf:108-115`)
   - Port `8080` is also world-open
   - `management.endpoint.health.show-details=always`
   - `host_key_checking = False` (`ansible/ansible.cfg:5`)
   - Shared `terraform-user` credentials; separate IAM users/roles are better for a team

9. **EC2 sizing risk**
   `t3.medium` = 4 GB RAM. Running Jenkins + k3s + Docker builds + 2 Spring Boot pods + 2 JVMs on it has a high OOM/CPU starvation risk. Use `t3.large` or separate EC2 hosts for Jenkins and k3s.

10. **2 replicas + in-memory storage = inconsistent API**
    A `POST` may hit pod A and a `GET` may hit pod B, so the created issue will not be found. The "create then list" demo can fail. Options: 1 replica, sticky sessions, or PostgreSQL later.

11. **Ansible has no Jenkins role**
    Only common, docker, and k3s exist. CloudWatch agent, firewall, swap disable, sysctl, and multi-node k3s join are also missing.

12. **Docs are ahead of reality**
    Webhook trigger, IAM least privilege, container monitoring, and the `/health` query in the Verify stage are claimed but not implemented. Docs must match implementation.

13. **Git workflow**
    `main` has only 1 commit. Feature branches, PR reviews, and branch protection are not used. `docs/ppt-presentation-content.md` is untracked.

14. **`.terraform.lock.hcl` is gitignored**
    Normally this file is committed so all 3 machines use the same provider version. It is currently ignored.

---

## 2. VPC Decision: 3 Separate VPCs?

**Three separate VPCs + peering is NOT recommended for DevOrbit.** It is over-engineering for this project:

- A VPC is not a collaboration boundary. Teammates collaborate through Git branches/PRs, not separate VPCs.
- 3 VPCs = 3 EC2 + 3 EBS + 3 public IPv4 + data transfer. Cost and failure points triple.
- VPC peering is **non-transitive**: A-B, B-C, and A-C require three peering connections, with route table entries on both sides.
- Splitting k3s requires opening `6443/tcp`, `10250/tcp`, `8472/udp` (flannel VXLAN), and NodePorts across VPCs. MTU/DNS issues are common.
- It is difficult to justify in a viva how 3 VPCs improved application delivery.

### Recommended architecture: 1 shared VPC + 3 logical workstreams

```text
VPC 10.0.0.0/16
├── Public Subnet A: Jenkins EC2 / bastion
├── Public Subnet B: k3s EC2 (app + cluster)
└── Optional private subnet: future DB (not now)
```

- Each member gets a **Git branch + Terraform module + responsibility**, not a separate VPC.
- If the rubric only requires demonstrating VPC creation, each member can create a personal sandbox VPC via `terraform workspace` for practice and **destroy it**. The final integrated system runs in one shared VPC.

### If 3 VPCs are mandatory

```text
VPC-A 10.10.0.0/16  → Jenkins / bastion / Ansible control
VPC-B 10.20.0.0/16  → k3s cluster + app
VPC-C 10.30.0.0/16  → monitoring host / CloudWatch agent
Peering: A↔B, B↔C, A↔C
```

Ports:
- Jenkins → k3s: `6443/tcp`, `30080/tcp`
- k3s internal nodes: `8472/udp`, `10250/tcp`
- SSH: only from bastion CIDR
- App users → `30080` (restricted CIDR)

Use this only if compulsory. Otherwise, **1 VPC + 3 subnets + correct security groups** is the more defensible academic design.

---

## 3. Complete Work Plan (Phase-wise)

| Phase | Work | Status |
|---|---|---|
| **0. Repo & toolchain** | Add Maven wrapper, verify `mvn clean test`, install Ansible, start Docker daemon, branch protection, PR workflow, commit PPT file | Partial |
| **1. Application** | Fix test isolation, single version source, green `mvn clean test`, malformed JSON test, optional Swagger | Partial |
| **2. Docker** | Verify image build/run, registry naming, tag strategy, optional image scan | Partial |
| **3. AWS baseline** | Decide reuse/import/destroy for `Jenkins-Maven-Lab` + `Dev-VPC`, AWS Budget, IAM user/role, key pair, restricted SSH CIDR | Missing |
| **4. Terraform** | Remote state S3+DynamoDB, modules, CIDR/AZ variables, IAM instance profile, SSM, EBS encryption, IMDSv2, CloudWatch dashboard/logs/SNS/alarm actions, outputs, `plan/apply/destroy` test | Partial |
| **5. Ansible** | Jenkins role, CloudWatch agent, hardening (swap/sysctl/UFW), optional multi-node k3s, idempotency rerun, `--syntax-check` | Partial |
| **6. Kubernetes** | Real registry image, `imagePullSecret`, optional Ingress, optional HPA/PDB/NetworkPolicy, apply verify, rolling update, scale, self-healing | Partial |
| **7. Jenkins** | Jenkins install, plugins, credentials, webhook/poll SCM, actual pipeline run, failing-test gate, `/health` verify, rollback, Linux agent label | Missing |
| **8. Monitoring** | SNS alarm actions, dashboard, CloudWatch agent (memory/disk), log group, Kubernetes status documentation | Partial |
| **9. Security** | Restrict SSH/NodePort, EBS encryption, IMDSv2, IAM least privilege, secrets audit, imagePullSecret, `show-details` fix, optional gitleaks | Missing |
| **10. Docs & demo** | Align docs with reality, actual outputs/commands, troubleshooting, demo script, cost cleanup, rehearsal | Partial |

---

## 4. Task Division for 3 Members

### Member A — Cloud & Infrastructure

**Owns:** `terraform/**`, `ansible/**`, `docs/aws.md`, `docs/terraform.md`, `docs/ansible.md`, `docs/linux.md`

Deliverables:
1. AWS account decision: reuse, import, or destroy existing `Dev-VPC`/`Jenkins-Maven-Lab`.
2. Terraform: VPC, subnets, IGW, route tables, SG, EC2, IAM instance profile, CloudWatch baseline, S3 backend + DynamoDB lock.
3. Ansible: common, Docker, k3s, **Jenkins role**, CloudWatch agent, hardening.
4. Outputs: `public_ip`, `instance_id`, `vpc_id`, `ssh_command`.
5. Budget + cleanup runbook.
6. Verify `terraform fmt/validate/plan/apply/destroy`; run the playbook twice to prove idempotency.

**Done when:** A new EC2 is created by Terraform, configured by Ansible, k3s is ready, and a rerun reports no changes.

### Member B — Application, Docker & Kubernetes

**Owns:** `app/**`, `k8s/**`, `docs/docker.md`, `docs/kubernetes.md`

Deliverables:
1. Maven wrapper + green `mvn clean test`.
2. Flaky test isolation fix + single version source.
3. Docker build/run/health verification; registry tag contract.
4. K8s manifests: real image, `imagePullSecret`, probes, resources, rolling update.
5. Scaling 2→3, pod-delete self-healing, version visible via `/`.
6. Optional Ingress/HPA/PDB.
7. Document the in-memory + 2-replica limitation or decide on 1 replica.

**Done when:** `kubectl rollout status` is healthy, scale/self-heal demos work, and the new version appears in the browser/API.

### Member C — CI/CD & Observability

**Owns:** `jenkins/**`, `docs/jenkins.md`, `docs/cicd.md`, `docs/monitoring.md`, `docs/demo-script.md`

Deliverables:
1. Jenkins install (Ansible role or Docker), plugins, Linux agent.
2. Credentials: registry + kubeconfig + imagePullSecret.
3. Jenkinsfile actual run: test failure → pipeline stops; success → image push → deploy → verify `/health`.
4. GitHub webhook or documented polling trigger.
5. CloudWatch: SNS topic, alarm action, dashboard, log group, agent metrics.
6. Rollback step.
7. Demo script + PPT update with real screenshots/outputs.

**Done when:** One commit builds/pushes/deploys a new image, a failing test stops the pipeline, and the CloudWatch dashboard shows real data.

### Shared responsibilities

- `README.md`, `docs/architecture.md`, security review, final demo rehearsal.
- **Only one person runs `terraform apply` at a time**; remote state lock is mandatory.
- Every PR is reviewed by another member.
- Freeze contracts: image name, tag format, namespace, service port, health path, ConfigMap keys.
- Daily 15-minute sync + weekly integration day.

---

## 5. Four-Week Execution Order

**Week 1 — Foundation**
- Maven wrapper, green tests, test isolation, single version source.
- Docker build/run verification.
- AWS decision: reuse/import/destroy existing resources.
- 1 EC2 + k3s + Jenkins install.
- Remote state setup.

**Week 2 — Infrastructure + Kubernetes**
- Complete Terraform (IAM, SG, alarm, outputs).
- Complete Ansible (Jenkins, CloudWatch agent, hardening).
- Manual K8s deploy with real registry image.
- Verify scale/self-heal/rolling update.

**Week 3 — CI/CD**
- Jenkins credentials + actual pipeline run.
- Test failure gate.
- Image push + deploy + verify `/health`.
- Webhook/poll trigger.
- Rollback.

**Week 4 — Monitoring, security, docs, demo**
- CloudWatch dashboard/alarm/SNS/logs.
- Security hardening.
- Align docs with reality.
- Full demo rehearsal twice.
- `terraform destroy` + recreate test (approved environment).

---

## 6. First 3 Concrete Tasks

1. **Write the architecture decision record** — In `docs/architecture.md`, finalize: 1 VPC vs 3 VPC peering, registry (ECR/Docker Hub/GHCR), Jenkins host (existing EC2 vs new), replicas (1 vs 2). This decision changes the Terraform layout, so do it first.

2. **Make the build reproducible** — Add the Maven wrapper in `app/`, run `mvn clean test`, isolate the flaky `IssueControllerTest`, and reduce the version to a single source. Start the Docker daemon and verify the image build/run.

3. **Reconcile AWS state** — Decide whether to import, reuse, or destroy the existing `Dev-VPC` and `Jenkins-Maven-Lab`. Then set `allowed_ssh_cidr` to your IP/32 in `terraform.tfvars` and run `terraform plan`. **Apply only after explicit approval.**

---

## 7. Decisions Required

1. **Is 3 VPC + peering a faculty requirement or an interpretation?** If compulsory, the 3-VPC design can be implemented; otherwise, 1 VPC is recommended.
2. **Which registry?** ECR is recommended (IAM-based, private). Docker Hub is simpler but requires rate-limit and credential management.
3. **Where will Jenkins run?** Reuse `Jenkins-Maven-Lab` or create a new one via Terraform?
4. **Budget?** The account already has 1 running `t3.medium`. Can you afford `t3.large`? Otherwise, Jenkins and k3s should run on separate smaller instances.
5. **1 or 2 replicas?** If 2, the in-memory data inconsistency needs a solution (1 replica or a DB).
6. **Is a frontend required?** It is optional in the spec; it is not recommended until the pipeline is stable.

After these decisions, implementation can start from Phase 0.

---

## 8. Decisions Finalized and Implemented

The team resolved every open decision above. This section records the outcome.

| Decision | Chosen | Notes |
| :--- | :--- | :--- |
| VPC layout | **3 VPCs with full-mesh peering** | A=infra, B=app, C=CI/CD; one per team member |
| Registry | **Amazon ECR** | IAM-based, private, no stored password |
| Jenkins host | **New EC2 via Terraform (VPC-C)** | `Jenkins-Maven-Lab` is left untouched |
| Replicas | **2** | With `sessionAffinity: ClientIP`; shared state documented as a limitation |
| Frontend | **Yes** | React + Vite served at `/ui/`, built into the image |
| Terraform state | **S3 + DynamoDB (bootstrap stack)** | Prevents concurrent applies |
| Where tooling runs | **AWS CloudShell / bastion** | No local Docker, Kubernetes or Maven |

Implementation status: Terraform (3 VPCs, peering, IAM, ECR, EC2, CloudWatch,
SNS), Ansible (common, cloudwatch, docker, k3s, jenkins), Kubernetes manifests,
and the ECR-based Jenkins pipeline are in place. `terraform plan` reports
52 resources to create and 0 to destroy. Apply is pending explicit approval.
