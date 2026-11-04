# ------------------------------------------------------------------------------
# Shared IAM roles and instance profiles for the DevOrbit hosts.
# Owner: Member 1 (Cloud/Infra)
#
#   base     -> CloudWatch agent + SSM (bastion)
#   jenkins  -> CloudWatch + SSM + ECR push (Member 3 host)
#   app      -> CloudWatch + SSM + ECR pull from the DevOrbit repository
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
    ]
    app = [
      "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
      "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
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

data "aws_iam_policy_document" "jenkins_ecr_push" {
  statement {
    sid       = "GetEcrAuthorizationToken"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "PushDevOrbitImages"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [aws_ecr_repository.app.arn]
  }
}

resource "aws_iam_role_policy" "jenkins_ecr_push" {
  name   = "${local.name_prefix}-jenkins-ecr-push"
  role   = aws_iam_role.instance["jenkins"].id
  policy = data.aws_iam_policy_document.jenkins_ecr_push.json
}

data "aws_iam_policy_document" "app_ecr_pull" {
  statement {
    sid       = "GetEcrAuthorizationToken"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "PullDevOrbitImages"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]

    resources = [aws_ecr_repository.app.arn]
  }
}

resource "aws_iam_role_policy" "app_ecr_pull" {
  name   = "${local.name_prefix}-app-ecr-pull"
  role   = aws_iam_role.instance["app"].id
  policy = data.aws_iam_policy_document.app_ecr_pull.json
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
