# Observability and CloudWatch Monitoring

## Philosophy

DevOrbit separates infrastructure health from application health:

1. **Infrastructure**: CloudWatch monitors EC2 CPU, network, memory, disk and
   system logs.
2. **Application health**: Kubernetes readiness/liveness probes call `/health`,
   and Spring Boot Actuator exposes `/actuator/health` internally.
3. **Application metrics**: Spring Boot Actuator exposes `/actuator/prometheus`,
   Prometheus scrapes both Pods, and Grafana visualizes the metrics.

## What is actually monitored

| Signal | Source | Where |
| :--- | :--- | :--- |
| EC2 CPU utilization | AWS/EC2 | Alarm per host + dashboard |
| EC2 network in/out | AWS/EC2 | Dashboard |
| Memory used % | CloudWatch agent (`CWAgent`) | Dashboard/metrics |
| Disk used % | CloudWatch agent (`CWAgent`) | Dashboard/metrics |
| System logs | CloudWatch agent | `/devorbit/dev/system` log group |
| Pod health | Kubernetes probes | `kubectl get pods` |
| HTTP request count/latency | Micrometer + Prometheus | `http_server_requests_seconds_*` |
| JVM heap, threads, GC | Micrometer + Prometheus | `jvm_*` |
| Scrape status of both Pods | Prometheus | `up{job="devorbit-app"}` |
| App metrics dashboard | Grafana | `DevOrbit App Metrics` |

CloudWatch does not replace Kubernetes health checks; they are complementary.

## Application metrics stack (Prometheus + Grafana)

The monitoring stack runs in the `devorbit` namespace on k3s and is applied by
the `Deploy` stage of the Jenkins pipeline (`k8s/monitoring.yaml`).

| Component | Image | Service | URL |
| :--- | :--- | :--- | :--- |
| Prometheus | `prom/prometheus:v2.54.1` | NodePort 30090 | `terraform output prometheus_url` |
| Grafana | `grafana/grafana:11.2.0` | NodePort 32000 | `terraform output grafana_url` |

- `devorbit-app-metrics` is a headless Service, so Prometheus discovers each Pod
  IP directly and keeps a separate time series per replica.
- The scrape job `devorbit-app` targets `/actuator/prometheus` every 15 seconds.
- Grafana starts with an anonymous **Viewer** account and a provisioned
  Prometheus datasource (`uid: devorbit-prom`).
- The provisioned dashboard `DevOrbit App Metrics` shows request rate per URI,
  p95 latency, JVM heap usage, Pod count and scrape health.

### Verify

```bash
curl "$(terraform output -raw prometheus_url)/api/v1/targets?state=active"
curl "$(terraform output -raw prometheus_url)/api/v1/query?query=up%7Bjob%3D%22devorbit-app%22%7D"
curl "$(terraform output -raw grafana_url)/api/health"
kubectl get pods,svc -n devorbit
```

Both `devorbit-app` targets must report `"health":"up"`. Opening the Grafana URL
shows the dashboard without a login (viewer only).

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
