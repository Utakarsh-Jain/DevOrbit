# Ansible Configuration Management Guide

## Purpose

Ansible configures the hosts that Terraform created: baseline packages and Java,
Docker Engine, the k3s cluster, Jenkins, and the CloudWatch agent. It is
idempotent, so it can be re-run safely.

## Roles

| Role | Applies to | Installs |
| :--- | :--- | :--- |
| `common` | all hosts | utilities, Java 21, Maven, sysctls, swap off |
| `cloudwatch` | all hosts | CloudWatch agent for metrics and system logs |
| `docker` | jenkins, k3s | Docker Engine from the official repository |
| `jenkins` | jenkins | Jenkins LTS and Docker group access |
| `k3s` | k3s | single-node k3s cluster and kubeconfig |

## Run from AWS CloudShell or the bastion

```bash
ansible-galaxy collection install community.general ansible.posix

cp inventory/hosts.ini.example inventory/hosts.ini   # paste terraform output
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --syntax-check
ansible-playbook -i inventory/hosts.ini playbooks/site.yml --check   # dry run
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

## Idempotency

Re-running the playbook converges the hosts to the desired state without
reinstalling software or restarting healthy services.
