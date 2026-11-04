# DevOrbit — Teammates ke Tasks (Member 2 & Member 3)

> Ye document as-is teammates ko bhej sakte hain. Password/keys is file mein mat daalna — wo alag se privately dena.

## 0. Common Context (dono padhein)

Project ab **live aur working** hai. Tumhara kaam dobara banana nahi, balki **apna part own karna, verify karna, report/PPT banana, aur demo/viva dena** hai.

- Repo: `https://github.com/Utakarsh-Jain/DevOrbit` (branch `main`)
- App: `http://43.205.146.155:30080/` | UI: `http://43.205.146.155:30080/ui/`
- Jenkins: `http://3.7.217.234:8080` (stable Elastic IP; job: `devorbit-pipeline`)
- Grafana: `http://43.205.146.155:32000` (anonymous viewer)
- Prometheus: `http://43.205.146.155:30090`
- ECR: `366700733051.dkr.ecr.ap-south-1.amazonaws.com/devorbit-app`
- k3s node private IP: `10.20.1.70` (Public: `43.205.146.155`)
- Jenkins node private IP: `10.30.1.15` (Public Elastic IP: `3.7.217.234`)
- Bastion node private IP: `10.10.1.242` (Public: `13.232.181.154`)
- AWS Region: `ap-south-1` (Mumbai)

### 0.0 Quick Action Summary (Dono Teammates ke liye Immediate Checklist)

| Member | Focus Area | Live Demo Task | Report/PPT Section |
| :--- | :--- | :--- | :--- |
| **Utakarsh (Member 1)** | Cloud & Infra (VPC-A) | 3 VPCs, Peering, Terraform & Ansible execution | Architecture diagram, Network & Security, Terraform IaC |
| **Ashwin (Member 2)** | K8s & Docker (VPC-B) | `kubectl` Scaling (2->3) & Pod delete (Self-healing) | Dockerfile multi-stage, K8s Deployment & Service specs |
| **Gaurav (Member 3)** | CI/CD & Metrics (VPC-C) | 8-Stage Pipeline run + Broken test failure gate | Jenkins pipeline design, CloudWatch & Grafana monitoring |

#### ⚠️ Dono ke liye Strict Golden Rules:
1. **Naya VPC/Subnet/EC2 AWS Console se mat banao:** Sab kuch Terraform se shared account me already bana hua hai.
2. **`terraform apply` ya `destroy` mat chalao:** Terraform execution sirf Member 1 karega taaki state lock na tute.
3. **Secrets kabhi Git me mat daalo:** `.pem` key, passwords, AWS keys, kubeconfig kabhi commit nahi karne.
4. **Direct `main` branch par push nahi:** Apna feature branch banao (`feature/<naam>`), PR kholo, review ke baad merge karo.

### 0.1 Shared AWS Account Access (important)

Teeno members ke personal AWS accounts alag hain, lekin DevOrbit ka infrastructure **ek hi shared project account** me chalega:

- Project AWS account: `366700733051`
- Region: `ap-south-1` (Mumbai)
- Console sign-in URL: `https://366700733051.signin.aws.amazon.com/console`
- Account owner: Member 1. Member 2/3 ko apna alag **IAM user** milega.
- Root credentials, access keys, kubeconfig ya `.pem` kabhi share/store mat karo.

**Member 1 (one-time setup):**

1. IAM -> Users -> Create user (`ashwin-devorbit`, `gaurav-devorbit`).
2. Console access enable karo, **MFA required**, aur koi access key mat banao.
3. Neeche diya gaya custom policy attach karo (ya quick fallback ke liye `ReadOnlyAccess` + SSM statement).
4. Temporary password privately do; first login par change + MFA mandatory.

**Member 2/3:**

1. Apne IAM user se sign in karo, MFA enable karo. Root user use mat karo.
2. Apne personal AWS account me DevOrbit infrastructure apply **mat** karo.
3. VPC console (`ap-south-1`) me teeno VPC (`devorbit-dev-infra`, `devorbit-dev-app`, `devorbit-dev-ci`), subnets, route tables aur peering connections dikhengi.
4. EC2 -> Instance -> **Connect -> Session Manager** se shell lo (browser-based, no SSH key). `kubectl` demo commands isi session se chalao.

