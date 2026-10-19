# Continuous Integration and Continuous Delivery

## Definitions

- **Continuous Integration**: developers merge frequently; every change is
  compiled and tested automatically.
- **Continuous Delivery**: every passing build produces a deployable artifact.
- **Continuous Deployment**: every passing build is deployed automatically.
  DevOrbit uses this model for the `dev` environment.

## DevOrbit flow

```text
git push -> GitHub webhook -> Jenkins -> mvn test -> docker build
        -> Amazon ECR -> kubectl apply -> k3s rollout -> /health verification
```

A failed test blocks the image push and the deployment.

## Traceability

Every image is tagged with the Jenkins build number and short Git SHA:

```text
<account>.dkr.ecr.<region>.amazonaws.com/devorbit-app:<build>-<sha>
```

The running tag is visible with:

```bash
kubectl get deployment devorbit-app -n devorbit \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

## Rollback

```bash
kubectl rollout undo deployment/devorbit-app -n devorbit
```

## Environment strategy

One `dev` environment is enough for the academic scope. No production
environment is created, which keeps cost and complexity controlled.
