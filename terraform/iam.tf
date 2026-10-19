# ------------------------------------------------------------------------------
# Shared IAM roles and instance profiles for the DevOrbit hosts.
# Owner: Member 1 (Cloud/Infra)
#
#   base     -> CloudWatch agent + SSM (bastion)
#   jenkins  -> CloudWatch + SSM + ECR push (Member 3 host)
#   app      -> CloudWatch + SSM + ECR pull (Member 2 host)
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