**Read-only console + Session Manager policy** (IAM -> Policies -> Create policy -> JSON):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyConsole",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*",
        "logs:Describe*",
        "logs:Get*",
        "logs:FilterLogEvents",
        "logs:StartQuery",
        "logs:GetQueryResults",
        "logs:StopQuery",
        "logs:ListTagsForResource",
        "logs:ListTagsLogGroup",
        "ecr:Describe*",
        "ecr:List*",
        "ecr:Get*",
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "sns:Get*",
        "sns:List*",
        "iam:GetRole",
        "iam:ListRoles",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:ListPolicies",
        "iam:ListAttachedRolePolicies",
        "iam:ListRolePolicies",
        "iam:ListInstanceProfiles",
        "iam:ListInstanceProfilesForRole",
        "tag:GetResources"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SessionManagerShell",
      "Effect": "Allow",
      "Action": [
        "ssm:DescribeInstanceInformation",
        "ssm:DescribeSessions",
        "ssm:GetConnectionStatus",
        "ssm:StartSession",
        "ssm:TerminateSession",
        "ssm:ResumeSession"
      ],
      "Resource": "*"
    }
  ]
}
```

**Network access:** Security groups IP-restricted hain. Apna public IP (`https://checkip.amazonaws.com`) Member 1 ko do. Wo `allowed_ssh_cidrs` aur `allowed_admin_cidrs` me add karke `terraform apply` karega. App UI (`:30080`) already public hai; Jenkins/Grafana/Prometheus sirf allowlisted IPs se khulenge.

### 0.2 VPC Ownership — naya VPC mat banao

Teeno VPC **already** Terraform se shared account me bane hue hain. Tumhe naya VPC, subnet, internet gateway, route table ya peering **banane ki zaroorat nahi** — na Console se, na apne personal AWS account me.

| VPC | CIDR | Owner | Kaam |
| :--- | :--- | :--- | :--- |
| `devorbit-dev-infra` | `10.10.0.0/16` | Member 1 | bastion, Ansible, network + peering |
| `devorbit-dev-app` | `10.20.0.0/16` | Member 2 | k3s, DevOrbit app, NodePort |
| `devorbit-dev-ci` | `10.30.0.0/16` | Member 3 | Jenkins, Docker build, ECR push |

- **Member 2:** `terraform/security_app.tf` + `terraform/compute_app.tf` me **VPC ke andar ke resources** edit karo. VPC khud `terraform/network.tf` (Member 1) banata hai.
- **Member 3:** `terraform/security_ci.tf` + `terraform/compute_ci.tf` + `jenkins/` edit karo. VPC khud `terraform/network.tf` banata hai.
- Console me existing VPC **dekh sakte ho**, lekin naya VPC/subnet/IGW/peering **create mat karo**. Naya VPC Terraform state se bahar ho jayega, peering/ECR/Jenkins se connect nahi hoga, aur duplicate cost banegi.
- Terraform me VPC ID hardcode mat karo; existing resources `terraform/network.tf` ke `aws_vpc.this["app"]` / `aws_vpc.this["ci"]` se reference hote hain.

### 0.3 Tumhara exact workflow (step-by-step)

**Aaj hi — access setup:**

1. IAM user se sign in karo + MFA enable karo.
2. VPC console (`ap-south-1`) -> **Your VPCs**: teeno VPC dikhni chahiye.
3. EC2 -> k3s/Jenkins instance -> **Connect -> Session Manager**: shell open hona chahiye.
4. Apna public IP (`https://checkip.amazonaws.com`) Member 1 ko bhejo, taaki Jenkins/Grafana allowlist me add ho.
5. Repo clone + apni branch:

```bash
git clone https://github.com/Utakarsh-Jain/DevOrbit.git
cd DevOrbit
git switch -c feature/<apna-naam>
git config user.name "<tumhara naam>"
git config user.email "<tumhara email>"
```

**Kaam karte waqt:**

1. Sirf apni owned files edit karo (Member 2/3 section me list hai).
2. Commit convention use karo: `feat:`, `fix:`, `docs:`, `infra:`, `ci:`, `k8s:`.
3. Branch push karo -> PR kholo -> dusre member se review -> merge.
4. Infra/Terraform change ho to **Member 1** ko bolo apply ke liye; khud apply mat karo.
5. Verify console + Session Manager + URLs se.
6. Screenshots, report section aur PPT slides apne part ke liye prepare karo.

