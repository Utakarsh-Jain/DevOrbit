# DevOrbit

> **The entire DevOps lifecycle revolving around one platform.**

A Cloud-Native DevOps and Infrastructure Automation academic project (team of 3).

DevOrbit runs entirely on AWS. Every workload (Maven build, Docker Engine,
k3s Kubernetes, Jenkins, and the application) executes on EC2 instances that
are created by Terraform and configured by Ansible. No part of the delivery
path depends on a developer laptop.

## 1. Architecture

Three separate VPCs, one per team member, joined by a full-mesh VPC peering.

```text
VPC-A 10.10.0.0/16  (infra / management)
  bastion host: Ansible control + operational entry point

VPC-B 10.20.0.0/16  (application)
  k3s node: DevOrbit Spring Boot + React application, NodePort 30080

VPC-C 10.30.0.0/16  (CI/CD)
  Jenkins host: Maven, Docker, ECR push, kubectl deploy

Peering: VPC-A <-> VPC-B, VPC-B <-> VPC-C, VPC-A <-> VPC-C
```

Application pipeline:

```text
Developer -> GitHub -> Jenkins -> Maven Build -> Tests -> Docker Image
        -> Amazon ECR -> k3s (Kubernetes) -> Application -> CloudWatch
```

Infrastructure pipeline:

```text
Terraform -> AWS (3 VPCs, subnets, security groups, EC2, ECR, alarms)
        -> Ansible -> configured Ubuntu hosts (Docker CE, Java 21, k3s, Jenkins, CloudWatch agent)
```

Detailed diagrams: [docs/architecture.md](docs/architecture.md).

## 2. Technology stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| Application | Java 21 / Spring Boot 3.3 | Campus Issue Management REST API with Actuator |
| Frontend | React + Vite | Minimal UI served at `/ui/` |
| Build | Apache Maven | Compile, test, package the executable JAR |
| VCS | Git + GitHub | Branching, pull requests, webhook trigger |
| Containers | Docker | Multi-stage, non-root runtime image |
| Orchestration | Kubernetes (k3s) | Rolling updates, probes, self-healing, scaling |
| IaC | Terraform | 3 VPCs, peering, EC2, IAM, ECR, CloudWatch |
| Config management | Ansible | Common baseline, Docker, k3s, Jenkins, CloudWatch agent |
| CI/CD | Jenkins | 8-stage pipeline to ECR and k3s |
| Cloud + monitoring | AWS CloudWatch | CPU alarms, dashboard, host metrics and logs |
| Registry | Amazon ECR | Versioned application images |

## 3. Application REST API

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Application name, version, environment, status |
| `GET` | `/health` | Lightweight health check used by Kubernetes probes |
| `GET` | `/api/issues` | List campus issues |
| `GET` | `/api/issues/{id}` | Get a single issue (200 or 404) |
| `POST` | `/api/issues` | Create an issue (201 or 400) |
| `PATCH` | `/api/issues/{id}` | Update issue status (200, 400 or 404) |

The React UI is available at `/ui/`.

## 4. Delivery workflow (all commands run on AWS)

Terraform and Ansible run from **AWS CloudShell** (or the bastion host). The
application itself never runs locally.

```bash
# 1. Provision infrastructure
cd terraform
cp terraform.tfvars.example terraform.tfvars   # set CIDRs, SSH key, region
terraform init && terraform plan && terraform apply

# 2. Configure the hosts
cd ../ansible
cp inventory/hosts.ini.example inventory/hosts.ini   # paste Terraform output
ansible-playbook -i inventory/hosts.ini playbooks/site.yml

# 3. Continuous delivery
#    Jenkins builds, tests, pushes to ECR and deploys to k3s automatically.
```

Verification URLs are printed by `terraform output`:

- Jenkins: `terraform output jenkins_url`
- Application: `terraform output application_url`
- UI: `terraform output application_frontend_url`

## 5. Jenkins pipeline stages

```text
Checkout -> Build -> Test -> Package -> Docker Build -> Docker Push (ECR) -> Deploy (k3s) -> Verify
```

A failing `mvn test` stops the pipeline before any image is pushed or deployed.
See [jenkins/README.md](jenkins/README.md).

## 6. Team responsibilities

| Member | VPC | Owns |
| :--- | :--- | :--- |
| Member 1 | VPC-A `10.10.0.0/16` | AWS networking, Terraform, IAM, bastion, Ansible control, CloudWatch |
| Member 2 | VPC-B `10.20.0.0/16` | Docker image, k3s cluster, Kubernetes manifests, scaling and self-healing |
| Member 3 | VPC-C `10.30.0.0/16` | Jenkins, Maven stages, ECR push, deployment automation, dashboards |

A detailed task split is in [docs/team-plan.md](docs/team-plan.md).

## 7. Documentation index

- [Architecture](docs/architecture.md)
- [AWS](docs/aws.md)
- [Linux](docs/linux.md)
- [Terraform](docs/terraform.md)
- [Ansible](docs/ansible.md)
- [Docker](docs/docker.md)
- [Kubernetes](docs/kubernetes.md)
- [Jenkins](docs/jenkins.md)
- [CI/CD](docs/cicd.md)
- [Monitoring](docs/monitoring.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Demo script](docs/demo-script.md)
- [AWS Console demo checklist](docs/aws-demo-checklist.md)
- [Team plan](docs/team-plan.md)

## 8. Known limitations

- In-memory storage: data is not shared between Pods and is lost on restart.
- Single-node k3s: high availability is limited by one application host.
- One environment (`dev`); no staging or production split.
