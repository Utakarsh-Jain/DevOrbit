# DevOrbit Live Demonstration Script

## 90-second pitch

> DevOrbit is a cloud-native DevOps project that demonstrates the entire
> automated delivery lifecycle, from a code commit to a monitored deployment on
> AWS. The infrastructure is codified with Terraform as three peered VPCs and
> configured with Ansible. The Java Spring Boot service and its React UI are
> packaged into one Docker image, stored in Amazon ECR, orchestrated on k3s with
> rolling updates and self-healing, and delivered by an 8-stage Jenkins
> pipeline. CloudWatch reports CPU, memory, disk and system logs.

## Prerequisites

- `terraform apply` completed and Ansible has configured all three hosts.
- Jenkins job created from `jenkins/Jenkinsfile` with the `k8s-kubeconfig`
  credential.
- Application URL, Jenkins URL and k3s private IP copied from `terraform output`.

## Runbook

| # | Action | Where | What to say |
| :--- | :--- | :--- | :--- |
| 1 | Open the architecture diagram | `docs/architecture.md` | GitHub -> Jenkins -> ECR -> k3s -> CloudWatch across three VPCs |
| 2 | Change `app.version` to `1.1.0` and push | Git | A developer change triggers the whole pipeline |
| 3 | Watch the Jenkins pipeline | Jenkins UI | Build, tests, image build and push to ECR |
| 4 | Watch the rollout | `kubectl get pods -n devorbit -w` | New version rolls out with no downtime |
| 5 | Open the app and UI | `http://<k3s-ip>:30080/` and `/ui/` | The new version `1.1.0` is live |
| 6 | Scale | `kubectl scale deployment/devorbit-app --replicas=3 -n devorbit` | Elasticity |
| 7 | Delete a Pod | `kubectl delete pod <pod> -n devorbit` | Kubernetes recreates it automatically |
| 8 | Show monitoring | CloudWatch dashboard | CPU, memory, disk, logs, and the CPU alarm |
| 9 | Show IaC | `terraform/` and `ansible/` | The whole environment is reproducible from code |

## Failure-gate demonstration

Temporarily break a test, push, and show the pipeline stop before the push and
deploy stages. Then revert and show it pass again.

## Cleanup

```bash
terraform destroy
```

Remove the bootstrap stack only after the main stack is destroyed.