**Kabhi mat karo:**

- Apne personal AWS account me DevOrbit VPC/infra banana.
- Shared account me console se duplicate VPC/subnet/IGW/peering banana.
- `terraform apply` / `destroy` chalana.
- Root credentials, access keys, kubeconfig ya `.pem` share/store karna.

## Golden Rules (dono ke liye)

1. **`terraform apply` / `destroy` / `init` mat chalao.** Sirf Member 1 chalayega (shared state + lock).
2. **Secrets kabhi mat commit karo:** kubeconfig, `.pem`, AWS keys, `terraform.tfvars`, Jenkins password, `.env`. Screenshot mein bhi password/keys hide karo.
3. **Jenkins credentials/job/password/webhook mat chhedo.** Verify karo, reconfigure nahi.
4. **Direct `main` pe bada change mat karo.** Branch banao (`feature/...`, `docs/...`), PR kholo, dusre member se review karwao, phir merge.
5. Commit convention: `feat:`, `fix:`, `docs:`, `test:`, `infra:`, `ci:`, `k8s:`.
6. Kisi aur ki file mat edit karo (ownership neeche di hai). Shared files (`variables.tf`, `README.md`, `docs/architecture.md`) sirf discussion ke baad.
7. Demo ke time `terraform destroy`, namespace delete, ya bulk pod delete **nahi**. Sirf ek pod delete karna hai (self-healing ke liye).
8. Force push / history rewrite nahi.
9. Naya tool/library/advanced feature mat add karo (EKS, Argo CD, Istio etc.) — project scope se bahar hai.
10. Rehearsal se pehle version bump ya test todna **team ko bata kar** karo, kyunki usse pipeline auto-trigger hoti hai.
11. **Apne personal AWS account me DevOrbit infra mat banao.** Sirf shared project account `366700733051` use karo.
12. **IAM user se login karo, MFA on rakho.** Root credentials aur access keys kabhi use/share mat karo.

---

# Member 2 — Ashwin (Containers & Kubernetes, VPC-B)

**Tumhara ownership:** `app/Dockerfile`, `app/.dockerignore`, `app/frontend/`, `k8s/`, `ansible/roles/k3s/`, `docs/docker.md`, `docs/kubernetes.md`, `terraform/security_app.tf` + `terraform/compute_app.tf` (changes sirf PR se; apply Member 1).

## A. Pehle apna code samjho (aaj)

1. `app/Dockerfile` padho — 3 stages:
   - `node:20-alpine` → React/Vite frontend build
   - `maven:3.9.9-eclipse-temurin-21-alpine` → JAR build
   - `eclipse-temurin:21-jre-alpine` → final runtime, user `devorbit` (uid/gid `1001`), `HEALTHCHECK` on `/health`, `EXPOSE 8080`
   - Samjho: multi-stage kyun? (chhota image, build tools runtime mein nahi, kam attack surface)
2. `app/.dockerignore` padho — `target`, `.git`, `.env`, `node_modules` etc. kyun exclude hain.
3. `k8s/` files padho:
   - `deployment.yaml`: 2 replicas, `RollingUpdate` (`maxSurge: 1`, `maxUnavailable: 0`), requests `100m/128Mi`, limits `500m/384Mi`, liveness `/health` (delay 25s, period 15s), readiness `/health` (delay 15s, period 10s), non-root `1001`, `imagePullSecret: ecr-registry-secret`
   - `service.yaml`: NodePort `30080` + `sessionAffinity: ClientIP`
   - `configmap.yaml`: `SERVER_PORT`, `APP_ENVIRONMENT`, logging level
   - `monitoring.yaml`: Prometheus (headless service `devorbit-app-metrics`, scrape `/actuator/prometheus`, 15s) + Grafana
4. `ansible/roles/k3s/tasks/main.yml` padho — k3s version pinned `v1.30.6+k3s1`, `--tls-san` private IP, kubeconfig `127.0.0.1` → private IP rewrite (taaki VPC-C se Jenkins API server reach kar sake), mode `0600`, `kubectl` symlink.

## B. Verify karo (commands Session Manager se)

