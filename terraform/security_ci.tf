# ------------------------------------------------------------------------------
# Security group for VPC-C (Jenkins CI/CD).
# Owner: Member 3 (CI/CD)
# ------------------------------------------------------------------------------

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
