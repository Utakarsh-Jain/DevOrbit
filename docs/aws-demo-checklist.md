# AWS Console Demo Checklist

Everything DevOrbit does is visible in the AWS Console and nothing runs on a
laptop. Use this checklist for the faculty demonstration.

## 0. Build the environment (AWS CloudShell only)

Open **AWS Console -> CloudShell** in the target region and run:

```bash
git clone https://github.com/Utakarsh-Jain/DevOrbit.git
cd DevOrbit/terraform

# Create a key pair inside CloudShell (no laptop involved)
ssh-keygen -t ed25519 -f ~/.ssh/devorbit-key -N ""
cat ~/.ssh/devorbit-key.pub

# Remote state (once)
cd bootstrap
terraform init
terraform apply -var="state_bucket_name=devorbit-tfstate-<unique-suffix>"
cd ..

# Variables
cp terraform.tfvars.example terraform.tfvars
# set ssh_public_key to the public key above
# set allowed_ssh_cidr and allowed_admin_cidr to your current public IP/32
# set alarm_email to your email
nano terraform.tfvars

# Review, then apply
terraform init
terraform fmt -check
terraform validate
terraform plan -out=devorbit.tfplan
terraform apply devorbit.tfplan
terraform output
```

Then configure the hosts from CloudShell:

```bash
cd ../ansible
ansible-galaxy collection install community.general ansible.posix
cp inventory/hosts.ini.example inventory/hosts.ini
# paste terraform output ansible_inventory into hosts.ini
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

## 1. Show the network (VPC)

Console -> **VPC**:

- [ ] **Your VPCs**: `devorbit-dev-infra`, `devorbit-dev-app`, `devorbit-dev-ci`
- [ ] **Peering connections**: 3 connections, all `Active`
- [ ] **Subnets**: one public subnet per VPC
- [ ] **Route tables**: each has `0.0.0.0/0 -> igw` and peer routes
- [ ] **Security groups**: infra, app, ci

Talking point: one VPC per team member, joined by full-mesh peering, so the
Jenkins host can reach the k3s API privately.

## 2. Show the compute (EC2)

Console -> **EC2 -> Instances**:

- [ ] 3 instances: `bastion`, `jenkins`, `k3s`
- [ ] Each has a public IP, encrypted EBS volume, IMDSv2 required
- [ ] **Connect -> Session Manager** works without an SSH key
- [ ] **Security** tab shows the instance IAM role

Talking point: all workloads run here; the laptop only opens the console.

## 3. Show IAM

Console -> **IAM -> Roles**:

- [ ] `devorbit-...-base` (SSM + CloudWatch)
- [ ] `devorbit-...-jenkins` (ECR power user)
- [ ] `devorbit-...-app` (ECR read only)

Talking point: least privilege and no stored registry password.

## 4. Show the registry (ECR)

Console -> **Elastic Container Registry -> Repositories**:

- [ ] `devorbit-app`
- [ ] Image tags include `<build>-<sha>` after the first pipeline run
- [ ] Lifecycle policy keeps the repository small

## 5. Show Kubernetes (via Session Manager on the k3s host)

EC2 -> select `k3s` -> **Connect -> Session Manager**, then:

```bash
sudo kubectl get nodes -o wide
sudo kubectl get pods,svc -n devorbit
sudo kubectl get deployment devorbit-app -n devorbit \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Demo scaling and self-healing:

```bash
sudo kubectl scale deployment/devorbit-app --replicas=3 -n devorbit
sudo kubectl get pods -n devorbit -w
sudo kubectl delete pod <pod-name> -n devorbit
```

## 6. Show CI/CD (Jenkins)

Open `terraform output jenkins_url` (port 8080):

- [ ] Pipeline stages: Checkout, Build, Test, Package, Docker Build,
      Docker Push, Deploy, Verify
- [ ] A green build and the image tag
- [ ] Failure gate: break a test, push, show the pipeline stop before push

## 7. Show the application (browser)

- [ ] `terraform output application_url` -> JSON with version and status
- [ ] `terraform output application_frontend_url` -> React UI
- [ ] `GET /health` -> `{"status":"UP"}`

## 8. Show monitoring (CloudWatch)

Console -> **CloudWatch**:

- [ ] **Dashboards -> devorbit-dev-dashboard**: CPU and network for 3 hosts
- [ ] **Alarms**: `devorbit-dev-<host>-high-cpu` (3 alarms)
- [ ] **Log groups**: `/devorbit/dev/system` with syslog streams
- [ ] **SNS -> Topics -> devorbit-dev-alerts** and the email subscription

Talking point: infrastructure metrics come from CloudWatch, application health
comes from Kubernetes probes; the two are complementary.

## 9. Prove it is code

Show in the repository:

- `terraform/` creates every resource above
- `ansible/` configures every host
- `jenkins/Jenkinsfile` delivers every change
- `k8s/` defines the deployment

## 10. Cleanup after the demo

```bash
cd terraform
terraform destroy
```

Destroy the `bootstrap` stack only after the main stack is gone.
