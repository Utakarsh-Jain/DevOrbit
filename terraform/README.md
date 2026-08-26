# DevOrbit Infrastructure as Code (Terraform)

This directory contains Terraform scripts to automate the provisioning of AWS infrastructure for DevOrbit.

## Resources Provisioned
- **VPC** (`10.0.0.0/16`) with DNS hostnames and support enabled
- **Public Subnet** (`10.0.1.0/24`) with automatic public IP assignment
- **Internet Gateway** and **Route Table**
- **Security Group** for SSH (22), HTTP (80), Spring Boot (8080), Kubernetes API (6443), and NodePort range (30000-32767)
- **EC2 Instance** running Ubuntu 22.04 LTS (t3.medium / t2.micro)
- **AWS CloudWatch Metric Alarm** for high CPU utilization (>80%)

## Quickstart

### 1. Prerequisites
Ensure you have the AWS CLI configured or environment variables set:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-south-1"
```

### 2. Configure Variables
Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars` to customize your region or add your SSH public key.

### 3. Initialize & Validate
```bash
terraform init
terraform fmt -check
terraform validate
```

### 4. Review Plan
```bash
terraform plan
```

### 5. Provision Infrastructure
```bash
terraform apply -auto-approve
```

### 6. Teardown / Cleanup
To avoid ongoing AWS charges after demonstrations:
```bash
terraform destroy -auto-approve
```
