# Observability & CloudWatch Monitoring

## Monitoring Philosophy
DevOrbit distinguishes between infrastructure metrics and application runtime health:
1. **Infrastructure Health**: AWS CloudWatch monitors EC2 CPU utilization, network I/O, disk operations, and triggers threshold alarms.
2. **Application Health**: Kubernetes probes and Spring Boot Actuator (`/health`, `/actuator/metrics`) monitor pod readiness and application liveness.

## Configured Alarms
- **High CPU Alarm**: Evaluates average EC2 CPU utilization over 2 consecutive 120-second periods. Triggers when utilization exceeds 80%.
- **Pod CrashLoop / Restart Monitoring**: Tracked via `kubectl get pods -n devorbit`.
