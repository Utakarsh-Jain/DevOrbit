# DevOrbit Jenkins CI/CD

Jenkins runs on the dedicated EC2 host in **VPC-C** and talks to the k3s
cluster in **VPC-B** over VPC peering.

```text
Checkout -> Build -> Test -> Package -> Docker Build -> Docker Push (ECR) -> Deploy (k3s) -> Verify
```

- **Build/Test/Package** use Maven, installed by the `common` Ansible role.
- **Docker Build** produces one multi-stage image containing the React UI and
  the Spring Boot JAR.
- **Docker Push** authenticates to Amazon ECR using the EC2 instance IAM role
  (no stored registry password).
- **Deploy** creates the `ecr-registry-secret` image pull secret and applies
  the manifests with the new image tag.
- **Verify** waits for the rollout and probes `/health` on the NodePort.

A failing `mvn test` aborts the pipeline before any image is pushed or deployed.

## Jenkins configuration

Credentials required (Manage Jenkins -> Credentials):

| ID | Type | Purpose |
|---|---|---|
| `k8s-kubeconfig` | Secret file | k3s kubeconfig from `/home/ubuntu/.kube/config` on the k3s host |

No registry credential is needed: the Jenkins EC2 instance profile grants ECR
access. See `terraform/compute.tf`.

Job settings:

- Pipeline script from SCM, pointing at this repository and `jenkins/Jenkinsfile`.
- Build trigger: GitHub webhook, or polling as a fallback:
  `H/5 * * * *`.

## Environment values

Edit the `environment` block in the `Jenkinsfile` when the region or ECR
repository changes:

| Variable | Meaning |
|---|---|
| `AWS_REGION` | Region that hosts the ECR repository |
| `ECR_REPOSITORY` | ECR repository name (`devorbit-app`) |
| `K3S_NODE_IP` | k3s host private IP, enables the external `/health` check |
