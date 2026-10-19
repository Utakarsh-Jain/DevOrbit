# Observability and CloudWatch Monitoring

## Philosophy

DevOrbit separates infrastructure health from application health:

1. **Infrastructure**: CloudWatch monitors EC2 CPU, network, memory, disk and
   system logs.
2. **Application**: Kubernetes readiness/liveness probes call `/health`, and
   Spring Boot Actuator exposes `/actuator/health` internally.

## What is actually monitored

| Signal | Source | Where |
| :--- | :--- | :--- |
| EC2 CPU utilization | AWS/EC2 | Alarm per host + dashboard |
| EC2 network in/out | AWS/EC2 | Dashboard |
| Memory used % | CloudWatch agent (`CWAgent`) | Dashboard/metrics |
| Disk used % | CloudWatch agent (`CWAgent`) | Dashboard/metrics |
| System logs | CloudWatch agent | `/devorbit/dev/system` log group |
| Pod health | Kubernetes probes | `kubectl get pods` |

CloudWatch does not replace Kubernetes health checks; they are complementary.

## Alarms

Terraform creates one alarm per host:

- Name: `devorbit-dev-<host>-high-cpu`
- Threshold: average CPU >= 80% for 2 x 120-second periods
- Action: publish to the `devorbit-dev-alerts` SNS topic
- Optional email subscription through `alarm_email`

## Dashboard

`terraform output cloudwatch_dashboard_url` opens the dashboard with:

- EC2 CPU utilization for bastion, Jenkins and k3s hosts
- EC2 network throughput per host
- A short operations note

## Verify

```bash
terraform output cloudwatch_dashboard_url
aws cloudwatch describe-alarms --alarm-name-prefix devorbit-dev
aws logs describe-log-groups --log-group-name-prefix /devorbit
```
