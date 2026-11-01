# Jenkins CI/CD Automation Guide

Member 3 (Gaurav) owns this area: the Jenkins host in **VPC-C**, the
`jenkins/Jenkinsfile` pipeline, the `jenkins` Ansible role, ECR push and the
deployment verification.

## Pipeline architecture

```text
Checkout -> Build -> Test -> Package -> Docker Build -> Docker Push (ECR) -> Deploy (k3s) -> Verify
```

| # | Stage | Command / action | Artifact |
| :--- | :--- | :--- | :--- |
| 1 | Checkout | `checkout scm` + `git rev-parse --short=7 HEAD` | image tag `<build>-<sha>` |
| 2 | Build | `mvn -B -ntp clean compile` | compiled classes |
| 3 | Test | `mvn -B -ntp test` (JUnit results published) | Surefire reports |
| 4 | Package | `mvn -B -ntp package -DskipTests` | `app/target/devorbit.jar` |
| 5 | Docker Build | `docker build -t devorbit-app:<tag> .` | local image |
| 6 | Docker Push | `aws ecr get-login-password` + `docker push` | ECR image |
| 7 | Deploy | `kubectl apply` + ECR pull secret + image substitution | new ReplicaSet |
| 8 | Verify | `kubectl rollout status`, `kubectl wait`, `/health` retries | build result |

The pipeline is declarative, runs on the Jenkins EC2 host, and uses:

| Option | Value | Reason |
| :--- | :--- | :--- |
| `timestamps()` | on | every console line is timed for the report |
| `buildDiscarder` | keep 10 | limits disk usage on the Jenkins host |
| `timeout` | 30 minutes | a hung Docker/Kubernetes call cannot block the agent forever |
| `disableConcurrentBuilds` | on | one deployment at a time on a single k3s node |

## Jenkins host bootstrap (Ansible role)

`ansible/roles/jenkins/` installs and configures:

- Jenkins LTS from the official Debian repository.
- OpenJDK 21 JDK from the `common` role.
- Apache Maven **3.9.9** in `/opt` with `/usr/local/bin/mvn` on the PATH.
- `kubectl` v1.30.6 in `/usr/local/bin`.
- Docker Engine from the `docker` role; the `jenkins` user is added to the
  `docker` group.
- Jenkins JVM heap of `-Xms512m -Xmx1536m` in `/etc/default/jenkins` so the
  t3.medium host can build and deploy without swapping.
- The plugin set required by the Jenkinsfile (installed with
  `jenkins-plugin-cli`).

The role is idempotent: the plugin task is skipped once
`/var/lib/jenkins/plugins/workflow-aggregator` exists. Change the plugin list in
`ansible/roles/jenkins/defaults/main.yml` and delete that directory if you need
to reinstall.

### Plugins

| Plugin | Used by |
| :--- | :--- |
| `git`, `github`, `github-branch-source` | checkout and webhook trigger |
| `workflow-aggregator`, `pipeline-stage-view` | declarative pipeline and stage view |
| `junit` | Test stage result publishing |
| `credentials-binding` | `k8s-kubeconfig` secret file |
| `docker-workflow` | Docker steps and future Docker pipeline syntax |
| `timestamper` | `timestamps()` option |
| `ws-cleanup` | `cleanWs()` at the start of every build |

## Credentials

| Credential | Type | Purpose |
| :--- | :--- | :--- |
| `k8s-kubeconfig` | Secret file | Access to the k3s cluster in VPC-B |

Registry authentication uses the IAM role attached to the Jenkins instance
(`devorbit-dev-jenkins-role`), which has `AmazonEC2ContainerRegistryPowerUser`.
No AWS keys or registry passwords are stored in Jenkins or in Git.

The Secret file content must match `/home/ubuntu/.kube/config` on the k3s host
byte for byte (LF line endings, no BOM). A truncated or re-encoded file fails at
`Deploy` with `yaml: invalid leading UTF-8 octet`. Compare checksums if unsure:

```bash
sha256sum /home/ubuntu/.kube/config          # on the k3s host
sha256sum "$KUBECONFIG_FILE"                 # inside the pipeline workspace
```

## One-time job setup

The job definition contains no secret, but the credential does, so the first
setup is done in the UI:

1. Open `terraform output -raw jenkins_url`.
2. Read the initial admin password on the host:
   `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`.
3. Install the suggested plugins (the role already installs the pipeline set).
4. Create the `k8s-kubeconfig` secret file credential from the k3s host.
5. Create a Pipeline job named `devorbit-pipeline`:
   - Definition: **Pipeline script from SCM**
   - SCM: this GitHub repository
   - Script Path: `jenkins/Jenkinsfile`
   - Build trigger: **GitHub hook trigger for GITScm polling**
6. Run the job once and confirm all eight stages are green.

## Trigger

GitHub webhook to `http://<jenkins-public-ip>:8080/github-webhook/` with content
type `application/json` and the push event.

Port 8080 is restricted in the security group, so GitHub's webhook source ranges
must also be allowed. Terraform manages them through `github_hook_cidrs`
(`terraform/security_ci.tf`). Refresh the list from
`https://api.github.com/meta` (the `hooks` array) if deliveries fail with
"failed to connect to host", then have Member 1 run `terraform apply`.

If webhooks cannot be configured, the fallback is polling: `H/5 * * * *`.
Document whichever trigger is actually enabled.

## Failure behaviour

- A failed `mvn test` exits the Test stage with a non-zero status, so
  `Docker Build`, `Docker Push` and `Deploy` never run.
- A failed rollout makes `kubectl rollout status` exit non-zero, so the Verify
  stage fails the build. The previous ReplicaSet keeps serving traffic.
- `disableConcurrentBuilds()` prevents two deploys racing on the single k3s node.

## Verification

```bash
# On the Jenkins host
jenkins --version
mvn -version
docker --version
kubectl version --client
sudo systemctl status jenkins --no-pager
sudo -u jenkins docker ps
```

In the Jenkins UI:

- Build history shows the eight stages and the `timestamps` column.
- Console output ends with the deployed image reference.
- Credentials page lists `k8s-kubeconfig` (never open or screenshot its content).

In the ECR console, the repository `devorbit-app` contains the tag
`<build>-<sha>` from the latest run.

## Rollback

```bash
kubectl rollout undo deployment/devorbit-app -n devorbit
kubectl rollout status deployment/devorbit-app -n devorbit
```

Alternative: re-run the pipeline on the previous commit, or deploy the previous
ECR tag with `kubectl set image`.

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `no basic auth credentials` on push | instance profile missing ECR permission | check the Jenkins IAM role attachments |
| `ImagePullBackOff` | expired `ecr-registry-secret` | re-run Deploy (it refreshes the token) |
| `yaml: invalid leading UTF-8 octet` | kubeconfig credential corrupted | re-upload the file as a Secret file |
| Verify fails with curl timeouts | SG does not allow Jenkins VPC on 30080 | check `terraform/security_app.tf` |
| GitHub delivery `failed to connect to host` | `github_hook_cidrs` outdated | refresh from `api.github.com/meta` |
| Job hangs in Docker Build | no disk space on the Jenkins root volume | `docker system prune -af`, check the disk alarm |
