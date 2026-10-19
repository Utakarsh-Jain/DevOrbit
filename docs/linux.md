# Linux Essentials and Host Administration

All three DevOrbit hosts are Ubuntu 22.04 LTS running in AWS. Connect through
the bastion (VPC-A) or directly from CloudShell.

## Common administrative commands

```bash
# Process and resource monitoring
top
ps aux | grep java
free -h
df -h

# Network and ports
ip a
ss -tulpn
curl -I http://localhost:8080/health        # on the k3s host
curl -I http://<k3s-private-ip>:30080/health  # from the Jenkins host

# Service management
sudo systemctl status docker
sudo systemctl status jenkins
sudo systemctl status k3s
sudo journalctl -u k3s -f
```

## Host responsibilities

| Host | VPC | Runs |
| :--- | :--- | :--- |
| bastion | VPC-A | Ansible control, operational checks |
| jenkins | VPC-C | Docker, Maven, Jenkins LTS |
| k3s | VPC-B | Docker, k3s single-node cluster, application Pods |

## Security best practices

- SSH keys only; no password login.
- The `ubuntu` user has sudo and docker group membership.
- Application containers run as the unprivileged `devorbit` user (uid 1001).
- IMDSv2 is required on every instance.
