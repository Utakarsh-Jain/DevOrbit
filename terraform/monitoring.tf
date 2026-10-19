# ------------------------------------------------------------------------------
# Monitoring layer: SNS alerts, CloudWatch alarms, dashboard and log group.
# ------------------------------------------------------------------------------

resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"

  tags = {
    Name = "${local.name_prefix}-alerts"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count = var.alarm_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# High CPU alarm for each DevOrbit host.
resource "aws_cloudwatch_metric_alarm" "cpu" {
  for_each = local.instances

  alarm_name          = "${local.name_prefix}-${each.key}-high-cpu"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "notBreaching"
  alarm_description   = "CPU utilization for the ${each.key} host stayed above 80% for 4 minutes"

  dimensions = {
    InstanceId = each.value.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "${local.name_prefix}-${each.key}-high-cpu"
  }
}

# Log group that receives syslog/auth.log from the CloudWatch agent (installed by Ansible).
resource "aws_cloudwatch_log_group" "system" {
  name              = "/${var.project_name}/${var.environment}/system"
  retention_in_days = 7

  tags = {
    Name = "/${var.project_name}/${var.environment}/system"
  }
}

# One dashboard covering CPU and network metrics for all hosts.
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title       = "EC2 CPU utilization (%)"
          region      = var.aws_region
          view        = "timeSeries"
          stat        = "Average"
          period      = 300
          annotations = { horizontal = [] }
          metrics = [
            for name, instance in local.instances : [
              "AWS/EC2",
              "CPUUtilization",
              "InstanceId",
              instance.id,
              { label = name }
            ]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title       = "EC2 network throughput"
          region      = var.aws_region
          view        = "timeSeries"
          stat        = "Sum"
          period      = 300
          annotations = { horizontal = [] }
          metrics = concat([
            for name, instance in local.instances : [
              ["AWS/EC2", "NetworkIn", "InstanceId", instance.id, { label = "${name} in" }],
              ["AWS/EC2", "NetworkOut", "InstanceId", instance.id, { label = "${name} out" }]
            ]
          ]...)
        }
      },
      {
        type   = "text"
        x      = 0
        y      = 6
        width  = 24
        height = 3
        properties = {
          markdown = "# DevOrbit Monitoring\n\nEC2 CPU and network metrics for the management, CI/CD and application hosts. Memory, disk and system logs are published by the CloudWatch agent installed through Ansible into the `CWAgent` namespace and the `${aws_cloudwatch_log_group.system.name}` log group."
        }
      }
    ]
  })
}
