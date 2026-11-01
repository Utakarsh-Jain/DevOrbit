# Observability and CloudWatch Monitoring

## Philosophy

DevOrbit separates infrastructure health from application health:

1. **Infrastructure**: CloudWatch monitors EC2 CPU and network, and the
   CloudWatch agent adds memory, root-disk and `/var/log/syslog` data.
2. **Application health**: Kubernetes readiness/liveness probes call `/health`;
   Spring Boot Actuator exposes `/actuator/health` internally.
3. **Application metrics**: Spring Boot Actuator exposes `/actuator/prometheus`,
   Prometheus scrapes both Pods and Grafana renders the dashboard.

CloudWatch does not replace Kubernetes health checks; they are complementary.

## What is actually monitored

| Signal | Source | Where |
| :--- | :--- | :--- |
| EC2 CPU utilization | `AWS/EC2` | per-host alarm + dashboard |
| EC2 network in/out | `AWS/EC2` | dashboard |
| Memory used % | CloudWatch agent (`CWAgent`) | dashboard |
| Root disk used % | CloudWatch agent (`CWAgent`) | dashboard |
| System logs (`/var/log/syslog`) | CloudWatch agent | `/devorbit/dev/system` log group + dashboard |
| Pod health | Kubernetes probes | `kubectl get pods` |
| HTTP request count | Micrometer + Prometheus | `http_server_requests_seconds_count` |
| Average response time | Micrometer + Prometheus | `http_server_requests_seconds_sum / _count` |
| JVM heap | Micrometer + Prometheus | `jvm_memory_used_bytes` |
| HTTP 5xx rate | Micrometer + Prometheus | `http_server_requests_seconds_count{status=~"5.."}` |
| Live threads | Micrometer + Prometheus | `jvm_threads_live_threads` |

## CloudWatch

### Alarms

| Alarm | Metric | Threshold | Action |
| :--- | :--- | :--- | :--- |
| `devorbit-dev-<host>-high-cpu` | `AWS/EC2 CPUUtilization` | >= 80% for 4 min | SNS `devorbit-dev-alerts` |
| `devorbit-dev-jenkins-high-memory` | `CWAgent mem_used_percent` | >= 85% for 10 min | SNS |
| `devorbit-dev-jenkins-high-disk` | `CWAgent disk_used_percent` | >= 85% for 10 min | SNS |

Alarms are defined in `terraform/monitoring.tf`. The Jenkins memory/disk alarms
protect the CI/CD host from a full disk during repeated Docker builds.

Email delivery is optional: set `alarm_email` in `terraform.tfvars` to subscribe
an address to the SNS topic. Until then the alarms change state in the console
and the SNS topic has no subscriber - do not claim email alerts in the viva.

### Dashboard

`terraform output cloudwatch_dashboard_url` opens `devorbit-dev-dashboard`:

- EC2 CPU utilization for the bastion, Jenkins and k3s hosts
- EC2 network throughput per host
- CloudWatch agent memory used (%) per host
- CloudWatch agent root disk used (%) per host
- Recent `/var/log/syslog` lines from the log group

The agent configuration is `ansible/roles/cloudwatch/templates/config.json.j2`.
It publishes under the `CWAgent` namespace with the `InstanceId` dimension and a
60-second collection interval.

### Logs

`/var/log/syslog` from all three hosts is shipped to `/devorbit/dev/system`
(7-day retention). Useful Logs Insights queries from the demo:

```text
fields @timestamp, @message
| filter @message like /devorbit/
| sort @timestamp desc
| limit 50
```

## Application metrics stack (Prometheus + Grafana)

The stack runs in the `devorbit` namespace on k3s and is applied by the `Deploy`
stage of the pipeline (`k8s/monitoring.yaml`).

| Component | Image | Service | URL |
| :--- | :--- | :--- | :--- |
| Prometheus | `prom/prometheus:v2.54.1` | NodePort 30090 | `terraform output prometheus_url` |
| Grafana | `grafana/grafana:11.2.0` | NodePort 32000 | `terraform output grafana_url` |

- `devorbit-app-metrics` is a headless Service, so Prometheus discovers each Pod
  IP directly and keeps a separate time series per replica.
- The scrape job `devorbit-app` targets `/actuator/prometheus` every 15 seconds.
- Grafana starts with an anonymous **Viewer** account and a provisioned
  Prometheus datasource (`uid: devorbit-prom`).
- The provisioned **DevOrbit App Metrics** dashboard (folder `DevOrbit`) has
  five panels: requests per second, average response time, JVM heap used, HTTP
  5xx per second and live threads.

### Verify

```bash
curl "$(terraform output -raw prometheus_url)/api/v1/targets?state=active"
curl "$(terraform output -raw prometheus_url)/api/v1/query?query=up%7Bjob%3D%22devorbit-app%22%7D"
curl "$(terraform output -raw grafana_url)/api/health"
kubectl get pods,svc -n devorbit
```

Both `devorbit-app` targets must report `"health":"up"`. Opening the Grafana URL
shows the dashboard without a login (viewer only).

## What is deliberately not claimed

- No Kubernetes cluster metrics in CloudWatch (no Container Insights). Pod
  health is shown by `kubectl` and the probes.
- No distributed tracing, no log aggregation beyond syslog.
- No p95 latency panel; the dashboard uses average latency. Prometheus still
  stores the histogram if a p95 query is needed during Q&A:

  ```text
  histogram_quantile(0.95,
    sum(rate(http_server_requests_seconds_bucket{job="devorbit-app"}[5m])) by (le))
  ```

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| CWAgent widgets are empty | agent not installed or wrong region | `sudo systemctl status amazon-cloudwatch-agent` on the host |
| No log lines | agent lacks `CloudWatchAgentServerPolicy` | check the instance profile |
| Prometheus target `down` | Pod not Ready or wrong metrics path | `kubectl logs` and curl `/actuator/prometheus` |
| Grafana shows "No data" | Prometheus empty after a fresh deploy | wait one scrape interval (15 s) |
| CloudWatch dashboard error | dashboard created in a different region | open the region from `terraform output` |
