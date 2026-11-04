# Kubernetes Orchestration Guide

## Key concepts

- **Cluster**: control plane plus nodes running containerized workloads.
- **Pod**: smallest deployable unit, one or more containers.
- **Deployment**: manages replicas, rolling updates and rollbacks.
- **Service**: stable virtual IP and load balancing to Pods; the DevOrbit
  service is a `NodePort` on port 30080.
- **ConfigMap**: externalized configuration (`devorbit-config`).
- **imagePullSecret**: credentials k3s uses to pull images from Amazon ECR
  (`ecr-registry-secret`, created by the Jenkins pipeline).

## DevOrbit manifests

```text
k8s/namespace.yaml    devorbit namespace
k8s/configmap.yaml    environment variables
k8s/deployment.yaml   2 replicas, rolling update, /health probes, resources
k8s/service.yaml      NodePort 30080, sessionAffinity ClientIP
k8s/monitoring.yaml   Prometheus (NodePort 30090) + Grafana (NodePort 32000)
```

The Jenkins `Deploy` stage applies `monitoring.yaml` together with the
application manifests, so an environment created from scratch also gets the
metrics stack.

## Operational commands (run on the k3s host)

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/monitoring.yaml

kubectl get pods,deployment,svc -n devorbit -o wide

# Scaling
kubectl scale deployment/devorbit-app --replicas=3 -n devorbit

# Self-healing
kubectl get pods -n devorbit
kubectl delete pod <pod-name> -n devorbit
kubectl get pods -n devorbit -w
```

## ECR pull-secret auto-refresh

New Pods pull the image from private ECR with `imagePullSecrets: ecr-registry-secret`.
ECR login tokens expire after **12 hours**, and Jenkins refreshes the secret only
during a deploy. Without a refresh, any new Pod (scale-up or self-healing) fails
with `ErrImagePull` / `403 Forbidden` once the last deploy is older than 12 hours.
This was found during rehearsal on 1 Nov 2026.

The k3s role installs `/usr/local/bin/refresh-ecr-secret.sh` and a root cron job
(`/etc/cron.d/refresh-ecr-secret`) that renews the secret every 6 hours using the
app node IAM role (repository-scoped ECR read policy). No AWS keys are stored.

```bash
# Check the job and its last runs
cat /etc/cron.d/refresh-ecr-secret
sudo tail /var/log/refresh-ecr-secret.log

# Refresh manually
sudo /usr/local/bin/refresh-ecr-secret.sh
```

## Notes for the viva

- The Deployment keeps 2 replicas; scaling to 3 shows elasticity, deleting a
  Pod shows self-healing, and changing the image shows a zero-downtime rolling
  update.
- Storage is in-memory and per Pod. `sessionAffinity: ClientIP` keeps a client
  on one Pod; add PostgreSQL later if shared state is required.
