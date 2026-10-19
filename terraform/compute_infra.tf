# ------------------------------------------------------------------------------
# Compute in VPC-A (management / bastion) and the shared SSH key pair.
# Owner: Member 1 (Cloud/Infra)
# ------------------------------------------------------------------------------

resource "aws_key_pair" "deployer" {
  count = var.ssh_public_key != "" ? 1 : 0

  key_name   = "${local.name_prefix}-key"
  public_key = var.ssh_public_key
}

resource "aws_instance" "bastion" {
  count = var.enable_bastion ? 1 : 0

  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_types.bastion
  subnet_id                   = aws_subnet.public["infra"].id
  vpc_security_group_ids      = [aws_security_group.infra.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.instance["base"].name
  key_name                    = var.ssh_public_key != "" ? aws_key_pair.deployer[0].key_name : null

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size           = var.root_volume_size_gb.bastion
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "${local.name_prefix}-bastion"
    Role = "management"
  }
}
