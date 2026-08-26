# DevOrbit Live Presentation & Viva Demonstration Script

## 90-Second Elevator Pitch
> *"Good morning/afternoon. DevOrbit is a cloud-native DevOps project demonstrating the entire automated software delivery lifecycle—from code commit to monitored cloud deployment.*
>
> *Instead of manually configuring servers, our infrastructure is codified using **Terraform** on AWS and provisioned via **Ansible**. Our lightweight Java Spring Boot service is containerized with **Docker**, orchestrated across **Kubernetes (k3s)** with self-healing and auto-restart capabilities, and continuously built, tested, and deployed through an automated 8-stage **Jenkins** pipeline. Finally, operational telemetry is tracked with **AWS CloudWatch**."*

---

## Step-by-Step Live Demo Runbook

| Step # | Action | Command / Location | What to Explain to Reviewer |
| :--- | :--- | :--- | :--- |
| **1** | **Show Architecture** | [docs/architecture.md](file:///c:/Users/utaka/Downloads/DevOrbit/docs/architecture.md) | Explain continuous workflow connecting GitHub $\rightarrow$ Jenkins $\rightarrow$ Docker $\rightarrow$ K8s $\rightarrow$ AWS. |
| **2** | **Trigger Code Change** | Update `app.version` in `application.properties` (e.g. `1.1.0`) & push | Demonstrates developer workflow triggering CI. |
| **3** | **Observe Jenkins Pipeline** | Jenkins Web UI | Show automated Maven compilation, unit test execution, and Docker build. |
| **4** | **Verify Kubernetes Rollout** | `kubectl get pods -n devorbit -w` | Show zero-downtime rolling update with new container version. |
| **5** | **Verify Live Application** | `curl http://<SERVER_IP>:30080/` | Highlight the updated version `1.1.0` live in response. |
| **6** | **Demonstrate Scaling** | `kubectl scale deployment/devorbit-app --replicas=3 -n devorbit` | Show instant creation of 3rd Pod replica. |
| **7** | **Demonstrate Self-Healing** | `kubectl delete pod <pod-name> -n devorbit` | Show Kubernetes immediately creating a replacement Pod. |
| **8** | **Show Monitoring** | AWS CloudWatch Console | Show EC2 CPU utilization graph and configured threshold alarm. |
| **9** | **Show IaC Reproducibility** | `terraform/main.tf` | Explain how entire AWS environment is reproducible with code. |