```bash
# k3s host par
sudo k3s kubectl -n devorbit get deploy,pods,svc -o wide
sudo k3s kubectl -n devorbit get deploy devorbit-app -o yaml | grep -A5 -E "strategy|resources|Probe|securityContext"
sudo k3s kubectl -n devorbit get pods -o jsonpath="{.items[*].spec.containers[0].image}"; echo
sudo k3s kubectl -n devorbit describe pod <pod-name> | grep -A8 -E "Liveness|Readiness"
k3s --version
systemctl status k3s --no-pager
stat -c '%a %U:%G' /home/ubuntu/.kube/config
```

```bash
# Jenkins build log / ECR console
# Stage "Docker Build" aur "Docker Push" ka output dekho
# ECR mein image tag 7-d41d1e2 verify karo
```

## C. Demo mein tumhara segment (60–90 seconds)

Version bump ke baad rollout tum dikhaoge:

```bash
sudo k3s kubectl -n devorbit rollout status deploy/devorbit-app --timeout=180s
sudo k3s kubectl -n devorbit get pods -w
```

Scaling + self-healing (demo script ke steps 6–7):

```bash
sudo k3s kubectl -n devorbit scale deploy/devorbit-app --replicas=3
sudo k3s kubectl -n devorbit get pods -o wide
sudo k3s kubectl -n devorbit delete pod <pod-name>
sudo k3s kubectl -n devorbit get pods -w      # naya pod aayega
sudo k3s kubectl -n devorbit scale deploy/devorbit-app --replicas=2
```

Bolna kya hai: "Deployment 2 replicas chalata hai, rolling update zero downtime deta hai, aur pod delete hone par ReplicaSet turant naya pod bana deta hai."

## D. Deliverables (report + PPT + screenshots)

- **Report sections (~2–3 pages):**
  - Docker: multi-stage build, non-root, healthcheck, `.dockerignore`, image tagging.
  - Kubernetes: deployment/service/probes/resources, rolling update, self-healing, scaling, k3s choice.
  - Limitation: in-memory issue storage per pod + `sessionAffinity: ClientIP` (documented).
- **PPT: 3–4 slides** — Dockerfile stages diagram, k8s architecture (Deployment→Service→Pods), scaling/self-healing screenshots, k3s justification.
- **Screenshots:** `kubectl get pods/deploy/svc -o wide`, pod describe (probes), ECR image tag, scale 3 ka output, delete pod ke baad recreated pod, `docker build` stage log.
- `docs/docker.md` + `docs/kubernetes.md` review karo; command/output update karke PR bhejo.
- Version bump ke waqt `k8s/deployment.yaml` ka label `app.kubernetes.io/version: "1.1.0"` bhi update karna (chhota PR).

## E. Viva questions (ratlo)

- Multi-stage build kyun? → chhota runtime image, build tools final image mein nahi, kam CVEs.
- Non-root kyun? → container escape/privilege escalation risk kam.
- Readiness vs liveness? → readiness traffic control karti hai, liveness container restart karti hai.
- `maxUnavailable: 0` kyun? → rollout ke waqt zero downtime.
- NodePort kyun, LoadBalancer/Ingress nahi? → single-node academic k3s, cost aur simplicity; AWS ALB unnecessary.
- `sessionAffinity: ClientIP` kyun? → app state in-memory per pod hai, isliye same client same pod pe bhejna.
- k3s vs EKS? → cost/control-plane overhead kam, seekhne ke liye sufficient; production mein EKS/managed.
- Jenkins ko cluster kaise milta hai? → kubeconfig private IP `10.20.1.70` + VPC peering + SG 6443.

## F. Mat karna

- **Naya VPC/subnet/IGW/peering console se mat banao** — `terraform/network.tf` already sab banata hai.
- `docker build` apne laptop pe mat karo (workloads AWS pe hi rahenge).
- Deployment/namespace/service delete mat karo; sirf demo mein ek pod.
- `ecr-registry-secret` manually mat banao/delete karo — pipeline har deploy pe refresh karti hai.
- `k8s/monitoring.yaml` ke Prometheus/Grafana config ko bina discussion badalna mat.

---

# Member 3 — Gaurav (CI/CD & Monitoring, VPC-C)

**Tumhara ownership:** `jenkins/Jenkinsfile`, `ansible/roles/jenkins/`, `docs/jenkins.md`, `docs/cicd.md`, `docs/monitoring.md`, `docs/demo-script.md`, `terraform/security_ci.tf` + `compute_ci.tf` (changes sirf PR se; apply Member 1).

