# DevOrbit Jenkins CI/CD

Jenkins runs on the dedicated EC2 host in **VPC-C** and talks to the k3s
cluster in **VPC-B** over VPC peering. Owner: Member 3.

```text
Checkout -> Build -> Test -> Package -> Docker Build -> Docker Push (ECR) -> Deploy (k3s) -> Verify
```

- **Build/Test/Package** use Maven 3.9.9 with Java 21, installed by the
  `common` and `jenkins` Ansible roles.
- **Docker Build** produces one multi-stage image containing the React UI and
  the Spring Boot JAR.
- **Docker Push** authenticates to Amazon ECR using the EC2 instance IAM role
  (no stored registry password).
- **Deploy** refreshes the `ecr-registry-secret` pull secret and applies the
  manifests with the new image tag.
- **Verify** waits for the rollout and probes `/health` on the NodePort.
- A failing `mvn test` aborts the pipeline before any image is pushed or
  deployed.

The image tag is `<Jenkins build number>-<short Git SHA>`, for example
`7-d41d1e2`, so every release is traceable to a commit.

## Jenkins host configuration

`ansible/roles/jenkins/` installs Jenkins LTS, Java 21, Maven 3.9.9, kubectl,
adds the `jenkins` user to the `docker` group, sets the JVM heap and installs
the required plugins. See `ansible/roles/jenkins/defaults/main.yml` for the
plugin list and `docs/jenkins.md` for details.

Credentials required (Manage Jenkins -> Credentials):

| ID | Type | Purpose |
|---|---|---|
| `k8s-kubeconfig` | Secret file | k3s kubeconfig from `/home/ubuntu/.kube/config` on the k3s host |

No registry credential is needed: the Jenkins EC2 instance profile grants ECR
access (`AmazonEC2ContainerRegistryPowerUser` in `terraform/iam.tf`).

Job settings:

- Pipeline script from SCM, pointing at this repository and `jenkins/Jenkinsfile`.
- Script Path: `jenkins/Jenkinsfile`.
- Build trigger: do not set it only in the UI. `Jenkinsfile` declares
  `githubPush()` and the `pollSCM('H/5 * * * *')` fallback. Run the job once
  manually so Jenkins registers the webhook trigger, then confirm the
  **GitHub hook trigger for GITScm polling** checkbox is ticked.

## Environment values

Edit the `environment` block in the `Jenkinsfile` when the region or ECR
repository changes:

| Variable | Meaning |
|---|---|
| `AWS_REGION` | Region that hosts the ECR repository |
| `ECR_REPOSITORY` | ECR repository name (`devorbit-app`) |
| `K3S_NODE_IP` | k3s host private IP, enables the external `/health` check |
| `KUBECONFIG_CRED` | Jenkins credential ID for the k3s kubeconfig |

## Rollback

```bash
kubectl rollout undo deployment/devorbit-app -n devorbit
```

The previous ReplicaSet is kept by Kubernetes, so rollback does not require a
rebuild.
