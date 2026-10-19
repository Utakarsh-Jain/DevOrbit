# Terraform Infrastructure as Code Guide

## What is IaC?

Infrastructure as Code defines compute, networking and cloud services in
declarative files instead of manual console clicks, so the environment is
reproducible and reviewable.

## What DevOrbit provisions

- 3 VPCs (`10.10.0.0/16`, `10.20.0.0/16`, `10.30.0.0/16`) with public subnets.
- Full-mesh VPC peering with routes in every route table.
- Security groups for infra, app and CI traffic.
- IAM roles and instance profiles: base, Jenkins (ECR push), app (ECR pull).
- Three EC2 instances: bastion, Jenkins, k3s (Ubuntu, encrypted gp3, IMDSv2).
- Amazon ECR repository `devorbit-app` with a lifecycle policy.
- SNS topic, CloudWatch CPU alarms, dashboard and log group.

## Where to run it

Run Terraform inside **AWS CloudShell** so nothing is installed on a laptop.
The files are in `terraform/`; a separate `terraform/bootstrap/` stack creates
the S3 state bucket and DynamoDB lock table.

## Commands

```bash
# One time: remote state
cd terraform/bootstrap
terraform init
terraform apply -var="state_bucket_name=<unique-name>"

cd ..
cp terraform.tfvars.example terraform.tfvars     # set region, CIDRs, key, email

terraform init
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
- The stack warns while SSH or Jenkins is open to `0.0.0.0/0`.
- Remote state with DynamoDB locking stops two members applying at once.