## A. Pehle apna code samjho (aaj)

1. `jenkins/Jenkinsfile` line-by-line:
   - 8 stages: Checkout → Build (`mvn clean compile`) → Test (`mvn test`, fail = pipeline stop) → Package (`mvn package -DskipTests`) → Docker Build → Docker Push (ECR via **IAM role**, no keys) → Deploy (kubeconfig credential, ECR pull secret refresh, `sed IMAGE_PLACEHOLDER`, manifests + monitoring apply) → Verify (`rollout status`, `kubectl wait`, 5× `/health` retries, fail par `exit 1`).
   - Env: `IMAGE_TAG = <build>-<git-sha7>`, `AWS_REGION=ap-south-1`, `K8S_NAMESPACE=devorbit`, `KUBECONFIG_CRED=k8s-kubeconfig`, `K3S_NODE_IP=10.20.1.70`.
   - `options`: build discarder 10, timeout 30 min, `disableConcurrentBuilds`.
2. `ansible/roles/jenkins/tasks/main.yml`: Jenkins LTS install, Java 21 JDK, kubectl 1.30.6, `jenkins` user docker group mein, service enabled.
3. Credentials: `k8s-kubeconfig` (Secret file). Ye `/home/ubuntu/.kube/config` ke **byte-for-byte** same hona chahiye. `SecretBytes.fromBytes` se banaya gaya tha (string conversion bytes corrupt kar deta hai). Isko UI mein copy-paste se dobara mat banao.
4. `docs/jenkins.md`, `docs/cicd.md`, `docs/monitoring.md`, `docs/demo-script.md` padho.

## B. Verify karo

```bash
# Jenkins host par
jenkins --version
sudo systemctl status jenkins --no-pager
sudo -u jenkins docker ps
sudo -u jenkins kubectl version --client
```

- Jenkins UI → Manage Jenkins → Plugins: Git, GitHub, Pipeline, JUnit, Credentials Binding, Docker Pipeline installed hain — list docs mein likho.
- Jenkins UI → Credentials → System → Global: `k8s-kubeconfig` present (content mat dikhao).
- Job `devorbit-pipeline` → Configure: SCM repo URL, `Script Path = jenkins/Jenkinsfile`. Trigger UI me manually set mat karo: `Jenkinsfile` me `githubPush()` + `pollSCM('H/5 * * * *')` declared hai, aur ek manual build ke baad Jenkins khud hook trigger register karta hai.
- Build #7 kholo → 8 stages green, timestamps, image tag, console output.
- GitHub → repo Settings → Webhooks → Recent Deliveries: last delivery **200**, aur ek trivial push par job khud build ho (manually start nahi).
- CloudWatch console: dashboard `devorbit-dev-dashboard`, alarms `devorbit-dev-*-high-cpu`, log group `/devorbit/dev/system`.
- Grafana: dashboard folder `DevOrbit` → `DevOrbit App Metrics`; Prometheus → Status → Targets: `devorbit-app` ke 2 targets **UP**.

## C. Failure-gate rehearsal (important, demo mein dikhana hai)

```bash
git switch -c demo/failure-gate
# app/src/test/java/com/devorbit/IssueServiceTest.java mein ek assertion deliberately todo
# (e.g. expected value galat karo)
git add app/src/test/java/com/devorbit/IssueServiceTest.java
git commit -m "test: intentionally break test for pipeline demo"
git push origin demo/failure-gate
```

- Jenkins mein Test stage **FAIL** hona chahiye; Docker Push/Deploy nahi chalne chahiye.
- Phir revert:

```bash
git revert --no-edit HEAD
git push origin demo/failure-gate
```

Note: webhook kisi bhi branch push par chalta hai; agar branch build trigger na ho to `main` par karke turant revert karo (team ko pehle batao). Demo ke liye pehle practice karo.

## D. Demo mein tumhara segment

1. Version bump ka pipeline narration: `app/pom.xml` `1.0.0` → `1.1.0`, commit + push, Jenkins khud trigger, 8 stages, ECR tag.
2. Failure gate dikhana (optional but high-value): test todo → pipeline Test pe fail → "deployment promote nahi hui".
3. Webhook proof: GitHub Recent Deliveries 200.
4. Monitoring: CloudWatch dashboard/alarm → Grafana request rate, p95 latency, JVM heap, 2 Prometheus targets.
5. Rollback ka answer (agar poocha jaye): `kubectl rollout undo deployment/devorbit-app -n devorbit` ya previous image tag redeploy.

