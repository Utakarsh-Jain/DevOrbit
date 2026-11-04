# Terraform Infrastructure as Code Guide

## What is IaC?

Infrastructure as Code defines compute, networking and cloud services in
declarative files instead of manual console clicks, so the environment is
reproducible and reviewable.

## What DevOrbit provisions

- 3 VPCs (`10.10.0.0/16`, `10.20.0.0/16`, `10.30.0.0/16`) with public subnets.
- Full-mesh VPC peering with routes in every route table.
- Security groups for infra, app and CI traffic.
- IAM roles and instance profiles: base, Jenkins (repository-scoped ECR push),
  app (repository-scoped ECR pull for the Kubernetes secret refresh job).
- Three EC2 instances: bastion, Jenkins, k3s (Ubuntu, encrypted gp3, IMDSv2).
- Amazon ECR repository `devorbit-app` with a lifecycle policy.
- SNS topic, CloudWatch CPU alarms, dashboard and log group.

## Where to run it

Run Terraform from the bastion host (or CloudShell) so nothing is installed on a
laptop. The files are in `terraform/`; a separate `terraform/bootstrap/` stack
creates the shared S3 state bucket.

State is stored remotely with S3 native lockfile locking (`backend.tf`):

```text
s3://devorbit-tfstate-366700733051/devorbit/terraform.tfstate
```

This requires Terraform >= 1.10 and prevents two members from applying at the
same time.

## Commands

```bash
# One time: remote state bucket (already created in this account)
cd terraform/bootstrap
terraform init
terraform apply -var="state_bucket_name=devorbit-tfstate-366700733051"

cd ..
cp terraform.tfvars.example terraform.tfvars     # set region, CIDRs, key, email

terraform init                                   # picks up backend.tf
terraform fmt -check
terraform validate
terraform plan -out=devorbit.tfplan
terraform apply devorbit.tfplan
terraform destroy
```

## Terraform vs Ansible for the viva

- **Terraform**: "What infrastructure should exist?" (VPCs, subnets, EC2, ECR, alarms).
- **Ansible**: "How should the existing servers be configured?" (Docker, k3s, Jenkins).

## Safety

- Re-running `apply` is idempotent: no duplicate resources.
- `allowed_ssh_cidrs` and `allowed_admin_cidrs` require one `/32` per
  administrator (Terraform rejects wider ranges); `allowed_app_cidrs` controls the app NodePort and should be limited to explicitly approved addresses or networks.
  All three inputs are required and reject `0.0.0.0/0`; use only explicitly
  approved administrator, reviewer, or college-network CIDRs.
- Remote state with S3 native locking stops two members applying at once. Only
  the infrastructure owner runs `apply`; other members use read-only IAM users.
- If a member's public IP changes, update the CIDR lists and re-apply.
