# AWS Foundations for DevOrbit

## Cloud concepts

- **Region**: geographically separate area (for example `ap-south-1`).
- **Availability Zone**: isolated data center inside a region.
- **EC2**: resizable Linux instances (Ubuntu 22.04 LTS) that run every DevOrbit
  workload.
- **VPC**: isolated virtual network with its own CIDR block.
- **Subnet, route table, internet gateway**: make a VPC reachable.
- **VPC peering**: connects two VPCs so they can use private IP addresses.
- **Security group**: stateful virtual firewall for inbound and outbound traffic.
- **IAM**: least-privilege roles for hosts and services.
- **Amazon ECR**: private container image registry integrated with IAM.
- **CloudWatch**: metrics, logs, dashboard and alarms.
- **SNS**: notification target for CloudWatch alarms.

## DevOrbit on AWS

```text
VPC-A 10.10.0.0/16  management: bastion, Ansible, CloudWatch agent
VPC-B 10.20.0.0/16  application: k3s, DevOrbit Pods, NodePort 30080
VPC-C 10.30.0.0/16  CI/CD: Jenkins, Docker, Maven, ECR push
Peering: VPC-A <-> VPC-B <-> VPC-C <-> VPC-A
```

- Three VPCs, one per team member, each with a public subnet and route table.
- Amazon ECR repository `devorbit-app` stores versioned images.
- CloudWatch covers EC2 CPU alarm per host, a combined dashboard, and a log
  group fed by the CloudWatch agent.
- Terraform and Ansible are executed from a control workstation, the bastion or
  AWS CloudShell; they are control-plane tools only.

## Cost and security discipline

- Run `terraform destroy` after each lab session to stop idle charges.
- Never commit AWS access keys or private keys.
- Restrict `allowed_ssh_cidr`, `allowed_admin_cidr` and `allowed_app_cidr` to
  your own IP. Jenkins, Grafana and Prometheus are not public.
- Port 8080 also allows GitHub's published webhook ranges (`github_hook_cidrs`)
  so pushes can trigger the pipeline. Refresh them from
  `https://api.github.com/meta` (`hooks`) when GitHub reports connection errors.
- Rotate the Jenkins administrator password after the first login; never commit
  it or keep it in a shell history file.
- Hosts use IAM roles, so no credentials are stored on the instances.
- Terraform state lives in a private, versioned S3 bucket; do not upload private
  keys to any bucket.
