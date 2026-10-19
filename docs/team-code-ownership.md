# Team Code Ownership

Three members, three VPCs, clearly separated files so everyone can work and
push in parallel with minimal conflicts.

## Member 1 - Cloud/Infra (VPC-A)

```text
terraform/network.tf
terraform/locals.tf
terraform/data.tf
terraform/iam.tf
terraform/security_infra.tf
terraform/compute_infra.tf
terraform/monitoring.tf
ansible/roles/common/
ansible/roles/cloudwatch/
docs/aws.md, docs/terraform.md, docs/monitoring.md
```

Owns: 3 VPCs and peering, subnets, IGW, routes, infra security group, bastion,
IAM roles, SSH key pair, ECR repository, CloudWatch alarms/dashboard/log group,
Ansible baseline and CloudWatch agent.

## Member 2 - Containers/Kubernetes (VPC-B)

```text
terraform/security_app.tf
terraform/compute_app.tf
app/Dockerfile, app/.dockerignore, app/frontend/
k8s/
ansible/roles/k3s/
docs/docker.md, docs/kubernetes.md
```

Owns: the application container image, the k3s host, Kubernetes manifests,
scaling and self-healing, the k3s Ansible role.

## Member 3 - CI/CD (VPC-C)

```text
terraform/security_ci.tf
terraform/compute_ci.tf
terraform/ecr.tf
jenkins/Jenkinsfile, jenkins/README.md
ansible/roles/jenkins/
docs/jenkins.md, docs/cicd.md, docs/demo-script.md
```

Owns: the Jenkins host, Jenkins LTS role, the pipeline, ECR push and ECR
lifecycle policy, deployment verification.

## Shared files (change only with agreement)

```text
terraform/variables.tf, outputs.tf, versions.tf, providers.tf
ansible/inventory/, ansible/playbooks/, ansible/group_vars/
README.md, docs/architecture.md, docs/team-plan.md, docs/team-code-ownership.md
```

## How the split stays safe

- Terraform resource addresses are based on resource names, not filenames, so
  splitting or moving code between files does not destroy resources.
- Each member edits only their own files. Cross-VPC needs go through Member 1
  (network and security rules).
- One member runs `terraform apply` at a time. Use the S3 + DynamoDB remote
  state so the lock prevents two applies at once.
