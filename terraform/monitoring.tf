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

# Memory and disk alarms for the CI/CD host. The CloudWatch agent publishes
# these under the CWAgent namespace with the InstanceId dimension.
resource "aws_cloudwatch_metric_alarm" "jenkins_memory" {
  alarm_name          = "${local.name_prefix}-jenkins-high-memory"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "mem_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  treat_missing_data  = "notBreaching"
  alarm_description   = "Memory utilization on the Jenkins host stayed above 85% for 10 minutes"

  dimensions = {
    InstanceId = aws_instance.jenkins.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "${local.name_prefix}-jenkins-high-memory"
  }
}

resource "aws_cloudwatch_metric_alarm" "jenkins_disk" {
  alarm_name          = "${local.name_prefix}-jenkins-high-disk"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  treat_missing_data  = "notBreaching"
  alarm_description   = "Root disk usage on the Jenkins host stayed above 85% for 10 minutes"

  dimensions = {
    InstanceId = aws_instance.jenkins.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Name = "${local.name_prefix}-jenkins-high-disk"
  }
}

# One dashboard covering CPU, network, memory and disk for all hosts.
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
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title       = "Memory used (%) - CloudWatch agent"
          region      = var.aws_region
          view        = "timeSeries"
          stat        = "Average"
          period      = 300
          annotations = { horizontal = [] }
          metrics = [
            for name, instance in local.instances : [
              "CWAgent",
              "mem_used_percent",
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
        y      = 6
        width  = 12
        height = 6
        properties = {
          title       = "Root disk used (%) - CloudWatch agent"
          region      = var.aws_region
          view        = "timeSeries"
          stat        = "Average"
          period      = 300
          annotations = { horizontal = [] }
          metrics = [
            for name, instance in local.instances : [
              "CWAgent",
              "disk_used_percent",
              "InstanceId",
              instance.id,
              { label = name }
            ]
          ]
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          title  = "Recent system log lines (${aws_cloudwatch_log_group.system.name})"
          region = var.aws_region
          view   = "table"
          query  = "SOURCE '${aws_cloudwatch_log_group.system.name}' | fields @timestamp, @message | sort @timestamp desc | limit 50"
        }
      },
      {
        type   = "text"
        x      = 0
        y      = 18
        width  = 24
        height = 3
        properties = {
          markdown = "# DevOrbit Monitoring\n\nEC2 CPU and network metrics, CloudWatch agent memory and root-disk metrics, and recent `/var/log/syslog` lines for the management, CI/CD and application hosts. Kubernetes pod health and application metrics are shown in Grafana (Prometheus scrapes `/actuator/prometheus` on both Pods)."
        }
      }
    ]
  })
}
