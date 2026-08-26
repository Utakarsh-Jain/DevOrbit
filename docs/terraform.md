# Terraform Infrastructure as Code Guide

## What is IaC?
Infrastructure as Code (IaC) defines compute, networking, and cloud services in declarative configuration files rather than manual console interactions.

## Core Commands
```bash
# Initialize working directory and download AWS provider
terraform init

# Check configuration syntax and formatting
terraform fmt -check
terraform validate

# Create an execution plan showing predicted changes
terraform plan

# Apply changes to provision real AWS resources
terraform apply -auto-approve

# Destroy all provisioned resources upon completion
terraform destroy -auto-approve
```

## Difference for Viva
- **Terraform**: "What infrastructure should exist?" (VPC, Subnets, EC2, CloudWatch).
- **Ansible**: "How should existing servers be configured?" (Software installation, services, clustering).
