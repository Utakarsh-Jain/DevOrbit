# ------------------------------------------------------------------------------
# Compute in VPC-B (k3s application host).
# Owner: Member 2 (Containers/Kubernetes)
# ------------------------------------------------------------------------------

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_types.app
  subnet_id                   = aws_subnet.public["app"].id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.instance["app"].name
  key_name                    = var.ssh_public_key != "" ? aws_key_pair.deployer[0].key_name : null

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size           = var.root_volume_size_gb.app
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "${local.name_prefix}-k3s"
    Role = "application"
  }
}
