# DevOrbit System Architecture

## Overview

DevOrbit is an academic cloud-native DevOps project. The whole lifecycle runs
on AWS: three EC2 hosts in three peered VPCs, provisioned by Terraform and
configured by Ansible.

## Network topology

```text
VPC-A 10.10.0.0/16 (infra)        VPC-B 10.20.0.0/16 (app)         VPC-C 10.30.0.0/16 (ci)
+-------------------------+        +-------------------------+      +-------------------------+
| bastion / Ansible host  |        | k3s single node         |      | Jenkins LTS host        |
| - operational entry     |        | - DevOrbit Pods (x2)    |      | - Maven build + tests   |
| - SSH + CloudWatch      |        | - NodePort 30080        |      | - Docker build/push ECR |
+-------------------------+        +-------------------------+      +-------------------------+
        |                                    |                              |
        |            VPC peering (full mesh) full mesh                    |
        +----------------  A<->B   B<->C   A<->C  -------------------------+
```

## Application lifecycle

```text
Developer -> GitHub -> Jenkins (VPC-C) -> Maven Build + Tests -> Docker Image
        -> Amazon ECR -> k3s (VPC-B) -> DevOrbit application -> CloudWatch
```

## Infrastructure lifecycle

```text
Terraform (CloudShell) -> AWS (3 VPCs, peering, subnets, security groups,
EC2, IAM, ECR, alarms) -> Ansible -> configured Ubuntu hosts
(Docker CE, Java 21, k3s, Jenkins, CloudWatch agent)
```

## Components

1. **Spring Boot application (`app/`)**: campus issue REST API, Maven built,
   packaged with a React UI into a single non-root container.
2. **Frontend (`app/frontend/`)**: React + Vite UI served at `/ui/`.
3. **Infrastructure as Code (`terraform/`)**: 3 VPCs, full-mesh peering,
   subnets, route tables, security groups, IAM, ECR, EC2, SNS + alarms.
4. **Configuration automation (`ansible/`)**: baseline, Docker, k3s, Jenkins
   and CloudWatch agent roles.
5. **Orchestration (`k8s/`)**: `devorbit` namespace, ConfigMap, rolling
   deployment with replicas and probes, NodePort service.
6. **CI/CD (`jenkins/`)**: 8-stage pipeline that pushes to ECR and deploys to
   k3s.
7. **Observability (CloudWatch)**: EC2 CPU alarms, dashboard, and host metrics
   and logs from the CloudWatch agent.

## Why each technology

| Technology | Reason |
| :--- | :--- |
| AWS | Provides the cloud compute, networking and managed services |
| EC2 | Simple, predictable Linux hosts for both workloads and tooling |
| Linux | Standard environment for Docker, k3s and Jenkins |
| Terraform | Reproducible, version-controlled infrastructure |
| Ansible | Idempotent configuration after provisioning |
| Docker | Immutable, portable application image |
| Kubernetes (k3s) | Rolling updates, probes, self-healing, scaling |
| Amazon ECR | Private, IAM-integrated image registry |
| Git/GitHub | Version control and change trigger |
| Jenkins | Automated CI/CD execution |
| Maven | Consistent Java build and test lifecycle |
| CloudWatch | Resource and host observability |
