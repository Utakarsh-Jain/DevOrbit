# DevOrbit Live Demonstration Script

## 90-second pitch

> DevOrbit is a cloud-native DevOps project that demonstrates the entire
> automated delivery lifecycle, from a code commit to a monitored deployment on
> AWS. Terraform provisions three peered VPCs and Ansible configures the Ubuntu
> hosts. The Spring Boot service and its React UI are packaged into one Docker
> image, stored in Amazon ECR, orchestrated on k3s with rolling updates and
> self-healing, and delivered by an 8-stage Jenkins pipeline. CloudWatch reports
> EC2 CPU, memory, disk and system logs, while Prometheus scrapes application
> metrics from both Pods and Grafana visualises request rate, latency and JVM
> health.

## Prerequisites

- `terraform apply` completed and Ansible has configured all three hosts.
- Jenkins job `devorbit-pipeline` exists with the `k8s-kubeconfig` credential.
- Application, Jenkins, Grafana and Prometheus URLs copied from
  `terraform output`.
- Browser tabs pre-opened: GitHub commit page, Jenkins job, application `/`,
  Grafana, CloudWatch dashboard.
- The team has agreed who pushes the version bump, so only one build runs.

## Team sequence

| Time | Member | Segment |
| :--- | :--- | :--- |
| 0:00 | Member 1 | Architecture, three VPCs, Terraform/Ansible, CloudWatch (2 min) |
| 2:00 | Member 3 | Version bump -> Jenkins 8 stages -> ECR tag (3 min) |
| 5:00 | Member 2 | Rollout, new version live, scale to 3, delete a Pod, self-heal (2 min) |
| 7:00 | Member 3 | Failure gate + Grafana/Prometheus (2 min) |
| 9:00 | Member 1 | Limitations, cleanup policy, Q&A (1 min) |

## Runbook (Member 3 detail)

| # | Action | Where | Command / check | What to say |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Show the pipeline design | `jenkins/Jenkinsfile` | open the file | "Eight stages, one gate: a red test stops the release." |
| 2 | Bump the version | Git | edit `app/pom.xml` `1.0.0` -> `1.1.0` | "A single developer change starts the lifecycle." |
| 3 | Push and open the webhook delivery | GitHub | `git commit -m "feat: bump version to 1.1.0"` + push | "GitHub calls Jenkins on port 8080; the SG allows the GitHub hooks CIDRs." |
| 4 | Watch the build | Jenkins | build page, stage view, timestamps | "Build, test, package, image, push, deploy, verify." |
| 5 | Point at the image tag | ECR console | `devorbit-app:<build>-<sha>` | "Every release is traceable to a commit." |
| 6 | Verify the running image | k3s host | see commands below | "The cluster runs exactly the artifact that passed the tests." |
| 7 | Failure gate | Jenkins | push a deliberately broken test, then revert | "Test failed, so nothing was pushed or deployed." |
| 8 | Application metrics | Grafana | `DevOrbit App Metrics` | "Requests/s, average latency, JVM heap, 5xx and threads, from both Pods." |
| 9 | Infrastructure metrics | CloudWatch | `devorbit-dev-dashboard` | "CPU, network, memory, disk and syslog; alarms publish to SNS." |

## Commands used during the demo

Run on the k3s host (Session Manager shell) unless noted:

```bash
# Confirm the running image tag
sudo k3s kubectl get deployment devorbit-app -n devorbit \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

# Rollout history (shows the change-cause annotation written by Jenkins)
sudo k3s kubectl rollout history deployment/devorbit-app -n devorbit

# Pod and service view
sudo k3s kubectl get pods,svc -n devorbit -o wide
```

```bash
# Prometheus targets (from any host allowed to reach the NodePort)
curl -s "http://<k3s-ip>:30090/api/v1/query?query=up%7Bjob%3D%22devorbit-app%22%7D"
```

```bash
# Jenkins verification (from the Jenkins host)
sudo systemctl status jenkins --no-pager
sudo -u jenkins docker ps
```

## Failure-gate demonstration

```bash
git switch -c demo/failure-gate
# change one expected value in
# app/src/test/java/com/devorbit/IssueServiceTest.java
git add app/src/test/java/com/devorbit/IssueServiceTest.java
git commit -m "test: intentionally break test for pipeline demo"
git push origin demo/failure-gate
```

Show: Test stage red, no Docker Build/Push/Deploy, ECR tag unchanged.

```bash
git revert --no-edit HEAD
git push origin demo/failure-gate
```

Show: Test stage green and the pipeline completes.

## Likely viva questions (Member 3)

| Question | Answer |
| :--- | :--- |
| CI vs CD? | CI builds and tests every change; CD automatically deploys the tested artifact. |
| Why Jenkins? | Self-hosted on EC2, full control, plugin ecosystem, academic requirement. |
| Why ECR? | AWS-native, private, IAM-based auth, no static registry password. |
| Tag `<build>-<sha>`? | Identifiable release, traceable to the exact commit. |
| Where are AWS keys? | Nowhere; the EC2 instance profile grants ECR access. |
| What happens on a failed test? | Test stage exits non-zero; push and deploy never run. |
| How does GitHub reach Jenkins? | Webhook to `:8080/github-webhook/`; SG allows GitHub hook CIDRs. |
| Rollback? | `kubectl rollout undo deployment/devorbit-app -n devorbit`. |
| CloudWatch vs Prometheus? | Infra/host metrics and logs vs application JVM/HTTP metrics. |
| Why NodePort, not ALB? | Single-node academic k3s; ALB adds cost and no learning value. |
| What is not monitored? | No Container Insights, no tracing; say so instead of overclaiming. |

## Cleanup

```bash
terraform destroy
```

Only after the demo, and only by Member 1. Never destroy during the demo:
`kubectl delete pod` (one Pod, for self-healing) is the only destructive step.
