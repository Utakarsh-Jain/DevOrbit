# AWS Foundations for DevOrbit

## Cloud Concepts & Rationale

- **Region**: A geographically separate area (e.g. `ap-south-1` Mumbai) ensuring data sovereignty and low network latency.
- **Availability Zone (AZ)**: Isolated data center locations within a region (e.g. `ap-south-1a`) providing physical fault domain separation.
- **EC2 (Elastic Compute Cloud)**: Resizable virtual compute instances in the cloud running Linux (Ubuntu 22.04 LTS).
- **VPC (Virtual Private Cloud)**: Logically isolated virtual network with custom CIDR block (`10.0.0.0/16`), custom subnets, and internet routing.
- **Security Groups**: Stateful virtual firewalls controlling inbound and outbound network traffic.
- **IAM (Identity and Access Management)**: Enforces the principle of least privilege for cloud management and resource interactions.
- **CloudWatch**: Centralized observability service monitoring system CPU metrics, operational thresholds, and alarms.

## Security & Cost Discipline
- EC2 instances should be stopped or destroyed (`terraform destroy`) after lab sessions to eliminate idle costs.
- Never commit AWS access keys or private PEM keys into source control.
