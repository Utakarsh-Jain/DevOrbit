# DevOrbit Terraform (AWS Only)

All DevOrbit infrastructure is provisioned on AWS. Nothing here runs the
application locally: Terraform only creates AWS resources, and the workloads
run on the provisioned EC2 instances.

## What Terraform creates

```text
VPC-A 10.10.0.0/16  infra  -> bastion / Ansible control host
VPC-B 10.20.0.0/16  app    -> k3s cluster and DevOrbit application
VPC-C 10.30.0.0/16  ci     -> Jenkins CI/CD host
VPC peering: A<->B, B<->C, A<->C
```

Other resources:

- Internet gateways, public subnets, route tables
- Security groups with least privilege rules
- IAM roles + instance profiles (CloudWatch agent, SSM, ECR access)
- Amazon ECR repository `devorbit-app`
- Three EC2 instances (Ubuntu 22.04, encrypted gp3 volumes, IMDSv2 required)
- CloudWatch dashboard, CPU alarms and SNS topic
- CloudWatch log group for host/system logs

## File ownership (parallel team work)

Each file belongs to one member so the three of you can work and push without
touching each other's code. Resource addresses depend on names, not filenames,
so splitting files never recreates resources.

| File | Owner | Contents |
| :--- | :--- | :--- |
| `network.tf`, `locals.tf`, `data.tf` | Member 1 | 3 VPCs, subnets, IGW, routes, peering |
| `security_infra.tf`, `compute_infra.tf`, `iam.tf` | Member 1 | infra SG, bastion, key pair, IAM |
| `monitoring.tf` | Member 1 | SNS, alarms, dashboard, log group |
| `security_app.tf`, `compute_app.tf` | Member 2 | app SG, k3s EC2 |
| `security_ci.tf`, `compute_ci.tf`, `ecr.tf` | Member 3 | ci SG, Jenkins EC2, ECR |
| `variables.tf`, `outputs.tf`, `versions.tf`, `providers.tf` | shared | change only with agreement |

Member 2 and Member 3 only add resources inside their own VPC. The shared
network and peering stay owned by Member 1.

## Recommended workflow: AWS CloudShell

Run every command below inside **AWS CloudShell** so no Terraform binary,
Docker or Kubernetes is installed on a local machine.

```bash
# 0. Create the remote state bucket and lock table (once)
cd terraform/bootstrap
terraform init
terraform apply -var="state_bucket_name=<globally-unique-name>"

# 1. Configure the main stack
cd ..
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: set allowed_ssh_cidr, ssh_public_key, alarm_email

# 2. Optional remote state
cp backend.tf.example backend.tf
# edit backend.tf with the bucket name from step 0
terraform init -migrate-state

# 3. Validate and review
terraform fmt -check
terraform validate
terraform plan -out=devorbit.tfplan

# 4. Apply only after the plan has been approved
terraform apply devorbit.tfplan
```

## Destroy

```bash
terraform destroy
```

Destroy the bootstrap stack only when the main stack is gone.

## Inputs

| Variable | Purpose |
|---|---|
| `aws_region` | Region for all resources |
| `project_name`, `environment` | Naming and tagging |
| `vpc_cidrs`, `subnet_cidrs` | Non-overlapping network ranges |
| `instance_types` | EC2 sizes for bastion, Jenkins and k3s |
| `root_volume_size_gb` | Encrypted gp3 volumes |
| `enable_bastion` | Create the management host |
| `ssh_public_key` | Public key used by Ansible |
| `allowed_ssh_cidr` | CIDR allowed to SSH (restrict this) |
| `allowed_admin_cidr` | CIDR allowed to reach Jenkins |
| `allowed_app_cidr` | CIDR allowed to reach the application NodePort |
| `alarm_email` | Optional SNS email subscription |
| `ecr_repository_name` | ECR repository name |

## Outputs

`terraform output` gives VPC/subnet/security-group IDs, instance IDs, public and
private IPs, SSH commands, the Jenkins URL, the application and UI URLs, the ECR
repository URL, the CloudWatch dashboard URL and the kubeconfig hint used by the
Jenkins credential.

## Security notes

- `terraform plan` prints warnings while `allowed_ssh_cidr` or
  `allowed_admin_cidr` is `0.0.0.0/0`. Restrict both before apply.
- Root volumes are encrypted and IMDSv2 is required on every instance.
- IAM roles follow per-host least privilege (Jenkins can push to ECR, the
  application host can only pull).
- The Jenkins host is the only component with ECR write access.
