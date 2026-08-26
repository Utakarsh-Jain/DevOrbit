variable "aws_region" {
  description = "AWS Region where infrastructure will be deployed"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name of the DevOps project"
  type        = string
  default     = "devorbit"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, local, staging)"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance size for running Jenkins/k3s workload"
  type        = string
  default     = "t3.medium"
}

variable "ssh_public_key" {
  description = "SSH public key content used to access EC2 instances"
  type        = string
  default     = ""
}

variable "allowed_ssh_cidr" {
  description = "Allowed CIDR block for SSH ingress (restrict to admin IP)"
  type        = string
  default     = "0.0.0.0/0"
}
