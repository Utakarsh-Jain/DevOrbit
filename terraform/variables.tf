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

variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed to SSH into the hosts. Add one /32 per administrator."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.allowed_ssh_cidrs) > 0 && !contains(var.allowed_ssh_cidrs, "0.0.0.0/0")
    error_message = "allowed_ssh_cidrs must contain at least one restricted CIDR block; 0.0.0.0/0 is forbidden."
  }
}

variable "allowed_admin_cidrs" {
  description = "CIDR blocks allowed to reach Jenkins, Grafana and Prometheus. Add one /32 per administrator."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.allowed_admin_cidrs) > 0 && !contains(var.allowed_admin_cidrs, "0.0.0.0/0")
    error_message = "allowed_admin_cidrs must contain at least one restricted CIDR block; 0.0.0.0/0 is forbidden."
  }
}

variable "allowed_app_cidrs" {
  description = "CIDR blocks allowed to reach the application NodePort 30080."
  type        = list(string)
  default     = ["0.0.0.0/0"]

  validation {
    condition     = length(var.allowed_app_cidrs) > 0
    error_message = "allowed_app_cidrs must contain at least one CIDR block."
  }
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

variable "teammate_iam_users" {
  description = "Read-only console IAM users for teammates. The map key is the IAM user name; the value holds the e-mail address used for communication/tagging."
  type = map(object({
    email = string
  }))
  default = {}
}

check "ssh_public_key_should_be_set" {
  assert {
    condition     = var.ssh_public_key != ""
    error_message = "ssh_public_key is empty. Ansible cannot configure the hosts without an SSH key pair."
  }
}
