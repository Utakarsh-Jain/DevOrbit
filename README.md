# DevOrbit 🚀

> **The entire DevOps lifecycle revolving around one platform.**
> 
> *A Cloud-Native DevOps & Infrastructure Automation Academic Project*

---

## 1. Project Overview

DevOrbit connects every stage of the software delivery lifecycle into a single continuous, automated, and observable pipeline. Rather than treating AWS, Linux, Terraform, Ansible, Docker, Kubernetes, Git, and Jenkins as separate siloed exercises, DevOrbit unifies them:

```text
+------------------------------------------------------------------------------------+
|                                 APPLICATION PIPELINE                               |
|                                                                                    |
|   Developer ──> GitHub ──> Jenkins ──> Maven Build & Test ──> Docker Image        |
|                                                                     │              |
|                                                                     v              |
|                                                              Container Registry    |
|                                                                     │              |
|                                                                     v              |
|                                                           Kubernetes (k3s)         |
|                                                                     │              |
|                                                                     v              |
|                                                              AWS CloudWatch        |
+------------------------------------------------------------------------------------+

+------------------------------------------------------------------------------------+
|                               INFRASTRUCTURE PIPELINE                              |
|                                                                                    |
|   Terraform ──> AWS Infrastructure (VPC, Subnet, Security Groups, EC2, Alarms)     |
|        │                                                                           |
|        v                                                                           |
|     Ansible ──> Configured Linux Environment (Docker CE + Java 21 + k3s Cluster)   |
+------------------------------------------------------------------------------------+
```

---

## 2. Technology Stack

| Layer | Technology | Role in DevOrbit |
| :--- | :--- | :--- |
| **Application** | Java 21 / Spring Boot 3.3 | Lightweight Campus Issue Management REST API with Actuator |
| **Build Tool** | Apache Maven | Compiles, validates, runs automated unit tests, and packages JAR |
| **Version Control** | Git + GitHub | Branching workflow, pull request reviews, and CI webhook triggers |
| **Containerization** | Docker | Multi-stage, unprivileged container packaging (`devorbit-app`) |
| **Orchestration** | Kubernetes (k3s) | Rolling deployments, service discovery, self-healing, and scaling |
| **Infrastructure as Code** | Terraform | Automated provisioning of AWS VPC, Subnet, Security Group, and EC2 |
| **Config Management** | Ansible | Automated configuration of Linux packages, Docker, and k3s |
| **CI/CD Automation** | Jenkins | 8-stage declarative pipeline (Build $\rightarrow$ Test $\rightarrow$ Package $\rightarrow$ Push $\rightarrow$ Deploy) |
| **Cloud & Monitoring** | AWS & CloudWatch | EC2 compute, network security groups, and CPU utilization alarms |

---

## 3. Application REST API Specification

| Method | Endpoint | Description | Sample Response / Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root info & version | `{"application":"DevOrbit...","version":"1.0.0","status":"running"}` (200 OK) |
| `GET` | `/health` | Healthcheck for K8s probes | `{"status":"UP"}` (200 OK) |
| `GET` | `/api/issues` | List all campus issues | `[{"id":"ISSUE-101","title":"...","status":"OPEN"}]` (200 OK) |
| `GET` | `/api/issues/{id}` | Get issue by ID | `{"id":"ISSUE-101","title":"...","status":"OPEN"}` (200 OK / 404 Not Found) |
| `POST` | `/api/issues` | Create new issue | `{"title":"...","description":"..."}` (201 Created / 400 Bad Request) |
| `PATCH` | `/api/issues/{id}` | Update issue status | `{"status":"RESOLVED"}` (200 OK / 400 / 404) |

---

## 4. Local Development & Testing

### Run Locally with Maven
```bash
cd app
mvn clean test
mvn spring-boot:run
```

### Build & Run Container with Docker
```bash
docker build -t devorbit-app:local app/
docker run -d -p 8080:8080 --name devorbit-local devorbit-app:local
curl http://localhost:8080/health
```

---

## 5. Infrastructure Provisioning (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Update terraform.tfvars with your region and SSH public key
terraform init
terraform plan
terraform apply -auto-approve
```

---

## 6. Server Configuration (Ansible)

```bash
cd ansible
cp inventory/hosts.ini.example inventory/hosts.ini
# Insert EC2 Public IP from Terraform output
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

---

## 7. Kubernetes Deployment

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods,svc -n devorbit
```

---

## 8. Jenkins CI/CD Pipeline Stages

1. **Checkout**: Pulls code from GitHub.
2. **Build**: Compiles source via Maven.
3. **Test**: Runs automated unit tests (`mvn test`). Fails pipeline if any test fails.
4. **Package**: Builds `target/devorbit.jar`.
5. **Docker Build**: Creates tagged Docker image.
6. **Docker Push**: Pushes image to container registry using Jenkins credentials.
7. **Deploy**: Applies Kubernetes manifests to cluster.
8. **Verify**: Asserts rollout status and health endpoint.

---

## 9. Team Responsibilities (Team of 3)

- **Member 1 (Cloud & IaC)**: AWS VPC, EC2, IAM, Terraform scripts, and Linux host administration.
- **Member 2 (Containers & Kubernetes)**: Docker packaging, Kubernetes manifests, pod scaling, and self-healing.
- **Member 3 (CI/CD & Observability)**: Jenkins pipeline, Maven automation, tests, and CloudWatch alarms.

---

## 10. Documentation Index

- [Architecture Guide](file:///docs/architecture.md)
- [AWS Cloud Guide](file:///docs/aws.md)
- [Linux & Administration Guide](file:///docs/linux.md)
- [Terraform IaC Guide](file:///docs/terraform.md)
- [Ansible Guide](file:///docs/ansible.md)
- [Docker Containerization Guide](file:///docs/docker.md)
- [Kubernetes Guide](file:///docs/kubernetes.md)
- [Jenkins Automation Guide](file:///docs/jenkins.md)
- [CI/CD Lifecycle Guide](file:///docs/cicd.md)
- [Observability & Monitoring Guide](file:///docs/monitoring.md)
- [Troubleshooting Runbook](file:///docs/troubleshooting.md)
- [Live Viva Presentation Script](file:///docs/demo-script.md)
