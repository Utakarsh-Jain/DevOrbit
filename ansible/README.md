# DevOrbit Server Configuration Management (Ansible)

This directory contains Ansible playbooks to configure the provisioned EC2 Linux machines with Docker, Java 21, and k3s Kubernetes.

## Directory Structure
- `ansible.cfg` - Global Ansible execution parameters.
- `inventory/hosts.ini.example` - Example inventory file.
- `playbooks/site.yml` - Master playbook executing roles.
- `roles/common` - Updates apt repository, installs baseline tools and JRE 21.
- `roles/docker` - Installs official Docker CE and configures permissions.
- `roles/k3s` - Installs lightweight k3s Kubernetes single-node cluster and configures kubectl.

## Usage

### 1. Setup Inventory
Copy the example inventory and update with your EC2 public IP from Terraform:
```bash
cp inventory/hosts.ini.example inventory/hosts.ini
# Edit inventory/hosts.ini with your public IP
```

### 2. Syntax Check
```bash
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --syntax-check
```

### 3. Run Playbook
```bash
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

### 4. Verify on Server
SSH into the server and check:
```bash
docker --version
kubectl get nodes
```
