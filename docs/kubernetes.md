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
k8s/namespace.yaml   devorbit namespace
k8s/configmap.yaml   environment variables
k8s/deployment.yaml  2 replicas, rolling update, /health probes, resources
k8s/service.yaml     NodePort 30080, sessionAffinity ClientIP
```

## Operational commands (run on the k3s host)

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods,deployment,svc -n devorbit -o wide

# Scaling
kubectl scale deployment/devorbit-app --replicas=3 -n devorbit

# Self-healing
kubectl get pods -n devorbit
kubectl delete pod <pod-name> -n devorbit
kubectl get pods -n devorbit -w
```

## Notes for the viva

- The Deployment keeps 2 replicas; scaling to 3 shows elasticity, deleting a
  Pod shows self-healing, and changing the image shows a zero-downtime rolling
  update.
- Storage is in-memory and per Pod. `sessionAffinity: ClientIP` keeps a client
  on one Pod; add PostgreSQL later if shared state is required.
