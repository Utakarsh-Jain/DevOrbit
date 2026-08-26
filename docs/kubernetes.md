# Kubernetes Orchestration Guide

## Key Concepts
- **Cluster**: Set of compute nodes running containerized workloads managed by a control plane.
- **Pod**: Smallest deployable unit containing one or more tightly coupled containers.
- **Deployment**: Declarative definition managing Pod replicas, rolling updates, and rollbacks.
- **Service**: Stable network endpoint and load balancer routing traffic to Pods via label selectors.
- **ConfigMap**: Key-value pairs for externalizing application configuration.

## Operational Commands
```bash
# Apply cluster resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify state
kubectl get pods,deployment,svc -n devorbit -o wide

# Horizontal Pod Scaling Demonstration
kubectl scale deployment/devorbit-app --replicas=3 -n devorbit

# Self-Healing Demonstration
# Delete a running pod and observe Kubernetes immediately recreate it
kubectl get pods -n devorbit
kubectl delete pod <pod-name> -n devorbit
kubectl get pods -n devorbit -w
```
