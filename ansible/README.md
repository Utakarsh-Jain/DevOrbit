# DevOrbit Configuration Management (Ansible)

Ansible turns the Terraform-provisioned EC2 instances into ready-to-use hosts:

```text
VPC-A bastion  -> common + CloudWatch agent
VPC-C jenkins  -> common + CloudWatch agent + Docker + Jenkins
VPC-B k3s      -> common + CloudWatch agent + Docker + k3s
```

## Directory structure

```text
ansible/
├── ansible.cfg
├── group_vars/all.yml
├── inventory/hosts.ini.example
├── playbooks/site.yml
└── roles/
    ├── common/       baseline packages, Java 21, sysctls, swap off
    ├── docker/       Docker Engine from the official Docker repository
    ├── k3s/          single-node k3s cluster + kubeconfig
    ├── jenkins/      Jenkins LTS and Docker group access
    └── cloudwatch/   CloudWatch agent for metrics and system logs
```

## Required collections

```bash
ansible-galaxy collection install community.general ansible.posix
```

## Usage

Run Ansible from **AWS CloudShell** or the bastion host, never from a local
machine.

```bash
# 1. Build the inventory from Terraform output
terraform -chdir=../terraform output ansible_inventory
cp inventory/hosts.ini.example inventory/hosts.ini
# edit inventory/hosts.ini with the printed IPs

# 2. Validate
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --syntax-check

# 3. Configure every host
ansible-playbook -i inventory/hosts.ini playbooks/site.yml

# 4. Verify
ansible -i inventory/hosts.ini all -m command -a "docker --version"
ansible -i inventory/hosts.ini k3s -m command -a "kubectl get nodes"
```

## Post-install steps

- Jenkins initial password: `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`
  (read it on the Jenkins host, never commit it).
- The kubeconfig for Jenkins is at `/home/ubuntu/.kube/config` on the k3s host,
  already rewritten to the host private IP for cross-VPC access.
