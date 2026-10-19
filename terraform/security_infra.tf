# ------------------------------------------------------------------------------
# Security group for VPC-A (management / bastion).
# Owner: Member 1 (Cloud/Infra)
# ------------------------------------------------------------------------------

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
