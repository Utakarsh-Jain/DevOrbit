# ------------------------------------------------------------------------------
# Security groups
# Each VPC gets a dedicated stateful firewall. Cross-VPC rules reference the
# peered VPC CIDR blocks instead of opening ports to the whole internet.
# ------------------------------------------------------------------------------

# Management / bastion VPC
resource "aws_security_group" "infra" {
  name        = "${local.name_prefix}-infra-sg"
  description = "DevOrbit management VPC security group"
  vpc_id      = aws_vpc.this["infra"].id

  ingress {
    description = "SSH from the administrator CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-infra-sg"
  }
}

# Application / k3s VPC
resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app-sg"
  description = "DevOrbit application VPC security group (k3s and workload)"
  vpc_id      = aws_vpc.this["app"].id

  ingress {
    description = "SSH from the administrator CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "SSH from the management VPC (Ansible)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["infra"].cidr]
  }

  ingress {
    description = "SSH from the CI/CD VPC (Ansible and troubleshooting)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["ci"].cidr]
  }

  ingress {
    description = "k3s API server from the CI/CD VPC (Jenkins deploys)"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["ci"].cidr]
  }

  ingress {
    description = "k3s API server from the management VPC"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["infra"].cidr]
  }

  ingress {
    description = "Application NodePort for public users"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = [var.allowed_app_cidr]
  }

  ingress {
    description = "Application NodePort from the CI/CD VPC (pipeline verification)"
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["ci"].cidr]
  }

  ingress {
    description = "Container port from the CI/CD VPC"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["ci"].cidr]
  }

  ingress {
    description = "Container port from the management VPC"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["infra"].cidr]
  }

  ingress {
    description = "k3s flannel VXLAN between cluster nodes"
    from_port   = 8472
    to_port     = 8472
    protocol    = "udp"
    cidr_blocks = [local.vpcs["app"].cidr]
  }

  ingress {
    description = "k3s kubelet API between cluster nodes"
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["app"].cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-app-sg"
  }
}

# CI/CD VPC
resource "aws_security_group" "ci" {
  name        = "${local.name_prefix}-ci-sg"
  description = "DevOrbit CI/CD VPC security group (Jenkins)"
  vpc_id      = aws_vpc.this["ci"].id

  ingress {
    description = "SSH from the administrator CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "SSH from the management VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [local.vpcs["infra"].cidr]
  }

  ingress {
    description = "Jenkins web UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.allowed_admin_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-ci-sg"
  }
}