## E. Deliverables (report + PPT + screenshots)

- **Report sections (~2–3 pages):** CI vs CD, Jenkins pipeline stages + diagram, ECR tagging strategy, webhook (incl. SG `github_hook_cidrs` troubleshooting), failure behavior, monitoring split (CloudWatch = infra, Prometheus/Grafana = app), security (IAM role, credentials).
- **PPT: 3–4 slides** — pipeline flow, build 7 stages screenshot, failure gate, monitoring dashboards.
- **Screenshots:** Jenkins build #7 stages, console tail, GitHub webhook 200 delivery, failed test build, CloudWatch dashboard/alarm, Grafana dashboard, Prometheus targets.
- `docs/cicd.md` mein actual pipeline diagram + build timing update karo; `docs/jenkins.md` mein plugin list + rollback section add karo (PR).
- **Monitoring gap task:** CloudWatch dashboard ka text memory/disk claim karta hai lekin widgets sirf CPU/network hain. `terraform/monitoring.tf` ke liye CWAgent (`mem_used_percent`, `disk_used_percent`) widgets ka PR banao **ya** text ko reality ke according fix karo; apply Member 1 karega.
- Alarm email abhi configured nahi (`alarm_email` empty) — demo ke liye decide karo: metrics-only dikhana hai ya email subscription chahiye (Member 1 apply karega).

## F. Viva questions (ratlo)

- CI vs CD? → CI = build+test har commit; CD = tested artifact ko automatically deploy.
- Jenkins kyun, GitHub Actions nahi? → self-hosted Jenkins EC2 pe, full control, academic requirement, plugin ecosystem.
- ECR kyun? → AWS-native, IAM integration, private registry.
- Tag `<build>-<sha>` kyun? → har release identifiable + traceable to commit.
- AWS keys kahan hain? → kahin nahi; EC2 IAM role se ECR auth.
- Test fail hone par kya hota hai? → pipeline Test stage pe rukti hai; image push/deploy nahi hota.
- Webhook kaise kaam karta hai? → GitHub → `:8080/github-webhook/`; SG mein GitHub hook CIDRs allow; delivery 200.
- "failed to connect to host" ka fix? → `github_hook_cidrs` refresh (`api.github.com/meta` → `hooks`) + Member 1 apply.
- Rollback kaise? → `kubectl rollout undo` ya previous tag redeploy.
- CloudWatch vs Prometheus? → infra/EC2/logs vs application JVM/HTTP metrics; complementary.

## G. Mat karna

- **Naya VPC/subnet/IGW/peering console se mat banao** — `terraform/network.tf` already sab banata hai.
- Jenkins password/credentials/job config/webhook mat badlo (password sirf Member 1 ke paas, privately).
- `terraform apply` mat karo; SG/CI infra change PR se, apply Member 1.
- Pipeline ke `Verify` ko weak mat karo (health retries/fail exit zaroori hai).
- Kubeconfig ya `terraform.tfstate` kabhi repo/screenshot mein mat lao.
- Demo ke beech mein doosra build trigger mat karo (`disableConcurrentBuilds` hai, par confusion avoid).

---

## Shared Demo Sequence (ek saath rehearse karo)

1. **Member 1:** Architecture + Terraform/Ansible + CloudWatch (2 min)
2. **Member 3:** Version bump push → Jenkins 8 stages live (3 min)
3. **Member 2:** Rollout status → app pe naya version → scale 3 → pod delete → self-heal (2 min)
4. **Member 3:** Failure gate (test todo → fail) + Grafana/Prometheus (2 min)
5. **Member 1:** Cleanup/limitations + Q&A

**Timeline suggestion:** Aaj code reading + verification + screenshots → kal report sections + PPT PR → parso full rehearsal (2 runs) → final demo.

**Har member ka Definition of Done:** apna section samajh liya, commands khud chala liye, screenshots le liye, report+PPT section PR mein daala, 8–10 viva questions ke answers ready, aur ek green pipeline / healthy cluster ka proof dikha diya.
