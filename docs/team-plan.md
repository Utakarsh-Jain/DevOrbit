# DevOrbit Team Plan (3 Members, 3 VPCs)

Every member owns a VPC and a slice of the pipeline. All three VPCs are joined
by a full-mesh peering so the components can talk to each other.

Shared first steps (do these together, once):

1. Create the GitHub repository and the branch-protection rule on `main`.
2. Run Terraform from AWS CloudShell (Member 1 drives, all watch).
3. Agree the naming: `devorbit`, region, and the ECR repository `devorbit-app`.

---

## Member 1 - Infrastructure and Cloud (VPC-A 10.10.0.0/16)

Owns the foundation everyone else depends on.

- Terraform: VPCs, subnets, internet gateways, route tables, full-mesh peering.
- IAM roles and instance profiles: base, Jenkins (ECR power user), app (ECR read only).
- Security groups: SSH from your IP, Jenkins 8080, application NodePort 30080, cross-VPC rules.
- EC2 instances: bastion (t3.micro), Jenkins (t3.medium), app/k3s (t3.medium), encrypted gp3, IMDSv2.
- CloudWatch: SNS topic, CPU alarms, dashboard, log group.
- Ansible: the `common` and `cloudwatch` roles and the inventory.
- Runs `terraform fmt/validate/plan/apply` and owns the remote state bucket.

Deliverables: working `terraform/`, `ansible/roles/common`, `ansible/roles/cloudwatch`,
`docs/aws.md`, `docs/terraform.md`.

Proof for the viva: `terraform output`, the CloudWatch dashboard, a CPU alarm.

---

## Member 2 - Containers and Kubernetes (VPC-B 10.20.0.0/16)

Owns how the application is packaged and run.

- `app/Dockerfile`: 3-stage build (frontend, Maven, JRE) and `.dockerignore`.
- `ansible/roles/k3s`: install the single-node cluster and publish the kubeconfig.
- `k8s/`: namespace, configmap, deployment (2 replicas, rolling update, probes,
  resources, imagePullSecret `ecr-registry-secret`), NodePort service.
- Demonstrates scaling (2 -> 3 replicas) and self-healing (`kubectl delete pod`).
- Validates the image runs as a non-root user and exposes `/health`.

Deliverables: `app/Dockerfile`, `k8s/`, `ansible/roles/k3s`,
`docs/docker.md`, `docs/kubernetes.md`.

Proof for the viva: `kubectl get pods`, a scale-up, a deleted pod that comes back,
a rolling update with zero downtime.

---

## Member 3 - CI/CD and Observability (VPC-C 10.30.0.0/16)

Owns automation from commit to running deployment.

- `ansible/roles/jenkins`: install Jenkins LTS and grant Docker access.
- Jenkins credentials: `k8s-kubeconfig` secret file.
- `jenkins/Jenkinsfile`: Checkout -> Build -> Test -> Package -> Docker Build ->
  Docker Push (ECR, IAM role) -> Deploy (k3s) -> Verify (`/health`).
- GitHub webhook trigger (or polling fallback) and the failing-test demo.
- Deployment verification and the CloudWatch dashboard review.
- Optional: presentation deck and the demo script.

Deliverables: `jenkins/Jenkinsfile`, `ansible/roles/jenkins`,
`docs/jenkins.md`, `docs/cicd.md`, `docs/monitoring.md`, `docs/demo-script.md`.

Proof for the viva: a green pipeline, a deliberately broken test that fails the
build, and the new version appearing at the application URL.

---

## Shared responsibilities

- Code review on every pull request.
- Keep secrets out of Git: use `.env.example`, Jenkins credentials and IAM roles.
- Keep the README, architecture doc and demo script current after each change.
- Run `mvn test` in CI before merging.
- Agree the commit convention (`feat:`, `fix:`, `infra:`, `ci:`, `docs:`).

## Suggested timeline

| Week | Focus |
| :--- | :--- |
| 1 | Repo bootstrap, application API, tests, Dockerfile |
| 2 | Terraform (3 VPCs), Ansible baseline, first EC2 hosts |
| 3 | k3s, Kubernetes manifests, Jenkins pipeline, ECR push |
| 4 | Monitoring, hardening, documentation, demo rehearsal |
