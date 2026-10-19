# DevOrbit Troubleshooting Guide

## 1. Pods in `CrashLoopBackOff` or `Pending`

```bash
kubectl describe pod <pod-name> -n devorbit
kubectl logs <pod-name> -n devorbit
```

Likely causes: missing `ecr-registry-secret`, an image tag that does not exist
in ECR, or a memory limit that is too low.

## 2. Image pull fails with `401 Unauthorized`

The ECR token expires. The Jenkins pipeline recreates the secret on every
deploy:

```bash
kubectl create secret docker-registry ecr-registry-secret \
  --docker-server="<account>.dkr.ecr.<region>.amazonaws.com" \
  --docker-username=AWS \
  --docker-password="$(aws ecr get-login-password --region <region>)" \
  -n devorbit --dry-run=client -o yaml | kubectl apply -f -
```

## 3. Jenkins fails at the Test stage

Reproduce on the Jenkins host (not a laptop):

```bash
cd /var/lib/jenkins/workspace/<job>
cd app && mvn -B test
```

A failing test is the correct behaviour: it must block the deployment.

## 4. Jenkins cannot reach the k3s API

- Confirm VPC peering is `active` and the routes exist.
- Confirm the k3s security group allows 6443 from VPC-C.
- Confirm the kubeconfig uses the k3s private IP, not `127.0.0.1`.

```bash
kubectl --kubeconfig /path/to/config get nodes
```

## 5. Ansible cannot connect

- Confirm port 22 is open from the Ansible source (`allowed_ssh_cidr`).
- Confirm the key pair matches `ssh_public_key` in `terraform.tfvars`.
- Confirm `ansible_host` values match `terraform output` (instances are
  recreated when replaced).

## 6. Terraform apply fails

- Check AWS credentials in CloudShell with `aws sts get-caller-identity`.
- Confirm the state bucket and DynamoDB lock table exist and are in the same
  region.
- Do not run two `apply` operations at once; the lock prevents it.

## 7. Application responds but the UI is blank

The UI is built into the image at `/ui/`. Check that the image was built from
the current Dockerfile and that `/ui/` is requested with the trailing slash.
