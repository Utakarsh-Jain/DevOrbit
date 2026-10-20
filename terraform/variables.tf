# ------------------------------------------------------------------------------
# DevOrbit Terraform input variables
# ------------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS region in which all DevOrbit resources are created"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name used as a prefix for all resource names"
  type        = string
  default     = "devorbit"
}

variable "environment" {
  description = "Deployment environment (for example dev or demo)"
  type        = string
  default     = "dev"
}

variable "vpc_cidrs" {
  description = "Non-overlapping CIDR ranges for the three DevOrbit VPCs"
  type = object({
    infra = string
    app   = string
    ci    = string
  })
  default = {
    infra = "10.10.0.0/16"
    app   = "10.20.0.0/16"
    ci    = "10.30.0.0/16"
  }
}

variable "subnet_cidrs" {
  description = "Public subnet CIDR ranges (one per VPC)"
  type = object({
    infra = string
    app   = string
    ci    = string
  })
  default = {
    infra = "10.10.1.0/24"
    app   = "10.20.1.0/24"
    ci    = "10.30.1.0/24"
  }
}

variable "instance_types" {
  description = "EC2 instance sizes for the bastion, Jenkins and k3s hosts"
  type = object({
    bastion = string
    jenkins = string
    app     = string
  })
  default = {
    bastion = "t3.micro"
    jenkins = "t3.medium"
    app     = "t3.medium"
  }
}

variable "root_volume_size_gb" {
  description = "Encrypted gp3 root volume size (GB) for each host"
  type = object({
    bastion = number
    jenkins = number
    app     = number
  })
  default = {
    bastion = 10
    jenkins = 30
    app     = 30
  }
}

variable "enable_bastion" {
  description = "Create the management/bastion host in the infra VPC"
  type        = bool
  default     = true
}

variable "ssh_public_key" {
  description = "SSH public key content used to access the EC2 instances (leave empty to skip key creation)"
  type        = string
  default     = ""
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into the hosts. Set this to your public IP/32."
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_admin_cidr" {
  description = "CIDR allowed to reach the Jenkins web UI on port 8080"
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_app_cidr" {
  description = "CIDR allowed to reach the application NodePort 30080"
  type        = string
  default     = "0.0.0.0/0"
}

variable "github_hook_cidrs" {
  description = "GitHub webhook source CIDRs allowed to reach the Jenkins hook endpoint on port 8080. Refresh from https://api.github.com/meta (hooks) if GitHub deliveries start failing."
  type        = list(string)
  default = [
    "9.234.106.48/28",
    "9.234.98.160/28",
    "9.234.98.176/28",
    "192.30.252.0/22",
    "185.199.108.0/22",
    "140.82.112.0/20",
    "143.55.64.0/20",
  ]
}

variable "alarm_email" {
  description = "Optional email address subscribed to CloudWatch alarm notifications"
  type        = string
  default     = ""
}

variable "ecr_repository_name" {
  description = "Name of the Amazon ECR repository that stores DevOrbit container images"
  type        = string
  default     = "devorbit-app"
}

# ------------------------------------------------------------------------------
# Safety checks. These produce plan warnings until the CIDRs are restricted.
# ------------------------------------------------------------------------------

check "ssh_cidr_should_be_restricted" {
  assert {
    condition     = var.allowed_ssh_cidr != "0.0.0.0/0"
    error_message = "allowed_ssh_cidr is open to the world. Restrict SSH to your administrator CIDR before applying."
  }
}

check "jenkins_ui_should_be_restricted" {
  assert {
    condition     = var.allowed_admin_cidr != "0.0.0.0/0"
    error_message = "allowed_admin_cidr is open to the world. Restrict the Jenkins UI to a trusted CIDR."
  }
}

check "ssh_public_key_should_be_set" {
  assert {
    condition     = var.ssh_public_key != ""
    error_message = "ssh_public_key is empty. Ansible cannot configure the hosts without an SSH key pair."
  }
}
