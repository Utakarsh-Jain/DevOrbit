# Jenkins CI/CD Automation Guide

## Pipeline architecture

Jenkins runs on the EC2 host in VPC-C and executes the 8 stages in
`jenkins/Jenkinsfile`.

```text
Checkout -> Build -> Test -> Package -> Docker Build -> Docker Push (ECR) -> Deploy (k3s) -> Verify
```

- Maven and Docker are installed on the Jenkins host by Ansible.
- The Jenkins EC2 instance profile grants ECR push permission, so no registry
  password is stored in Jenkins.
- The k3s API is reached over VPC peering using the `k8s-kubeconfig` credential.
- `Deploy` applies the namespace, ConfigMap, ECR imagePullSecret, the application
  Deployment/Service and `k8s/monitoring.yaml` (Prometheus + Grafana).
- `Verify` waits for the rollout, for both Pods to become Ready, then calls
  `/health` on the k3s NodePort with retries. It fails the build if the health
  check never succeeds.

## Failure gate discipline

If `mvn test` fails, the pipeline exits non-zero before `Docker Build`, so no
image is pushed and no deployment happens.

## Secrets

| Credential | Type | Purpose |
| :--- | :--- | :--- |
| `k8s-kubeconfig` | Secret file | Access to the k3s cluster |

Registry authentication uses the IAM role attached to the Jenkins instance.
Never put AWS keys or the kubeconfig in the repository.

The Secret file content must match `/home/ubuntu/.kube/config` from the k3s host
byte for byte (LF line endings, no BOM). A truncated or re-encoded file fails at
`Deploy` with `yaml: invalid leading UTF-8 octet`. Compare checksums if unsure:

```bash
sha256sum /home/ubuntu/.kube/config   # on the k3s host
```

```bash
sha256sum "$KUBECONFIG_FILE"          # inside the pipeline, or verify after upload
```

## Trigger

Configure a GitHub webhook to `http://<jenkins-public-ip>:8080/github-webhook/`
(content type `application/json`, event "Just the push event").

Because port 8080 is restricted in the security group, GitHub's own webhook
source ranges must also be allowed. Terraform manages them through the
`github_hook_cidrs` variable. Refresh the list from
`https://api.github.com/meta` (the `hooks` array) if deliveries fail with
"failed to connect to host", then run `terraform apply`.

If webhooks are blocked, use polling (`H/5 * * * *`) and document it.

## Initial setup

1. Open `terraform output jenkins_url`.
2. Read the initial admin password on the Jenkins host:
   `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`.
3. Install the suggested plugins plus Pipeline, Git and JUnit.
4. Create the `k8s-kubeconfig` secret file credential.
5. Create the pipeline job from `jenkins/Jenkinsfile`.
