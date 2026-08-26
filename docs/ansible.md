# Ansible Configuration Management Guide

## Purpose
Automates package installation, user privileges, Docker runtime configuration, and k3s Kubernetes cluster bootstrap across target Linux hosts without manual SSH script execution.

## Playbook Execution Workflow

```bash
# Check syntax of playbooks and roles
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --syntax-check

# Execute playbook in dry-run mode
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --check

# Execute configuration against inventory
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

## Idempotency
Ansible playbooks are idempotent: running the playbook multiple times ensures the system converges to the desired state without creating redundant files or breaking services.
