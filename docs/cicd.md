# Continuous Integration and Continuous Delivery

## Definitions

- **Continuous Integration**: developers merge frequently; every change is
  compiled and tested automatically.
- **Continuous Delivery**: every passing build produces a deployable artifact.
- **Continuous Deployment**: every passing build is deployed automatically.

DevOrbit uses continuous deployment for the single `dev` environment.

## DevOrbit flow

```text
git push -> GitHub webhook -> Jenkins (VPC-C)
         -> Maven compile + test (fail = stop)
         -> Docker image build
         -> Amazon ECR push
         -> kubectl apply on k3s (VPC-B)
         -> rolling update
         -> /health verification
         -> Grafana / CloudWatch
```

## Stages and gates

| Stage | What it proves | Failure consequence |
| :--- | :--- | :--- |
| Checkout | the build is tied to a commit | no build |
| Build | the code compiles on a clean host | no image |
| Test | the unit/controller tests pass | **no push, no deploy** |
| Package | a runnable JAR exists | no image |
| Docker Build | the multi-stage image builds reproducibly | no image |
| Docker Push | the artifact is in the private registry | no deploy |
| Deploy | Kubernetes accepted the new ReplicaSet | old version keeps serving |
| Verify | the rollout finished and `/health` answers | build marked failed |

The Test stage is the gate the viva looks for: a deliberately broken assertion
turns the build red before the image can be promoted.

## Traceability

Every image is tagged with the Jenkins build number and the short Git SHA:

```text
<account>.dkr.ecr.<region>.amazonaws.com/devorbit-app:<build>-<sha>
```

Examples: `7-d41d1e2`, `8-a9fdc4d`.

The running tag is visible with:

```bash
kubectl get deployment devorbit-app -n devorbit \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

and in `kubectl rollout history` because the Deploy stage writes a
`kubernetes.io/change-cause` annotation.

## Trigger

GitHub webhook -> `http://<jenkins-public-ip>:8080/github-webhook/`.

- The security group allows the GitHub `hooks` CIDR ranges in addition to the
  administrator CIDRs (`github_hook_cidrs` in `terraform/variables.tf`).
- Deliveries are visible in GitHub -> Settings -> Webhooks -> Recent Deliveries
  (expected `200`).
- Fallback if webhooks are unavailable: polling `H/5 * * * *`.

## Failure-gate rehearsal

```bash
git switch -c demo/failure-gate
# break one assertion in
# app/src/test/java/com/devorbit/IssueServiceTest.java
git add app/src/test/java/com/devorbit/IssueServiceTest.java
git commit -m "test: intentionally break test for pipeline demo"
git push origin demo/failure-gate
```

Expected: the Test stage fails, the pipeline stops, and ECR/deployment are
untouched. Then revert:

```bash
git revert --no-edit HEAD
git push origin demo/failure-gate
```

Tell the team before pushing: the webhook fires on every branch push, and
`disableConcurrentBuilds()` means the normal build waits.

## Rollback

```bash
kubectl rollout undo deployment/devorbit-app -n devorbit
kubectl rollout status deployment/devorbit-app -n devorbit
```

Kubernetes keeps the previous ReplicaSets, so rollback is immediate and does not
need a rebuild. The alternative is re-running the pipeline on the previous
commit, which produces a new image tag.

## Environment strategy

One `dev` environment is enough for the academic scope. No production
environment is created, which keeps cost and complexity controlled. All
configuration that differs between runs lives in the Jenkinsfile `environment`
block, the Kubernetes ConfigMap or the Terraform variables, never in the image.

## Evidence to capture for the report

- Jenkins build page with the eight green stages and stage timings.
- Console output showing the image tag and the `/health` response.
- Failed-test build (red Test stage) with no push/deploy.
- GitHub webhook delivery `200`.
- ECR image list with `<build>-<sha>` tags.
- `kubectl rollout history` and the running image.
