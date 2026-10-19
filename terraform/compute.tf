# ------------------------------------------------------------------------------
# Compute layer: IAM, EC2 instances and the ECR image repository.
# ------------------------------------------------------------------------------

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

locals {
  # Managed policies attached to each instance profile.
  role_policies = {
    base = [
      "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
    ]
    jenkins = [
      "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
      "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser",
    ]
    app = [
      "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
      "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    ]
  }

  # Flatten the role -> policy map into a set of attachments.
  role_policy_attachments = merge([
    for role, policies in local.role_policies : {
      for policy in policies : "${role}::${policy}" => {
        role   = role
        policy = policy
      }
    }
  ]...)
}

resource "aws_iam_role" "instance" {
  for_each = local.role_policies

  name               = "${local.name_prefix}-${each.key}-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = {
    Name = "${local.name_prefix}-${each.key}-role"
  }
}

resource "aws_iam_role_policy_attachment" "instance" {
  for_each = local.role_policy_attachments

  role       = aws_iam_role.instance[each.value.role].name
  policy_arn = each.value.policy
}

resource "aws_iam_instance_profile" "instance" {
  for_each = local.role_policies

  name = "${local.name_prefix}-${each.key}-profile"
  role = aws_iam_role.instance[each.key].name
}

# Optional SSH key pair used by Ansible and manual administration.
resource "aws_key_pair" "deployer" {
  count = var.ssh_public_key != "" ? 1 : 0

  key_name   = "${local.name_prefix}-key"
  public_key = var.ssh_public_key
}

# Amazon ECR repository that stores the versioned DevOrbit images.
resource "aws_ecr_repository" "app" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name = var.ecr_repository_name
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the last 15 DevOrbit images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 15
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Management / bastion host (infra VPC)
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

# Jenkins CI/CD host (ci VPC)
resource "aws_instance" "jenkins" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_types.jenkins
  subnet_id                   = aws_subnet.public["ci"].id
  vpc_security_group_ids      = [aws_security_group.ci.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.instance["jenkins"].name
  key_name                    = var.ssh_public_key != "" ? aws_key_pair.deployer[0].key_name : null

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size           = var.root_volume_size_gb.jenkins
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name = "${local.name_prefix}-jenkins"
    Role = "cicd"
  }
}

# k3s application host (app VPC)
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

# Convenience map used by monitoring and outputs.
locals {
  instances = merge(
    {
      jenkins = aws_instance.jenkins
      app     = aws_instance.app
    },
    {
      for index, instance in aws_instance.bastion :
      (index == 0 ? "bastion" : "bastion-${index + 1}") => instance
    }
  )
}
