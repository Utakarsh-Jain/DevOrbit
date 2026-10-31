# ------------------------------------------------------------------------------
# Read-only console access for teammates.
# Owner: Member 1 (Cloud/Infra)
#
# The user names and e-mail addresses are supplied through terraform.tfvars so
# nothing personal is hardcoded in the repository. Each teammate gets:
#   - a dedicated IAM user (no access keys),
#   - read-only visibility into VPC/EC2/CloudWatch/ECR/IAM,
#   - Session Manager shell access to the DevOrbit hosts,
#   - an MFA enforcement guard.
#
# Passwords are NOT managed by Terraform. Create the console login profile once
# with the AWS CLI and share the temporary password privately.
# ------------------------------------------------------------------------------

resource "aws_iam_group" "teammates" {
  name = "${local.name_prefix}-teammates"
  path = "/devorbit/"
}

data "aws_iam_policy_document" "teammate_readonly" {
  statement {
    sid    = "ReadOnlyConsole"
    effect = "Allow"

    actions = [
      "ec2:Describe*",
      "cloudwatch:Describe*",
      "cloudwatch:Get*",
      "cloudwatch:List*",
      "logs:Describe*",
      "logs:Get*",
      "logs:FilterLogEvents",
      "logs:StartQuery",
      "logs:GetQueryResults",
      "logs:StopQuery",
      "logs:ListTagsForResource",
      "logs:ListTagsLogGroup",
      "ecr:Describe*",
      "ecr:List*",
      "ecr:Get*",
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "sns:Get*",
      "sns:List*",
      "iam:GetRole",
      "iam:ListRoles",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:ListPolicies",
      "iam:ListAttachedRolePolicies",
      "iam:ListRolePolicies",
      "iam:ListInstanceProfiles",
      "iam:ListInstanceProfilesForRole",
      "tag:GetResources",
    ]

    resources = ["*"]
  }

  statement {
    sid    = "SessionManagerShell"
    effect = "Allow"

    actions = [
      "ssm:DescribeInstanceInformation",
      "ssm:DescribeSessions",
      "ssm:GetConnectionStatus",
      "ssm:StartSession",
      "ssm:TerminateSession",
      "ssm:ResumeSession",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "teammate_readonly" {
  name        = "${local.name_prefix}-teammate-readonly"
  description = "Read-only console plus Session Manager access for DevOrbit teammates"
  policy      = data.aws_iam_policy_document.teammate_readonly.json

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_group_policy_attachment" "teammate_readonly" {
  group      = aws_iam_group.teammates.name
  policy_arn = aws_iam_policy.teammate_readonly.arn
}

# Deny every action except the MFA bootstrap allow-list until the teammate has
# signed in with MFA. This keeps the shared account protected even if a
# temporary password is shared privately.
data "aws_iam_policy_document" "teammate_mfa" {
  statement {
    sid    = "DenyAllExceptMfaBootstrapWhenMfaAbsent"
    effect = "Deny"

    not_actions = [
      "iam:ChangePassword",
      "iam:GetAccountPasswordPolicy",
      "iam:GetUser",
      "iam:ListUsers",
      "iam:ListMFADevices",
      "iam:ListVirtualMFADevices",
      "iam:CreateVirtualMFADevice",
      "iam:EnableMFADevice",
      "iam:ResyncMFADevice",
      "iam:DeactivateMFADevice",
      "iam:DeleteVirtualMFADevice",
      "sts:GetCallerIdentity",
      "sts:GetSessionToken",
    ]

    resources = ["*"]

    condition {
      test     = "BoolIfExists"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["false"]
    }
  }
}

resource "aws_iam_group_policy" "teammate_mfa" {
  name   = "${local.name_prefix}-teammate-mfa"
  group  = aws_iam_group.teammates.name
  policy = data.aws_iam_policy_document.teammate_mfa.json
}

resource "aws_iam_user" "teammate" {
  for_each = var.teammate_iam_users

  name = each.key
  path = "/devorbit/"

  tags = {
    Project = var.project_name
    Email   = each.value.email
  }
}

resource "aws_iam_user_group_membership" "teammate" {
  for_each = var.teammate_iam_users

  user   = aws_iam_user.teammate[each.key].name
  groups = [aws_iam_group.teammates.name]
}
